"""database cleanup module"""
import time
import logging
from firebase_functions import scheduler_fn
from firebase_functions.options import MemoryOption
from . import cloud_storage
from . import fire_store
from . import ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BUCKET_NAME = "promo_list_for_ai_scraper_123"
COLLECTION_NAME = "ai_data_cache"

@scheduler_fn.on_schedule(schedule="59 04 * * *", memory=MemoryOption.MB_512, timeout_sec=100, max_instances=1)
def databasecleanup(event: scheduler_fn.ScheduledEvent) -> None:
    """Delete old data from and add new data to the firestore database. And generate a new URI"""
    logger.info("Cleanup running")
    sales = fire_store.create_sale_data()
    promos = fire_store.create_promotional_data()
    cloud_storage.write_promos(sales+"\n"+promos)
    promo_bytes = cloud_storage.promos_to_bytes()
    
    bot = ai.AiBot()
    uri = bot.upload_file(promo_bytes)
    cloud_storage.new_uri(uri)
    
    logger.info("Cleanup finished")

