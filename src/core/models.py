from __future__ import annotations

"""Newspedia 공용 문서 계약 모델.

이 파일의 모델은 UI, pipeline, 저장 계층, LLM 체인이 함께 의존하는 공용 계약입니다.
특히 `IssueDocument`의 필드 이름, 타입, 의미는 팀 합의 없이 임의로 변경하면 안 됩니다.

변경이 필요한 경우에는 아래 항목을 함께 검토해야 합니다.
1. docs/AGENTS.md
2. docs/PLAN.md
3. docs/ARCHITECTURE.md
4. docs/ROLES.md
5. docs/WORKFLOW.md
6. app/, src/pipeline/, 저장 계층 코드
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    article_id: int
    title: str
    publisher: str
    url: str
    published_at: datetime | None = None


class RelatedIssue(BaseModel):
    issue_id: int
    title: str


class IssueDocument(BaseModel):
    """이슈 문서 공용 계약.

    이 모델은 팀 전체의 고정 인터페이스입니다.
    AI 도구를 활용한 구현 과정에서도 임의로 필드를 추가, 삭제, 이름 변경하지 않도록 유지합니다.
    """

    issue_id: int
    title: str
    overview: str
    background: str
    key_facts: list[str] = Field(default_factory=list)
    source_articles: list[SourceRef] = Field(default_factory=list)
    related_issues: list[RelatedIssue] = Field(default_factory=list)
    generated_at: datetime
