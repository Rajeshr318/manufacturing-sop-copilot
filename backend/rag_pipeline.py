
import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from backend.retrieval import retrieve_documents


# =============================================================================
# CONFIGURATION
# =============================================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b").strip()
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
).strip()

ENABLE_OLLAMA_FALLBACK = (
    os.getenv("ENABLE_OLLAMA_FALLBACK", "true").lower()
    in {"true", "1", "yes", "on"}
)

NO_ANSWER = (
    "I could not find relevant information in the available "
    "manufacturing documents."
)

SERVICE_ERROR = (
    "ForgeIQ is temporarily unable to generate an answer. "
    "Please try again later."
)

MAX_NORMAL_CHUNKS = 8
MAX_MAINTENANCE_CHUNKS = 5
MAX_CONTEXT_CHARACTERS = 6500

MAINTENANCE_DOCUMENT_KEY = "TX-200_Preventive_Maintenance"

COMPLEX_DEFECT_KEYWORDS = (
    "defect",
    "defective",
    "rejection",
    "reject",
    "quarantine",
    "non-conforming",
    "nonconforming",
)


# =============================================================================
# LLM PROVIDERS
# =============================================================================

def get_llm():
    """Create the primary Groq language model."""

    if not GROQ_API_KEY or not GROQ_MODEL:
        raise RuntimeError(
            "GROQ_API_KEY or GROQ_MODEL is missing from the environment."
        )

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.1,
        max_tokens=1200,
        max_retries=0,
    )


def get_ollama_llm():
    """Create the local Ollama fallback model with JSON output."""

    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
        num_predict=1200,
        format="json",
    )


# =============================================================================
# RETRIEVAL QUERY GENERATION
# =============================================================================

def build_retrieval_queries(question: str) -> list[str]:
    """
    Generate focused retrieval queries based on the user's question.

    QC-specific expansion uses word-boundary matching so that
    words such as 'preventive' do not accidentally match 'rev'.
    """

    question = question.strip()
    question_lower = question.lower()

    queries = [question]

    is_qc_question = bool(
        re.search(
            r"\b(qc|quality|inspection|sampling|sample|lot|"
            r"revision|rev|defect|reject|rejection|superseded|"
            r"supersede|acceptance)\b",
            question_lower,
        )
    )

    is_maintenance_question = (
        "tx-200" in question_lower
        or "preventive maintenance" in question_lower
        or "maintenance procedure" in question_lower
    )

    if is_qc_question:
        queries.extend([
            (
                f"{question} quality control sampling "
                "inspection incoming material"
            ),
            (
                f"{question} lot-size sampling plan "
                "sample quantity acceptance rejection"
            ),
            (
                "incoming material inspection lot size "
                "sampling table sample quantity"
            ),
            (
                "QC SOP revision history current revision "
                "Rev04 supersedes Rev03"
            ),
        ])

    elif is_maintenance_question:
        queries.extend([
            (
                "TX-200 yearly preventive maintenance "
                "annual maintenance activities"
            ),
            (
                "TX-200 yearly maintenance hydraulic oil "
                "ISO VG46 geometric accuracy coolant replacement"
            ),
            (
                "TX-200 preventive maintenance schedule "
                "Maintenance Engineer yearly"
            ),
        ])

    else:
        queries.append(
            f"{question} manufacturing SOP procedure "
            "responsibilities requirements"
        )

    unique_queries = []
    seen = set()

    for query in queries:
        normalized = query.strip().lower()

        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_queries.append(query.strip())

    return unique_queries


# =============================================================================
# CHUNK METADATA AND CONTENT HELPERS
# =============================================================================

def get_chunk_metadata(chunk: Any) -> dict:
    """
    Support both LangChain Documents and dictionary-based chunks.

    Dictionary chunks may contain metadata either under 'metadata'
    or directly at the top level.
    """

    if isinstance(chunk, dict):
        metadata = chunk.get("metadata", {})

        if not isinstance(metadata, dict):
            metadata = {}

        combined_metadata = {
            key: value
            for key, value in chunk.items()
            if key not in {
                "content",
                "page_content",
                "metadata",
                "score",
            }
        }

        # Nested metadata takes priority.
        combined_metadata.update(metadata)

        return combined_metadata

    metadata = getattr(chunk, "metadata", {})

    return metadata if isinstance(metadata, dict) else {}


def get_chunk_content(chunk: Any) -> str:
    """Retrieve text content from a Document or dictionary."""

    if isinstance(chunk, dict):
        return str(
            chunk.get("content")
            or chunk.get("page_content")
            or ""
        )

    return str(
        getattr(chunk, "page_content", "")
        or getattr(chunk, "content", "")
    )


def get_chunk_score(chunk: Any) -> float:
    """Read retrieval score or distance with a safe default."""

    if isinstance(chunk, dict):
        value = chunk.get(
            "score",
            chunk.get("distance", chunk.get("relevance_score", 999))
        )
    else:
        metadata = get_chunk_metadata(chunk)

        value = metadata.get(
            "score",
            metadata.get("distance", 999)
        )

    try:
        return float(value)
    except (TypeError, ValueError):
        return 999.0


# =============================================================================
# CHUNK SELECTION
# =============================================================================

def select_relevant_chunks(
    chunks: list,
    question: str,
) -> list:
    """
    Deduplicate and select relevant active chunks.

    TX-200 maintenance questions are restricted to the TX-200
    maintenance manual.
    """

    question_lower = question.lower()

    is_maintenance_question = (
        "tx-200" in question_lower
        or "preventive maintenance" in question_lower
        or "maintenance procedure" in question_lower
    )

    filtered_chunks = []

    for chunk in chunks:
        content = get_chunk_content(chunk)
        metadata = get_chunk_metadata(chunk)

        if not content.strip():
            continue

        status = str(
            metadata.get("status", "active")
        ).lower()

        if status not in {"active", "current", ""}:
            continue

        if is_maintenance_question:
            source = str(
                metadata.get("source", "")
            ).lower()

            if (
                "tx-200" not in source
                and MAINTENANCE_DOCUMENT_KEY.lower() not in source
            ):
                continue

        filtered_chunks.append(chunk)

    unique_chunks = {}

    for chunk in filtered_chunks:
        metadata = get_chunk_metadata(chunk)
        content = get_chunk_content(chunk)

        key = (
            str(metadata.get("source", "unknown")),
            str(metadata.get("page", "unknown")),
            content.strip(),
        )

        score = get_chunk_score(chunk)

        if key not in unique_chunks:
            unique_chunks[key] = chunk
        else:
            existing_score = get_chunk_score(
                unique_chunks[key]
            )

            if score < existing_score:
                unique_chunks[key] = chunk

    selected_chunks = list(unique_chunks.values())
    selected_chunks.sort(key=get_chunk_score)

    maximum = (
        MAX_MAINTENANCE_CHUNKS
        if is_maintenance_question
        else MAX_NORMAL_CHUNKS
    )

    return selected_chunks[:maximum]


# =============================================================================
# CONTEXT BUILDING
# =============================================================================

def build_context(chunks: list) -> tuple[str, dict]:
    """Build numbered source context and its source metadata mapping."""

    context_parts = []
    source_map = {}

    total_characters = 0

    for index, chunk in enumerate(chunks, start=1):
        source_id = f"S{index}"

        content = get_chunk_content(chunk)
        metadata = get_chunk_metadata(chunk)

        source = str(
            metadata.get("source", "Unknown document")
        )

        # Preserve the original page value, including integer page numbers.
        page = metadata.get("page", "Unknown")

        source_map[source_id] = {
            "source": source,
            "page": page,
            "metadata": metadata,
        }

        section = (
            f"[{source_id}]\n"
            f"Document: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{content.strip()}"
        )

        remaining = MAX_CONTEXT_CHARACTERS - total_characters

        if remaining <= 0:
            break

        if len(section) > remaining:
            section = section[:remaining]

        context_parts.append(section)
        total_characters += len(section)

    return "\n\n".join(context_parts), source_map


# =============================================================================
# RESPONSE EXTRACTION
# =============================================================================

def extract_response_text(response: Any) -> str:
    """Extract text from LangChain or plain-text responses."""

    if response is None:
        return ""

    if isinstance(response, str):
        return response.strip()

    content = getattr(response, "content", None)

    if content is None and isinstance(response, dict):
        content = response.get(
            "content",
            response.get("text", "")
        )

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                text_value = item.get("text")

                if text_value:
                    text_parts.append(str(text_value))

        return "\n".join(text_parts).strip()

    return str(content or "").strip()


def extract_json_response(response: Any) -> dict | None:
    """Parse a JSON object from the LLM response."""

    raw_text = extract_response_text(response)

    if not raw_text:
        return None

    cleaned = raw_text.strip()

    # Remove Markdown JSON fences.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Attempt to extract a JSON object from surrounding text.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    try:
        parsed = json.loads(cleaned[start:end + 1])

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        return None

    return None


# =============================================================================
# CITATION VALIDATION
# =============================================================================

def deduplicate_sources(source_ids: list[str]) -> list[str]:
    """Remove duplicate source IDs while preserving order."""

    result = []
    seen = set()

    for source_id in source_ids:
        source_id = str(source_id).strip()

        if source_id and source_id not in seen:
            seen.add(source_id)
            result.append(source_id)

    return result


def validate_citations(
    answer: str,
    source_map: dict,
) -> bool:
    """Validate that every inline citation exists in the source map."""

    if not answer or not isinstance(answer, str):
        return False

    citations = re.findall(
        r"\[(S\d+)\]",
        answer,
    )

    if not citations:
        return False

    available_sources = set(source_map.keys())

    return all(
        citation in available_sources
        for citation in citations
    )


def validate_answer_payload(
    payload: Any,
    source_map: dict,
) -> dict | None:
    """Validate the structured LLM response and its citations."""

    if not isinstance(payload, dict):
        return None

    status = str(
        payload.get("status", "")
    ).strip().lower()

    answer = payload.get("answer", "")

    if not isinstance(answer, str):
        return None

    answer = answer.strip()

    if status == "no_answer":
        return {
            "status": "no_answer",
            "answer": NO_ANSWER,
            "sources": [],
        }

    if status != "answered" or not answer:
        return None

    if not validate_citations(answer, source_map):
        return None

    cited_ids = re.findall(
        r"\[(S\d+)\]",
        answer,
    )

    cited_ids = deduplicate_sources(cited_ids)

    return {
        "status": "answered",
        "answer": answer,
        "sources": [
            {
                "id": source_id,
                "citation_id": source_id,
                "source": source_map[source_id]["source"],
                "page": source_map[source_id]["page"],
            }
            for source_id in cited_ids
        ],
    }


# =============================================================================
# PROMPT BUILDERS
# =============================================================================

def build_answer_prompt(
    question: str,
    context: str,
) -> str:
    """Build a grounded-answer prompt."""

    return f"""
You are ForgeIQ, an AI assistant for manufacturing SOP documents.

Answer the user's question using ONLY the supplied document context.

USER QUESTION:
{question}

DOCUMENT CONTEXT:
{context}

STRICT RULES:

1. Use only facts explicitly supported by the supplied context.
2. Do not invent procedures, quantities, responsibilities, dates or values.
3. Cite every factual statement using the source IDs provided.
4. Use citations exactly in this format: [S1], [S2], etc.
5. Never create a citation ID that is not present in the context.
6. Never present a superseded document as the current procedure.
7. If the context does not contain enough information, return status "no_answer".
8. Preserve exact technical values, units and document revisions.
9. Answer the question directly and clearly.
10. Do not use outside knowledge to fill missing information.

REVISION AND SAMPLING RULES:

- Identify the current approved revision when asked which revision to follow.
- Use the lot-size range from the current sampling table.
- Do not confuse an older fixed sample size with the current lot-size plan.
- Explain why an older revision was superseded only when supported by revision history.

Return ONLY one valid JSON object.

For a supported answer:
{{
  "status": "answered",
  "answer": "Your answer with inline citations such as [S1]."
}}

For an unsupported answer:
{{
  "status": "no_answer",
  "answer": "{NO_ANSWER}"
}}
""".strip()


def build_complex_section_prompt(
    question: str,
    context: str,
    section_name: str,
    section_instruction: str,
) -> str:
    """Build a focused prompt for one section of a complex SOP answer."""

    return f"""
You are ForgeIQ, a manufacturing SOP assistant.

Answer ONLY the requested section of the user's question.

USER QUESTION:
{question}

SECTION:
{section_name}

SECTION INSTRUCTION:
{section_instruction}

DOCUMENT CONTEXT:
{context}

STRICT RULES:

1. Use only the supplied document context.
2. Do not invent facts or procedures.
3. Cite every factual statement using the supplied source IDs.
4. Use citations exactly as [S1], [S2], etc.
5. Do not create source IDs.
6. Preserve technical values, quantities and units.
7. If the requested section is not supported, return status "no_answer".
8. Do not use outside knowledge.

Return ONLY valid JSON:

{{
  "status": "answered",
  "answer": "Section answer with inline citations."
}}

Or:

{{
  "status": "no_answer",
  "answer": "{NO_ANSWER}"
}}
""".strip()


# =============================================================================
# PROVIDER RESPONSE GENERATION
# =============================================================================

def generate_validated_response(
    prompt: str,
    source_map: dict,
) -> dict:
    """Generate an answer using Groq, then Ollama if necessary."""

    providers = []

    try:
        providers.append(("Groq", get_llm()))
    except Exception as error:
        print(f"WARNING: Groq initialization failed: {error}")

    if ENABLE_OLLAMA_FALLBACK:
        try:
            providers.append(("Ollama", get_ollama_llm()))
        except Exception as error:
            print(f"WARNING: Ollama initialization failed: {error}")

    if not providers:
        print("ERROR: No LLM provider is available.")

        return {
            "status": "error",
            "answer": SERVICE_ERROR,
            "sources": [],
        }

    provider_errors = []

    for provider_name, llm in providers:
        try:
            print(f"DEBUG: LLM provider: {provider_name}")

            response = llm.invoke(prompt)

            if provider_name == "Ollama":
                print(
                    "DEBUG: Raw Ollama response:",
                    extract_response_text(response),
                )

            payload = extract_json_response(response)

            if payload is None:
                print(
                    f"WARNING: {provider_name} returned invalid JSON."
                )

                provider_errors.append(
                    f"{provider_name}: invalid JSON"
                )
                continue

            validated = validate_answer_payload(
                payload,
                source_map,
            )

            if validated is None:
                print(
                    f"WARNING: {provider_name} returned an "
                    "invalid answer or citation."
                )

                provider_errors.append(
                    f"{provider_name}: invalid answer or citation"
                )
                continue

            print(
                f"DEBUG: {provider_name} response validated: "
                f"{validated['status']}"
            )

            return validated

        except Exception as error:
            print(
                f"WARNING: {provider_name} generation failed: {error}"
            )

            provider_errors.append(
                f"{provider_name}: {str(error)}"
            )

    print("WARNING: No provider returned a valid grounded answer.")

    # If every provider failed operationally, return a service error.
    # Invalid model output is treated as an unanswerable response.
    if provider_errors and all(
        "invalid JSON" not in error
        and "invalid answer or citation" not in error
        for error in provider_errors
    ):
        return {
            "status": "error",
            "answer": SERVICE_ERROR,
            "sources": [],
        }

    return {
        "status": "no_answer",
        "answer": NO_ANSWER,
        "sources": [],
    }


# =============================================================================
# COMPLEX SOP ANSWER GENERATION
# =============================================================================

def generate_complex_sop_answer(
    context: str,
    source_map: dict,
    question: str = "",
) -> dict:
    """
    Generate a complex answer in focused sections.

    The default question value maintains compatibility with existing
    callers that provide only context and source_map.

    All sections must succeed. Partial answers are never returned.
    """

    sections = [
        (
            "Sampling and defect criteria",
            (
                "Explain the relevant sampling plan, lot-size range, "
                "sample quantity, acceptance criteria and rejection "
                "criteria supported by the documents."
            ),
        ),
        (
            "Rejection, quarantine and escalation",
            (
                "Explain the documented rejection process, quarantine "
                "requirements and escalation responsibilities."
            ),
        ),
        (
            "Personnel and records",
            (
                "Explain the documented responsible personnel, "
                "inspection records and required forms."
            ),
        ),
    ]

    section_answers = []
    all_sources = []

    for section_name, instruction in sections:
        prompt = build_complex_section_prompt(
            question=question,
            context=context,
            section_name=section_name,
            section_instruction=instruction,
        )

        result = generate_validated_response(
            prompt,
            source_map,
        )

        if result["status"] != "answered":
            print(
                "WARNING: Complex answer generation failed for "
                f"section: {section_name}"
            )

            # Do not return a partial answer.
            # Preserve service/provider errors for the caller.
            if result["status"] == "error":
                return {
                    "status": "error",
                    "answer": SERVICE_ERROR,
                    "sources": [],
                }

            return {
                "status": "no_answer",
                "answer": NO_ANSWER,
                "sources": [],
            }

        section_answers.append(
            f"**{section_name}**\n{result['answer']}"
        )

        all_sources.extend(
            result.get("sources", [])
        )

    unique_sources = []
    seen_sources = set()

    for source in all_sources:
        source_id = source.get("id")

        if source_id and source_id not in seen_sources:
            seen_sources.add(source_id)
            unique_sources.append(source)

    return {
        "status": "answered",
        "answer": "\n\n".join(section_answers),
        "sources": unique_sources,
    }


# =============================================================================
# MAIN RAG PIPELINE
# =============================================================================

def generate_answer(question: str) -> dict:
    """
    Main ForgeIQ RAG pipeline.

    1. Validate question.
    2. Generate retrieval queries.
    3. Retrieve document chunks.
    4. Merge and deduplicate chunks.
    5. Select relevant active chunks.
    6. Build context and source mapping.
    7. Generate and validate the answer.
    8. Return answer and source metadata.
    """

    if not isinstance(question, str) or not question.strip():
        return {
            "status": "no_answer",
            "answer": NO_ANSWER,
            "sources": [],
        }

    question = question.strip()

    try:
        queries = build_retrieval_queries(question)

        print("\n========== RETRIEVAL QUERIES ==========")

        for index, query in enumerate(queries, start=1):
            print(f"{index}. {query}")

        print("=======================================\n")

        retrieved_chunks = []

        for query in queries:
            results = retrieve_documents(
                question=query,
                top_k=10,
            )

            if results:
                retrieved_chunks.extend(results)

        if not retrieved_chunks:
            print("DEBUG: No document chunks retrieved.")

            return {
                "status": "no_answer",
                "answer": NO_ANSWER,
                "sources": [],
            }

        # Merge duplicate chunks from multiple retrieval queries.
        merged_chunks = {}

        for chunk in retrieved_chunks:
            metadata = get_chunk_metadata(chunk)
            content = get_chunk_content(chunk)

            key = (
                str(metadata.get("source", "unknown")),
                str(metadata.get("page", "unknown")),
                content.strip(),
            )

            if key not in merged_chunks:
                merged_chunks[key] = chunk
            else:
                current_score = get_chunk_score(
                    merged_chunks[key]
                )

                new_score = get_chunk_score(chunk)

                if new_score < current_score:
                    merged_chunks[key] = chunk

        unique_chunks = list(merged_chunks.values())

        print(
            "DEBUG: Unique retrieved chunks:",
            len(unique_chunks),
        )

        selected_chunks = select_relevant_chunks(
            unique_chunks,
            question,
        )

        print(
            "DEBUG: Selected chunks:",
            len(selected_chunks),
        )

        if not selected_chunks:
            print("DEBUG: No relevant active chunks selected.")

            return {
                "status": "no_answer",
                "answer": NO_ANSWER,
                "sources": [],
            }

        context, source_map = build_context(
            selected_chunks
        )

        if not context.strip() or not source_map:
            print("DEBUG: Context construction returned empty data.")

            return {
                "status": "no_answer",
                "answer": NO_ANSWER,
                "sources": [],
            }

        print(
            "DEBUG: Context length:",
            len(context),
        )

        print(
            "DEBUG: Available sources:",
            list(source_map.keys()),
        )

        question_lower = question.lower()

        is_complex_question = (
            any(
                keyword in question_lower
                for keyword in COMPLEX_DEFECT_KEYWORDS
            )
            and (
                " and " in question_lower
                or "why" in question_lower
                or "how" in question_lower
                or "explain" in question_lower
                or "procedure" in question_lower
            )
        )

        if is_complex_question:
            print("DEBUG: Using complex SOP answer generation.")

            return generate_complex_sop_answer(
                context=context,
                source_map=source_map,
                question=question,
            )

        prompt = build_answer_prompt(
            question=question,
            context=context,
        )

        return generate_validated_response(
            prompt,
            source_map,
        )

    except Exception as error:
        print(f"ERROR: RAG pipeline failed: {error}")

        return {
            "status": "error",
            "answer": SERVICE_ERROR,
            "sources": [],
        }


# =============================================================================
# LOCAL DIAGNOSTIC
# =============================================================================

if __name__ == "__main__":

    test_questions = [
        (
            "Which revision should the QC inspector follow for a lot "
            "of 450 components, how many samples are required, and "
            "why is Rev03 superseded?"
        ),
        (
            "What is the yearly preventive maintenance procedure "
            "for the TX-200?"
        ),
    ]

    for question in test_questions:
        print("\n" + "=" * 80)
        print("QUESTION:", question)
        print("=" * 80)

        result = generate_answer(question)

        print("\nANSWER")
        print("=" * 80)
        print(result.get("answer"))

        print("\nSTATUS")
        print("=" * 80)
        print(result.get("status"))

        print("\nSOURCES")
        print("=" * 80)

        for source in result.get("sources", []):
            print(
                f"{source.get('citation_id', source.get('id'))} | "
                f"{source.get('source')} | "
                f"Page {source.get('page')}"
            )
