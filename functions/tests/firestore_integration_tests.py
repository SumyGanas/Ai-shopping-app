import pytest
from datetime import datetime, timezone, timedelta
from google.cloud import firestore
from functions.fn_imports.fire_store import add_data, delete_old_data

COLLECTION_NAME = "ai_data_cache"
db = firestore.Client()

QUERY = ("dry skin", "sensitive")
RESP = "Try using a gentle, hydrating cleanser."
KEY = str(QUERY)

def get_today_doc_ref():
    document_date = str(datetime.now(timezone.utc)).split()[0]
    return db.collection(COLLECTION_NAME).document(document_date)

def test_add_data():
    """Integration test for adding query-response pair to Firestore"""
    add_data(QUERY, RESP)

    doc = get_today_doc_ref().get()
    assert doc.exists, "Expected Firestore document does not exist."

    data = doc.to_dict()
    assert KEY in data, f"Key '{KEY}' not found in Firestore document."
    assert data[KEY] == RESP, f"Value mismatch for key '{KEY}'. Expected '{RESP}', got '{data[KEY]}'"

    print(f"Successfully added and verified key: {KEY} with value: {RESP}")

def test_delete_old_data():
    """Integration test for deleting old Firestore data"""

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_date_str = yesterday.strftime('%Y-%m-%d')
    doc_ref = db.collection(COLLECTION_NAME).document(yesterday_date_str)

    dummy_data = {"old_test_field": "delete me"}
    doc_ref.set(dummy_data)

    assert doc_ref.get().exists, "Setup failed: test doc for yesterday was not created."

    delete_old_data()

    assert not doc_ref.get().exists, "Old document was not deleted."

    print(f"Successfully deleted document dated {yesterday_date_str}")
