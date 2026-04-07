import os
import streamlit as st
from src.core import PaperDetailDocument, analyze_paper_detail, build_summary, stream_answer_question
from src.integrations import PaperRepository
from app.components.navigation import go_list

@st.cache_resource(show_spinner=False)
def _get_paper_repository() -> PaperRepository:
    return PaperRepository()

def _load_paper_from_db(arxiv_id: str) -> dict | None:
    repository = _get_paper_repository()
    paper = repository.get_paper(arxiv_id)
    if not paper:
        return None

    fulltext = repository.get_paper_fulltext(arxiv_id) or {}
    chunks = repository.list_paper_chunks(arxiv_id, limit=20)

    merged = dict(paper)
    if fulltext:
        merged["fulltext"] = fulltext
        merged["text"] = fulltext.get("text") or ""
        merged["sections"] = fulltext.get("sections") or []
    else:
        merged["text"] = ""
        merged["sections"] = []
    merged["chunks"] = chunks
    return merged


@st.fragment
def _render_chat_panel(paper: dict, arxiv_id: str) -> None:
    chat_key = f"chat_{arxiv_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {"role": "assistant", "content": "이 논문에 대해 궁금한 점을 편하게 물어보세요!"}
        ]

    col_chat_title, col_chat_clear = st.columns([3, 1])
    with col_chat_title:
        st.markdown("### Ask AI")
    with col_chat_clear:
        if st.button("Clear", key=f"clear_{arxiv_id}", use_container_width=True):
            st.session_state[chat_key] = [
                {"role": "assistant", "content": "이 논문에 대해 궁금한 점을 편하게 물어보세요!"}
            ]
            st.rerun()

    pending_key = f"chat_pending_{arxiv_id}"

    chat_container = st.container(border=True, height=600)
    with chat_container:
        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        pending_prompt = st.session_state.get(pending_key)
        if pending_prompt:
            with st.chat_message("assistant"):
                context_chunks = list(paper.get("chunks", []))

                top_summary = st.session_state.get("top_summary")
                if isinstance(top_summary, PaperDetailDocument):
                    overview_text = top_summary.overview or ""
                    if top_summary.key_findings:
                        overview_text += "\n\nKey Findings:\n" + "\n".join(
                            f"- {kf}" for kf in top_summary.key_findings
                        )
                    if overview_text.strip():
                        context_chunks.insert(0, {
                            "arxiv_id": paper.get("arxiv_id"),
                            "title": paper.get("title"),
                            "chunk_text": overview_text,
                            "section_title": "AI Overview & Key Findings",
                        })

                detailed_text = st.session_state.get("summary")
                if detailed_text:
                    context_chunks.insert(0, {
                        "arxiv_id": paper.get("arxiv_id"),
                        "title": paper.get("title"),
                        "chunk_text": detailed_text,
                        "section_title": "Detailed Summary",
                    })

                try:
                    chat_history = [
                        (m["role"], m["content"])
                        for m in st.session_state[chat_key][:-1]
                        if m["role"] in ["user", "assistant"]
                    ]
                    answer_stream = stream_answer_question(
                        pending_prompt,
                        context_papers=context_chunks,
                        chat_history=chat_history,
                    )
                    answer = st.write_stream(answer_stream)
                    st.session_state[chat_key].append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"답변 중 오류 발생: {e}")
                    st.session_state[chat_key].append({"role": "assistant", "content": f"오류: {e}"})

            del st.session_state[pending_key]
            st.rerun(scope="fragment")

    if prompt := st.chat_input("이 논문에 대해 질문하기...", key=f"chat_input_{arxiv_id}"):
        st.session_state[chat_key].append({"role": "user", "content": prompt})
        st.session_state[pending_key] = prompt
        st.rerun(scope="fragment")


def _render_paper_content(paper: dict, has_api_key: bool) -> None:
    pdf_link = paper.get("pdf_url") or f"https://arxiv.org/abs/{paper['arxiv_id']}"
    authors_str = ", ".join(paper.get("authors", []))

    st.markdown(
        f"<h1 style='margin-bottom: 0.5rem;'>{paper['title']}</h1>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(f"**Authors:** {authors_str}")

    st.divider()

    detailed_text = st.session_state.get("summary")
    detailed_error = st.session_state.pop("summary_error", None)

    col_h, col_detail, col_pdf = st.columns([5, 1.8, 1.5], gap="small")
    with col_h:
        st.markdown("### AI Overview & Key Findings")
    with col_detail:
        st.markdown("<div style='padding-top: 0.45rem;'></div>", unsafe_allow_html=True)
        if not detailed_text:
            if st.button("📝 상세요약 생성하기", key="generate_detailed_btn", use_container_width=True):
                if not has_api_key:
                    st.session_state["summary_error"] = "OPENAI_API_KEY가 없어 실행할 수 없습니다."
                    st.rerun()
                else:
                    st.session_state["__summary_pending"] = True
                    st.rerun()
    with col_pdf:
        st.markdown("<div style='padding-top: 0.45rem;'></div>", unsafe_allow_html=True)
        st.link_button("📄 PDF 보기", pdf_link, use_container_width=True)

    if detailed_error:
        st.error(f"상세 요약 생성 실패: {detailed_error}")

    if not has_api_key:
        st.warning("OPENAI_API_KEY가 설정되어 있지 않아 분석을 생략합니다.")
        st.markdown("**Abstract**")
        st.write(paper.get("abstract"))
    else:
        summary_doc = st.session_state.get("top_summary")
        error_msg = st.session_state.pop("top_summary_error", None)
        if error_msg:
            st.error(f"요약 중 에러 발생: {error_msg}")
        if isinstance(summary_doc, PaperDetailDocument):
            with st.container(border=True):
                st.markdown("#### Overview")
                st.write(summary_doc.overview)

                if summary_doc.key_findings:
                    st.divider()
                    st.markdown("#### Key Findings")
                    for finding in summary_doc.key_findings:
                        st.markdown(f"- {finding}")
        elif summary_doc is None and not error_msg:
            st.info("요약을 생성하지 못했습니다.")

    if detailed_text:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(detailed_text)


def show_detail_page():
    st.button("← 뒤로 가기", on_click=go_list)

    arxiv_id = st.session_state.get("selected_arxiv_id")
    if not arxiv_id:
        st.warning("선택된 논문이 없습니다.")
        return

    paper = _load_paper_from_db(arxiv_id)
    if not paper:
        st.error("논문 정보를 읽어올 수 없습니다.")
        return

    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))

    def _show_overlay(message: str) -> "st.delta_generator.DeltaGenerator":
        # viewport 전체를 덮는 fixed 오버레이로 Streamlit DOM diff 잔존을 차단한다.
        slot = st.empty()
        slot.markdown(
            f"""
            <div style='position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                        background: #0e1117; z-index: 9999;
                        display: flex; flex-direction: column; align-items: center; justify-content: center;
                        gap: 1rem; color: #fafafa;'>
                <div style='font-size: 1.6rem; font-weight: 600; max-width: 80%; text-align: center;'>
                    {paper['title']}
                </div>
                <div style='font-size: 1rem; opacity: 0.85;'>{message}</div>
                <div style='width: 32px; height: 32px; border: 3px solid rgba(255,255,255,0.2);
                            border-top-color: #ff4b4b; border-radius: 50%;
                            animation: arxplore-spin 1s linear infinite;'></div>
            </div>
            <style>
                @keyframes arxplore-spin {{ to {{ transform: rotate(360deg); }} }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        return slot

    if has_api_key and "top_summary" not in st.session_state:
        overlay = _show_overlay("AI가 실시간으로 논문을 분석하고 있습니다...")
        try:
            summary_doc = analyze_paper_detail(paper)
            st.session_state["top_summary"] = summary_doc
        except Exception as e:
            st.session_state["top_summary"] = None
            st.session_state["top_summary_error"] = str(e)
        overlay.empty()

    if st.session_state.pop("__summary_pending", False) and has_api_key:
        overlay = _show_overlay("상세 요약을 생성하고 있습니다...")
        try:
            summary_text = paper.get("text") or "\n\n".join(
                f"[{s['title']}]\n{s['text']}" for s in paper.get("sections", [])
            )
            detailed = build_summary(
                title=paper["title"],
                authors=paper["authors"],
                text=summary_text,
                sections=paper.get("sections"),
            )
            st.session_state["summary"] = detailed
        except Exception as e:
            st.session_state["summary_error"] = str(e)
        overlay.empty()

    # 우측 채팅 column을 sticky로 만들어 스크롤 시 따라오게 한다 (첫 번째 horizontal block의 2번째 column 타겟).
    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"]:nth-child(2)) > div[data-testid="stColumn"]:nth-child(2) {
            position: sticky;
            top: 1rem;
            align-self: flex-start;
            max-height: calc(100vh - 2rem);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_main, col_chat = st.columns([3, 2], gap="large")

    with col_main:
        _render_paper_content(paper, has_api_key)

    with col_chat:
        _render_chat_panel(paper, arxiv_id)
