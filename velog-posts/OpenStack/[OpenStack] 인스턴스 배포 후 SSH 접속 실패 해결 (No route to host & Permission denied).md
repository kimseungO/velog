![](https://velog.velcdn.com/images/rtd7878/post/a5f5cc98-b6cc-453b-8408-822900328b9f/image.png)

### 문제

워커 노드 2대를 성공적으로 `ACTIVE` 상태로 띄웠습니다. 하지만 인스턴스에 SSH 접속을 시도하자, 각각 다른 이유로 접속이 거부되는 장애가 발생했습니다.

**현상 1. Worker-01 접속 실패 (네트워크 도달 불가)**

```bash
$ ssh -i ~/.ssh/k8s_key ubuntu@192.168.95.138
ssh: connect to host 192.168.95.138 port 22: No route to host
```

**현상 2. Worker-02 접속 실패 (키 인증 거부)**

```bash
$ ssh -i ~/.ssh/k8s_key ubuntu@192.168.95.169
ubuntu@192.168.95.169: Permission denied (publickey).
```
---
### 원인

두 에러는 발생 지점과 원인이 다릅니다.

**1. `No route to host` 에러의 원인 (L3 라우팅 단절)**
해당 에러는 접속을 시도하는 클라이언트(Controller 노드)에서 목적지 IP로 가는 물리적/논리적 길을 찾지 못했을 때 발생합니다.
앞선 트러블슈팅 과정에서 하이퍼바이저(VMware)를 재부팅했는데, 수동으로 `UP` 시켜두었던 외부 통신용 물리 인터페이스(`ens37`)가 재부팅되면서 다시 `DOWN` 상태로 초기화된 것이 원인이었습니다. 통신 랜카드가 꺼져 있으니 패킷이 나가지 못한 것입니다.

**2. `Permission denied (publickey)` 에러의 원인 (Metadata 주입 실패)**
대상 서버가 응답은 했으나 사용자의 키를 거부한 상황입니다. 원인을 찾기 위해 인스턴스의 콘솔 부팅 로그를 확인해 보았습니다.

```bash
$ openstack console log show k8s-worker-02 | grep cloud-init
[    6.654122] cloud-init[549]: 2026-04-02 03:29:03,623 - log_util.py[WARNING]: No active metadata service found
...
[   43.587289] cloud-init[581]: 2026-04-02 03:29:41,705 - log_util.py[WARNING]: No active metadata service found
[   59.151250] cloud-init[852]: 2026-04-02 03:29:57,269 - cc_final_message.py[WARNING]: Used fallback datasource
```

로그 확인 결과, **"No active metadata service found"**라는 경고가 발견되었습니다.
아
OpenStack에서 인스턴스가 생성될 때 내부의 `cloud-init` 데몬이 메타데이터 서비스(`169.254.169.254`)와 통신하여 사용자의 SSH Public Key를 받아오고 `authorized_keys`에 주입(Injection)해야 합니다.
하지만 현재 라우터를 거치지 않는 Provider Network 구조(물리망을 직접 연결) 특성상 메타데이터 IP로 가는 경로를 찾지 못해 타임아웃이 발생했고, 결국 **키가 주입되지 않은 채로 부팅이 완료**되어 접속이 거부된 것입니다.

---

### 해결

**현상 1. 물리 인터페이스 상태 복구 (No route to host 해결)**
명령어를 실행하는 노드(Controller)와 VM이 떠 있는 노드(Compute) 양쪽 모두에서 브릿지에 물려있는 물리 랜카드가 `UP` 상태인지 확인하고 올려줍니다.

```bash
# 인터페이스 상태 확인
ip link show ens37

# DOWN 상태일 경우 활성화 (재부팅 시 유지를 위해 netplan에 등록하는 것을 권장)
sudo ip link set ens37 up
```

**현상 2. Config Drive를 이용한 인스턴스 재생성 (Permission denied 해결)**
네트워크를 통한 메타데이터 서비스 통신이 불가능한 환경에서는, OpenStack의 기능인 **Config Drive**를 사용해야 합니다.
이 기능을 활성화하면, OpenStack이 SSH 키와 초기 설정값들을 작은 **가상 CD-ROM(.iso)**으로 만들어 VM에 직접 마운트합니다. 
즉, `cloud-init`이 네트워크를 헤매지 않고 로컬 디스크에서 즉시 키를 읽어오므로 주입에 성공할 것입니다.

기존 인스턴스를 삭제하고 `--config-drive true` 옵션을 추가하여 다시 배포합니다.

```bash
# 1. 기존 에러 인스턴스 삭제
openstack server delete k8s-worker-01 k8s-worker-02

# 2. Config Drive 옵션을 켜서 워커 노드 재배포
openstack server create --flavor k8s-flavor \
  --image Ubuntu-22.04 \
  --network public_net \
  --key-name k8s_key \
  --config-drive true \
  k8s-worker-01
```

인스턴스가 재생성된 후 약 1\~2분 정도 기다린 뒤 SSH 접속을 시도하면 정상적으로 터미널에 진입할 수 있습니다.
