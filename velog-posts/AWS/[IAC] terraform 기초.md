테라폼은 코드를 이용한 인프라 운영 자동화 툴이다.
코드를 이용한 인프라 운영 = IAC (Intelligent Automation Cloud)

IAC는 다음과 같은 장점을 가진다.
![](https://velog.velcdn.com/images/rtd7878/post/6019e514-7367-4add-a55e-1ac7657a875c/image.png)

실습

테라폼 설치 - 환경변수 설정 - IAM로그인

아래는 간단한 vpc 생성하는 테라폼 코드
```python
provider "aws" {
    region = "ap-northeast-2"
}

# vpc 생성
resource "aws_vpc" "terraform-vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_support = true
    enable_dns_hostnames = true

    tags = {
        Name = "terraform-vpc"
    }
}
```

퍼블릭 서브넷 2개 생성
```python
# 퍼블릭 서브넷 2개
resource "aws_subnet" "public_1"{
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = "10.0.1.0/24"
    availability_zone = "ap-northeast-2a"
    map_public_ip_on_launch = true

    tags = {
        Name = "public-subnet-1"
    }
}

resource "aws_subnet" "public_2"{
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = "10.0.2.0/24"
    availability_zone = "ap-northeast-2c"
    map_public_ip_on_launch = true

    tags = {
        Name = "public-subnet-2"
    }
}
```



IGW
```python
# IGW
resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.terraform-vpc.id
    tags = {
        Name = "example-igw"
    }
}
```

퍼블릭 라우팅 테이블
```python
# public rouote table
resource "aws_route_table" "public" {
    vpc_id = aws_vpc.terraform-vpc.id
    tags = {
        Name = "example-public-rt"
    }
}

```

라우팅 테이블에 IGW 경로 추가
```python
resource "aws_route" "public_route" {
    route_table_id = aws_route_table.public.id
    destination_cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
}
```

서브넷과 라우팅 테이블 연결
```python
resource "aws_route_table_association" "public_1" {
    subnet_id = aws_subnet.public_1.id
    route_table_id = aws_route_table.public.id
}
```

보안그룹
```python
resource "aws_security_group" "ec2_sg" {
    vpc_id = aws_vpc.terraform-vpc.id
    name = "example-ec2-sg"

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_block = ["183.96.187.252/32"]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_block = ["0.0.0.0/0"]
    }

    tags = {
        Name = "example-ec2-sg"
    }
}
```

ec2 생성
```python
# ec2
resource "aws_instance" "ec2_server" {
    ami = "ami-0c593c3690c32e925"
    instance_type = "t2.micro"
    subnet_id = aws_subnet.public_1.id
    associate_public_ip_address = true
    key_name = "kyobo"

    vpc_security_group_ids = [
        aws_security_group.ec2_sg.id
    ]

    tags = {
        Name = "ec2_server"
    }
}
```
만든 resource 확인 및 생성
```bash
terraform plan
terraform apply
```

삭제
```bash
terraform destroy
```