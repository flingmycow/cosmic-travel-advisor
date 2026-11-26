from utils.app_data import horoscopes, chinese_zodiac, zodiac_colours, get_chinese_zodiac, get_western_sign
from utils.custom_func import extract_json_from_text, parse_ai_response
import streamlit as st
import requests
import json
import os
import re
import uuid
import datetime
import time

# set streamlit page config
st.set_page_config(
    page_title="Cosmic Travel Agent",
    page_icon="🌌",
    layout="centered"
)

# Constants
API_BASE_URL = "http://localhost:8000"
APP_NAME="travel_agent"
min_date = datetime.date(1900, 1, 1)
max_date = datetime.date.today()

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "auto_western" not in st.session_state:
    st.session_state.auto_western = "None"

if "auto_chinese" not in st.session_state:
    st.session_state.auto_chinese = "None"

def create_session():
    """
    Create a new session with the speaker agent.

    This function:
    1. Generates a unique session ID based on timestamp
    2. Sends a POST request to the ADK API to create a session
    3. Updates the session state variables if successful

    Returns:
        bool: True if session was created successfully, False otherwise

    API Endpoint:
        POST /apps/{app_name}/users/{user_id}/sessions/{session_id}
    """
    session_id = f"session-{int(time.time())}"
    response = requests.post(
        f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({})
    )

    if response.status_code == 200:
        st.session_state.session_id = session_id
        st.session_state.messages = []
        return True
    else:
        st.error(f"Failed to create session: {response.text}")
        return False

def send_message(message):
    """
    Send a message to the speaker agent and process the response.

    This function:
    1. Adds the user message to the chat history
    2. Sends the message to the ADK API

    Args:
        message (str): The user's message to send to the agent

    Returns:
        bool: True if message was sent and processed successfully, False otherwise

    API Endpoint:
        POST /run

    Response Processing:
        - Parses the ADK event structure to extract text responses
    """
    if not st.session_state.session_id:
        st.error("No active session. Please create a session first.")
        return False

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})

    # Send message to API
    response = requests.post(
        f"{API_BASE_URL}/run",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        })
    )

    if response.status_code != 200:
        st.error(f"Error: {response.text}")
        return False

    # Process the response
    events = response.json()
    print(f"events = {events}")

    # Extract assistant's text response
    assistant_message = None
    audio_file_path = None

    for event in events:
        # Look for the final text response from the model
        if event.get("content", {}).get("role") == "model" and "text" in event.get("content", {}).get("parts", [{}])[0]:
            assistant_message = event["content"]["parts"][0]["text"]

        # Look for text_to_speech function response to extract audio file path
        if "functionResponse" in event.get("content", {}).get("parts", [{}])[0]:
            func_response = event["content"]["parts"][0]["functionResponse"]

    # Add assistant response to chat
    if assistant_message:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message, "audio_path": audio_file_path})

    return True

def apply_custom_theme(sign):
    color = zodiac_colours.get(sign, "#0E1117")

    custom_css = f"""
    <style>
        /* Change the primary background color of the main area */
        .stApp {{
            background-color: {color}22; /* 22 adds transparency so text stays readable */
        }}
        
        /* Change the color of all Primary Buttons */
        div.stButton > button:first-child {{
            background-color: {color};
            color: white;
            border: none;
        }}

        /* Change the color of headers */
        h1, h2, h3, h4 {{
            color: {color} !important;
        }}

        /* Change the border color of containers/cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: {color} !important;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# UI Components
st.title("🔮 Cosmic Travel Agent")

# Sidebar for session management
with st.sidebar:
    st.header("Session Management")

    if st.session_state.session_id:
        st.success(f"Active session: {st.session_state.session_id}")
        if st.button("➕ New Session"):
            create_session()
    else:
        st.warning("No active session")
        if st.button("➕ Create Session"):
            create_session()

    st.divider()
    with st.expander("🔍 Don't know your signs? Find them here!"):
        st.write("Enter your birthday to find your celestial markers.")

        # 1. Western Sign Finder
        bday = st.date_input("Your Birthday", value=None, min_value=min_date, max_value=max_date)
        if bday:
            w_sign = get_western_sign(bday.month, bday.day)
            c_sign = get_chinese_zodiac(bday.year)

            st.markdown(f"""
            * **Western Sign:** {w_sign}
            * **Chinese Zodiac:** {c_sign}
            """)

            # Optional: A button to automatically fill the boxes
            if st.button("Use these signs"):
                st.session_state.auto_western = w_sign
                st.session_state.auto_chinese = c_sign
                st.rerun()

    st.divider()
    st.caption("This app interacts with the Speaker Agent via the ADK API Server.")
    st.caption("Make sure the ADK API Server is running on port 8000.")

# Chat interface
st.subheader("Conversation")
st.markdown("Choose your Western Horoscope, a specific Decan, or your Chinese Zodiac.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Western Astrology")
    w_options = ["None"] + list(horoscopes.keys())
    # Added "None" as the first option so nothing is selected by default
    selected_sign = st.selectbox(
        "Select Sign",
        options=["None"] + list(horoscopes.keys()),
        index=w_options.index(st.session_state.auto_western))

    # Decan selection logic
    if selected_sign != "None":
        selected_decan = st.selectbox(
            "Select Variant (Decan)",
            options=horoscopes[selected_sign]
        )
        apply_custom_theme(selected_sign)

    else:
        # If no sign is picked, we show a placeholder for the decan box
        st.selectbox("Select Variant (Decan)", options=["N/A"], disabled=True)
        selected_decan = "None"

with col2:
    st.subheader("Eastern Astrology")
    c_options = ["None"] + chinese_zodiac
    # Added "None" as the first option
    selected_chinese = st.selectbox(
        "Select Chinese Zodiac",
        options=["None"] + chinese_zodiac,
        index=c_options.index(st.session_state.auto_chinese)
    )

st.write("---")

# --- 2. Update the Submit Logic ---
if st.button("Submit Selections", type="primary"):
    results = {
        "western_sign": None if selected_sign == "None" else selected_sign,
        "decan_variant": None if "General" in selected_decan or selected_decan in ["None", "N/A"] else selected_decan,
        "chinese_zodiac": None if selected_chinese == "None" else selected_chinese
    }

    if all(v is None for v in results.values()):
        st.warning("You haven't selected any zodiac information.")
    else:
        # 1. Create message string
        selections = []
        if results['western_sign']:
            selections.append(f"{results['western_sign']} ({results['decan_variant'] or 'General'})")
        if results['chinese_zodiac']:
            selections.append(f"the Year of the {results['chinese_zodiac']}")

        prompt = f"Plan a trip for someone with these signs: {' & '.join(selections)}"

        # 2. Send to API
        with st.spinner("Consulting the stars..."):
            success = send_message(prompt)
            if success:
                # We don't rerun manually here yet; let the script finish
                # or the state update will trigger the view.
                pass

# --- 3. Dynamic Rendering Logic (Place this AFTER the button block) ---
# --- In your UI Rendering section ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_response = st.session_state.messages[-1]["content"]
    print(last_response)
    data = extract_json_from_text(last_response)

    if data:
        st.header("🌟 Your Celestial Journey")
        st.info(data["summary"])

        # Create Grid
        dest_list = data["destinations"]
        cols = st.columns(2)
        for idx, dest in enumerate(dest_list):
            with cols[idx % 2]:
                with st.container(border=True):
                    # 1. Clean the city name for the URL (Remove spaces)
                    city_only = dest['name'].split(',')[0].strip().replace(" ", "")

                    # 2. Add a random seed so duplicate cities get different photos
                    img_url = f"https://loremflickr.com/400/250/{city_only}?random={idx}"

                    # 3. Use the correct parameter for sizing
                    st.image(img_url, width=True)

                    st.subheader(f"📍 {dest['name']}")
                    st.write(dest['description'])

        # Final Pick
        rec = data["recommendation"]
        st.success(f"### 👑 Our Top Pick: {rec['city']}")
        st.write(f"**Rationale:** {rec['rationale']}")
