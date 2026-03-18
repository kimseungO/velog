<p>변수 설정하기
<img alt="" src="https://velog.velcdn.com/images/rtd7878/post/a180f411-9b68-479b-8ab9-5a9ae5c040b4/image.png" /></p>
<p>variables.tf 파일에 변수를 설정한다.
variables.tf</p>
<pre><code class="language-python">variable &quot;aws_region&quot; {
    type = string
    default = &quot;ap-northeast-2&quot;
    description = &quot;AWS Region&quot;
}

variable &quot;vpc_cidr&quot; {
    type = string
    default = &quot;10.0.0.0/16&quot;
    description = &quot;CIDR Block for the vpc&quot;
}

variable &quot;vpc_name&quot; {
    type = string
    default = &quot;example-vpc&quot;
    description = &quot;VPC Name&quot;
}</code></pre>
<p>main.tf 파일에 변수를 이용해 resource를 생성할 수 있다.</p>
<pre><code class="language-python">provider &quot;aws&quot; {
    region = var.aws_region
}


# vpc 생성
resource &quot;aws_vpc&quot; &quot;main&quot; {
    cidr_block = var.vpc_cidr
    enable_dns_support = true
    enable_dns_hostnames = true

    tags = {
        Name = var.vpc_name
    }
}</code></pre>
<p>terraform.tfvars
이 파일은 변수 값을 따로 붙여주는 파일이다. 이게 필요한 이유는 개발, 운영 등 각각의 사용처에 따라 변수 값을 붙여서 재사용성을 높인다.</p>
<p>variables.tf 파일이 아래와 같을때</p>
<pre><code class="language-python">variable &quot;aws_region&quot; {
    type = string
#    default = &quot;ap-northeast-2&quot;
    description = &quot;AWS Region&quot;
}

variable &quot;vpc_cidr&quot; {
    type = string
#    default = &quot;10.0.0.0/16&quot;
    description = &quot;CIDR Block for the vpc&quot;
}

variable &quot;vpc_name&quot; {
    type = string
#    default = &quot;example-vpc&quot;
    description = &quot;VPC Name&quot;
}</code></pre>
<p>terraform.tfvars 파일에 다음과 같이 변수를 설정해줄수 있다.</p>
<pre><code class="language-python">aws_region = &quot;ap-northeast-2&quot;
vpc_cidr = &quot;10.0.0.0/24&quot;
vpc_name = &quot;Example-vpc&quot;</code></pre>
<p>IAC 단점</p>
<ul>
<li>코딩 진입 장벽</li>
<li>느리다</li>
<li>장애 상황에서 복구가 어렵다. (코드 수정 및 테스트)</li>
<li>그러다보니 공부가 많이 필요</li>
</ul>