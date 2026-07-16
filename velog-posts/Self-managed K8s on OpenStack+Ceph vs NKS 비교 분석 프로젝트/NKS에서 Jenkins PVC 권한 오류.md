## 들어가며

NKS 클러스터에 Jenkins를 배포하려다 `Permission denied` 하나로 꽤 오래 헤맸습니다. 표면적으로는 흔한 볼륨 권한 문제였지만, 일반적인 해결책(`fsGroup` 설정)이 전혀 통하지 않았습니다.

원인은 StorageClass에 파일시스템 타입을 선언하지 않은 것이 문제였고, 그게 CSI 드라이버의 권한 정책과 맞물려 `fsGroup`을 무시하고 있었습니다.


---

## 1. 증상

Helm으로 Jenkins를 배포하자 Pod가 계속 `Init:CrashLoopBackOff`에 빠졌습니다.

```
jenkins-0   0/2   Init:Error   ...
jenkins-0   0/2   Init:CrashLoopBackOff   ...
```

Init 컨테이너 로그를 확인하니 원인이 나왔습니다.

```bash
kubectl logs jenkins-0 -n cicd -c init --tail=20
```

```
/var/jenkins_config/apply_config.sh: 4: cannot create 
/var/jenkins_home/jenkins.install.UpgradeWizard.state: Permission denied
```

`/var/jenkins_home`은 PVC(Cinder 블록 스토리지)가 마운트된 경로입니다. Jenkins가 여기에 파일을 쓰려는데 권한이 없었습니다.

---

## 2. 첫 시도 — fsGroup 설정 (실패)

볼륨 권한 문제의 정석적인 해결책은 `fsGroup`입니다. Pod에 `fsGroup: 1000`을 지정하면, 마운트된 볼륨의 그룹 소유권을 1000으로 바꿔서 컨테이너(uid 1000의 jenkins 사용자)가 쓸 수 있게 해줍니다.

values에 관련 설정을 넣어봤습니다.

```yaml
controller:
  usePodSecurityContext: true
  runAsUser: 1000
  fsGroup: 1000
  fsGroupChangePolicy: "Always"
```

재배포했지만 **똑같은 에러**가 반복됐습니다. `fsGroupChangePolicy: Always`로 강제해도, `supplementalGroups`를 추가해도 소용없었습니다.

여기서 방향을 바꿨습니다. 같은 우회책을 반복하는 대신, 근본 원인을 파악하기로 했습니다.

---

## 3. 원인 추적 — 볼륨 권한을 직접 확인

Jenkins Pod가 계속 죽어서 볼륨 상태를 볼 수 없었습니다. 그래서 **같은 PVC를 마운트하는 디버그 Pod**를 띄워 권한을 직접 확인했습니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: debug-vol
  namespace: cicd
spec:
  securityContext:
    runAsUser: 1000
    fsGroup: 1000
    fsGroupChangePolicy: "Always"
  containers:
  - name: debug
    image: busybox
    command: ["sleep", "3600"]
    volumeMounts:
    - name: vol
      mountPath: /data
  volumes:
  - name: vol
    persistentVolumeClaim:
      claimName: jenkins
```

그리고 권한을 확인했습니다.

```bash
kubectl exec -it debug-vol -n cicd -- sh -c "id; ls -la /data; touch /data/test && echo WRITE_OK || echo WRITE_FAIL"
```

결과를 보면 원인을 찾을수 있었습니다.

```
uid=1000 gid=0(root) groups=0(root),1000
drwxr-xr-x  root root  casc_configs
drwx------  root root  lost+found
touch: /data/test: Permission denied
WRITE_FAIL
```

세 가지가 드러났습니다.

첫째, 볼륨의 소유권이 `root:root`입니다. `fsGroup: 1000`을 설정했는데도 그룹이 root(0)로 남아 있었습니다. **fsGroup이 적용되지 않은 것입니다.**

둘째, `lost+found` 디렉토리가 보입니다. 이건 ext4 파일시스템의 표식입니다. 볼륨이 ext4로 포맷됐다는 증거입니다.

셋째, 당연히 쓰기가 실패했습니다(WRITE_FAIL).

---

## 4. 근본 원인 — CSI 드라이버의 fsGroup 정책

fsGroup이 적용되지 않는 이유를 CSI 드라이버에서 찾았습니다.

```bash
kubectl get csidriver cinder.csi.openstack.org -o yaml | grep -i fsgroup
```

```
fsGroupPolicy: ReadWriteOnceWithFSType
```

**이 정책 이름 자체가 원인을 담고 있었습니다.**

`ReadWriteOnceWithFSType`는 "ReadWriteOnce 접근 모드이고, **파일시스템 타입(FSType)이 지정된 경우에만** fsGroup을 적용한다"는 의미입니다.

그런데 제가 만든 StorageClass를 다시 보니, `fsType`이 선언되어 있지 않았습니다.

```yaml
provisioner: cinder.csi.openstack.org
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
# fsType 선언이 없음
```

즉 볼륨은 실제로 ext4로 포맷됐지만(lost+found가 그 증거), StorageClass에 그 사실을 명시하지 않았습니다. 그래서 CSI 드라이버가 "FSType 조건을 충족하지 못했으니 fsGroup을 적용하지 않겠다"고 판단한 것입니다.

정리하면 이렇습니다.

```
StorageClass에 fsType 미선언
   → ReadWriteOnceWithFSType 정책이 조건 미충족으로 판단
   → fsGroup 적용 건너뜀
   → 볼륨이 root:root 소유로 남음
   → uid 1000의 Jenkins가 쓰기 불가
   → Permission denied
```

`fsGroup`을 아무리 설정해도 소용없던 이유가 이것이었습니다. 문제는 Pod의 securityContext가 아니라 StorageClass에 있었습니다.

---

## 5. 해결 — StorageClass에 fsType 추가

StorageClass의 `parameters`에 파일시스템 타입을 명시했습니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: cinder-default
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: cinder.csi.openstack.org
parameters:
  csi.storage.k8s.io/fstype: ext4
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
```

핵심은 추가한 이 두 줄입니다.

```yaml
parameters:
  csi.storage.k8s.io/fstype: ext4
```

이제 StorageClass가 "이 볼륨은 ext4다"라고 선언하므로, `ReadWriteOnceWithFSType` 정책이 조건을 충족해서 fsGroup을 적용하게 됩니다.

StorageClass는 일부 필드가 수정 불가라 지우고 다시 만들었습니다.

```bash
kubectl delete storageclass cinder-default
kubectl apply -f storageclass.yaml
```

그리고 Jenkins를 재배포했습니다. 기존 볼륨은 fsType 없이 만들어졌으니 PVC도 함께 삭제하고 새로 생성했습니다.

```bash
helm uninstall jenkins -n cicd
kubectl delete pvc jenkins -n cicd
helm install jenkins jenkins/jenkins -n cicd -f jenkins-values.yaml
```

---

## 6. 결과

Init 컨테이너가 정상적으로 통과했습니다.

```
jenkins-0   0/2   Init:0/2
jenkins-0   0/2   Init:1/2
jenkins-0   0/2   PodInitializing
jenkins-0   1/2   Running
```

이번에는 `Permission denied` 없이 볼륨에 쓰기가 됐습니다. fsGroup이 제대로 적용되어 볼륨 소유권이 jenkins 사용자로 바뀐 것입니다.

---

## 중간에 겪은 함정 하나 — PVC가 Terminating에서 멈춤

재배포 과정에서 PVC가 `Terminating` 상태로 몇십 분간 사라지지 않는 문제도 있었습니다.

```
jenkins   Terminating   pvc-6902fa11-...   8Gi   RWO   cinder-default
```

원인은 앞서 만든 디버그 Pod였습니다. 그 Pod가 PVC를 여전히 마운트하고 있어서, PVC의 보호 finalizer가 삭제를 막고 있었습니다. 디버그 Pod를 지우니 바로 해결됐습니다.

```bash
kubectl delete pod debug-vol -n cicd --force --grace-period=0
```

PVC가 Terminating에서 안 지워질 때는, **그 볼륨을 참조하는 Pod가 남아있는지** 먼저 확인하는 것이 순서입니다.

---

## 마치며

이 문제의 표면은 "볼륨 쓰기 권한이 없다"였지만, 본질은 "StorageClass에 fsType이 없어서 CSI의 fsGroup 정책이 조건을 충족하지 못했다"였습니다.

managed Kubernetes에서 CSI 드라이버의 세부 정책(`fsGroupPolicy`)까지 신경 쓸 일은 드뭅니다. 하지만 그 정책이 StorageClass의 사소한 누락(`fsType`)과 맞물리면 이렇게 원인을 찾기 어려운 문제가 됩니다.

앞으로 NKS에서 PVC를 쓰는 워크로드(Jenkins처럼 non-root로 실행되는 것들)를 배포할 때는, StorageClass에 `csi.storage.k8s.io/fstype: ext4`를 반드시 넣어야 한다는 걸 기억해야겠습니다.