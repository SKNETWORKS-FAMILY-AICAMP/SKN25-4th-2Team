"""이슈 및 이슈 문서 저장 계층 뼈대."""

from __future__ import annotations

from src.core.models import IssueDocument


class IssueRepository:
    """이슈 메타데이터와 `IssueDocument`를 저장하고 조회하는 진입점."""

    def save_issue(self, issue_id: int, title: str) -> int:
        """이슈 메타데이터를 저장하고 issue_id를 반환한다."""
        raise NotImplementedError("이슈 메타데이터 저장은 저장 담당자가 구현할 예정입니다.")

    def save_issue_articles(self, issue_id: int, article_ids: list[int]) -> None:
        """이슈와 기사 간 매핑을 저장한다."""
        raise NotImplementedError("이슈-기사 매핑 저장은 저장 담당자가 구현할 예정입니다.")

    def save_issue_document(self, document: IssueDocument) -> int:
        """이슈 문서를 저장하고 issue_id를 반환한다."""
        raise NotImplementedError("이슈 문서 저장은 저장 담당자가 구현할 예정입니다.")

    def get_issue_document(self, issue_id: int) -> IssueDocument | None:
        """단일 이슈 문서를 조회한다."""
        raise NotImplementedError("이슈 문서 조회는 저장 담당자가 구현할 예정입니다.")

    def list_issue_documents(self, *, limit: int = 20) -> list[IssueDocument]:
        """메인 화면 카드 섹션에 사용할 이슈 문서 목록을 조회한다."""
        raise NotImplementedError("이슈 목록 조회는 저장 담당자가 구현할 예정입니다.")
