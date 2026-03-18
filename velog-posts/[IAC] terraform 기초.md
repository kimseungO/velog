<p>테라폼은 코드를 이용한 인프라 운영 자동화 툴이다.
코드를 이용한 인프라 운영 = IAC (Intelligent Automation Cloud)</p>
<p>IAC는 다음과 같은 장점을 가진다.
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/6019e514-7367-4add-a55e-1ac7657a875c/image.png" /></p>
<p>실습</p>
<p>테라폼 설치 - 환경변수 설정 - IAM로그인</p>
<p>아래는 간단한 vpc 생성하는 테라폼 코드</p>
<pre><code class="language-python">provider &quot;aws&quot; {
    region = &quot;ap-northeast-2&quot;
}

# vpc 생성
resource &quot;aws_vpc&quot; &quot;terraform-vpc&quot; {
    cidr_block = &quot;10.0.0.0/16&quot;
    enable_dns_support = true
    enable_dns_hostnames = true

    tags = {
        Name = &quot;terraform-vpc&quot;
    }
}</code></pre>
<p>퍼블릭 서브넷 2개 생성</p>
<pre><code class="language-python"># 퍼블릭 서브넷 2개
resource &quot;aws_subnet&quot; &quot;public_1&quot;{
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = &quot;10.0.1.0/24&quot;
    availability_zone = &quot;ap-northeast-2a&quot;
    map_public_ip_on_launch = true

    tags = {
        Name = &quot;public-subnet-1&quot;
    }
}

resource &quot;aws_subnet&quot; &quot;public_2&quot;{
    vpc_id = aws_vpc.terraform-vpc.id
    cidr_block = &quot;10.0.2.0/24&quot;
    availability_zone = &quot;ap-northeast-2c&quot;
    map_public_ip_on_launch = true

    tags = {
        Name = &quot;public-subnet-2&quot;
    }
}</code></pre>
<p>IGW</p>
<pre><code class="language-python"># IGW
resource &quot;aws_internet_gateway&quot; &quot;igw&quot; {
    vpc_id = aws_vpc.terraform-vpc.id
    tags = {
        Name = &quot;example-igw&quot;
    }
}</code></pre>
<p>퍼블릭 라우팅 테이블</p>
<pre><code class="language-python"># public rouote table
resource &quot;aws_route_table&quot; &quot;public&quot; {
    vpc_id = aws_vpc.terraform-vpc.id
    tags = {
        Name = &quot;example-public-rt&quot;
    }
}
</code></pre>
<p>라우팅 테이블에 IGW 경로 추가</p>
<pre><code class="language-python">resource &quot;aws_route&quot; &quot;public_route&quot; {
    route_table_id = aws_route_table.public.id
    destination_cidr_block = &quot;0.0.0.0/0&quot;
    gateway_id = aws_internet_gateway.igw.id
}</code></pre>
<p>서브넷과 라우팅 테이블 연결</p>
<pre><code class="language-python">resource &quot;aws_route_table_association&quot; &quot;public_1&quot; {
    subnet_id = aws_subnet.public_1.id
    route_table_id = aws_route_table.public.id
}</code></pre>
<p>보안그룹</p>
<pre><code class="language-python">resource &quot;aws_security_group&quot; &quot;ec2_sg&quot; {
    vpc_id = aws_vpc.terraform-vpc.id
    name = &quot;example-ec2-sg&quot;

    ingress {
        from_port = 22
        to_port = 22
        protocol = &quot;tcp&quot;
        cidr_block = [&quot;183.96.187.252/32&quot;]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = &quot;-1&quot;
        cidr_block = [&quot;0.0.0.0/0&quot;]
    }

    tags = {
        Name = &quot;example-ec2-sg&quot;
    }
}</code></pre>
<p>ec2 생성</p>
<pre><code class="language-python"># ec2
resource &quot;aws_instance&quot; &quot;ec2_server&quot; {
    ami = &quot;ami-0c593c3690c32e925&quot;
    instance_type = &quot;t2.micro&quot;
    subnet_id = aws_subnet.public_1.id
    associate_public_ip_address = true
    key_name = &quot;kyobo&quot;

    vpc_security_group_ids = [
        aws_security_group.ec2_sg.id
    ]

    tags = {
        Name = &quot;ec2_server&quot;
    }
}</code></pre>
<p>만든 resource 확인 및 생성</p>
<pre><code class="language-bash">terraform plan
terraform apply</code></pre>
<p>삭제</p>
<pre><code class="language-bash">terraform destroy</code></pre>