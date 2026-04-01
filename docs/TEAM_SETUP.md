# Newspedia 개발 환경 설정 가이드

## 1. 문서 목적

이 문서는 Newspedia 프로젝트 구성원이 개발 환경을 처음 준비할 때 따라야 하는 절차를 정리한 문서이다. 현재 저장소는 두 가지 실행 모드를 제공한다. 첫째는 대부분의 개발자가 사용하는 `dev` 컨테이너 기반 개발 모드이고, 둘째는 인프라, Airflow, DB, 통합 검증 담당자가 사용하는 서버 스택 모드이다.

프로젝트 초안 단계에서는 모든 팀원이 동일한 환경 기준으로 작업을 시작해야 한다. 각자 편한 방식으로 실행하기보다, 본 문서의 기준에 맞춰 Docker, `.env`, 개발 컨테이너, 서버 스택을 통일해 두는 편이 좋다.

## 2. 준비 사항

다음 항목이 먼저 준비되어 있어야 한다.

- 프로젝트 저장소
- 전달받은 `.env` 파일
- Docker Desktop 또는 Docker Engine
- Git
- 선택 사항: Tailscale 또는 팀 공용 서버 접속 수단

> **용어 안내**
> - **Docker**는 프로그램 실행에 필요한 환경을 컨테이너 단위로 묶어 동일하게 실행할 수 있게 해 주는 도구이다.
> - **`.env` 파일**은 API 키, DB 계정, 포트 등 민감한 설정을 모아 두는 파일이다.
> - **Tailscale**은 팀 공용 서버에 사설 네트워크로 접속할 때 사용할 수 있는 VPN 도구이다. 필수는 아니지만, 팀이 공용 서버를 쓰는 경우 유용하다.

### Docker가 설치되어 있지 않은 경우

- Windows: https://docs.docker.com/desktop/setup/install/windows-install/ 에서 설치한다.
- macOS: https://docs.docker.com/desktop/setup/install/mac-install/ 또는 `brew install --cask docker`를 사용한다.
- Linux: 배포판에 맞는 Docker Engine 설치 절차를 따른다.

설치 후 Docker가 실제로 동작하는지 확인한다.

```bash
docker --version
docker compose version
```

## 3. 저장소 가져오기

원하는 작업 폴더에서 저장소를 clone한다.

```bash
git clone <repository-url>
cd Newspedia
```

## 4. `.env` 배치

전달받은 `.env` 파일을 프로젝트 루트에 둔다.

현재 저장소에서 중요도가 높은 항목은 다음과 같다.

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `LANGSMITH_WORKSPACE_ID`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `NEWS_POSTGRES_DB`
- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`
- `SERVER_POSTGRES_PORT`
- `SERVER_MONGO_PORT`
- `SERVER_AIRFLOW_PORT`

공용 서버를 붙여서 쓰는 경우에는 아래 항목도 팀 기준에 맞춰 맞춘다.

- `MONGO_HOST`
- `POSTGRES_HOST`
- `AIRFLOW_BASE_URL`

예시는 다음과 같다.

```env
MONGO_HOST=100.x.x.x
POSTGRES_HOST=100.x.x.x
AIRFLOW_BASE_URL=http://100.x.x.x:18080
```

## 5. 실행 모드 선택

### A. 일반 개발 모드

대부분의 팀원은 이 모드만으로 작업을 시작할 수 있다. UI 개발, 프롬프트 실험, RAG 응답 체인 개발, 코어 로직 작성, 일반 Python 개발은 `dev` 컨테이너만으로 충분하다.

### B. 서버 통합 모드

인프라 담당, Airflow 담당, DB 담당, 통합 테스트 담당은 서버 스택까지 함께 올리는 것이 좋다. 이 모드에서는 MongoDB, PostgreSQL, Airflow API 서버, 스케줄러, DAG 파서까지 함께 확인할 수 있다.

### C. 공용 서버 접속 모드

팀이 중앙 서버를 따로 운영한다면, 로컬에서는 `dev` 컨테이너만 띄우고 MongoDB, PostgreSQL, Airflow는 공용 서버 주소로 붙는 방식도 사용할 수 있다. 이 경우 `.env`의 `MONGO_HOST`, `POSTGRES_HOST`, `AIRFLOW_BASE_URL`를 서버 주소 기준으로 맞춘다.

## 6. 개발 컨테이너 실행

일반 개발 모드에서는 프로젝트 루트에서 아래 명령을 실행한다.

```bash
bash scripts/setup-dev.sh
```

정상 실행 후 확인할 항목은 다음과 같다.

- 컨테이너 이름: `newspedia-dev`
- Jupyter 주소: `http://127.0.0.1:18888`
- Streamlit 포트: `18501`

상태 확인 명령은 다음과 같다.

```bash
docker compose -p newspedia_dev ps
```

## 7. dev 컨테이너 접속

아래 명령으로 `dev` 컨테이너에 접속한다.

```bash
docker compose -p newspedia_dev exec dev bash
```

컨테이너 안에서는 다음 작업을 수행할 수 있다.

- Python 스크립트 실행
- Jupyter 실험
- 프롬프트 검증
- Streamlit 실행
- 테스트 및 임시 검증

## 8. Streamlit 실행

`dev` 컨테이너 안에서 아래 명령을 실행한다.

```bash
streamlit run app/main.py --server.address=0.0.0.0
```

브라우저에서는 아래 주소로 접속한다.

```text
http://127.0.0.1:18501
```

현재 UI는 데모 `IssueDocument`를 사용하므로, UI 담당자는 먼저 검색 영역, 카드 섹션, 문서 상세 흐름을 정리한 뒤 저장 계층과 연결하는 방식으로 작업하면 된다. 수집 담당과 저장 담당은 `src/integrations` 아래에 준비된 역할별 파일 뼈대에서 바로 구현을 시작하면 된다.

## 9. 서버 스택 실행

인프라, Airflow, DB, 통합 검증이 필요한 경우에는 아래 명령을 실행한다.

```bash
bash scripts/setup-server.sh
```

이 명령은 다음 구성을 올린다.

- `newspedia-postgres`
- `newspedia-mongodb`
- `newspedia-airflow-init`
- `newspedia-airflow-web`
- `newspedia-airflow-scheduler`
- `newspedia-airflow-dag-processor`

`newspedia-airflow-init`은 초기화 전용 컨테이너이므로, 완료 후 `Exited` 상태가 정상이다. 나머지 컨테이너는 `Up` 상태여야 한다.

상태 확인 명령은 다음과 같다.

```bash
docker compose -p newspedia_server -f docker-compose.server.yml ps
```

## 10. 접속 정보

### Jupyter

```text
http://127.0.0.1:18888
```

### Streamlit

```text
http://127.0.0.1:18501
```

### Airflow

```text
http://localhost:18080
```

### MongoDB

GUI 도구를 사용하는 경우 아래 URI를 사용할 수 있다.

```text
mongodb://<MONGO_INITDB_ROOT_USERNAME>:<MONGO_INITDB_ROOT_PASSWORD>@localhost:17017/?authSource=admin
```

공용 서버를 사용하는 경우에는 `localhost` 대신 해당 서버 주소를 사용한다.

### PostgreSQL

DBeaver 또는 다른 DB 도구에서 다음 정보를 사용한다.

- Host: `localhost`
- Port: `.env`의 `SERVER_POSTGRES_PORT`
- User: `.env`의 `POSTGRES_USER`
- Password: `.env`의 `POSTGRES_PASSWORD`
- Database: `.env`의 `POSTGRES_DB`

공용 서버를 사용하는 경우에는 Host를 팀 서버 주소로 바꾼다.

## 11. Tailscale 사용 시 추가 절차

팀이 공용 서버를 Tailscale로 운영하는 경우에만 이 절차를 따른다. 로컬에서 서버 스택을 직접 띄우는 경우에는 이 절을 생략해도 된다.

### WSL 사용자

WSL 사용자는 Windows가 아니라 **WSL 내부에 Tailscale을 설치하고 실행하는 것**을 권장한다.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale version
sudo tailscale up
tailscale status
tailscale ip -4
```

### macOS 사용자

macOS에서는 Tailscale 앱 또는 Homebrew를 사용할 수 있다.

```bash
brew install --cask tailscale
tailscale status
tailscale ip -4
```

연결 후 `.env`의 `MONGO_HOST`, `POSTGRES_HOST`, `AIRFLOW_BASE_URL`를 서버 주소 기준으로 맞춘다.

## 12. LangSmith 사용 방식

LangSmith는 별도 컨테이너 없이 Python 실행 환경에서 사용한다. 개인 API 키를 사용하되, 프로젝트명과 workspace는 팀 공용 기준으로 맞춘다. 이렇게 해야 각자의 로컬 실험 결과를 하나의 프로젝트 안에서 비교할 수 있다.

중요 항목은 다음과 같다.

- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `LANGSMITH_WORKSPACE_ID`
- `LANGSMITH_TRACING`

## 13. 현재 UI와 목표 UI 구분

현재 저장소의 Streamlit UI는 데모 `IssueDocument`를 기반으로 카드와 문서 상세 흐름을 먼저 검증하는 단계이다. `PLAN.md`에 정의된 목표 구조는 다음과 같다.

- 상단 검색창 기반 RAG 질의응답
- 하단 이슈 카드 탐색
- 문서 상세 페이지
- 목차와 네비게이션 트리

따라서 UI 관련 작업을 시작할 때는 "현재 구현된 화면"과 "계획상 목표 화면"을 구분해서 이해하는 것이 중요하다. 현재 구현은 초안이고, 목표 구조는 `PLAN.md`를 기준으로 확장한다.

## 14. 자주 발생하는 문제

### `.env` 파일을 못 읽는 경우

- 프로젝트 루트에 `.env`가 있는지 확인한다.
- 파일명이 `.env.txt`처럼 바뀌지 않았는지 확인한다.
- 필요한 값이 비어 있지 않은지 확인한다.
