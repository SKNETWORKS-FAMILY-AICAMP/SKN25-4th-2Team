"""로컬 GPU 환경에서 prepare 자동추적/백필을 실행하는 워커 모듈."""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

from src.pipeline import run_backfill_prepare_papers, run_consume_prepare_queue


def _run_once(args: argparse.Namespace) -> dict[str, Any]:
    normalized_worker_id = (args.worker_id or args.state_name or "").strip() or "default"
    normalized_max_papers = (args.max_papers or "").strip() or None

    if args.mode == "auto":
        return run_consume_prepare_queue(
            runtime="local",
            user="local_prepare_worker",
            mode="auto",
            worker_id=normalized_worker_id,
            max_jobs_per_run=max(1, int(args.max_jobs_per_run)),
            max_papers=normalized_max_papers,
        )

    return run_backfill_prepare_papers(
        runtime="local",
        user="local_prepare_worker",
        cursor_date=(args.cursor_date or "").strip() or None,
        oldest_date=(args.oldest_date or "").strip() or None,
        batch_days=max(1, int(args.batch_days)),
        state_name=normalized_worker_id,
        max_papers=normalized_max_papers,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="로컬 GPU에서 prepare 워커를 실행한다.")
    parser.add_argument(
        "--mode",
        choices=["auto", "backfill"],
        default="auto",
        help="auto는 신규 수집분 자동 추적, backfill은 과거 날짜 수동 배치 처리다.",
    )
    parser.add_argument("--max-jobs-per-run", type=int, default=1, help="auto 모드에서 한 run에 소비할 큐 작업 수.")
    parser.add_argument("--cursor-date", default="", help="시작 cursor 날짜(YYYY-MM-DD). 비우면 저장된 state를 사용한다.")
    parser.add_argument("--oldest-date", default="", help="종료 기준 날짜(YYYY-MM-DD). 비우면 state 또는 기본값을 사용한다.")
    parser.add_argument("--batch-days", type=int, default=3, help="한 번에 처리할 날짜 수. 기본값은 3이다.")
    parser.add_argument("--max-papers", default="", help="날짜당 최대 논문 수. 비우면 해당 날짜 전체를 처리한다.")
    parser.add_argument("--worker-id", default="default", help="큐 작업 선점에 사용하는 워커 식별자.")
    parser.add_argument("--state-name", default="", help="deprecated: --worker-id를 사용한다.")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="활성화하면 completed 상태가 될 때까지 반복 실행한다.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=60.0,
        help="loop 실행 시 run 사이 대기 시간(초). 기본값은 60초다.",
    )
    args = parser.parse_args()

    while True:
        result = _run_once(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))

        if not args.loop:
            return 0 if result.get("status") != "failed" else 1

        status = str(result.get("status") or "")
        if status in {"completed", "no_op"}:
            return 0
        if status == "failed":
            return 1
        time.sleep(max(0.0, float(args.sleep_seconds)))


if __name__ == "__main__":
    raise SystemExit(main())
