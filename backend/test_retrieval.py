
from backend.retrieval import retrieve_documents

questions = [
    "What is the recommended coolant concentration for TX-200?",
    "What is the normal hydraulic pressure range for TX-200?",
    "What is the monthly electricity consumption of the factory?"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    results = retrieve_documents(question, top_k=4)

    if not results:
        print("RESULT: No relevant documents found.")
        continue

    print("RESULT: Relevant documents found.")

    for result in results:
        print(
            f"\nSource: {result['source']}"
            f"\nPage: {result['page']}"
            f"\nDistance: {result['score']}"
        )
