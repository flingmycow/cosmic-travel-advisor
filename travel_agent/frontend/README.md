# Frontend Notes

## Folder Structure

```
frontend/
├── app.py                  # The new, clean entry point
├── services/
│   ├── __init__.py
│   └── adk_bridge.py       # Handles all API/Requests logic
├── ui/
│   ├── __init__.py
│   ├── layout.py           # Sidebar, Titles, CSS styling
│   └── results.py          # The complex grid rendering logic
└── utils/
    ├── __init__.py
    ├── parsers.py          # JSON cleaning tools
    └── zodiac_data.py      # Your original 'utils.py' (renamed)
```