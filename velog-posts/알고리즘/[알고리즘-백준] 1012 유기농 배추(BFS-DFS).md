https://www.acmicpc.net/problem/1012
![](https://velog.velcdn.com/images/rtd7878/post/3e6d50fa-6740-4165-9239-90c38aa03cd5/image.png)![](https://velog.velcdn.com/images/rtd7878/post/84d9936b-c475-413f-9e15-3288748b961c/image.png)

전형적인 그래프 문제.

풀지 못해서 다른 사람 코드를 참고했다.

이 문제 의도는 BFS 구현이라서 DFS를 제출하면 런타임 에러(최대 재귀 횟수 초과)가 뜬다.

### 풀이
**DFS**: 재귀함수를 이용해서 상하좌우를 재귀적으로 탐색
```python
t = int(input())

def dfs(x, y): 
    nx = [0, 0, -1, 1]  #상하좌우를 탐색할 리스트
    ny = [1, -1, 0, 0]

    for i in range(4): #현재 위치에서 상하좌우 탐색
        ax = x+nx[i] 
        ay = y+ny[i]
        if 0 <= ax < m and 0 <= ay < n:  #그래프 범위를 넘어가지 않을 때
            if graph[ay][ax] == 1: #배추가 심어져 있을 때
                graph[ay][ax] = -1 #-1로 방문 표시
                dfs(ax, ay) # -1로 표시 후 그 곳에서 다시 탐색

for _ in range(t): # t만큼 반복
    m, n, k = map(int, input().split())
    graph = [[0 for x in range(m)] for x in range(n)]

    for _ in range(k): # 그래프 만들기
        x, y = map(int, input().split())
        graph[y][x] = 1 

    cnt = 0
    for a in range(m): # 그래프를 처음부터 하나하나 탐색
        for b in range(n): # 
            if graph[b][a] == 1: # 1이라면(배추가 심어져 있다면)
                dfs(a, b) #dfs 탐색
                cnt += 1 # 탐색이 한 번 끝나면 cnt +1
    print(cnt)
```
**BFS**: 함수 내에서 for 반복문을 활용해 상하좌우를 탐색
```python
from collections import deque
t = int(input())

def bfs(x, y):
    q = deque() # 탐색해야할 좌표 리스트(데크) 생성
    q.append([x, y]) # 탐색해야할 좌표 추가
    graph[y][x] == 0 # 배추가 심어져있는 좌표를 0으로 방문 표시

    dx = [0, 0, -1, 1] # 상하좌우를 탐색할 리스트
    dy = [1, -1, 0, 0]

    while q: # q가 비어있다면 더이상 탐색할 좌표가 없음.
        x, y = q.popleft() # q에서 좌표를 꺼내서
        for i in range(4): # 그 좌표의 상하좌우를 탐색
            ax = x + dx[i]
            ay = y + dy[i]
            if 0<= ax <m and 0<= ay <n: # 그래프 범위를 넘어가지 않을 때
                if graph[ay][ax] == 1: # 배추가 심어져 있다면
                    q.append([ax, ay]) # q에 탐색할 좌표 추가
                    graph[ay][ax] = 0 # 그리고 그 좌표를 0으로 방문 표시

for _ in range(t): # t만큼 반복
    m, n, k = map(int, input().split())
    graph = [[0 for x in range(m)] for x in range(n)]

    for _ in range(k): # 그래프 만들기
        x, y = map(int, input().split())
        graph[y][x] = 1

    cnt = 0
    for a in range(m): #그래프를 처음부터 하나하나 탐색
        for b in range(n):
            if graph[b][a] == 1: # 1이라면(배추가 심어져 있다면)
                bfs(a, b) #bfs탐색
                cnt += 1 # 탐색이 한 번 끝내면 cnt +1
    print(cnt)

```
