"""수집/백필/메타보강/오케스트레이션 DAG를 묶은 모듈."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.sdk import dag, task

from src.pipeline import run_backfill_collect_papers, run_collect_papers, run_enrich_papers_metadata


@dag(
    dag_id="arxplore_collect_papers",
    schedule="0 18 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Seoul")),
    catchup=False,
    params={"target_date": ""},
    tags=["arxplore", "collect", "papers"],
)
def collect_papers_dag():
    @task(task_id="run_collect_papers")
    def _run(target_date: str | None = None) -> dict:
        return run_collect_papers(target_date=target_date)

    _run(target_date="{{ dag_run.conf.get('target_date', params.target_date) if dag_run else params.target_date }}")


@dag(
    dag_id="arxplore_backfill_collect_papers",
    schedule="0 */3 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Seoul")),
    catchup=False,
    params={
        "cursor_date": "",
        "oldest_date": "",
        "batch_days": 30,
        "state_name": "default",
    },
    tags=["arxplore", "collect", "papers", "backfill"],
)
def backfill_collect_papers_dag():
    @task(task_id="run_backfill_collect_papers")
    def _run(
        cursor_date: str | None = None,
        oldest_date: str | None = None,
        batch_days: str | int | None = None,
        state_name: str | None = None,
    ) -> dict:
        normalized_batch_days = int(str(batch_days or "30").strip() or "30")
        normalized_state_name = (state_name or "").strip() or "default"
        return run_backfill_collect_papers(
            cursor_date=(cursor_date or "").strip() or None,
            oldest_date=(oldest_date or "").strip() or None,
            batch_days=normalized_batch_days,
            state_name=normalized_state_name,
        )

    _run(
        cursor_date="{{ dag_run.conf.get('cursor_date', params.cursor_date) if dag_run else params.cursor_date }}",
        oldest_date="{{ dag_run.conf.get('oldest_date', params.oldest_date) if dag_run else params.oldest_date }}",
        batch_days="{{ dag_run.conf.get('batch_days', params.batch_days) if dag_run else params.batch_days }}",
        state_name="{{ dag_run.conf.get('state_name', params.state_name) if dag_run else params.state_name }}",
    )


@dag(
    dag_id="arxplore_enrich_papers_metadata",
    schedule="30 */3 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Seoul")),
    catchup=False,
    params={"max_papers": 30},
    tags=["arxplore", "enrich", "papers", "metadata"],
)
def enrich_papers_metadata_dag():
    @task(task_id="run_enrich_papers_metadata")
    def _run(max_papers: str | int | None = None) -> dict:
        normalized_max_papers = int(str(max_papers or "30").strip() or "30")
        return run_enrich_papers_metadata(max_papers=normalized_max_papers)

    _run(max_papers="{{ dag_run.conf.get('max_papers', params.max_papers) if dag_run else params.max_papers }}")


@dag(
    dag_id="arxplore_orchestrate_ingestion",
    schedule=None,
    start_date=datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Seoul")),
    catchup=False,
    params={
        "collect_target_date": "",
        "backfill_cursor_date": "",
        "backfill_oldest_date": "",
        "backfill_batch_days": 30,
        "backfill_state_name": "default",
        "enrich_max_papers": 30,
    },
    tags=["arxplore", "orchestrator", "collect", "backfill", "enrich"],
)
def orchestrate_ingestion_dag():
    start = EmptyOperator(task_id="start")

    collect = TriggerDagRunOperator(
        task_id="trigger_collect_papers",
        trigger_dag_id="arxplore_collect_papers",
        conf={
            "target_date": "{{ dag_run.conf.get('collect_target_date', params.collect_target_date) if dag_run else params.collect_target_date }}",
        },
        wait_for_completion=True,
        poke_interval=30,
    )

    backfill = TriggerDagRunOperator(
        task_id="trigger_backfill_collect_papers",
        trigger_dag_id="arxplore_backfill_collect_papers",
        conf={
            "cursor_date": "{{ dag_run.conf.get('backfill_cursor_date', params.backfill_cursor_date) if dag_run else params.backfill_cursor_date }}",
            "oldest_date": "{{ dag_run.conf.get('backfill_oldest_date', params.backfill_oldest_date) if dag_run else params.backfill_oldest_date }}",
            "batch_days": "{{ dag_run.conf.get('backfill_batch_days', params.backfill_batch_days) if dag_run else params.backfill_batch_days }}",
            "state_name": "{{ dag_run.conf.get('backfill_state_name', params.backfill_state_name) if dag_run else params.backfill_state_name }}",
        },
        wait_for_completion=True,
        poke_interval=30,
    )

    enrich = TriggerDagRunOperator(
        task_id="trigger_enrich_papers_metadata",
        trigger_dag_id="arxplore_enrich_papers_metadata",
        conf={
            "max_papers": "{{ dag_run.conf.get('enrich_max_papers', params.enrich_max_papers) if dag_run else params.enrich_max_papers }}",
        },
        wait_for_completion=True,
        poke_interval=30,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_DONE)

    start >> collect >> backfill >> enrich >> end


collect_papers = collect_papers_dag()
backfill_collect_papers = backfill_collect_papers_dag()
enrich_papers_metadata = enrich_papers_metadata_dag()
orchestrate_ingestion = orchestrate_ingestion_dag()
