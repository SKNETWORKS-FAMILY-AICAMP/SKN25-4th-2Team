import streamlit as st
import streamlit.components.v1 as components
from src.integrations import PaperRepository
from app.components.navigation import go_detail, go_agent_chat

@st.cache_resource(show_spinner=False)
def _get_paper_repository() -> PaperRepository:
    return PaperRepository()

def show_list_page():
    if st.session_state.get("scroll_top"):
        import time
        components.html(
            f"""
            <script>
                // Streamlit이 동일한 HTML 문자열 캐싱을 방지하기 위해 랜덤 앵커 삽입: {time.time()}
                setTimeout(function() {{
                    const doc = window.parent.document;
                    const wrappers = [
                        doc.querySelector('[data-testid="stAppViewContainer"]'),
                        doc.querySelector('[data-testid="stMain"]'),
                        doc.querySelector('main'),
                        doc.querySelector('.main')
                    ];
                    wrappers.forEach(w => {{
                        if(w && typeof w.scrollTo === 'function') w.scrollTo(0, 0);
                    }});
                    window.parent.scrollTo(0, 0);
                }}, 150);
            </script>
            """,
            height=0,
        )
        st.session_state.scroll_top = False

    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>ArXplore Papers</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 2.5rem;'>HF Daily Papers & arXiv 기반 최신 AI 논문 탐색 플랫폼</p>", unsafe_allow_html=True)

    _, col_search, _ = st.columns([1, 2, 1])
    with col_search:
        search_query = st.text_input(
            "Search or Ask AI",
            placeholder="Search any paper with AI",
            label_visibility="collapsed",
            key="list_search_input",
        )
        if search_query:
            # 위젯 상태를 비워 다음 진입 시 잔존 값으로 인한 재트리거 방지
            del st.session_state["list_search_input"]
            go_agent_chat(initial_query=search_query)
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    col_title, col_sort = st.columns([6, 1])
    with col_title:
        st.subheader("Explore Papers")
    with col_sort:
        sort_by = st.selectbox(
            "Sort by", 
            ["최신순 (Latest)", "추천순 (Upvotes)"], 
            label_visibility="collapsed"
        )
    
    repo = _get_paper_repository()
    try:
        papers = repo.list_recent_papers(limit=1500)
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {e}")
        return

    if not papers:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container(border=True):
                st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>아직 수집된 논문이 없습니다</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: gray;'>데이터베이스가 비어 있습니다. 파이프라인 수집기를 먼저 실행하여 논문 데이터를 적재해 주세요.</p>", unsafe_allow_html=True)
        return

    if sort_by == "추천순 (Upvotes)":
        papers.sort(key=lambda x: x.get("upvotes", 0) or 0, reverse=True)
        
    items_per_page = 21
    total_pages = max(1, (len(papers) - 1) // items_per_page + 1)
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
        
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    display_papers = papers[start_idx:end_idx]

    cols = st.columns(3)
    for idx, paper in enumerate(display_papers):
        with cols[idx % 3]:
            with st.container(border=True, height=280):
                pdf_link = paper.get("pdf_url") or f"https://arxiv.org/abs/{paper['arxiv_id']}"
                
                short_title = paper['title'][:65] + "..." if len(paper['title']) > 65 else paper['title']
                st.markdown(f"**[{short_title}]({pdf_link})**")
                
                abstract = paper.get("abstract", "")
                preview = abstract[:150] + "..." if len(abstract) > 150 else abstract
                st.markdown(f"<p style='font-size: 0.9em; color: #555; height: 70px; overflow: hidden; margin-bottom: 5px;'>{preview}</p>", unsafe_allow_html=True)
                
                authors_str = ", ".join(paper.get("authors", []))
                if len(authors_str) > 40:
                    authors_str = authors_str[:37] + "..."
                    
                pub_date = paper.get("published_at", "Unknown date")
                if "T" in str(pub_date):
                    pub_date = str(pub_date).split("T")[0]
                
                upvotes = paper.get("upvotes", 0) or 0
                st.markdown(f"<div style='font-size: 0.85em; color: gray; margin-bottom: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{authors_str}<br>📅 {pub_date} &nbsp;•&nbsp; ❤️ {upvotes}</div>", unsafe_allow_html=True)
                
                st.button(
                    "상세 보기", 
                    key=f"btn_{paper['arxiv_id']}", 
                    on_click=go_detail, 
                    args=(paper["arxiv_id"],), 
                    use_container_width=True
                )

    st.markdown("<br>", unsafe_allow_html=True)
    _, pj_prev, p_prev, p_mid, p_next, pj_next, _ = st.columns([4, 1.4, 1, 1.2, 1, 1.4, 4])

    def go_prev():
        st.session_state.current_page = max(1, st.session_state.current_page - 1)
        st.session_state.scroll_top = True
    def go_next():
        st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
        st.session_state.scroll_top = True
    def jump_prev_10():
        st.session_state.current_page = max(1, st.session_state.current_page - 10)
        st.session_state.scroll_top = True
    def jump_next_10():
        st.session_state.current_page = min(total_pages, st.session_state.current_page + 10)
        st.session_state.scroll_top = True

    cur = st.session_state.current_page
    with pj_prev:
        st.button("이전 10페이지", on_click=jump_prev_10, disabled=(cur == 1), use_container_width=True)
    with p_prev:
        st.button("이전", on_click=go_prev, disabled=(cur == 1), use_container_width=True)
    with p_mid:
        st.markdown(f"<p style='text-align: center; line-height: 2.5;'>{cur} / {total_pages}</p>", unsafe_allow_html=True)
    with p_next:
        st.button("다음", on_click=go_next, disabled=(cur >= total_pages), use_container_width=True)
    with pj_next:
        st.button("다음 10페이지", on_click=jump_next_10, disabled=(cur >= total_pages), use_container_width=True)
