"""한국어 번역 및 상세 요약 체인을 담당하는 모듈"""

from __future__ import annotations

from typing import Any, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from src.shared import get_settings

from .prompts import DETAILED_SUMMARY_PROMPT, TRANSLATION_PROMPT
from .tracing import build_detailed_summary_trace_config, build_translation_trace_config


def _build_llm() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않아 한국어 번역/요약 체인을 실행할 수 없습니다.")

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )


def _format_authors(authors: Any) -> str:
    if not authors:
        return "저자 미상"
    if isinstance(authors, str):
        return authors.strip() or "저자 미상"

    names: list[str] = []
    if isinstance(authors, list):
        for author in authors:
            if isinstance(author, str):
                author_name = author.strip()
                if author_name:
                    names.append(author_name)
                continue
            if isinstance(author, dict):
                author_name = str(author.get("name") or "").strip()
                if author_name:
                    names.append(author_name)
    return ", ".join(names) or "저자 미상"


def translate_chunk(
    chunk_text: str,
    *,
    runtime: str = "dev",
    user: Optional[str] = None,
    quality_score: float | None = None,
) -> str:
    chain = TRANSLATION_PROMPT | _build_llm() | StrOutputParser()
    config = build_translation_trace_config(
        runtime=runtime,
        user=user,
        quality_score=quality_score,
    )
    return chain.invoke(
        {"chunk_text": str(chunk_text or "")},
        config=config,
    )


def build_detailed_summary(
    *,
    title: str,
    authors: Any,
    text: str,
    runtime: str = "dev",
    user: Optional[str] = None,
    quality_score: float | None = None,
) -> str:
    chain = DETAILED_SUMMARY_PROMPT | _build_llm() | StrOutputParser()
    config = build_detailed_summary_trace_config(
        runtime=runtime,
        user=user,
        quality_score=quality_score,
    )
    return chain.invoke(
        {
            "title": title or "제목 없음",
            "authors": _format_authors(authors),
            "text": str(text or ""),
        },
        config=config,
    )
