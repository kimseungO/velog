<h2 id="rdd프로그래밍">RDD프로그래밍</h2>
<h3 id="spark-application">Spark Application</h3>
<ul>
<li>RDD생성, RDD변형, RDD 내용 추출</li>
<li>Spark은 RDD에 대한 연산이 클러스터에서 병렬로 수행하도록 함</li>
</ul>
<h3 id="rdd">RDD</h3>
<ul>
<li>분산되어 있는 변경 불가능한 객체 집합</li>
<li>클러스터의 노드들에서 연산이 가능하도록 여러 파티션으로 나뉨</li>
<li>외부 데이터 집합을 load하거나 드라이버 자체적으로 객체 컬렉션을 분산시켜서 생성</li>
</ul>
<pre><code class="language-bash">textFile = sc.textFile(&quot;README.md&quot;)
nums = sc.parallelize([1, 2, 3, 4]) #RDD로 변환</code></pre>
<h3 id="rdd연산의-종류">RDD연산의 종류</h3>
<ul>
<li>Transformation<ul>
<li>기존 RDD에서 새로운 RDD를 만들어 냄</li>
<li>filter, map 등</li>
</ul>
</li>
<li>Action<ul>
<li>RDD를 기반으로 결과 값을 계산하여 드라이버 프로그램에 반환하거나 외부 스토리지(HDFS등)에 저장</li>
</ul>
</li>
</ul>
<pre><code class="language-bash">lines = sc.textFile(&quot;testfile&quot;)
filteredLines = lines.filter(lambda line: &quot;python&quot; in line) #transformation
filteredLined.first() #action
filteredLined.count() #action</code></pre>
<h3 id="rdd연산의-처리-방식">RDD연산의 처리 방식</h3>
<ul>
<li>Lazy evaluation<ul>
<li>action을 만날때 transformation 실행
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/422bfdc8-5b42-4d36-9c6b-a862386dc78b/image.png" /></li>
</ul>
</li>
</ul>
<h3 id="rdd는-매번-새로-생성됨">RDD는 매번 새로 생성됨</h3>
<ul>
<li>RDD.persist()</li>
<li>결과를 지속적으로 메모리에 유지 가능
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/ffcf1f7c-0da1-47fe-ac0e-12048c8b6aff/image.png" /></li>
</ul>