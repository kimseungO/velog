
### 1. **도커 설치 및 설정**

- **도커 버전 확인**
  ```bash
  docker --version
  ```
- **도커 정보 확인**
  ```bash
  docker info
  ```

### 2. **도커 이미지 관리**

- **도커 이미지 검색**
  ```bash
  docker search <이미지 이름>
  ```
- **도커 이미지 다운로드 (Pull)**
  ```bash
  docker pull <이미지 이름>
  ```
- **도커 이미지 목록 보기**
  ```bash
  docker images
  ```
- **도커 이미지 삭제**
  ```bash
  docker rmi <이미지 이름 또는 ID>
  ```
- **이미지 태그 설정**
  ```bash
  docker tag <이미지 이름> <새 이미지 이름>:<태그>
  ```
- **도커 이미지 업로드 (Push)**
  ```bash
  docker push <이미지 이름>:<태그>
  ```

### 3. **도커 컨테이너 관리**

- **도커 컨테이너 실행 및 생성**
  ```bash
  docker run <옵션> <이미지 이름>
  ```
  - 주요 옵션:
    - `-d`: 백그라운드에서 실행 (detached mode)
    - `-it`: 인터랙티브 모드 + TTY
    - `--name`: 컨테이너 이름 지정
    - `-p`: 포트 매핑 (예: `-p 8080:80`)
    - `-v`: 볼륨 마운트 (예: `-v /host/path:/container/path`)
  
- **도커 실행 중인 컨테이너 목록 보기**
  ```bash
  docker ps
  ```
- **모든 도커 컨테이너 목록 보기 (중지된 컨테이너 포함)**
  ```bash
  docker ps -a
  ```
- **컨테이너 중지**
  ```bash
  docker stop <컨테이너 이름 또는 ID>
  ```
- **컨테이너 시작**
  ```bash
  docker start <컨테이너 이름 또는 ID>
  ```
- **컨테이너 재시작**
  ```bash
  docker restart <컨테이너 이름 또는 ID>
  ```
- **컨테이너 삭제**
  ```bash
  docker rm <컨테이너 이름 또는 ID>
  ```
- **컨테이너 로그 확인**
  ```bash
  docker logs <컨테이너 이름 또는 ID>
  ```
- **컨테이너 내부에 접속**
  ```bash
  docker exec -it <컨테이너 이름 또는 ID> /bin/bash
  ```
  - 관리자로 접속
  ```bash
  docker exec -it --user 0 <컨테이너 이름 또는 ID> /bin/bash
  ```

### 4. **도커 네트워크 관리**

- **도커 네트워크 목록 보기**
  ```bash
  docker network ls
  ```
- **도커 네트워크 생성**
  ```bash
  docker network create <네트워크 이름>
  ```
- **도커 네트워크 삭제**
  ```bash
  docker network rm <네트워크 이름>
  ```
- **컨테이너를 네트워크에 연결**
  ```bash
  docker network connect <네트워크 이름> <컨테이너 이름>
  ```
- **컨테이너를 네트워크에서 분리**
  ```bash
  docker network disconnect <네트워크 이름> <컨테이너 이름>
  ```

### 5. **도커 볼륨 관리**

- **도커 볼륨 목록 보기**
  ```bash
  docker volume ls
  ```
- **도커 볼륨 생성**
  ```bash
  docker volume create <볼륨 이름>
  ```
- **도커 볼륨 삭제**
  ```bash
  docker volume rm <볼륨 이름>
  ```
- **도커 볼륨 상세 정보 보기**
  ```bash
  docker volume inspect <볼륨 이름>
  ```

### 6. **Dockerfile 빌드 및 이미지 생성**

- **도커 이미지 빌드**
  ```bash
  docker build -t <이미지 이름>:<태그> .
  ```
  - `-t`: 이미지 이름과 태그 지정
  - `.`: 현재 디렉토리의 `Dockerfile`을 사용

### 7. **도커 컴포즈 (docker-compose)**

- **도커 컴포즈 실행**
  ```bash
  docker-compose up
  ```
- **백그라운드에서 도커 컴포즈 실행**
  ```bash
  docker-compose up -d
  ```
- **도커 컴포즈 중지**
  ```bash
  docker-compose down
  ```
- **도커 컴포즈 특정 서비스 재시작**
  ```bash
  docker-compose restart <서비스 이름>
  ```
- **도커 컴포즈 로그 보기**
  ```bash
  docker-compose logs
  ```
- **도커 컴포즈 빌드**
  ```bash
  docker-compose build
  ```
