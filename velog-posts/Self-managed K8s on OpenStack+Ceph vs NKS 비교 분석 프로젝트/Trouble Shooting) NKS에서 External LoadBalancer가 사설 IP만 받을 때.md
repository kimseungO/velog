
## 들어가며

NHN Cloud NKS 위에 3-tier 웹 서비스를 구성하던 중, 외부 노출 단계에서 문제가 발생했습니다. `type: LoadBalancer`로 만든 LoadBalancer가 공인 IP가 아니라 **사설 IP만** 받고있었습니다.

결국 워커 노드를 Private에 유지한 채 공인 노출을 구현하기 위해 **공인 LoadBalancer를 직접 구성**하는 방식으로 해결했습니다.

---

## 1. 문제 상황

보통의 경우, NKS 클러스터에 Ingress Controller를 설치하면, `Service type: LoadBalancer`에 의해 NHN Cloud LoadBalancer가 자동 생성됩니다. 그런데 생성된 LB의 EXTERNAL-IP를 확인해보니 사설 대역이었습니다.

```bash
kubectl get svc -n ingress-nginx
```

```
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
ingress-nginx-controller   LoadBalancer   10.254.42.158   10.1.1.112    80:32118/TCP,443:32643/TCP
```

`10.1.1.112`. Private Subnet(10.1.1.0/24) 대역의 사설 IP입니다. 공인 IP가 아니니 외부 인터넷에서 접근할 수 없습니다.

콘솔에서 LoadBalancer 목록을 확인해도 생성된 LB가 전부 `private_subnet`에 위치해 있었습니다.

---

## 2. 원인 추적

### 첫 번째 시도 — Ingress 재설치, annotation 추가

처음엔 Ingress Controller 설정 문제라고 생각하고 `loadbalancer.openstack.org/keep-floatingip: "true"` 같은 annotation을 넣어 재설치도 해봤으나 결과는 동일했습니다.

### 네트워크 구조 확인

라우팅 테이블 확인.

```
Public Subnet  라우팅: 0.0.0.0/0 → Internet Gateway
Private Subnet 라우팅: 0.0.0.0/0 → NAT Gateway
```

NKS 워커 노드는 Private Subnet에 있었고, Private Subnet은 IGW가 아니라 NAT Gateway(아웃바운드 전용)에만 연결돼 있었으며, NKS를 Private Subnet에 구성한다면 외부 인바운드를 받을수 있는 공인IP를 할당 받을수 없었습니다.

### 대조 실험 — public 서브넷 테스트 클러스터

그래서 **public 서브넷 기준으로 테스트 클러스터를 하나 만들어** 동일하게 `type: LoadBalancer` 서비스를 만들어서 대조 실험을 해봤습니다. 

```bash
kubectl expose deployment test-nginx --type=LoadBalancer --port=80
kubectl get svc test-nginx -w
```

```
NAME         TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)
test-nginx   LoadBalancer   10.254.126.91   <pending>         80:32089/TCP
test-nginx   LoadBalancer   10.254.126.91   114.110.162.198   80:32089/TCP
```

**공인 IP(114.110.162.198)가 붙었습니다.**

같은 명령, 유일한 차이는 클러스터가 어느 서브넷 기준으로 생성됐는가였습니다.

### 확정된 원인

```
- NKS의 자동 LB 기능 자체는 정상 동작한다
- 다만 LB가 공인/사설로 생성되는지는
  "클러스터가 생성된 서브넷"에 따라 결정된다
- private_subnet 기준 클러스터 → LB가 사설로 생성
- public_subnet 기준 클러스터  → LB가 공인으로 생성
```

여기서 중요한 점은 NKS 클러스터 생성 화면에는 **LB 전용 서브넷을 따로 지정하는 항목이 없습니다.** 클러스터 생성 시 지정한 서브넷을 기준으로 LB도 생성됩니다. 그리고 이 LB 서브넷 결정 로직은 NHN이 관리하는 마스터(컨트롤 플레인) 영역에 있어서, 사용자가 kubectl로 조회하거나 변경할 수 없습니다. 추가적인 annotation 설정으로는 바뀌지 않았습니다. (NHN Cloud에서만의 문제같습니다.)

---

## 3. 수동 공인 LB 구축

전체 구조

```
사용자 → 공인 LB (Public Subnet)
       → 워커 노드 NodePort (30080)
       → Ingress Controller
       → web / was 서비스
```
 **NKS의 자동 LB를 쓰지 않고, Ingress Controller를 NodePort로만 노출한 뒤, 그 앞에 공인 LB를 직접 붙이는 것**을 구조로 잡았습니다.

### 3-1. Ingress Controller를 NodePort로 설치

자동 LB(사설로 나오는 IP)를 안 쓰기 위해, Service 타입을 NodePort로 지정.

```yaml
# ingress-values.yaml
controller:
  service:
    type: NodePort
    nodePorts:
      http: 30080
      https: 30443
```

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  -f ingress-values.yaml
```

나중에 LB가 이 포트를 대상으로 지정하기위해 NodePort를 30080으로 고정했습니다.

설치 후 확인하면 EXTERNAL-IP가 `<none>`으로 나옵니다. 외부 노출은 다음 단계의 수동 LB 설정에서 합니다.

```
NAME                       TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)
ingress-nginx-controller   NodePort   10.254.98.59    <none>        80:30080/TCP,443:30443/TCP
```

### 3-2. 공인 LoadBalancer 생성

콘솔에서 LoadBalancer를 직접 생성합니다. 이때 **서브넷을 반드시 public_subnet으로 지정**합니다.
![](https://velog.velcdn.com/images/rtd7878/post/042314f3-f1c7-4e1f-a729-cb3d73d0ad71/image.png)


리스너와 멤버 그룹 설정은 포트를 매핑해 줍니다.

```
리스너 (외부에서 받는 포트)
  - 프로토콜: HTTP
  - 로드밸런서 포트: 80

멤버 그룹 (워커 노드로 보내는 포트)
  - 포트: 30080   ← Ingress Controller의 NodePort
```



리스너 80으로 받아서 멤버 30080으로 넘기도록 설정해 줍니다.

그리고 아래쪽 멤버 목록에 워커 노드의 사설 IP를 포트는 30080으로 등록합니다.

```bash
kubectl get nodes -o wide
```

```
NAME                            INTERNAL-IP   ...
lab-nks-default-worker-node-0   10.1.1.106
lab-nks-default-worker-node-1   10.1.1.35
```
![](https://velog.velcdn.com/images/rtd7878/post/5bc4e841-c47f-4564-a368-50b915b919c5/image.png)

### 헬스 체크 이슈 — /healthz

LB 생성 직후 멤버 상태가 `INACTIVE`로 나왔습니다. LB 헬스 체크가 실패하고 있다는 뜻입니다.

원인은 헬스 체크 경로였습니다. 기본 설정은 `/`로 요청해 200을 기대하는데, Ingress Controller는 `/`로 요청하면 라우팅 규칙이 없어 404를 반환합니다.

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://10.1.1.106:30080/healthz  # 200
curl -s -o /dev/null -w "%{http_code}\n" http://10.1.1.106:30080/         # 404
```

Ingress Controller에는 `/healthz`라는 헬스 체크 전용 경로가 있고, 여기는 항상 200을 반환합니다. LB의 상태 확인 URL을 `/`에서 `/healthz`로 바꾸니 멤버가 `ACTIVE`로 바뀌었습니다.

### 3-3. Floating IP 연결

직접 만든 LB는 콘솔에서 Floating IP를 수동으로 연결할 수 있습니다. (NKS 자동 생성 LB는 이게 막혀 있는데, 직접 만든 LB는 가능합니다.)
![](https://velog.velcdn.com/images/rtd7878/post/ca09fff9-b807-40dd-952b-80a0ba4739d7/image.png)

LB에 Floating IP를 연결하니 공인 IP가 붙었습니다.

---

## 4. 결과

전체 경로가 완성됐습니다.

```
사용자 → 공인 LB (***.***.***.***)
       → 워커 노드 NodePort (30080)
       → Ingress Controller
       → web (nginx)
          ├─ /     → 정적 페이지 서빙
          └─ /api  → was (node.js) → RDS
```

외부에서 접속 테스트.

```bash
curl http://***.***.***.***/
# → 정적 페이지 정상 응답

curl http://***.***.***.***/api/health
# → {"status":"ok","tier":"was"}
```

워커 노드를 Private Subnet에 유지한 채, 공인 노출을 했습니다.

---

## 마치며

이 문제의 표면은 "LB에 공인 IP가 안 붙는다"였지만, 본질은 "NKS가 LB를 어느 서브넷 기준으로 생성하는가"였다. 그리고 그 결정 로직이 사용자가 접근할 수 없는 마스터 영역에 있다는 점이 핵심이었다.

가장 도움이 된 건 **public 테스트 클러스터로 대조 실험을 한 것**이다. 변수 하나(서브넷)만 바꿔 결과를 비교하니 원인이 명확하게 드러났다.

managed Kubernetes는 많은 것을 자동화해주지만, 그 자동화가 특정 조건(서브넷 구성)에 묶여 있다는 걸 이해하지 못하면 오히려 헤매게 된다. 이번 경험으로 그 경계를 한 겹 더 이해하게 됐다.