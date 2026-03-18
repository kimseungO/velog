<h2 id="21-setting-up-the-pyspark-shell">2.1 Setting up the PySpark shell</h2>
<h3 id="211-the-sparksession-entry-point">2.1.1 The SparkSession entry point</h3>
<pre><code class="language-python">from pyspark.sql import SparkSession 
spark = (SparkSession  
  .builder 
  .appName(&quot;Pride and Prejudice Vocabulary Analysis.&quot;) 
  .getOrCreate())</code></pre>
<ul>
<li><p>PySpark 애플리케이션을 시작하고 Spark 클러스터에 연결하는 데 사용됨.</p>
</li>
<li><p><strong><code>spark</code></strong> 변수는 이후 PySpark 기능에 접근할 때 사용될 SparkSession 객체를 나타냄</p>
</li>
<li><p>코드 설명</p>
<pre><code class="language-python">  from pyspark.sql import SparkSession </code></pre>
<ul>
<li><p><strong><code>pyspark.sql</code></strong>에서 <strong><code>SparkSession</code></strong> 클래스를 임포트.
이는 PySpark에서 데이터 프레임 및 관련 기능을 사용하기 위한 핵심 클래스</p>
<pre><code class="language-python">from pyspark.sql import SparkSession 
spark = (SparkSession  
.builder 
.appName(&quot;Pride and Prejudice Vocabulary Analysis.&quot;) 
.getOrCreate())</code></pre>
</li>
<li><p><strong><code>SparkSession.builder</code></strong>를 사용하여 SparkSession 객체를 생성. 
빌더 패턴을 사용하여 다양한 구성 옵션을 설정할 수 있다.</p>
</li>
<li><p><strong><code>appName(&quot;Pride and Prejudice Vocabulary Analysis.&quot;)</code></strong>은 Spark 애플리케이션의 이름을 지정하는 메서드.</p>
</li>
<li><p><strong><code>getOrCreate()</code></strong> 메서드는 이미 존재하는 SparkSession을 반환하거나 존재하지 않는 경우 새로운 SparkSession을 생성.</p>
</li>
</ul>
</li>
</ul>
<pre><code class="language-bash">$ spark.sparkContext  
# &lt;SparkContext master=local[*] appName=...&gt;</code></pre>
<ul>
<li><strong><code>spark</code></strong> 변수는 앞서 생성한 SparkSession 객체를 나타냄.</li>
<li>SparkContext의 정보 표시</li>
</ul>
<h3 id="212-configuring-how-chatty-spark-is-the-log-level">2.1.2 Configuring how chatty spark is: The log level</h3>
<pre><code class="language-python">Spark.sparkContext.setLogLevel(&quot;ALL&quot;)</code></pre>
<ul>
<li>로그 레벨 조정<ul>
<li>로그의 출력 양을 제어하고 원하는 수준의 로그 표시<ul>
<li><strong><code>&quot;ALL&quot;</code></strong>: 가장 상세한 로그 레벨로 모든 로그를 출력합니다.</li>
<li><strong><code>&quot;DEBUG&quot;</code></strong>: 디버그 정보를 포함한 모든 로그를 출력합니다.</li>
<li><strong><code>&quot;INFO&quot;</code></strong>: 정보 수준 이상의 로그를 출력합니다.</li>
<li><strong><code>&quot;WARN&quot;</code></strong>: 경고 수준 이상의 로그를 출력합니다.</li>
<li><strong><code>&quot;ERROR&quot;</code></strong>: 오류 수준 이상의 로그를 출력합니다.</li>
<li><strong><code>&quot;FATAL&quot;</code></strong>: 치명적인 오류 수준의 로그를 출력합니다.</li>
<li><strong><code>&quot;OFF&quot;</code></strong>: 모든 로그를 출력하지 않습니다.</li>
</ul>
</li>
</ul>
</li>
</ul>
<h2 id="22-mapping-our-program">2.2 Mapping our program</h2>
<ul>
<li><p>데이터 분석을 미리 설계</p>
<ul>
<li>구조와 작동 방식을 먼저 생각하고 설계함으로 발생 문제 예상 가능</li>
<li>코드 작성 속도 향상</li>
<li>신뢰성과 향상</li>
</ul>
</li>
<li><p>매핑 단계</p>
<ol>
<li><strong>Read</strong> - 입력 데이터를 읽습니다(일반 텍스트로 가정).</li>
<li><strong>Token</strong> - 각 단어를 토큰화합니다.</li>
<li><strong>Clean</strong> - 모든 구두점 및 단어가 아닌 토큰을 제거합니다. 각 단어를 소문자로 변환합니다.</li>
<li><strong>Count</strong> - 텍스트에 포함된 각 단어의 빈도를 계산합니다.</li>
<li><strong>Answer</strong> - 상위 10개(또는 20개, 50개, 100개)를 반환합니다.</li>
</ol>
</li>
<li><p>“영어에서 가장 많이 쓰이는 단어는 무엇인가?” 문제
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/a9e80c2a-5f58-41f4-823b-49594781da45/image.png" /></p>
</li>
</ul>
<h2 id="23-ingest-and-explore-데이터-변환을-위한-스테이지">2.3 Ingest and explore: 데이터 변환을 위한 스테이지</h2>
<ul>
<li>데이터 변환을 위한 PySpark 프로그램에서 접하게 되는 세 가지 작업<ol>
<li>데이터를 구조로 수집</li>
<li>구조(또는 스키마)를 출력하여 데이터의 구성 확인</li>
<li>데이터 샘플을 표시</li>
</ol>
</li>
</ul>
<h3 id="231-sparkread를-사용하여-데이터-프레임으로-데이터-읽기">2.3.1 Spark.read를 사용하여 데이터 프레임으로 데이터 읽기</h3>
<ul>
<li>프로그램의 첫 단계인 구조로 데이터 수집하기</li>
<li>PySpark가 제공하는 조작을 수행할 때 데이터를 저장하기 위한 두 가지 주요 구조<ul>
<li><strong>RDD</strong><ul>
<li>“명령을 내리는 가방”</li>
<li>일반 Python 함수를 통해서 가방에 있는 항목에 대해 RDD에 주문을 전달.</li>
</ul>
</li>
<li><strong>데이터 프레임</strong><ul>
<li>RDD의 더 엄격한 버전</li>
<li>“각 셀에 하나의 값이 포함될 수 있는 테이블”</li>
<li>RDD와 같이 레코드 대신 열(colomun)개념을 많이 사용</li>
</ul>
</li>
</ul>
</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/f9c4075a-6b07-46bc-a55c-9895d762b7b9/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/rtd7878/post/8fdf2df0-cb2d-4170-a25f-096913ac8232/image.png" /></p>
<ul>
<li>Spark.read<ul>
<li>데이터 프레임으로 데이터를 읽는 작업</li>
<li>DataFrameReader 객체를 통해 수행</li>
</ul>
</li>
</ul>
<pre><code class="language-bash">&gt;&gt;&gt; spark.read 
&lt;pyspark.sql.readwriter.DataFrameReader object at 0x7fb0a2a5dc10&gt;
&gt;&gt;&gt; dir(spark.read) 
# ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_df', '_jreader', '_set_opts', '_spark', 'csv', 'format', 'jdbc', 'json', 'load', 'option', 'options', 'orc', 'parquet', 'schema', 'table', 'text']</code></pre>
<ul>
<li><strong><code>spark.read</code>:</strong> 데이터 프레임을 읽기 위한 객체. 다양한 형식의 데이터를 읽을 수 있음.</li>
<li><strong><code>dir(spark.read)</code>:</strong> 객체의 속성과 메서드 목록을 반환</li>
</ul>
<pre><code class="language-python">book = spark.read.text(&quot;./data/gutenberg_books/1342-0.txt&quot;)
book
# DataFrame[value: string]</code></pre>
<ul>
<li><strong><code>spark.read.text</code></strong> 메서드를 사용하여 특정 텍스트 파일을 읽고, 그 내용을 데이터 프레임인 <strong><code>book</code></strong>에 저장</li>
<li><strong><code>book</code></strong>을 출력하면 데이터 프레임이 생성된 것을 확인할 수 있다.</li>
<li>출력에는 데이터가 직접 표시되지 않고, 스키마의 구조 (데이터 타입) 출력
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/921f2a9c-0097-4910-9099-fbb92b5aa3d2/image.png" /></li>
</ul>
<ul>
<li>book의 스키마</li>
</ul>
<p><strong>데이터 프레임의 스키마 출력</strong></p>
<pre><code class="language-python">book.printSchema()
# root 
# |-- value: string (nullable = true) 

print(book.dtypes)
# [('value', 'string')]</code></pre>
<ul>
<li><strong><code>root</code>:</strong> 각 데이터 프레임의 트리는 root에서 시작하며 여기에 각 열이 연결된다.</li>
<li><strong><code>|-- value: string (nullable = true)</code>:</strong> value라는 열의 이름과, 해당 열의 타입과, null이 허용되는지 여부가 나타난다.</li>
<li><strong><code>'value'</code></strong>라는 열이 문자열(string) 형태임을 보여준다.</li>
</ul>
<h3 id="232-구조에서-내용으로-show를-사용하여-데이터-프레임-탐색">2.3.2 구조에서 내용으로: show()를 사용하여 데이터 프레임 탐색</h3>
<ul>
<li>데이터 프레임에 포함된 데이터를 보는 중요한 방법 ‘show()’</li>
</ul>
<pre><code class="language-python">book.show()
# +--------------------+
# | value| 
# +--------------------+
# |The Project Guten...|
# | |
# |This eBook is for...|
# |almost no restric...|
# |re-use it under t...|
# |with this eBook o...|
# | |
# | |
# |Title: Pride and ...|
# | |
# | [... more records] |
# |Character set enc...|
# | |
# +--------------------+
# only showing top 20 rows</code></pre>
<ul>
<li>Spark는 데이터 프레임의 데이터를 기본적으로 20자로 제한</li>
</ul>
<pre><code class="language-python">book.show(10, truncate=50)
# +--------------------------------------------------+
# | value|
# +--------------------------------------------------+
# |The Project Gutenberg EBook of Pride and Prejud...|
# | |
# |This eBook is for the use of anyone anywhere at...|
# |almost no restrictions whatsoever. You may cop...|
# |re-use it under the terms of the Project Gutenb...|
# | with this eBook or online at www.gutenberg.org|
# | |
# | |
# | Title: Pride and Prejudice|
# | |
# +--------------------------------------------------+
# only showing top 10 rows</code></pre>
<ul>
<li>상위 10개 행이 표시되며, 50자 제한</li>
</ul>
<h2 id="24-단순-열-변환-문장에서-단어-목록으로-이동">2.4 단순 열 변환: 문장에서 단어 목록으로 이동</h2>
<ul>
<li><strong>토큰화</strong>: 문자열을 각 단어로</li>
</ul>
<pre><code class="language-python">from pyspark.sql.functions import split
lines = book.select(split(book.value, &quot; &quot;).alias(&quot;line&quot;))
lines.show(5)
# +--------------------+
# | line|
# +--------------------+
# |[The, Project, Gu...|
# | []|
# |[This, eBook, is,...|
# |[almost, no, rest...|
# |[re-use, it, unde...|
# +--------------------+
# only showing top 5 rows</code></pre>
<ul>
<li>pyspark.sql.functions 에서 열 함수 가져오기</li>
<li><strong>select()</strong> : 데이터 선택</li>
<li><strong>split(book.value, “ “)</strong> : book의 데이터를 “ “(공백) 기준으로 분할</li>
<li><strong>alias()</strong> : spark dataframe의 컬럼에 새로운 이름을 붙여줄 수 있다.</li>
</ul>
<h3 id="241-select를-이용해-특정-컬럼-선택하기">2.4.1 select()를 이용해 특정 컬럼 선택하기</h3>
<pre><code class="language-python">from pyspark.sql.functions import col

book.select(book.value)
book.select(book[&quot;value&quot;]) #열 이름 지정(열 이름 문자열로 전달)
book.select(col(&quot;value&quot;)) #col 함수 사용
book.select(&quot;value&quot;) #열 이름을 문자열로 사용</code></pre>
<ul>
<li>열을 선택하는 가장 일반적인 네 가지</li>
</ul>
<h3 id="242-열-변환-문자열을-단어-목록으로-분할">2.4.2 열 변환: 문자열을 단어 목록으로 분할</h3>
<pre><code class="language-python">from pyspark.sql.functions import col, split

lines = book.select(split(col(&quot;value&quot;), &quot; &quot;))
lines
# DataFrame[split(value, , -1): array&lt;string&gt;] 

lines.printSchema()
# root
# |-- split(value, , -1): array (nullable = true)
# | |-- element: string (containsNull = true)

lines.show(5)
# +--------------------+
# | split(value, , -1)|
# +--------------------+
# |[The, Project, Gu...|
# | []|
# |[This, eBook, is,...|
# |[almost, no, rest...|
# |[re-use, it, unde...|
# +--------------------+
# only showing top 5 rows</code></pre>
<ul>
<li><strong><code>split</code></strong> 함수를 적용하여 새로운 데이터 프레임 <strong><code>lines</code></strong>을 생성.</li>
<li>value 열을 공백 기준으로 분할, 분할 시 모든 분할을 수행</li>
</ul>
<h3 id="243-열-이름-바꾸기--alias">2.4.3 열 이름 바꾸기 : alias</h3>
<pre><code class="language-python">book.select(split(col(&quot;value&quot;), &quot; &quot;)).printSchema()
# root
# |-- split(value, , -1): array (nullable = true) 
# | |-- element: string (containsNull = true)

book.select(split(col(&quot;value&quot;), &quot; &quot;).alias(&quot;line&quot;)).printSchema()
# root
# |-- line: array (nullable = true) 
# | |-- element: string (containsNull = true)</code></pre>
<ul>
<li>alias() : 작업을 수행한 후, 열 이름을 지정하는 명확하고 명시적인 방법을 제공.</li>
<li>프로그래머적으로 훨씬 깔끔함.</li>
</ul>
<h3 id="244-데이터-재구성-리스트를-행으로-분해">2.4.4 데이터 재구성: 리스트를 행으로 분해</h3>
<ul>
<li><strong>explode()</strong> : 리스트 형식을 풀어내고 그 결과를 새로운 열로 만들어줌
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/a2f0ef3f-ef00-46aa-a21f-9aef69891297/image.png" /></li>
</ul>
<pre><code class="language-python">from pyspark.sql.functions import explode, col
words = lines.select(explode(col(&quot;line&quot;)).alias(&quot;word&quot;))
words.show(15)
# +----------+
# | word|
# +----------+
# | The|
# | Project|
# | Gutenberg|
# | EBook|
# | of|
# | Pride|
# | and|
# |Prejudice,|
# | by|
# | Jane|
# | Austen|
# | |
# | This|
# | eBook|
# | is|
# +----------+
# only showing top 15 rows</code></pre>
<ul>
<li><strong>explode(</strong>) : 이전에 사용했던 split()과 똑같은 사용 방식</li>
</ul>
<h3 id="245-단어-작업-대소문자-변경-및-구두점-제거">2.4.5 단어 작업: 대소문자 변경 및 구두점 제거</h3>
<ul>
<li><strong>lower()</strong> : 문자형을 모두 소문자로 변환</li>
</ul>
<pre><code class="language-python">from pyspark.sql.functions import lower
words_lower = words.select(lower(col(&quot;word&quot;)).alias(&quot;word_lower&quot;))

words_lower.show()

# +-----------+
# | word_lower|
# +-----------+
# | the|
# | project|
# | gutenberg|
# | ebook|
# | of|
# | pride|
# | and|
# | prejudice,|
# | by|
# | jane|
# | austen|
# | |
# | this|
# | ebook|
# | is|
# | for|
# | the|
# | use|
# | of|
# | anyone|
# +-----------+
# only showing top 20 rows</code></pre>
<ul>
<li><strong>lower() :</strong> 이전에 사용했던 split()과 똑같은 사용 방식</li>
</ul>
<p><strong>구두점 제거</strong></p>
<ul>
<li><strong>regexp_extract()</strong> : 단어의 구두점 제거</li>
</ul>
<pre><code class="language-python">from pyspark.sql.functions import regexp_extract
words_clean = words_lower.select(
regexp_extract(col(&quot;word_lower&quot;), &quot;[a-z]+&quot;, 0).alias(&quot;word&quot;) 
)

words_clean.show()
# +---------+
# | word|
# +---------+
# | the|
# | project|
# |gutenberg|
# | ebook|
# | of|
# | pride|
# | and|
# |prejudice|
# | by|
# | jane|
# | austen|
# | |
# | this|
# | ebook|
# | is|
# | for|
# | the|
# | use|
# | of|
# | anyone|
# +---------+
# only showing top 20 rows</code></pre>
<ul>
<li><strong><code>[a-z]+</code></strong>는 소문자 알파벳의 연속된 문자열을 의미한다. 여기서 <strong><code>+</code></strong>는 하나 이상의 알파벳 문자가 매칭되어야 함을 나타낸다.</li>
<li>0: 인덱스</li>
</ul>
<h2 id="25-행-필터링">2.5 행 필터링</h2>
<pre><code class="language-python">words_nonull = words_clean.filter(col(&quot;word&quot;) != &quot;&quot;)
words_nonull.show()
# +---------+
# | word|
# +---------+
# | the|
# | project|
# |gutenberg|
# | ebook|
# | of|
# | pride|
# | and|
# |prejudice|
# | by|
# | jane|
# | austen|
# | this| 
# | ebook|
# | is|
# | for|
# | the|
# | use|
# | of|
# | anyone|
# | anywhere|
# +---------+
# only showing top 20 rows</code></pre>
<ul>
<li>‘! =’ 연산자를 이용한 행 필터링</li>
</ul>