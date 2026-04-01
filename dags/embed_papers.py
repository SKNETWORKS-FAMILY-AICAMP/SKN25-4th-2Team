"""임베딩 및 토픽 묶기 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_embed_papers


@dag(
    dag_id="arxplore_embed_papers",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["arxplore", "embed", "papers", "scaffold"],
)
def embed_papers_dag():
    @task(task_id="run_embed_papers")
    def _run() -> dict:
        return run_embed_papers()

    _run()


dag = embed_papers_dag()
