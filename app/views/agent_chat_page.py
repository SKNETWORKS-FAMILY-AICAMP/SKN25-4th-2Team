import streamlit as st
from src.core import stream_agent_search
from app.components.navigation import go_list

def show_agent_chat_page():
    st.button("← 뒤로가기", on_click=go_list)
    
    st.markdown("## AI 스마트 탐색 비서 (Agent Chat)")
    st.caption("최신 트렌드나 특정 기술 키워드에 대해 자유롭게 질문해 보세요. AI가 논문 DB를 뒤져 스스로 답변합니다.")
    st.divider()

    hist_key = "agent_chat_history"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
        
    chat_container = st.container(height=500, border=True)
    
    with chat_container:
        for msg in st.session_state[hist_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    pending_query = st.session_state.get("agent_pending_query")
    if pending_query:
        st.session_state[hist_key].append({"role": "user", "content": pending_query})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(pending_query)
            with st.chat_message("assistant"):
                with st.spinner("의도를 분석하고 도구를 호출 중입니다..."):
                    try:
                        tuple_history = [(m["role"], m["content"]) for m in st.session_state[hist_key][:-1] if m["role"] in ["user", "assistant"]]
                        answer_stream = stream_agent_search(pending_query, chat_history=tuple_history)
                        answer = st.write_stream(answer_stream)
                        st.session_state[hist_key].append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
                        
        del st.session_state["agent_pending_query"]
        st.rerun()

    if prompt := st.chat_input("에이전트에게 할 질문을 입력하세요..."):
        st.session_state[hist_key].append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("의도를 파악하여 적합한 도구를 사용 중입니다..."):
                    try:
                        tuple_history = [(m["role"], m["content"]) for m in st.session_state[hist_key][:-1] if m["role"] in ["user", "assistant"]]
                        answer_stream = stream_agent_search(prompt, chat_history=tuple_history)
                        answer = st.write_stream(answer_stream)
                        st.session_state[hist_key].append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
