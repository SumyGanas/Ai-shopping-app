"""database cleanup module"""
import logging
from firebase_functions import scheduler_fn
from firebase_functions.options import MemoryOption
import cloud_storage, fire_store
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BUCKET_NAME = "promo_list_for_ai_scraper_123"
COLLECTION_NAME = "ai_data_cache"

@scheduler_fn.on_schedule(schedule="59 04 * * *", memory=MemoryOption.MB_512, timeout_sec=120, max_instances=1)
def databasecleanup(event: scheduler_fn.ScheduledEvent) -> None:
    """Update the daily promotional data"""
    db = fire_store.Promotions()
    sales = db.update_sales()
    promos = db.update_promotions()
    cloud_storage.write_promos(sales+"\n"+promos)