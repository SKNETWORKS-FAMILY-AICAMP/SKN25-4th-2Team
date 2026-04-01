from __future__ import annotations

import streamlit as st

from app.components.section_renderer import render_issue_sections
from src.core import IssueDocument


def render_issue_detail(issue: IssueDocument) -> None:
    st.title(issue.title)
    st.caption(f"문서 갱신 시각: {issue.generated_at.strftime('%Y-%m-%d %H:%M')}")
    render_issue_sections(issue)
