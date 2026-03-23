# backend/rag/retriever.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from backend.rag.hybrid_retriever import hybrid_retrieve, build_bm25_retriever

# -------------------------
# 1. Load vector DB
# -------------------------
def load_vector_db():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        "backend/data/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return db


# -------------------------
# 2. Initialize retrievers (once)
# -------------------------
db = load_vector_db()

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