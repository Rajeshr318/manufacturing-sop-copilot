
import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from backend.rag_pipeline import (
    generate_answer,
    NO_ANSWER
)


@pytest.fixture
def active_chunk():
    return {
        "source": "MNT-MAN-CNC-02_TX-200_Preventive_Maintenance.pdf",
        "page": 1,
        "content": "Coolant concentration must be maintained between 6% and 8%.",
        "status": "active"
    }


def test_successful_answer_with_valid_citation(monkeypatch, active_chunk):
    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: [active_chunk]
    )

    monkeypatch.setattr(
        "backend.rag_pipeline.get_llm",
        lambda: RunnableLambda(
            lambda _: AIMessage(
                content='{"answer":"Coolant concentration must be 6–8%.", "citations":["S1"]}'
            )
        )
    )

    result = generate_answer("What is the coolant concentration?")

    assert "6" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["page"] == 1


def test_unsupported_question_returns_no_answer(monkeypatch):
    monkeypatch.setattr(
        "backend.rag_pipeline.retrieve_documents",
        lambda question, top_k: []
    )

    result = generate_answer("What is the factory electricity consumption?")

    assert result["answer"] == NO_ANSWER
    assert result["sources"] == []


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
