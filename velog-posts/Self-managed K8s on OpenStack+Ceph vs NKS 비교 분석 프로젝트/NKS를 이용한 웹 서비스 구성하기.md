
## 1. 목적
NHN Cloud를 이용하여 Cloud Native 환경에서 3-Tier 웹 서비스를 구성하여 NHN Cloud 활용 능력과 Cloud Native 환경에 대한 이해도를 높이고자 합니다.

추후 NKS 위에서 구성하는 3-tier 워크로드를, OpenStack+Ceph 위에 직접 구축한 K8s에서도 동일하게 구현하고 플랫폼 레이어 관점에서 비교 분석합니다.

## 2. 아키텍처
아래는 아키텍처 초본입니다. 프로젝트를 진행하며 수정될 수 있으며, 추후 CI/CD, Monitoring 파트도 추가할 예정입니다.


![](https://velog.velcdn.com/images/rtd7878/post/a1d501af-f3ab-48d3-834a-f77aa318c8a8/image.png)


1. 단일 VPC로 구성했습니다.
2. Public Subnet과 Private Subnet으로 나누고 DB용 Private Subent을 따로 만들어 주었습니다.
3. Private Subnet 내에선 단일 NKS cluster로 구성했고 namespace를 web과 was로 나눠주었습니다. 
- 관리자 진입 흐름
  - Public Subnet에는 관리자의 진입점인 Bastion host와 Private Subnet의 외부 접속용 NAT gateway를 두었습니다.
  - Bastion host는 NKS cluster 및 DB 서버에 접속이 가능합니다.
- 사용자 진입 흐름
  - Public Subnet에는 사용자 접속용 Internet gateway를 통해 Load Balancer를 거쳐서 웹 서비스 요청이 전달됩니다.
  - Ingress Controller에서 전달된 사용자 요청에 따라 목적지(web)에 전달해주고, was에서 사용자 요청을 DB와 연계하여 처리합니다.
  
## 3. 스택 선택 근거

| 레이어 | 선택 | 이유 |
|--------|------|------|
| WEB | Nginx | 경량 컨테이너 이미지, 리버스 프록시 역할, K8s 환경에 자연스러운 구성 |
| WAS | Node.js | 사전 사용 경험 있음 → 스택 구현에 시간 소모 없이 플랫폼 비교에 집중 가능 |
| DB | RDS for MySQL | NHN Cloud 관리형 서비스, 설치/운영 부담 없음 |

다음 단계에서 아래 컴포넌트를 추가할 수 있습니다:
- Object Storage (정적 파일, 사용자 업로드)
- CI/CD 파이프라인 (Gitlab, Jenkins, Harbor)
- Monitoring (Prometheus, Grafana)