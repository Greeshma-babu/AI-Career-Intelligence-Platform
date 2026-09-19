from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.chain import ask_career_coach

router = APIRouter(
    prefix="/api/career",
    tags=["Career Coach"],
)


class CareerRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Career question from the user.",
    )

    analysis_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Existing TalentPulse resume analysis result.",
    )


class CareerResponse(BaseModel):
    answer: str

    sources: List[str] = Field(default_factory=list)

    retrieved_documents: int = 0

    model: str = ""


@router.post(
    "/ask",
    response_model=CareerResponse,
)
def career_coach(
    request: CareerRequest,
):
    """
    TalentPulse Career Coach.

    Uses:
    - Resume analysis
    - Job requirements
    - Skill gap
    - FAISS retrieval
    - Ollama
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Career question cannot be empty.",
        )

    if not request.analysis_result:
        raise HTTPException(
            status_code=400,
            detail=(
                "Resume analysis is required. " "Please analyze your resume first."
            ),
        )

    try:

        result = ask_career_coach(
            question=question,
            analysis_result=request.analysis_result,
        )

        return CareerResponse(
            answer=result.get(
                "answer",
                "",
            ),
            sources=result.get(
                "sources",
                [],
            ),
            retrieved_documents=result.get(
                "retrieved_documents",
                0,
            ),
            model=result.get(
                "model",
                "",
            ),
        )

    except Exception as exc:

        error_message = str(exc)

        if "ollama" in error_message.lower() or "connection" in error_message.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Ollama is not available. "
                    "Make sure Ollama is running and "
                    f"the model '{'qwen2.5:0.5b'}' is installed."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=("Career Coach failed: " f"{error_message}"),
        )
