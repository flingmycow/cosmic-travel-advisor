from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.maps_agent.agent import planner_agent, geocoder_agent
from .sub_agents.google_search_agents.agent import horoscope_agent, high_level_travel_agent
from .sub_agents.accommodation_agent.agent import airbnb_agent

# --- 3. DEFINE DELEGATION FUNCTIONS (The "Glue") ---
horoscope_tool = AgentTool(horoscope_agent)
high_level_travel_tool = AgentTool(high_level_travel_agent)
planner_tool = AgentTool(planner_agent)
geocoder_tool = AgentTool(geocoder_agent)
accommodation_tool = AgentTool(airbnb_agent)


# --- 4. DEFINE ROOT AGENT ---
# The Root Agent has NO native tools (Search/MCP).
# It only has "Function" tools (the python functions above).
# This avoids the "Multiple tools" error completely.

root_agent = Agent(
    model='gemini-2.5-flash',
    name='travel_coordinator',
    instruction="""
    You are a Travel Coordinator. Your goal is to generate a horoscope-based itinerary.
    
    IF the user provides their horoscope / chinese zodiac THEN you must follow this strictly:
    1. Use the `horoscope_researcher` tool with the user's sign to get characteristics of their sign(s).
    2. Pass the result from step 1 using the `planner` tool. Incorporate information from Google Maps into the response for each city.
    3. Output the final JSON returned

    IF the user asks for flight cost, flight duration, weather, or travel logistics for a city then:
    1. Use the `high_level_travel_agent` tool with the city name.
    2. Output the final JSON

    IF the user asks for accommodation suggestions then:
    1. Use the `airbnb` tool to find a listing on Airbnb in the city they are looking for
    2. Output the final JSON

    IF theres a request to get coordinates or lat/lon of a city then:
    1. Use the `geocoder_utility` tool and provide the name of the city
    2. Output the final JSON
    """,
    tools=[horoscope_tool, high_level_travel_tool, planner_tool, accommodation_tool, geocoder_tool]
)