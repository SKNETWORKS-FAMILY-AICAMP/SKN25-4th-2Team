"""수집/백필/메타보강 DAG를 순차 실행으로 묶는 오케스트레이터."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.sdk import dag


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
        # backfill이 실패해도 메타 보강은 계속 시도한다.
        trigger_rule=TriggerRule.ALL_DONE,
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_DONE)

    start >> collect >> backfill >> enrich >> end


dag = orchestrate_ingestion_dag()
