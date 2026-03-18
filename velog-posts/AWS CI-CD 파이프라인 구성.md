<p>*현재 환경은 ECS 실습 진행중인 환경임</p>
<h2 id="1-나의-깃허브-계정과-aws-연결하기">1. 나의 깃허브 계정과 AWS 연결하기</h2>
<h3 id="01-개발자-도구---연결-생성">01. 개발자 도구 - 연결 생성</h3>
<p>AWS 개발자 도구(CodeBuild)
설정 -&gt; 연결(선택) -&gt; 연결 생성
    -&gt; 공급자 선택 -&gt; Github
    -&gt; Guihub 앱 연결 생성 -&gt; 연결 이름 -&gt; flask-github(예시)
-&gt; Github에 연결
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/e615e5ef-323f-4cb1-a2ed-e1a53ada7780/image.png" /></p>
<p>-&gt; Sign in to GitHub to continue to AWS Connector for GitHub
    -&gt; GitHub ID/Password 입력
        -&gt; Sign in</p>
<h3 id="02-aws-connector-for-github">02. AWS Connector for GitHub</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/e7439f77-e4db-4f7d-992a-48f6818a57d8/image.png" /></p>
<p>-&gt; Authorize AWS Connector for GitHub</p>
<h3 id="03-github에-연결">03. GitHub에 연결</h3>
<p>-&gt; Github 연결 설정 -&gt; 새 앱 설치
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/b22ce5ed-6587-48a7-a204-74cd959a9dfd/image.png" /></p>
<h3 id="04-install--authorize-aws-connector-for-github">04. Install &amp; Authorize AWS Connector for GitHub</h3>
<p>-&gt; Install &amp; Authorize AWS Connector for GitHub
      -&gt; Only select repositories (선택) 
      -&gt; rusita-cloud/flask (선택)
-&gt;   Install &amp; Authorize   (클릭)</p>
<h3 id="05-연결-생성">05. 연결 생성</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/412258a7-951f-42b5-922a-5c78a073cee9/image.png" /></p>
<p>-&gt; GitHub 연결 설정
      -&gt; 연결 이름 -&gt; flask-github (확인) 
      -&gt; 앱 설치 - 선택 사항 -&gt; 55367047 (확인)
-&gt;   연결   (클릭)</p>
<h2 id="2-codebuild-project-생성">2. CodeBuild Project 생성</h2>
<h3 id="01-빌드-프로젝트-생성-및-buildspec-작성">01. 빌드 프로젝트 생성 및 Buildspec 작성</h3>
<p>CodeBuild -&gt; 프로젝트 빌드
   -&gt;   프로젝트 생성
      -&gt; 프로젝트 이름 -&gt; flask-cicd-pipeline (입력)</p>
<p>-&gt; Buildspec -&gt; 빌드 명령
   -&gt;   편집기로 전환   (클릭)</p>
<p>아래 코드의 &lt;본인id&gt;를 지우고 본인의 id를 넣고 편집기에 붙여넣기</p>
<pre><code>version: 0.2

phases:
  pre_build:
    commands:
      - echo &quot;AWS ECR Login&quot;
      - aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin &lt;본인id&gt;.dkr.ecr.ap-northeast-2.amazonaws.com
      - export IMAGE_TAG=$CODEBUILD_BUILD_NUMBER

  build:
    commands:
      - echo &quot;Docker Image Build&quot;
      - docker build -t rusita/flask:$IMAGE_TAG .
      - docker tag rusita/flask:$IMAGE_TAG &lt;본인id&gt;.dkr.ecr.ap-northeast-2.amazonaws.com/rusita/flask:$IMAGE_TAG

  post_build:
    commands:
      - echo &quot;Docker Image Push&quot;
      - docker push &lt;본인id&gt;.dkr.ecr.ap-northeast-2.amazonaws.com/rusita/flask:$IMAGE_TAG
      - echo &quot;Image Definition&quot;
      - printf '[{&quot;name&quot;:&quot;flask&quot;,&quot;imageUri&quot;:&quot;&lt;본인id&gt;.dkr.ecr.ap-northeast-2.amazonaws.com/rusita/flask:%s&quot;}]' &quot;$IMAGE_TAG&quot; &gt; imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json</code></pre><p>-&gt; 빌드 프로젝트 생성 (클릭)</p>
<h3 id="02-빌드-프로젝트-iam-권한-추가">02. 빌드 프로젝트 IAM 권한 추가</h3>
<p>개발자 도구
CodeBuild -&gt; 프로젝트 빌드 -&gt; flask-cicd-pipeline (클릭)
   -&gt; 서비스 역할 (링크 클릭) </p>
<p>IAM
역할 -&gt; codebuild-flask-cicd-pipeline-service-role -&gt; 권한 탭
   -&gt; 권한 정책 -&gt; 권한 추가 (클릭) -&gt; 정책 연결(클릭)
      -&gt; container 검색 -&gt; AmazonEC2ContainerRegistryFullAccess (선택) -&gt;   권한 추가   (클릭)</p>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/8fedb654-a833-4c05-a690-9a5631054a7f/image.png" /></p>
<h2 id="3-codepipeline-설정">3. CodePipeline 설정</h2>
<h3 id="01-codepipeline-생성">01. CodePipeline 생성</h3>
<p>개발자 도구
-&gt; CodePipeline -&gt; 파이프라인 -&gt;   파이프라인 생성   (클릭)</p>
<p>사용자 지정 파이프라인 빌드 (선택) 
-&gt; 다음</p>
<p>파이프라인 이름 (입력) 
-&gt; 다음</p>
<p>소스 공급자 -&gt; GitHub(GitHub 앱을 통해)  (선택) -&gt; 연결
-&gt; flask-github (선택)
-&gt; 리포지토리 이름 (본인 저장소 선택)
-&gt; 기본 브랜치 (선택)
-&gt; 다음</p>
<p>-&gt; 빌드 공급자 -&gt; 기타 빌드 공급사 (선택) -&gt; AWS CodeBuild (선택)
-&gt; 프로젝트 이름 (선택)
-&gt; 다음</p>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/663380e1-0c0b-49b9-abba-e416ea0f1b27/image.png" />
-&gt; 테스트 스테이지 건너뛰기
(본 실습에서 테스트 스테이지는 건너뜁니다.)</p>
<p>-&gt; 배포 공급자 -&gt; Amazon ECS (선택)
-&gt; 클러스터 이름 -&gt;  (선택)
-&gt; 서비스 이름 -&gt;  (선택)
-&gt; 이미지 정의 파일 - 선택 사항 -&gt; imagedefinitions.json (입력)
-&gt; 다음</p>
<p>-&gt; 파이프라인 생성</p>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/d026ec1e-35d1-40c5-b6b6-34f2d513b8f1/image.png" />
Source
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/02d09540-298c-4c3a-923b-72d50d28585a/image.png" />
Build
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/77f1b6a3-1e0c-438f-af21-07a90dbe2198/image.png" />
Deploy</p>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/71e3c8f1-9f2a-43f4-ab3c-1d20b1463e13/image.png" />
배포 완료</p>
<h2 id="4-ec2-접속-후-파일-수정해서-cicd-동작-확인">4. EC2 접속 후 파일 수정해서 CI/CD 동작 확인</h2>
<h3 id="01-파일-수정">01. 파일 수정</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/bb528302-f1f1-40d7-bc41-b0f50277e946/image.png" /></p>
<h3 id="02-깃허브-푸쉬">02. 깃허브 푸쉬</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/a93bfafc-e1de-43e1-9fae-aeb335bc5720/image.png" /></p>
<h3 id="결과">결과</h3>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/89ff3d8b-c17a-41c2-ad48-83ddcb930b0c/image.png" />파이프라인 동작
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/a276677e-efea-4dab-8697-c3dda1a4fb30/image.png" />웹 페이지 업데이트 확인</p>