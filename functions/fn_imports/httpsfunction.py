"""HTTPS function module"""
import logging, json
from firebase_functions import https_fn, options
from firebase_functions.options import MemoryOption
from . import ai, fire_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@https_fn.on_request(
        max_instances=1, cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post", "options"]), timeout_sec=80, memory=MemoryOption.MB_512
       )
def receive_query(req: https_fn.Request) -> https_fn.Response:
    """Receives a query for the firestore DB or the AI and returns the response"""
    
    data = req.get_json()
    ai_resp = None
    cache = fire_store.Cache()
    try:
        query = data["todays_deals"]
        deal_type = "todays_deals"
        cached_response = cache.check_if_cached(deal_type)
    except KeyError:
        try:
            query = (data['skin_types'], data['skin_concerns'], data['hair_types'],
                    data['hair_concerns'], data['makeup_preferences'])
            deal_type = "preferred_deals"
            cached_response = cache.check_if_cached(str(query))
        except KeyError as exc:
            raise RuntimeError("Unknown Query") from exc
    if not cached_response:
        ai_bot = ai.AiBot()
        
        if deal_type == "todays_deals":
            resp = ai_bot.get_top_deals()

        elif deal_type == "preferred_deals":
            resp = ai_bot.get_pref_deals(query)
        
        if resp is False:
            return https_fn.Response("Error: No AI response generated", status=500)
        else:
            cache_handler = fire_store.Cache_Handler(resp)
            cache_handler.add_to_cache(deal_type, query)
            ai_resp = cache.check_if_cached(str(query))
    else:
        ai_resp = cached_response

    try:
        resp = json.dumps(ai_resp, ensure_ascii=False, separators=(',', ':'))
        return https_fn.Response(resp, status=200)
    except json.JSONDecodeError:
        return https_fn.Response("ERROR: Gemini response cannot be parsed", status=500)