import streamlit as st
import requests
import urllib.parse  # Import this to handle URL spaces safely


@st.cache_data(show_spinner=False)
def get_city_image(city_name: str, fallback_idx: int) -> str:
    """Fetch a real city thumbnail from Wikipedia (no API key needed), with a Picsum fallback."""
    city = city_name.split(",")[0].strip()
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(city)}"
        resp = requests.get(url, headers={"User-Agent": "CosmicTravelAgent/1.0"}, timeout=5)
        if resp.status_code == 200:
            thumb = resp.json().get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass
    city_slug = urllib.parse.quote(city.replace(" ", ""))
    return f"https://picsum.photos/seed/{city_slug}{fallback_idx}/400/250"


def render_destination_grid(data):
    if not data: return

    st.divider()
    st.header("🌟 Your Celestial Journey")
    st.info(data.get("summary", "Analysis complete."))

    # Destination Grid
    dest_list = data.get("destinations", [])

    # 1. CHANGE: Create 3 columns instead of 2
    cols = st.columns(3)

    for idx, dest in enumerate(dest_list):
        with cols[idx % 3]:
            with st.container(border=True):
                # Image Logic
                img_url = get_city_image(dest['name'], idx)
                st.image(img_url, width='stretch')

                st.subheader(f"📍 {dest['name']}")

                # Limit description height effectively by keeping it concise or using scroll (optional)
                st.write(dest['description'])

                st.divider() # Visual separator before buttons

                # 3. CHANGE: Add Action Buttons
                # Encode the city name (e.g., "New York, USA" -> "New%20York%2C%20USA")
                query = urllib.parse.quote(dest['name'])

                if st.button("🚀 Explore Deep Dive", key=f"btn_{idx}"):
                    st.session_state.selected_city = dest
                    st.rerun()

    # Recommendation Section
    rec = data.get("recommendation", {})
    if rec:
        st.markdown("---")
        st.success(f"### 👑 Our Top Pick: {rec.get('city')}")
        st.write(f"**Rationale:** {rec.get('rationale')}")