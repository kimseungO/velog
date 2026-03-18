## YARN의 등장 배경

### Cluster의 확장성

- HADOOP1
    - 클러스터의 규모와는 상관없이 Job Tracker의 개수는 1개
    - 예를 들어 4000개의 노드로 구성된 클러스터에 단 1개의 JobTracker가 모든 노드의 job을 관리
- HADOOP2 YARN
    - Job Tracker의 기능을 resource Manager와 Application Master로 분리
    - 클러스터에는 여러 개의 Application이 동시 동작 가능
    - 각 Application은 Application Master가 모든 task를 관리
    ![](https://velog.velcdn.com/images/rtd7878/post/cb6c7a66-1446-47ed-aa22-6503982fce96/image.png)

    ![](https://velog.velcdn.com/images/rtd7878/post/158b6c12-79e9-45b4-a25f-3eb2667fcd93/image.png)

    
    ### Application 호환성
    
    - HADOOP1
        - MapReduce외에 다른 Application은 클러스터의 자원을 공유할 수 없는 문제
    - HADOOP2 YARN
        - 같은 클러스터내에서 MapReduce 와 다른 application을 실행할 수 있도록 지원
        
    
    ### 자원 할당의 유연성
    
    - HADOOP1
        - Slot에 미리 자원 (memory, cpu cores)를 할당 후 미리 정해진 설정에 따라서 slot을 job에 할당
        - job이 모두 끝나기 전까지는 자원이 반납되지 않는 문제
    - HADOOP2 YARN
        - 요청이 있을 때마다 요구하는 자원에 맞게 **container**의 개념으로 할당
            - container마다 다른 사양의 자원을 가질 수 있음
            - 모든 task는 container에서 수행되고 task가 끝나는 즉시 자원을 반납
            
    
    ## YARN 시스템 아키텍처
    
    ### 맵리듀스 애플리케이션 외 다양한 애플리케이션 수용 가능
    
    ### 잡트래커 분리 → 리소스 매니저, 애플리케이션 마스터
    
    - 리소스 매니저
        - YARN의 마스터 역할
        - 클라이언트가 실행한 애플리케이션이 필요한 전체 클러스터의 리소스 관리
        - 내부적으로 스케줄러, 애플리케이션 매니저를 실행
            - 스케줄러: 리소스 스케줄링 수행(FIFO, 커패시티)
            - 애플리케이션 매니저: 애플리케이션 마스터의 실행, 모니터링, 재실행 기능
    - 애플리케이션 마스터
        - job의 스케줄링과 모니터링을 담당
        
![](https://velog.velcdn.com/images/rtd7878/post/43074257-b364-4e76-b068-2eaec58d77a6/image.png)


### 리소스 매니저

- 어플리케이션 매니저
- 스케줄러

### 어플리케이션 마스터

- 하나의 애플리케이션을 관리하는 마스터 역할
- 태스크 실행, 진행상태, 장애 처리

### 노드 매니저

- 애플리케이션 컨테이너를 실행
- 서버의 리소스가 어떻게 사용되는지 모니터링
- 리소스 매니저와 지속적으로 통신

### 컨테이너

## YARN 구성

### Resource Manager(RM)

- master node에서 동장
- global resource scheduler
- application들의 자원 요구 할당 및 관리

### Node Manager(NM)

- slave node에서 동작
- node의 자원 관리
- container에 node의 자원 할당

### Containers

- RM의 요청에 의해 NM에서 할당
- slave node의 CPU core, mamory의 자원을 할당
- Application은 다수의 container에서 동작

### Application Master(AM)

- application당 한 개씩 존재
- application의 spec을 정의
- container에서 동작
- application task를 위해 container 할당을 RM에게 요청

## YARN의 장점

### 확장성

- 실행가능 서버의 개수
    - 4000대 → 6000대 이상

### 가용성

- 보조 리소스 매니저를 사용
    - 리소스 매니저에 장애가 발생하면 보조 리소스 사용

### 호환성

- Hadoop 1.x와 호환가능

### 리소스 이용확대

- Hadoop 1.x의 맵, 리두스 슬롯 할당방법이 개선

### 알고리즘 지원 확대

- 다양한 프로그래밍 모델 사용 가능

[하둡1.0과 하둡2.0 태스크 처리 비교](https://www.notion.so/1-0-2-0-1f7b3e1d810c448390c3267bc3e8b03a?pvs=21)

클라이언트 → 리소스매니저한테 요청 → 리소스매니저 안에 있는 앱매니저가 노드 매니저에 의해 관리되고 있던 앱 마스터를 실행시킴 → 앱 마스터는 리소스매니저한테 자기가 실행해야하는 태스크를 위한 리소스를 요청 → 리소스매니저내의 리소스 스케줄러가, 요청된 리소스만큼 노드매니저한테 컨테이너 할당 → 앱마스터가 노드매니저에 태스크 보내면 →그 태스크가 컨테이너에 들어가 실행됨→컨테이너가 태스크 상태정보를 앱 마스터에 전달 →앱 마스터는 리소스 매니저한테 상태정보 전달 →클라이언트한테 전달
![](https://velog.velcdn.com/images/rtd7878/post/a34a6f82-d1c5-4252-b863-061071703f69/image.png)
