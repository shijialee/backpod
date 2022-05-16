import os
from google.cloud import storage


def upload(file_path, filename):
    storage_client = storage.Client()
    bucket_name = os.getenv("FEED_BUCKET_NAME")
    bucket = storage_client.bucket(bucket_name)
    new_blob = bucket.blob(filename)
    new_blob.upload_from_filename(file_path)
    print(f"file uploaded to: gs://{bucket_name}/{filename}")