"""이슈 문서 생성 파이프라인 스캐폴드."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .tracing import build_pipeline_trace_config


def run_analyze_issues(*, runtime: str = "airflow", user: Optional[str] = None) -> Dict[str, Any]:
    """이슈 문서 생성 단계의 실행 메타데이터를 반환합니다."""
    return {
        "stage": "analyze",
        "status": "scaffold",
        "trace_config": build_pipeline_trace_config(stage="analyze", runtime=runtime, user=user),
    }
