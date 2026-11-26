import streamlit as st
import pandas as pd
from services.adk_bridge import AdkService
from utils.custom_func import extract_json_from_text

def render_detail_view():
    city = st.session_state.get("selected_city")

    if not city:
        st.session_state.selected_city = None
        st.rerun()
        return

    # 1. Navigation: Back Button
    if st.button("← Back to Results"):
        st.session_state.selected_city = None
        st.rerun()

    st.title(f"🌍 Deep Dive: {city['name']}")

    # --- SECTION 1: MAP & POIS ---
    st.header(f"📍 Exploring {city['name']}", divider=True)


    show_map = st.button("Show Map")
    if show_map:
        prompt = f"Get the lat lon for the city {city['name']}"
        with st.spinner(f"Locating {city['name']}..."):
            success = AdkService.send_message(prompt)

        if success:
            last_msg = extract_json_from_text(st.session_state.messages[-1]['content'])
            if last_msg and 'lat' in last_msg and 'lng' in last_msg:
                st.session_state.selected_city['pois'] = [
                    {'lat': float(last_msg['lat']), 'lon': float(last_msg['lng']), 'name': city['name']}
                ]
            else:
                st.error("Could not parse coordinates for this city.")

    if city.get('pois'):
        map_data = pd.DataFrame(city['pois'])
        # Streamlit Map
        st.map(map_data, latitude='lat', longitude='lon', size=15, color='#FF4B4B')

    # --- SECTION 2: FLIGHTS & WEATHER ---
    st.divider()
    st.header("✈️ Logistics from London", divider=True)

    # Check if we already have the data to avoid re-fetching on every rerun
    has_logistics = "cost" in city.get('logistics', {})

    # Show button only if we don't have data yet
    if not has_logistics:
        if st.button("Get Live Logistics Info"):
            with st.spinner(f"Searching flights and weather for {city['name']}..."):
                # 1. Send specific instruction to Coordinator
                # The Coordinator will see 'flight' and 'weather' and route to 'logistics_specialist'
                prompt = f"Get flight cost, duration, and current weather for {city['name']} from London. Return JSON."

                # Assuming AdkService handles the chat interaction
                success = AdkService.send_message(prompt)

                # 2. Extract the JSON from the last message
                new_data = None
                if success:
                    last_msg_content = st.session_state.messages[-1]['content']
                    new_data = extract_json_from_text(last_msg_content)

                if new_data:
                    # 3. Update the Session State directly
                    # We merge the new data into the existing city object
                    st.session_state.selected_city['logistics'] = new_data
                    st.success("Updated!")
                    st.rerun() # <--- Force reload to display the metrics below
                else:
                    st.error("Could not retrieve logistics data.")

    # Display Metrics
    stats = st.session_state.selected_city.get('logistics', {})

    # ROW 1: Logistics & Live Weather
    st.subheader("✈️ Flight & Current Conditions")
    m1, m2 = st.columns(2)
    m3, m4, m5 = st.columns(3)
    m1.metric("Avg Flight Cost", stats.get('cost', "£---"))
    m2.metric("Duration", stats.get('duration', "-- h"))
    m3.metric("Current Date & Time", stats.get('current_date_time', "--"))
    m4.metric("Temp (Now)", stats.get('current_temp', "--°C"))
    m5.metric("Rain (Now)", stats.get('current_rain', "--%"))

    # ROW 2: Best Time to Visit (New Section)
    if 'best_time_to_visit' in stats:
        st.divider()
        st.subheader(f"🗓️ Best Time to Visit: ", divider=True)
        st.markdown(f"#### {stats.get('best_time_to_visit')} ")
        st.space()

        c1, c2 = st.columns([1, 1])

        c1.metric(
            label="Seasonal Avg Temp",
            value=stats.get('best_time_avg_temp', "--"),
            help=f"Average temperature during {stats.get('best_time_to_visit')}"
        )

        c2.metric(
            label="Seasonal Rain Risk",
            value=stats.get('best_time_rain_chance', "--"),
            help=f"Likelihood of rain during {stats.get('best_time_to_visit')}"
        )

        # Optional: Add a visual cue or advice
        st.info(f"💡 **Tip:** Planning for {stats.get('best_time_to_visit')} usually ensures the best balance of weather and events.")

    # Flight Summary Expander
    if 'flight_summary' in stats:
        with st.expander("See Flight Details"):
            st.write(stats['flight_summary'])

    st.text("TODO: Add function to show real flights")
    st.button("See Real Flights")

    # --- SECTION 3: ACCOMMODATION ---
    st.divider()
    st.write("TODO: Add a button that allows the user to get this info if they want to")
    st.header("🏡 Where to Stay")
    st.caption(f"Curated Airbnb neighborhoods in {city['name']}")

    cols = st.columns(3)
    stays = city.get('stays', [])

    for idx, stay in enumerate(stays):
        with cols[idx % 3]:
            with st.container(border=True):
                st.subheader(stay['name'])
                st.write(stay['description'])
                st.write(f"**Vibe:** {stay['vibe']}")
                st.link_button("Search on Airbnb", f"https://www.airbnb.com/s/{stay['name']}/homes")