변수 설정하기
![](https://velog.velcdn.com/images/rtd7878/post/a180f411-9b68-479b-8ab9-5a9ae5c040b4/image.png)

variables.tf 파일에 변수를 설정한다.
variables.tf
```python
variable "aws_region" {
    type = string
    default = "ap-northeast-2"
    description = "AWS Region"
}

variable "vpc_cidr" {
    type = string
    default = "10.0.0.0/16"
    description = "CIDR Block for the vpc"
}

variable "vpc_name" {
    type = string
    default = "example-vpc"
    description = "VPC Name"
}
```

main.tf 파일에 변수를 이용해 resource를 생성할 수 있다.
```python
provider "aws" {
    region = var.aws_region
}


# vpc 생성
resource "aws_vpc" "main" {
    cidr_block = var.vpc_cidr
    enable_dns_support = true
    enable_dns_hostnames = true

    tags = {
        Name = var.vpc_name
    }
}
```

terraform.tfvars
이 파일은 변수 값을 따로 붙여주는 파일이다. 이게 필요한 이유는 개발, 운영 등 각각의 사용처에 따라 변수 값을 붙여서 재사용성을 높인다.

variables.tf 파일이 아래와 같을때
```python
variable "aws_region" {
    type = string
#    default = "ap-northeast-2"
    description = "AWS Region"
}

variable "vpc_cidr" {
    type = string
#    default = "10.0.0.0/16"
    description = "CIDR Block for the vpc"
}

variable "vpc_name" {
    type = string
#    default = "example-vpc"
    description = "VPC Name"
}
```

terraform.tfvars 파일에 다음과 같이 변수를 설정해줄수 있다.
```python
aws_region = "ap-northeast-2"
vpc_cidr = "10.0.0.0/24"
vpc_name = "Example-vpc"
```


IAC 단점
- 코딩 진입 장벽
- 느리다
- 장애 상황에서 복구가 어렵다. (코드 수정 및 테스트)
- 그러다보니 공부가 많이 필요