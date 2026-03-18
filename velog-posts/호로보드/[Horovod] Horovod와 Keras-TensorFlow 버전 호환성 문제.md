
**Horovod**를 사용해 분산 학습을 진행하던 중, Horovod의 **`hvd.callbacks.BroadcastGlobalVariablesCallback(0)`** 콜백을 사용해 여러 GPU에서 모델의 가중치를 동기화하려고 할 때 문제가 생겼다.

### 문제 발생

모델을 학습시키려는데, 엄청난 오류와 함께 다음과 같은 오류 메시지가 발생했다.

```plaintext

AttributeError: 'Variable' object has no attribute 'ref'
```

이 오류는 Horovod의 `hvd.callbacks.BroadcastGlobalVariablesCallback(0)` 함수가 **모델의 변수**를 브로드캐스트하려고 할 때, **Keras의 변수(`tf.Variable`)**에 대해 `.ref()` 메서드를 호출하려다가 발생한 것이었다. 하지만 최신 Keras에서는 더 이상 `ref()` 메서드를 지원하지 않고 있어, 학습이 중간에 중단되었다.

### 원인 분석

조사를 해보니, **Horovod**의 최신 버전은 작년 6월에 마지막으로 업데이트되었고, 그 이후로 **Keras**와 **TensorFlow**는 지속적으로 업데이트되어 왔다. 특히, Keras의 최신 버전에서는 `tf.Variable` 객체에 `ref()` 메서드가 더 이상 존재하지 않는다는 것을 알게 되었다. 하지만 Horovod는 아직 이 변화를 따라가지 못한 상태였고, 그래서 Keras와 TensorFlow의 최신 버전에서는 호환성 문제가 발생한 것이었다.

### 해결 과정

이 문제를 해결하기 위해, 나는 **Keras**와 **TensorFlow**의 버전을 낮추기로 했다. 최신 버전의 Horovod는 **Keras 2.15**와 **TensorFlow 2.15**에서는 정상적으로 동작한다는 정보를 확인했기 때문이다.

#### 1. Keras와 TensorFlow 제거

먼저, 현재 설치된 Keras와 TensorFlow를 제거했다.

```bash
pip uninstall keras tensorflow
```

#### 2. Keras 2.15 및 TensorFlow 2.15 설치

그런 다음, Keras 2.15와 TensorFlow 2.15 버전을 다시 설치했다. 이 버전들은 서로 호환되며, Horovod와도 잘 동작한다.

```bash
pip install keras==2.15 tensorflow==2.15
```

#### 3. Horovod와 함께 학습 재시도

Keras와 TensorFlow의 버전을 2.15로 맞추고 다시 학습을 진행해 보니, 더 이상 `ref()` 관련 오류는 발생하지 않았다. Horovod의 `hvd.callbacks.BroadcastGlobalVariablesCallback(0)` 함수도 정상적으로 작동했고, 학습이 원활하게 진행되었다.

