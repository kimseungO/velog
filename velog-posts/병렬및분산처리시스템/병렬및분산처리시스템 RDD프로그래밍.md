## RDD프로그래밍

### Spark Application

- RDD생성, RDD변형, RDD 내용 추출
- Spark은 RDD에 대한 연산이 클러스터에서 병렬로 수행하도록 함

### RDD

- 분산되어 있는 변경 불가능한 객체 집합
- 클러스터의 노드들에서 연산이 가능하도록 여러 파티션으로 나뉨
- 외부 데이터 집합을 load하거나 드라이버 자체적으로 객체 컬렉션을 분산시켜서 생성

```bash
textFile = sc.textFile("README.md")
nums = sc.parallelize([1, 2, 3, 4]) #RDD로 변환
```

### RDD연산의 종류

- Transformation
    - 기존 RDD에서 새로운 RDD를 만들어 냄
    - filter, map 등
- Action
    - RDD를 기반으로 결과 값을 계산하여 드라이버 프로그램에 반환하거나 외부 스토리지(HDFS등)에 저장

```bash
lines = sc.textFile("testfile")
filteredLines = lines.filter(lambda line: "python" in line) #transformation
filteredLined.first() #action
filteredLined.count() #action
```

### RDD연산의 처리 방식

- Lazy evaluation
    - action을 만날때 transformation 실행
    ![](https://velog.velcdn.com/images/rtd7878/post/422bfdc8-5b42-4d36-9c6b-a862386dc78b/image.png)

    

### RDD는 매번 새로 생성됨

- RDD.persist()
- 결과를 지속적으로 메모리에 유지 가능
![](https://velog.velcdn.com/images/rtd7878/post/ffcf1f7c-0da1-47fe-ac0e-12048c8b6aff/image.png)
