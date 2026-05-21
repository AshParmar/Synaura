# vector_store/pinecone_client.py
"""
Pinecone client singleton.

Requires in .env:
  PINECONE_API_KEY        — your Pinecone API key
  PINECONE_ENVIRONMENT    — e.g. us-east-1-aws
  PINECONE_INDEX_NAME     — e.g. synaura-radiology
"""

import os
from functools import lru_cache
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "synaura-radiology")
EMBEDDING_DIMENSION = 384   # all-MiniLM-L6-v2 outputs 384-dimensional vectors


@lru_cache(maxsize=1)
def get_pinecone_index():
    """
    Return a connected Pinecone Index object.
    Creates the index (serverless, cosine) if it does not already exist.
    Result is cached for the process lifetime.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "PINECONE_API_KEY is not set. Copy .env.example → .env and fill in your Pinecone key."
        )

    pc = Pinecone(api_key=api_key)

    # Create index only if it doesn't exist yet
    existing = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return pc.Index(INDEX_NAME)
