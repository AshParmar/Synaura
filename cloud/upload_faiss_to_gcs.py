# cloud/upload_faiss_to_gcs.py
"""
One-time script: zips the local FAISS index and uploads it to GCS.

Run this from project root whenever you rebuild the FAISS index:
    python -m cloud.upload_faiss_to_gcs

Requires GCS_FAISS_BUCKET in .env (same bucket as scan uploads, different folder).
"""

import os
import zipfile
import tempfile
from pathlib import Path

from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

LOCAL_INDEX_PATH = "backend/data/faiss_index"
GCS_OBJECT_NAME  = "faiss_index/faiss_index.zip"


def upload_faiss_index():
    bucket_name = os.getenv("GCS_FAISS_BUCKET") or os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise EnvironmentError("Set GCS_FAISS_BUCKET (or GCS_BUCKET_NAME) in .env")

    if not Path(LOCAL_INDEX_PATH).exists():
        raise FileNotFoundError(f"FAISS index not found at {LOCAL_INDEX_PATH}. Run build_index.py first.")

    # Zip the index folder
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = tmp.name

    print(f"[upload_faiss] Zipping {LOCAL_INDEX_PATH}…")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in Path(LOCAL_INDEX_PATH).rglob("*"):
            zf.write(file, arcname=file.relative_to(Path(LOCAL_INDEX_PATH).parent))

    # Upload to GCS
    print(f"[upload_faiss] Uploading to gs://{bucket_name}/{GCS_OBJECT_NAME}…")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob   = bucket.blob(GCS_OBJECT_NAME)
    blob.upload_from_filename(zip_path)

    os.remove(zip_path)
    print(f"[upload_faiss] Done. gs://{bucket_name}/{GCS_OBJECT_NAME}")


if __name__ == "__main__":
    upload_faiss_index()
