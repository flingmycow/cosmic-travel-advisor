import streamlit as st
from services.adk_bridge import AdkService # these imports are fine when using streamlit run
from utils.app_data import get_western_sign, get_chinese_zodiac

def setup_page():
    st.set_page_config(page_title="Cosmic Travel Agent", page_icon="🌌", layout="wide")

def render_sidebar():
    with st.sidebar:
        st.header("Session Management")

        # Check if session exists
        if st.session_state.get("session_id"):
            st.success(f"Active: {st.session_state.session_id}")

            # Button to reset/start new
            if st.button("➕ New Session"):
                AdkService.create_session()
                st.rerun()  # force refresh
        else:
            st.warning("No active session")

            # Button to create initial session
            if st.button("➕ Create Session"):
                AdkService.create_session()
                st.rerun()

        st.divider()
        # Date calculator logic
        with st.expander("🔍 Find your signs"):
            bday = st.date_input("Your Birthday", value=None, min_value=None, max_value=None)
            if bday:
                w = get_western_sign(bday.month, bday.day)
                c = get_chinese_zodiac(bday.year)
                st.markdown(f"* **Western:** {w}\n* **Chinese:** {c}")
                if st.button("Use these signs"):
                    st.session_state.auto_western = w
                    st.session_state.auto_chinese = c
                    st.rerun()

def apply_custom_theme(sign, zodiac_colours):
    """Injects CSS based on the sign color"""
    color = zodiac_colours.get(sign, "#0E1117")
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {color}22; }}
        div.stButton > button:first-child {{ background-color: {color}; color: white; border: none; }}
    </style>
    """, unsafe_allow_html=True)