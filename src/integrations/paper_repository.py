"""정제 논문 저장 및 조회 계층 뼈대."""

from __future__ import annotations

from typing import Any


class PaperRepository:
    """정제 논문과 논문 청크를 PostgreSQL에 저장하고 조회하는 진입점."""

    def save_paper(self, paper: dict[str, Any]) -> str:
        """정제 논문 1건을 저장하고 arxiv_id를 반환한다."""
        raise NotImplementedError("논문 저장 계층은 저장 담당자가 구현할 예정입니다.")

    def save_paper_chunks(self, arxiv_id: str, chunks: list[dict[str, Any]]) -> None:
        """논문 청크 목록을 저장한다."""
        raise NotImplementedError("논문 청크 저장 계층은 저장 담당자가 구현할 예정입니다.")

    def list_papers_for_topic(self, topic_id: int) -> list[dict[str, Any]]:
        """토픽 문서 생성에 사용할 논문 묶음을 반환한다."""
        raise NotImplementedError("토픽별 논문 조회는 저장 담당자가 구현할 예정입니다.")
