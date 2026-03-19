## 1. HAProxy VIP를 통한 클러스터링 통신이 막힌 상황
### 문제:
kolla-ansible 배포시 타임아웃 에러
```bash
kolla-ansible deploy -i multinode
fatal: [controller]: FAILED! => {"changed": false, "elapsed": 300, "msg": "Timeout when waiting for :61313"}



PLAY RECAP *************************************************************************************************************************************************************************

compute01                  : ok=20   changed=13   unreachable=0    failed=0    skipped=3    rescued=0    ignored=0   

compute02                  : ok=20   changed=13   unreachable=0    failed=0    skipped=3    rescued=0    ignored=0   

controller                 : ok=92   changed=61   unreachable=0    failed=1    skipped=88   rescued=0    ignored=0   

localhost                  : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   



Kolla Ansible playbook(s) /home/sok/kolla-venv/share/kolla-ansible/ansible/site.yml exited 2
```
### **원인:**
오픈스택의 로드밸런서(Keepalived)는 VIP를 소유하기 위해 가상 MAC 주소를 생성하고 네트워크 패킷을 브로드캐스트합니다. 하지만 VMware의 기본 보안 정책은 "자신의 원래 MAC 주소가 아닌 패킷(위조된 패킷)은 모두 차단한다"로 되어 있기 때문에 이 통신이 드랍되는 것입니다.
이로 인해 VMware vSwitch의 **'무작위 모드(Promiscuous Mode)'**가 허용되지 않아, HAProxy VIP를 통한 클러스터링 통신이 막힌 것.
>**무작위 모드(Promiscuous Mode):** 네트워크 카드(NIC)가 자신에게 향하지 않은 패킷을 포함해, 네트워크상에서 흐르는 모든 패킷을 차단하지 않고 수신하는 설정.

### 해결:
**VMware Workstation / Fusion (개인 PC용) 환경**
개인 PC에서 Workstation 프로를 사용 중이면 가상머신의 설정 파일(.vmx)을 직접 수정해야 합니다.

1. 가상머신 종료: 세 대의 서버(Controller, Compute01, Compute02)를 모두 안전하게 종료(sudo poweroff)합니다.

2. VMware 프로그램 종료: Workstation 프로그램을 완전히 닫습니다.

3. .vmx 파일 열기: 윈도우 탐색기(또는 Mac 파인더)를 열고 각 가상머신이 저장된 폴더로 이동하여 [가상머신이름].vmx 파일을 찾습니다. (예: Controller.vmx)

4. 텍스트 편집기로 수정: 해당 파일을 메모장(또는 VS Code 등)으로 열고, 맨 아래 줄에 다음 설정을 추가합니다. (만약 ethernet0이 아니라면 자신의 네트워크 어댑터 번호에 맞게 적어주세요.)

```Plaintext
ethernet0.noPromisc = "FALSE"
```
5. 파일을 저장하고 닫습니다.

6. 이 작업을 세 대의 가상머신(.vmx 파일)에 모두 동일하게 적용합니다.

7. 다시 VMware를 켜고 세 대의 서버를 부팅합니다.