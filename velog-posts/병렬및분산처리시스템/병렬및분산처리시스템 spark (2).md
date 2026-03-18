## Spark Architecture

- master/worker 구조
- Driver, executors : run java processes
![](https://velog.velcdn.com/images/rtd7878/post/178decb5-d10f-4f6d-a84d-576aaebe81d4/image.png)

![](https://velog.velcdn.com/images/rtd7878/post/5627b6c5-21b4-44a3-8aa0-a4949147f67c/image.png)


## 스파크 핵심 개념

### Spark Application 구조

- application은 하나의 드라이버를 가지며 드라이버는 다수의 익스큐터(excutor)들을 통해 병렬 처리 수행
- 드라이버
    - main함수, 클러스터 분산 데이터집합(RDD) 정의, RDD연산
    - 클러스터에 대한 연결을 SparkContext객체를 통해서 수행
    - SparkContext를 통해 RDD 생성 및 연산 가능
- Excutor
    - 클러스터의 work node에서 동작하는 자바프로세스
    - 실제로 RDD에 대한 분산 병렬처리 수행
    ![](https://velog.velcdn.com/images/rtd7878/post/6cf27146-0f1a-4d50-b3b5-2967325024d8/image.png)

    
- 스파크 API 동작 방식
    - RDD에 대한 연산을 수행하기 위한 함수를 작성해서 API에 전달

## lambda(람다)

### Lambda

- 함수 body는 가지지만 이름이 없는 함수
- 암시적으로 함수 객체 클래스를 정의하고, 함수 객체를 생성

![](https://velog.velcdn.com/images/rtd7878/post/47bf21a8-93f3-47e6-a7ca-fe69a29bef81/image.png)
