"""HTTPS function module"""
import logging
import json
from firebase_functions import https_fn, options
from firebase_functions.options import MemoryOption
from . import ai
from . import cloud_storage
from . import fire_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@https_fn.on_request(
        max_instances=1, cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post", "options"]), timeout_sec=50, memory=MemoryOption.MB_512
       )
def receive_query(req: https_fn.Request) -> https_fn.Response:
    """Receives a query for the firestore DB or the AI and returns the response"""
    
    data = req.get_json()
    ai_resp = None

    try:
        query = data["todays_deals"]
        deal_type = "todays_deals"
    except KeyError:
        try:
            query = (data['skin_types'], data['skin_concerns'], data['hair_types'],
                    data['hair_concerns'], data['makeup_preferences'])
            deal_type = "preferred_deals"
        except KeyError as exc:
            raise RuntimeError("Unknown Query") from exc

    cached_response = fire_store.check_if_cached(str(query))

    if not cached_response:
        ai_bot = ai.AiBot()
        uri = cloud_storage.get_uri()
        
        if deal_type == "todays_deals":
            resp = ai_bot.get_top_deals(uri)

        elif deal_type == "preferred_deals":
            resp = ai_bot.get_pref_deals(uri, query)

        if resp is False:
            return https_fn.Response("Error: No AI response generated", status=500)
        else:
            fire_store.add_data(query, json.dumps(resp))
            ai_resp = fire_store.check_if_cached(str(query))
    else:
        ai_resp = cached_response

    return https_fn.Response(ai_resp, status=200)
