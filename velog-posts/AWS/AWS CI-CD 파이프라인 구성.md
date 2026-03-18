*현재 환경은 ECS 실습 진행중인 환경임

## 1. 나의 깃허브 계정과 AWS 연결하기

### 01. 개발자 도구 - 연결 생성

AWS 개발자 도구(CodeBuild)
설정 -> 연결(선택) -> 연결 생성
	-> 공급자 선택 -> Github
    -> Guihub 앱 연결 생성 -> 연결 이름 -> flask-github(예시)
-> Github에 연결
![](https://velog.velcdn.com/images/rtd7878/post/e615e5ef-323f-4cb1-a2ed-e1a53ada7780/image.png)

-> Sign in to GitHub to continue to AWS Connector for GitHub
	-> GitHub ID/Password 입력
    	-> Sign in

### 02. AWS Connector for GitHub
![](https://velog.velcdn.com/images/rtd7878/post/e7439f77-e4db-4f7d-992a-48f6818a57d8/image.png)

-> Authorize AWS Connector for GitHub

### 03. GitHub에 연결
-> Github 연결 설정 -> 새 앱 설치
![](https://velog.velcdn.com/images/rtd7878/post/b22ce5ed-6587-48a7-a204-74cd959a9dfd/image.png)

### 04. Install & Authorize AWS Connector for GitHub

-> Install & Authorize AWS Connector for GitHub
      -> Only select repositories (선택) 
      -> rusita-cloud/flask (선택)
->   Install & Authorize   (클릭)

### 05. 연결 생성
![](https://velog.velcdn.com/images/rtd7878/post/412258a7-951f-42b5-922a-5c78a073cee9/image.png)

-> GitHub 연결 설정
      -> 연결 이름 -> flask-github (확인) 
      -> 앱 설치 - 선택 사항 -> 55367047 (확인)
->   연결   (클릭)

## 2. CodeBuild Project 생성
### 01. 빌드 프로젝트 생성 및 Buildspec 작성
CodeBuild -> 프로젝트 빌드
   ->   프로젝트 생성
      -> 프로젝트 이름 -> flask-cicd-pipeline (입력)
      
-> Buildspec -> 빌드 명령
   ->   편집기로 전환   (클릭)

아래 코드의 <본인id>를 지우고 본인의 id를 넣고 편집기에 붙여넣기
```
version: 0.2

phases:
  pre_build:
    commands:
      - echo "AWS ECR Login"
      - aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <본인id>.dkr.ecr.ap-northeast-2.amazonaws.com
      - export IMAGE_TAG=$CODEBUILD_BUILD_NUMBER

  build:
    commands:
      - echo "Docker Image Build"
      - docker build -t rusita/flask:$IMAGE_TAG .
      - docker tag rusita/flask:$IMAGE_TAG <본인id>.dkr.ecr.ap-northeast-2.amazonaws.com/rusita/flask:$IMAGE_TAG

  post_build:
    commands:
      - echo "Docker Image Push"
      - docker push <본인id>.dkr.ecr.ap-northeast-2.amazonaws.com/rusita/flask:$IMAGE_TAG
      - echo "Image Definition"
      - printf '[{"name":"flask","imageUri":"<본인id>.dkr.ecr.ap-northeast-2.amazonaws.com/rusita/flask:%s"}]' "$IMAGE_TAG" > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
```
-> 빌드 프로젝트 생성 (클릭)

### 02. 빌드 프로젝트 IAM 권한 추가
개발자 도구
CodeBuild -> 프로젝트 빌드 -> flask-cicd-pipeline (클릭)
   -> 서비스 역할 (링크 클릭) 

IAM
역할 -> codebuild-flask-cicd-pipeline-service-role -> 권한 탭
   -> 권한 정책 -> 권한 추가 (클릭) -> 정책 연결(클릭)
      -> container 검색 -> AmazonEC2ContainerRegistryFullAccess (선택) ->   권한 추가   (클릭)
      
![](https://velog.velcdn.com/images/rtd7878/post/8fedb654-a833-4c05-a690-9a5631054a7f/image.png)


## 3. CodePipeline 설정
### 01. CodePipeline 생성
개발자 도구
-> CodePipeline -> 파이프라인 ->   파이프라인 생성   (클릭)

사용자 지정 파이프라인 빌드 (선택) 
-> 다음

파이프라인 이름 (입력) 
-> 다음

소스 공급자 -> GitHub(GitHub 앱을 통해)  (선택) -> 연결
-> flask-github (선택)
-> 리포지토리 이름 (본인 저장소 선택)
-> 기본 브랜치 (선택)
-> 다음

-> 빌드 공급자 -> 기타 빌드 공급사 (선택) -> AWS CodeBuild (선택)
-> 프로젝트 이름 (선택)
-> 다음

![](https://velog.velcdn.com/images/rtd7878/post/663380e1-0c0b-49b9-abba-e416ea0f1b27/image.png)
-> 테스트 스테이지 건너뛰기
(본 실습에서 테스트 스테이지는 건너뜁니다.)

-> 배포 공급자 -> Amazon ECS (선택)
-> 클러스터 이름 ->  (선택)
-> 서비스 이름 ->  (선택)
-> 이미지 정의 파일 - 선택 사항 -> imagedefinitions.json (입력)
-> 다음

-> 파이프라인 생성

![](https://velog.velcdn.com/images/rtd7878/post/d026ec1e-35d1-40c5-b6b6-34f2d513b8f1/image.png)
Source
![](https://velog.velcdn.com/images/rtd7878/post/02d09540-298c-4c3a-923b-72d50d28585a/image.png)
Build
![](https://velog.velcdn.com/images/rtd7878/post/77f1b6a3-1e0c-438f-af21-07a90dbe2198/image.png)
Deploy

![](https://velog.velcdn.com/images/rtd7878/post/71e3c8f1-9f2a-43f4-ab3c-1d20b1463e13/image.png)
배포 완료

## 4. EC2 접속 후 파일 수정해서 CI/CD 동작 확인
### 01. 파일 수정
![](https://velog.velcdn.com/images/rtd7878/post/bb528302-f1f1-40d7-bc41-b0f50277e946/image.png)

### 02. 깃허브 푸쉬
![](https://velog.velcdn.com/images/rtd7878/post/a93bfafc-e1de-43e1-9fae-aeb335bc5720/image.png)

### 결과
![](https://velog.velcdn.com/images/rtd7878/post/89ff3d8b-c17a-41c2-ad48-83ddcb930b0c/image.png)파이프라인 동작
![](https://velog.velcdn.com/images/rtd7878/post/a276677e-efea-4dab-8697-c3dda1a4fb30/image.png)웹 페이지 업데이트 확인
