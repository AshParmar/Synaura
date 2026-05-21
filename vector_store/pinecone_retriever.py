# vector_store/pinecone_retriever.py
"""
Production retriever backed by Pinecone.

In production (Cloud Run), this replaces the FAISS-based retriever.
Locally, you can still fall back to FAISS if PINECONE_API_KEY is not set.

Usage:
    from vector_store.pinecone_retriever import retrieve_pinecone
    docs = retrieve_pinecone("pleural effusion treatment", k=5)
"""

import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from vector_store.pinecone_client import get_pinecone_index

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_embeddings: HuggingFaceEmbeddings | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def retrieve_pinecone(query: str, k: int = 5) -> list[Document]:
    """
    Embed `query` and return the top-k semantically similar chunks from Pinecone
    as LangChain Document objects (so they're drop-in compatible with existing code).
    """
    embeddings = _get_embeddings()
    query_vector = embeddings.embed_query(query)

    index = get_pinecone_index()
    response = index.query(
        vector=query_vector,
        top_k=k,
        include_metadata=True,
    )

    docs = []
    for match in response.get("matches", []):
        metadata = match.get("metadata", {})
        text = metadata.pop("text", "")
        docs.append(Document(page_content=text, metadata=metadata))

    return docs
