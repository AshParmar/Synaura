# backend/rag/retriever.py

from backend.rag.faiss_loader import load_faiss_db
from backend.rag.hybrid_retriever import hybrid_retrieve, build_bm25_retriever

# ── Lazy-loaded database & retrievers ─────────────────────────────────────────
_db = None
_vector_retriever = None
_bm25_retriever = None


def get_retrievers():
    """Lazily load and cache the FAISS DB and retrievers to avoid network/disk calls on import."""
    global _db, _vector_retriever, _bm25_retriever
    if _db is None:
        _db = load_faiss_db()
        _vector_retriever = _db.as_retriever(search_kwargs={"k": 5})
        # get all docs from FAISS (for BM25)
        documents = _db.similarity_search("", k=1000)
        _bm25_retriever = build_bm25_retriever(documents)
    return _db, _vector_retriever, _bm25_retriever


# -------------------------
# 3. Hybrid Retrieval
# -------------------------
def retrieve_hybrid(query):
    _, vector_retriever, bm25_retriever = get_retrievers()
    return hybrid_retrieve(query, vector_retriever, bm25_retriever)


# -------------------------
# 4. Old Vector Retrieval (baseline)
# -------------------------
def retrieve_documents(query, k=10):
    db, _, _ = get_retrievers()
    return db.similarity_search(query, k=k)