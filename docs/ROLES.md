# Newspedia 역할 분담

## 1. 문서 목적

이 문서는 Newspedia를 5인 팀이 병렬로 구현할 때 각자의 책임 범위, 소유 파일, 구현 대상, 산출물, 완료 기준을 구체적으로 정리한다. 현재 저장소는 초안 스캐폴드가 정리된 상태이며, 각 담당자는 자신이 소유하는 파일과 함수를 기준으로 독립적으로 구현하되 `IssueDocument` 계약과 문서 기준을 공통 인터페이스로 삼아 통합하는 방식으로 작업한다.

## 2. 기본 원칙

역할 분담은 파일을 나누는 작업이 아니다. 책임의 경계를 분명히 정해 병렬 개발이 가능하도록 하는 장치다. 각 담당자는 자신의 영역에서 설계 결정과 구현 우선순위를 주도할 수 있어야 하며, 동시에 다른 담당자가 의존하는 계약은 안정적으로 유지해야 한다.

본 프로젝트의 공통 기준은 다음과 같다.

- 제품 방향과 문서 구조 기준은 [PLAN.md](./PLAN.md)를 따른다.
- 도메인 데이터 계약은 `IssueDocument`를 기준으로 통일한다.
- `IssueDocument` 계약은 `src/core/models.py`와 [AGENTS.md](./AGENTS.md)에 정의된 절차 없이 변경하지 않는다.
- DAG 정의는 가볍게 유지하고, 실제 처리 로직은 `src/pipeline` 이하에 둔다.
- 외부 서비스 연동 코드는 `src/integrations`를 기본 위치로 삼는다.
- 결과물이 불완전하더라도 입력, 출력, 책임 경계는 문서로 먼저 확정한다.
- 파일 소유권이 명시된 파일은 해당 담당자만 수정한다. 다른 담당자의 파일을 수정해야 할 경우 반드시 해당 담당자와 협의한다.

## 3. 5인 팀 기준 역할 구성

| 역할 | 권장 인원 | 주 책임 |
|------|-----------|--------|
| **1. 인프라 · 데이터 파이프라인 담당** | 1명 | Docker, Compose, Airflow, 뉴스 수집, 스크래핑, DB 스키마, 초기 적재, 공용 설정 |
| **2. 저장 계층 담당** | 1명 | PostgreSQL Repository 구현, 기사/이슈 문서 CRUD, 조회 함수 |
| **3. 임베딩 · 클러스터링 · 벡터 검색 담당** | 1명 | 임베딩 생성, 청크 전략, pgvector 검색, 이슈 클러스터링 |
| **4. LLM · RAG 담당** | 1명 | 프롬프트, 체인, Retriever 조합, 질의응답, LangSmith 평가 |
| **5. UI · 문서 소비 계층 담당** | 1명 | Streamlit 전체 화면, 검색 UX, 카드, 상세 문서, 네비게이션 |

이 배치는 기능 흐름과 책임 경계에 맞춰 구성했다. 인프라 · 데이터 파이프라인 담당자가 수집과 적재를 선행 완료하면, 나머지 4명은 실데이터가 들어 있는 DB를 기반으로 각자의 영역을 병렬 구현할 수 있다.

## 4. 역할별 상세

### 4-1. 인프라 · 데이터 파이프라인 담당

이 역할은 "다른 팀원이 실데이터 기반으로 개발을 시작할 수 있는 환경과 데이터"를 준비한다. Docker 이미지, Compose 구성, Airflow 서비스, DAG 설계, 뉴스 수집 클라이언트, 기사 스크래핑, MongoDB 원본 저장, PostgreSQL 스키마 설계, 초기 데이터 적재, 공용 설정과 tracing까지를 포함한다. 다른 팀원의 병렬 개발이 시작되기 전에 DB에 데이터가 들어 있는 상태를 만들어 두어야 한다.

#### 소유 파일

이 역할이 직접 소유하고 수정 권한을 갖는 파일은 다음과 같다.

**Docker · Compose · 스크립트**

- `docker-compose.yml` — 개발 컨테이너 구성
- `docker-compose.server.yml` — 서버 스택 구성 (Airflow, PostgreSQL, MongoDB)
- `docker/airflow/Dockerfile` — Airflow 3 서비스 이미지
- `docker/dev/Dockerfile` — 개발 환경 이미지
- `docker/mongo/Dockerfile` — MongoDB 이미지
- `docker/postgres/Dockerfile` — PostgreSQL + pgvector 이미지
- `docker/postgres/init/01-create-news-db.sh` — DB 초기화 스크립트
- `scripts/setup-dev.sh` — 개발 환경 기동 스크립트
- `scripts/setup-server.sh` — 서버 환경 기동 스크립트

**Airflow DAG 정의**

- `dags/collect_news.py` — 뉴스 수집 DAG
- `dags/prepare_articles.py` — 기사 전처리 DAG
- `dags/embed_articles.py` — 임베딩 및 이슈 클러스터링 DAG
- `dags/analyze_issues.py` — 이슈 문서 생성 DAG

**파이프라인 진입점**

- `src/pipeline/__init__.py`
- `src/pipeline/collect_news.py` — `run_collect_news()` 함수
- `src/pipeline/prepare_articles.py` — `run_prepare_articles()` 함수
- `src/pipeline/embed_articles.py` — `run_embed_articles()` 함수
- `src/pipeline/analyze_issues.py` — `run_analyze_issues()` 함수
- `src/pipeline/tracing.py` — 파이프라인 단계별 trace 설정

**데이터 수집 · 원문 처리**

- `src/integrations/news_search.py` — `NewsSearchClient` 클래스
- `src/integrations/article_scraper.py` — `ArticleScraper` 클래스
- `src/integrations/raw_store.py` — `RawNewsStore` 클래스

**공용 설정**

- `src/shared/__init__.py`
- `src/shared/settings.py` — `AppSettings`, `get_settings()`
- `src/shared/langsmith.py` — LangSmith 환경 설정 유틸리티

#### 구현 대상

**Docker · Compose 안정화**

`docker-compose.yml`과 `docker-compose.server.yml`이 모든 서비스를 정상적으로 기동할 수 있는지 검증한다. PostgreSQL에 pgvector 확장이 활성화되어 있는지, MongoDB가 외부에서 접근 가능한지, Airflow 웹 서버와 스케줄러가 정상 동작하는지 확인한다. 개발 환경과 서버 환경 모두에서 `setup-dev.sh`와 `setup-server.sh`가 실패 없이 실행되어야 한다.

**Airflow DAG 설계**

현재 4개 DAG는 `schedule=None`으로 등록되어 있다. 각 DAG의 실행 순서, 의존 관계, 재시도 정책, 실행 주기를 확정한다. DAG 파일 자체는 가볍게 유지하고, 실제 비즈니스 로직은 `src/pipeline` 진입점에서 호출하는 구조를 유지한다. 실제 주기 실행 정책은 데이터 적재가 안정화된 이후에 반영한다.

**`NewsSearchClient.search()` 구현**

`src/integrations/news_search.py`의 `NewsSearchClient` 클래스에 뉴스 검색 API 호출 로직을 구현한다. Naver News API를 기본 provider로 사용하고, 실패 시 Brave Search API 또는 Tavily를 fallback으로 호출하는 규칙을 정의한다. `search(query, *, limit=10)` 메서드는 기사 제목, URL, 발행일, 출처 정보를 포함하는 `list[dict]`를 반환해야 한다. API 키는 `src/shared/settings.py`의 `AppSettings`에 추가하고 `.env`에 항목을 정의한다.

**`ArticleScraper.fetch_article()` 구현**

`src/integrations/article_scraper.py`의 `ArticleScraper` 클래스에 기사 URL 기반 본문 스크래핑 로직을 구현한다. `fetch_article(url)` 메서드는 제목, 본문, 발행 시각, 매체명을 포함하는 `dict`를 반환한다. BeautifulSoup 또는 동등한 HTML 파싱 도구를 사용하며, 광고, 태그, 불필요한 문구 제거 등 정제 규칙을 포함한다. Tavily Extract API를 보조 수단으로 활용할 수 있다.

**`RawNewsStore.save_search_response()` 구현**

`src/integrations/raw_store.py`의 `RawNewsStore` 클래스에 MongoDB 원본 저장 로직을 구현한다. `save_search_response(provider, query, payload)` 메서드는 API 원본 응답을 그대로 저장하고, provider, 수집 시각, fallback 사용 여부, 상태 필드를 함께 기록한다. 반환값은 MongoDB document ID 문자열이다.

**PostgreSQL 스키마 설계 및 초기화**

저장 계층 담당자와 협의하여 PostgreSQL 테이블 구조를 확정하고, `docker/postgres/init/` 경로에 초기화 SQL을 작성한다. 목표 테이블은 `articles`, `article_chunks`, `article_embeddings`, `issues`, `issue_articles`, `issue_documents`, `document_sections`, `document_source_refs`이다. 스키마 설계의 최종 결정은 저장 계층 담당자가 하되, SQL 파일의 물리적 배치와 DB 초기화 실행은 이 역할이 담당한다.

**파이프라인 진입점 구현**

`src/pipeline/collect_news.py`의 `run_collect_news()` 함수에서 `NewsSearchClient`와 `RawNewsStore`를 호출하는 실제 수집 흐름을 구현한다. `src/pipeline/prepare_articles.py`의 `run_prepare_articles()` 함수에서 `ArticleScraper`를 호출하고, 정제 결과를 저장 계층 담당자의 `ArticleRepository.save_article()`에 전달하는 흐름을 구현한다. `run_embed_articles()`와 `run_analyze_issues()`는 각각 임베딩 담당자와 LLM 담당자의 함수를 호출하는 오케스트레이션 코드를 작성한다. 각 진입점은 `runtime`과 `user` 파라미터를 받아 LangSmith trace에 전달한다.

**초기 데이터 적재**

Airflow 또는 수동 스크립트를 통해 실제 뉴스 기사를 수집하고, MongoDB와 PostgreSQL에 적재한다. 다른 팀원이 병렬 개발을 시작할 때 DB에 최소한의 실데이터가 들어 있는 상태를 목표로 한다.

**공용 설정 관리**

`src/shared/settings.py`의 `AppSettings`에 새로운 환경 변수가 필요할 경우 추가하고, `.env` 파일에 항목과 설명을 정의한다. 다른 담당자가 새로운 환경 변수를 요청하면 이 역할이 `AppSettings`에 반영한다.

#### 산출물

- 개발 환경과 서버 환경이 모두 기동 가능한 Compose 구성
- Airflow에 등록되어 수동 실행 가능한 DAG 4개
- 뉴스 수집 클라이언트, 기사 스크래핑, MongoDB 저장 코드
- PostgreSQL 초기화 SQL
- DB에 적재된 실데이터 (최소 1개 주제, 기사 10건 이상)
- 파이프라인 단계별 실행 진입점
- 공용 `.env` 항목 정의

#### 완료 기준

- `setup-dev.sh`와 `setup-server.sh`가 실패 없이 동작한다.
- Airflow UI에서 4개 DAG가 등록되고, 수동 트리거로 실행된다.
- 특정 키워드 기준으로 뉴스 기사를 수집하고 MongoDB에 저장할 수 있다.
- 수집된 기사를 스크래핑하고 정제하여 PostgreSQL `articles` 테이블에 적재할 수 있다.
- 다른 담당자가 PostgreSQL에 접속하면 실데이터를 확인할 수 있다.
- 각 파이프라인 진입점이 다른 담당자의 함수를 호출할 수 있는 구조가 준비되어 있다.
- LangSmith에서 수집 및 전처리 단계의 trace가 확인된다.

---

### 4-2. 저장 계층 담당

이 역할의 책임은 "정제된 기사와 이슈 문서가 일관된 구조로 저장되고 다시 읽힐 수 있게 만드는 것"이다. PostgreSQL의 관계형 테이블을 설계하고, 기사 저장, 기사 청크 저장, 이슈별 기사 조회, 이슈 문서 저장과 조회를 담당한다. 이 역할이 제공하는 Repository 함수는 파이프라인, LLM · RAG, UI 세 계층 모두가 의존하므로, 함수 시그니처의 안정성이 매우 중요하다.

#### 소유 파일

- `src/integrations/article_repository.py` — `ArticleRepository` 클래스
- `src/integrations/issue_repository.py` — `IssueRepository` 클래스

#### 구현 대상

**PostgreSQL 스키마 설계**

인프라 담당자와 협의하여 다음 테이블의 컬럼, 타입, 제약 조건, 인덱스를 설계한다. 설계 결과는 SQL 파일로 작성하여 인프라 담당자에게 전달하고, 인프라 담당자가 `docker/postgres/init/` 경로에 배치한다.

- `articles` — 정제된 기사 1건의 메타데이터와 본문을 저장한다. 최소 컬럼은 `article_id` (PK, serial), `title`, `content`, `publisher`, `url`, `published_at`, `created_at`이다.
- `article_chunks` — 기사 본문을 일정 길이로 분할한 청크를 저장한다. 최소 컬럼은 `chunk_id` (PK), `article_id` (FK → articles), `chunk_index`, `chunk_text`이다. 임베딩 담당자가 이 테이블의 청크를 읽어 벡터로 변환한다.
- `issues` — 이슈 단위의 메타데이터를 저장한다. 최소 컬럼은 `issue_id` (PK), `title`, `created_at`이다.
- `issue_articles` — 이슈와 기사의 다대다 관계를 저장한다. 최소 컬럼은 `issue_id` (FK), `article_id` (FK)이다.
- `issue_documents` — `IssueDocument`의 본문 섹션을 저장한다. 최소 컬럼은 `document_id` (PK), `issue_id` (FK → issues), `title`, `overview`, `background`, `key_facts` (JSON 배열), `generated_at`이다.
- `document_sections` — 문서 섹션을 별도로 저장해야 할 경우의 확장 테이블이다. 초기 구현에서는 `issue_documents` 테이블에 섹션을 직접 포함하는 방식으로 시작할 수 있다.
- `document_source_refs` — 이슈 문서와 근거 기사의 연결을 저장한다. 최소 컬럼은 `document_id` (FK → issue_documents), `article_id` (FK → articles)이다.

`article_embeddings` 테이블은 임베딩 · 벡터 검색 담당자가 설계한다. 이 역할은 관계형 테이블만 담당한다.

**`ArticleRepository` 구현**

`src/integrations/article_repository.py`의 `ArticleRepository` 클래스에 다음 메서드를 구현한다.

- `save_article(article: dict) -> int` — 정제된 기사 1건을 `articles` 테이블에 저장하고 `article_id`를 반환한다. 인프라 담당자의 `run_prepare_articles()`가 이 함수를 호출한다. 입력 dict의 키는 `title`, `content`, `publisher`, `url`, `published_at`을 포함하며, 인프라 담당자와 키 이름을 협의하여 확정한다.
- `save_article_chunks(article_id: int, chunks: list[dict]) -> None` — 기사 청크 목록을 `article_chunks` 테이블에 저장한다. 각 chunk dict는 `chunk_index`와 `chunk_text`를 포함한다. 청크 분할 로직 자체는 임베딩 담당자가 구현하고, 이 함수는 분할된 결과를 저장하는 역할만 한다.
- `list_articles_for_issue(issue_id: int) -> list[dict]` — 특정 이슈에 속하는 기사 목록을 `issue_articles` 조인을 통해 반환한다. LLM 담당자의 `analyze_issue()` 함수와 인프라 담당자의 `run_analyze_issues()` 진입점이 이 함수를 호출한다. 반환 dict는 `article_id`, `title`, `content`, `publisher`, `url`, `published_at`을 포함해야 한다.
- `get_article(article_id: int) -> dict | None` — 단일 기사를 조회한다. UI에서 근거 기사 상세를 보여줄 때 사용할 수 있다.
- `list_article_chunks(article_id: int) -> list[dict]` — 특정 기사의 청크 목록을 반환한다. 임베딩 담당자가 `embed_texts()`에 넘길 텍스트를 가져올 때 사용한다.

**`IssueRepository` 구현**

`src/integrations/issue_repository.py`의 `IssueRepository` 클래스에 다음 메서드를 구현한다.

- `save_issue_document(document: IssueDocument) -> int` — `IssueDocument` 객체를 `issue_documents`, `document_source_refs` 테이블에 저장하고 `issue_id`를 반환한다. 이 함수는 `IssueDocument` 모델의 모든 필드를 빠짐없이 저장해야 한다. `source_articles`는 `document_source_refs` 테이블에, `related_issues`는 별도 컬럼 또는 JSON으로 저장한다. LLM 담당자의 `analyze_issue()` 결과물과 인프라 담당자의 `run_analyze_issues()` 진입점이 이 함수를 호출한다.
- `get_issue_document(issue_id: int) -> IssueDocument | None` — 단일 이슈 문서를 조회하여 `IssueDocument` 객체로 반환한다. `source_articles`와 `related_issues`를 포함한 완전한 객체를 반환해야 한다. UI의 상세 문서 페이지가 이 함수를 호출한다.
- `list_issue_documents(*, limit: int = 20) -> list[IssueDocument]` — 메인 화면 카드 섹션에 사용할 이슈 문서 목록을 조회한다. 최신순 정렬을 기본으로 하며, UI 담당자가 이 함수를 호출한다.
- `save_issue(issue_id: int, title: str) -> int` — `issues` 테이블에 이슈 메타데이터를 저장한다. 임베딩 담당자의 클러스터링 결과를 저장할 때 사용한다.
- `save_issue_articles(issue_id: int, article_ids: list[int]) -> None` — 이슈와 기사의 매핑을 `issue_articles` 테이블에 저장한다.

**DB 접속 관리**

PostgreSQL 연결은 `src/shared/settings.py`의 `AppSettings`에 정의된 환경 변수를 사용한다. 연결 풀링, 트랜잭션 관리, 에러 핸들링 방식을 결정한다. `psycopg2`, `asyncpg`, 또는 SQLAlchemy 중 적절한 드라이버를 선택한다.

#### 산출물

- PostgreSQL 테이블 정의 SQL (인프라 담당자에게 전달)
- `ArticleRepository` 구현 코드
- `IssueRepository` 구현 코드
- 각 메서드의 입출력 계약 정리 (다른 담당자가 호출할 함수의 파라미터와 반환 형태)

#### 완료 기준

- 인프라 담당자가 적재한 정제 기사 1건 이상을 `save_article()`로 저장하고 다시 조회할 수 있다.
- 이슈 단위로 기사 묶음을 `list_articles_for_issue()`로 읽어 올 수 있다.
- `IssueDocument` 객체를 `save_issue_document()`로 저장하고, `get_issue_document()`로 동일한 구조의 객체를 다시 읽어 올 수 있다.
- `list_issue_documents()`가 메인 화면 카드에 사용할 문서 목록을 반환한다.
- LLM 담당자와 UI 담당자가 호출할 함수의 시그니처가 안정적이고, 호출 예시가 정리되어 있다.

---

### 4-3. 임베딩 · 클러스터링 · 벡터 검색 담당

이 역할의 책임은 "정제된 기사 텍스트를 벡터로 변환하고, 유사 기사를 이슈 단위로 묶고, 질문에 대한 유사 청크를 검색할 수 있게 만드는 것"이다. 관계형 저장과는 다른 기술 영역을 다루며, 임베딩 모델 선택, 청크 분할 전략, pgvector 인덱스 설정, 이슈 클러스터링 알고리즘, 유사도 검색 최적화를 포함한다. 이 역할이 제공하는 `search_article_chunks()` 함수는 LLM · RAG 담당자의 Retriever가 직접 호출하는 핵심 인터페이스이다.

#### 소유 파일

- `src/integrations/embedding_client.py` — `EmbeddingClient` 클래스
- `src/integrations/vector_repository.py` — `VectorRepository` 클래스

필요에 따라 다음 파일을 신규 생성할 수 있다.

- `src/integrations/chunker.py` — 기사 본문 청크 분할 로직 (별도 파일로 분리할 경우)
- `src/integrations/clustering.py` — 이슈 클러스터링 로직 (별도 파일로 분리할 경우)

#### 구현 대상

**기사 청크 분할 전략 설계**

기사 본문을 임베딩하기 전에 적절한 길이로 분할하는 전략을 설계한다. 청크 크기, 오버랩 길이, 분할 기준(문단, 문장, 토큰 수)을 결정한다. LangChain의 `RecursiveCharacterTextSplitter` 또는 유사한 도구를 활용할 수 있다. 분할된 청크는 저장 계층 담당자의 `ArticleRepository.save_article_chunks()`를 호출하여 `article_chunks` 테이블에 저장한다. 청크 분할 함수는 `list[dict]` 형태로 `chunk_index`와 `chunk_text`를 반환해야 한다.

**`EmbeddingClient.embed_texts()` 구현**

`src/integrations/embedding_client.py`의 `EmbeddingClient` 클래스에 임베딩 생성 로직을 구현한다. `embed_texts(texts: Sequence[str]) -> list[list[float]]` 메서드는 문자열 목록을 받아 동일한 길이의 벡터 목록을 반환한다. 기본 모델은 `src/shared/settings.py`의 `openai_embedding_model` 설정값(`text-embedding-3-small`)을 사용한다. 대량 텍스트 처리를 위한 배치 호출, 속도 제한 대응, 재시도 로직을 포함한다. OpenAI Embeddings API를 직접 호출하거나 LangChain의 `OpenAIEmbeddings`를 사용할 수 있다.

**`article_embeddings` 테이블 설계**

pgvector 확장을 사용하는 `article_embeddings` 테이블의 스키마를 설계한다. 최소 컬럼은 `embedding_id` (PK), `chunk_id` (FK → article_chunks), `article_id` (FK → articles), `embedding` (vector 타입)이다. 벡터 차원은 임베딩 모델에 맞춰 설정한다 (`text-embedding-3-small`은 1536 차원). pgvector의 인덱스 타입(IVFFlat, HNSW)과 파라미터를 결정한다. 설계 결과는 SQL로 작성하여 저장 계층 담당자 및 인프라 담당자와 공유한다.

**`VectorRepository.upsert_article_embeddings()` 구현**

`src/integrations/vector_repository.py`의 `VectorRepository` 클래스에 벡터 저장 로직을 구현한다. `upsert_article_embeddings(rows: list[dict]) -> None` 메서드는 청크 ID, 기사 ID, 임베딩 벡터를 포함하는 dict 목록을 받아 `article_embeddings` 테이블에 저장하거나 갱신한다. 각 row dict는 `chunk_id`, `article_id`, `embedding` 키를 포함한다.

**`VectorRepository.search_article_chunks()` 구현**

`search_article_chunks(query_embedding: Sequence[float], *, limit: int = 5) -> list[dict]` 메서드는 질문 임베딩 벡터를 받아 유사도 기준 상위 N개 기사 청크를 반환한다. 반환 dict는 `chunk_id`, `article_id`, `chunk_text`, `similarity_score`를 포함해야 한다. pgvector의 `<=>` (코사인 거리) 또는 `<->` (L2 거리) 연산자를 사용한다. LLM · RAG 담당자의 Retriever가 이 함수를 직접 호출하므로, 반환 형태를 LLM 담당자와 협의하여 확정한다.

**이슈 클러스터링 구현**

임베딩된 기사 청크 또는 기사 단위 벡터를 기반으로 유사 기사를 하나의 이슈로 묶는 클러스터링 로직을 구현한다. K-Means, DBSCAN, 또는 유사도 기반 계층적 클러스터링 중 적절한 알고리즘을 선택한다. 클러스터링 결과는 이슈 ID와 기사 ID의 매핑으로 출력하며, 저장 계층 담당자의 `IssueRepository.save_issue()`와 `save_issue_articles()`를 호출하여 `issues`, `issue_articles` 테이블에 저장한다. 클러스터 수 또는 유사도 임계값은 실데이터 기반으로 조정한다.

**파이프라인 연동**

인프라 담당자의 `src/pipeline/embed_articles.py`에서 호출할 함수의 입출력 계약을 확정한다. `run_embed_articles()` 진입점은 이 역할의 `EmbeddingClient`, `VectorRepository`, 청크 분할 함수, 클러스터링 함수를 순서대로 호출한다. 인프라 담당자가 오케스트레이션 코드를 작성할 수 있도록 함수 시그니처와 호출 순서를 먼저 정리하여 공유한다.

#### 산출물

- 기사 청크 분할 로직
- `EmbeddingClient` 구현 코드
- `VectorRepository` 구현 코드
- `article_embeddings` 테이블 설계 SQL
- 이슈 클러스터링 로직
- 임베딩 모델, 청크 크기, 클러스터링 파라미터 결정 근거

#### 완료 기준

- 기사 본문 1건 이상을 청크로 분할하고 임베딩 벡터를 생성할 수 있다.
- 생성된 벡터가 `article_embeddings` 테이블에 저장된다.
- 임의의 질문 벡터로 `search_article_chunks()`를 호출하면 유사 청크가 반환된다.
- 클러스터링을 통해 유사 기사가 하나의 이슈로 묶이고, `issues`와 `issue_articles` 테이블에 저장된다.
- LLM · RAG 담당자가 `search_article_chunks()`를 호출할 수 있는 인터페이스가 안정적이다.
- 인프라 담당자가 `run_embed_articles()` 진입점에서 호출할 함수 목록과 순서가 정리되어 있다.

---

### 4-4. LLM · RAG 담당

이 역할은 "기사가 이슈 문서로 바뀌는 품질"과 "검색 결과가 답변으로 바뀌는 품질"을 함께 책임진다. 프롬프트 작성 자체보다 중요한 일은 출력이 `PLAN.md`의 서술 원칙과 `IssueDocument` 데이터 계약을 만족하는지 검증하고 반복 개선하는 것이다. 이 역할은 문서 생성 체인과 RAG 질의응답 체인 두 축을 모두 다룬다.

#### 소유 파일

- `src/core/prompts/__init__.py`
- `src/core/prompts/overview.py` — `OVERVIEW_PROMPT`
- `src/core/prompts/background.py` — `BACKGROUND_PROMPT`
- `src/core/prompts/key_facts.py` — `KEY_FACTS_PROMPT`
- `src/core/chains.py` — `analyze_issue()`, `build_issue_overview()`, `build_issue_background()`, `build_issue_key_facts()` 및 내부 헬퍼 함수
- `src/core/rag.py` — `answer_question()`
- `src/core/tracing.py` — `build_analysis_trace_config()`

`src/core/models.py`는 읽기 전용이다. `IssueDocument`, `SourceRef`, `RelatedIssue`의 필드를 변경하려면 전원 합의가 필요하다.

#### 구현 대상

**프롬프트 개선**

현재 `src/core/prompts/` 디렉토리에는 개요, 배경, 핵심 사실 생성을 위한 초기 프롬프트가 존재한다. 인프라 담당자가 적재한 실데이터 기사를 입력으로 사용하여 프롬프트를 반복 개선한다.

`OVERVIEW_PROMPT`는 3~5문장 사실 중심 개요를 생성해야 한다. 기사에 명시된 수치, 기관, 인물을 포함하되 추측이나 의견은 배제한다. 생성 결과가 일관되게 이 기준을 충족하는지 LangSmith trace로 확인한다.

`BACKGROUND_PROMPT`는 기사 본문에 명시된 배경 정보를 우선 사용하고, LLM의 일반 지식을 보강할 때는 반드시 `[일반 배경 정보]`를 표기해야 한다. 이 표기가 누락되거나 과도하게 사용되는 경우를 찾아 프롬프트를 조정한다.

`KEY_FACTS_PROMPT`는 2개 이상의 기사가 공통으로 다루는 사실만 추출해야 한다. 단일 기사에만 있는 사실이 포함되거나, 해석이나 관점이 섞이는 경우를 걸러내도록 프롬프트를 보강한다.

필요하다면 새로운 프롬프트 파일을 `src/core/prompts/` 디렉토리에 추가할 수 있다. 예를 들어 RAG 질의응답을 위한 프롬프트가 필요하면 `src/core/prompts/answer.py`를 생성한다.

**`chains.py` 개선**

현재 `src/core/chains.py`에는 `analyze_issue()` 함수와 3개의 섹션 생성 함수가 프로토타입으로 구현되어 있다. 실데이터 기사를 입력으로 사용하여 출력 품질을 검증하고 개선한다.

`_format_articles()` 함수의 기사 포맷 방식이 프롬프트 성능에 적합한지 검토한다. `_extract_key_facts()` 함수의 파싱 로직이 다양한 LLM 출력 형태를 안정적으로 처리하는지 확인한다. `_build_source_refs()`와 `_build_related_issues()` 함수는 결정적 조합이므로 현재 구조를 유지하되, 입력 dict의 키 규칙을 저장 계층 담당자와 맞춘다.

`analyze_issue()` 함수가 `IssueDocument` 계약에 맞는 완전한 출력을 안정적으로 반환하는지 반복 검증한다. 개요, 배경, 핵심 사실이 서로 역할이 겹치지 않아야 하며, 동일한 입력에 대해 구조적으로 일관된 결과가 나와야 한다.

**`rag.py` 구현**

`src/core/rag.py`의 `answer_question()` 함수를 구현한다. 현재는 `NotImplementedError`를 발생시키는 스켈레톤 상태이다.

```python
def answer_question(
    question: str,
    *,
    context_articles: list[dict],
    context_documents: list[IssueDocument],
    runtime: str = "dev",
    user: str | None = None,
) -> dict[str, Any]:
```

이 함수의 구현 흐름은 다음과 같다.

1. 임베딩 담당자의 `EmbeddingClient.embed_texts()`를 호출하여 질문을 벡터로 변환한다.
2. 임베딩 담당자의 `VectorRepository.search_article_chunks()`를 호출하여 유사 기사 청크를 검색한다.
3. 검색된 청크와 이슈 문서를 컨텍스트로 조합한다.
4. LLM에 컨텍스트와 질문을 전달하여 답변을 생성한다.
5. 답변, 근거 기사, 관련 문서를 포함하는 dict를 반환한다.

반환 구조는 최소한 `answer` (문자열), `source_articles` (근거 기사 메타데이터 목록), `related_documents` (관련 이슈 문서 목록)를 포함해야 한다. 이 반환 구조는 UI 담당자가 검색 결과를 렌더링할 때 사용하므로, UI 담당자와 협의하여 확정한다.

검색 결과가 부족할 때 답변을 과도하게 확장하지 않는 기준을 정의한다. 근거가 불충분한 경우 "관련 자료가 충분하지 않습니다"와 같은 응답을 반환하거나, 부분적인 답변과 함께 근거 부족 상태를 명시한다.

**Retriever 설계**

LangChain의 Retriever 인터페이스를 활용하여 벡터 검색 결과를 체인에 연결하는 방식을 설계한다. 임베딩 담당자의 `VectorRepository`를 LangChain `BaseRetriever`로 래핑하거나, 커스텀 Retriever를 구현한다. 검색 대상은 기사 청크 검색을 중심으로 하되, 이슈 문서 검색을 보조 수단으로 추가할 수 있다.

**LangSmith 기반 평가**

LangSmith를 이용하여 프롬프트 실험과 결과 비교를 수행한다. `src/core/tracing.py`의 `build_analysis_trace_config()`를 활용하여 문서 생성 단계의 trace를 기록한다. 샘플 기사 묶음 기준으로 생성 결과의 품질을 비교하고, 개선 이력을 유지한다.

평가 기준은 다음과 같다.

- 개요가 3~5문장을 유지하는가
- 배경에서 `[일반 배경 정보]` 표기가 정확한가
- 핵심 사실이 복수 기사 공통 사실만 포함하는가
- 동일 입력에 대해 구조적으로 일관된 결과가 나오는가
- RAG 답변이 검색 결과 범위를 벗어나지 않는가

#### 산출물

- 개선된 프롬프트 파일 3종
- 실데이터 기반 `analyze_issue()` 동작 검증 결과
- `answer_question()` 구현 코드
- Retriever 연동 방식 설계
- LangSmith trace 기반 품질 평가 기록
- RAG 답변 반환 구조 정의

#### 완료 기준

- 실데이터 기사 묶음을 입력하면 `IssueDocument` 계약에 맞는 문서가 생성된다.
- 개요, 배경, 핵심 사실이 서로 역할이 겹치지 않는다.
- 기사에 없는 일반 지식은 배경 섹션에서만 `[일반 배경 정보]`로 구분된다.
- `answer_question()`이 질문에 대해 근거 기사와 함께 답변을 반환한다.
- 검색 결과가 부족할 때 과도한 답변 확장을 하지 않는 기준이 동작한다.
- LangSmith에서 문서 생성과 RAG 응답의 trace가 확인된다.
- UI 담당자가 `answer_question()` 반환값을 바로 렌더링할 수 있다.

---

### 4-5. UI · 문서 소비 계층 담당

이 역할은 "사용자가 실제로 이 프로젝트를 경험하는 표면"을 완성한다. 화면만 그리는 수준에 머물지 않고, 상단 검색 경험, 이슈 카드 탐색 경험, 문서 상세 읽기 경험, 네비게이션 트리 기반 탐색 경험을 안정적으로 제공해야 한다. 현재 UI는 하드코딩된 데모 데이터로 동작하며, 이를 실데이터 조회 구조로 전환하는 일이 핵심 과제다.

#### 소유 파일

- `app/main.py` — 메인 페이지 (검색 영역 + 카드 리스트)
- `app/components/issue_card.py` — `render_issue_card()` 함수
- `app/components/section_renderer.py` — `render_issue_sections()` 함수
- `app/pages/issue_detail.py` — `render_issue_detail()` 함수

필요에 따라 다음 파일을 신규 생성할 수 있다.

- `app/components/search_result.py` — 검색 결과 렌더링 컴포넌트
- `app/components/navigation_tree.py` — 네비게이션 트리 컴포넌트
- `app/pages/` 하위 추가 페이지

#### 구현 대상

**검색 영역 구현**

`app/main.py`의 최상단에 검색엔진 스타일의 검색창을 구현한다. 현재 `main.py`에는 검색 영역이 없고, 이슈 카드와 상세 문서만 표시한다. 사용자가 자연어 질문을 입력하면 LLM · RAG 담당자의 `answer_question()` 함수를 호출하고, 결과를 아래에 표시한다. `answer_question()`이 아직 구현되지 않은 동안에는 임시 응답을 보여주는 스텁을 사용한다.

검색 결과 영역에는 다음 요소를 포함한다.

- 사용자가 입력한 질문
- RAG 기반 답변 텍스트
- 근거 기사 목록 (제목, 매체명, 발행일, 원문 URL 링크)
- 관련 이슈 문서 링크 (클릭 시 상세 문서 페이지로 이동)

검색 결과 렌더링이 복잡해지면 `app/components/search_result.py`를 신규 생성하여 분리한다.

**이슈 카드 리스트 개선**

현재 `app/main.py`의 `_load_demo_issues()` 함수에서 하드코딩된 데모 데이터를 로드한다. 이를 저장 계층 담당자의 `IssueRepository.list_issue_documents()`를 호출하는 구조로 전환한다. 저장 계층이 아직 준비되지 않은 동안에는 기존 데모 데이터를 fallback으로 유지하되, 전환 경로를 미리 설계해 둔다.

`app/components/issue_card.py`의 `render_issue_card()` 함수를 개선한다. 현재는 제목, 갱신 시각, 근거 기사 수, 개요를 표시한다. 카드에 이슈 카테고리, 핵심 사실 일부 미리보기 등을 추가할 수 있다. 카드 클릭 시 해당 이슈의 상세 문서 페이지로 이동하는 동작을 구현한다. Streamlit의 `st.session_state`를 활용하여 선택된 이슈를 관리한다.

**문서 상세 페이지 개선**

`app/pages/issue_detail.py`의 `render_issue_detail()` 함수는 현재 제목, 갱신 시각, 섹션 렌더러를 호출한다. 저장 계층 담당자의 `IssueRepository.get_issue_document()`를 호출하여 실데이터를 조회하는 구조로 전환한다.

`app/components/section_renderer.py`의 `render_issue_sections()` 함수를 개선한다. 현재 목차, 개요, 배경, 핵심 사실, 근거 기사, 관련 이슈를 순서대로 렌더링한다. 개선 방향은 다음과 같다.

- 목차 클릭 시 해당 섹션으로 스크롤 이동이 동작하는지 확인한다.
- 배경 섹션에서 `[일반 배경 정보]` 텍스트를 시각적으로 구분한다 (배경색, 아이콘 등).
- 핵심 사실이 비어 있을 때의 안내 문구를 개선한다.
- 근거 기사의 원문 URL이 클릭 가능한 링크로 표시되는지 확인한다.
- 관련 이슈 클릭 시 해당 이슈의 상세 페이지로 이동하는 동작을 구현한다.

**네비게이션 트리 구현**

`PLAN.md`에 정의된 세 가지 네비게이션 요소를 반영한다.

- 문서 내부 목차: 현재 `section_renderer.py`에 마크다운 형태로 존재한다. 실제 스크롤 이동이 동작하도록 개선한다.
- 관련 이슈 트리: 현재 이슈와 연결된 다른 이슈를 목록 또는 트리 형태로 보여준다. `IssueDocument.related_issues`를 기반으로 렌더링한다.
- 주제 탐색 트리: 상위 주제에서 하위 이슈로 확장 탐색할 수 있는 구조를 설계한다. 베타에서는 관련 이슈 연결을 기반으로 단순화된 형태로 구현할 수 있다.

네비게이션 트리가 복잡해지면 `app/components/navigation_tree.py`를 신규 생성하여 분리한다.

**데이터 전환 준비**

데모 데이터에서 실데이터로 전환할 때 UI 계약이 흔들리지 않도록 준비한다. UI는 항상 `IssueDocument` 모델을 입력으로 받으며, 데이터 소스가 하드코딩이든 DB 조회든 동일한 렌더링 경로를 거쳐야 한다. 전환 시점에 수정이 필요한 부분은 `main.py`의 데이터 로딩 함수뿐이어야 한다.

**엣지 케이스 처리**

- 이슈 문서가 0건일 때 빈 카드 섹션 안내
- 검색 결과가 0건일 때 안내 메시지
- 개요, 배경, 핵심 사실 중 일부가 비어 있을 때 렌더링 처리
- 본문이 매우 길 때 스크롤 또는 접기/펼치기 처리
- 근거 기사의 `published_at`이 None일 때 "발행일 미상" 표시 (현재 구현되어 있음, 유지)
- 관련 이슈가 0건일 때 안내 문구 (현재 구현되어 있음, 유지)

#### 산출물

- 검색창과 RAG 답변 표시 영역
- 개선된 이슈 카드 리스트
- 개선된 문서 상세 페이지
- 네비게이션 트리 또는 동등한 탐색 구조
- 실데이터 연결을 위한 데이터 로딩 인터페이스

#### 완료 기준

- 검색창에 질문을 입력하면 답변 영역이 표시된다 (RAG 연동 전에는 스텁 응답).
- 카드 섹션에서 이슈 목록이 표시되고, 카드 클릭 시 상세 페이지로 이동한다.
- 문서 상세 페이지에서 목차, 개요, 배경, 핵심 사실, 근거 기사, 관련 이슈가 모두 렌더링된다.
- `[일반 배경 정보]` 표기가 시각적으로 구분된다.
- 관련 이슈 클릭 시 해당 이슈 페이지로 이동한다.
- 네비게이션 트리 또는 동등한 탐색 구조가 반영되어 있다.
- 빈 데이터, 부분 데이터에 대한 렌더링이 깨지지 않는다.
- `_load_demo_issues()`를 `IssueRepository.list_issue_documents()` 호출로 교체하면 화면이 실데이터로 전환된다.
- 데모 상태에서도 제품 방향을 충분히 설명할 수 있는 UI가 완성되어 있다.

## 5. 역할 간 인터페이스

병렬 개발에서는 "누가 누구에게 무엇을 넘기는가"가 분명해야 한다. 역할 간 핵심 인터페이스는 다음과 같다.

| 제공 역할 | 받는 역할 | 넘기는 것 |
|-----------|-----------|-----------|
| 인프라 · 데이터 파이프라인 | 전원 | 실행 환경, DAG 경계, 공용 설정, DB에 적재된 실데이터 |
| 인프라 · 데이터 파이프라인 | 저장 계층 | 정제 기사 dict (`save_article()` 입력) |
| 저장 계층 | 임베딩 · 벡터 검색 | `list_article_chunks()` 반환값 (청크 텍스트) |
| 저장 계층 | LLM · RAG | `list_articles_for_issue()` 반환값 (이슈별 기사 묶음) |
| 저장 계층 | UI | `list_issue_documents()`, `get_issue_document()` 반환값 |
| 임베딩 · 벡터 검색 | 저장 계층 | 클러스터링 결과 (`save_issue()`, `save_issue_articles()` 입력) |
| 임베딩 · 벡터 검색 | LLM · RAG | `search_article_chunks()` 반환값, `embed_texts()` |
| LLM · RAG | 저장 계층 | `IssueDocument` 출력 (`save_issue_document()` 입력) |
| LLM · RAG | UI | `answer_question()` 반환값 |
| UI | 전원 | 화면 요구사항, 조회 계약 피드백 |

모든 역할은 결국 `IssueDocument`, "이슈별 기사 묶음 조회", "기사 청크 벡터 검색", "RAG 질의응답 반환"이라는 네 인터페이스를 중심으로 연결된다. 따라서 이 네 계약이 흔들리면 통합 비용이 커지고, 반대로 안정적이면 구현 속도를 크게 높일 수 있다.

## 6. 파일 소유권 전체 매핑

아래 표는 저장소 내 모든 구현 파일의 소유권을 정리했다. 각 파일은 한 명의 담당자만 소유한다.

| 파일 경로 | 소유 역할 |
|-----------|-----------|
| `docker-compose.yml` | 인프라 · 데이터 파이프라인 |
| `docker-compose.server.yml` | 인프라 · 데이터 파이프라인 |
| `docker/airflow/Dockerfile` | 인프라 · 데이터 파이프라인 |
| `docker/dev/Dockerfile` | 인프라 · 데이터 파이프라인 |
| `docker/mongo/Dockerfile` | 인프라 · 데이터 파이프라인 |
| `docker/postgres/Dockerfile` | 인프라 · 데이터 파이프라인 |
| `docker/postgres/init/01-create-news-db.sh` | 인프라 · 데이터 파이프라인 |
| `scripts/setup-dev.sh` | 인프라 · 데이터 파이프라인 |
| `scripts/setup-server.sh` | 인프라 · 데이터 파이프라인 |
| `dags/collect_news.py` | 인프라 · 데이터 파이프라인 |
| `dags/prepare_articles.py` | 인프라 · 데이터 파이프라인 |
| `dags/embed_articles.py` | 인프라 · 데이터 파이프라인 |
| `dags/analyze_issues.py` | 인프라 · 데이터 파이프라인 |
| `src/pipeline/__init__.py` | 인프라 · 데이터 파이프라인 |
| `src/pipeline/collect_news.py` | 인프라 · 데이터 파이프라인 |
| `src/pipeline/prepare_articles.py` | 인프라 · 데이터 파이프라인 |
| `src/pipeline/embed_articles.py` | 인프라 · 데이터 파이프라인 |
| `src/pipeline/analyze_issues.py` | 인프라 · 데이터 파이프라인 |
| `src/pipeline/tracing.py` | 인프라 · 데이터 파이프라인 |
| `src/shared/__init__.py` | 인프라 · 데이터 파이프라인 |
| `src/shared/settings.py` | 인프라 · 데이터 파이프라인 |
| `src/shared/langsmith.py` | 인프라 · 데이터 파이프라인 |
| `src/integrations/news_search.py` | 인프라 · 데이터 파이프라인 |
| `src/integrations/article_scraper.py` | 인프라 · 데이터 파이프라인 |
| `src/integrations/raw_store.py` | 인프라 · 데이터 파이프라인 |
| `src/integrations/article_repository.py` | 저장 계층 |
| `src/integrations/issue_repository.py` | 저장 계층 |
| `src/integrations/embedding_client.py` | 임베딩 · 클러스터링 · 벡터 검색 |
| `src/integrations/vector_repository.py` | 임베딩 · 클러스터링 · 벡터 검색 |
| `src/core/__init__.py` | 공용 (변경 시 전원 합의) |
| `src/core/models.py` | 공용 (변경 시 전원 합의) |
| `src/core/prompts/__init__.py` | LLM · RAG |
| `src/core/prompts/overview.py` | LLM · RAG |
| `src/core/prompts/background.py` | LLM · RAG |
| `src/core/prompts/key_facts.py` | LLM · RAG |
| `src/core/chains.py` | LLM · RAG |
| `src/core/rag.py` | LLM · RAG |
| `src/core/tracing.py` | LLM · RAG |
| `app/main.py` | UI · 문서 소비 계층 |
| `app/components/issue_card.py` | UI · 문서 소비 계층 |
| `app/components/section_renderer.py` | UI · 문서 소비 계층 |
| `app/pages/issue_detail.py` | UI · 문서 소비 계층 |

`src/integrations/__init__.py`는 빈 파일이며 별도 소유권을 두지 않는다.

## 7. 구현 순서와 병렬 가능 영역

### 먼저 고정해야 하는 것

- 환경 변수 이름과 `.env` 항목
- PostgreSQL 핵심 테이블 이름과 컬럼
- `IssueDocument` 계약
- 검색 입력과 검색 결과 반환 구조
- DAG 이름과 단계 이름
- Repository 함수 시그니처

### 인프라 담당자가 선행 완료해야 하는 것

- Docker 환경 기동 검증
- 뉴스 수집 클라이언트 구현
- 기사 스크래핑 및 정제
- MongoDB 원본 적재
- PostgreSQL 스키마 초기화
- `articles` 테이블에 정제 기사 적재
- Airflow DAG 등록 및 수동 실행 검증

### 병렬로 진행 가능한 것

인프라 담당자의 선행 작업이 진행되는 동안에도 다음 작업은 병렬로 시작할 수 있다.

- 저장 계층 담당자는 테이블 스키마 설계와 Repository 코드 작성을 먼저 시작할 수 있다. DB에 실데이터가 들어오면 바로 검증한다.
- 임베딩 담당자는 임베딩 모델 선택, 청크 전략 설계, 클러스터링 알고리즘 조사를 먼저 진행할 수 있다. 샘플 텍스트로 임베딩 생성을 테스트한다.
- LLM 담당자는 프롬프트 설계와 체인 개선을 샘플 기사 묶음으로 먼저 진행할 수 있다. 실데이터가 들어오면 품질 검증을 시작한다.
- UI 담당자는 데모 데이터로 검색 영역, 카드 개선, 상세 문서 개선, 네비게이션 트리를 먼저 구현한다. Repository가 준비되면 실데이터 전환을 수행한다.

### 통합 시 반드시 맞춰야 하는 것

- 인프라 → 저장: `save_article()` 입력 dict 키
- 저장 → 임베딩: `list_article_chunks()` 반환 dict 키
- 임베딩 → 저장: 클러스터링 결과 → `save_issue()`, `save_issue_articles()` 호출 규칙
- 임베딩 → LLM: `search_article_chunks()` 반환 dict 키, `embed_texts()` 호출 방식
- LLM → 저장: `analyze_issue()` 출력 → `save_issue_document()` 입력
- LLM → UI: `answer_question()` 반환 dict 키
- 저장 → UI: `list_issue_documents()`, `get_issue_document()` 반환 형태

## 8. 통합 단계 체크리스트

통합 전에 각 담당자는 최소한 다음 항목을 점검해야 한다.

- 자신의 산출물이 어느 파일과 계층에 들어가는지 문서화했는가
- 다른 담당자가 호출할 함수의 파라미터와 반환 형태가 정리되어 있는가
- 임시 코드, 하드코딩 값, 로컬 경로 의존성을 정리했는가
- 실패 시 로그나 에러 메시지로 원인을 추적할 수 있는가
- `PLAN.md`, `ARCHITECTURE.md`, `WORKFLOW.md`, `AGENTS.md`의 용어와 어긋나지 않는가

통합 순서는 다음과 같다.

1. 인프라 담당자가 DB에 데이터를 적재한다.
2. 저장 계층 담당자가 `ArticleRepository`와 `IssueRepository`를 연결한다.
3. 임베딩 담당자가 임베딩 생성과 클러스터링을 실행한다.
4. LLM 담당자가 실데이터 기반으로 문서를 생성하고 RAG 응답을 검증한다.
5. UI 담당자가 데모 데이터를 실데이터 조회로 전환한다.
6. 인프라 담당자가 Airflow에서 전체 파이프라인을 순차 실행하여 end-to-end 검증한다.
