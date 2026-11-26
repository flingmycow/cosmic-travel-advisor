import streamlit as st
import re
import json

def extract_json_from_text(text):
    """
    Extracts JSON from text even if not formatted in markdown blocks.
    """
    try:
        # 1. Try finding standard Markdown JSON block first
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        # 2. Flexible Fallback: Look for the outermost JSON structure
        # Matches content starting with { or [ and ending with } or ]
        # [\s\S]*? is a non-greedy match for any character including newlines

        # We try to find a List structure first (common for grids)
        list_match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
        if list_match:
            return json.loads(list_match.group(0))

        # If no list, try to find a single Object structure
        obj_match = re.search(r"\{[\s\S]*\}", text, re.DOTALL)
        if obj_match:
            return json.loads(obj_match.group(0))

        # 3. Last Resort: Try parsing the raw text
        return json.loads(text)

    except (json.JSONDecodeError, AttributeError):
        # Return None if no valid JSON is found, so the main loop can handle it
        return None
    except Exception as e:
        st.error(f"Unexpected error parsing data: {e}")
        return None

def parse_ai_response(text):
    # 1. Extract the main personality summary
    # Looks for text before "Based on these characteristics"
    summary_match = re.search(r"(.*?)(?=Based on these characteristics)", text, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else "Your Astrological Profile"

    # 2. Extract specific destinations
    # This regex looks for: "City, Country" followed by the description text
    # It assumes the AI uses a common pattern of "Name - Description" or "Name [Newline] Description"
    dest_pattern = re.findall(r"([\w\s]+, [\w\s]+)\s*(.*?)(?=\n[\w\s]+, [\w\s]+|\nRecommendation:|$)", text, re.DOTALL)

    destinations = []
    for name, desc in dest_pattern:
        destinations.append({
            "name": name.strip(),
            "description": desc.strip()
        })

    # 3. Extract final recommendation and rationale
    rec_match = re.search(r"Recommendation:\s*(.*?)\s*Rationale:\s*(.*)", text, re.DOTALL)
    recommendation = {
        "city": rec_match.group(1).strip() if rec_match else "Unknown",
        "rationale": rec_match.group(2).strip() if rec_match else ""
    }

    return summary, destinations, recommendation