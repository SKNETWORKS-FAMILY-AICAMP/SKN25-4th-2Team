"""뉴스 수집 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_collect_news


@dag(
    dag_id="newspedia_collect_news",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["newspedia", "collect", "scaffold"],
)
def collect_news_dag():
    @task(task_id="run_collect_news")
    def _run() -> dict:
        return run_collect_news()

    _run()


dag = collect_news_dag()
