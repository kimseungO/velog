

### 1. 노드에서 다른 노드를 구독(subscribe)하는 방법
구독을 위해서는 `rclpy` 라이브러리를 사용하며, 구독하려는 메시지 타입과 토픽 이름을 지정해야 합니다.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String  # 구독할 메시지 타입

class MySubscriberNode(Node):

    def __init__(self):
        super().__init__('my_subscriber_node')
        self.subscription = self.create_subscription(
            String,               # 구독할 메시지 타입
            'topic_name',          # 구독할 토픽 이름
            self.listener_callback,# 콜백 함수
            10                     # 큐 사이즈
        )
        self.subscription  # 방금 생성한 구독 객체를 이용하는 것을 방지하기 위해 선언

    def listener_callback(self, msg):
        self.get_logger().info('Received: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    node = MySubscriberNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

위 코드에서:
- `create_subscription` 함수를 사용하여 구독자를 생성합니다.
- 메시지가 수신되면, 지정된 콜백 함수 `listener_callback`이 호출됩니다.

### 2. 노드에서 데이터를 발행(publish)하는 방법
발행 노드도 `rclpy` 라이브러리를 사용하여 생성할 수 있으며, 발행하려는 메시지 타입을 지정해야 합니다.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String  # 발행할 메시지 타입

class MyPublisherNode(Node):

    def __init__(self):
        super().__init__('my_publisher_node')
        self.publisher_ = self.create_publisher(String, 'topic_name', 10)  # 발행할 토픽과 메시지 타입 지정
        timer_period = 2.0  # 발행 주기 (2초마다 메시지 발행)
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello, ROS2'
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    node = MyPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

위 코드에서:
- `create_publisher` 함수를 사용하여 발행자를 생성합니다.
- 타이머 콜백 `timer_callback` 함수에서 주기적으로 메시지를 생성하고 발행합니다.


**메세지 타입 예시**
```python
from std_msgs.msg import Int32  # 정수형 메시지
from sensor_msgs.msg import Image  # 이미지 메시지
from geometry_msgs.msg import Point  # 3D 좌표 메시지
```

- 메시지를 발행할 때나 구독할 때 이처럼 적절한 메시지 타입을 지정해야 합니다.

