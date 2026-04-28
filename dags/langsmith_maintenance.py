"""LangSmith trace retention maintenance DAG."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from airflow.sdk import dag, task

from src.pipeline import run_cleanup_langsmith


@dag(
    dag_id="arxplore_langsmith_maintenance",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Seoul")),
    catchup=False,
    params={
        "days": 14,
        "project_name": "",
        "user": "",
        "limit": "",
        "dry_run": False,
    },
    tags=["arxplore", "langsmith", "maintenance"],
)
def langsmith_maintenance_dag():
    @task(task_id="run_cleanup_langsmith")
    def _run(
        days: str | int | None = None,
        project_name: str | None = None,
        user: str | None = None,
        limit: str | int | None = None,
        dry_run: bool | str | None = None,
    ) -> dict:
        normalized_days = int(str(days or "14").strip() or "14")
        normalized_limit = None
        if str(limit or "").strip():
            normalized_limit = int(str(limit).strip())
        normalized_dry_run = str(dry_run).strip().lower() in {"1", "true", "yes", "y"}
        if isinstance(dry_run, bool):
            normalized_dry_run = dry_run

        return run_cleanup_langsmith(
            days=normalized_days,
            project_name=(project_name or "").strip() or None,
            user=(user or "").strip() or None,
            limit=normalized_limit,
            dry_run=normalized_dry_run,
        )

    _run(
        days="{{ dag_run.conf.get('days', params.days) if dag_run else params.days }}",
        project_name="{{ dag_run.conf.get('project_name', params.project_name) if dag_run else params.project_name }}",
        user="{{ dag_run.conf.get('user', params.user) if dag_run else params.user }}",
        limit="{{ dag_run.conf.get('limit', params.limit) if dag_run else params.limit }}",
        dry_run="{{ dag_run.conf.get('dry_run', params.dry_run) if dag_run else params.dry_run }}",
    )


langsmith_maintenance = langsmith_maintenance_dag()
