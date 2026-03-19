## 1. Ansible 설치시 권한이 없어 실패하는 상황
### **문제:**
각 노드에 접속하여 Docker 엔진을 설치하고, 컨테이너 환경을 구동하기 위한 필수 패키지들을 자동으로 구성하는 node bootstrap 설치 명령어 입력시 아래와 같은 의존성 에러 발생.
```bash
(kolla-venv) sok@controller:~$ kolla-ansible bootstrap-servers -i multinode
Bootstrapping servers
[WARNING]: Invalid characters were found in group names but not replaced, use -vvvv to see details

PLAY [Gather facts for all hosts] **************************************************************************************************************************************************

TASK [Group hosts to determine when using --limit] *********************************************************************************************************************************
ok: [compute02]
ok: [compute01]
ok: [controller]
ok: [localhost]

TASK [Gather facts] ****************************************************************************************************************************************************************
ok: [localhost]
ok: [controller]
ok: [compute01]
ok: [compute02]
[WARNING]: Could not match supplied host pattern, ignoring: all_using_limit_True

PLAY [Gather facts for all hosts (if using --limit)] *******************************************************************************************************************************
skipping: no hosts matched

PLAY [Apply role baremetal] ********************************************************************************************************************************************************

TASK [openstack.kolla.etc_hosts : Include etc-hosts.yml] ***************************************************************************************************************************
included: /home/sok/.ansible/collections/ansible_collections/openstack/kolla/roles/etc_hosts/tasks/etc-hosts.yml for controller, compute01, compute02

TASK [openstack.kolla.etc_hosts : Ensure localhost in /etc/hosts] ******************************************************************************************************************
fatal: [controller]: FAILED! => {"msg": "Missing sudo password"}
fatal: [compute01]: FAILED! => {"msg": "Missing sudo password"}
fatal: [compute02]: FAILED! => {"msg": "Missing sudo password"}

PLAY RECAP *************************************************************************************************************************************************************************
compute01                  : ok=3    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0   
compute02                  : ok=3    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0   
controller                 : ok=3    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0   
localhost                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

Kolla Ansible playbook(s) /home/sok/kolla-venv/share/kolla-ansible/ansible/kolla-host.yml exited 2
```

### 원인:
Ansible이 각 컴퓨트 노드와 컨트롤러 노드의 /etc/hosts 파일 같은 시스템 핵심 설정을 수정하려고 sudo (관리자 권한)를 시도했는데, 비밀번호를 입력해야 하는 상태라 백그라운드 작업이 막혀버린 것.

### 해결:
**Passwordless Sudo 설정**
세 대의 서버(controller, compute01, compute02)에 각각 접속하셔서 아래 명령어를 한 번씩만 실행.

```bash
echo "sok ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/sok
(이 명령어를 실행할 때는 마지막으로 sok 계정의 비밀번호를 한 번 물어볼 것입니다.)
```

설정 확인:
명령어 적용 후, 세 대의 서버 모두에서 sudo ls 같은 명령어를 입력했을 때 비밀번호를 묻지 않고 바로 실행된다면 완벽하게 적용된 것.