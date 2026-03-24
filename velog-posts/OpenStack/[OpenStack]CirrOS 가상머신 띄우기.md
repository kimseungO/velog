![](https://velog.velcdn.com/images/rtd7878/post/997a24a1-0fd9-4394-b496-849b0f09d3ae/image.png)

>본 시리즈는 이제 막 배포된 오픈스택에 CirrOS 가상 머신을 띄우기 위한 과정중 발생한 트러블 슈팅을 담고 있습니다.

### 가상머신을 띄우는 과정
- Provider Network 만들기 - CirrOS 이미지 올리기 - 가상머신 띄우기

#### 1. CirrOS 이미지 다운로드 및 업로드

```bash
# CirrOS 이미지 다운로드
wget http://download.cirros-cloud.net/0.6.3/cirros-0.6.3-x86_64-disk.img

# OpenStack 환경에 이미지 등록
openstack image create "cirros" \
  --file cirros-0.6.3-x86_64-disk.img \
  --disk-format qcow2 \
  --container-format bare \
  --public
```

#### 2. Provider Network 생성 및 Subnet 생성
- 현재 인프라 대역(192.168.6.0/24)을 그대로 사용하되, 기존 노드 IP나 VIP와 충돌하지 않도록 VM용 IP 할당 범위(Pool)를 100~150으로 지정
```bash
# Provider Network 생성 (Flat 타입, physnet1 매핑)
openstack network create  --share --external \
  --provider-physical-network physnet1 \
  --provider-network-type flat provider-net

# Subnet 생성 (IP 충돌 방지를 위해 allocation-pool 설정) 
openstack subnet create --network provider-net \
  --allocation-pool start=192.168.6.100,end=192.168.6.150 \
  --dns-nameserver 8.8.8.8 \
  --gateway 192.168.6.1 \
  --subnet-range 192.168.6.0/24 provider-subnet
```

#### 3. 인스턴스 Flavor 생성
- CirrOS를 실행하기 위한 최소 사양의 Flavor(가상 하드웨어 템플릿)를 만듭니다.
```bash
openstack flavor create --id auto --ram 256 --disk 1 --vcpus 1 m1.nano
```

#### 4. SSH 키페어(Keypair) 생성
인스턴스에 접속하기 위해 SSH 키페어를 생성하고 Nova에 등록합니다. (이미 컨트롤러에 키가 있다면 생성 부분은 건너뛰셔도 됩니다.)
```bash
# SSH 키 생성 (기본 경로)
ssh-keygen -q -N "" -t rsa -f ~/.ssh/id_rsa

# OpenStack에 키페어 등록
openstack keypair create --public-key ~/.ssh/id_rsa.pub mykey
```

#### 5. 보안 그룹(Security Group) 규칙 추가
기본 상태에서는 모든 인바운드 트래픽이 차단되어 있습니다. Ping(ICMP) 테스트와 SSH 접속을 위해 default 보안 그룹에 규칙을 추가합니다.
```bash
# Ping (ICMP) 허용
openstack security group rule create --proto icmp default

# SSH (TCP 22) 허용
openstack security group rule create --proto tcp --dst-port 22 default
```

#### 6. 첫 번째 인스턴스(VM) 생성 및 확인
```bash
# 인스턴스 생성
openstack server create \
  --flavor m1.nano \
  --image cirros \
  --nic net-id=provider-net \
  --security-group default \
  --key-name mykey \
  test-vm
```
배포가 완료될 때까지 잠시 기다린 후, 상태와 할당된 IP를 확인합니다.

```bash
# 인스턴스 상태 및 IP 확인 (상태가 'ACTIVE'가 되어야 함)
openstack server list
```

#### 7. 통신 테스트
할당된 IP(예: 192.168.6.100)를 확인하셨다면, 컨트롤러 노드에서 직접 Ping과 SSH 접속을 테스트해 봅니다.
```bash
# Ping 테스트
ping -c 4 192.168.6.100

# SSH 접속 테스트 (CirrOS의 기본 유저는 'cirros' 입니다)
ssh cirros@192.168.6.100
```

### Keystone 인증 정보(환경 변수)가 로드되지 않아서 OpenStack CLI 안먹는 에러
```bash
(kolla-venv) sok@controller:~$ openstack image create "cirros"\
> --file cirros-0.6.3-x86_64-disk.img \
> --disk-format qcow2 \
> --container-format bare \
> --public
Missing value auth-url required for auth plugin password
```
아래의 관리자 인증 정보(환경 변수)를 로드하여 현재 쉥에 환경 변수를 적용한다.
```bash
source /etc/kolla/admin-openrc.sh
```