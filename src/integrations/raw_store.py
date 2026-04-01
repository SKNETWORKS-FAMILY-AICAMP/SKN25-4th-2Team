"""논문 원본 응답 저장 계층 뼈대."""

from __future__ import annotations

from typing import Any


class RawPaperStore:
    """HF Daily Papers 원본 응답을 MongoDB에 저장하는 진입점."""

    def save_daily_papers_response(
        self,
        *,
        date: str,
        payload: list[dict[str, Any]] | dict[str, Any],
    ) -> str:
        """원본 응답과 수집 날짜를 저장하고 저장 식별자를 반환한다."""
        raise NotImplementedError("MongoDB 원본 저장은 수집 담당자가 구현할 예정입니다.")
