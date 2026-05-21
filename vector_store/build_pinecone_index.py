# vector_store/build_pinecone_index.py
"""
One-time migration script: reads your existing medical docs, generates embeddings
with the same HuggingFace model already used in the FAISS pipeline, and upserts
them into Pinecone.

Run once (from project root):
    python -m vector_store.build_pinecone_index

Prerequisites:
  - PINECONE_API_KEY and PINECONE_INDEX_NAME set in .env
  - Medical docs present at backend/data/medical_docs/
"""

import os
import uuid

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

from vector_store.pinecone_client import get_pinecone_index

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "medical_docs")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 100   # Pinecone upsert batch size


def load_documents(data_path: str):
    """Load all .txt files from the medical docs directory."""
    documents = []
    for filename in os.listdir(data_path):
        filepath = os.path.join(data_path, filename)
        if not os.path.isfile(filepath):
            continue
        loader = TextLoader(filepath, encoding="utf-8")
        documents.extend(loader.load())
    print(f"[build_pinecone_index] Loaded {len(documents)} source document(s).")
    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"[build_pinecone_index] Split into {len(chunks)} chunks.")
    return chunks


def upsert_to_pinecone(chunks, embeddings_model):
    """Embed chunks in batches and upsert to Pinecone."""
    index = get_pinecone_index()
    texts = [c.page_content for c in chunks]

    print(f"[build_pinecone_index] Generating embeddings for {len(texts)} chunks…")
    vectors = embeddings_model.embed_documents(texts)

    # Build Pinecone vector records
    records = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        records.append({
            "id": str(uuid.uuid4()),
            "values": vec,
            "metadata": {
                "text": chunk.page_content,
                "source": chunk.metadata.get("source", "unknown"),
            },
        })

    # Upsert in batches
    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start : start + BATCH_SIZE]
        index.upsert(vectors=batch)
        print(f"[build_pinecone_index] Upserted {start + len(batch)}/{len(records)} vectors.")

    print("[build_pinecone_index] ✅ Pinecone index build complete.")


def main():
    documents = load_documents(DATA_PATH)
    chunks = split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    upsert_to_pinecone(chunks, embeddings)


if __name__ == "__main__":
    main()
