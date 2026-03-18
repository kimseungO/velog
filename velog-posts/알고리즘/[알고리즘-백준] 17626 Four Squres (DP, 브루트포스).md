https://www.acmicpc.net/problem/17626
![](https://velog.velcdn.com/images/rtd7878/post/4b56a22e-ee6d-4563-8ea8-5bcc6c63755b/image.png)

DP와 브루트포스를 이용한 문제.


### 풀이
먼저 dp변수 초기화.

n_root라는 변수에 n값의 제곱근 정수값을 넣어주었고,
1 ~ n_root값 까지의 수를 모두 제곱한 리스트를 만들었다. (sqrlst)

그후 체크리스트(chcklst)도 만들어 주었고
for문을 이용해 sqrlst 값들중 n에서 뺀 값중 가장 작은 수를 dp에 넣어주었다.

### 정답
```python
n = int(input())

dp =[0] * (n+4)
dp[1] =1
dp[2] =2
dp[3] =3

if n>3:
    for i in range(4, n+1):
        n_root = int(i**(1/2))
        sqrlst=[x**2 for x in range(1, n_root+1)]
        chcklst=[]

        for j in sqrlst:
            a=i-j
            chcklst.append(dp[a]+1)
        dp[i]=min(chcklst)
print(dp[n])
```


푸는데 세시간 정도 걸렸다.
dp는 아직 어려운거 같다.