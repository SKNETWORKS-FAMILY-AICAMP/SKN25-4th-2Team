"""벡터 저장 및 검색 계층 뼈대."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class VectorRepository:
    """기사 청크 임베딩 저장과 유사도 검색을 담당하는 진입점."""

    def upsert_article_embeddings(self, rows: list[dict[str, Any]]) -> None:
        """기사 청크와 임베딩 벡터를 저장하거나 갱신한다."""
        raise NotImplementedError("벡터 저장 계층은 저장 담당자가 구현할 예정입니다.")

    def search_article_chunks(
        self,
        query_embedding: Sequence[float],
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """질문 임베딩과 유사한 기사 청크 목록을 반환한다."""
        raise NotImplementedError("벡터 검색 계층은 저장 담당자가 구현할 예정입니다.")
