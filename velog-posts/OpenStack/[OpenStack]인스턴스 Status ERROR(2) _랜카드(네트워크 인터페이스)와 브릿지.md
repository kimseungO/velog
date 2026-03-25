![](https://velog.velcdn.com/images/rtd7878/post/af0c06f0-5a44-471d-9c28-a58f4899f165/image.png)

## 가상머신 생성후 Status: ERROR 발생
### 문제: 
- 가상머신 생성후 Status가 ACTIVE가 아닌 ERROR 발생

```bash
(kolla-venv) sok@controller:~$ openstack server list

+--------------------------------------+---------+--------+----------+--------+---------+

| ID                                   | Name    | Status | Networks | Image  | Flavor  |

+--------------------------------------+---------+--------+----------+--------+---------+

| a6394371-1067-4b00-b447-1cb9ffba17e6 | test-vm | ERROR  |          | cirros | m1.nano |

+--------------------------------------+---------+--------+----------+--------+---------+
```

---

### 확인사항:
1. 상태 에러 메세지 확인
```bash
(kolla-venv) sok@controller:~$ openstack server show a6394371-1067-4b00-b447-1cb9ffba17e6 -f value -c fault

{'code': 500, 'created': '2026-03-23T07:18:15Z', 'message': 'Exceeded maximum number of retries. Exhausted all hosts available for retrying build failures for instance a6394371-1067-4b00-b447-1cb9ffba17e6.', 'details': 'Traceback (most recent call last):\n  File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/conductor/manager.py", line 705, in build_instances\n    raise exception.MaxRetriesExceeded(reason=msg)\nnova.exception.MaxRetriesExceeded: Exceeded maximum number of retries. Exhausted all hosts available for retrying build failures for instance a6394371-1067-4b00-b447-1cb9ffba17e6.\n'}

```
- Controller의 스케줄러가 자원이 남은 Compute 노드를 정상적으로 찾아내서 VM 생성을 지시(Build request)했으나, 막상 명령을 받은 Compute 노드가 VM을 띄우는 과정에서 치명적인 오류를 발생시켰다는 뜻입니다. 
실패를 확인한 스케줄러가 다른 Compute 노드에 재시도했지만 거기서도 실패하여 결국 포기한 상태입니다.
=> compute노드쪽 문제

Compute 노드에서 Nova 로그 확인
```bash
sok@compute01:~$ sudo grep -i "ERROR" /var/log/kolla/nova/nova-compute.log | tail -n 20
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     nwinfo = self.network_api.allocate_for_instance(
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 1229, in allocate_for_instance
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     created_port_ids = self._update_ports_for_instance(
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 1365, in _update_ports_for_instance
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     with excutils.save_and_reraise_exception():
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/oslo_utils/excutils.py", line 227, in __exit__
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     self.force_reraise()
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/oslo_utils/excutils.py", line 200, in force_reraise
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     raise self.value
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 1340, in _update_ports_for_instance
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     updated_port = self._update_port(
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]                    ^^^^^^^^^^^^^^^^^^
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 585, in _update_port
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     _ensure_no_port_binding_failure(port)
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 294, in _ensure_no_port_binding_failure
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6]     raise exception.PortBindingFailed(port_id=port['id'])
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6] nova.exception.PortBindingFailed: Binding failed for port 378c844d-b0b5-45be-90ec-8b222b954163, please check neutron logs for more information.
2026-03-23 07:17:58.377 7 ERROR nova.compute.manager [instance: a6394371-1067-4b00-b447-1cb9ffba17e6] 
```
- **nova.exception.PortBindingFailed 에러**: 
Nova가 Neutron에게 "이 VM에 꽂아줄 가상 랜선 좀 연결해 줘!"라고 요청했는데, Compute01 노드에서 네트워크를 담당하는 Open vSwitch(OVS) 에이전트가 VM의 가상 랜카드를 물리 인터페이스(ens37)가 있는 br-ex 브릿지에 물리적으로 결합하지 못한 것.

2. Neutron 에이전트 상태 확인 (Controller 노드에서)
우선 Controller에서 전체 네트워크 에이전트들이 정상적으로 살아있는지(Alive) 확인합니다.

```bash
openstack network agent list
```
- _UP 확인(정상)_

3. OVS 브릿지 구성 확인 (Compute01 노드에서)
에러가 발생한 Compute01 노드에 직접 접속하여, OVS가 br-ex 브릿지를 잘 만들었고 거기에 ens37을 정상적으로 꽂아두었는지 확인합니다.
```bash
sok@compute01:~$ sudo ovs-vsctl show

29cd41e8-541f-4b87-af62-611343443c84
    Manager "ptcp:6640:127.0.0.1"
        is_connected: true
    Bridge br-tun
        Controller "tcp:127.0.0.1:6633"
            is_connected: true
        fail_mode: secure
        datapath_type: system
        Port br-tun
            Interface br-tun
                type: internal
        Port patch-int
            Interface patch-int
                type: patch
                options: {peer=patch-tun}
    Bridge br-int
        Controller "tcp:127.0.0.1:6633"
            is_connected: true
        fail_mode: secure
        datapath_type: system
        Port br-int
            Interface br-int
                type: internal
        Port patch-tun
            Interface patch-tun
                type: patch
                options: {peer=patch-int}

```
- **문제점 확인: 내부 통신용 브릿지(br-int, br-tun)는 잘 생성되어 있지만, 외부 네트워크와 직접 연결되어야 할 핵심 브릿지인 br-ex가 아예 존재하지 않습니다.**

4. 물리 랜카드(ens37) UP/DOWN 상태 확인 (Compute01 노드에서)
Ubuntu 22.04에서는 두 번째 랜카드(ens37)를 꽂아두기만 하고 OS(Netplan) 단에서 IP를 할당하지 않으면, 네트워크 인터페이스 자체가 DOWN 상태로 머물러 있는 경우가 많습니다. 
인터페이스가 DOWN 상태면 OVS가 포트 바인딩을 거부합니다.
```bash
sok@compute01:~$ ip a show ens37
3: ens37: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:0c:29:34:05:96 brd ff:ff:ff:ff:ff:ff
    altname enp2s5

```

- ** 문제점 확인: DOWN 상태인 네트워크 인터페이스.**

--- 

### 해결: Compute 노드에서 실행
#### 1. 먼저 네트워크 인터페이스 활성화
```bash
sok@compute01:~$ sudo ip link set ens37 up
sok@compute02:~$ sudo ip link set ens37 up
```
#### 2. 수동으로 br-ex 브릿지 생성 및 포트 연결
Kolla의 OVS 컨테이너 내부에 직접 명령을 내려 br-ex를 만들고 ens37을 꽂아주겠습니다.
```bash
# 1. br-ex 브릿지 생성
sudo docker exec openvswitch_vswitchd ovs-vsctl add-br br-ex

# 2. br-ex 브릿지에 ens37 물리 랜카드 연결
sudo docker exec openvswitch_vswitchd ovs-vsctl add-port br-ex ens37

# 3. 브릿지가 잘 생성되었는지 최종 확인
sudo docker exec openvswitch_vswitchd ovs-vsctl show
```

#### 3. Neutron OVS 에이전트 재시작
OVS 브릿지 구조가 변경되었으므로, 네트워크 에이전트가 이를 새로 인식할 수 있도록 컨테이너를 재시작해 줍니다.

```bash
sudo docker restart neutron_openvswitch_agent
```

<span style="color:red">원래 여기서 되어야 하나, 다시 VM Status ERROR 발생<style>
  
  
이어서...