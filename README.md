# Newspedia

Newspedia는 뉴스 기사와 이슈 문서를 바탕으로, 사용자가 검색과 탐색을 함께 수행할 수 있도록 설계한 RAG 기반 이슈 문서 베타 프로젝트입니다. 메인 화면 상단에는 검색엔진 스타일의 질의응답 인터페이스를 두고, 하단에는 주요 이슈를 카드 형태로 배치하며, 각 카드를 선택하면 구조화된 이슈 문서 상세 화면으로 이동하는 흐름을 목표로 합니다.

현재 저장소는 팀 개발을 시작하기 위한 초안 구조까지 정리된 상태입니다. Docker 기반 개발 환경과 서버 스택, Airflow 3 DAG 등록 구조, `IssueDocument` 중심 데이터 계약, Streamlit 데모 UI, 프로젝트 문서 세트가 준비되어 있습니다. 실제 뉴스 수집, 전처리, 벡터 저장, 검색, LangChain 기반 RAG 응답, 실데이터 UI 연결은 역할 분담 후 단계적으로 구현할 예정입니다.

## 1. 목표

본 프로젝트는 다음 목표를 기준으로 진행합니다.

- 환각을 최소화하면서, 팀이 수집한 뉴스 및 문서 데이터 범위 안에서 답변하는 RAG 기반 질의응답 시스템을 구현합니다.
- 문서를 벡터 형태로 임베딩하여 벡터 데이터베이스에 저장하고 검색할 수 있도록 구성합니다.
- LangChain을 활용하여 벡터 데이터베이스와 LLM을 연동합니다.
- 검색 기반 질의응답과 이슈 문서 탐색 경험을 하나의 서비스 안에서 제공합니다.

## 2. 현재 범위

현재 저장소에는 다음 항목이 반영되어 있습니다.

- `IssueDocument` 중심 코어 모델과 문서 생성 체인 진입점
- `collect_news`, `prepare_articles`, `embed_articles`, `analyze_issues` 4단계 파이프라인 스캐폴드
- Airflow 3 기준 DAG 등록 구조
- MongoDB, PostgreSQL, Airflow, dev 컨테이너용 Docker 설정
- Streamlit 기반 데모 UI
- 역할 분담, 환경 설정, 아키텍처, 워크플로우 문서

현재 기준에서 아직 구현이 필요한 영역은 다음과 같습니다.

- 뉴스 API 수집 로직
- 본문 스크래핑 및 전처리
- PostgreSQL 및 pgvector 저장 구조
- 임베딩 생성과 벡터 검색
- LangChain 기반 Retriever + LLM 질의응답
- 실데이터 기반 이슈 카드 및 문서 조회

## 3. 목표 사용자 경험

목표 사용자 경험은 다음과 같습니다.

1. 화면 최상단에서 검색창에 질문을 입력합니다.
2. 시스템이 벡터 데이터베이스에서 관련 기사 청크와 이슈 문서를 검색합니다.
3. LLM이 검색 결과를 바탕으로 답변을 생성합니다.
4. 답변 아래에 근거 기사와 관련 문서를 함께 표시합니다.
5. 사용자는 하단 카드 섹션에서 주요 이슈를 탐색할 수 있습니다.
6. 카드를 선택하면 이슈 문서 상세 페이지로 이동합니다.
7. 상세 페이지에서는 목차와 네비게이션 트리를 통해 관련 이슈를 계속 탐색할 수 있습니다.

현재 Streamlit UI는 이 목표 구조를 모두 구현한 상태는 아니며, 데모 `IssueDocument`를 사용해 카드와 상세 문서 흐름을 먼저 검증하는 단계입니다.

## 4. 빠른 시작

### 개발 환경

대부분의 개발자는 아래 순서로 로컬 개발 컨테이너를 사용하시면 됩니다.

```bash
bash scripts/setup-dev.sh
docker compose -p newspedia_dev exec dev bash
streamlit run app/main.py --server.address=0.0.0.0
```

접속 주소는 다음과 같습니다.

- Jupyter: `http://127.0.0.1:18888`
- Streamlit: `http://127.0.0.1:18501`

### 서버 스택

인프라, Airflow, DB, 통합 담당자는 아래 명령으로 서버 스택을 올리실 수 있습니다.

```bash
bash scripts/setup-server.sh
```

서버 스택은 다음 컨테이너로 구성됩니다.

- `newspedia-postgres`
- `newspedia-mongodb`
- `newspedia-airflow-init`
- `newspedia-airflow-web`
- `newspedia-airflow-scheduler`
- `newspedia-airflow-dag-processor`

접속 주소는 다음과 같습니다.

- Airflow: `http://localhost:18080`
- MongoDB: `localhost:17017`
- PostgreSQL: `localhost:15432`

## 5. 저장소 구조

```text
app/                    Streamlit UI를 구성합니다.
dags/                   Airflow DAG 정의를 관리합니다.
docker/                 컨테이너 이미지 정의를 담고 있습니다.
docs/                   계획, 구조, 역할, 작업 규칙, 환경 설정 문서를 제공합니다.
scripts/                개발 및 서버 기동 스크립트를 제공합니다.
src/core/               IssueDocument 및 문서 생성 로직을 담고 있습니다.
src/integrations/       뉴스 API, 스크래핑, 저장, 벡터 검색 연동 뼈대를 담고 있습니다.
src/pipeline/           DAG가 호출하는 실행 진입점을 제공합니다.
src/shared/             설정, tracing, 공용 기반 기능을 제공합니다.
```

## 6. 문서 안내

- [docs/PLAN.md](./docs/PLAN.md): 제품 목표, 베타 범위, RAG 흐름, 데이터 계약, 목표 구조
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md): 시스템 구조, 모듈 관계, 런타임 토폴로지
- [docs/ROLES.md](./docs/ROLES.md): 5인 팀 기준 역할 분담과 산출물 정의
- [docs/WORKFLOW.md](./docs/WORKFLOW.md): 구현 및 통합 워크플로우
- [docs/TEAM_SETUP.md](./docs/TEAM_SETUP.md): 개발자와 인프라 담당자의 환경 설정 절차
- [docs/AGENTS.md](./docs/AGENTS.md): AI 도구 작업 시 따라야 하는 공통 규칙
