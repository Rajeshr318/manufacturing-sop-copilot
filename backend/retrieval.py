

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from backend.vector_store import (
    VECTORSTORE_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL
)

# Initial threshold based on our diagnostic tests.
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


def retrieve_documents(question: str, top_k: int = 4):

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        question,
        k=top_k
    )

    retrieved_chunks = []

    for document, score in results:

        distance = float(score)

        # Reject weak semantic matches.
        if distance > RELEVANCE_THRESHOLD:
            continue

        metadata = document.metadata

        # Reject superseded revisions.
        if metadata.get("status") != "active":
            continue

        retrieved_chunks.append({
            "content": document.page_content,
            "source": metadata.get("source"),
            "page": metadata.get("page"),
            "status": metadata.get("status"),
            "score": round(distance, 4)
        })

    return retrieved_chunks


if __name__ == "__main__":

    question = (
        "What is the recommended coolant concentration "
        "for the TX-200 CNC machine?"
    )

    results = retrieve_documents(question)

    print("\nQUESTION:", question)
    print("\nRELEVANT DOCUMENTS:")

    for result in results:
        print("\nSource:", result["source"])
        print("Page:", result["page"])
        print("Distance:", result["score"])
        print("Content:", result["content"][:300])
