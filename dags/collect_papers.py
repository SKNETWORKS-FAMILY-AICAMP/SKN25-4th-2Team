"""논문 수집 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_collect_papers


@dag(
    dag_id="arxplore_collect_papers",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["arxplore", "collect", "papers", "scaffold"],
)
def collect_papers_dag():
    @task(task_id="run_collect_papers")
    def _run() -> dict:
        return run_collect_papers()

    _run()


dag = collect_papers_dag()
