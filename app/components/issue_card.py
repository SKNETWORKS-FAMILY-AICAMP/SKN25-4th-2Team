from __future__ import annotations

import streamlit as st

from src.core import IssueDocument


def render_issue_card(issue: IssueDocument) -> None:
    st.subheader(issue.title)
    st.caption(
        f"최근 갱신: {issue.generated_at.strftime('%Y-%m-%d %H:%M')} · "
        f"근거 기사 {len(issue.source_articles)}건"
    )
    st.write(issue.overview)
