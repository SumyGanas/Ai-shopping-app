import requests

form_data = {
    "skin_types": "Dry",
    "skin_concerns": "Redness and/or Wrinkles",
    "hair_types": "Straight",
    "hair_concerns": "Damaged and/or Frizzy",
    "makeup_preferences": "Light/Daily"
}

#form_data = {"todays_deals" : "todays_deals"}


#cloud_function_url = "https://receive-query-dy3kdkbuyq-uc.a.run.app"
firebase_emulator_url = "http://127.0.0.1:5001/alpine-figure-414421/us-central1/receive_query"
#local_host_url = "http://localhost:8080"

header = {"Content-Type": "application/json"}
ai_response = requests.post(firebase_emulator_url, json=form_data, timeout=30, headers=header)
print(ai_response.text, ai_response.status_code)

# curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{"test" : "test"}'
# curl -X POST http://127.0.0.1:5001/alpine-figure-414421/us-central1/receive_query -H "Content-Type: application/json" -d '{"test" : "test"}'
# curl -X POST http://127.0.0.1:5001/alpine-figure-414421/us-central1/receive_query -H "Content-Type: application/json" -d '{"skin_types": "Oily", "skin_concerns": "Acne and/or Dark Spots", "hair_types": "Straight", "hair_concerns": "Damaged and/or Frizzy", "makeup_preferences": "Light/Daily"}'

#  Request to function failed: Error: socket hang up  > [ERROR] Worker (pid:50034) was sent SIGKILL! Perhaps out of memory?