# ArXplore 역할 분담

## 1. 문서 목적

이 문서는 ArXplore를 5인 팀이 병렬로 구현할 때 각자의 책임 범위, 소유 파일, 구현 대상, 협업 인터페이스, 산출물, 완료 기준을 구체적으로 정리한다. 현재 저장소는 초안 스캐폴드가 정리된 상태이며, 각 담당자는 자신이 소유하는 파일과 함수를 기준으로 독립적으로 구현하되 `TopicDocument` 계약과 운영 문서를 공통 인터페이스로 삼아 통합하는 방식으로 작업한다.

본 문서의 목적은 "누가 무슨 파일을 만지는가"만 적는 것이 아니다. 더 중요한 목적은 다음 세 가지다.

- 병렬 개발 중 충돌을 줄인다.
- 역할 간 의존 관계와 함수 계약을 미리 고정한다.
- 구현 전에 책임 경계를 분명히 해 통합 실패를 줄인다.

## 2. 기본 원칙

역할 분담은 편의상 파일을 나누는 작업이 아니라, 책임을 분리해 병렬 개발을 가능하게 하는 장치다. 각 담당자는 자신의 영역에서 설계 결정을 주도할 수 있어야 하지만, 다른 담당자가 의존하는 계약은 함부로 바꾸면 안 된다.

공통 원칙은 다음과 같다.

- 제품 방향과 구조 기준은 [PLAN.md](./PLAN.md)를 따른다.
- 시스템 아키텍처와 계층 경계는 [ARCHITECTURE.md](./ARCHITECTURE.md)를 따른다.
- 공용 데이터 계약은 `src/core/models.py`의 `TopicDocument`, `PaperRef`, `RelatedTopic`를 기준으로 한다.
- `TopicDocument` 계약은 전원 합의 없이 변경하지 않는다.
- DAG 정의는 가볍게 유지하고, 실제 비즈니스 로직은 `src/pipeline` 이하에 둔다.
- 외부 서비스 연동과 저장 코드는 `src/integrations`를 기본 위치로 삼는다.
- UI는 저장 계층이나 외부 API를 직접 두드리지 않고, 합의된 조회 경로를 사용한다.
- 결과물이 미완성이라도 입력, 출력, 에러 정책, 의존 함수는 먼저 문서화한다.
- 파일 소유권이 명시된 파일은 원칙적으로 해당 담당자가 수정한다.

## 3. 공통 용어

ArXplore에서는 다음 용어를 공통으로 사용한다.

- `paper`: 단일 논문 메타데이터
- `paper chunk`: RAG 검색을 위한 논문 텍스트 단위
- `topic`: 유사 논문 묶음
- `topic document`: 토픽을 설명하는 구조화 문서
- `RAG answer`: 검색 결과 범위 안에서 생성한 응답

다음 용어는 더 이상 사용하지 않는다.

- 기사
- 뉴스
- 이슈 문서
- source article
- related issue

## 4. 5인 팀 기준 역할 구성

| 역할 | 권장 인원 | 주 책임 |
|------|-----------|--------|
| **1. 인프라 · 데이터 파이프라인 담당** | 1명 | Docker, Compose, Airflow, 논문 수집, 원본 저장, arXiv 보강, 공용 설정 |
| **2. 저장 계층 담당** | 1명 | PostgreSQL 스키마, `papers`/`topics`/`topic_documents` CRUD, 조회 함수 |
| **3. 임베딩 · 클러스터링 · 벡터 검색 담당** | 1명 | 청크 전략, 임베딩 생성, pgvector 저장 및 검색, 토픽 그룹핑 |
| **4. LLM · RAG 담당** | 1명 | 프롬프트, 문서 생성 체인, RAG 응답 정책, LangSmith 평가 |
| **5. UI · 문서 소비 계층 담당** | 1명 | Streamlit 검색 화면, 카드, 상세 문서, 상태 처리 |

이 배치는 기능 흐름과 책임 경계에 맞춰 구성했다. 인프라 담당자가 수집 가능한 환경과 기초 데이터를 준비하면, 나머지 네 역할은 공용 계약을 기준으로 병렬 구현을 진행할 수 있다.

## 5. 역할 간 핵심 의존 관계

### 인프라 → 저장 계층

- 인프라 담당자는 실제 수집 흐름과 입력 데이터 형태를 정의한다.
- 저장 담당자는 그 입력을 받아 저장 가능한 최소 스키마와 Repository 시그니처를 확정한다.

### 저장 계층 → 임베딩 담당

- 저장 담당자는 `papers`, `paper_chunks` 조회 경로를 제공한다.
- 임베딩 담당자는 이 데이터를 읽어 임베딩과 검색 구조를 만든다.

### 저장 계층 + 임베딩 담당 → LLM 담당

- 저장 담당자는 토픽별 논문 로딩 함수를 제공한다.
- 임베딩 담당자는 질문 기준 검색 결과를 반환하는 함수를 제공한다.
- LLM 담당자는 이 두 경로를 사용해 문서 생성과 Q&A를 구현한다.

### 저장 계층 + LLM 담당 → UI 담당

- 저장 담당자는 카드/상세 문서 조회 함수를 제공한다.
- LLM 담당자는 질의응답 진입점과 응답 형태를 제공한다.
- UI 담당자는 이 두 결과를 화면 흐름으로 연결한다.

## 6. 공통 계약과 보호 대상

다음 요소는 모든 역할이 의존하는 보호 대상이다.

- `src/core/models.py`
- `src/core/__init__.py`
- `src/core/prompts/__init__.py`
- `src/shared/settings.py`

특히 `TopicDocument`는 다음 역할을 동시에 수행한다.

- 분석 체인의 최종 출력
- PostgreSQL `topic_documents` 저장 대상
- Streamlit 상세 문서 렌더링 입력
- RAG 응답에서 참조하는 문서 메타데이터 구조

이 계약을 바꿀 때는 적어도 다음을 함께 점검해야 한다.

- 프롬프트 출력
- 체인 파서
- DB 저장/조회
- UI 렌더링
- 문서 예시

## 7. 역할별 상세

### 7-1. 인프라 · 데이터 파이프라인 담당

이 역할은 "다른 팀원이 실데이터 기반으로 개발을 시작할 수 있는 환경과 데이터"를 준비한다. Docker 이미지, Compose 구성, Airflow 서비스, DAG 설계, HF Daily Papers 수집, arXiv 메타데이터 보강, MongoDB 원본 저장, 공용 환경 변수, 초기 데이터 적재를 포함한다.

#### 소유 파일

**Docker · Compose · 스크립트**

- `docker-compose.yml`
- `docker-compose.server.yml`
- `docker/airflow/Dockerfile`
- `docker/dev/Dockerfile`
- `docker/mongo/Dockerfile`
- `docker/postgres/Dockerfile`
- `docker/postgres/init/01-create-app-db.sh`
- `scripts/setup-dev.sh`
- `scripts/setup-server.sh`
- `scripts/port-forward.sh`

**Airflow DAG 정의**

- `dags/collect_papers.py`
- `dags/prepare_papers.py`
- `dags/embed_papers.py`
- `dags/analyze_topics.py`

**파이프라인 진입점**

- `src/pipeline/__init__.py`
- `src/pipeline/collect_papers.py`
- `src/pipeline/prepare_papers.py`
- `src/pipeline/embed_papers.py`
- `src/pipeline/analyze_topics.py`
- `src/pipeline/tracing.py`

**수집 및 원본 저장**

- `src/integrations/paper_search.py`
- `src/integrations/raw_store.py`

**공용 설정**

- `src/shared/__init__.py`
- `src/shared/settings.py`
- `src/shared/langsmith.py`

#### 구현 대상

**개발 환경과 서버 환경 안정화**

- dev 컨테이너와 server stack이 모두 정상 기동해야 한다.
- PostgreSQL + pgvector, MongoDB, Airflow 웹/스케줄러/프로세서가 정상 연결되어야 한다.
- `.env` 기준 설정명이 ArXplore 계약과 일치해야 한다.

**HF Daily Papers 수집**

- `PaperSearchClient.fetch_daily_papers(date)`를 구현한다.
- 날짜 기준 feed를 호출하고, 실제 응답이 `list` 형태임을 반영해 처리한다.
- 실패 시 재시도, 로깅, trace 태그 정책을 정한다.

**arXiv 메타데이터 보강**

- `fetch_arxiv_metadata(arxiv_ids)`를 구현한다.
- arXiv `id_list`를 사용해 초록, primary category, PDF 링크, 발행일을 보강한다.
- 연속 호출 제한을 고려한 지연 정책을 반영한다.

**원본 저장**

- `RawPaperStore.save_daily_papers_response(date, payload)`를 구현한다.
- MongoDB에 원본 payload, 수집 날짜, 수집 시각을 저장한다.

**DAG 오케스트레이션**

- DAG 파일은 얇게 유지한다.
- 실제 비즈니스 로직은 `src/pipeline`에서 실행한다.
- DAG 의존 순서와 태스크 이름을 문서화한다.

#### 다른 역할에 제공해야 할 것

- 날짜 기준 원본 feed 수집 함수
- arXiv 메타데이터 보강 함수
- MongoDB 저장 함수
- `run_collect_papers()`, `run_prepare_papers()`, `run_embed_papers()`, `run_analyze_topics()` 진입점
- 통합 테스트에 사용할 최소 실데이터

#### 완료 기준

- `setup-dev.sh`, `setup-server.sh`가 실패 없이 실행된다.
- Airflow UI에서 `arxplore_*` 4개 DAG가 확인된다.
- 특정 날짜의 HF Daily Papers를 MongoDB에 저장할 수 있다.
- arXiv 보강 데이터를 저장 계층 담당자에게 넘길 수 있다.
- 다른 담당자가 같은 DB에 접속해 실데이터를 확인할 수 있다.

### 7-2. 저장 계층 담당

이 역할의 책임은 "정제된 논문과 토픽 문서가 일관된 구조로 저장되고 다시 읽힐 수 있게 만드는 것"이다. 이 계층이 흔들리면 파이프라인, RAG, UI가 모두 불안정해진다. 따라서 저장 담당자는 함수 이름보다도 입출력 계약의 안정성을 우선해야 한다.

#### 소유 파일

- `src/integrations/paper_repository.py`
- `src/integrations/topic_repository.py`

#### 구현 대상

**PostgreSQL 스키마 설계**

다음 테이블의 컬럼, 키, 인덱스를 설계한다.

- `papers`
- `paper_chunks`
- `topics`
- `topic_documents`

`paper_embeddings`는 임베딩 담당자가 책임진다.

**자연키 결정**

- `papers`는 `arxiv_id`를 자연키로 사용한다.
- 동일 논문 재수집 시 insert가 아니라 upsert 기준으로 동작해야 한다.

**`PaperRepository` 구현**

최소 필요 메서드는 다음과 같다.

- `save_paper(paper: dict) -> str`
- `save_paper_chunks(arxiv_id: str, chunks: list[dict]) -> None`
- `get_paper(arxiv_id: str) -> dict | None`
- `list_paper_chunks(arxiv_id: str) -> list[dict]`
- `list_papers_for_topic(topic_id: int) -> list[dict]`

**`TopicRepository` 구현**

최소 필요 메서드는 다음과 같다.

- `save_topic(topic_id: int, title: str, keywords: list[str] | None = None) -> int`
- `save_topic_papers(topic_id: int, arxiv_ids: list[str]) -> None`
- `save_topic_document(document: TopicDocument) -> int`
- `get_topic_document(topic_id: int) -> TopicDocument | None`
- `list_topic_documents(*, limit: int = 20) -> list[TopicDocument]`

#### 구현 시 유의점

- `TopicDocument`를 JSONB로 저장하되, 카드 목록 조회가 가능하도록 정렬/인덱스를 고려한다.
- `citation_count`는 optional 필드이므로 NULL 허용이 필요하다.
- `github_url`, `github_stars`, `upvotes`도 누락 가능성을 전제로 저장해야 한다.
- DB 드라이버 선택과 트랜잭션 정책을 문서화한다.

#### 다른 역할에 제공해야 할 것

- 논문 저장 함수
- 논문 청크 저장 함수
- 토픽 문서 저장/조회 함수
- UI 카드용 토픽 문서 목록 조회 함수
- 토픽별 논문 묶음 조회 함수

#### 완료 기준

- 논문 1건 이상을 저장하고 다시 조회할 수 있다.
- 토픽 문서 1건 이상을 저장하고 동일 구조로 다시 읽을 수 있다.
- 카드 UI가 소비할 목록 조회 함수가 준비되어 있다.
- LLM 담당자와 UI 담당자가 Repository 시그니처에 의존해 개발할 수 있다.

### 7-3. 임베딩 · 클러스터링 · 벡터 검색 담당

이 역할의 책임은 "논문 텍스트를 벡터 검색 가능한 구조로 바꾸고, 유사 논문을 토픽으로 묶는 것"이다. 이 역할의 출력 품질은 검색 정확도와 토픽 품질을 동시에 좌우한다.

#### 소유 파일

- `src/integrations/embedding_client.py`
- `src/integrations/vector_repository.py`

필요에 따라 다음 파일을 새로 추가할 수 있다.

- `src/integrations/chunker.py`
- `src/integrations/clustering.py`

#### 구현 대상

**청크 전략**

- 초록을 적절한 길이로 나누는 규칙을 정한다.
- 청크 크기, overlap, 문장/문단 기준 여부를 문서화한다.

**임베딩 생성**

- `EmbeddingClient.embed_texts(texts)`를 구현한다.
- 배치 처리와 재시도 정책을 정한다.

**pgvector 저장**

- `paper_embeddings` 테이블 구조를 설계한다.
- `VectorRepository.upsert_paper_embeddings()`를 구현한다.

**검색 함수**

- `VectorRepository.search_paper_chunks(query_embedding, limit=5)`를 구현한다.
- 반환값에는 `chunk_id`, `arxiv_id`, `chunk_text`, `similarity_score`가 포함되어야 한다.

**토픽 그룹핑**

- 유사 논문을 토픽 단위로 묶는 로직을 구현한다.
- 결과는 `topic_id -> arxiv_ids` 매핑으로 저장 계층에 전달할 수 있어야 한다.

#### 다른 역할에 제공해야 할 것

- 청크 분할 함수 또는 규칙
- 임베딩 생성 함수
- 유사 청크 검색 함수
- 토픽 그룹핑 결과

#### 완료 기준

- 논문 초록을 청크로 분할할 수 있다.
- 생성한 벡터를 저장하고 다시 검색할 수 있다.
- 질문 벡터 기준으로 유사 청크를 반환할 수 있다.
- 토픽 그룹핑 결과를 저장 계층과 연결할 수 있다.

### 7-4. LLM · RAG 담당

이 역할은 "논문 묶음이 읽을 수 있는 토픽 문서로 바뀌는 품질"과 "검색 결과가 신뢰 가능한 답변으로 바뀌는 품질"을 함께 책임진다.

#### 소유 파일

- `src/core/prompts/overview.py`
- `src/core/prompts/key_findings.py`
- `src/core/chains.py`
- `src/core/rag.py`
- `src/core/tracing.py`

`src/core/models.py`는 직접 소유 파일이 아니다. 계약 변경이 필요하면 문서와 함께 전원 합의를 거쳐야 한다.

#### 구현 대상

**프롬프트 정교화**

- `overview`는 토픽 흐름을 3~5문장으로 설명해야 한다.
- `key_findings`는 논문들의 기여, 결과, 차이를 항목형으로 정리해야 한다.
- 추측형 문장, 과장된 평가, 근거 없는 전망을 줄이는 방향으로 다듬는다.

**체인 안정화**

- `_format_papers()`가 LLM에 전달할 입력을 잘 구성하는지 점검한다.
- `_build_paper_refs()`와 `_build_related_topics()`가 결정적으로 조합되는지 검증한다.
- `analyze_topic()`이 항상 `TopicDocument` 구조를 반환하도록 안정화한다.

**RAG 응답 구현**

- 검색 결과 범위 안에서만 답변하게 한다.
- 검색 결과 부족 시 응답 정책을 정한다.
- 답변과 함께 근거 논문이나 토픽 문서를 반환하는 구조를 정의한다.

**LangSmith 평가**

- 프롬프트, 체인, 응답 품질을 trace로 비교한다.
- 출력 포맷 실패나 환각 가능성이 보이면 prompt / parser / retrieval 쪽 원인을 구분한다.

#### 다른 역할에 제공해야 할 것

- `analyze_topic()` 진입점
- `answer_question()` 또는 동등한 질의응답 진입점
- 응답 포맷 계약
- 추적 가능한 trace 태그

#### 완료 기준

- 샘플 논문 묶음에서 `TopicDocument`를 안정적으로 생성할 수 있다.
- 질의응답 진입점이 검색 결과와 함께 동작한다.
- 검색 결과 부족 상황에서도 과도한 환각 없이 응답한다.

### 7-5. UI · 문서 소비 계층 담당

이 역할은 "현재 저장소가 사용자에게 어떤 경험으로 보이는가"를 책임진다. 즉, UI는 단순 렌더링 계층이 아니라 제품 구조를 최종적으로 드러내는 계층이다.

#### 소유 파일

- `app/main.py`
- `app/components/topic_card.py`
- `app/components/section_renderer.py`
- `app/pages/topic_detail.py`

필요 시 UI 보조 컴포넌트를 추가할 수 있다.

#### 구현 대상

**메인 화면 흐름**

- 검색 입력
- 답변 결과 영역
- 토픽 카드 영역
- 빈 상태와 오류 상태

**카드 렌더링**

- 토픽 제목
- 짧은 개요
- 논문 수
- 생성 시각 또는 최근성 힌트

**상세 문서 렌더링**

- 개요
- 핵심 발견
- 논문 목록
- 관련 토픽
- 목차 기반 이동

**실데이터 연결 대비**

- 데모 데이터와 실데이터가 같은 렌더링 경로를 타도록 구조를 정리한다.
- DB 조회 실패, 문서 없음, 검색 결과 부족 상태를 화면에서 처리한다.

#### 다른 역할에 제공해야 할 것

- 카드/상세 페이지가 기대하는 데이터 형태
- 검색 응답이 UI에서 어떻게 소비되는지에 대한 요구사항
- 오류 상태와 로딩 상태 정책

#### 완료 기준

- 데모 데이터 기준으로 메인/카드/상세 흐름이 안정적으로 동작한다.
- 실데이터로 바꿔도 같은 컴포넌트 구조를 유지할 수 있다.
- 카드와 상세 문서가 `TopicDocument` 계약에 직접 의존하도록 정리되어 있다.

## 8. 역할 간 handoff 체크리스트

### 인프라 담당이 넘겨야 하는 것

- 샘플 HF Daily Papers 원본 payload
- arXiv 보강 후 paper dict 예시
- `.env` 기준 환경 변수 설명
- Airflow 실행 방법

### 저장 담당이 넘겨야 하는 것

- Repository 메서드 시그니처
- 입력 dict 필드 규칙
- 반환 dict / `TopicDocument` 예시

### 임베딩 담당이 넘겨야 하는 것

- 청크 전략
- 검색 함수 입력/출력 예시
- 토픽 그룹핑 결과 구조

### LLM 담당이 넘겨야 하는 것

- `TopicDocument` 샘플 출력
- 질의응답 응답 예시
- 검색 결과 부족 시 동작 예시

### UI 담당이 넘겨야 하는 것

- 화면 상태 정의
- 필요한 조회 함수 목록
- 카드/상세/검색 응답 렌더링 요구사항

## 9. 변경 금지 또는 협의 필수 항목

다음 항목은 개인 판단으로 바꾸지 않는다.

- `TopicDocument` 필드 구조
- 공용 import 경로
- DAG 이름
- Compose 서비스명
- `.env`의 핵심 설정 키
- 저장소 전역 용어

이 항목을 바꿔야 하면 관련 담당자와 문서부터 같이 업데이트해야 한다.

## 10. 최종 완료 조건

역할별 구현이 끝났다고 보기 위한 최종 기준은 다음과 같다.

- Airflow 4개 DAG가 등록되고 실행 경로가 이어진다.
- 논문 수집부터 `TopicDocument` 저장까지 한 번의 흐름으로 연결된다.
- 검색창에서 질문하고 근거 기반 응답을 받을 수 있다.
- 메인 카드와 상세 문서가 실데이터를 렌더링할 수 있다.
- 역할 간 임시 코드가 아니라 공용 계약 기반으로 통합돼 있다.

이 문서는 구현이 진행되면서 구체화될 수 있지만, 책임 경계 자체를 흐리는 방향으로 바뀌어서는 안 된다.
