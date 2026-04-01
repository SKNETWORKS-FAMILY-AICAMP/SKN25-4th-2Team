"""논문 전처리 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_prepare_papers


@dag(
    dag_id="arxplore_prepare_papers",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["arxplore", "prepare", "papers", "scaffold"],
)
def prepare_papers_dag():
    @task(task_id="run_prepare_papers")
    def _run() -> dict:
        return run_prepare_papers()

    _run()


dag = prepare_papers_dag()
