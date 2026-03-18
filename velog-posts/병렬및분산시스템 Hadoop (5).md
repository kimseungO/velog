<h2 id="맵리듀스">맵리듀스</h2>
<ul>
<li>대규모 데이터 분석/처리를 위한 프로그래밍 모델</li>
<li>맵과 리듀스라는 두 개의 함수로 구성</li>
<li>하둡의 코어 프로젝트</li>
<li>다양한 언어들로 작성가능(자바, 루비, 파이선, 씨++)</li>
</ul>
<h2 id="맵리듀스-동작">맵리듀스 동작</h2>
<h3 id="맵리듀스-처리-과정-5단계">맵리듀스 처리 과정 5단계</h3>
<ul>
<li>입력 데이터 분리<ul>
<li>입력데이터를 키와 값 형식의 데이터로 분류</li>
<li>입력 스플릿 단위로 분류된 데이터를 맵함수로 전달</li>
</ul>
</li>
<li>맵 메소드<ul>
<li>키와 값으로 구성된 데이터를 입력 받아 새로운 키와 값을 ㅗ구성된 데이터를 출력</li>
<li>맵: (k1, v1) → list(k2, v2)</li>
</ul>
</li>
<li>정렬, 병합<ul>
<li>리듀스 부하 감소 목적</li>
</ul>
</li>
<li>리듀스 메소드<ul>
<li>집계연산을 통한 최종 목록 생성</li>
<li>리듀스 : (k, list(v2)) → list(k3, v3)</li>
</ul>
</li>
<li>저장<ul>
<li>최종 출력
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/c40338e2-5e8a-4e21-ae8e-4a1f844cf664/image.png" /></li>
</ul>
</li>
</ul>
<h2 id="맵리듀스-아키텍처">맵리듀스 아키텍처</h2>
<ul>
<li>jobClient<ul>
<li>공통 파일을 분산 파일 시스템에 복사</li>
<li>jobTracker에 Map-Reduce 잡을 제출</li>
</ul>
</li>
<li>JobTracker<ul>
<li>제출된 맵 리듀스 잡을 스케쥴링</li>
<li>태스크 트래커에 태스크(Map/Reduce)를 할당</li>
</ul>
</li>
<li>TaskTracker<ul>
<li>할당된 태스크를 수행</li>
<li>수행되는 태스크는 별도의 JVM에서 실행됨</li>
<li>일반적으로 HDFS의 Data-node와 같은 곳에서 실행됨. - 데이터 지역성 극대화
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/4d556ab4-3adc-4ccd-b0c3-7f4a9dc9c682/image.png" /></li>
</ul>
</li>
</ul>
<h3 id="클라이언트">클라이언트</h3>
<ul>
<li>사용자가 실행한 맵리듀스 프로그램과 맵리듀스 API를 의미</li>
<li>사용자는 맵리듀스 API를 이용하여 프로그램을 개발</li>
<li>잡트래커에 잡을 요청<ul>
<li>잡: 하나의 작업단위</li>
</ul>
</li>
</ul>
<h3 id="잡트래커">잡트래커</h3>
<ul>
<li>하둡 클러스터에 등록된 전체 잡의 스케줄링을 관리</li>
</ul>
<h3 id="잡트래커-동작">잡트래커 동작</h3>
<ul>
<li>새로운 잡을 요청하면 잡트래커는 몇 개의 맵과 리듀스를 실행할지 계산</li>
<li>어떤 태스크트래커에서 실행할지 결정</li>
<li>실행 요청을 받은 태스크트래커는 맵리듀스 프로그램 실행
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/ac016f9d-bf8e-45d7-8f31-489baee077fb/image.png" /></li>
</ul>
<h3 id="태스크-트래커">태스크 트래커</h3>
<ul>
<li>사용자가 설정한 맵리듀스 프로그램을 실행</li>
<li>하둡의 데이터노드에서 실행되는 데몬</li>
<li>잡트래커가 요청한 맵과 리듀스 개수 만큼 맵태스크와 리듀스태스크를 생성</li>
<li><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/8adfca9f-ab89-49e7-9d5d-534e0fcda878/image.png" /></li>
</ul>