from pathlib import Path
import importlib.util
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent
RAG_MODULE_PATH = BASE_DIR / "question-vector.py"


def load_rag_module() -> Any:
    if not RAG_MODULE_PATH.exists():
        raise FileNotFoundError(f"Could not find RAG module at {RAG_MODULE_PATH}")

    spec = importlib.util.spec_from_file_location("rag_module", RAG_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("Failed to load RAG module specification.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rag_module = load_rag_module()
ask_question = rag_module.ask_question


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


app = FastAPI(title="Local RAG Chat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        answer, sources = ask_question(payload.question)
        return ChatResponse(answer=answer, sources=sorted(list(sources)))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {exc}") from exc
