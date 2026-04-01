from __future__ import annotations

import streamlit as st

from src.core import IssueDocument


def render_issue_sections(issue: IssueDocument) -> None:
    st.markdown("## 목차")
    st.markdown("- [개요](#개요)")
    st.markdown("- [배경](#배경)")
    st.markdown("- [핵심 사실](#핵심-사실)")
    st.markdown("- [근거 기사](#근거-기사)")
    st.markdown("- [관련 이슈](#관련-이슈)")

    st.markdown("## 개요")
    st.write(issue.overview)

    st.markdown("## 배경")
    st.write(issue.background)

    st.markdown("## 핵심 사실")
    if issue.key_facts:
        for fact in issue.key_facts:
            st.markdown(f"- {fact}")
    else:
        st.caption("공통으로 확인된 핵심 사실이 아직 충분하지 않습니다.")

    st.markdown("## 근거 기사")
    for article in issue.source_articles:
        published_at = article.published_at.strftime("%Y-%m-%d %H:%M") if article.published_at else "발행일 미상"
        st.markdown(
            f"- [{article.title}]({article.url}) · {article.publisher} · {published_at}"
        )

    st.markdown("## 관련 이슈")
    if issue.related_issues:
        for related in issue.related_issues:
            st.markdown(f"- {related.title} (`issue_id={related.issue_id}`)")
    else:
        st.caption("연결된 관련 이슈가 아직 없습니다.")
