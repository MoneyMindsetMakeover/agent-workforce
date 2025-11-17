import streamlit as st

def mark_page():
    st.header("MARK - Marketing AI")

    st.markdown("""
    MARK assists with:
    - Marketing automation
    - Email & SMS campaigns
    - Engagement workflows
    - Lead nurturing
    """)

    st.markdown("---")

    user_msg = st.text_input("Ask MARK something:")
    if user_msg:
        with st.chat_message("user"):
            st.write(user_msg)

        with st.chat_message("assistant"):
            st.write("I’m MARK. I'm still learning from CORA’s activity.")

