
### replicas 장애 테스트
- replicas 배포
```bash
■ manager ~ # docker service create --name swarm-web --replicas 2 -p 80:80 nginx
rfd9cppdw9j2sx6sr6nstewst
overall progress: 2 out of 2 tasks 
1/2: running   
2/2: running   
verify: Service rfd9cppdw9j2sx6sr6nstewst converged 

■ manager ~ # docker service ls
ID             NAME        MODE         REPLICAS   IMAGE          PORTS
rfd9cppdw9j2   swarm-web   replicated   2/2        nginx:latest   *:80->80/tcp

■ manager ~ # docker service ps swarm-web 
ID             NAME          IMAGE          NODE           DESIRED STATE   CURRENT STATE                ERROR     PORTS
0w7parlk1yvx   swarm-web.1   nginx:latest   manager-node   Running         Running about a minute ago             
e3a2k3mot2vj   swarm-web.2   nginx:latest   worker2        Running         Running 56 seconds ago   
```

- 장애 테스트: worker2에서 task 강제로 삭제
```bash
■ worker2 ~ # docker ps --filter is-task=true
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS     NAMES
9e3ffa0694c4   nginx:latest   "/docker-entrypoint.…"   3 minutes ago   Up 3 minutes   80/tcp    swarm-web.2.e3a2k3mot2vjxb0khtha4cwdv
■ worker2 ~ # docker rm -f swarm-web.2.e3a2k3mot2vjxb0khtha4cwdv 
swarm-web.2.e3a2k3mot2vjxb0khtha4cwdv
```

- 복구 확인
```bash
■ manager ~ # docker service ps swarm-web 
ID             NAME              IMAGE          NODE           DESIRED STATE   CURRENT STATE                ERROR                         PORTS
0w7parlk1yvx   swarm-web.1       nginx:latest   manager-node   Running         Running 4 minutes ago                                      
vgb9yhp85f3s   swarm-web.2       nginx:latest   worker1        Running         Running about a minute ago                                 
e3a2k3mot2vj    \_ swarm-web.2   nginx:latest   worker2        Shutdown        Failed about a minute ago    "task: non-zero exit (137)"  
```