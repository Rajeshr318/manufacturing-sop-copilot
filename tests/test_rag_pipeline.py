
import backend.rag_pipeline as rag_pipeline
import pytest

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from backend.rag_pipeline import (
    generate_answer,
    generate_complex_sop_answer,
    NO_ANSWER,
    SERVICE_ERROR
)


# =====================================================
# FIXTURE: DISABLE OLLAMA FALLBACK DURING UNIT TESTS
# =====================================================

@pytest.fixture(autouse=True)
def disable_ollama_fallback_during_unit_tests(monkeypatch):
    monkeypatch.setattr(
        rag_pipeline,
        "ENABLE_OLLAMA_FALLBACK",
        False
    )


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture
def active_chunk():
    return {
        "source": "MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf",
        "page": 1,
        "content": "Coolant concentration must be maintained between 6% and 8%.",
        "status": "active"
    }


# =====================================================
# TEST 1: SUCCESSFUL ANSWER WITH VALID CITATION
# =====================================================

def test_successful_answer_with_valid_citation(monkeypatch, active_chunk):

    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: [active_chunk]
    )

    monkeypatch.setattr(
        "backend.rag_pipeline.get_llm",
        lambda: RunnableLambda(
            lambda _: AIMessage(
                content='{"answer":"Coolant concentration must be 6–8% [S1].", "citations":["S1"], "status":"answered"}'
            )
        )
    )

    result = generate_answer("What is the coolant concentration?")

    assert "6" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["page"] == 1
    assert result["sources"][0]["citation_id"] == "S1"
    assert result["status"] == "answered"


# =====================================================
# TEST 2: UNSUPPORTED QUESTION
# =====================================================

def test_unsupported_question_returns_no_answer(monkeypatch):

    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: []
    )

    result = generate_answer(
        "What is the factory electricity consumption?"
    )

    assert result["answer"] == NO_ANSWER
    assert result["sources"] == []
    assert result["status"] == "no_answer"


# =====================================================
# TEST 3: INVALID LLM RESPONSE
# =====================================================

def test_invalid_llm_response_returns_no_answer(monkeypatch, active_chunk):

    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: [active_chunk]
    )

    monkeypatch.setattr(
        "backend.rag_pipeline.get_llm",
        lambda: RunnableLambda(
            lambda _: AIMessage(content="This is not valid JSON")
        )
    )

    result = generate_answer("What is the coolant concentration?")

    assert result["answer"] == NO_ANSWER
    assert result["sources"] == []
    assert result["status"] == "no_answer"


# =====================================================
# TEST 4: INVALID CITATION
# =====================================================

def test_invalid_citation_returns_no_answer(monkeypatch, active_chunk):

    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: [active_chunk]
    )

    monkeypatch.setattr(
        "backend.rag_pipeline.get_llm",
        lambda: RunnableLambda(
            lambda _: AIMessage(
                content='{"answer":"Coolant concentration is 6–8% [S9].", "citations":["S9"], "status":"answered"}'
            )
        )
    )

    result = generate_answer("What is the coolant concentration?")

    assert result["answer"] == NO_ANSWER
    assert result["sources"] == []
    assert result["status"] == "no_answer"


# =====================================================
# TEST 5: LLM FAILURE
# =====================================================

def test_llm_failure_returns_error(monkeypatch, active_chunk):

    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: [active_chunk]
    )

    def failing_llm():
        raise RuntimeError("Groq API quota exceeded")

    monkeypatch.setattr(
        "backend.rag_pipeline.get_llm",
        failing_llm
    )

    result = generate_answer("What is the coolant concentration?")

    assert result["answer"] == SERVICE_ERROR
    assert result["sources"] == []
    assert result["status"] == "error"


# =====================================================
# TEST 6: RETRIEVAL FAILURE
# =====================================================

def test_retrieval_failure_returns_error(monkeypatch):

    def failing_retrieval(question, top_k):
        raise RuntimeError("Vector database unavailable")

    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        failing_retrieval
    )

    result = generate_answer("What is the coolant concentration?")

    assert result["answer"] == SERVICE_ERROR
    assert result["sources"] == []
    assert result["status"] == "error"


# =====================================================
# TEST 7: COMPLEX GENERATION FAILURE
# =====================================================

def test_complex_generation_failure_does_not_return_partial_answer(
    monkeypatch
):

    class FailingAfterFirstSection:

        def __init__(self):
            self.call_count = 0

        def invoke(self, prompt):

            self.call_count += 1

            if self.call_count == 1:
                return AIMessage(
                    content=(
                        '{"answer":"13 samples are required [S1].",'
                        '"citations":["S1"],'
                        '"status":"answered"}'
                    )
                )

            raise RuntimeError("Groq API quota exceeded")

    fake_llm = FailingAfterFirstSection()

    monkeypatch.setattr(
        "backend.rag_pipeline.get_llm",
        lambda: fake_llm
    )

    source_map = {
        "S1": {
            "source": "QC-SOP-014_Rev04.pdf",
            "page": 1
        }
    }

    result = generate_complex_sop_answer(
        context="[S1] Sampling plan information",
        source_map=source_map
    )

    assert result["status"] == "error"
    assert result["answer"] == SERVICE_ERROR
    assert result["sources"] == []

    # Confirms generation stopped after the second section failed.
    assert fake_llm.call_count == 2


# =====================================================
# TEST 8: EMPTY QUESTION
# =====================================================

def test_empty_question_returns_no_answer():

    result = generate_answer("   ")

    assert result["answer"] == NO_ANSWER
    assert result["sources"] == []
    assert result["status"] == "no_answer"
