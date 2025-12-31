import uuid
import pytest
from google.cloud import storage
from fn_imports.cloud_storage import write_promos, read_promos

TEST_BUCKET_NAME = "ai_port_test"

def test_write_and_read_promos_using_file():
    test_blob_name = f"test-promo-blob-{uuid.uuid4()}"

    with open("local.test_promos.txt", "r", encoding="utf-8") as f:
        test_data = f.read()

    write_promos(
        "",
        bucket_name_override=TEST_BUCKET_NAME,
        blob_name_override=test_blob_name,
        contents_override=test_data
    )

    result = read_promos(
        bucket_name_override=TEST_BUCKET_NAME,
        blob_name_override=test_blob_name
    )

    assert result == test_data

    storage_client = storage.Client()
    bucket = storage_client.bucket(TEST_BUCKET_NAME)
    #bucket.blob(test_blob_name).delete()
