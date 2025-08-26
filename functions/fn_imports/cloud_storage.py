"""Firestore config"""
import logging
from google.cloud import storage
from . import web_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKET_NAME = "promo_list_for_ai_scraper_123"
COLLECTION_NAME = "ai_data_cache"

def write_promos(bucket_name_override=None, blob_name_override=None, contents_override=None):
    """Add promos to a cloud storage bucket"""
    storage_client = storage.Client()
    deal_generator = web_scraper.DealGenerator()

    bucket_name = bucket_name_override or BUCKET_NAME
    blob_name = blob_name_override or "promo-blob"
    contents = contents_override or deal_generator.get_all_data()

    bucket = storage_client.bucket(bucket_name)

    try:
        blob = bucket.blob(blob_name)
        blob.cache_control = "no-cache"
        blob.upload_from_string(contents, content_type="application/json")

    except RuntimeError:
        logger.error("Issue encountered while writing new promos to the bucket")


def read_promos(bucket_name_override=None, blob_name_override=None):
    """Read promos from a cloud storage bucket"""
    storage_client = storage.Client()

    bucket_name = bucket_name_override or BUCKET_NAME
    blob_name = blob_name_override or "promo-blob"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    promos = blob.download_as_text()

    return promos