import requests
from firebase_functions import scheduler_fn
form_data = {
    'skin_types': 'Dry',
    'skin_concerns': 'Redness and/or Wrinkles',
    'hair_types': 'Curly',
    'hair_concerns': 'Damaged and/or Frizzy',
    'makeup_preferences': 'Light/Daily'
}

# db_url = "https://databasecleanup-dy3kdkbuyq-uc.a.run.app"
# ai_url = 'https://receive-query-dy3kdkbuyq-uc.a.run.app'

# #ai_response = requests.post(ai_url, data=form_data, timeout=30)
# #print(ai_response.content)
# headers = {
#     'User-Agent': 'Google-Cloud-Scheduler',
# }


# db_response = requests.post(db_url, json={})

# print('Status Code:', db_response.status_code)
# print('Response Data:', db_response.text)
