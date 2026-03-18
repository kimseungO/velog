PAM은 리눅스 시스템에서 사용되는 인증 모듈로써 응용 프로그램(서비스)에 대한 사용자의 사용 권한을 제어하는 모듈이다.

▣ PAM 동작 원리
1. 인증이 필요한 응용프로그램은 더 이상 passwd 파일을 열람하지 않고, PAM 모듈에 사용자 인증을 요청한다.
2. PAM은 인증을 요청한 사용자의 정보를 가지고 결과를 도출하여 응용프로그램에 전달한다.

![](https://velog.velcdn.com/images/rtd7878/post/5f36be20-d46d-4de5-ad93-67087c51b0e5/image.png)

▣ PAM 기본 구조
![](https://velog.velcdn.com/images/rtd7878/post/426bcbef-66cb-45c9-a5a0-196b4f967323/image.png)
