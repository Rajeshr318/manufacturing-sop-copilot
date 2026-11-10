
import os
import json
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.retrieval import retrieve_documents

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

NO_ANSWER = (
    "I could not find sufficient information to answer "
    "this question in the available manufacturing documents."
)


def get_llm():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing from .env")

    if not GROQ_MODEL:
        raise ValueError("GROQ_MODEL is missing from .env")

    return ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        api_key=GROQ_API_KEY
    )


def parse_llm_response(response_text):
    """Parse the LLM's JSON response safely."""

    response_text = response_text.strip()

    # Remove optional Markdown code fences
    response_text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None


def generate_answer(question: str):

    # Step 1: Retrieve relevant active SOP passages
    retrieved_chunks = retrieve_documents(question, top_k=4)

    active_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("status") == "active"
    ]

    if not active_chunks:
        return {
            "answer": NO_ANSWER,
            "sources": []
        }

    # Step 2: Assign source IDs to retrieved passages
    context_parts = []
    source_map = {}

    for index, chunk in enumerate(active_chunks, start=1):

        source_id = f"S{index}"

        source_map[source_id] = {
            "filename": chunk["source"],
            "page": chunk["page"]
        }

        context_parts.append(
            f"""
            Source ID: {source_id}
            Filename: {chunk['source']}
            Page: {chunk['page']}

            Content:
            {chunk['content']}
            """
        )

    context = "\n\n".join(context_parts)

    # Step 3: Create the RAG prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a Manufacturing SOP AI Copilot.

            Answer questions using ONLY the supplied document passages.

            STRICT RULES:

            1. Never invent technical specifications or procedures.
            2. Use only active document revisions.
            3. Never treat superseded revisions as valid instructions.
            4. Preserve important safety instructions.
            5. If the supplied passages do not contain enough
               information to answer, use the exact no-answer message.
            6. Cite only source IDs whose passages directly support
               the information in your answer.
            7. Never cite a passage merely because it was retrieved.
            8. Do not invent source IDs.
            9. Keep answers concise and clear.

            Return ONLY valid JSON in this exact structure:

            {{
                "answer": "Your answer here",
                "citations": ["S1", "S2"]
            }}

            If you cannot answer, return:

            {{
                "answer": "{no_answer}",
                "citations": []
            }}
            """
        ),
        (
            "human",
            """
            DOCUMENT PASSAGES:

            {context}

            USER QUESTION:
            {question}
            """
        )
    ])

    # Step 4: Generate answer
    chain = prompt | get_llm()

    response = chain.invoke({
        "context": context,
        "question": question,
        "no_answer": NO_ANSWER
    })

    # Step 5: Parse the response
    parsed_response = parse_llm_response(response.content)

    # Fail safely if the model returns invalid JSON
    if not isinstance(parsed_response, dict):
        return {
            "answer": NO_ANSWER,
            "sources": []
        }

    answer = parsed_response.get("answer")
    citations = parsed_response.get("citations")

    if not isinstance(answer, str) or not isinstance(citations, list):
        return {
            "answer": NO_ANSWER,
            "sources": []
        }

    answer = answer.strip()

    # Step 6: Handle unsupported questions
    if not answer or NO_ANSWER.lower() in answer.lower():
        return {
            "answer": NO_ANSWER,
            "sources": []
        }

    # Step 7: Validate citations against retrieved source IDs
    sources = []

    for source_id in citations:

        if not isinstance(source_id, str):
            continue

        if source_id not in source_map:
            continue

        source = source_map[source_id]

        if source not in sources:
            sources.append(source)

    # Do not display an answer without a valid supporting citation
    if not sources:
        return {
            "answer": NO_ANSWER,
            "sources": []
        }

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    test_questions = [
    "What is the BH-220 outer diameter tolerance, nominal dimension, measuring instrument, and defect classification?",

    "How frequently should spindle runout be checked, who is responsible, and what is the maximum permitted runout?",

    "What is the required disposition when a critical defect is identified in an incoming material lot?"
]

    for question in test_questions:

        result = generate_answer(question)

        print("\n" + "=" * 60)
        print("USER QUESTION:")
        print(question)

        print("\nGENERATED ANSWER:")
        print(result["answer"])

        print("\nSUPPORTING SOURCES:")

        if result["sources"]:
            for source in result["sources"]:
                print(
                    f"- {source['filename']} | Page {source['page']}"
                )
        else:
            print("No supporting sources found.")
