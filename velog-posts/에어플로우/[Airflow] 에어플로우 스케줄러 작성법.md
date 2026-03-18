Airflow에서 스케줄러를 작성하려면, DAG(Directed Acyclic Graph)와 스케줄링에 필요한 파라미터를 정의해야 합니다. DAG은 작업(task)들의 순서와 실행 방법을 정의한 그래프입니다. Airflow의 스케줄러는 정의된 DAG을 주기적으로 실행하는 역할을 합니다. 아래는 Airflow 스케줄러를 작성하는 기본적인 과정입니다.

### 1. DAG 파일 생성
Airflow에서 스케줄러를 설정하려면, Python 파일을 생성하고 그 안에서 DAG을 정의해야 합니다.

```bash
# Airflow DAGs 폴더로 이동
cd $AIRFLOW_HOME/dags

# 새로운 DAG 파일 생성
touch my_dag.py
```

### 2. DAG 작성
DAG 파일에 스케줄러가 실행할 작업과 주기를 정의합니다. 예시 코드:

```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 24),  # DAG이 언제부터 실행되는지
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 객체 생성
dag = DAG(
    'my_first_dag',
    default_args=default_args,
    description='A simple DAG',
    schedule_interval=timedelta(days=1),  # 하루에 한 번씩 실행
)

# 작업 정의
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

t2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    dag=dag,
)

t3 = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello World"',
    dag=dag,
)

# 작업 순서 정의 (의존성 설정)
t1 >> t2 >> t3
```

### 3. 주요 요소 설명

- **default_args**: DAG 및 각 작업(task)의 기본 설정을 정의합니다. 예를 들어, 작업 실패 시 재시도 횟수나 시작 날짜 등을 설정합니다.
- **schedule_interval**: DAG이 얼마나 자주 실행되는지 설정합니다. `timedelta(days=1)`은 하루에 한 번 실행을 의미합니다.
  - `@daily`, `@hourly`, `@weekly`와 같은 문자열도 사용 가능합니다.
- **task_id**: 각 작업의 고유한 ID를 정의합니다.
- **bash_command**: BashOperator에서 실행할 명령어를 정의합니다.
- **의존성 설정**: `t1 >> t2 >> t3`은 `t1`이 먼저 실행되고, 그 후에 `t2`, `t3`가 차례대로 실행된다는 의미입니다.

### 4. 스케줄 설정 방법

**schedule_interval**의 다양한 예시는 다음과 같습니다:

- `timedelta(days=1)`: 하루에 한 번 실행
- `@daily`: 매일 자정에 실행
- `@hourly`: 매 시간마다 실행
- `@weekly`: 매주 일요일 자정에 실행
- `@monthly`: 매달 1일 자정에 실행
- `cron 표현식`: 더 복잡한 일정이 필요한 경우 사용
  - `0 12 * * *`: 매일 12시에 실행
  - `0 0 1 * *`: 매월 1일 00시에 실행

### 5. Airflow 스케줄러 실행
DAG 파일이 작성되면 Airflow 스케줄러가 DAG을 주기적으로 실행할 수 있도록 설정해야 합니다.

1. Airflow 웹 UI에서 DAG을 활성화합니다.
2. `airflow scheduler` 명령을 실행하여 스케줄러를 시작합니다.

```bash
airflow scheduler
```

이렇게 설정하면, Airflow 스케줄러가 설정한 주기에 따라 DAG을 실행하게 됩니다.

---

이제 이 DAG은 매일 한 번씩 작업을 수행하게 됩니다.


