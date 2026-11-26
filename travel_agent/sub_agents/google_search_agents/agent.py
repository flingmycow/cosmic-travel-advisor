import json

from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from ...scripts.schemas import SignDetails, TravelPersona, HoroscopeResponse

schema_instruction = json.dumps(HoroscopeResponse.model_json_schema(), indent=2)

# --- 2. DEFINE SUB-AGENTS ---
# Sub-Agent A: The Researcher (Uses Native Google Search)
# This agent is ISOLATED, so it can use Google Search without conflict.
horoscope_agent = Agent(
    model='gemini-3.8-flash',
    name='horoscope_researcher',
    description="Analyzes zodiac signs to create a structured Travel Persona",
    instruction="""
    You are an expert Astrologer and Travel Psychologist.
    
    YOUR GOAL:
    Research the user's sign (Western and/or Chinese) and translate their personality traits into specific travel recommendations.
    
    STEP 1: IDENTIFY & RESEARCH
    - Identify if the input is Western (e.g. Gemini), Chinese (e.g. Monkey), or both.
    - If a specific variant/decan is mentioned (e.g. "Decan 2"), focus research on that specific nuance.
    - Search for: "travel style", "vacation preferences", "likes/dislikes" for that sign.
    
    STEP 2: RECOMMEND
    - Find at least 5 distinct cities/countries that match this vibe.
    """,
    tools=[google_search],
    input_schema=SignDetails,
    output_key="user_profile",
)

# this agent formats the output from the horoscope researcher agent as cannot use output_schema with the google_search tool??
horoscope_formatter_agent = Agent(
    model='gemini-3.8-flash',
    name='profiler',
    instruction="""
    You are a data extraction expert. 
    Take the provided research summary and strictly format it into the UserProfile JSON.
    """,
    input_schema=None, # Accepts the string output from researcher
    output_key="user_profile",
    output_schema=HoroscopeResponse, # Schema goes here
)

high_level_travel_agent = Agent(
    model='gemini-3.8-flash',
    name='high_level_travel_agent',
    description="Gets high level travel logistics: avg flight costs, flight duration, weather, best travel season",
    instruction="""
    You are a travel logistics API.
    When asked about a city (from London), search for:
    1. Average flight cost (economy, round trip).
    2. Flight duration.
    3. Current temperature and rain chance (Live data)
    4. Time and Timezone
    5. The recommended **Best Time of Year** to visit (e.g. "Spring" or "September-October").
    6. The historical average temperature and rain chance **during that specific 'Best Time'**.
    
    You MUST output valid JSON only. No markdown formatting.
    Format:
    {
        "cost": "£XXX",
        "duration": "X h Y m",
        "current_temp": "XX°C",
        "current_rain": "XX%",
        "current_date_time": "YYYY-MM-DD hh:mm",
        "best_time_to_visit": "e.g. May-June",
        "best_time_avg_temp": "XX°C (seasonal avg)",
        "best_time_rain_chance": "High/Low/XX%",
        "flight_summary": "Short text summary of airlines/routes."
    }
    """,
    tools=[google_search]
)

itinerary_agent = Agent(
    model='gemini-3.8-flash',
    name='itinerary_agent',
    description="Based on the horoscope/zodiac and travel characteristics",
    instruction="""
    You are a travel logistics API.
    When asked about a city (from London), search for:
    1. Average flight cost (economy, round trip).
    2. Flight duration.
    3. Current temperature and rain chance (Live data).
    4. The recommended **Best Time of Year** to visit (e.g. "Spring" or "September-October").
    5. The historical average temperature and rain chance **during that specific 'Best Time'**.
    
    You MUST output valid JSON only. No markdown formatting.
    Format:
    {
        "cost": "£XXX",
        "duration": "X h Y m",
        "current_temp": "XX°C",
        "current_rain": "XX%",
        "best_time_to_visit": "e.g. May-June",
        "best_time_avg_temp": "XX°C (seasonal avg)",
        "best_time_rain_chance": "High/Low/XX%",
        "flight_summary": "Short text summary of airlines/routes."
    }
    """,
    tools=[google_search]
)
