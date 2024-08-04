"""HTTPS function module"""
import logging
from firebase_functions import https_fn, options
from . import ai
from . import database_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@https_fn.on_request(max_instances=1, cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def receive_query(req: https_fn.Request) -> https_fn.Response:
    """Receives a query for the firestore DB or the AI and returns the response"""
    logger.info("https running")
    data = req.form
    skin_types_field = data.get('skin_types')
    skin_concerns_field = data.get('skin_concerns')
    hair_types_field = data.get('hair_types')
    hair_concerns_field = data.get('hair_concerns')
    makeup_preferences_field = data.get('makeup_preferences')
    todays_deals_field = data.get('todays_deals')

    if todays_deals_field is None:
        query = (skin_types_field, skin_concerns_field, hair_types_field,
                hair_concerns_field, makeup_preferences_field)
        query_str = str(query)
        cached_response = database_config.check_if_cached(query_str)
        if cached_response is False:
            ai_bot = ai.AiBot()
            promos = database_config.read_promos()
            ai_resp = ai_bot.get_best_deals(query, promos)
            database_config.add_data(query, ai_resp)
        else:
            ai_resp = cached_response
        return https_fn.Response(ai_resp)
    else:
        query = "today_deals"
        cached_response = database_config.check_if_cached(query)
        if cached_response is False:
            ai_bot = ai.AiBot()
            promos = database_config.read_promos()
            ai_resp = ai_bot.current_best_deals(promos)
            database_config.add_data(query, ai_resp)
        else:
            ai_resp = cached_response
        return https_fn.Response(ai_resp)
