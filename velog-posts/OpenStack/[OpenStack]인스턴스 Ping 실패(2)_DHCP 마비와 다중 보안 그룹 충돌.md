이전 포스팅에서 OVS(Open vSwitch)의 격리망(Dead VLAN 4095) 블랙홀을 탈출하여, 마침내 새 인스턴스에 정상적인 내부 통신 태그(tag: 3)를 할당받는 데 성공했다. 이제 통신이 뚫렸겠거니 하고 Controller 노드에서 당당하게 Ping을 날렸지만, 화면에는 또다시 Destination Host Unreachable이 찍히고 있었다.

### 문제 1: 문 앞까지 갔는데 대답이 없는 VM
논리적 네트워크 구조(OVS)와 물리망(ens37)이 모두 정상인데 통신이 안 된다면, 패킷이 도대체 어느 구간에서 증발하는지 현장을 덮쳐야 한다. 네트워크 엔지니어의 최종 병기인 tcpdump를 꺼내 들었다.

Compute 노드(인스턴스가 띄워진 노드)에서 터미널을 두 개 열고, 물리 랜카드(ens37) 구간과 가상머신 바로 앞단(qvo...) 구간을 동시에 감청했다.

[A. 물리 랜카드(ens37) 패킷 캡처]

```bash
01:39:23.043469 ARP, Request who-has 192.168.6.124 tell 192.168.6.10, length 46
01:39:24.074351 ARP, Request who-has 192.168.6.124 tell 192.168.6.10, length 46
```

[B. 가상머신 앞단(qvo) 패킷 캡처]

```bash
01:39:23.043659 ARP, Request who-has 192.168.6.124 tell 192.168.6.10, length 46
01:39:24.074373 ARP, Request who-has 192.168.6.124 tell 192.168.6.10, length 46
```

결과는 명확했다. Controller(192.168.6.10)가 "192.168.6.124 누구냐?" 하고 외치는 소리(ARP Request)가 OVS 브릿지를 무사히 통과해 가상머신 앞문(qvo)까지 완벽하게 도달하고 있었다. 그런데 정작 방 안의 가상머신이 아무런 대답(ARP Reply)을 하지 않는 것이었다.

### 원인 1: DHCP 에이전트 마비로 인한 'IP 없는 깡통'
가상머신이 대답을 안 하는 이유는 단 하나, 자기가 192.168.6.124라는 사실을 모르고 있기 때문이다.

Horizon 대시보드에 접속해 VNC 콘솔로 가상머신 내부에 직접 들어가 ip a 명령어를 쳐보았다. 아니나 다를까, eth0 인터페이스에 IP가 아예 할당되지 않은 '빈 깡통' 상태였다.

왜 이런 일이 발생했을까? 가상머신에게 IP를 빌려주는 **DHCP 에이전트(neutron_dhcp_agent)**는 Controller 노드에서 동작한다. 확인해 보니 **Controller 노드의 통신 출구인 ens37 랜카드가 DOWN 상태로 잠들어 있었다.** 
출구가 막혀있으니 DHCP 에이전트가 아무리 IP를 주려고(Offer) 해도 패킷이 밖으로 나가지 못하고 컨트롤러 내부에 갇혀 있었던 것이다.

### 해결 과정 1: Controller 통신구 정상화 및 DHCP 재시작
```bash
# 1. Controller 노드의 잠든 ens37 인터페이스 깨우기
sudo ip link set ens37 up

# 2. (추가 조치) OVS 브릿지에 남아있던 에러 유령 포트(ens34) 제거
sudo docker exec openvswitch_vswitchd ovs-vsctl del-port br-ex ens34

# 3. DHCP 에이전트 강제 재시작 (뇌 씻기)
sudo docker restart neutron_dhcp_agent

# 4. 인스턴스 재부팅 (DHCP 재요청 유도)
openstack server reboot test-vm
```

재부팅 후 VNC 콘솔에서 다시 ip a를 쳐보니, 드디어 eth0에 192.168.6.124가 잘 들어와 있었다.

--- 

### 문제 2: 다중 보안 그룹(Security Group) 충돌
IP가 들어왔으니 끝났다고 생각했지만, Controller에서 치는 Ping은 여전히 100% Packet Loss(시간 초과)가 나고 있었다. 이번엔 Destination Host Unreachable이 아닌 걸 보니 경로는 뚫렸는데 누군가 패킷을 버리고(Drop) 있는 상황이었다.

VNC 콘솔(VM 내부)에서 구글 DNS(8.8.8.8)와 게이트웨이(192.168.6.1)로 핑을 날려보니 시원하게 통신이 성공했다. OpenStack의 아웃바운드(Egress) 네트워크는 완벽하다는 뜻이다.

문제는 밖에서 안으로 들어오는 **인바운드(Ingress) 통신**이었다. 호스트 PC(회사 노트북)의 CMD 창에서 핑을 치니 역시나 "_요청 시간이 만료되었습니다._"가 떴다.

### 원인 2: 방화벽(Security Group) 적용의 함정
VM을 생성할 때 default 보안 그룹을 지정했고, 이전 명령어 이력을 보면 분명히 default 그룹에 Ping(ICMP)과 SSH(TCP 22)를 허용하는 룰을 넣었었다. 하지만 다시 룰을 확인해 보려 하자 이런 에러가 떴다.

```bash
(kolla-venv) sok@controller:~$ openstack security group rule list default
More than one SecurityGroup exists with the name 'default'.
```
**이름이 default인 보안 그룹이 여러 개 존재한다는 뜻이다.** 
OpenStack은 배포 시 내부적으로 여러 프로젝트(admin, service 등)를 만들며, 각 프로젝트마다 이름이 똑같은 default 보안 그룹을 생성한다. 터미널에서 이름만으로 룰을 추가하려다 보니, 시스템이 엉뚱한 프로젝트의 default 방화벽을 열어버렸고, 정작 내 인스턴스의 방화벽은 여전히 굳게 닫혀있었던 것이다.

### 해결 과정 2: 고유 ID를 통한 방화벽 개방 (최종 해결)
보안 그룹의 이름(default) 대신 고유한 UUID를 찾아서 룰을 정확하게 꽂아주어야 한다.

```bash
# 1. 내 프로젝트(admin)의 정확한 default 보안 그룹 ID 찾기
openstack security group list

# 2. 해당 고유 ID를 사용하여 Ping(ICMP)과 SSH(22) 허용 룰 추가
openstack security group rule create <정확한_보안그룹_ID> --protocol icmp
openstack security group rule create <정확한_보안그룹_ID> --protocol tcp --dst-port 22
```
룰을 추가하자마자 호스트 PC(노트북)에서 막혀있던 Ping 응답이 쏟아지기 시작했다!

```DOS
C:\>ping 192.168.6.124

192.168.6.124에 대한 Ping 통계:
    패킷: 보냄 = 4, 받음 = 4, 손실 = 0 (0% 손실)
```

SSH 접속까지 깔끔하게 뚫리며, 길고 길었던 Multi-Node OpenStack 트러블슈팅이 끝났다.

### 요약
통신 문제를 겪을 때는 1) tcpdump로 패킷이 가상머신 앞단(qvo)까지 오는지 확인하고, 2) VNC 콘솔로 들어가 IP가 정상 할당되었는지(DHCP 확인), 인터넷 통신이 되는지 확인해야 한다. 방화벽 룰을 다룰 때는 이름 중복으로 인한 사고를 막기 위해 반드시 **보안 그룹의 고유 ID(UUID)**를 사용하는 습관을 들이자.