"""뉴스 검색 API 연동 뼈대."""

from __future__ import annotations

from typing import Any


class NewsSearchClient:
    """뉴스 검색 API 클라이언트의 공통 진입점.

    수집 담당자는 이 클래스를 기준으로 provider별 호출 로직과 fallback 규칙을 구현한다.
    반환 데이터는 이후 MongoDB 원본 저장과 기사 정제 단계에서 재사용할 수 있어야 한다.
    """

    def search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """질의에 해당하는 기사 목록을 반환한다."""
        raise NotImplementedError("뉴스 검색 API 연동은 수집 담당자가 구현할 예정입니다.")
