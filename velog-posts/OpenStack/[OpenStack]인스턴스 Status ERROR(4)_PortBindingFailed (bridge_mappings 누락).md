![](https://velog.velcdn.com/images/rtd7878/post/e1568fe8-e8d5-4e3e-8d44-571915e175b8/image.png)

### 문제:
가상머신 생성후 Status가 ACTIVE가 아닌 ERROR 발생했습니다.

```bash
$ openstack server list
+--------------------------------------+-----------------+--------+----------+--------------+------------+
| ID                                   | Name            | Status | Networks | Image        | Flavor     |
+--------------------------------------+-----------------+--------+----------+--------------+------------+
| 294fc52b-eedf-4550-b756-31fa85e34797 | k8s-master-node | ERROR  |          | Ubuntu-22.04 | k8s-flavor |
+--------------------------------------+-----------------+--------+----------+--------------+------------+
```
정확한 에러 원인을 파악하기 위해 Controller 노드에서 nova-conductor 로그를 확인해 보았습니다.

```bash
$ sudo egrep -i "error|exception|failed" /var/log/kolla/nova/nova-conductor.log | tail -n 10

nova.exception.PortBindingFailed: Binding failed for port d6e20df1-0a1a-4c18-9828-847c99ad755c, please check neutron logs for more information.
...
nova.exception.MaxRetriesExceeded: Exceeded maximum number of retries. Exhausted all hosts available for retrying build failures for instance...
```
로그 확인 결과, PortBindingFailed 에러가 발생하며 스케줄러가 최대 재시도 횟수를 초과해 인스턴스 생성을 강제 중단한 것을 알 수 있었습니다.

### 원인:
PortBindingFailed는 주로 Neutron(네트워크 서비스)이 **인스턴스의 가상 랜카드**를 **OVS 브릿지**에 연결하지 못할 때 발생합니다.

원인 파악을 위해 Compute 노드에서 OVS 상태와 Neutron 에이전트 설정 파일을 디버깅한 결과, 다음과 같은 사실을 발견했습니다.

**물리 랜카드 및 브릿지 상태 확인:**
통신을 담당할 물리 인터페이스(ens37)가 DOWN 상태였고, 심지어 외부 통신용 브릿지인 br-ex가 생성되어 있지 않았습니다. (수동으로 ip link set ens37 up 및 ovs-vsctl add-br br-ex 조치를 취함)

**결정적 원인 - bridge_mappings 누락:**
물리 인터페이스와 브릿지를 살려놓아도 에러가 지속되었습니다. 확인해 보니, Neutron OVS 에이전트 설정 파일에 OpenStack 네트워크(physnet1)와 실제 OVS 브릿지(br-ex)를 연결해 주는 매핑 정보가 아예 누락되어 있었습니다.

```bash
# 매핑 정보가 비어있음
$ sudo cat /etc/kolla/neutron-openvswitch-agent/openvswitch_agent.ini | grep bridge_mappings
```
**왜 Kolla-Ansible이 자동으로 매핑해주지 않았을까?**
최신 OpenStack 릴리즈(Yoga 이후)에서는 기본 SDN 백엔드가 OVN으로 넘어가면서, 기존 OVS 기반 배포 시 globals.yml에 선언한 변수(neutron_bridge_name 등)가 .ini 파일에 자동으로 렌더링되지 않는 경우가 발생합니다. **즉, Kolla-Ansible이 템플릿을 생성할 때 해당 값을 무시하고 넘어간 것입니다.**

### 해결:
비어있는 매핑 정보를 직접 주입하여 Neutron이 다리를 인식하게 만들어야 합니다.

#### 방법 1. 임시 조치 (Compute 노드에서 직접 수정)
당장 문제를 해결하기 위해 각 Compute 노드의 컨테이너 마운트 설정 파일을 직접 수정합니다.

1. 에이전트 설정 파일 편집

```bash
$ sudo vi /etc/kolla/neutron-openvswitch-agent/openvswitch_agent.ini
```
2. [ovs] 섹션 아래에 매핑 정보 추가

```TOML
[ovs]
bridge_mappings = physnet1:br-ex
```
3. OVS 에이전트 컨테이너 재시작

```bash
$ sudo docker restart neutron_openvswitch_agent
```
#### 방법 2. 영구 조치 (Kolla-Ansible Config Override 권장)
주의: 위 1번 방법은 추후 kolla-ansible reconfigure를 실행하면 초기화됩니다. 클라우드 확장성을 위해 Controller 노드에서 Custom Config Override 방식을 사용하는 것이 좋습니다.

1. Controller 노드에서 오버라이드 경로 생성 및 파일 작성

```bash
$ sudo mkdir -p /etc/kolla/config/neutron
$ sudo vi /etc/kolla/config/neutron/openvswitch_agent.ini
```
2. 아래 내용 저장

```yml
[ovs]
bridge_mappings = physnet1:br-ex
```
3. Kolla-Ansible 재구성 실행 (전체 노드에 자동 배포됨)

```bash
$ kolla-ansible -i multinode reconfigure
```
조치 완료 후, 기존 ERROR 상태의 VM을 삭제하고 다시 생성하면 상태가 정상적으로 ACTIVE 로 변경되는 것을 확인할 수 있습니다.