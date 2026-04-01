from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.components.issue_card import render_issue_card
from app.pages.issue_detail import render_issue_detail
from src.core import IssueDocument, RelatedIssue, SourceRef

st.set_page_config(page_title="Newspedia", layout="wide")


def _load_demo_issues() -> list[IssueDocument]:
    return [
        IssueDocument(
            issue_id=1,
            title="국내 AI 반도체 스타트업, 신규 추론 칩 공개",
            overview=(
                "국내 AI 반도체 스타트업이 신규 추론 칩을 공개하며 데이터센터와 온디바이스 "
                "시장 동시 진입 전략을 내놨다. 발표 기사들은 성능 수치와 고객사 확보 여부를 "
                "집중적으로 다뤘고, 업계 반응은 국산 대체재 가능성에 주목했다."
            ),
            background=(
                "생성형 AI 서비스 확산으로 추론 전용 칩 수요가 빠르게 증가하고 있다. "
                "[일반 배경 정보] GPU 중심 시장에서 전력 효율과 가격 경쟁력을 앞세운 "
                "전용 반도체 수요가 커지고 있다."
            ),
            key_facts=[
                "회사는 신규 추론 칩의 정식 제품명을 공개했다.",
                "양산 시점과 초기 고객사 확보 계획이 기사 전반에서 공통으로 언급됐다.",
                "전력 효율 개선 수치가 여러 기사에서 핵심 근거로 제시됐다.",
            ],
            source_articles=[
                SourceRef(
                    article_id=101,
                    title="AI 반도체 스타트업, 추론 칩 공개",
                    publisher="테크데일리",
                    url="https://example.com/article-101",
                    published_at=datetime(2026, 3, 31, 9, 0),
                ),
                SourceRef(
                    article_id=102,
                    title="국산 추론 칩 시장 진입 본격화",
                    publisher="IT뉴스",
                    url="https://example.com/article-102",
                    published_at=datetime(2026, 3, 31, 10, 30),
                ),
            ],
            related_issues=[
                RelatedIssue(issue_id=2, title="클라우드 사업자, AI 인프라 투자 확대"),
                RelatedIssue(issue_id=3, title="국내 반도체 설계 인력 확보 경쟁 심화"),
            ],
            generated_at=datetime(2026, 3, 31, 12, 0),
        )
    ]


issues = _load_demo_issues()

st.title("Newspedia")
st.caption("최근 이슈를 문서 단위로 읽고, 근거 기사와 함께 맥락을 빠르게 파악하는 베타 UI")

issue_map = {issue.title: issue for issue in issues}
selected_title = st.sidebar.selectbox("이슈 선택", list(issue_map.keys()))
selected_issue = issue_map[selected_title]

st.markdown("## 이슈 카드")
for issue in issues:
    with st.container(border=True):
        render_issue_card(issue)

st.divider()
render_issue_detail(selected_issue)
