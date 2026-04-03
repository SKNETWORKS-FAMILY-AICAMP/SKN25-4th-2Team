"""로컬 GPU 환경에서 prepare backfill을 실행하는 워커 스크립트."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _run_once(args: argparse.Namespace) -> dict[str, Any]:
    # 런타임 의존성이 무거워 --help만 볼 때는 import가 필요 없다.
    from src.pipeline import run_backfill_prepare_papers, run_track_prepare_papers

    normalized_state_name = (args.state_name or "").strip() or "default"
    normalized_max_papers = (args.max_papers or "").strip() or None

    if args.mode == "auto":
        return run_track_prepare_papers(
            runtime="local",
            user="local_prepare_worker",
            state_name=normalized_state_name,
            max_dates_per_run=max(1, int(args.max_dates_per_run)),
            max_papers=normalized_max_papers,
            bootstrap_cursor_date=(args.bootstrap_cursor_date or "").strip() or None,
        )

    return run_backfill_prepare_papers(
        runtime="local",
        user="local_prepare_worker",
        cursor_date=(args.cursor_date or "").strip() or None,
        oldest_date=(args.oldest_date or "").strip() or None,
        batch_days=max(1, int(args.batch_days)),
        state_name=normalized_state_name,
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
    parser.add_argument(
        "--max-dates-per-run",
        type=int,
        default=1,
        help="auto 모드에서 한 run에 처리할 날짜 수. 기본값은 1이다.",
    )
    parser.add_argument(
        "--bootstrap-cursor-date",
        default="",
        help="auto 모드 최초 실행 시 cursor 초기값(YYYY-MM-DD). 비우면 어제로 시작한다.",
    )
    parser.add_argument("--cursor-date", default="", help="시작 cursor 날짜(YYYY-MM-DD). 비우면 저장된 state를 사용한다.")
    parser.add_argument("--oldest-date", default="", help="종료 기준 날짜(YYYY-MM-DD). 비우면 state 또는 기본값을 사용한다.")
    parser.add_argument("--batch-days", type=int, default=3, help="한 번에 처리할 날짜 수. 기본값은 3이다.")
    parser.add_argument("--max-papers", default="", help="날짜당 최대 논문 수. 비우면 해당 날짜 전체를 처리한다.")
    parser.add_argument("--state-name", default="default", help="Mongo pipeline state 이름. 기본값은 default다.")
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
