import requests
import uuid
import time
import streamlit as st

# Constants
API_BASE_URL = "http://localhost:8000"
APP_NAME = "travel_agent"

class AdkService:
    @staticmethod
    def initialize_state():
        """Setup session state variables if they don't exist"""
        if "user_id" not in st.session_state:
            st.session_state.user_id = f"user-{uuid.uuid4()}"
        if "session_id" not in st.session_state:
            st.session_state.session_id = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "itinerary_data" not in st.session_state:
            st.session_state.itinerary_data = None

    @staticmethod
    def create_session():
        session_id = f"session-{int(time.time())}"
        url = f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}"

        try:
            response = requests.post(url, json={}, headers={"Content-Type": "application/json"}, timeout=10)
            if response.status_code != 200:
                st.error(f"Failed to create ADK session ({response.status_code}): {response.text}")
                return False
            st.session_state.session_id = session_id
            st.session_state.messages = []
            st.session_state.itinerary_data = None
            st.session_state.selected_city = None
            return True
        except Exception as e:
            st.error(f"Failed to connect to ADK: {e}")
            return False

    @staticmethod
    def send_message(message):
        if not st.session_state.session_id:
            st.error("No active session.")
            return False

        # 1. Update UI immediately
        st.session_state.messages.append({"role": "user", "content": message})

        # 2. Prepare Payload
        payload = {
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {"role": "user", "parts": [{"text": message}]}
        }

        try:
            # 3. Call API
            response = requests.post(f"{API_BASE_URL}/run", json=payload, timeout=120)
            if response.status_code != 200:
                st.error(f"API Error: {response.text}")
                return False

            # 4. Process Events
            events = response.json()
            final_text = ""

            for event in events:
                content = event.get("content", {})
                # Grab text from model (iterate parts safely in case of empty parts or thought blocks)
                if content.get("role") == "model":
                    for part in content.get("parts", []):
                        if isinstance(part, dict) and "text" in part:
                            final_text = part["text"]

                # (Optional) Grab audio logic here if you need it back

            if final_text:
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                return True

            st.warning("Agent returned an empty response. Please try again.")
            return False

        except Exception as e:
            st.error(f"Connection Error: {e}")
            return False