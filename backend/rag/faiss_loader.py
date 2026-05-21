# backend/rag/faiss_loader.py
"""
Production-safe FAISS loader for Google Cloud Run.

The FAISS index is NOT baked into the Docker image (it's large and changes).
Instead, it's stored in GCS and downloaded on container startup.

Workflow:
  Local dev  → load from  backend/data/faiss_index/  (already on disk)
  Production → download from GCS → load → cache in memory

Set GCS_FAISS_BUCKET in .env to enable GCS loading.
If not set, falls back to local disk (local dev works unchanged).
"""

import os
import shutil
import tempfile
from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

LOCAL_INDEX_PATH = "backend/data/faiss_index"
EMBEDDING_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"
GCS_OBJECT_NAME  = "faiss_index/faiss_index.zip"   # path inside the bucket


def _download_from_gcs(bucket_name: str, dest_dir: str) -> None:
    """Download and unzip the FAISS index from GCS into dest_dir."""
    from google.cloud import storage
    import zipfile

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob   = bucket.blob(GCS_OBJECT_NAME)

    zip_path = os.path.join(dest_dir, "faiss_index.zip")
    print(f"[faiss_loader] Downloading {GCS_OBJECT_NAME} from gs://{bucket_name}…")
    blob.download_to_filename(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)

    print("[faiss_loader] Download complete.")


@lru_cache(maxsize=1)
def load_faiss_db() -> FAISS:
    """
    Return the FAISS vector store.
    - In production (GCS_FAISS_BUCKET set): downloads from GCS on first call.
    - In local dev: loads from backend/data/faiss_index directly.
    Result is cached for the container lifetime.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    bucket_name = os.getenv("GCS_FAISS_BUCKET")

    if bucket_name:
        # ── Production path: download from GCS ───────────────────────────────
        tmp_dir = tempfile.mkdtemp()
        try:
            _download_from_gcs(bucket_name, tmp_dir)
            index_path = os.path.join(tmp_dir, "faiss_index")
            db = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True,
            )
        finally:
            # Cleanup zip, keep the loaded db in memory
            zip_path = os.path.join(tmp_dir, "faiss_index.zip")
            if os.path.exists(zip_path):
                os.remove(zip_path)
    else:
        # ── Local dev path: load from disk directly ───────────────────────────
        print(f"[faiss_loader] Loading FAISS index from {LOCAL_INDEX_PATH}…")
        db = FAISS.load_local(
            LOCAL_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    print("[faiss_loader] ✅ FAISS index loaded.")
    return db
