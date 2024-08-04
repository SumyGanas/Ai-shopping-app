"""Firestore config"""
import logging
import time
from datetime import datetime, timedelta
from firebase_admin import firestore, db, credentials
import firebase_admin
from google.cloud import storage
from . import web_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cred = credentials.Certificate("service_account.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

BUCKET_NAME = "promo_list_for_ai_scraper_123"
COLLECTION_NAME = "ai_data_cache"

def write_promos():
    """Add promos to a cloud storage bucket"""
    storage_client = storage.Client()
    deal_generator = web_scraper.DealGenerator()

    bucket_name = BUCKET_NAME
    blob_name = "promo-blob"

    bucket = storage_client.bucket(bucket_name)

    try:
        contents = deal_generator.get_all_data()
        blob = bucket.blob(blob_name)
        blob.upload_from_string(contents)
        logger.info("New promos written to cloud storage bucket")
    except RuntimeError:
        logger.error("Issue encountered while writing new promos to the bucket")


def read_promos():
    """Read promos from a cloud storage bucket"""
    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)

    blob_name = "promo-blob"
    blob = bucket.get_blob(blob_name)
    promos = blob.download_as_text()

    return promos

def test_cloud_storage_conn():
    """testing cloud storage database connectivity"""
    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)

    blob = bucket.blob("test_blob")

    blob.upload_from_string("This is a test string")

    time.sleep(5)

    data = blob.download_as_text()

    print(data)



def check_if_cached(query: str):
    """
    checks if ai response data is cached in database.
    Returns data if true, or stores it and returns it if false.
    """
    #check if it is cached
    document_date = str(datetime.today()).split()[0]

    doc_ref = db.collection(COLLECTION_NAME).document(document_date)
    doc = doc_ref.get()

    if doc.exists:
        doc_data = doc.to_dict()
        if query in doc_data:
            return doc_data[query]
        return False

    default_data = {
        'created_at': datetime.now(),
        query: {}
    }
    doc_ref.set(default_data)
    return False

def add_data(query: tuple[str], resp: str):
    """
    adds new query data to the database collection in today's document
    """
    key = str(query)
    document_date = str(datetime.today()).split()[0]
    doc_ref = db.collection(COLLECTION_NAME).document(document_date)

    data = {
    key : resp,
    }

    doc_ref.set(data, merge=True)

def delete_old_data():
    """
    Deletes old firestore data 
    """
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    yesterday_date_str = yesterday.strftime('%Y-%m-%d')

    #Old queries
    docs = list(db.collection(COLLECTION_NAME).stream())
    if len(docs) > 1:
        doc_ref = db.collection(COLLECTION_NAME).document(yesterday_date_str)
        if doc_ref.get().exists:
            doc_ref.delete()
            logger.info("Old AI queries have been deleted from firestore")
    else:
        logger.info("No old queries to delete from %s", yesterday_date_str)

def test_firestore_conn():
    """testing firestore database connectivity"""
    document_date = str(datetime.today()).split()[0]
    doc_ref = db.collection(COLLECTION_NAME).document(document_date)
    doc = doc_ref.get()
    if doc.exists:
        print(f"Document data: {doc.to_dict()}")
