# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Dev Environment

```bash
# 개발 환경 초기 설정 (컨테이너 빌드 및 시작)
bash scripts/setup-dev.sh

# 특정 서비스만 시작
docker compose -p arxplore_dev -f docker-compose.dev.yml up django frontend

# dev 컨테이너 셸 접속
docker compose -p arxplore_dev -f docker-compose.dev.yml exec dev bash
```

접속 주소: Frontend `http://localhost:5173` · Django `http://localhost:18001` · Jupyter `http://localhost:18888`

### Django

```bash
# dev 컨테이너 안에서 실행
cd /workspace/web && python manage.py runserver 0.0.0.0:8001
python manage.py migrate
python manage.py shell
```

### Prepare Worker

```bash
# auto 모드 (LISTEN/NOTIFY, 루프)
bash scripts/prepare-worker.sh

# 1회 실행
bash scripts/prepare-worker.sh once
```

### Local Parser

```bash
docker compose -f docker-compose.parser.yml up -d --build
docker logs -f arxplore-layout-parser
```

### Pipeline (dev 컨테이너 안에서)

```bash
# PYTHONPATH=/workspace:/workspace/src 가 설정되어 있어야 함
python3 -m src.pipeline.collect_papers
python3 -m src.pipeline.prepare_papers
python3 -m src.pipeline.embed_papers
python3 -m src.pipeline.enrich_papers_metadata
```

## Architecture

### Runtime Topology

시스템은 **서버**, **로컬 개발**, **로컬 파서** 세 런타임으로 분리된다.

- **서버** (`docker-compose.server.yml`): PostgreSQL, MongoDB, Airflow (2개 DAG)
  - `arxplore_daily_collect` — KST 18:00, HF Daily Papers 수집 → `prepare_jobs` enqueue
  - `arxplore_maintenance` — 3시간마다 raw backfill → arXiv 메타데이터 enrichment
- **로컬 개발** (`docker-compose.dev.yml`): Python/Jupyter, Django API, React 프론트엔드
- **로컬 파서** (`docker-compose.parser.yml`): HURIDOCS Layout Parser HTTP 서버

서버는 큐를 만들고, **무거운 파싱과 임베딩은 로컬 worker**가 처리해 서버 DB에 직접 적재한다.

### Data Flow

```
HF Daily Papers → MongoDB(raw) → prepare_jobs(PostgreSQL)
                                        ↓ LISTEN/NOTIFY
                              prepare-worker (로컬)
                                        ↓
                     HURIDOCS Parser → pypdf → abstract fallback
                                        ↓
                papers / paper_fulltexts / paper_chunks / paper_embeddings (PostgreSQL + pgvector)
                                        ↓
                       lexical / vector / hybrid retrieval
                                        ↓
                  PaperDetailDocument chains + LangGraph React Agent → React UI
```

### Module Layers

| 계층 | 경로 | 책임 |
|------|------|------|
| shared | `src/shared/` | 설정(`settings.py`), LangSmith tracing |
| integrations | `src/integrations/` | 외부 연동, 저장소 접근, retrieval 구현 |
| core | `src/core/` | 도메인 모델, 프롬프트, 생성 체인, RAG 응답, agent |
| pipeline | `src/pipeline/` | DAG/worker가 호출하는 실행 진입점 |
| dags | `dags/` | Airflow DAG 정의만 |
| web | `web/` | Django API + React shell |
| frontend | `frontend/` | React + Vite + TypeScript UI |

**계층 경계 규칙**: DAG에 비즈니스 로직 금지, 외부 연동 코드는 `src/integrations/`에만, UI 편의로 도메인 계약 변경 금지.

### Key Contracts (임의 변경 금지)

`src/core/models.py`의 `PaperRef`, `PaperDetailDocument`는 팀 공용 계약이다. 생성 체인의 출력이자 UI 입력이므로 필드 이름·타입·삭제는 팀 합의 없이 하지 않는다.

retrieval 결과의 핵심 필드(`chunk_id`, `arxiv_id`, `chunk_text`, `section_title`, `content_role`, `score`)도 안정적으로 유지한다.

계약 변경이 필요하면: ① 변경 이유, ② 영향 계층, ③ 문서·코드 수정 범위를 먼저 제시한다.

### Settings & Environment

`src/shared/settings.py`의 `AppSettings`(pydantic-settings)가 `.env`를 로드한다. 필수 환경변수: `POSTGRES_HOST`, `POSTGRES_DB` 또는 `APP_POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `MONGO_HOST`, `OPENAI_API_KEY`. `get_settings()`는 `lru_cache`로 싱글톤이다.

OpenAI API key와 모델은 `override_openai_runtime()` context manager로 요청별로 교체할 수 있다(사용자 개인 API key 지원).

### Django API

`web/papers/api_views.py` — 논문 분석, 요약, 채팅, bootstrap, 인증, 즐겨찾기 엔드포인트.  
`web/papers/services.py` — 비즈니스 로직 계층, `src/core`·`src/integrations`를 조합.

### Retrieval Pipeline

`src/integrations/paper_retriever.py`가 lexical / vector / hybrid 세 채널을 통합 제공한다. rerank는 lexical overlap, section prior, content_role penalty, reference 오염 완화를 적용한다. hybrid + rerank 조합이 grounding 품질에서 가장 우수하다.

### LangGraph React Agent

`src/core/agent.py`에 구현된 에이전트는 두 도구를 사용한다:
- `search_paper_chunks_tool` — 키워드 기반 본문 청크 근거 검색
- `get_trending_papers_tool` — 최신/인기 논문 통계 조회

`stream_mode="messages"`로 실시간 스트리밍 응답을 프론트엔드에 전달한다.

### LangSmith Tracing

주요 stage 이름: `collect_papers`, `prepare_papers`, `embed_papers`, `enrich_papers_metadata`, `analyze_paper_detail`, `paper_overview`, `paper_key_findings`, `translation`, `summary`, `rag_answer`

### Inspection Notebook

`notebooks/retrieval_inspection.ipynb` — 적재 상태, queue 상태, retrieval 결과를 직접 확인.

## Terminology

| 표준 표현 | 설명 |
|----------|------|
| `논문 상세 문서` | `PaperDetailDocument` 단위 구조화 문서 |
| `논문 개요` | 단일 논문의 목적·접근·결과를 설명하는 overview |
| `핵심 포인트` | 단일 논문의 기여·결과를 정리한 key findings |
| `상세 요약` | 논문 본문을 한국어로 구조화한 detailed summary |
| `근거 번역` | 근거 chunk의 한국어 번역 |
| `논문 청크` | retrieval과 grounding 입력 단위 |
| `prepare job` | 날짜 단위 prepare 작업 |
