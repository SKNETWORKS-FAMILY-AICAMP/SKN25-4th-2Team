"""임베딩 및 이슈 묶기 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_embed_articles


@dag(
    dag_id="newspedia_embed_articles",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["newspedia", "embed", "scaffold"],
)
def embed_articles_dag():
    @task(task_id="run_embed_articles")
    def _run() -> dict:
        return run_embed_articles()

    _run()


dag = embed_articles_dag()
