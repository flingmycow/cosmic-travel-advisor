import streamlit as st
from utils.app_data import horoscopes, chinese_zodiac, zodiac_colours
from utils.custom_func import extract_json_from_text
from services.adk_bridge import AdkService
from ui.layout import setup_page, render_sidebar, apply_custom_theme
from ui.results import render_destination_grid
from ui.city_details import render_detail_view

# 1. Setup
setup_page()
AdkService.initialize_state()
render_sidebar()

# === THE ROUTER ===
# Check if a city is currently selected.
# If YES -> Show ONLY the detail view.
# If NO  -> Show the Search Interface (Inputs + Grid).

if st.session_state.get("selected_city"):
    # --- VIEW A: DEEP DIVE ---
    render_detail_view()

else:
    # --- VIEW B: SEARCH INTERFACE ---
    st.title("🔮 Cosmic Travel Agent")

    # 2. Input Section (Only show this in Search View)
    col1, col2 = st.columns(2)
    with col1:
        default_w = st.session_state.get("auto_western", "None")
        w_index = (["None"] + list(horoscopes.keys())).index(default_w) if default_w in horoscopes else 0

        selected_sign = st.selectbox("Western Sign", ["None"] + list(horoscopes.keys()), index=w_index)

        if selected_sign != "None":
            apply_custom_theme(selected_sign, zodiac_colours)
            selected_decan = st.selectbox("Variant (Decan)", horoscopes[selected_sign])
        else:
            selected_decan = "None"

    with col2:
        default_c = st.session_state.get("auto_chinese", "None")
        c_index = (["None"] + chinese_zodiac).index(default_c) if default_c in chinese_zodiac else 0
        selected_chinese = st.selectbox("Chinese Zodiac", ["None"] + chinese_zodiac, index=c_index)

    # 3. Action
    st.space(size="small")
    if st.button("Submit Selections", type="primary"):
        parts = []
        if selected_sign != "None": parts.append(f"{selected_sign} ({selected_decan})")
        if selected_chinese != "None": parts.append(f"Year of the {selected_chinese}")

        if not parts:
            st.warning("Please select at least one sign.")
        else:
            if not st.session_state.get("session_id"):
                if not AdkService.create_session():
                    st.stop()
            prompt = f"Plan a trip for: {' & '.join(parts)}"
            with st.spinner("Consulting the stars..."):
                success = AdkService.send_message(prompt)
                if success:
                    last_msg = st.session_state.messages[-1]
                    st.session_state.itinerary_data = extract_json_from_text(last_msg["content"])
                    st.rerun()

    # 4. Render Output (Grid)
    # Only render the grid if we are in search mode AND have itinerary data
    if st.session_state.get("itinerary_data"):
        render_destination_grid(st.session_state.itinerary_data)