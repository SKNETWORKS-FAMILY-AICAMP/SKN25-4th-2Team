"""뉴스 원본 응답 저장 계층 뼈대."""

from __future__ import annotations

from typing import Any


class RawNewsStore:
    """뉴스 API 원본 응답을 MongoDB에 저장하는 진입점."""

    def save_search_response(
        self,
        *,
        provider: str,
        query: str,
        payload: dict[str, Any],
    ) -> str:
        """원본 응답과 메타데이터를 저장하고 저장 식별자를 반환한다."""
        raise NotImplementedError("MongoDB 원본 저장은 수집 담당자가 구현할 예정입니다.")
