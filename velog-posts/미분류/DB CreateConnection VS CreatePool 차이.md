> 웹 서비스를 개발할 때 필수적으로 설계해야할 부분인 DB를 어떤 방식으로 연결해야 하는지에 대한 글입니다.

## Active-Active VS Active-Standby
보통의 웹 서비스는 안정성을 위해 Master DB를 하나 두고 Candidate DB를 하나 두어서 장애에 대비합니다.
이 Candidate DB 동작 방식은 Active-Acive 방식과 Active-Standby 형식으로 나뉩니다.

- **Active-Active**
이 방식은 두 DB가 동시에 동작하며 동시에 읽기/쓰기 동작이 가능합니다.
성능 높지만 구성이 복잡하고, 충돌 관리가 필요합니다.

- **Active-Standby**
이 방식은 평소에 Primary DB만 작동하고 장애시에 Standby DB가 자동 승격되어 failover 됩니다.

> 그렇다면 failover가 일어날 때 웹 어플리케이션 입장에서는 어떻게 DB Connection을 처리할까?

## CreateConnection VS CreatePool
DB Connection을 하기 위해 두 가지 방식이 있습니다.

### 첫째로 CreateConnection 방식입니다.

이 방식은 요청이 올 때마다:
→ DB 연결 생성
→ 쿼리 실행
→ 연결 유지 (끊지 않음)

그러나, 연결이 끊기면:
→ 재연결 로직 없음
→ 에러 발생
→ 직접 재연결 코드 작성 필요

**그래서 CreateConnection 방식은 단발성 작업에 주로 쓰입니다.**
→ DB 마이그레이션 스크립트
→ 배치 작업 (1회 실행 후 종료)
→ 관리자 CLI 도구

또한 단일 연결로 충분한 경우에도 쓰입니다.
→ 동시 요청이 없는 환경
→ 개발/테스트 환경에서 간단한 확인

### 두 번째로 CreatePool 방식입니다.

이 방식은 앱 시작 시:
→ 연결 N개를 미리 생성해서 Pool에 보관

요청이 오면:
→ Pool에서 연결 하나 꺼냄
→ 쿼리 실행
→ 연결 Pool에 반납 (재사용)

연결이 끊기면:
→ Pool이 감지
→ 끊긴 연결 제거
→ 새 연결 자동 생성
→ 대기 중인 요청은 새 연결로 처리

**한 마디로 어플리케이션 단에서 자동으로 failover가 되는 DB Connection 방식입니다.**
그래서 실제 서비스에서 StandbyDB를 두고 서비스의 안정성을 위해 일반적으로 사용됩니다.

## 비교 실험
마지막으로 DB재시작을 통해 failover가 잘 이뤄지는지 두 방식을 실습해보겠습니다.
실험은 NHN Cloud RDS for MySQL로 진행했습니다.
![](https://velog.velcdn.com/images/rtd7878/post/70de8b00-2784-44e3-9c18-3cd1f0985dba/image.png)

아래 명령어로 실시간 DB연결을 모니터링 해보겠습니다.
```bash
while true; do
  echo -n "$(date '+%H:%M:%S') → "
  curl -s http://{IP}/api/users | head -c 50
  echo ""
  sleep 1
done

```

### 1. CreateConnection
![](https://velog.velcdn.com/images/rtd7878/post/64435367-7bd8-443e-988f-4c84c29bed19/image.png)
DB 재시작이 되면서 502 에러를 뱉었습니다.
하지만 곧 연결이 되었습니다.
그 이유는 NHN Cloud의 RDS for MySQL 서비스가 재시작시 자동으로 failover를 해줬기 때문입니다. (인프라 단의 failover)

### 2. CreatePool
![](https://velog.velcdn.com/images/rtd7878/post/b52e9b8b-4e34-46ea-a31c-2c37d6a60b52/image.png)
DB 재시작이 되면서 DB 연결이 끊겼지만 에러가 나오진 않았습니다. 곧 failover가 이뤄지며 DB가 무사히 연결되는 모습입니다.


최종 요약을 해보자면,
테스트 및 단발성을 위한 DB connection은 CreateConneciton 방식으로, 실제 서비스를 위한 DB connection은 CreatePool 방식으로 구성해주면 됩니다.