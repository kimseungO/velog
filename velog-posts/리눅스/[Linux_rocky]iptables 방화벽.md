▣ iptables
iptables는 리눅스에서 네트워크 트래픽을 관리하고 보안을 강화하기 위해 사용되는 강력한 명령줄 기반 방화벽 도구이다. 이는 커널의 Netfilter 모듈을 제어하여 네트워크 패킷을 필터링하고, 특정 규칙에 따라 트래픽을 허용하거나 차단한다.

▣ iptables의 주요 구성 요소
1. 테이블(Tables) : 패킷 처리 유형에 따라 분류된 규칙 집합이다. 주요 테이블로는 filter, nat, mangle, raw 등이 있다.
- filter: 기본 테이블로, 패킷 필터링을 담당한다.
- nat: 네트워크 주소(NAT)을 처리한다.
- mangle: 패킷 수정 작업을 수행한다.
2. 체인(Chain) : 테이블 내부에서 규칙이 적용되는 흐름이다.
- INPUT: 시스템으로 들어오는 패킷을 처리
- OUTPUT: 시스템에서 나가는 패킷을 처리
- FORWARD: 시스템을 통과하는 패킷을 처리
3. 타겟(Targets): 규칙이 적용된 후 수행할 작업이다.
- ACCEPT: 패킷을 허용한다.
- DROP: 패킷을 차단하며 응답하지 않는다.
- REJECT: 패킷을 차단하며 오류메시지를 보낸다.
- LOG: 패킷 정보를 로그에 기록

▣ DROP vs. REJECT
- DROP: DROP은 패킷을 조용히 삭제하여 송신자에게 아무런 응답을 보내지 않는다. 이는 공격자나 송신자가 서버가 존재하는지 알수 없도록 숨기는데 유용하다.
- REJECT: REJECT는 패킷을 차단하면서 오류 메시지를 송신자에게 반환한다. 송신자는 서비스가 이용 불가능하다는 것을 즉시 알 수 있다.

![](https://velog.velcdn.com/images/rtd7878/post/36ae7e22-c251-4d9a-b99e-9029c5c388cf/image.png)

*chain 테이블은 위에서 아래로 순서대로 참고하기 때문에 만약 클라이언트에서 접속시, 서버에서 iptables의 위에서 거절라인에 부합한다면 아래에서 승인하는 명령어를 넣어도 접속이 거절당함

### INPUT chain 관리 예제
```bash
[root@server ~]# netstat -tnp | grep :22
tcp        0     52 192.168.10.100:22       192.168.56.1:13281      ESTABLISHED 1294/sshd: root [pr 
[root@server ~]# iptables -L INPUT -n
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         
[root@server ~]# iptables -A INPUT -p tcp -s 192.168.56.1 --dport 22 -j ACCEPT
[root@server ~]# iptables -A INPUT -p tcp -s 192.168.10.103 --dport 22 -j REJECT
[root@server ~]# iptables -L INPUT -n
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         
ACCEPT     6    --  192.168.56.1         0.0.0.0/0            tcp dpt:22
REJECT     6    --  192.168.10.103       0.0.0.0/0            tcp dpt:22 reject-with icmp-port-unreachable
[root@server ~]# iptables -D INPUT -p tcp -s 192.168.10.103 --dport 22 -j REJECT
[root@server ~]# iptables -L INPUT -n
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         
ACCEPT     6    --  192.168.56.1         0.0.0.0/0            tcp dpt:22
[root@server ~]# iptables -F INPUT
[root@server ~]# iptables -L INPUT -n
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         

```