import logging
from datetime import datetime, timedelta, timezone
from firebase_admin import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLLECTION_NAME = "ai_data_cache"

def check_if_cached(query: str):
    """
    checks if ai response data is cached in database.
    Returns data if true, or stores it and returns it if false.
    """
    document_date = str(datetime.now(timezone.utc)).split()[0]

    doc_ref = db.collection(COLLECTION_NAME).document(document_date)
    doc = doc_ref.get()

    if doc.exists:
        doc_data = doc.to_dict()
        if query in doc_data:
            return doc_data[query]
    else:
        default_data = {
            'created_at': datetime.now(timezone.utc),
            query: {}
        }
        doc_ref.set(default_data)

    return False

def add_data(query: tuple[str], resp: str):
    """
    adds new query data to the database collection in today's document
    """
    key = str(query)
    document_date = str(datetime.now(timezone.utc)).split()[0]
    doc_ref = db.collection(COLLECTION_NAME).document(document_date)

    data = {
    key : resp,
    }

    doc_ref.set(data, merge=True)

def delete_old_data():
    """
    Deletes old firestore data 
    """
    today = datetime.now(timezone.utc)
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
    document_date = str(datetime.now(timezone.utc)).split()[0]
    doc_ref = db.collection(COLLECTION_NAME).document(document_date)
    doc = doc_ref.get()
    if doc.exists:
        print(f"Document data: {doc.to_dict()}")
        