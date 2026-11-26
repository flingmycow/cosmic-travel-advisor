import streamlit as st
import pandas as pd
from services.adk_bridge import AdkService
from utils.custom_func import extract_json_from_text


def _extract_lat_lon(data):
    """Extract (lat, lon) from flat or nested JSON regardless of lng/lon/longitude naming."""
    if isinstance(data, list) and data:
        return _extract_lat_lon(data[0])
    if not isinstance(data, dict):
        return None
    lower = {k.lower(): v for k, v in data.items()}
    lat = lower.get("lat", lower.get("latitude"))
    lon = lower.get("lng", lower.get("lon", lower.get("longitude")))
    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon)
        except (TypeError, ValueError):
            return None
    for v in data.values():
        if isinstance(v, (dict, list)):
            found = _extract_lat_lon(v)
            if found:
                return found
    return None


def _normalize_logistics(data):
    """Unwrap nested dicts/lists and map common key aliases to the expected logistics schema."""
    if isinstance(data, list) and data:
        data = data[0]
    if not isinstance(data, dict):
        return None

    # Flatten nested dicts (e.g. {"logistics": {...}} or {"flights": {...}, "weather": {...}})
    flat = {}
    for k, v in data.items():
        if isinstance(v, dict):
            for nk, nv in v.items():
                if not isinstance(nv, (dict, list)):
                    flat[nk.lower()] = nv
        elif not isinstance(v, list):
            flat[k.lower()] = v

    aliases = {
        "cost": ["cost", "flight_cost", "avg_flight_cost", "average_flight_cost", "price"],
        "duration": ["duration", "flight_duration", "travel_time"],
        "current_date_time": ["current_date_time", "current_time", "local_time", "date_time", "datetime"],
        "current_temp": ["current_temp", "current_temperature", "temp", "temperature"],
        "current_rain": ["current_rain", "current_rain_chance", "rain_chance", "rain", "precipitation"],
        "best_time_to_visit": ["best_time_to_visit", "best_time", "best_season"],
        "best_time_avg_temp": ["best_time_avg_temp", "seasonal_avg_temp", "best_time_temp"],
        "best_time_rain_chance": ["best_time_rain_chance", "seasonal_rain_risk", "best_time_rain"],
        "flight_summary": ["flight_summary", "summary", "airlines", "routes"],
    }

    normalized = {}
    for canonical, candidates in aliases.items():
        for key in candidates:
            if key in flat and flat[key] not in (None, ""):
                normalized[canonical] = flat[key]
                break

    return normalized or None


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
        prompt = f"Get the lat and lng coordinates for the city {city['name']}. Return JSON with keys 'lat' and 'lng'."
        with st.spinner(f"Locating {city['name']}..."):
            success = AdkService.send_message(prompt, isolated=True)

        if success:
            last_msg = extract_json_from_text(st.session_state.messages[-1]['content'])
            coords = _extract_lat_lon(last_msg)
            if coords:
                st.session_state.selected_city['pois'] = [
                    {'lat': coords[0], 'lon': coords[1], 'name': city['name']}
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
                # The Coordinator will see 'flight' and 'weather' and route to 'high_level_travel_agent'
                prompt = (
                    f"Get flight cost, duration, current weather, local time, and best time to visit "
                    f"for {city['name']} from London. Return flat JSON with keys: cost, duration, "
                    f"current_date_time, current_temp, current_rain, best_time_to_visit, "
                    f"best_time_avg_temp, best_time_rain_chance, flight_summary."
                )

                # Assuming AdkService handles the chat interaction
                success = AdkService.send_message(prompt, isolated=True)

                # 2. Extract the JSON from the last message
                new_data = None
                if success:
                    last_msg_content = st.session_state.messages[-1]['content']
                    new_data = _normalize_logistics(extract_json_from_text(last_msg_content))

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