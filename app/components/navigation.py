import streamlit as st


def go_detail(arxiv_id: str):
    st.session_state.view_mode = "detail"
    st.session_state.selected_arxiv_id = arxiv_id


def go_list():
    st.session_state.view_mode = "list"
    st.session_state.selected_arxiv_id = None

    if "top_summary" in st.session_state:
        del st.session_state["top_summary"]
    if "summary" in st.session_state:
        del st.session_state["summary"]


def go_agent_chat(initial_query: str = None):
    st.session_state.view_mode = "agent_chat"

    if "agent_chat_history" not in st.session_state:
        st.session_state["agent_chat_history"] = []

    if initial_query:
        # 답변 생성은 채팅 페이지 렌더링 시점에 트리거되도록 플래그만 세팅한다.
        st.session_state["agent_pending_query"] = initial_query
