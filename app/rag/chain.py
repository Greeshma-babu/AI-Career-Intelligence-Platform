import os
from functools import lru_cache
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai

from app.rag.prompt import build_prompt
from app.rag.retriever import get_relevant_documents

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"


@lru_cache(maxsize=1)
def get_llm():
    """
    Create the Gemini client once.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Please add GEMINI_API_KEY to your .env file."
        )

    return genai.Client(api_key=api_key)


def _build_context(documents) -> str:
    """
    Convert retrieved documents into the context
    supplied to the LLM.
    """

    if not documents:
        return "No relevant career information " "was retrieved."

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        source = document.metadata.get(
            "source",
            "unknown",
        )

        context_parts.append(f"""
Context {index}
Source: {source}

{document.page_content}
""")

    return "\n".join(context_parts)


def ask_career_coach(
    question: str,
    analysis_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Complete RAG pipeline:

    Question
       ↓
    FAISS retrieval
       ↓
    Relevant context
       ↓
    Prompt
       ↓
    Gemini
       ↓
    Answer
    """

    question = (question or "").strip()

    if not question:
        raise ValueError("Career question cannot be empty.")

    if not analysis_result:
        raise ValueError("Resume analysis is required before " "using Career Coach.")

    # ========================================================
    # 1. RETRIEVE RELEVANT DOCUMENTS
    # ========================================================

    documents = get_relevant_documents(
        question=question,
        analysis_result=analysis_result,
        k=5,
    )

    # ========================================================
    # 2. BUILD RAG CONTEXT
    # ========================================================

    context = _build_context(documents)

    # ========================================================
    # 3. BUILD CAREER COACH PROMPT
    # ========================================================

    prompt = build_prompt(
        context=context,
        question=question,
    )

    # ========================================================
    # 4. CALL GEMINI
    # ========================================================

    client = get_llm()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    answer = response.text if response.text else ""

    if not answer:
        answer = "I could not generate a career " "recommendation. Please try again."

    # ========================================================
    # 5. COLLECT SOURCES
    # ========================================================

    sources = []

    for document in documents:

        source = document.metadata.get("source")

        if source and source not in sources:
            sources.append(source)

    # ========================================================
    # 6. RETURN SAME RESPONSE STRUCTURE
    # ========================================================

    return {
        "answer": str(answer).strip(),
        "sources": sources,
        "retrieved_documents": len(documents),
        "model": GEMINI_MODEL,
    }
