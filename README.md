# 🌌 Cosmic Travel Agent

A multi-agent travel planner built with **Google ADK (Agent Development Kit)**, **MCP (Model Context Protocol)**, and **Streamlit**. Pick your Western zodiac sign (including decan) and/or Chinese zodiac animal—or enter your birthday to calculate them—and the agent researches your travel persona, suggests 5 destinations across multiple continents with real landmarks via Google Maps, and lets you deep-dive into maps and live flight/weather logistics.

## 🏗️ Architecture

The backend uses a **coordinator + isolated sub-agent** pattern (`AgentTool`) so each sub-agent can use its own specialized toolset (native Google Search vs. MCP servers) without tool-mixing conflicts:

```
Streamlit UI (travel_agent/frontend/)
        │  REST (/apps/.../sessions, /run)
        ▼
ADK API Server (travel_agent/agent.py -> travel_coordinator)
        ├── horoscope_researcher     (Google Search + Pydantic input schema)
        ├── planner                  (Google Maps MCP — places & landmarks)
        ├── geocoder_utility         (Google Maps MCP — city lat/lng)
        ├── high_level_travel_agent  (Google Search — flights, weather, best season)
        └── airbnb                   (Airbnb MCP — accommodation search)
```

### Sub-Agents
| Agent | Tooling | Role |
| :--- | :--- | :--- |
| `travel_coordinator` | `AgentTool` wrappers | Root orchestrator that routes user requests to the right specialist sub-agent. |
| `horoscope_researcher` | Google Search | Researches Western/Chinese zodiac traits and travel preferences (validated with Pydantic `SignDetails`). |
| `planner` | Google Maps MCP (`@modelcontextprotocol/server-google-maps`) | Generates 5 destination ideas across 3+ continents, verifies real-world landmarks via Maps, and picks a top recommendation. |
| `geocoder_utility` | Google Maps MCP | Returns latitude/longitude coordinates for rendering the interactive map in the Deep Dive view. |
| `high_level_travel_agent` | Google Search | Looks up average flight cost/duration from London, live weather, local time, and best time of year to visit. |
| `airbnb` | Airbnb MCP (`@openbnb/mcp-server-airbnb`) | Searches and filters accommodation listings by location, dates, guests, and budget. |

## 📁 Project Structure

```text
fun_travel_agent/
├── requirements.txt
├── pyproject.toml
└── travel_agent/
    ├── agent.py                        # Root coordinator agent
    ├── .env.example                    # Required environment variables template
    ├── scripts/
    │   ├── schemas.py                  # Pydantic models (SignDetails, TravelPersona, HoroscopeResponse)
    │   └── tests/testing_file.sh       # Quick curl test script for the ADK API server
    ├── sub_agents/
    │   ├── google_search_agents/       # Horoscope researcher & travel logistics agents
    │   ├── maps_agent/                 # Planner & geocoder agents (Google Maps MCP)
    │   └── accommodation_agent/        # Airbnb agent (Airbnb MCP)
    └── frontend/
        ├── Home.py                     # Streamlit entry point
        ├── pages/
        │   ├── 01_🌌_Cosmic_Agent.py   # Main agent search + deep-dive router
        │   └── 02_📊_Data_Insights.py  # Analytics page (WIP)
        ├── services/adk_bridge.py      # HTTP client for ADK /run & session APIs
        ├── ui/                         # Sidebar, zodiac theming, results grid, city deep dive
        └── utils/                      # Zodiac data/calculators & JSON extraction helpers
```

## 🚀 Getting Started

### Prerequisites
* **Python 3.10+**
* **Node.js / `npx`** (used by the Google Maps and Airbnb MCP servers)
* A **Google Cloud project** with Vertex AI enabled (or Gemini API credentials) and a **Google Maps API key**

### 1. Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables
Copy the example env file and fill in your credentials:
```bash
cp travel_agent/.env.example travel_agent/.env
```

```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 3. Run the ADK API Server
Run this from the **repository root** (the directory *above* `travel_agent/`):
```bash
adk api_server
```
The server starts on `http://localhost:8000` by default.

### 4. Launch the Streamlit Frontend
In a separate terminal (from the repository root):
```bash
streamlit run travel_agent/frontend/Home.py
```

## 🧪 Quick API Smoke Test
With `adk api_server` running, you can also test the backend directly without Streamlit:
```bash
bash travel_agent/scripts/tests/testing_file.sh
```

## 🚧 Work in Progress / Ideas
* Wiring the `airbnb` sub-agent directly into the **Where to Stay** section on the Deep Dive page
* Adding real-time flight search results
* Building out the **Data Insights** analytics page

## 📚 References
* [Google Maps MCP Documentation](https://developers.google.com/maps/ai/mcp)
* [Google Maps Grounding Lite (MCP)](https://developers.google.com/maps/ai/grounding-lite)
* [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers/tree/main)
