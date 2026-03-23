from langchain_community.retrievers import BM25Retriever

def build_bm25_retriever(documents):
    """
    Build BM25 keyword-based retriever
    """
    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = 5
    return bm25


def hybrid_retrieve(query, vector_retriever, bm25_retriever, k=8):
    """
    Combine vector + BM25 retrieval
    """

    # -------------------------
    # 1. Vector search
    # -------------------------
    # Use the correct method for VectorStoreRetriever
    docs_vec = vector_retriever.invoke(query)

    # -------------------------
    # 2. Keyword search (BM25)
    # -------------------------
    docs_bm25 = bm25_retriever.invoke(query)

    # -------------------------
    # 3. Combine results
    # -------------------------
    combined = docs_vec + docs_bm25

    # -------------------------
    # 4. Remove duplicates
    # -------------------------
    unique_docs = list({
        doc.page_content: doc for doc in combined
    }.values())

    return unique_docs[:k]