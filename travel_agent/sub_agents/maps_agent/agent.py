import os
import logging

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

logging.basicConfig(level=logging.INFO)

# --- 1. SETUP & CREDENTIALS ---
maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
if not maps_api_key:
    print("Warning: GOOGLE_MAPS_API_KEY not found.")

# --- 2. DEFINE SUB-AGENT ---
# This agent is also ISOLATED, so it can use MCP without conflict.
maps_mcp_tool = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=['-y', '@modelcontextprotocol/server-google-maps'],
            env={"GOOGLE_MAPS_API_KEY": maps_api_key}
        )
    )
)

planner_agent = Agent(
    model='gemini-3.8-flash',
    name='planner',
    description="Recommends 5 travel destinations and a top pick with real Google Maps landmarks based on a personality profile.",
    instruction="""
    You are a travel agent generating an itinerary based on a provided personality profile.

    Step 1: Analyze the provided personality description.
    
    Step 2: Brainstorm 5 holiday destinations that match those traits. 
       * One destination must be different from typical travel destinations.
       * There must be at least three continents covered (except Antarctica and Australia). 
       * Do not suggest dangerous countries due to war or geopolitics.
    
    Step 3: Add extra information using Google Maps (Use Google Maps MCP):
       * TOOL NAME: Look for a tool named `search_places` OR `maps_search_places`.
       * ARGUMENTS: The tool expects a parameter named `query` (NOT textQuery). Example: {"query": "luxury hotel in Paris"}
       * Execute this tool to confirm a real address exists.
       * For every recommendation use the Maps tool to find a SPECIFIC real-world landmark or district in that city \
        that aligns with the personality (e.g., "Borough Market in London" or "Taj Mahal" or "Copacabana", and so on).
       * Verify the city spelling is correct.

    Step 4: Final Rationale.
       * Pick a destination from the list to recommend to the user along with the rationale.
    
    IMPORTANT: You must return your final answer in the following JSON format inside a markdown code block:
    {
      "summary": "personality description here",
      "destinations": [
        {"name": "City, Country", "description": "detailed reason why it fits"},
        ...
      ],
      "recommendation": {
        "city": "City, Country",
        "rationale": "detailed explanation of the suggestion and include a reference to the specific landmark found via Maps"
      }
    }
    """,
    tools=[maps_mcp_tool]
)

# 3. another sub-agent specifically for geocoding
# Usage: Strictly technical geocoding (City Name -> Lat/Long).
geocoder_agent = Agent(
    name="geocoder_utility",
    model="gemini-3.8-flash",
    description="Converts city names or addresses into geographic coordinates (latitude/longitude).",
    instruction="""
    You are a strict geocoding utility. 
    Your ONLY goal is to take a city name or address and return its exact Latitude and Longitude.
    Do NOT offer recommendations. Do NOT look for reviews.
    Use the Google Maps tools to find the precise location geometry.
    Output format: JSON with keys 'lat' and 'lng'.
    """,
    tools=[maps_mcp_tool]
)