>오픈스택 설치중 마주쳤던 에러에 관해서 정리하는 시리즈입니다.




### **[1. 인프라 아키텍처 및 IP 구성]**
- 하이퍼바이저: VMware
- 노드 구성 (3대):
  * Controller: 192.168.6.10 memory: 12GB processor: 4core HDD: 60GB
  * Compute01: 192.168.6.11 memory: 6GB processor: 2core HDD: 60GB
  * Compute02: 192.168.6.12 memory: 6GB processor: 2core HDD: 60GB(cinder 실습을 위한 추가 스토리지 20Gb /dev/sdb)
- 네트워크 인터페이스 (2-NIC 구조로 분리):
  * Management & Internal API (network_interface): ens33
  * Provider & External (neutron_external_interface): ens37
  
### **[2. 소프트웨어 버전 정보]**
- OS: Ubuntu 22.04 LTS
- 배포 도구: Kolla-Ansible 19.7.0 (Python venv 환경: kolla-venv)
- Ansible 환경: Ansible 9.13.0, ansible-core 2.16.17
- OpenStack CLI: python-openstackclient (cliff>=4.7.0)

### **[3. globals.yml 파일 수정사항]**
```yml
# 1. OS 배포판 및 설치 타입
kolla_base_distro: "ubuntu"
kolla_install_type: "source" # (명시적으로 추가함: 안정적인 소스 빌드 이미지 사용)

# 2. 네트워크 인터페이스 (2-NIC 구조로 분리)
network_interface: "ens33"            # 관리 및 내부 API 통신용 (IP: 192.168.6.10)
neutron_external_interface: "ens37"   # OVS 브릿지(br-ex)용 깡통 랜카드 (외부 인터넷 통신용)

# 3. VIP (Virtual IP) 및 FQDN 설정
kolla_internal_vip_address: "192.168.6.200"
kolla_internal_fqdn: "192.168.6.200"  # (추가: Ansible 변수 누락 버그 방지)
kolla_external_vip_address: "192.168.6.200" # (추가: HAProxy가 0.0.0.0을 잡아먹어 RabbitMQ 포트와 충돌하는 현상 방지)

# 4. 데이터베이스 백엔드 우회 (최신 아키텍처 대응)
database_address: "192.168.6.10"      # (추가: HAProxy가 더 이상 DB 포워딩을 하지 않는 최신 버전 스펙에 맞춰 컨트롤러 물리 IP로 직접 연결)

# 5. Cinder 스토리지 서비스 활성화
enable_cinder: "yes"
enable_cinder_backend_lvm: "yes"      # (Compute02의 /dev/sdb를 사용하는 LVM 백엔드 활성화)
```

#### 버전 업데이트에 따른 명령어 변경사항
kolla-ansible 19.7.0, 최근 Kolla-Ansible이 기존의 Bash 쉘 스크립트 방식에서 **Python 기반의 CLI(Command Line Interface)**로 시스템을 완전히 개편했습니다.

과거에는 kolla-ansible -i [인벤토리] [명령어] 순서로 작성했지만, 새로운 구조에서는 -i 같은 세부 옵션이 명령어 뒤로 가야 합니다.

노드 부트스트랩 명령어
```Bash
kolla-ansible bootstrap-servers -i multinode
```