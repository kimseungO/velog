![](https://velog.velcdn.com/images/rtd7878/post/af0c06f0-5a44-471d-9c28-a58f4899f165/image.png)

전편에 이어서 작성하는 내용입니다.
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
**1. 로그 확인**
```bash
sok@compute01:~$ sudo grep -i "ERROR" /var/log/kolla/nova/nova-compute.log | tail -n 20
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     nwinfo = self.network_api.allocate_for_instance(
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 1229, in allocate_for_instance
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     created_port_ids = self._update_ports_for_instance(
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 1365, in _update_ports_for_instance
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     with excutils.save_and_reraise_exception():
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/oslo_utils/excutils.py", line 227, in __exit__
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     self.force_reraise()
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/oslo_utils/excutils.py", line 200, in force_reraise
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     raise self.value
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 1340, in _update_ports_for_instance
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     updated_port = self._update_port(
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]                    ^^^^^^^^^^^^^^^^^^
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 585, in _update_port
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     _ensure_no_port_binding_failure(port)
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]   File "/var/lib/kolla/venv/lib/python3.12/site-packages/nova/network/neutron.py", line 294, in _ensure_no_port_binding_failure
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858]     raise exception.PortBindingFailed(port_id=port['id'])
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858] nova.exception.PortBindingFailed: Binding failed for port 08772e00-7449-42d0-b319-6792f0698863, please check neutron logs for more information.
2026-03-23 07:46:38.846 7 ERROR nova.compute.manager [instance: aaf45e13-d313-4faf-8155-79d133ef7858] 
```
- Nova(컴퓨트 서비스)의 로그가 please check neutron logs for more information라며 책임을 Neutron(네트워크 서비스)으로 넘겼습니다. 
즉, 통로(br-ex)도 열려있고 에이전트도 살아있는데, Neutron 에이전트가 내부적인 설정 누락이나 다른 이유로 포트 바인딩을 거부하고 있는 상황.

정확히 어떤 설정이 어긋났는지 확인하기 위해, Compute01 노드에서 Neutron OVS 에이전트의 속마음(로그와 설정 파일)을 들여다봐야 합니다.

**2. Neutron OVS 에이전트 로그 확인**
바인딩이 실패한 정확한 사유가 에이전트 로그에 고스란히 남아있을 것입니다. Compute01 노드에서 아래 명령어를 실행해 주세요.
```bash
sok@compute01:~$ sudo grep -i "ERROR\|WARNING" /var/log/kolla/neutron/neutron-openvswitch-agent.log | tail -n 20
2026-03-20 10:16:23.631 7 ERROR oslo.messaging._drivers.impl_rabbit [-] [a59d8046-2ae3-47cb-acff-8bcf24ca0e0c] AMQP server on 192.168.6.10:5672 is unreachable: <RecoverableConnectionError: unknown error>. Trying again in 1 seconds.: amqp.exceptions.RecoverableConnectionError: <RecoverableConnectionError: unknown error>
2026-03-20 10:16:24.191 7 ERROR oslo.messaging._drivers.impl_rabbit [-] [37821ceb-b51b-472b-b9b6-916209685a99] AMQP server on 192.168.6.10:5672 is unreachable: <RecoverableConnectionError: unknown error>. Trying again in 1 seconds.: amqp.exceptions.RecoverableConnectionError: <RecoverableConnectionError: unknown error>
2026-03-20 10:16:24.441 7 ERROR oslo.messaging._drivers.impl_rabbit [-] [4a680fdf-151f-4577-9c87-13df1ee14070] AMQP server on 192.168.6.10:5672 is unreachable: <RecoverableConnectionError: unknown error>. Trying again in 1 seconds.: amqp.exceptions.RecoverableConnectionError: <RecoverableConnectionError: unknown error>
2026-03-23 06:57:38.525 7 WARNING oslo_config.cfg [-] Deprecated: Option "heartbeat_in_pthread" from group "oslo_messaging_rabbit" is deprecated for removal (The option is related to Eventlet which will be removed. In addition this has never worked as expected with services using eventlet for core service framework.).  Its value may be silently ignored in the future.
2026-03-23 06:57:41.659 7 ERROR oslo.messaging._drivers.impl_rabbit [-] Connection failed: [Errno 111] ECONNREFUSED (retrying in 1.0 seconds): ConnectionRefusedError: [Errno 111] ECONNREFUSED
2026-03-23 06:57:42.663 7 ERROR oslo.messaging._drivers.impl_rabbit [-] Connection failed: [Errno 111] ECONNREFUSED (retrying in 3.0 seconds): ConnectionRefusedError: [Errno 111] ECONNREFUSED
2026-03-23 06:57:45.667 7 ERROR oslo.messaging._drivers.impl_rabbit [-] Connection failed: [Errno 111] ECONNREFUSED (retrying in 5.0 seconds): ConnectionRefusedError: [Errno 111] ECONNREFUSED
2026-03-23 06:57:50.674 7 ERROR oslo.messaging._drivers.impl_rabbit [-] Connection failed: [Errno 111] ECONNREFUSED (retrying in 7.0 seconds): ConnectionRefusedError: [Errno 111] ECONNREFUSED
2026-03-23 06:57:59.285 57 WARNING neutron.privileged.agent.ovsdb.native.helpers [-] OVS Manager creation failed, it might already exist (stderr: ovs-vsctl: multiple rows in Manager match "ptcp:6640:127.0.0.1"
2026-03-23 07:33:20.711 7 ERROR neutron.agent.common.async_process [-] Error received from [ovsdb-client monitor tcp:127.0.0.1:6640 Interface name,ofport,external_ids --format=json]: None
2026-03-23 07:33:22.858 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:22.865 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:22.873 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:22.878 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:22.883 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:22.891 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:23.617 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:23.634 7 WARNING amqp [None req-21c3fe68-e499-4dd5-b090-7803a53d338d - - - - - -] Received method (60, 30) during closing channel 1. This method will be ignored
2026-03-23 07:33:37.389 7 WARNING oslo_config.cfg [-] Deprecated: Option "heartbeat_in_pthread" from group "oslo_messaging_rabbit" is deprecated for removal (The option is related to Eventlet which will be removed. In addition this has never worked as expected with services using eventlet for core service framework.).  Its value may be silently ignored in the future.
2026-03-23 07:33:41.986 57 WARNING neutron.privileged.agent.ovsdb.native.helpers [-] OVS Manager creation failed, it might already exist (stderr: ovs-vsctl: multiple rows in Manager match "ptcp:6640:127.0.0.1"
```

에러 로그 주목: **OVS Manager creation failed, it might already exist (stderr: ovs-vsctl: multiple rows in Manager match "ptcp:6640:127.0.0.1"**

**3. 브릿지 매핑(bridge_mappings) 설정 확인**
앞선 reconfigure 단계에서 Kolla-Ansible이 외부 네트워크 이름(physnet1)과 OVS 브릿지(br-ex)를 연결해 주는 설정을 파일에 제대로 기록했는지 검증해야 합니다. Compute01 노드에서 아래 명령어를 쳐서 설정값을 확인합니다.
```bash
sok@compute01:~$ sudo grep -i "bridge_mappings" /etc/kolla/neutron-openvswitch-agent/openvswitch_agent.ini

sok@compute01:~$ 
```
정상적이라면 bridge_mappings = physnet1:br-ex라는 값이 출력되어야 합니다.
(아무것도 나오지 않음)

---

### 원인:
가장 결정적인 단서는 **Step 2(bridge_mappings 부재)**입니다. reconfigure 명령어를 실행했음에도 불구하고, Compute01 노드의 설정 파일에 bridge_mappings = physnet1:br-ex 설정이 들어가지 않았습니다. 설정 파일이 비어있으니, 에이전트가 physnet1이라는 네트워크를 처리할 수 없는 것이 당연합니다.

왜 reconfigure가 설정을 넣어주지 않았을까요?

Kolla-Ansible은 reconfigure를 돌릴 때, **"이 노드의 물리 랜카드(ens37)가 OVS 브릿지에 할당될 수 있는 정상 상태인가?"**를 다시 한번 검사합니다. 이때 조금 전 올려주신 **Step 1(에이전트 로그)**의 마지막 줄을 보면 그 이유가 나옵니다.

**OVS Manager creation failed, it might already exist (stderr: ovs-vsctl: multiple rows in Manager match "ptcp:6640:127.0.0.1"**

이 에러는 호스트(Ubuntu)에 설치하셨던 openvswitch-switch 서비스가 아직 완전히 죽지 않아서, 도커 안의 OVS 컨테이너와 포트(6640) 충돌을 일으키고 있다는 뜻입니다. 충돌이 나니 Kolla가 OVS 설정을 제대로 읽고 쓰지 못했고, 그 결과 bridge_mappings 설정을 포기한 채 넘어가 버린 것입니다.

결론적으로, kolla-ansible로 openstack을 배포할 때 openvswitch를 임의로 따로 설치하면 위와 같은 오류가 발생하게 됩니다.

---

### 해결1: OVS 완벽히 제거후 재실행

**Step 1: 호스트 OVS 서비스 완벽 제거 및 정리 (Compute01, Compute02)**

```bash
# 1. 호스트 OVS 패키지 삭제
sudo apt-get purge -y openvswitch-switch

# 2. 혹시 살아있는 프로세스가 있다면 강제 종료
sudo pkill -9 ovs-vswitchd
sudo pkill -9 ovsdb-server
```
**Step 2: 도커 OVS 컨테이너 재시작 (Compute01, Compute02)**

```bash
sudo docker restart openvswitch_vswitchd openvswitch_db
```

**Step 3: Controller에서 Reconfigure 재실행 (가장 중요)**
이제 OVS 환경이 깨끗해졌으므로, Controller 노드로 돌아가서 reconfigure를 다시 실행합니다. 이번에는 100% 성공적으로 bridge_mappings 설정이 들어갈 것입니다.

```bash
# Controller 노드의 가상 환경(kolla-venv)에서 실행
kolla-ansible reconfigure -i multinode --tags openvswitch,neutron
```

**Step 4: 설정 파일 확인 (Compute01)**

```bash
sok@compute01:~$ sudo grep -i "bridge_mappings" /etc/kolla/neutron-openvswitch-agent/openvswitch_agent.ini
sok@compute01:~$ 
```
<span style="color:red">설정 파일 확인 했으나, bridge_mappings = physnet1:br-ex 가 출력되지 않고 있음.<style>


### 해결2: 직접 파일에 핵심 설정을 주입
  
**Step 1: 수동으로 매핑 설정 주입 (Compute01, Compute02 모두 실행)**

```bash
sudo vi /etc/kolla/neutron-openvswitch-agent/openvswitch_agent.ini
```  

파일이 열리면 키보드 방향키로 내려가면서 [ovs] 라고 적힌 섹션을 찾습니다. 그리고 그 바로 아래에 우리가 그토록 원하던 매핑 설정을 직접 타이핑해서 넣어줍니다.

```Ini, TOML
[ovs]
bridge_mappings = physnet1:br-ex
# (기존에 있던 다른 설정들은 그대로 둡니다)
```
  
**Step 2: Neutron OVS 에이전트 재시작 (Compute01, Compute02 모두 실행)**

```bash
sudo docker restart neutron_openvswitch_agent
```
  
성공적으로 ACTIVE 됨.
```bash
(kolla-venv) sok@controller:~$ openstack server list

+--------------------------------------+---------+--------+----------------------------+--------+---------+

| ID                                   | Name    | Status | Networks                   | Image  | Flavor  |

+--------------------------------------+---------+--------+----------------------------+--------+---------+

| 24daf230-e502-4cd4-86ce-972f5ae57706 | test-vm | ACTIVE | provider-net=192.168.6.133 | cirros | m1.nano |

+--------------------------------------+---------+--------+----------------------------+--------+---------+
  
```