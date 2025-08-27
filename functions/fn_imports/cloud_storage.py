"""Firestore config"""
import logging
import json
import tempfile
import os
from google.cloud import storage
from . import web_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKET_NAME = "promo_list_for_ai_scraper_123"
COLLECTION_NAME = "ai_data_cache"
URI_BUCKET = "ai-uri-bucket"

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
    blob_name = "uri_blob"
    storage_client = storage.Client()
    bucket = storage_client.bucket(URI_BUCKET)
    blob = bucket.blob(blob_name)
    blob.cache_control = "no-cache"
    blob.upload_from_string(uri)

def get_uri() -> str:
    blob_name = "uri_blob"
    storage_client = storage.Client()
    bucket = storage_client.bucket(URI_BUCKET)
    blob = bucket.get_blob(blob_name)
    uri = blob.download_as_text()
    return uri

def json_to_tmp(data, prefix="upload_", suffix=".json"):
    if isinstance(data, dict):
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    else:
        json_str = str(data)

    tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix, mode="w", encoding="utf-8")
    tmp.write(json_str)
    tmp.close()

    return tmp.name
