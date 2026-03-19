## 1. 의존성 충돌 문제
### 문제: 
ansible의 버전을 명시하여 설치(ansible-core도 자동으로 설치됨) 후 kolla-ansible을 설치하려 했으나 ERROR 상황
```bash

# Ansible 설치
pip install 'ansible>=8,<9'

# Kolla-Ansible 설치
pip install kolla-ansible

ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.

ansible 8.7.0 requires ansible-core~=2.15.7, but you have ansible-core 2.17.14 which is incompatible.

Successfully installed PrettyTable-3.17.0 ansible-core-2.17.14 autopage-0.6.0 backports.strenum-1.3.1 bcrypt-5.0.0 certifi-2026.2.25 charset_normalizer-3.4.5 cliff-4.13.2 cmd2-3.4.0 debtcollector-3.0.0 hvac-2.4.0 idna-3.11 iso8601-2.1.0 jmespath-1.1.0 kolla-ansible-20.3.0 markdown-it-py-4.0.0 mdurl-0.1.2 netaddr-1.3.0 oslo.config-10.3.0 oslo.i18n-6.7.2 oslo.utils-10.0.0 passlib-1.7.4 pbr-7.0.3 psutil-7.2.2 pygments-2.19.2 pyparsing-3.3.2 pyperclip-1.11.0 requests-2.32.5 rfc3986-2.0.0 rich-14.3.3 rich-argparse-1.7.2 stevedore-5.7.0 urllib3-2.6.3 wcwidth-0.6.0 wrapt-2.1.2
```


### **원인**: 
먼저 설치한 **ansible 8.7.0**은 **ansible-core 2.15.x** 버전을 요구하는데, 그 다음에 설치한 **kolla-ansible**이 의존성 패키지들을 끌고 오면서 최신 버전인 **ansible-core 2.17.14**를 강제로 설치해버려서 두 패키지 간의 호환성이 깨진 상황

### 해결: 
1. 충돌난 패키지 삭제
```Bash
pip uninstall -y ansible ansible-core kolla-ansible
```
2. 의존성을 맞춰서 동시 설치
```Bash
pip install 'ansible>=9,<10' kolla-ansible
```
3. 설치 확인
```Bash
ansible --version
```

## 2. 의존성 모듈 부재 문제
### 문제:
각 노드에 접속하여 Docker 엔진을 설치하고, 컨테이너 환경을 구동하기 위한 필수 패키지들을 자동으로 구성하는 node bootstrap 설치 명령어 입력시 아래와 같은 의존성 에러 발생.
```bash
(kolla-venv) sok@controller:~$ kolla-ansible bootstrap-servers -i multinode

Bootstrapping servers

[WARNING]: Invalid characters were found in group names but not replaced, use -vvvv to see details

ERROR! the role 'openstack.kolla.baremetal' was not found in /home/sok/kolla-venv/share/kolla-ansible/ansible/roles:/home/sok/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles:/home/sok/kolla-venv/share/kolla-ansible/ansible



The error appears to be in '/home/sok/kolla-venv/share/kolla-ansible/ansible/kolla-host.yml': line 13, column 7, but may

be elsewhere in the file depending on the exact syntax problem.



The offending line appears to be:



  roles:

    - { role: openstack.kolla.baremetal,

      ^ here
```

### **원인:**
최신 버전의 Kolla-Ansible은 pip를 통해 코어 패키지를 설치하더라도, Ansible이 내부적으로 사용하는 확장 모듈(Ansible Galaxy 컬렉션 및 Roles)까지 한 번에 다운로드해주지 않는다. 이 모듈들이 없어서 발생하는 에러.

### 해결:
1. 의존성 설치
```bash
kolla-ansible install-deps
```

2. 재시도
```bash
kolla-ansible bootstrap-servers -i multinode
```