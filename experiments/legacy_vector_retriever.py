"""
Legacy vector-only retriever for experiment isolation.
"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load vector DB (FAISS)
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

db = load_vector_db()

def retrieve_documents(query, k=10):
    return db.similarity_search(query, k=k)
