from typing import Any, Dict, List

from langchain_core.documents import Document

from app.rag.vector_store import build_vector_store

# ============================================================
# GENERAL CAREER QUESTION DETECTION
# ============================================================


GENERAL_CAREER_KEYWORDS = {
    "ai engineer",
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "ml engineer",
    "generative ai",
    "generative ai engineer",
    "nlp engineer",
    "computer vision engineer",
    "llm engineer",
    "agentic ai",
    "mlops",
    "career path",
    "career",
    "role",
    "roles",
    "difference between",
    "what is",
    "how to become",
    "skills required",
    "skills needed",
    "what should i learn",
    "what should i learn next",
    "learning path",
    "roadmap",
}


# ============================================================
# QUESTION CLASSIFICATION
# ============================================================


def _is_general_career_question(
    question: str,
) -> bool:
    """
    Determine whether the question is primarily
    asking for general career knowledge.
    """

    normalized = (question or "").lower().strip()

    if not normalized:
        return False

    for keyword in GENERAL_CAREER_KEYWORDS:

        if keyword in normalized:
            return True

    return False


# ============================================================
# DOCUMENT DEDUPLICATION
# ============================================================


def _deduplicate_documents(
    documents: List[Document],
) -> List[Document]:
    """
    Remove duplicate document chunks.
    """

    result = []

    seen = set()

    for document in documents:

        source = document.metadata.get(
            "source",
            "",
        )

        chunk = document.metadata.get(
            "chunk",
            "",
        )

        key = (
            source,
            chunk,
            document.page_content.strip(),
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(document)

    return result


# ============================================================
# RETRIEVE
# ============================================================


def get_relevant_documents(
    question: str,
    analysis_result: Dict[str, Any],
    k: int = 5,
) -> List[Document]:
    """
    Retrieve relevant documents from BOTH:

        1. app/documents
        2. Resume / analysis_result

    General career questions prioritize knowledge documents.

    Personalized questions retrieve both candidate
    information and career knowledge.
    """

    question = (question or "").strip()

    if not question:
        return []

    vector_store = build_vector_store(analysis_result)

    # ========================================================
    # GENERAL CAREER QUESTION
    # ========================================================

    if _is_general_career_question(question):

        # Retrieve more candidates than we finally need.
        candidate_k = max(
            k * 3,
            12,
        )

        documents = vector_store.similarity_search(
            question,
            k=candidate_k,
        )

        documents = _deduplicate_documents(documents)

        # ----------------------------------------------------
        # Prefer knowledge documents.
        # ----------------------------------------------------

        knowledge_documents = [
            document
            for document in documents
            if document.metadata.get("source_type") == "knowledge"
        ]

        candidate_documents = [
            document
            for document in documents
            if document.metadata.get("source_type") == "candidate"
        ]

        # General questions should primarily use
        # the knowledge base.
        #
        # Candidate context can still be included
        # when available.

        selected = []

        selected.extend(knowledge_documents[:k])

        if len(selected) < k:

            remaining = k - len(selected)

            selected.extend(candidate_documents[:remaining])

        return selected[:k]

    # ========================================================
    # PERSONALIZED QUESTION
    # ========================================================

    candidate_k = max(
        k * 3,
        12,
    )

    documents = vector_store.similarity_search(
        question,
        k=candidate_k,
    )

    documents = _deduplicate_documents(documents)

    # --------------------------------------------------------
    # For personalized questions, retain both types.
    # --------------------------------------------------------

    knowledge_documents = [
        document
        for document in documents
        if document.metadata.get("source_type") == "knowledge"
    ]

    candidate_documents = [
        document
        for document in documents
        if document.metadata.get("source_type") == "candidate"
    ]

    selected = []

    # Candidate context first for personalized
    # questions.

    selected.extend(candidate_documents[:k])

    if len(selected) < k:

        remaining = k - len(selected)

        selected.extend(knowledge_documents[:remaining])

    return selected[:k]
