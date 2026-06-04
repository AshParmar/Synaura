# cloud/upload_weights_to_gcs.py
"""
One-time script: uploads the local model weights to GCS.

Run this from project root:
    python -m cloud.upload_weights_to_gcs
"""

import os
from pathlib import Path
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

LOCAL_WEIGHTS_PATH = "backend/classify/densenet121_fuzzy_uselftrained_best.pth"
GCS_OBJECT_NAME = "weights/densenet121_fuzzy_uselftrained_best.pth"


def upload_weights():
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise EnvironmentError("Set GCS_BUCKET_NAME in your .env file")

    if not Path(LOCAL_WEIGHTS_PATH).exists():
        raise FileNotFoundError(f"Model weights not found at {LOCAL_WEIGHTS_PATH}.")

    print(f"[upload_weights] Uploading {LOCAL_WEIGHTS_PATH} to gs://{bucket_name}/{GCS_OBJECT_NAME}…")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(GCS_OBJECT_NAME)
    blob.upload_from_filename(LOCAL_WEIGHTS_PATH)
    print(f"[upload_weights] Done. gs://{bucket_name}/{GCS_OBJECT_NAME}")


if __name__ == "__main__":
    upload_weights()
