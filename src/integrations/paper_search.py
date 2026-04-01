"""논문 검색 API 연동 뼈대."""

from __future__ import annotations

from typing import Any


class PaperSearchClient:
    """AI 논문 수집용 API 클라이언트의 공통 진입점.

    수집 담당자는 이 클래스를 기준으로 HF Daily Papers와 arXiv 보강 로직을 구현한다.
    반환 데이터는 이후 MongoDB 원본 저장과 논문 정규화 단계에서 재사용할 수 있어야 한다.
    """

    def fetch_daily_papers(self, date: str) -> list[dict[str, Any]]:
        """HF Daily Papers API에서 날짜별 큐레이션 논문 목록을 가져온다."""
        raise NotImplementedError("HF Daily Papers 연동은 수집 담당자가 구현할 예정입니다.")

    def fetch_arxiv_metadata(self, arxiv_ids: list[str]) -> dict[str, dict[str, Any]]:
        """arXiv API에서 카테고리, PDF 링크, 발행일 등 메타데이터를 보강한다."""
        raise NotImplementedError("arXiv 메타데이터 보강은 수집 담당자가 구현할 예정입니다.")
