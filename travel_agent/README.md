# Cosmic Travel Agent

A little fun agent that uses horoscopes or chinese zodiac animals to suggest travel destinations.

## Instructions

1. To start the adk API server run `adk api_server` in directory ABOVE where `travel_agent` is (otherwise it will crash and create a duplicate directory with other stuff in it)
2. Run streamlit on the front end code `streamlit run frontend/Home.py` to then show the interface for ADK

## FYIs
###  Suggested directory and layout

For `adk` and `streamlit` together. Although, could be applied to other front-end frameworks (depending on front-end dependencies)

```build
fun_travel_agent/               # Project Root
├── .env                        # Secrets (API Keys)
├── requirements.txt            # All dependencies
├── README.md
│
├── backend/                    # THE ADK SERVER (Run 'adk run backend')
│   ├── __init__.py
│   ├── agent.py                # Defines 'root_agent'
│   └── agents/                 # Sub-agents (formerly 'sub_agents')
│       ├── __init__.py
│       ├── accommodation.py    # Refactored from folders if simple
│       ├── horoscope.py
│       └── maps.py
│
└── frontend/                   # THE STREAMLIT CLIENT (Run 'streamlit run frontend/Home.py')
    ├── app.py                  # Entry point (formerly agent_app.py)
    ├── assets/                 # Images, CSS
    ├── services/               # API handling (The bridge we discussed)
    │   └── adk_client.py       # Handles requests.post()
    └── utils/
        └── ui_components.py    # Formatting, Grids, Styles
```

* `adk` has requirements on file names and folder structures. for multi-agents I have a sub_agents folder and my root agent in `agent.py`

### Variables (for me)

These are the structures of the response variables that come back and is used for some of the streamlit logic

```python
events[0] = {'actions': {'artifactDelta': {},
             'requestedAuthConfigs': {},
             'requestedToolConfirmations': {},
             'stateDelta': {}},
 'author': 'travel_coordinator',
 'avgLogprobs': -0.06642186215945653,
 'content': {'parts': [{'functionCall': {'args': {'request': 'Leo 3rd Decan '
                                                             '(Mars) horoscope '
                                                             'characteristics'},
                                         'id': 'adk-ac78dfd0-1886-49a2-8681-0c8d50077d15',
                                         'name': 'researcher'},
                        'thoughtSignature': 'Cr0DAY89a19J6VoWNVxQw8MYWvBQABZ3UAVBnNQy2VUc0V3PhtFPJcmMU0DJFlmqGS0B5L_3d4FrP-oodsf0xUG8-_odUR_pXXV4ISbfshyDbDUPVe8SNDPdxY8zJcU-iPLxPfJFpmgvesGpLeFIoIeuuS5nMJ1Wfg6z_SN7IZp0pGLXy8LV2HduwEwee3STDEgyWh2EnBFfn5-aqo6p3ATsDzIzAdgTiEF1cVnmsalFTAqvqhYvXwR76W2oxDYjX4JySJ6BjTALIpiRC7lHsuOAgmPUtlDTxsjCSSP-jf10VHruLYgkwOeMgEVk0Xi6A9mHx-7lHhX1720LoN-Ijc45TPi5jVWQoyrJC7DEe1BLQgak439bnRDcFB7SZwTSWQsLFt7VWp0wPe_CuvLkr7NC-AZMQcj-Eu5bgzI1nBvO8CmB3Ie-ePj6zVpC9U9O9jks25k6WkdCt21uT9kY3VC2CkPauKtWmYCrRZxRFdfXyWH8ltgs1NCGBDgyJA-2ex7yw2pCAJOr0crUlo5Xm6lJ8AWJf9cmQsOnV1u-Rh5kpvinnrSj1Uost-IsN0kOBsQ2dlR-2vYKX5-NlPlqrA=='}],
             'role': 'model'},
 'finishReason': 'STOP',
 'id': '3d4432ef-8746-4c83-96ad-74dce9e52312',
 'invocationId': 'e-91d0dd20-14a3-4498-b323-561c5864c329',
 'longRunningToolIds': [],
 'modelVersion': 'gemini-2.5-flash',
 'timestamp': 1768410033.017437,
 'usageMetadata': {'candidatesTokenCount': 14,
                   'candidatesTokensDetails': [{'modality': 'TEXT',
                                                'tokenCount': 14}],
                   'promptTokenCount': 3791,
                   'promptTokensDetails': [{'modality': 'TEXT',
                                            'tokenCount': 3791}],
                   'thoughtsTokenCount': 99,
                   'totalTokenCount': 3904,
                   'trafficType': 'ON_DEMAND'}}
```

```python
func_response = functionResponse = {'id': 'adk-ac78dfd0-1886-49a2-8681-0c8d50077d15', 'name': 'researcher', 'response': {'result': 'Leo 3rd Decan (Mars): Daring, driven, and sometimes impulsive, with big dreams and a love for exotic travel. They are confident, competitive, and versatile problem-solvers, but can be restless and impatient. They enjoy action-packed adventures and culturally rich destinations.\n'}}
```

### Reminders

* Used `adk api_server` to see all of the FastAPI endpoints
* You don't need to use MCP for everything
* Tempting to PE everything but Pydyantic is useful

## References / Documentation
Resources I used when creating this
* [Documentation on MCP for GoogleMaps](https://developers.google.com/maps/ai/mcp) describes steps for mcp to googlemaps.
* [Documentation on MCP for GoogleMaps (Newer)](https://developers.google.com/maps/ai/grounding-lite)
* [Documentation on MCP for GoogleMaps specifically for searching places](https://developers.google.com/maps/ai/grounding-lite/reference/mcp/search_places)
* [So many MCP Servers!](https://github.com/modelcontextprotocol/servers/tree/main)