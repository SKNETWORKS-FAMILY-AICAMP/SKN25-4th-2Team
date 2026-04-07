import streamlit as st
from app.views import show_list_page, show_detail_page, show_agent_chat_page

st.set_page_config(page_title="ArXplore", layout="wide")

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "list"
    st.session_state.selected_arxiv_id = None

current_view = st.session_state.view_mode

if current_view == "list":
    show_list_page()
elif current_view == "detail":
    show_detail_page()
elif current_view == "agent_chat":
    show_agent_chat_page()
else:
    st.error(f"알 수 없는 화면 모드입니다: {current_view}")
    st.session_state.view_mode = "list"
    st.rerun()
