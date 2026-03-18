```bash
■ manager ~ # docker service create --name nodejs --replicas 3 takytaky/app:v1
uf0vb7rnacquxl8xjpv8jii0n
overall progress: 3 out of 3 tasks 
1/3: running   
2/3: running   
3/3: running   
verify: Service uf0vb7rnacquxl8xjpv8jii0n converged 
```
#### 버전2로 롤링 업데이트:
```bash
■ manager ~ # docker service update nodejs --image takytaky/app:v2
image takytaky/app:v2 could not be accessed on a registry to record
its digest. Each node will access takytaky/app:v2 independently,
possibly leading to different nodes running different
versions of the image.

nodejs
overall progress: 0 out of 3 tasks 
1/3: preparing 
2/3:   
3/3:   
service update paused: update paused due to failure or early termination of task dn6lo6ls4qqt32ymc60jtr23v

```

#### 서비스 모니터링:
```bash
Every 1.0s: docker service ps nodejs                   manager-node: Thu May  1 01:06:46 2025

ID             NAME           IMAGE             NODE           DESIRED STATE   CURRENT STATE
          ERROR     PORTS
os8zdznk9id0   nodejs.1       takytaky/app:v1   worker1        Running         Running 2 minu
tes ago
ce8fvf1eseeh   nodejs.2       takytaky/app:v1   worker2        Running         Running 2 minu
tes ago
u3amg196q4ne   nodejs.3       takytaky/app:v2   manager-node   Ready           Ready 8 second
s ago
8ljy56s80ken    \_ nodejs.3   takytaky/app:v1   manager-node   Shutdown        Running 8 seco
nds ago

``` 
- task가 돌아가면서 v2로 업데이트 되는 모습


#### 롤백
```bash
■ manager ~ # docker service rollback  nodejs
nodejs
rollback: manually requested rollback 
overall progress: rolling back update: 3 out of 3 tasks 
1/3: running   
2/3: running   
3/3: running   
verify: Service nodejs converged 
```

```bash
Every 1.0s: docker service ps nodejs                   manager-node: Thu May  1 01:08:59 2025

ID             NAME           IMAGE             NODE           DESIRED STATE   CURRENT STATE
                ERROR     PORTS
iryymtwk9ktf   nodejs.1       takytaky/app:v1   worker1        Ready           Ready 2 second
s ago
bzblhj4es79q    \_ nodejs.1   takytaky/app:v2   worker1        Shutdown        Running 2 seco
nds ago
os8zdznk9id0    \_ nodejs.1   takytaky/app:v1   worker1        Shutdown        Shutdown about
 a minute ago
o9epa2p8ryfl   nodejs.2       takytaky/app:v2   worker2        Running         Running about
a minute ago
ce8fvf1eseeh    \_ nodejs.2   takytaky/app:v1   worker2        Shutdown        Shutdown about
 a minute ago
oqymefeuvdkq   nodejs.3       takytaky/app:v1   manager-node   Running         Running 2 seco
nds ago
u3amg196q4ne    \_ nodejs.3   takytaky/app:v2   manager-node   Shutdown        Shutdown 3 sec
onds ago
8ljy56s80ken    \_ nodejs.3   takytaky/app:v1   manager-node   Shutdown        Shutdown 2 min
```