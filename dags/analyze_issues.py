"""이슈 문서 생성 DAG 스캐폴드."""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from src.pipeline import run_analyze_issues


@dag(
    dag_id="newspedia_analyze_issues",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["newspedia", "analyze", "scaffold"],
)
def analyze_issues_dag():
    @task(task_id="run_analyze_issues")
    def _run() -> dict:
        return run_analyze_issues()

    _run()


dag = analyze_issues_dag()
