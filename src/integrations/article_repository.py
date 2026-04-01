"""정제 기사 저장 및 조회 계층 뼈대."""

from __future__ import annotations

from typing import Any


class ArticleRepository:
    """정제 기사와 기사 청크를 PostgreSQL에 저장하고 조회하는 진입점."""

    def save_article(self, article: dict[str, Any]) -> int:
        """정제 기사 1건을 저장하고 article_id를 반환한다."""
        raise NotImplementedError("기사 저장 계층은 저장 담당자가 구현할 예정입니다.")

    def save_article_chunks(self, article_id: int, chunks: list[dict[str, Any]]) -> None:
        """기사 청크 목록을 저장한다."""
        raise NotImplementedError("기사 청크 저장 계층은 저장 담당자가 구현할 예정입니다.")

    def list_articles_for_issue(self, issue_id: int) -> list[dict[str, Any]]:
        """이슈 문서 생성에 사용할 기사 묶음을 반환한다."""
        raise NotImplementedError("이슈별 기사 조회는 저장 담당자가 구현할 예정입니다.")
