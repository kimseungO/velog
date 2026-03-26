## 1. kolla-ansible deploy 중 RabbitMQ 에러(에러 코드70)
>RabbitMQ는 오픈스택의 모든 컴포넌트(Nova, Neutron 등)가 서로 대화를 나누는 '중앙 우체국(Message Broker)' 역할을 함.

### 문제: 
kolla-ansible deploy 중 RabbitMQ 에러 후 종료된 상황. (contoller failed)
```bash
$ kolla-ansible deploy -i multinode
TASK [rabbitmq : Waiting for rabbitmq to start] ************************************************************************************************************************************

fatal: [controller]: FAILED! => {"changed": true, "cmd": ["docker", "exec", "rabbitmq", "rabbitmqctl", "wait", "--timeout", "60", "/var/lib/rabbitmq/mnesia/rabbitmq.pid"], "delta": "0:00:06.688953", "end": "2026-03-16 08:07:10.246376", "msg": "non-zero return code", "rc": 70, "start": "2026-03-16 08:07:03.557423", "stderr": "{:case_clause, {:badrpc, :nodedown}}", "stderr_lines": ["{:case_clause, {:badrpc, :nodedown}}"], "stdout": "Waiting for pid file '/var/lib/rabbitmq/mnesia/rabbitmq.pid' to appear\npid is 25\nWaiting for erlang distribution on node 'rabbit@controller' while OS process '25' is running\nWaiting for applications 'rabbit_and_plugins' to start on node 'rabbit@controller'\nStack trace: \n\n** (CaseClauseError) no case clause matching: {:badrpc, :nodedown}\n    (rabbitmqctl 3.13.0-dev) lib/rabbitmq/cli/core/helpers.ex:105: anonymous fn/2 in RabbitMQ.CLI.Core.Helpers.stream_until_error_parameterised/2\n    (elixir 1.17.2) lib/stream.ex:990: Stream.do_transform_user/6\n    (elixir 1.17.2) lib/stream.ex:1891: Enumerable.Stream.do_each/4\n    (elixir 1.17.2) lib/enum.ex:2585: Enum.reduce_while/3\n    (rabbitmqctl 3.13.0-dev) lib/rabbitmq/cli/core/output.ex:56: RabbitMQ.CLI.Core.Output.print_output_0/3\n    (rabbitmqctl 3.13.0-dev) lib/rabbitmq/cli/core/output.ex:31: RabbitMQ.CLI.Core.Output.print_output/3\n    (rabbitmqctl 3.13.0-dev) lib/rabbitmqctl.ex:234: RabbitMQCtl.process_output/3\n    (rabbitmqctl 3.13.0-dev) lib/rabbitmqctl.ex:642: RabbitMQCtl.maybe_with_distribution/3", "stdout_lines": ["Waiting for pid file '/var/lib/rabbitmq/mnesia/rabbitmq.pid' to appear", "pid is 25", "Waiting for erlang distribution on node 'rabbit@controller' while OS process '25' is running", "Waiting for applications 'rabbit_and_plugins' to start on node 'rabbit@controller'", "Stack trace: ", "", "** (CaseClauseError) no case clause matching: {:badrpc, :nodedown}", "    (rabbitmqctl 3.13.0-dev) lib/rabbitmq/cli/core/helpers.ex:105: anonymous fn/2 in RabbitMQ.CLI.Core.Helpers.stream_until_error_parameterised/2", "    (elixir 1.17.2) lib/stream.ex:990: Stream.do_transform_user/6", "    (elixir 1.17.2) lib/stream.ex:1891: Enumerable.Stream.do_each/4", "    (elixir 1.17.2) lib/enum.ex:2585: Enum.reduce_while/3", "    (rabbitmqctl 3.13.0-dev) lib/rabbitmq/cli/core/output.ex:56: RabbitMQ.CLI.Core.Output.print_output_0/3", "    (rabbitmqctl 3.13.0-dev) lib/rabbitmq/cli/core/output.ex:31: RabbitMQ.CLI.Core.Output.print_output/3", "    (rabbitmqctl 3.13.0-dev) lib/rabbitmqctl.ex:234: RabbitMQCtl.process_output/3", "    (rabbitmqctl 3.13.0-dev) lib/rabbitmqctl.ex:642: RabbitMQCtl.maybe_with_distribution/3"]}



PLAY RECAP *************************************************************************************************************************************************************************

compute01                  : ok=23   changed=3    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0   

compute02                  : ok=24   changed=4    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0   

controller                 : ok=120  changed=9    unreachable=0    failed=1    skipped=109  rescued=0    ignored=0   

localhost                  : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   



Kolla Ansible playbook(s) /home/sok/kolla-venv/share/kolla-ansible/ansible/site.yml exited 2
```
### 원인:
RabbitMQ는 내부적으로 'Mnesia'라는 자체 데이터베이스를 사용해 클러스터 상태를 저장합니다. 문제는 우리가 앞서 MariaDB와 HAProxy 문제를 해결하기 위해 배포를 여러 번 재시도하고 끊는 과정에서, **RabbitMQ 컨테이너의 Mnesia 데이터가 꼬인 채로 Docker 볼륨(디스크)에 남아버렸기 때문**입니다.

그래서 컨테이너를 다시 띄우려 해도, 과거의 오염된 데이터를 물고 올라오다가 "어? 내 상태가 이상한데?" 하고 스스로 뻗어버리는 것입니다. (nodedown 상태)

### 해결:
**오염된 RabbitMQ 볼륨 완전 삭제**
해결책은 아주 간단하고 명쾌합니다. 꼬여버린 RabbitMQ의 뇌(Docker 볼륨)를 완전히 포맷해 버리고, Ansible이 깨끗한 상태로 처음부터 다시 만들게 하면 됩니다.

Controller 노드에서 아래 명령어들을 순서대로 실행해 주세요. (RabbitMQ 컨테이너와 찌꺼기 데이터를 날리는 작업입니다.)

```bash
# 1. 비정상 작동 중인 RabbitMQ 컨테이너 중지
sudo docker stop rabbitmq

# 2. RabbitMQ 컨테이너 삭제
sudo docker rm rabbitmq

# 3. (가장 중요) 오염된 데이터가 남아있는 Docker 볼륨 삭제
sudo docker volume rm rabbitmq
```
(만약 1, 2번에서 No such container 에러가 나더라도 당황하지 마시고 3번 볼륨 삭제까지 쭉 진행해 주시면 됩니다.)

## 2. kolla-ansible deploy 중 RabbitMQ 에러(에러 코드69)
### 문제:
kolla-ansible deploy 중 RabbitMQ 에러 후 종료된 상황.
컨테이너가 켜지려고 시도하다가 모종의 이유로 기동 자체를 실패하고 스스로 종료(Crash)되어 버린 상태
```bash
$ kolla-ansible deploy -i multinode
TASK [rabbitmq : Waiting for rabbitmq to start] ************************************************************************************************************************************

fatal: [controller]: FAILED! => {"changed": true, "cmd": ["docker", "exec", "rabbitmq", "rabbitmqctl", "wait", "--timeout", "60", "/var/lib/rabbitmq/mnesia/rabbitmq.pid"], "delta": "0:00:04.274591", "end": "2026-03-16 08:14:46.042505", "msg": "non-zero return code", "rc": 69, "start": "2026-03-16 08:14:41.767914", "stderr": "Error:\nrabbit_is_not_running", "stderr_lines": ["Error:", "rabbit_is_not_running"], "stdout": "Waiting for pid file '/var/lib/rabbitmq/mnesia/rabbitmq.pid' to appear\npid is 24\nWaiting for erlang distribution on node 'rabbit@controller' while OS process '24' is running\nWaiting for applications 'rabbit_and_plugins' to start on node 'rabbit@controller'", "stdout_lines": ["Waiting for pid file '/var/lib/rabbitmq/mnesia/rabbitmq.pid' to appear", "pid is 24", "Waiting for erlang distribution on node 'rabbit@controller' while OS process '24' is running", "Waiting for applications 'rabbit_and_plugins' to start on node 'rabbit@controller'"]}



PLAY RECAP *************************************************************************************************************************************************************************

compute01                  : ok=22   changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0   

compute02                  : ok=22   changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0   

controller                 : ok=119  changed=7    unreachable=0    failed=1    skipped=109  rescued=0    ignored=0   

localhost                  : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   



Kolla Ansible playbook(s) /home/sok/kolla-venv/share/kolla-ansible/ansible/site.yml exited 2
```

### 확인 사항:
RabbitMQ가 왜 켜지다 말았는지 상세한 에러 원인을 확인하기 위해 **컨테이너에 찍힌 로그**를 확인해 봅시다.
```bash
(kolla-venv) sok@controller:~$ sudo docker logs rabbitmq --tail 50
Runtime terminating during boot ({5739,{error,{rabbitmq_management,{bad_return,{{rabbit_mgmt_app,start,[normal,[]]},{'EXIT',{{could_not_start_listener,[{cowboy_opts,[{sendfile,false}]},{ip,"192.168.6.10"},{port,15672}],{shutdown,{failed_to_start_child,{ranch_listener_sup,{acceptor,{192,168,6,10},15672}},{shutdown,{failed_to_start_child,ranch_acceptors_sup,{listen_error,{acceptor,{192,168,6,10},15672},eaddrinuse}}}}}},{gen_server,call,[rabbit_web_dispatch_registry,{add,rabbitmq_management_tcp,[{cowboy_opts,[{sendfile,false}]},{ip,"192.168.6.10"},{port,15672}],#Fun<rabbit_web_dispatch.0.29520022>,[{'_',[],[{[],[],rabbit_mgmt_wm_static,{priv_file,rabbitmq_management,"www/index.html"}},{[<<"js">>,<<"oidc-oauth">>,<<"bootstrap.js">>],[],rabbit_mgmt_oauth_bootstrap,#{}},{[<<"login">>],[],rabbit_mgmt_login,[]},{[<<"api">>,<<"overview">>],[],rabbit_mgmt_wm_overview,[]},{[<<"api">>,<<"cluster-name">>],[],rabbit_mgmt_wm_cluster_name,[]},{[<<"api">>,<<"nodes">>],[],rabbit_mgmt_wm_nodes,[]},{[<<"api">>,<<"nodes">>,node]



Crash dump is being written to: /var/log/kolla/rabbitmq/erl_crash.dump...done

[os_mon] cpu supervisor port (cpu_sup): Erlang has closed

[os_mon] memory supervisor port (memsup): Erlang has closed

  Starting broker...
```
### 원인:
**{listen_error,{acceptor,{192,168,6,10},15672},eaddrinuse}**
**eaddrinuse**는 **"Error: Address Already In Use (주소가 이미 사용 중입니다)"**라는 뜻입니다. 즉, RabbitMQ 컨테이너가 켜지면서 자신의 웹 관리자 포트인 15672번을 열려고 시도했는데, 컨트롤러 노드의 누군가가 이미 그 포트를 꽉 쥐고 놓아주지 않고 있어서 충돌이 나며 컨테이너가 뻗어버린 것.

### 해결:
**1. 15672 포트를 물고 있는 범인 색출**
어떤 프로세스가 이 포트를 점유하고 있는지 확인합니다.

```bash
(kolla-venv) sok@controller:~$ sudo ss -lnpt | grep 15672

LISTEN 0      4096         0.0.0.0:15672      0.0.0.0:*    users:(("haproxy",pid=52135,fd=32))  
```

**2. HAProxy 컨테이너 삭제**
일단 포트를 물고 있는 녀석을 강제로 끄고 지워버립니다. (설정 수정 후 다시 깨끗하게 띄울 예정이니 안심하고 지우셔도 됩니다.)

```bash
sudo docker stop haproxy
sudo docker rm haproxy
```

**3. globals.yml에 HAProxy 활동 구역 제한**
HAProxy가 0.0.0.0 전체를 잡았던 이유는, 외부망 VIP 설정이 누락되어 기본값(전체 허용)으로 동작했기 때문입니다.

  파일을 열고, 기존에 작성한 kolla_internal_vip_address 바로 아래에 **kolla_external_vip_address**를 동일한 IP로 추가해 줍니다. 
(실습 환경에서는 내/외부 VIP를 동일하게 맞추는 것이 정석.)

```bash
sudo vi /etc/kolla/globals.yml
```


```yaml
kolla_internal_vip_address: "192.168.6.200"
kolla_internal_fqdn: "192.168.6.200"
# 아래 줄을 추가합니다.
kolla_external_vip_address: "192.168.6.200"
```