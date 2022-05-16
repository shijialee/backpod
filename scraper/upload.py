import os
from google.cloud import storage


def upload(file_path, filename):
    storage_client = storage.Client()
    bucket_name = os.getenv("FEED_BUCKET_NAME")
    bucket = storage_client.bucket(bucket_name)
    new_blob = bucket.blob(filename)
    new_blob.upload_from_filename(file_path)
    print(f"Blurred image uploaded to: gs://{bucket_name}/{filename}")


def upload_blob_from_memory():
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    bucket_name = os.getenv("FEED_BUCKET_NAME")

    # The contents to upload to the file
    contents = "these are my contents"

    # The ID of your GCS object
    destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

    print(
        "{} with contents {} uploaded to {}.".format(
            destination_blob_name, contents, bucket_name
        )
    )
