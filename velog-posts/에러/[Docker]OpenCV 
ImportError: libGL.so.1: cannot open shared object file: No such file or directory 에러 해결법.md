### 참고
https://yuevelyne.tistory.com/entry/OpenCV-ImportError-libGLso1-cannot-open-shared-object-file-No-such-file-or-directory

### 에러 발생
airflow실행 후 docker 환경에서 아래와 같은 에러 발생
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```
사전에 아래 명령어로 opencv-python 설치된 상태
```
pip3 install opencv-python
```

에러 발생 시정
```
import cv2
```

### 해결법
```
apt-get update -y
apt-get install -y libgl1-mesa-glx
```
위 명령어로 libgl1-mesa-glx 설치
설치 후에 아래 에러가 발생한다면,
```
ImportError: libgthread-2.0.so.0: cannot open shared object file: No such file or directory
```
추가로 libglib2.0-0설치
```
apt-get install -y libglib2.0-0