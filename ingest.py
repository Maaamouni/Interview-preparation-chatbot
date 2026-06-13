import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------
DATA_PATH = "./External Documents"          # folder containing PDFs
DB_PATH = "chroma_db"        # where vector DB will be stored

# ----------------------------
# 1. LOAD DOCUMENTS
# ----------------------------
def load_documents(data_path):
    documents = []

    for file in Path(data_path).rglob("*.pdf"):
        print(f"[INFO] Loading: {file}")
        loader = PyPDFLoader(str(file))
        documents.extend(loader.load())

    return documents


# ----------------------------
# 2. CHUNK DOCUMENTS
# ----------------------------
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)
    print(f"[INFO] Total chunks created: {len(chunks)}")

    return chunks


# ----------------------------
# 3. EMBEDDINGS MODEL
# ----------------------------
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ----------------------------
# 4. CREATE VECTOR DB
# ----------------------------
def create_vectorstore(chunks, embeddings):
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    vectorstore.persist()
    print(f"[INFO] Vector DB stored at: {DB_PATH}")

    return vectorstore


# ----------------------------
# MAIN PIPELINE
# ----------------------------
def main():
    print("[INFO] Starting ingestion pipeline...")

    # Step 1: Load
    documents = load_documents(DATA_PATH)

    if not documents:
        print("[ERROR] No documents found!")
        return

    # Step 2: Chunk
    chunks = split_documents(documents)

    # Step 3: Embeddings
    embeddings = get_embeddings()

    # Step 4: Store in ChromaDB
    create_vectorstore(chunks, embeddings)

    print("[INFO] Ingestion completed successfully!")


if __name__ == "__main__":
    main()