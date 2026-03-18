https://www.acmicpc.net/problem/1260
![](https://velog.velcdn.com/images/rtd7878/post/640a4106-c6c5-4f72-a1c7-7f22330ac776/image.png)![](https://velog.velcdn.com/images/rtd7878/post/db850369-6bb8-48d6-a4c8-71a4922981b4/image.png)

### 문제
이 문제는 심플하게 DFS와 BFS를 구현해 내는 것.
DFS는 재귀적으로 어렵지 않게 구현해 냈지만 BFS를 구현할 때 조금 애를 먹었다.
그래프문제가 아직은 익숙하지 않은것 같다.
생각해야 할 조건들이 많았는데, 방문표시를 어떻게 할지 고민을 좀 했다.

### 내 답
```python
import sys
from collections import deque
input = sys.stdin.readline

def dfs(num):
    for i in arr[num]: # 그래프의 시작점부터 탐색
        if i not in res: # 만약 탐색점이 결과리스트에 없다면
            res.append(i) # 결과 리스트에 탐색점 추가
            dfs(i) # 탐색점으로 깊이 탐색
            
def bfs(num):
    q = deque()
    q.append(num) # 큐에 탐색점 추가하기
    while q: # 큐가 비어있으면 종료
        num = q.popleft() # 큐에서 값을 하나 꺼내서
        for i in arr[num]: # 탐색
            if i not in res and i != -1: # 만약 탐색점이 결과리스트에 없고 이미 방문하지 않았다면(-1이 아니라면)
                res.append(i) # 결과리스트에 탐색점 추가
                arr[num][arr[num].index(i)] = -1 # 탐색점 방문 표시(-1)
                q.append(i) # 큐에 현재 리스트 탐색이 끝난 후 방문할 탐색점 추가

n, m, v = map(int,input().split())
arr =[[] for _ in range(n+1)]
for _ in range(m):
    a, b = map(int,input().split()) 
    arr[a].append(b)
    arr[b].append(a)
for i in arr: # 조건 "문할 수 있는 정점이 여러 개인 경우에는 정점 번호가 작은 것을 먼저 방문"
    i.sort()       

res = [v] #결과 리스트
dfs(v)
print(*res)
res = [v]
bfs(v)
print(*res)
```