import os
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "medical_docs")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "faiss_index")

def load_documents(data_path):
    documents = []
    for file in os.listdir(data_path):
        path = os.path.join(data_path, file)
        if not os.path.isfile(path):
            continue
        loader=TextLoader(path, encoding="utf-8")
        docs=loader.load()
        
        documents.extend(docs)
    return documents

def split_documents(documents):

    splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks=splitter.split_documents(documents)
    return chunks
    
def build_vector(chunks):
    embeddings=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_db=FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    vector_db.save_local(VECTOR_STORE_PATH)
    print(f"Vector database saved to {VECTOR_STORE_PATH}")
    return vector_db

def main():
    documents=load_documents(DATA_PATH)
    chunks=split_documents(documents)
    build_vector(chunks)

if __name__ == "__main__":
    main()
