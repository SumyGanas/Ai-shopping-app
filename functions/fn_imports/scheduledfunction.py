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
    cloud_storage.write_promos()
    promos = cloud_storage.read_promos()

    bot = ai.AiBot()
    uri = bot.generate_uri(promos)
    cloud_storage.new_uri(uri)
    
    fire_store.delete_old_data()
    logger.info("Cleanup finished")

