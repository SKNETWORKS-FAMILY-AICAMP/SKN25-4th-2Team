# Newspedia 개발 및 운영 워크플로우

## 1. 문서 목적

이 문서는 Newspedia 베타를 5인 팀이 병렬로 구현하고 통합할 때 따를 작업 흐름을 정리한 운영 기준 문서이다. 환경 설정 자체는 [TEAM_SETUP.md](./TEAM_SETUP.md)를 기준으로 하고, 본 문서는 "어떤 순서로 구현하고, 어떤 시점에 통합하며, 어떤 기준으로 완료를 판단할 것인가"를 설명한다.

## 2. 기본 원칙

프로젝트는 현재 초안 스캐폴드 상태까지 준비되어 있으므로, 이후 작업은 "큰 구조를 바꾸는 것"보다 "정해진 계층에 실제 기능을 채워 넣는 것"에 집중해야 한다. 각 팀원은 자신의 담당 영역에서 독립적으로 개발하되, 다음 원칙을 지켜야 한다.

- 제품 기준 문서는 항상 [PLAN.md](./PLAN.md)를 우선한다.
- 구조와 계층 설명은 [ARCHITECTURE.md](./ARCHITECTURE.md)를 기준으로 맞춘다.
- 역할 경계는 [ROLES.md](./ROLES.md)를 기준으로 유지한다.
- 공통 용어는 `IssueDocument`, `collect`, `prepare`, `embed`, `analyze`를 사용한다.
- DAG 파일은 가볍게 유지하고, 실제 로직은 `src/pipeline` 이하에 둔다.
- `IssueDocument`는 공용 계약이므로 팀 합의 없이 필드 구조를 바꾸지 않는다.
- 상단 검색 영역, 하단 카드 영역, 상세 문서 영역이라는 목표 화면 구성을 유지한다.

## 3. 작업 시작 전 공통 확인

작업 시작 전에는 아래 항목을 먼저 확인한다.

- `.env` 파일이 최신 버전인지
- Docker가 실행 중인지
- 본인이 사용하는 작업 모드가 무엇인지
- 필요한 컨테이너가 올라와 있는지
- 자신의 작업이 어느 계층에 속하는지

상태 확인 명령은 다음과 같다.

```bash
docker compose -p newspedia_dev ps
docker compose -p newspedia_server -f docker-compose.server.yml ps
```

## 4. 작업 모드

### 개발자 기본 모드

대부분의 개발자는 `dev` 컨테이너만 사용하면 된다.

```bash
bash scripts/setup-dev.sh
docker compose -p newspedia_dev exec dev bash
```

이 모드에서는 다음 작업을 수행한다.

- Python 코드 작성
- Jupyter 실험
- 프롬프트 테스트
- Streamlit UI 확인
- 단위 수준 검증

### 서버 통합 모드

인프라, Airflow, DB, 통합 테스트 담당자는 서버 스택을 함께 사용한다.

```bash
bash scripts/setup-server.sh
```

현재 서버 스택의 핵심 컨테이너는 다음과 같다.

- `newspedia-postgres`
- `newspedia-mongodb`
- `newspedia-airflow-init`
- `newspedia-airflow-web`
- `newspedia-airflow-scheduler`
- `newspedia-airflow-dag-processor`

여기서 `newspedia-airflow-init`은 1회성 초기화 컨테이너이므로 `Exited` 상태가 정상이다.

현재 초안 상태의 DAG는 구조 검증과 수동 실행을 우선하기 위해 `schedule=None`으로 등록되어 있다. 따라서 자동 주기를 기대하기보다, 우선은 DAG 등록과 수동 실행 경로가 정상인지 확인하는 것을 기준으로 삼는다.

## 5. 구현 순서

프로젝트는 아래 순서로 진행할 때 충돌이 가장 적다.

### 1단계: 공통 기준 고정

먼저 다음 항목을 고정한다.

- `IssueDocument` 계약
- 검색 질의응답 흐름의 입력과 출력 구조
- 환경 변수 이름
- DAG 이름과 단계 이름
- 저장할 핵심 테이블 목록
- 역할 분담

`IssueDocument` 계약은 `src/core/models.py`를 기준으로 유지한다. AI 도구를 사용하더라도 이 계약은 임의로 수정하지 않는 것을 원칙으로 한다. AI 작업 규칙은 [AGENTS.md](./AGENTS.md)를 따른다.

이 단계에서 구조가 흔들리면 이후 병렬 개발의 이점이 크게 줄어든다.

### 2단계: 계층별 병렬 구현 시작

이후 각 역할은 아래 위치를 중심으로 작업한다.

- 인프라 담당: `docker/`, `scripts/`, `dags/`, `src/pipeline/`, `src/shared/`
- 수집 담당: `src/integrations/news_search.py`, `src/integrations/article_scraper.py`, `src/integrations/raw_store.py`, `src/pipeline/collect_news.py`, `src/pipeline/prepare_articles.py`
- 저장 담당: `src/integrations/article_repository.py`, `src/integrations/issue_repository.py`, `src/integrations/embedding_client.py`, `src/integrations/vector_repository.py`, DB 스키마
- LLM · RAG 담당: `src/core/prompts/`, `src/core/chains.py`, `src/core/rag.py`
- UI 담당: `app/` 전체

### 3단계: 단계별 연결

병렬 구현이 어느 정도 진행되면 아래 순서로 연결한다.

1. 수집 결과를 MongoDB에 저장한다.
2. 정제 결과를 PostgreSQL에 저장한다.
3. 임베딩과 이슈 매핑을 저장한다.
4. 이슈별 기사 묶음을 읽어 `IssueDocument`를 생성한다.
5. 기사 청크 검색 경로를 연결한다.
6. 생성된 문서를 저장하고 UI에서 조회한다.
7. 검색 응답을 근거 기사와 함께 노출한다.

이 순서는 실제 사용자 경험과 데이터 흐름을 함께 만족시키는 최소 통합 경로이다.

## 6. 역할별 일상 작업 흐름

### 인프라 · Airflow 담당

인프라 담당자는 서버 스택이 깨지지 않도록 유지하면서, 다른 팀원이 붙일 수 있는 통합 경로를 열어주는 역할을 수행한다. 따라서 다음 순서를 반복적으로 수행한다.

1. Compose와 Docker 이미지를 확인한다.
2. Airflow DAG 등록 상태를 확인한다.
3. 팀원이 추가한 pipeline 코드를 DAG 경계와 연결한다.
4. 환경 변수 규칙과 실행 절차 문서를 갱신한다.

### 데이터 수집 담당

수집 담당자는 "기사 원문이 얼마나 신뢰할 수 있게 들어오는가"를 중심으로 작업한다.

1. API 호출 결과를 수집한다.
2. 원본을 MongoDB에 저장한다.
3. 스크래핑과 정제 품질을 검증한다.
4. 저장 담당과 정제 결과 스키마를 맞춘다.

### 저장 계층 담당

저장 담당자는 "다른 계층이 신뢰할 수 있는 저장 구조"를 만드는 역할을 한다.

1. PostgreSQL 스키마를 설계한다.
2. 저장 함수와 조회 함수를 만든다.
3. 이슈, 문서, 근거 기사 매핑 구조를 확정한다.
4. UI와 LLM 담당이 재사용할 읽기 함수를 제공한다.

### LLM · RAG 담당

LLM 담당자는 "기사가 어떤 규칙으로 문서가 되는가"와 "검색 결과가 어떤 규칙으로 답변이 되는가"를 책임진다.

1. 샘플 기사 묶음을 준비한다.
2. 프롬프트를 수정한다.
3. LangSmith trace로 결과를 비교한다.
4. `IssueDocument` 계약에 맞게 체인 출력을 안정화한다.
5. 검색 결과가 부족한 경우의 응답 기준을 정리한다.

### UI 담당

UI 담당자는 "현재 저장소가 어떤 사용자 경험을 보여 주는가"를 책임진다.

1. 데모 데이터 기반으로 검색 영역, 카드 영역, 상세 문서 영역 흐름을 먼저 고정한다.
2. 섹션 구조와 문서 가독성을 맞춘다.
3. 저장 담당과 조회 계약을 협의한다.
4. 실데이터 연결 후 빈 상태와 오류 상태를 보완한다.
5. 목차와 네비게이션 트리 구조를 상세 화면에 반영한다.

## 7. LangSmith 운영 방식

LangSmith는 개인 API 키를 사용하되, 공용 프로젝트 기준으로 trace를 축적한다. 이렇게 하면 각자 로컬에서 실험하더라도 동일 프로젝트 안에서 결과를 비교할 수 있다.

trace 구분 기준은 다음과 같다.

- `collect`: 뉴스 수집
- `prepare`: 기사 전처리
- `embed`: 임베딩 및 이슈 묶기
- `analyze`: 이슈 문서 생성

문서 생성 품질 검토는 특히 `stage=analyze`를 중심으로 수행한다.

## 8. 통합 확인 순서

기능을 붙일 때는 아래 순서로 점검한다.

1. MongoDB에 원본 수집 결과가 저장되는지 확인한다.
2. PostgreSQL에 정제 기사와 청크가 저장되는지 확인한다.
3. 임베딩과 이슈 매핑이 저장되는지 확인한다.
4. `IssueDocument`가 생성되는지 확인한다.
5. 문서 저장 결과를 다시 조회할 수 있는지 확인한다.
6. Streamlit에서 검색 영역, 카드 영역, 상세 문서가 정상 렌더링되는지 확인한다.
7. 검색 결과와 근거 기사가 함께 노출되는지 확인한다.
8. Airflow에서 해당 단계가 실제로 실행 가능한지 확인한다.
9. LangSmith trace가 남는지 확인한다.

## 9. 자주 쓰는 명령

```bash
bash scripts/setup-dev.sh
bash scripts/setup-server.sh
docker compose -p newspedia_dev exec dev bash
docker compose -p newspedia_dev ps
docker compose -p newspedia_server -f docker-compose.server.yml ps
streamlit run app/main.py --server.address=0.0.0.0
docker exec newspedia-airflow-web airflow dags list
```

## 10. 문제 발생 시 대응 순서

### 컨테이너가 뜨지 않는 경우

1. Docker 실행 여부를 확인한다.
2. `.env` 존재 여부를 확인한다.
3. `docker compose ... ps`로 상태를 확인한다.
4. 필요한 경우 `setup-dev.sh` 또는 `setup-server.sh`를 다시 실행한다.

### Airflow에서 DAG가 보이지 않는 경우

1. `newspedia-airflow-dag-processor`가 실행 중인지 확인한다.
2. `newspedia-airflow-web`과 `newspedia-airflow-scheduler` 상태를 확인한다.
3. `docker exec newspedia-airflow-web airflow dags list`로 등록 상태를 확인한다.
4. DAG 파일이 `src/pipeline`을 올바르게 호출하는지 확인한다.

### 문서 생성 결과가 이상한 경우

1. LangSmith trace를 확인한다.
2. 입력 기사 묶음이 정상인지 확인한다.
3. 프롬프트 변경 이력을 확인한다.
4. `IssueDocument` 계약이 깨지지 않았는지 확인한다.

### UI에 데이터가 안 보이는 경우

1. 현재 UI가 데모 데이터 모드인지 실데이터 모드인지 확인한다.
2. 검색 영역 문제인지 카드 조회 문제인지 상세 렌더링 문제인지 먼저 분리한다.
3. DB 조회 함수가 값을 반환하는지 확인한다.
4. 렌더링 계층에서 빈 상태 처리 로직을 확인한다.

## 11. 작업 마무리 기준

작업을 마무리하기 전에는 아래 항목을 확인한다.

- 변경한 코드가 어느 계층에 속하는지 명확한가
- 다른 담당자에게 넘길 입력/출력 계약이 정리되어 있는가
- 문서와 구현이 어긋나지 않는가
- `.env`와 개인 실험 파일을 커밋하지 않았는가
- 필요 시 README, PLAN, ARCHITECTURE, ROLES, WORKFLOW, TEAM_SETUP, AGENTS 중 관련 문서를 같이 갱신했는가

현재 단계의 핵심은 "각자 맡은 기능을 빨리 만드는 것"만이 아니라, "최종적으로 무리 없이 통합 가능한 구조를 유지하는 것"이다. 따라서 빠른 구현과 함께 계약 유지, 문서 반영, 실행 경로 확인을 동일한 비중으로 관리해야 한다.
