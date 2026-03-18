### Docker Swarm ip set

	manager-node: 192.168.137.100
	worker1: 192.168.137.101
	worker2: 192.168.137.102

### Swarm init
manager 노드에서 아래 실행 후 swarm join 명령어 복사

```bash
■ manager ~ # docker swarm init --advertise-addr 192.168.137.100
Swarm initialized: current node (e706qzj1wvdw52elywu56x4xa) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token <token>192.168.137.100:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

```

worker1, 2 노드에서 붙여넣기
```bash
■ worker1 ~ # docker swarm join --token <token>192.168.137.100:2377
This node joined a swarm as a worker.

■ worker2 ~ # docker swarm join --token <token>192.168.137.100:2377
This node joined a swarm as a worker.
```

manager node 에서 연결된 node 확인
```bash
■ manager ~ # docker node ls
ID                            HOSTNAME       STATUS    AVAILABILITY   MANAGER STATUS   ENGINE VERSION
e706qzj1wvdw52elywu56x4xa *   manager-node   Ready     Active         Leader           28.1.1
wgeabmussi66rx30piw1jx5sa     worker1        Ready     Active                          28.1.1
z127py95b6bgfd5p5z5izyryh     worker2        Ready     Active                          28.1.1
```


### service 배포
```bash
■ manager ~ # docker service create takytaky/app:v1
5d9do8q75yyrrm4qmnovp9s89
overall progress: 1 out of 1 tasks 
1/1: running   
verify: Service 5d9do8q75yyrrm4qmnovp9s89 converged 
■ manager ~ # docker service ls
ID             NAME                MODE         REPLICAS   IMAGE             PORTS
5d9do8q75yyr   dreamy_chatterjee   replicated   1/1        takytaky/app:v1   

```

