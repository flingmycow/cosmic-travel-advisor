import streamlit as st
import urllib.parse  # Import this to handle URL spaces safely

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
                city_clean = dest['name'].split(',')[0].strip().replace(" ", "")
                img_url = f"https://loremflickr.com/400/250/{city_clean}?random={idx}"
                st.image(img_url, width='content')

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