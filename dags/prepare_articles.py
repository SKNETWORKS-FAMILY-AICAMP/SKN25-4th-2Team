"""기사 전처리 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_prepare_articles


@dag(
    dag_id="newspedia_prepare_articles",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["newspedia", "prepare", "scaffold"],
)
def prepare_articles_dag():
    @task(task_id="run_prepare_articles")
    def _run() -> dict:
        return run_prepare_articles()

    _run()


dag = prepare_articles_dag()
