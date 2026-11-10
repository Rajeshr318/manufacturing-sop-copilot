
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.rag_pipeline import generate_answer

app = FastAPI(
    title="Manufacturing SOP AI Copilot",
    description="RAG-based assistant for manufacturing SOP documents",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Manufacturing SOP AI Copilot API is running!"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = generate_answer(request.question)
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
