# Django microservices

WIP

### mysqlclient 패키지

- `python3-dev`: Python 개발 헤더 파일을 설치

mysqlclient 패키지는 C 확장 모듈로 구성되어 있으므로 Python 개발 헤더 파일이 필요

- `default-libmysqlclient-dev`: MySQL 클라이언트 라이브러리 개발 파일을 설치

mysqlclient 패키지는 MySQL 클라이언트 라이브러리와 연동되어 작동하기 때문에 해당 라이브러리 개발 파일이 필요

- `build-essential`: 필수적인 빌드 도구를 설치

mysqlclient 패키지를 빌드하고 컴파일하기 위해 필요한 도구들이 포함되어 있습니다.

``` bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
```

### docker compose exec backend sh

``` bash
python manage.py makemigrations
python manage.py migrate
```