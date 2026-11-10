import pymupdf
from pathlib import Path

DOCUMENTS_DIR = Path("documents")


def get_revision_status(filename):
    name = filename.lower().replace("-", "").replace("_", "")

    if "qcsop014" in name and "rev03" in name:
        return "superseded"

    return "active"


def extract_pdf_text():
    documents = []

    for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):

        status = get_revision_status(pdf_path.name)

        with pymupdf.open(pdf_path) as pdf:

            for page_number, page in enumerate(pdf, start=1):

                text = page.get_text("text").strip()

                if not text:
                    continue

                documents.append({
                    "content": text,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_number,
                        "status": status
                    }
                })

    return documents


if __name__ == "__main__":

    extracted_documents = extract_pdf_text()

    print("PDF INGESTION SUMMARY")
    print("=====================")
    print("Total extracted pages:", len(extracted_documents))

    for doc in extracted_documents:
        print("\nSource:", doc["metadata"]["source"])
        print("Page:", doc["metadata"]["page"])
        print("Status:", doc["metadata"]["status"])
        print("Extracted text:", doc["content"][:250])
