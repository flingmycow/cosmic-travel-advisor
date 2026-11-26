#!/bin/bash

APP_NAME="travel_agent"
USER_ID="test_user"
SESSION_ID="test-session94983"

echo "------------------------------------------------"
echo "Targeting App: $APP_NAME"
echo "------------------------------------------------"

# Step 1: Create session
# We use -f to fail silently on server errors so we can catch them in the logic
echo "1. Creating session..."
curl -s -X POST "http://localhost:8000/apps/$APP_NAME/users/$USER_ID/sessions/$SESSION_ID" \
   -H "Content-Type: application/json" \
   -d "{}" | jq . || echo "Failed to parse Session response"

sleep 1

# Step 2: Define JSON Payload using a Heredoc (Cleaner syntax)
# This prevents quoting errors
JSON_PAYLOAD=$(cat <<EOF
{
  "app_name": "$APP_NAME",
  "user_id": "$USER_ID",
  "session_id": "$SESSION_ID",
  "new_message": {
    "parts": [{"text": "I am a Cancer and a Monkey"}],
    "role": "user"
  }
}
EOF
)

echo ""
echo "2. Sending message..."
echo "Payload: $JSON_PAYLOAD"
echo ""

# Execute Curl
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

# Extract Body and Status
HTTP_BODY=$(echo "$RESPONSE" | sed -e 's/HTTP_STATUS:.*//g')
HTTP_STATUS=$(echo "$RESPONSE" | tr -d '\n' | sed -e 's/.*HTTP_STATUS://')

echo "------------------------------------------------"
echo "Server responded with Status: $HTTP_STATUS"
echo "------------------------------------------------"

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "$HTTP_BODY" | jq .
else
    echo "⚠️ Error encountered!"
    echo "Raw Body: $HTTP_BODY"
fi