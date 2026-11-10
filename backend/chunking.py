
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.ingestion import extract_pdf_text


def create_chunks():

    documents = extract_pdf_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []

    for document in documents:

        chunks = splitter.split_text(document["content"])

        for index, chunk in enumerate(chunks):

            all_chunks.append({
                "content": chunk,
                "metadata": {
                    **document["metadata"],
                    "chunk_id": index
                }
            })

    return all_chunks


if __name__ == "__main__":

    chunks = create_chunks()

    print("\nCHUNKING SUMMARY")
    print("================")
    print("Total chunks:", len(chunks))

    for chunk in chunks[:5]:
        print("\nSource:", chunk["metadata"]["source"])
        print("Page:", chunk["metadata"]["page"])
        print("Chunk ID:", chunk["metadata"]["chunk_id"])
        print("Content:", chunk["content"][:250])
