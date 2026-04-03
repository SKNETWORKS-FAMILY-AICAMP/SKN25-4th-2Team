"""논문 청크 임베딩을 생성해 pgvector에 적재하는 DAG."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_embed_papers


@dag(
    dag_id="arxplore_embed_papers",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    params={"max_chunks": 200, "arxiv_id": ""},
    tags=["arxplore", "embed", "papers"],
)
def embed_papers_dag():
    @task(task_id="run_embed_papers")
    def _run(max_chunks: str | int | None = None, arxiv_id: str | None = None) -> dict:
        normalized_limit = int(str(max_chunks or "200").strip() or "200")
        normalized_arxiv_id = (arxiv_id or "").strip() or None
        return run_embed_papers(max_chunks=normalized_limit, arxiv_id=normalized_arxiv_id)

    _run(
        max_chunks="{{ dag_run.conf.get('max_chunks', params.max_chunks) if dag_run else params.max_chunks }}",
        arxiv_id="{{ dag_run.conf.get('arxiv_id', params.arxiv_id) if dag_run else params.arxiv_id }}",
    )


dag = embed_papers_dag()
