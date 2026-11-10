
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from backend.chunking import create_chunks


# Persistent database location
VECTORSTORE_DIR = Path("vectorstore")

COLLECTION_NAME = "manufacturing_sop_active"

# Local embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def create_vector_store():

    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Extracting and chunking documents...")

    chunks = create_chunks()

    # Only index active SOP revisions
    active_chunks = [
        chunk for chunk in chunks
        if chunk["metadata"]["status"] == "active"
    ]

    if not active_chunks:
        raise ValueError("No active document chunks found.")

    documents = []
    ids = []

    for chunk in active_chunks:

        documents.append(
            Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
        )

        metadata = chunk["metadata"]

        # Stable IDs prevent duplicate records on reruns
        chunk_id = (
            f'{metadata["source"]}_'
            f'{metadata["page"]}_'
            f'{metadata["chunk_id"]}'
        )

        ids.append(chunk_id)

    print("Creating ChromaDB vector store...")

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR)
    )

    # Add or update documents using stable IDs
    vector_store.add_documents(
        documents=documents,
        ids=ids
    )

    print("\nVECTOR DATABASE SUMMARY")
    print("=======================")
    print("Total extracted chunks:", len(chunks))
    print("Active chunks indexed:", len(active_chunks))
    print("Superseded chunks excluded:", len(chunks) - len(active_chunks))
    print("Embedding model:", EMBEDDING_MODEL)
    print("Collection:", COLLECTION_NAME)
    print("Storage location:", VECTORSTORE_DIR)

    return vector_store


if __name__ == "__main__":
    create_vector_store()
