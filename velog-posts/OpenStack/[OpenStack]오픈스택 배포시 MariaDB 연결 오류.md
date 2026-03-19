## kolla-ansible deploy 중 MariaDB 연결 오류
### 문제:
kolla-ansible deploy 명령어 실행시 MariaDB와의 연결이 안되는 오류 발생
```bash
kolla-ansible deploy -i multinode

TASK [mariadb : Wait for MariaDB service to be ready through VIP] ******************************************************************************************************************

FAILED - RETRYING: [controller]: Wait for MariaDB service to be ready through VIP (6 retries left).

FAILED - RETRYING: [controller]: Wait for MariaDB service to be ready through VIP (5 retries left).

FAILED - RETRYING: [controller]: Wait for MariaDB service to be ready through VIP (4 retries left).

FAILED - RETRYING: [controller]: Wait for MariaDB service to be ready through VIP (3 retries left).

FAILED - RETRYING: [controller]: Wait for MariaDB service to be ready through VIP (2 retries left).

FAILED - RETRYING: [controller]: Wait for MariaDB service to be ready through VIP (1 retries left).

fatal: [controller]: FAILED! => {"attempts": 6, "changed": false, "cmd": ["docker", "exec", "mariadb", "mysql", "-h", "-P", "3306", "-u", "root_shard_0", "-pZ79IpzTd90gfIX8WqoRVgQMDjAsSbAzbHNyOWSgg", "-e", "show databases;"], "delta": "0:00:00.039618", "end": "2026-03-16 07:10:30.364958", "msg": "non-zero return code", "rc": 1, "start": "2026-03-16 07:10:30.325340", "stderr": "ERROR 2005 (HY000): Unknown server host '-P' (-2)", "stderr_lines": ["ERROR 2005 (HY000): Unknown server host '-P' (-2)"], "stdout": "", "stdout_lines": []}



PLAY RECAP *************************************************************************************************************************************************************************

compute01                  : ok=16   changed=0    unreachable=0    failed=0    skipped=3    rescued=0    ignored=0   

compute02                  : ok=16   changed=0    unreachable=0    failed=0    skipped=3    rescued=0    ignored=0   

controller                 : ok=103  changed=11   unreachable=0    failed=1    skipped=97   rescued=0    ignored=1   

localhost                  : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   



Kolla Ansible playbook(s) /home/sok/kolla-venv/share/kolla-ansible/ansible/site.yml exited 2

(kolla-venv) sok@controller:~$ sudo docker ps -a | grep -v Up

CONTAINER ID   IMAGE                                                        COMMAND                  CREATED              STATUS                        PORTS     NAMES

(kolla-venv) sok@controller:~$ 
```

### 확인 사항:
1. VIP 할당 여부 확인(Keppalived 상태)
- 오픈스택의 Keepalived 컨테이너가 ens33 인터페이스에 가상 IP(192.168.6.200)를 성공적으로 붙였는지 확인
```bash
ip a | grep 192.168.6.200
 inet 192.168.6.200/32 scope global ens33
```
_**(정상)**_

2. 로드밸런서 우회 테스트 (MariaDB 다이렉트 접속)
- VIP(HAProxy)를 거치지 않고, 물리 노드의 IP(192.168.6.10)로 MariaDB에 직접 찔러봅니다. 만약 이게 성공한다면 DB 자체는 아주 건강한 것이고 프록시 설정만 고치면 됩니다.
```bash
sudo docker exec mariadb mysql -h 192.168.6.10 -P 3306 -u root_shard_0 -pZ79IpzTd90gfIX8WqoRVgQMDjAsSbAzbHNyOWSgg -e "show databases;"
Database

information_schema
mysql
performance_schema
sys
```
_**(정상)**_

3. 우분투 방화벽 비활성화
- Ubuntu 22.04의 기본 방화벽이 켜져 있으면 Docker 내부의 HAProxy 포워딩 통신이 드랍될 수 있다. 오픈스택 노드들은 내부적으로 iptables를 Kolla가 직접 관리하므로 UFW는 끄는 것이 원칙.
```bash
sudo ufw disable
```
_**(원래 꺼져 있었으므로 정상)**_

4. HAProxy 컨테이너 재시작
- 가장 유력한 원인인 '타이밍 꼬임'을 해결하기 위해 HAProxy를 깔끔하게 재시작하여 VIP와 포트 매핑을 다시 인식시킵니다.
```bash
sudo docker restart haproxy
```
_**(여전함)**_

5. HAProxy가 실제로 포트를 열고 있는지 확인
- 현재 컨트롤러 노드에서 누군가가 3306 포트(DB)와 VIP를 점유하고 있는지 확인하는 명령어입니다.
```bash
sudo ss -lnpt | grep 3306
LISTEN 0      900     192.168.6.10:3306       0.0.0.0:*    users:(("mariadbd",pid=9097,fd=32))      

LISTEN 0      80         127.0.0.1:3306       0.0.0.0:*    users:(("mariadbd",pid=17404,fd=20))    
```
_**정상**_
6. HAProxy 컨테이너 에러 로그 확인
HAProxy가 시작될 때 VIP에 바인딩(Binding)을 실패했거나, 설정 파일에 문제가 있어서 나는 에러를 확인합니다.
```bash
sudo docker logs haproxy 2>&1 | tail -n 20

INFO:__main__:Copying /var/lib/kolla/config_files/services.d/heat-api-cfn.cfg to /etc/haproxy/services.d/heat-api-cfn.cfg
INFO:__main__:Setting permission for /etc/haproxy/services.d/heat-api-cfn.cfg
INFO:__main__:Writing out command to execute
++ cat /run_command
+ CMD=/etc/haproxy/haproxy_run.sh
+ ARGS=
+ sudo kolla_copy_cacerts
+ sudo kolla_install_projects
Running command: '/etc/haproxy/haproxy_run.sh'
+ [[ ! -n '' ]]
+ . kolla_extend_start
+ echo 'Running command: '\''/etc/haproxy/haproxy_run.sh'\'''
+ exec /etc/haproxy/haproxy_run.sh
+ exec /usr/sbin/haproxy -W -db -p /run/haproxy.pid -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/services.d/
[NOTICE]   (7) : haproxy version is 2.8.16-0ubuntu0.24.04.1
[NOTICE]   (7) : path to executable is /usr/sbin/haproxy
[WARNING]  (7) : config : parsing [/etc/haproxy/services.d//horizon.cfg:7] : a 'http-request' rule placed after a 'use_backend' rule will still be processed before.
[WARNING]  (7) : config : parsing [/etc/haproxy/services.d//horizon.cfg:23] : a 'http-request' rule placed after a 'use_backend' rule will still be processed before.
[NOTICE]   (7) : New worker (17) forked
[NOTICE]   (7) : Loading success.
```
- 현재 상황: _**MariaDB는 LISTEN상태이지만 HAProxy는 시작만 되었을 뿐, 3306 포트를 아에 잡고있지 않음.**_


### 원인:
최신 Kolla-Ansible 버전(Bobcat, Caracal 등)부터 오픈스택 아키텍처에 거대한 변화가 있었습니다.
과거에는 정문 안내원(HAProxy)이 DB 통신(3306)을 VIP로 받아서 분배해 주었지만, **최신 버전부터는 성능 저하를 막고 구조를 단순화하기 위해 HAProxy에서 MariaDB 로드밸런싱 기능을 아예 제거해 버렸습니다!** 대신 OpenStack 서비스들이 MariaDB 노드(192.168.6.10)에 '직접' 연결하도록 아키텍처가 바뀌었습니다.
> _최신 공식 문서를 참고해야 하는 이유_

**그럼 왜 배포 스크립트는 실패했는가?**
배포 도구인 Ansible의 'DB 검증 스크립트(Wait for MariaDB...)'가 아직 과거의 방식을 버리지 못하고 멍청하게 VIP(192.168.6.200) 에 대고 3306 포트가 열렸는지 찔러보고 있었던 것입니다. (HAProxy가 포트를 안 열어주니 당연히 115 연결 거부 에러가 났던 것이죠.)

### 해결:
**"VIP 말고 직접 찾아가라"고 지시하기**
Ansible이 더 이상 헛발질을 하지 않도록, globals.yml에 데이터베이스 주소를 VIP가 아닌 컨트롤러 노드의 물리 IP로 명확하게 지정하기.

1. globals.yml 수정
Controller 노드에서 설정 파일을 엽니다.
```bash
sudo vi /etc/kolla/globals.yml
```
파일 아무 곳에나(기존 VIP 설정 바로 아래쪽이 좋습니다) 아래 한 줄을 추가해 줍니다.
```yml
database_address: "192.168.6.10"
```
