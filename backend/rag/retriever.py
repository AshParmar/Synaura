# backend/rag/retriever.py

from backend.rag.faiss_loader import load_faiss_db
from backend.rag.hybrid_retriever import hybrid_retrieve, build_bm25_retriever

# -------------------------
# 1. Load vector DB
# (production: downloads from GCS on cold start)
# (local dev: loads from backend/data/faiss_index)
# -------------------------
db = load_faiss_db()

# -------------------------
# 2. Initialize retrievers (once)
# -------------------------

# vector retriever
vector_retriever = db.as_retriever(search_kwargs={"k": 5})

# get all docs from FAISS (for BM25)
documents = db.similarity_search("", k=1000)

# BM25 retriever
bm25_retriever = build_bm25_retriever(documents)


# -------------------------
# 3. Hybrid Retrieval
# -------------------------
def retrieve_hybrid(query):
    return hybrid_retrieve(query, vector_retriever, bm25_retriever)


# -------------------------
# 4. Old Vector Retrieval (baseline)
# -------------------------
def retrieve_documents(query, k=10):
    return db.similarity_search(query, k=k)