"""database cleanup module"""
import time
import logging
from firebase_functions import scheduler_fn
from firebase_functions.options import MemoryOption
from . import database_config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@scheduler_fn.on_schedule(schedule="59 04 * * *", memory=MemoryOption.MB_512, timeout_sec=30, max_instances=1)
def databasecleanup(event: scheduler_fn.ScheduledEvent) -> None:
    """Delete old data from and add new data to the firestore database"""
    logger.info("Cleanup running")
    database_config.write_promos()
    time.sleep(60)
    database_config.delete_old_data()
    logger.info("Cleanup finished")

