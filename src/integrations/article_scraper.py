"""기사 본문 스크래핑 뼈대."""

from __future__ import annotations

from typing import Any


class ArticleScraper:
    """기사 URL에서 본문과 메타데이터를 추출하는 진입점."""

    def fetch_article(self, url: str) -> dict[str, Any]:
        """단일 기사 URL에서 본문, 제목, 발행 시각 등 정제 가능한 입력을 반환한다."""
        raise NotImplementedError("기사 스크래핑은 수집 담당자가 구현할 예정입니다.")
