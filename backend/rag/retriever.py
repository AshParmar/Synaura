# backend/rag/retriever.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


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


def retrieve_documents(query, k=10):

    db = load_vector_db()

    docs = db.similarity_search(query, k=k)

    return docs