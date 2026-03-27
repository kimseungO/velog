새롭게 test-vm을 배포했다.
인스턴스 상태도 ACTIVE로 예쁘게 올라왔고, IP(192.168.6.122)도 정상적으로 할당된 것을 확인했다. 그러나 ping을 찍어본 결과 Destination Host unreachable 에러가 발생했다.

### 문제:
Controller 노드에서 새로 생성된 인스턴스로 Ping 테스트를 시도했으나, Timeout(시간 초과)도 아닌 Destination Host Unreachable 에러가 발생했다.

```bash
(kolla-venv) sok@controller:~$ ping -c 4 192.168.6.122
PING 192.168.6.122 (192.168.6.122) 56(84) bytes of data.
From 192.168.6.10 icmp_seq=1 Destination Host Unreachable
From 192.168.6.10 icmp_seq=2 Destination Host Unreachable
From 192.168.6.10 icmp_seq=3 Destination Host Unreachable
From 192.168.6.10 icmp_seq=4 Destination Host Unreachable
```

이 에러는 방화벽(보안 그룹)에서 패킷을 차단한 것이 아니라, L2(데이터 링크) 계층에서 해당 IP의 MAC 주소를 아예 찾지 못했을 때(ARP 응답 없음) 발생한다. 즉, 물리적으로 통신 경로가 끊어졌다는 뜻이다.


### 원인:
#### 1. 물리 네트워크 상태 확인
먼저 해당 VM이 어느 Compute 노드에 생성되었는지 확인해 보니 compute02였다. 해당 노드에 접속하여 외부망과 연결되는 물리 랜카드(ens37)의 상태를 확인했다.

```bash
sok@compute02:~$ ip a show ens37
3: ens37: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master ovs-system state UP group default qlen 1000
```
결과는 정상(UP). 물리적인 연결은 완벽했다.

#### 2. 패킷 캡처(tcpdump)로 통신 구간 확인
랜카드가 켜져 있는데 통신이 안 된다면 패킷이 어디서 증발하는지 현장을 덮쳐야 한다. compute02 노드에서 tcpdump를 켜두고 Controller에서 핑을 날려보았다.


```bash
# compute02에서 패킷 감청 결과
01:20:07.835199 ARP, Request who-has 192.168.6.122 tell controller, length 46
01:20:08.857252 ARP, Request who-has 192.168.6.122 tell controller, length 46
...
```
Controller가 "192.168.6.122 누구냐?"라고 외치는 소리(ARP Request)가 compute02의 랜카드까지는 아주 잘 도착하고 있었다. 즉, VMware 보안 설정이나 물리망 이슈는 아니었다. 그런데 가상머신이 대답(ARP Reply)을 하지 않았다.

#### 3. OVS 브릿지 로그에서 범인 발견 (Dead VLAN 4095)
패킷은 들어왔는데 가상머신에게 전달되지 않는 상황. OVS(Open vSwitch) 설정을 까보던 중 소름 돋는 로그를 발견했다.

```bash
sok@compute02:~$ sudo docker exec openvswitch_vswitchd ovs-vsctl show
...
        Port qvoc35c730d-be
            tag: 4095
            Interface qvoc35c730d-be
...
```
가상머신과 연결되는 가상 랜선 포트(qvo...)에 **tag: 4095**가 찍혀있었다.

OpenStack Neutron OVS 에이전트는 포트 바인딩에 실패하거나 bridge_mappings 설정을 찾을 수 없을 때, 해당 포트를 **'Dead VLAN (VLAN ID 4095)'**이라는 격리망에 던져버린다. 물리적인 선은 꽂혀 있지만, 스위치 단에서 통신을 원천 차단해 블랙홀에 빠뜨린 것이다.

**진짜 원인:** 이전에 수동으로 bridge_mappings = physnet1:br-ex 설정을 주입하고 에이전트를 완전히 재시작하여 동기화하기 직전에 해당 VM이 생성되는 바람에, 길을 잃은 VM이 4095번 격리망에 갇혀버린 것이었다.

### 해결 과정
원인은 에이전트 동기화 타이밍 이슈였으므로, OVS 에이전트 설정이 정상화된 지금은 블랙홀에 빠진 인스턴스를 미련 없이 지우고 새로 생성하면 된다.

#### 1. 격리된 인스턴스 삭제 및 재생성
Controller 노드에서 인스턴스를 삭제하고 다시 배포한다.

```bash
# 기존 인스턴스 삭제
openstack server delete test-vm

# 인스턴스 재생성
openstack server create \
  --flavor m1.nano \
  --image cirros \
  --nic net-id=provider-net \
  --security-group default \
  --key-name mykey \
  test-vm
```
#### 2. OVS Tag 정상화 확인
새로 배포된 인스턴스가 위치한 Compute 노드에서 다시 ovs-vsctl show를 확인해 보았다.

```bash
        Port qvo03f2ebfe-c2
            tag: 3
            Interface qvo03f2ebfe-c2
```
드디어 4095가 아닌 정상적인 통신용 내부 태그(tag: 3)가 할당되었다! 논리적인 OVS 내부 통신망 연결이 100% 정상화된 것이다.


### 요약
Destination Host Unreachable 에러가 뜬다면 ovs-vsctl show를 쳐서 가상머신 포트(qvo)의 태그가 4095인지 확인하라. 4095라면 bridge_mappings 설정 누락이나 에이전트 동기화 실패로 인한 격리 상태이므로, 네트워크 설정을 바로잡고 에이전트를 재시작해야 한다.

...이제 정상적으로 핑이 나갈 줄 알았다. 하지만 새롭게 생성된 인스턴스에 핑을 날렸을 때, 나는 또 다른 형태의 100% Packet Loss 절망을 맛봐야 했다. (다음 편에 계속...)