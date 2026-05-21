# cloud/gcs_client.py
"""
Google Cloud Storage helper for Synaura.

Used to upload user-submitted X-ray/scan files to a GCS bucket
and return a public (or signed) URL for downstream processing.

Requires:
  GCS_BUCKET_NAME in .env
  GOOGLE_APPLICATION_CREDENTIALS pointing to your service account JSON (local dev)
  OR the Cloud Run service account having Storage Object Creator role (production)
"""

import os
import uuid
from pathlib import Path

from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "synaura-uploads")

_gcs_client: storage.Client | None = None


def _get_client() -> storage.Client:
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = storage.Client()
    return _gcs_client


def upload_scan(local_path: str, content_type: str = "image/png") -> str:
    """
    Upload a local file to GCS.

    Returns the GCS URI: gs://<bucket>/<blob_name>
    """
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)

    # Unique blob name to avoid collisions
    suffix = Path(local_path).suffix
    blob_name = f"scans/{uuid.uuid4()}{suffix}"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path, content_type=content_type)

    gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"
    return gcs_uri


def get_signed_url(blob_name: str, expiration_minutes: int = 60) -> str:
    """
    Generate a signed URL for temporary access to a private GCS object.
    Requires the service account to have the iam.serviceAccounts.signBlob permission.
    """
    from datetime import timedelta

    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )
    return url
