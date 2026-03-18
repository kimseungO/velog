<h2 id="11what-is-pyspark">1.1What is PySpark?</h2>
<h3 id="111-what-is-spark">1.1.1 what is Spark?</h3>
<ul>
<li><strong>Spark</strong> : “대규모 데이터 처리를 위한 통합 분석 엔진”</li>
<li>하드웨어 확장 대신 <strong>여러 시스템에 걸친 확장</strong>을 통해 점점 더 많은 양의 데이터 처리 가능</li>
<li>비용 대비 효율성 좋음</li>
</ul>
<h3 id="112-pyspark--spark--python">1.1.2 PySpark = Spark + Python</h3>
<ul>
<li>Spark 자체는 Scala.2로 코딩 되어 있음.</li>
<li>Python : 다양한 플랫폼과 다양한 작업에 사용할 수 있는 동적 범용 언어<ul>
<li>이런 다양성과 표현력 덕분에 Spark에 적합하다</li>
</ul>
</li>
</ul>
<h3 id="113-why-pyspark">1.1.3 Why PySpark?</h3>
<ul>
<li><strong>PYSPARK IS FAST</strong><ul>
<li>Hadoop을 기반으로 만들어짐</li>
<li>공격적인 쿼리 최적화, RAM의 효율적인 사용</li>
</ul>
</li>
<li><strong>PYSPARK IS EXPRESSIVE</strong><ul>
<li>이해하기 쉬운 언어 Python</li>
<li>SQL 어휘를 차용하고 확장</li>
<li>사전 지식 없이도 대강 이해 가능
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/62e9ecf9-4625-4205-b6f7-48d8fc23f1ed/image.png" /></li>
</ul>
</li>
</ul>
<ul>
<li><p><strong>PYSPARK IS VERSATILE</strong></p>
<ul>
<li>PySpark의 주요 장점인 “<strong>다양성”</strong></li>
<li>다양성1: 프레임워크의 가용성<ul>
<li>클라우드 제공업체 AWS, GCP, Azure등 모두 관리형 Spark 클러스터를 갖추고 있다.</li>
<li>클러스터 확장시에 Spark로 쉽게 확장 가능</li>
</ul>
</li>
<li>다양성2: 생태계<ul>
<li>다양한 언어<ul>
<li>Scala, Java, R, SQL</li>
</ul>
</li>
<li>오픈소스<ul>
<li>활발한 개발자 및 사용자 커뮤니티를 보유하고 있으며, 다양한 라이브러리 및 도구가 개발되어 있다.</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
<li><p><strong>WHERE PYSPARK FALLS SHORT</strong></p>
<ul>
<li><p>매우 작은 데이터 셋을 빠르게 처리하는 경우 부적절</p>
</li>
<li><p>Spark는 Scala기반이기 때문에 Python 코드는 JVM(Java Virtual Machine,Java 및 Scala 코드를 구동하는 런타임) 명령간에 변환되어야 함.</p>
<ul>
<li>⇒RDD 데이터 구조를 사용하거나 Python 사용자 정의 함수를 정의할 때 여전히 작업 속도가 느려질 수 있다.</li>
</ul>
</li>
<li><p>클러스터 관리의 난해함</p>
<ul>
<li>프로그래밍은 간단할 수 있으나 관리는 복잡할 수 있다.</li>
</ul>
<h2 id="12-pyspark-작동-방식">1.2 PySpark 작동 방식</h2>
<h3 id="121-클러스터-관리자를-통한-일부-물리적-계획">1.2.1 클러스터 관리자를 통한 일부 물리적 계획</h3>
</li>
<li><p>클러스터 관리자 : 프로그램에 할당할 용량을 계획</p>
<ul>
<li>사용 가능한 컴퓨팅 리소스가 있는 머신을 살펴보고 필요한 수의 실행기를 실행하기 전에 리소스를 보호한다.</li>
<li>용량에 대한 모든 지침은 SparkContext에 있다.</li>
<li>지침에 특정 용량이 언급되지 않은 경우, 클러스터 관리자는 Spark 설치에서 규정한 기본 용량 할당</li>
</ul>
<h3 id="122-게으른-리더를-통해-효율적으로-만들어진-공장">1.2.2 게으른 리더를 통해 효율적으로 만들어진 공장</h3>
</li>
<li><p>Spark의 가장 기본적인 측면인 “지연 평가 기능”</p>
<ul>
<li>명령을 실행할 때까지 대기, 필요한 경우에만 연산</li>
<li>효율적인 실행 계획: 불필요한 연산 방지</li>
<li>성능 향상: 중간 단계의 불필요한 연산 방지</li>
</ul>
</li>
</ul>
</li>
</ul>
<ol>
<li><strong>변환(Transformations):</strong><ul>
<li><strong>특징:</strong> 변환은 원본 데이터를 가져와 새로운 데이터셋을 생성하는 작업입니다. 그러나 실제 변환 작업은 아직 수행되지 않고, 실행 계획만 생성됩니다. 이는 지연평가의 핵심입니다.</li>
<li><strong>예시:</strong> <strong><code>map</code></strong>, <strong><code>filter</code></strong>, <strong><code>groupBy</code></strong>, <strong><code>join</code></strong> 등의 연산이 변환 작업에 해당합니다.</li>
<li><strong>사용 목적:</strong> 주로 데이터의 형태를 변경하거나 조작하고, 분산 데이터셋을 다양한 형태로 변환하는 데 사용됩니다.</li>
<li><strong>실행 시점:</strong> 변환 작업은 액션을 트리거하기 전까지 실제로 수행되지 않습니다.</li>
</ul>
</li>
<li><strong>액션(Actions):</strong><ul>
<li><strong>특징:</strong> 액션은 지연평가된 연산들을 트리거하고 결과를 생성하는 작업입니다. 즉, 실제 데이터 처리가 시작되고 결과를 얻게 됩니다.</li>
<li><strong>예시:</strong> <strong><code>count</code></strong>, <strong><code>collect</code></strong>, <strong><code>saveAsTextFile</code></strong> 등의 연산이 액션에 해당합니다.</li>
<li><strong>사용 목적:</strong> 주로 최종 결과를 얻기 위해 사용되며, 실제로 데이터 처리 작업이 발생합니다.</li>
<li><strong>실행 시점:</strong> 액션을 호출할 때 지연평가된 변환 작업이 수행되고, 결과를 생성합니다.</li>
</ul>
</li>
</ol>