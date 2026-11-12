
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from backend.vector_store import (
    VECTORSTORE_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL
)

RELEVANCE_THRESHOLD = 1.40


def get_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR)
    )

    return vector_store


def retrieve_multiple_documents(
    queries: list[str],
    top_k: int = 6,
    max_chunks: int = 12
):
    """
    Retrieve relevant chunks for multiple query variations.

    The vector store and embedding model are initialized once.
    Duplicate chunks are removed before returning the results.
    """

    vector_store = get_vector_store()

    unique_chunks = {}

    for query in queries:

        if not query or not query.strip():
            continue

        results = vector_store.similarity_search_with_score(
            query,
            k=top_k
        )

        for document, score in results:

            distance = float(score)

            if distance > RELEVANCE_THRESHOLD:
                continue

            metadata = document.metadata

            if metadata.get("status") != "active":
                continue

            chunk = {
                "content": document.page_content,
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "status": metadata.get("status"),
                "score": round(distance, 4)
            }

            # Avoid adding the same document chunk more than once.
            chunk_key = (
                chunk["source"],
                chunk["page"],
                chunk["content"]
            )

            if (
                chunk_key not in unique_chunks
                or distance < unique_chunks[chunk_key]["score"]
            ):
                unique_chunks[chunk_key] = chunk

    # Best semantic matches first.
    retrieved_chunks = sorted(
        unique_chunks.values(),
        key=lambda chunk: chunk["score"]
    )

    return retrieved_chunks[:max_chunks]


def retrieve_documents(question: str, top_k: int = 4):

    return retrieve_multiple_documents(
        queries=[question],
        top_k=top_k,
        max_chunks=top_k
    )
