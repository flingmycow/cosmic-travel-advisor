# frontend/Home.py
import streamlit as st

st.set_page_config(page_title="Cosmic Travel Portal", layout="wide")

st.title("🌌 Cosmic Travel Portal")
st.write("Welcome to the internal tool for Zodiac-based travel planning. "
         "If you want recommendations on your next travel destination then launch the agent!")

col1, col2 = st.columns(2)

with col1:
    st.info("🤖 **For Users** who want travel recommendations")
    if st.button("Launch Agent"):
        st.switch_page("pages/01_🌌_Cosmic_Agent.py")

with col2:
    st.warning("📊 **For Admins** who want to analyze data around travel recommendations")
    if st.button("View Analytics"):
        st.switch_page("pages/02_📊_Data_Insights.py")