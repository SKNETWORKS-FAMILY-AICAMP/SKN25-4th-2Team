"""논문 처리 관련 prepare/embed/analyze DAG를 한 모듈에서 정의한다."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_analyze_topics, run_embed_papers, run_prepare_papers


@dag(
    dag_id="arxplore_prepare_papers",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    params={"target_date": "", "max_papers": ""},
    tags=["arxplore", "prepare", "papers"],
)
def prepare_papers_dag():
    @task(task_id="run_prepare_papers")
    def _run(target_date: str | None = None, max_papers: str | None = None) -> dict:
        return run_prepare_papers(target_date=target_date, max_papers=max_papers)

    _run(
        target_date="{{ dag_run.conf.get('target_date', params.target_date) if dag_run else params.target_date }}",
        max_papers="{{ dag_run.conf.get('max_papers', params.max_papers) if dag_run else params.max_papers }}",
    )


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


@dag(
    dag_id="arxplore_analyze_topics",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["arxplore", "analyze", "topics", "scaffold"],
)
def analyze_topics_dag():
    @task(task_id="run_analyze_topics")
    def _run() -> dict:
        return run_analyze_topics()

    _run()


prepare_papers = prepare_papers_dag()
embed_papers = embed_papers_dag()
analyze_topics = analyze_topics_dag()
