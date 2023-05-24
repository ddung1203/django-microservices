# Python Microservices Web App - Django, Flask, React, DevOps

MSA는 각각을 Micro하게 나눈 서비스 지향 아키텍처로, 필요한 부분만 업데이트 및 배포가 가능하다.

MSA는 API를 통해서만 상호작용할 수 있으며, 각각의 서비스는 end-point를 API 형태로 외부에 노출하고, 실질적인 세부 사항은 모두 추상화한다.

## Architecture

![Architecture](./img/architecture.png)

상기와 같이 앱을 서로 통신하는 작은 부분으로 나눌 수 있다. 이를 통해 트래픽을 기반으로 애플리케이션을 쉽게 확장할 수 있으며, 일부 장애가 전체 서비스로 확장될 가능성이 낮다.

## Kubernetes settings

| name | cpu | memory | ip |
| --- | --- | --- | --- |
| k8s-master | 4 | 6144 | 192.168.100.100 |
| k8s-node1 | 2 | 4096 | 192.168.100.101 |
| k8s-node2 | 2 | 4096 | 192.168.100.102 |
| k8s-node3 | 2 | 4096 | 192.168.100.103 |

기본적으로 NFS를 이용하여 storage를 사용하는 `Pod`를 배포하기 위해 Kubernetes Cluster 상에서 NFS Storage를 사용할 수 있도록 Provisioner를 설정하였다. 이는 ServiceAccount로서 Kubernetes Cluster 상에서 `PV`를 배포할 수 있도록 권한을 부여해 주는 역할을 한다. 

[TIL - 동적 프로비저닝](https://github.com/ddung1203/TIL/blob/main/k8s/10_Volume.md#%EB%8F%99%EC%A0%81-%ED%94%84%EB%A1%9C%EB%B9%84%EC%A0%80%EB%8B%9D)


### Admin

`admin.yaml`

Service는 `NodePort`로, `admin` 레이블을 가진 `Pod`를 선택한다. 8000 포트로 요청을 받아 해당 `Pod`의 8000 포트로 전달한다.

Deployment는 3개의 복제본을 생성하며, `admin` 레이블을 가진 `Pod`에 대한 설정을 지정한다. 또한 Pod Template에서는 `admin` 컨테이너를 정의하고, `python manage.py runserver 0.0.0.0:8000` 명령을 실행한다.

추가로 livenessProbe와 readinessProbe가 정의되어 있으며, `/api/products` 경로로 8000 포트에 HTTP GET 요청을 보내고 응답을 기다린다. initialDelaySeconds, periodSeconds 및 timeoutSeconds는 livenessProbe가 시작되기까지의 지연 시간, 주기적으로 실행되는 간격 및 타임아웃을 나타낸다.

또한 Pod Template에는 `initContainers`도 정의되어 있다. `initContainer`는 파드 내에서 실행되는 컨테이너로, 주로 초기화 작업을 수행하는 데 사용되며 하기 코드에서는 migration이라는 이름의 `initContainer`가 정의되어 있다. `initContainer`는 `python manage.py migrate` 명령을 실행하여 데이터베이스 마이그레이션 작업을 수행한다.

``` yaml
apiVersion: v1
kind: Service
metadata:
  name: admin-svc-np
spec:
  type: NodePort
  selector:
    app: admin
  ports:
    - port: 8000
      targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-deploy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: admin
  template:
    metadata:
      labels:
        app: admin
    spec:
      containers:
        - name: admin
          image: ddung1203/admin:10
          command: ["python", "manage.py", "runserver", "0.0.0.0:8000"]
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /api/products
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
          readinessProbe:
            httpGet:
              path: /api/products
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 2
            timeoutSeconds: 1
      initContainers:
        - name: migration
          image: ddung1203/admin:10
          command: ["python", "manage.py", "migrate"]
```

`admin-mysql-deployment.yaml`

하기 코드는 Kubernetes 클러스터 내에서 실행되는 MySQL 데이터베이스를 위한 Service와 Deployment를 정의한다.

먼저, `admin-mysql` Service는 MySQL 데이터베이스에 대한 접근을 제공하기 위해 사용된다. Service는 3306 포트로 접근 가능하며, `admin-mysql` 레이블을 가진 파드를 선택한다. 또한, `clusterIP: None`으로 설정되어 내부 클러스터 IP를 할당하지 않다. 이로 인해 헤드리스 서비스로 만들어 로드밸런싱이 필요없거나 단일 서비스 IP가 필요 없는 경우에 하기와 같이 사용한다.

다음으로, `admin-mysql` Deployment는 `admin-mysql` 레이블을 가진 파드를 선택하며 배포 전략은 Recreate로 설정되어 있어 파드를 재생성하는 방식으로 업데이트를 수행한다.

Pod Template에서는 MySQL 컨테이너가 정의되어 있다. 컨테이너에는 환경 변수가 설정되어 있으며, 이는 `admin-mysql-secret`이라는 이름의 Secret에서 값을 가져온다. 환경 변수로는 `MYSQL_DATABASE`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD가` 있으며, 컨테이너는 3306 포트를 열고 `admin-mysql`이라는 이름으로 서비스에 연결된다.

컨테이너에는 `admin-mysql-persistent-storage`라는 이름의 볼륨이 마운트되어 있다. 이는 MySQL 데이터를 지속적으로 저장하기 위한 볼륨으로, `/var/lib/mysql` 경로에 마운트된다.

또한, 컨테이너에는 자원 요청이 정의되어 있으며, CPU는 `500m(0.5)`를 요청하고, 메모리는 `1Gi`를 요청한다.

컨테이너에는 `livenessProbe`와 `readinessProbe`가 정의되어 있다. `livenessProbe`는 컨테이너의 상태를 확인하기 위해 `mysqladmin ping -p$MYSQL_PASSWORD` 명령을 실행한다. `initialDelaySeconds`, `periodSeconds` 및 `timeoutSeconds`는 `livenessProbe`가 시작되기까지의 지연 시간, 주기적으로 실행되는 간격 및 타임아웃을 나타낸다.

마지막으로 배포에는 `admin-mysql-pv-claim`라는 이름의 PVC는 NFS 클라이언트를 위한 `storageClassName`을 사용하며, ReadWriteMany 액세스 모드로 설정되어 여러 파드에서 동시에 읽고 쓸 수 있다. 요청된 스토리지는 5Gi로 지정되어 있다.

``` yaml
apiVersion: v1
kind: Service
metadata:
  name: admin-mysql
spec:
  ports:
  - port: 3306
  selector:
    app: admin-mysql
  clusterIP: None
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-mysql
spec:
  selector:
    matchLabels:
      app: admin-mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: admin-mysql
    spec:
      containers:
      - image: mysql:8.0.33-debian
        name: admin-mysql
        env:
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: admin-mysql-secret
              key: MYSQL_DATABASE
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: admin-mysql-secret
              key: MYSQL_PASSWORD
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: admin-mysql-secret
              key: MYSQL_ROOT_PASSWORD
        ports:
        - containerPort: 3306
          name: admin-mysql
        volumeMounts:
        - name: admin-mysql-persistent-storage
          mountPath: /var/lib/mysql
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          exec:
            command: ["/bin/sh", "-c", "mysqladmin ping -p$MYSQL_PASSWORD"]
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          exec:
            # Check we can execute queries over TCP (skip-networking is off).
            command: ["/bin/sh", "-c", "mysqladmin ping -p$MYSQL_PASSWORD"]
          initialDelaySeconds: 5
          periodSeconds: 2
          timeoutSeconds: 1
      volumes:
      - name: admin-mysql-persistent-storage
        persistentVolumeClaim:
          claimName: admin-mysql-pv-claim
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: admin-mysql-pv-claim
spec:
  storageClassName: nfs-client
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

`admin-mysql-secret.yaml`
``` yaml
apiVersion: v1
kind: Secret
metadata:
  name: admin-mysql-secret
type: Opaque
data:
  MYSQL_DATABASE: YWRtaW4=
  MYSQL_PASSWORD: cm9vdA==
  MYSQL_ROOT_PASSWORD: cm9vdA==
```

`Dockerfile`

admin 이미지의 Dockerfile

``` Dockerfile
FROM python:3.10.6
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

RUN python manage.py makemigrations products

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8000
```

admin queue 이미지의 Dockerfile

``` Dockerfile
FROM python:3.10.6
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

CMD ["python", "consumer.py"]
```

`backend-ing.yaml`

Ingress 리소스는 Nginx Ingress 컨트롤러의 어노테이션을 포함하고 있다. nginx.ingress.kubernetes.io/rewrite-target 어노테이션은 URL을 재작성하는 데 사용되며, 이 경우 `/admin` 경로는 `/`로, `/main` 경로는 `/`로 재작성된다.

Ingress 리소스의 구성은 다음과 같다.

- spec 섹션은 Ingress의 규칙 및 설정을 정의
- rules 섹션은 호스트와 해당 호스트로의 요청에 대한 경로를 정의
- host는 호스트 패턴을 지정. `*.nip.io`는 모든 서브도메인에 대해 `nip.io` 도메인을 사용하겠다는 것을 의미
- http는 HTTP 프로토콜에 대한 경로 및 백엔드 서비스를 정의
- paths는 경로 및 해당 경로로의 요청을 처리할 백엔드 서비스를 지정
- path는 요청 경로를 나타내며, `/admin(/|$)(.*)`는 `/admin`으로 시작하는 모든 경로 및 하위 경로를 나타낸다. `/main(/|$)(.*)`는 `/main`으로 시작하는 모든 경로 및 하위 경로를 나타낸다.
- pathType은 경로 유형을 지정. Prefix는 경로 접두사를 기준으로 매칭됨을 의미.

위의 Ingress 리소스를 사용하면 `/admin` 및 `/main` 경로에 대한 요청이 각각 `admin-svc-np`와 `main-svc-np`라는 이름의 서비스로 전달되도록 설정된다. 이를 통해 클러스터 외부에서 애플리케이션의 다른 경로에 대한 액세스를 가능하게 한다.

``` yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: react-ing
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
    - host: '*.nip.io'
      http:
        paths:
          - path: /admin(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: admin-svc-np
                port:
                  number: 8000
          - path: /main(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: main-svc-np
                port:
                  number: 5000
```

`rabbitmq.yaml`

RabbitMQ는 오픈 소스 메시지 브로커 소프트웨어이다. 다양한 프로토콜을 지원하며, 분산 메시징 시스템에서 사용되어 복잡한 애플리케이션 간에 메시지 전달을 단순화하고 확장성을 제공한다.

- 메시지 큐: RabbitMQ는 메시지 큐를 통해 메시지를 안전하게 저장하고 전달한다. Producer는 메시지를 큐에 전송하고, Consumer는 큐에서 메시지를 가져와 처리할 수 있다.
- AMQP 프로토콜: RabbitMQ는 AMQP(Advanced Message Queuing Protocol) 프로토콜을 기반으로 동작한다. AMQP는 메시지 브로커와 클라이언트 간에 안정적인 메시지 전달을 위한 표준 프로토콜이다.
- 큐 패턴: RabbitMQ는 다양한 큐 패턴을 지원한다. Direct, Fanout, Topic, Headers 등의 패턴을 사용하여 메시지 라우팅과 구독을 관리할 수 있다.
- Publish-Subscribe 모델: RabbitMQ는 발행-구독(Publish-Subscribe) 모델을 지원하여 하나의 메시지를 여러 개의 소비자에게 전달할 수 있다. 이를 통해 다수의 애플리케이션 간에 이벤트 기반 통신을 구축할 수 있다.
- 메시지 지속성: RabbitMQ는 메시지를 디스크에 지속적으로 저장하여 안전하게 보호한다. 이를 통해 메시지 손실이나 장애 발생 시에도 데이터의 안정성을 유지할 수 있다.
- 클러스터링: RabbitMQ는 여러 노드로 구성된 클러스터를 형성하여 고가용성과 확장성을 제공한다. 클러스터링을 통해 메시지 처리 능력을 향상시키고 장애 복구 기능을 제공할 수 있다.
- 관리 도구: RabbitMQ는 웹 기반 관리 도구를 제공하여 관리자가 큐, 교환기, 바인딩 등을 모니터링하고 구성할 수 있다. 또한, 통계 정보와 로그를 확인하여 시스템 성능을 모니터링할 수 있다.

``` yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq-svc
spec:
  clusterIP: None
  selector:
    app: rabbitmq
  ports:
  - port: 5672
    targetPort: 5672
    name: amqp
  - port: 15672
    targetPort: 15672
    name: console 
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
        - name: myweb
          image: rabbitmq:management
          ports:
            - containerPort: 5672
              protocol: TCP
            - containerPort: 15672
              protocol: TCP
```