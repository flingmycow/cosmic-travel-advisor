import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 1. Set up your Maps API Key
maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

# 2. Configure the MCP Tool
# We define this outside the Agent to keep the main block clean
maps_mcp_tool = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=['-y', '@modelcontextprotocol/server-google-maps'],
            env={"GOOGLE_MAPS_API_KEY": maps_api_key}
        )
    )
)

# 3. Updated Instruction
root_agent = Agent(
    model='gemini-2.5-flash',
    name='travel_agent',
    description='An agent that will generate a basic travel itinerary based on horoscopes or chinese zodiac (for fun!)',
    instruction= """Generate a travel itinerary based on horoscopes or chinese zodiac signs.

    1. Search for a personality description based on the user's signs (use Google Search).
    2. Brainstorm 4-5 holiday destinations that match those traits.
       * One destination must be different from typical travel destinations.
       * There should be at least three continents covered (except Antarctica and Australia).
       * Do not suggest dangerous countries due to war.
    
    3. VERIFICATION STEP (Use Google Maps MCP):
       * For your top recommendation, use the Maps tool to find a specific landmark or district that aligns with the user's horoscope trait (e.g., "secluded beach" or "bustling market").
       * Confirm the city and country names are spelled correctly according to Maps data.

    4. Choose one top recommendation with a rationale that references the specific place found in step 3.
    
    IMPORTANT: You must return your final answer in the following JSON format inside a markdown code block:
    {
      "summary": "personality description here",
      "destinations": [
        {"name": "City, Country", "description": "detailed reason why it fits"},
        ...
      ],
      "recommendation": {
        "city": "City, Country",
        "rationale": "detailed explanation also referencing the specific landmark found via Maps and explain why it was picked"
      }
    }
    """,
    tools=[google_search, maps_mcp_tool]
)


