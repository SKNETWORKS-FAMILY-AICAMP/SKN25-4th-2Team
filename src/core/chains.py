"""이슈 문서 생성 프로토타입 체인 모듈.

현재 구현은 `IssueDocument` 계약을 기준으로 한 초기 프로토타입이다.
실제 저장 계층, 검색 계층, 평가 기준이 정리되면 입력 구조와 호출 방식이 확장될 수 있다.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.shared import get_settings

from .models import IssueDocument, RelatedIssue, SourceRef
from .prompts import BACKGROUND_PROMPT, KEY_FACTS_PROMPT, OVERVIEW_PROMPT
from .tracing import build_analysis_trace_config


def _build_llm() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않아 이슈 문서 생성 체인을 실행할 수 없습니다.")

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )


def _format_articles(articles: List[Dict[str, Any]]) -> str:
    """기사 목록을 프롬프트에 넣을 텍스트로 변환합니다."""
    if not articles:
        raise ValueError("이슈 문서 생성에는 최소 1개 이상의 기사가 필요합니다.")

    parts = []
    for i, article in enumerate(articles, 1):
        title = article.get("title", "제목 없음")
        content = article.get("content", "")
        source = article.get("source", "출처 미상")
        url = article.get("url", "URL 없음")
        published_at = article.get("published_at", "발행일 미상")
        parts.append(
            f"[기사 {i}] {title} ({source})\n"
            f"발행일: {published_at}\n"
            f"URL: {url}\n"
            f"{content}"
        )
    return "\n\n---\n\n".join(parts)


def _extract_key_facts(text: str) -> list[str]:
    facts: list[str] = []
    for line in text.splitlines():
        cleaned = line.strip().lstrip("-*• ").strip()
        if cleaned:
            facts.append(cleaned)
    return facts


def _build_source_refs(articles: List[Dict[str, Any]]) -> list[SourceRef]:
    refs: list[SourceRef] = []
    for index, article in enumerate(articles, 1):
        refs.append(
            SourceRef(
                article_id=article.get("article_id", index),
                title=article.get("title", "제목 없음"),
                publisher=article.get("source", article.get("publisher", "출처 미상")),
                url=article.get("url", ""),
                published_at=article.get("published_at"),
            )
        )
    return refs


def _build_related_issues(related_issues: Optional[List[Dict[str, Any]]]) -> list[RelatedIssue]:
    if not related_issues:
        return []

    return [
        RelatedIssue(
            issue_id=issue["issue_id"],
            title=issue["title"],
        )
        for issue in related_issues
    ]


def build_issue_overview(
    articles: List[Dict[str, Any]],
    *,
    runtime: str = "dev",
    user: Optional[str] = None,
) -> str:
    """이슈 문서의 개요를 생성합니다."""
    chain = OVERVIEW_PROMPT | _build_llm() | StrOutputParser()
    config = build_analysis_trace_config(runtime=runtime, user=user)
    return chain.invoke(
        {"articles": _format_articles(articles)},
        config=config,
    )


def build_issue_background(
    articles: List[Dict[str, Any]],
    *,
    runtime: str = "dev",
    user: Optional[str] = None,
) -> str:
    """이슈 문서의 배경을 생성합니다."""
    chain = BACKGROUND_PROMPT | _build_llm() | StrOutputParser()
    config = build_analysis_trace_config(runtime=runtime, user=user)
    return chain.invoke(
        {"articles": _format_articles(articles)},
        config=config,
    )


def build_issue_key_facts(
    articles: List[Dict[str, Any]],
    *,
    runtime: str = "dev",
    user: Optional[str] = None,
) -> list[str]:
    """이슈 문서의 핵심 사실 목록을 생성합니다."""
    chain = KEY_FACTS_PROMPT | _build_llm() | StrOutputParser()
    config = build_analysis_trace_config(runtime=runtime, user=user)
    response = chain.invoke(
        {"articles": _format_articles(articles)},
        config=config,
    )
    return _extract_key_facts(response)


def analyze_issue(
    issue_id: int,
    title: str,
    articles: List[Dict[str, Any]],
    *,
    related_issues: Optional[List[Dict[str, Any]]] = None,
    generated_at: Optional[datetime] = None,
    runtime: str = "dev",
    user: Optional[str] = None,
) -> IssueDocument:
    """이슈 전체를 문서 형태로 생성합니다."""
    return IssueDocument(
        issue_id=issue_id,
        title=title,
        overview=build_issue_overview(articles, runtime=runtime, user=user),
        background=build_issue_background(articles, runtime=runtime, user=user),
        key_facts=build_issue_key_facts(articles, runtime=runtime, user=user),
        source_articles=_build_source_refs(articles),
        related_issues=_build_related_issues(related_issues),
        generated_at=generated_at or datetime.now(timezone.utc),
    )
