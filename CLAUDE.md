# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### 컨테이너 실행

```bash
# 기본 (django + nginx + vite)
bash scripts/setup.sh

# 내리기
docker compose down

# GPU parser + prepare-worker 포함
docker compose --profile parser up -d --build

# 서버 인프라 (PostgreSQL, MongoDB, Airflow) — 원격 서버에서 실행
bash scripts/setup-server.sh

# SSH 포트 포워딩 (원격 서버 → localhost)
bash scripts/setup.sh forward [start|stop|status|restart]
```

### 개발

```bash
# Django 컨테이너 셸
docker compose exec django bash

# vite 이미지 재빌드 (package.json 변경 후)
docker compose build vite

# 로그 확인
docker compose logs -f [django|nginx|vite]
```

### Key Ports

| Service | Host Port |
|---------|-----------|
| Web (nginx) | 80 (`PROD_HTTP_PORT`) |
| Vite (dev) | 5173 (`FRONTEND_PORT`) |
| Layout Parser | 5060 (`LAYOUT_PARSER_PORT`) |
| Airflow | 18080 |
| MongoDB | 17017 |
| PostgreSQL | 15432 |

## Architecture

ArXplore는 HuggingFace Daily Papers + arXiv 논문을 수집·처리해 RAG 기반 채팅 인터페이스로 제공하는 플랫폼입니다.

### Data Flow

```
HF Daily Papers / arXiv
  → Airflow DAGs (daily_collect, maintenance)  [서버]
  → MongoDB (raw payload)                       [서버]
  → PostgreSQL prepare_jobs queue (LISTEN/NOTIFY)
  → prepare-worker (PDF parse → embed)          [--profile parser]
  → PostgreSQL: papers, paper_fulltexts, paper_chunks, paper_embeddings (pgvector)
  → Retrieval (lexical / vector / hybrid + rerank)
  → LangChain chains + LangGraph React Agent
  → Django REST API → React UI
```

### Docker Compose 구조

단일 `docker-compose.yml`로 모든 서비스를 관리합니다.

| 서비스 | 프로필 | 설명 |
|--------|--------|------|
| `django` | (기본) | gunicorn WSGI 서버 |
| `nginx` | (기본) | React 빌드 서빙 + API 프록시 |
| `vite` | (기본) | 프론트엔드 HMR 개발 서버 |
| `prepare-worker` | `parser` | prepare queue 소비 worker |
| `layout-parser` | `parser` | HURIDOCS GPU PDF 파서 |

서버 인프라(PostgreSQL, MongoDB, Airflow)는 `docker-compose.server.yml`로 별도 운영합니다.

### Key Architectural Split

**Server-side** (`docker-compose.server.yml`): PostgreSQL, MongoDB, Airflow — 항상 켜져있는 원격 서버에서 실행.

**Local** (`docker-compose.yml`): Django(gunicorn) + nginx + vite는 로컬에서 실행. parser 프로필은 GPU 보유 시에만 추가.

**prepare-worker는 Airflow가 아닌 로컬에서 실행** — PDF 파싱과 임베딩은 무거운 작업이므로 로컬 GPU에서 처리. 이 분리를 깨지 말 것.

### Module Responsibilities

- **`backend/`** — Django 프로젝트 루트 (`manage.py`, `arxplore_web/` 설정, `papers/` 앱)
  - `papers/api_views.py` — REST 엔드포인트 (인증, 논문 조회·분석·채팅, 즐겨찾기)
  - `papers/services.py` — 비즈니스 로직 계층 (LLM 체인 호출, 캐시, 권한)
  - `papers/models.py` — `UserSettings`, `FavoritePaper`, `PaperAISummary`
- **`src/core/`** — LLM 체인, 프롬프트, RAG 로직, LangGraph 에이전트
- **`src/integrations/`** — 외부 I/O: MongoDB, PostgreSQL 리포지토리, HURIDOCS 클라이언트, OpenAI 임베딩, hybrid retriever
- **`src/pipeline/`** — Airflow DAG 및 prepare-worker가 호출하는 진입점 스크립트
- **`src/shared/`** — Pydantic `AppSettings` (`.env` 로드), LangSmith 트레이싱
- **`dags/`** — Airflow DAG 정의 (`PythonOperator`로 `src/pipeline/` 호출)
- **`frontend/`** — React 18 + Vite + TanStack Query + TypeScript

### PDF Parsing Strategy

3단계 폴백:
1. HURIDOCS Layout Parser (Docker, `LAYOUT_PARSER_BASE_URL`)
2. pypdf
3. abstract only

청크에 `content_role`, `section_title`, `parser_metadata`, `quality_metrics` 저장.

### Retrieval

`src/integrations/paper_retriever.py`:
- **Lexical** — PostgreSQL 전문 검색
- **Vector** — pgvector (text-embedding-3-large, 1536 dims)
- **Hybrid** — reciprocal rank fusion + content-role reranking

### Agent

`src/core/agent/chatbot.py` — LangGraph ReAct Agent (`stream_mode="messages"`)
- `search_paper_chunks_tool` — 키워드 기반 청크 검색
- `get_trending_papers_tool` — 트렌딩 논문 통계

### Architectural Contracts (do not break)

`PaperDetailDocument` 필드: `arxiv_id`, `title`, `overview`, `key_findings` — 체인·API·UI 공용 계약.

Retrieval 결과 shape: `chunk_id`, `arxiv_id`, `chunk_text`, `section_title`, `content_role`, `score`.

## Configuration

모든 런타임 설정은 루트 `.env`. `src/shared/settings.py`가 Pydantic `BaseSettings`로 로드.

```
OPENAI_API_KEY              # LLM + 임베딩 필수
OPENAI_MODEL                # 기본: gpt-4o
OPENAI_EMBEDDING_MODEL      # 기본: text-embedding-3-large
LANGSMITH_API_KEY           # 선택; 트레이싱 활성화
PROD_POSTGRES_HOST          # 메인 서버 PostgreSQL host (setup.sh 필수 체크)
DJANGO_SECRET_KEY           # Django 시크릿 키 (setup.sh 필수 체크)
LAYOUT_PARSER_BASE_URL      # 파서 컨테이너 실행 시 자동 감지
```

Django 설정: `backend/arxplore_web/settings.py`. 언어 `ko-kr`, 타임존 `Asia/Seoul`.

Vite 프록시는 `frontend/vite.config.ts`에서 `arxplore-django:8001`로 포워딩 (Host 헤더 `localhost` 고정).

## Reference Docs

1. `docs/management/PLAN.md` — 제품 목표, 도메인 범위
2. `docs/architecture/ARCHITECTURE.md` — 시스템 구조, DB 스키마
3. `docs/architecture/AGENTS.md` — AI 작업 규칙, 모듈 계약, 용어
4. `docs/management/WORKFLOW.md` — 운영 절차, 작업 모드
