## kollas-ansible deploy 중 ssh 연결이 갑자기 끊긴 상황
### 문제:
kollas-ansible deploy 중 TASK openvswitch 셋업중에 ssh 연결이 갑자기 끊김.
vm으로 가서 ping google.com 으로 인터넷 접속도 끊어진 걸 확인.
```bash
TASK [openvswitch : Ensuring OVS ports are properly setup] *************************************************************************************************************************
skipping: [compute01] => (item=['br-ex', 'ens33']) 
skipping: [compute01]
skipping: [compute02] => (item=['br-ex', 'ens33']) 
skipping: [compute02]
changed: [controller] => (item=['br-ex', 'ens33'])

RUNNING HANDLER [openvswitch : Restart openvswitch-vswitchd container] *************************************************************************************************************



Socket error Event: 32 Error: 10053.
Connection closing...Socket close.


Connection closed by foreign host.


Disconnected from remote host(Controller) at 17:40:06.
```

---
### 원인:
**로그의 item=['br-ex', 'ens33'] 부분이 범인입니다.**
앞서 globals.yml 설정 시 외부 통신용 인터페이스(neutron_external_interface)를 ens33으로 지정하셨습니다. 
Kolla-Ansible은 지시받은 대로 오픈스택 가상 스위치(OVS)의 외부 브릿지인 br-ex에 ens33 랜카드를 물리적으로 꽂아버렸습니다.

문제는 리눅스 환경에서 어떤 물리 랜카드가 OVS 브릿지의 포트로 종속되는 순간, 그 랜카드가 가지고 있던 기존 IP(192.168.6.10) 설정이 싹 날아가 버린다는 것입니다. 우리가 SSH로 접속해 있던 바로 그 랜카드와 IP가 브릿지 안으로 흡수되면서 통신이 뚝 끊긴 것입니다.

결국 지금 외부 인터넷도 안 되고 다른 노드로 SSH도 안 되는 이유는, 오픈스택의 가상 스위치(br-ex)가 통신을 담당하던 유일한 랜카드(ens33)를 통째로 집어삼켜서(포트로 편입시켜서) ens33이 가지고 있던 IP(192.168.6.10)가 증발해버렸기 때문.

>실무 클라우드 환경에서 **관리용 네트워크(Management)**와 **서비스용 네트워크(External/Provider)**의 랜카드를 물리적으로 2개 이상 분리해야 하는 이유가 바로 이것입니다.

---
### 해결:
1. OVS 컨테이너 내부에서 랜카드 강제 분리
호스트 OS가 아니라, 돌아가고 있는 OVS 컨테이너 안에 명령을 내려서 브릿지(br-ex)가 삼켜버린 ens33을 뱉어내게 합니다.

```bash
sudo docker exec openvswitch_vswitchd ovs-vsctl del-port br-ex ens33
```
  (명령어를 쳤을 때 아무런 메시지 없이 다음 줄로 넘어가면 성공한 것입니다.)

2. OVS 컨테이너 일시 정지 (재발 방지)
네트워크를 살리는 동안 이 녀석들이 다시 랜카드를 집어삼키지 못하도록 컨테이너를 잠깐 재워둡니다.

```bash
sudo docker stop openvswitch_vswitchd openvswitch_db
```

3. 네트워크 설정(IP) 원상복구
이제 뱉어낸 ens33에 원래 IP(192.168.6.10)를 다시 할당해 줍니다. Ubuntu 22.04의 기본 네트워크 관리자인 netplan을 재적용하면 됩니다.

```bash
sudo netplan apply
```

4. 복구 확인 (Ping 테스트)
IP가 정상적으로 돌아왔는지, 인터넷이 다시 되는지 확인합니다.

```bash
ip a | grep ens33
ping -c 3 google.com
```

**복구 후 필수 진행 스텝 (2-NIC 구성)**
이제 똑같은 참사가 발생하지 않도록 물리적인 랜카드(NIC)를 하나 더 추가하여 역할을 분리해야 합니다.

가상머신 종료: 복구된 Controller 노드를 포함해 Compute01, Compute02까지 세 대를 모두 안전하게 종료합니다. (sudo poweroff)

VMware 랜카드 추가: VMware 설정(Settings)에 들어가서 세 대의 가상머신 모두 **Network Adapter를 1개씩 추가(Add)**해 줍니다. (기존과 똑같이 NAT 또는 Bridged로 맞추시면 됩니다.)

새 랜카드 이름 확인: 서버들을 다시 켜고 Controller에 SSH로 접속하여 ip a를 입력합니다. 새로 생긴 랜카드 이름(예: ens34, ens38 등)을 확인합니다.

globals.yml 수정:

```bash
sudo vi /etc/kolla/globals.yml
```
외부 통신용 인터페이스를 새로 추가한 깡통 랜카드 이름으로 변경해 줍니다.

```yml
# 관리 및 통신용 (IP 192.168.6.10이 있는 랜카드)
network_interface: "ens33"

# 가상머신들이 외부 인터넷으로 나갈 때 쓸 깡통 랜카드 (새로 추가한 랜카드)
neutron_external_interface: "ens34"
```