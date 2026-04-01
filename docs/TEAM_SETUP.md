# Newspedia 개발 환경 설정 가이드

## 1. 문서 목적

이 문서는 Newspedia 프로젝트 구성원이 개발 환경을 처음 준비할 때 따라야 하는 절차를 정리한 문서이다.

서버 스택(MongoDB, PostgreSQL, Airflow)은 팀 공용 서버(encore)에서 운영되고 있으며, 각 팀원은 자신의 컴퓨터에서 `dev` 컨테이너만 띄워 작업한다. 서버 접속은 Tailscale VPN을 통해 이루어진다.

## 2. 전체 흐름

```
1. WSL 환경 준비 (Windows 사용자)
2. Tailscale 설치 (WSL 내부)
3. 저장소 clone
4. .env 설정
5. dev 컨테이너 실행
6. (선택) Windows 브라우저에서 Airflow/DB 접근 시 포트 포워딩
```

## 3. 준비 사항

- Git
- Docker Desktop 또는 Docker Engine
- 전달받은 `.env` 파일
- 전달받은 Tailscale Auth Key

> **용어 안내**
> - **Docker**는 프로그램 실행에 필요한 환경을 컨테이너 단위로 묶어 동일하게 실행할 수 있게 해 주는 도구이다.
> - **`.env` 파일**은 API 키, DB 계정, 포트 등 민감한 설정을 모아 두는 파일이다.
> - **Tailscale**은 팀 공용 서버에 접속할 때 사용하는 VPN 도구이다.

### Docker가 설치되어 있지 않은 경우

- Windows: https://docs.docker.com/desktop/setup/install/windows-install/ 에서 설치한다.
- macOS: https://docs.docker.com/desktop/setup/install/mac-install/ 또는 `brew install --cask docker`를 사용한다.
- Linux: 배포판에 맞는 Docker Engine 설치 절차를 따른다.

설치 후 확인:

```bash
docker --version
docker compose version
```

## 4. Tailscale 설치

개발 컨테이너에서 서버의 DB/Airflow에 접속하려면 Tailscale이 필요하다.

### WSL 사용자 (권장)

WSL 내부에 설치한다. Windows가 아닌 WSL 터미널에서 실행해야 한다.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

설치 후 팀에서 전달받은 Auth Key를 사용하여 접속한다.

```bash
sudo tailscale up --auth-key=<전달받은 Auth Key>
```

> Auth Key는 팀 Tailnet에 기기를 등록하기 위한 1회용 키이다. 서버 담당자에게 전달받는다.

설치 확인:

```bash
tailscale status
```

아래와 같이 encore 서버가 보이면 정상이다.

```
100.x.x.x      본인PC   user@  linux  -
100.106.29.101  encore   user@  linux  active; ...
```

### macOS 사용자

```bash
brew install --cask tailscale
```

Tailscale 앱을 실행한 뒤, 터미널에서 Auth Key로 접속한다.

```bash
sudo tailscale up --auth-key=<전달받은 Auth Key>
```

### 연결 확인

```bash
tailscale ping 100.106.29.101
```

`pong from encore` 응답이 오면 서버 연결이 정상이다.

## 5. 저장소 가져오기

```bash
git clone -b dev <repository-url>
cd Newspedia
```

## 6. `.env` 배치

전달받은 `.env` 파일을 프로젝트 루트에 둔다. 서버 접속 정보, DB 계정 등은 이미 설정되어 있다.

팀원 각자 수정해야 하는 항목:

| 항목 | 설명 |
|------|------|
| `LANGSMITH_TRACE_USER` | 본인 이름 (트레이스 구분용) |

## 7. dev 컨테이너 실행

```bash
bash scripts/setup-dev.sh
```

정상 실행 후 확인:

```bash
docker compose -p newspedia_dev ps
```

- 컨테이너 이름: `newspedia-dev`
- Jupyter: `http://127.0.0.1:18888`
- Streamlit 포트: `18501`

### dev 컨테이너 접속

```bash
docker compose -p newspedia_dev exec dev bash
```

컨테이너 안에서 할 수 있는 작업:

- Python 스크립트 실행
- Jupyter 실험
- 프롬프트 검증
- Streamlit 실행
- 테스트 및 임시 검증

### Streamlit 실행

dev 컨테이너 안에서:

```bash
streamlit run app/main.py --server.address=0.0.0.0
```

브라우저: `http://127.0.0.1:18501`

## 8. Windows 브라우저에서 서버 접근 (선택)

WSL에만 Tailscale이 설치되어 있으므로, Windows 브라우저에서 Airflow 웹 UI 등을 보려면 포트 포워딩이 필요하다.

### 사전 준비: openssh-server 설치 (최초 1회)

```bash
sudo apt install openssh-server -y
sudo service ssh start
```

### 포트 포워딩 실행

```bash
bash scripts/port-forward.sh
```

WSL 비밀번호를 입력하면 다음 포트가 포워딩된다.

| 서비스 | Windows 브라우저 주소 |
|--------|----------------------|
| Airflow | `http://127.0.0.1:18080` |
| PostgreSQL | `127.0.0.1:15432` |
| MongoDB | `127.0.0.1:17017` |

> `localhost`로 접속이 안 되는 경우 `127.0.0.1`을 사용해 본다.

## 9. 접속 정보 요약

### WSL / dev 컨테이너에서 (코드로 접속)

| 서비스 | 주소 |
|--------|------|
| PostgreSQL | `100.106.29.101:15432` |
| MongoDB | `100.106.29.101:17017` |
| Airflow API | `http://100.106.29.101:18080` |

### Windows 브라우저 / DB 클라이언트에서 (포트 포워딩 후)

| 서비스 | 주소 |
|--------|------|
| Airflow | `http://127.0.0.1:18080` |
| PostgreSQL | `127.0.0.1:15432` |
| MongoDB | `127.0.0.1:17017` |

### MongoDB 접속 URI

```
mongodb://skn25:skn25@100.106.29.101:17017/?authSource=admin
```

### PostgreSQL 접속 정보

- Host: `100.106.29.101`
- Port: `15432`
- User / Password: `.env` 참고
- Database: `newspedia_meta` 또는 `newspedia_app`

## 10. LangSmith 설정

LangSmith는 별도 컨테이너 없이 Python 실행 환경에서 사용한다. 공용 API 키는 `.env`에 이미 설정되어 있으므로, 각자 `LANGSMITH_TRACE_USER`에 본인 이름만 넣으면 된다.

```env
LANGSMITH_TRACE_USER=홍길동
```

## 11. 자주 발생하는 문제

### `.env` 파일을 못 읽는 경우

- 프로젝트 루트에 `.env`가 있는지 확인한다.
- 파일명이 `.env.txt`처럼 바뀌지 않았는지 확인한다.
- 필요한 값이 비어 있지 않은지 확인한다.

### Tailscale로 서버에 접속이 안 되는 경우

```bash
tailscale status        # encore가 보이는지 확인
tailscale ping 100.106.29.101  # 응답이 오는지 확인
```

- `no reply`: encore 서버의 Tailscale이 꺼져 있거나 네트워크 문제. 서버 담당자에게 확인 요청.
- status에 encore가 안 보임: 같은 Tailnet에 가입되어 있는지 확인.

### 포트 충돌 (Address already in use)

로컬에서 서버 컨테이너가 띄워져 있으면 포트가 충돌한다. 개발 PC에서는 서버 컨테이너를 띄울 필요가 없다.

```bash
docker ps  # 서버 컨테이너가 떠있는지 확인
docker compose -p newspedia_server -f docker-compose.server.yml down  # 서버 컨테이너 내리기
```

### Windows 브라우저에서 `localhost`로 접속이 안 되는 경우

`localhost` 대신 `127.0.0.1`을 사용한다.
