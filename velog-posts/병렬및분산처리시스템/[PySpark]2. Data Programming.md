## 2.1 Setting up the PySpark shell

### 2.1.1 The SparkSession entry point

```python
from pyspark.sql import SparkSession 
spark = (SparkSession  
  .builder 
  .appName("Pride and Prejudice Vocabulary Analysis.") 
  .getOrCreate())
```

- PySpark 애플리케이션을 시작하고 Spark 클러스터에 연결하는 데 사용됨.
- **`spark`** 변수는 이후 PySpark 기능에 접근할 때 사용될 SparkSession 객체를 나타냄
- 코드 설명
    
    ```python
    from pyspark.sql import SparkSession 
    ```
    
    - **`pyspark.sql`**에서 **`SparkSession`** 클래스를 임포트.
    이는 PySpark에서 데이터 프레임 및 관련 기능을 사용하기 위한 핵심 클래스
    
    ```python
    from pyspark.sql import SparkSession 
    spark = (SparkSession  
      .builder 
      .appName("Pride and Prejudice Vocabulary Analysis.") 
      .getOrCreate())
    ```
    
    - **`SparkSession.builder`**를 사용하여 SparkSession 객체를 생성. 
    빌더 패턴을 사용하여 다양한 구성 옵션을 설정할 수 있다.
    - **`appName("Pride and Prejudice Vocabulary Analysis.")`**은 Spark 애플리케이션의 이름을 지정하는 메서드.
    - **`getOrCreate()`** 메서드는 이미 존재하는 SparkSession을 반환하거나 존재하지 않는 경우 새로운 SparkSession을 생성.

```bash
$ spark.sparkContext  
# <SparkContext master=local[*] appName=...>
```

- **`spark`** 변수는 앞서 생성한 SparkSession 객체를 나타냄.
- SparkContext의 정보 표시

### 2.1.2 Configuring how chatty spark is: The log level

```python
Spark.sparkContext.setLogLevel("ALL")
```

- 로그 레벨 조정
    - 로그의 출력 양을 제어하고 원하는 수준의 로그 표시
        - **`"ALL"`**: 가장 상세한 로그 레벨로 모든 로그를 출력합니다.
        - **`"DEBUG"`**: 디버그 정보를 포함한 모든 로그를 출력합니다.
        - **`"INFO"`**: 정보 수준 이상의 로그를 출력합니다.
        - **`"WARN"`**: 경고 수준 이상의 로그를 출력합니다.
        - **`"ERROR"`**: 오류 수준 이상의 로그를 출력합니다.
        - **`"FATAL"`**: 치명적인 오류 수준의 로그를 출력합니다.
        - **`"OFF"`**: 모든 로그를 출력하지 않습니다.

## 2.2 Mapping our program

- 데이터 분석을 미리 설계
    - 구조와 작동 방식을 먼저 생각하고 설계함으로 발생 문제 예상 가능
    - 코드 작성 속도 향상
    - 신뢰성과 향상

- 매핑 단계
    1. **Read** - 입력 데이터를 읽습니다(일반 텍스트로 가정).
    2. **Token** - 각 단어를 토큰화합니다.
    3. **Clean** - 모든 구두점 및 단어가 아닌 토큰을 제거합니다. 각 단어를 소문자로 변환합니다.
    4. **Count** - 텍스트에 포함된 각 단어의 빈도를 계산합니다.
    5. **Answer** - 상위 10개(또는 20개, 50개, 100개)를 반환합니다.

- “영어에서 가장 많이 쓰이는 단어는 무엇인가?” 문제
![](https://velog.velcdn.com/images/rtd7878/post/a9e80c2a-5f58-41f4-823b-49594781da45/image.png)


## 2.3 Ingest and explore: 데이터 변환을 위한 스테이지

- 데이터 변환을 위한 PySpark 프로그램에서 접하게 되는 세 가지 작업
    1. 데이터를 구조로 수집
    2. 구조(또는 스키마)를 출력하여 데이터의 구성 확인
    3. 데이터 샘플을 표시

### 2.3.1 Spark.read를 사용하여 데이터 프레임으로 데이터 읽기

- 프로그램의 첫 단계인 구조로 데이터 수집하기
- PySpark가 제공하는 조작을 수행할 때 데이터를 저장하기 위한 두 가지 주요 구조
    - **RDD**
        - “명령을 내리는 가방”
        - 일반 Python 함수를 통해서 가방에 있는 항목에 대해 RDD에 주문을 전달.
    - **데이터 프레임**
        - RDD의 더 엄격한 버전
        - “각 셀에 하나의 값이 포함될 수 있는 테이블”
        - RDD와 같이 레코드 대신 열(colomun)개념을 많이 사용
        
![](https://velog.velcdn.com/images/rtd7878/post/f9c4075a-6b07-46bc-a55c-9895d762b7b9/image.png)

![](https://velog.velcdn.com/images/rtd7878/post/8fdf2df0-cb2d-4170-a25f-096913ac8232/image.png)


- Spark.read
    - 데이터 프레임으로 데이터를 읽는 작업
    - DataFrameReader 객체를 통해 수행

```bash
>>> spark.read 
<pyspark.sql.readwriter.DataFrameReader object at 0x7fb0a2a5dc10>
>>> dir(spark.read) 
# ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_df', '_jreader', '_set_opts', '_spark', 'csv', 'format', 'jdbc', 'json', 'load', 'option', 'options', 'orc', 'parquet', 'schema', 'table', 'text']
```

- **`spark.read`:** 데이터 프레임을 읽기 위한 객체. 다양한 형식의 데이터를 읽을 수 있음.
- **`dir(spark.read)`:** 객체의 속성과 메서드 목록을 반환

```python
book = spark.read.text("./data/gutenberg_books/1342-0.txt")
book
# DataFrame[value: string]
```

- **`spark.read.text`** 메서드를 사용하여 특정 텍스트 파일을 읽고, 그 내용을 데이터 프레임인 **`book`**에 저장
- **`book`**을 출력하면 데이터 프레임이 생성된 것을 확인할 수 있다.
- 출력에는 데이터가 직접 표시되지 않고, 스키마의 구조 (데이터 타입) 출력
![](https://velog.velcdn.com/images/rtd7878/post/921f2a9c-0097-4910-9099-fbb92b5aa3d2/image.png)


- book의 스키마

**데이터 프레임의 스키마 출력**

```python
book.printSchema()
# root 
# |-- value: string (nullable = true) 

print(book.dtypes)
# [('value', 'string')]
```

- **`root`:** 각 데이터 프레임의 트리는 root에서 시작하며 여기에 각 열이 연결된다.
- **`|-- value: string (nullable = true)`:** value라는 열의 이름과, 해당 열의 타입과, null이 허용되는지 여부가 나타난다.
- **`'value'`**라는 열이 문자열(string) 형태임을 보여준다.

### 2.3.2 구조에서 내용으로: show()를 사용하여 데이터 프레임 탐색

- 데이터 프레임에 포함된 데이터를 보는 중요한 방법 ‘show()’

```python
book.show()
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
# only showing top 20 rows
```

- Spark는 데이터 프레임의 데이터를 기본적으로 20자로 제한

```python
book.show(10, truncate=50)
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
# only showing top 10 rows
```

- 상위 10개 행이 표시되며, 50자 제한

## 2.4 단순 열 변환: 문장에서 단어 목록으로 이동

- **토큰화**: 문자열을 각 단어로

```python
from pyspark.sql.functions import split
lines = book.select(split(book.value, " ").alias("line"))
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
# only showing top 5 rows
```

- pyspark.sql.functions 에서 열 함수 가져오기
- **select()** : 데이터 선택
- **split(book.value, “ “)** : book의 데이터를 “ “(공백) 기준으로 분할
- **alias()** : spark dataframe의 컬럼에 새로운 이름을 붙여줄 수 있다.

### 2.4.1 select()를 이용해 특정 컬럼 선택하기

```python
from pyspark.sql.functions import col

book.select(book.value)
book.select(book["value"]) #열 이름 지정(열 이름 문자열로 전달)
book.select(col("value")) #col 함수 사용
book.select("value") #열 이름을 문자열로 사용
```

- 열을 선택하는 가장 일반적인 네 가지

### 2.4.2 열 변환: 문자열을 단어 목록으로 분할

```python
from pyspark.sql.functions import col, split

lines = book.select(split(col("value"), " "))
lines
# DataFrame[split(value, , -1): array<string>] 

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
# only showing top 5 rows
```

- **`split`** 함수를 적용하여 새로운 데이터 프레임 **`lines`**을 생성.
- value 열을 공백 기준으로 분할, 분할 시 모든 분할을 수행

### 2.4.3 열 이름 바꾸기 : alias

```python
book.select(split(col("value"), " ")).printSchema()
# root
# |-- split(value, , -1): array (nullable = true) 
# | |-- element: string (containsNull = true)

book.select(split(col("value"), " ").alias("line")).printSchema()
# root
# |-- line: array (nullable = true) 
# | |-- element: string (containsNull = true)
```

- alias() : 작업을 수행한 후, 열 이름을 지정하는 명확하고 명시적인 방법을 제공.
- 프로그래머적으로 훨씬 깔끔함.

### 2.4.4 데이터 재구성: 리스트를 행으로 분해

- **explode()** : 리스트 형식을 풀어내고 그 결과를 새로운 열로 만들어줌
![](https://velog.velcdn.com/images/rtd7878/post/a2f0ef3f-ef00-46aa-a21f-9aef69891297/image.png)


```python
from pyspark.sql.functions import explode, col
words = lines.select(explode(col("line")).alias("word"))
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
# only showing top 15 rows
```

- **explode(**) : 이전에 사용했던 split()과 똑같은 사용 방식

### 2.4.5 단어 작업: 대소문자 변경 및 구두점 제거

- **lower()** : 문자형을 모두 소문자로 변환

```python
from pyspark.sql.functions import lower
words_lower = words.select(lower(col("word")).alias("word_lower"))

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
# only showing top 20 rows
```

- **lower() :** 이전에 사용했던 split()과 똑같은 사용 방식

**구두점 제거**

- **regexp_extract()** : 단어의 구두점 제거

```python
from pyspark.sql.functions import regexp_extract
words_clean = words_lower.select(
regexp_extract(col("word_lower"), "[a-z]+", 0).alias("word") 
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
# only showing top 20 rows
```

- **`[a-z]+`**는 소문자 알파벳의 연속된 문자열을 의미한다. 여기서 **`+`**는 하나 이상의 알파벳 문자가 매칭되어야 함을 나타낸다.
- 0: 인덱스

## 2.5 행 필터링

```python
words_nonull = words_clean.filter(col("word") != "")
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
# only showing top 20 rows
```

- ‘! =’ 연산자를 이용한 행 필터링