
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.rag_pipeline import generate_answer


# =====================================================
# CONFIGURATION
# =====================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Manufacturing SOP AI Copilot",
    description="RAG-based assistant for manufacturing SOP documents",
    version="1.1.0"
)

DOCUMENTS_DIR = (
    Path(__file__).resolve().parent.parent / "documents"
)


# =====================================================
# STATIC DOCUMENTS
# =====================================================

app.mount(
    "/documents",
    StaticFiles(directory=str(DOCUMENTS_DIR)),
    name="documents"
)


# =====================================================
# REQUEST MODEL
# =====================================================

class QuestionRequest(BaseModel):
    question: str


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Manufacturing SOP AI Copilot API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ForgeIQ API"
    }


# =====================================================
# ASK ENDPOINT
# =====================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = generate_answer(question)

        if not isinstance(result, dict):
            logger.error("RAG pipeline returned an invalid response.")

            raise HTTPException(
                status_code=500,
                detail="Invalid response from the answer generation service."
            )

        # Keep the response structure consistent.
        response = {
            "answer": result.get(
                "answer",
                "No answer was generated."
            ),
            "sources": result.get("sources", []),
            "status": result.get("status", "no_answer")
        }

        return response

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error while processing the question."
        )

        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later."
        )
