<h2 id="apache-spark-등장">Apache Spark 등장</h2>
<h3 id="인메모리-기반의-대용량-데이터-고속-처리-엔진">인메모리 기반의 대용량 데이터 고속 처리 엔진</h3>
<ul>
<li>하둡의 맵리듀스 작업처리 속도보다 최대 100배 빠른 성능 구현</li>
<li>범용의 분산 클러스터 컴퓨팅 프레임 워크</li>
</ul>
<h3 id="쉬운-사용">쉬운 사용</h3>
<ul>
<li>JAVA, Python, Scala, R, SQL 기반 응용 개발 가능</li>
</ul>
<h3 id="mapreduce의-단점">MapReduce의 단점</h3>
<ul>
<li>중간과정에 많은 맵과 리듀스 과정을 hdfs에 기록함(Fault Tolerant(장애대응))</li>
<li>많은 io 발생
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/be18ae1c-5890-43fe-a66d-e6df3eb2c1ba/image.png" /></li>
</ul>
<h2 id="rddresilient-distributed-datasets">RDD(Resilient Distributed Datasets)</h2>
<p><strong>탄력있는 분산 데이터셋</strong></p>
<ul>
<li>분산 처리 및 장애복구가 가능하다는 뜻을 내포</li>
</ul>
<p><strong>Spark 에서는 내부적으로 연산하는 데이터들을 모두 RDD 타입으로 처리</strong></p>
<p><strong>Spark application 개발은 아래의 3가지에 대한 이해를 바탕으로 시작</strong></p>
<ul>
<li>RDD</li>
<li>RDD 변환 API (Scala/ Python/ java/ R)</li>
<li>RDD 변환 API로 만들어진 SQL/ ML/ ../</li>
</ul>
<p><strong>Immutable, partitioned collections of record</strong></p>
<ul>
<li>immutable: 생성된 RDD는 수정 안됨</li>
<li>partitioned: RDD를 분할해서 여러 노드에 분산 처리</li>
</ul>
<p><strong>RDD에 대한 연산 처리 방식</strong></p>
<ul>
<li>coarse grained (not fine grained(파일내 일부만 수정 불가능)) 방식으로 진행됨 ⇒ 연산 단위가 한 파일</li>
<li>RDD에 속한 레코드 개별적으로 적용되는 연산이 아니라 전체에 적용되는 연산을 지원함</li>
</ul>
<p><strong>Lineage(계보)</strong></p>
<ul>
<li>어떤 RDD가 생성되기 까지의 역사</li>
<li>컴퓨터가 고장이나 오류가 난 경우 Lineage를 다시 수행하면 RDD를 재생할 수 있음
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/ad31c7a6-ccee-48b4-b9c2-7a1082364fd8/image.png" /></li>
</ul>
<ul>
<li>한 작업 수행 때마다 RDD 하나가 만들어지는 모습</li>
</ul>