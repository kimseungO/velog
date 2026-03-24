![](https://velog.velcdn.com/images/rtd7878/post/7e7eab25-cbf3-4c39-bfab-430a77f4cc78/image.png)

## 가상머신 생성후 Status : ERROR  발생

### 문제:
- 가상머신 생성후 Status가 ACTIVE가 아닌 ERROR 상태 발생.
```bash
(kolla-venv) sok@controller:~$ openstack server list

+--------------------------------------+---------+--------+----------+--------+---------+

| ID                                   | Name    | Status | Networks | Image  | Flavor  |

+--------------------------------------+---------+--------+----------+--------+---------+

| 617f376f-f451-459b-9ed7-66efa21c2a41 | test-vm | ERROR  |          | cirros | m1.nano |

+--------------------------------------+---------+--------+----------+--------+---------+
```

### 원인:
- **VMware 중첩 가상화**(Nested Virtualization)
Kolla-Ansible은 기본적으로 하드웨어 가속인 KVM(virt_type: kvm)을 사용하여 VM을 생성합니다. 그런데 VMware에 설치된 Ubuntu(Compute 노드)의 설정에서 하드웨어 가속(VT-x/AMD-V) 전달이 켜져 있지 않으면 KVM이 동작하지 않아 VM 생성이 실패합니다.
- Compute01 또는 Compute02 노드의 터미널(또는 SSH)에 접속해서 아래 명령어를 입력
```bash
$ egrep -c '(vmx|svm)' /proc/cpuinfo
0
```
- 결과가 0인 경우: VMware 설정에서 해당 가상머신(Compute01, 02)의 설정(Settings) -> Processors -> "Virtualize Intel VT-x/EPT or AMD-V/RVI" 옵션이 체크되어 있지 않은 것.


### 해결:

>_*현 상황에서 하드웨어 가속을 위한 조치를 해보았으나 실패하여 소프트웨어 에뮬레이션 방식으로 대체_

Step 1: QEMU 가상화 방식으로 변경
컨트롤러 노드의 globals.yml 파일에 다음 한 줄을 추가하여 Nova가 QEMU를 사용하도록 지시합니다.

```yml
# /etc/kolla/globals.yml 파일 하단 등에 추가
nova_compute_virt_type: "qemu"
```

Step 2: 변경된 설정 적용 (Reconfigure)
전체 배포(deploy)를 다시 돌릴 필요 없이, 변경된 설정만 Nova 서비스에 덮어씌우면 됩니다. Controller 노드에서 가상 환경(kolla-venv)이 활성화된 상태로 아래 명령어를 실행해 주세요.

```bash
kolla-ansible reconfigure -i multinode --tags nova
```

--tags nova 옵션을 붙이면 전체 서비스가 아닌 Nova 관련 컨테이너만 빠르게 설정이 업데이트되고 재시작되어 시간을 크게 단축할 수 있습니다.

Step 3: 실패한 기존 인스턴스 정리
Nova 서비스가 QEMU 방식으로 업데이트되었다면, 에러 상태로 멈춰있는 기존 인스턴스를 지워줍니다.

```bash
openstack server delete test-vm
```