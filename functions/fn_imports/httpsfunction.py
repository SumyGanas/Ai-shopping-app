"""HTTPS function module"""
import logging
import json
from firebase_functions import https_fn, options
from firebase_functions.options import MemoryOption
from . import ai
from . import cloud_storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@https_fn.on_request(
        max_instances=1, cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]), timeout_sec=30, memory=MemoryOption.MB_512
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

    cached_response = cloud_storage.check_if_cached(str(query))

    if not cached_response:
        logger.info("not cached")
        ai_bot = ai.AiBot()
        promos = cloud_storage.read_promos()
        if deal_type == "todays_deals":
            gemini_resp = ai_bot.get_top_deals(promos)
            logger.info(gemini_resp)
            resp = ai_bot.validate_response_schema(gemini_resp, "td")

        elif deal_type == "preferred_deals":
            gemini_resp = ai_bot.get_pref_deals(promos, query)
            resp = ai_bot.validate_response_schema(gemini_resp, "prefs")
        if resp is False:
            ai_resp = None
        else:
            cloud_storage.add_data(query, json.dumps(gemini_resp))
            ai_resp = cloud_storage.check_if_cached(str(query))
    else:
        logger.info("cached")
        ai_resp = cached_response



    if ai_resp is None:
        return https_fn.Response("Error: No AI response generated", status=500)
    return https_fn.Response(ai_resp, status=200)
