"""Firestore config"""
import logging, io
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKET_NAME = "promo_list_for_ai_scraper_123"
COLLECTION_NAME = "ai_data_cache"
URI_BUCKET = "ai-uri-bucket"

def write_promos(promos: str, bucket_name_override=None, blob_name_override=None, contents_override=None):
    """Add promos to a cloud storage bucket"""
    storage_client = storage.Client()

    bucket_name = bucket_name_override or BUCKET_NAME
    blob_name = blob_name_override or "promo-blob"
    contents = contents_override or promos

    bucket = storage_client.bucket(bucket_name)

    try:
        blob = bucket.blob(blob_name)
        blob.cache_control = "no-cache"
        blob.upload_from_string(contents)

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

def new_uri(uri: str):
    """
    Replaces URI link with a new one
    """
    blob_name = "uri_blob"
    storage_client = storage.Client()
    bucket = storage_client.bucket(URI_BUCKET)
    blob = bucket.blob(blob_name)
    blob.cache_control = "no-cache"
    blob.upload_from_string(uri)

def get_uri() -> str:
    """
    Returns a pre-existing uri string
    """
    blob_name = "uri_blob"
    storage_client = storage.Client()
    bucket = storage_client.bucket(URI_BUCKET)
    blob = bucket.get_blob(blob_name)
    uri = blob.download_as_text()
    return uri

def promos_to_bytes():
    file_bytes_io = io.BytesIO()
    bucket = BUCKET_NAME
    blob = bucket.blob("promo-blob")
    blob.download_to_file(file_bytes_io)
    return file_bytes_io
