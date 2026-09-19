import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.rag.embeddings import get_embeddings

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DOCUMENTS_DIR = BASE_DIR / "documents"

# Cache the most recently generated vector store.
_VECTOR_STORE_CACHE = {}


# ============================================================
# TEXT HELPERS
# ============================================================


def _clean_text(value: Any) -> str:
    """
    Convert arbitrary values into clean searchable text.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float, bool)):
        return str(value)

    if isinstance(value, list):

        parts = []

        for item in value:

            text = _clean_text(item)

            if text:
                parts.append(text)

        return "\n".join(parts)

    if isinstance(value, dict):

        parts = []

        for key, item in value.items():

            text = _clean_text(item)

            if text:

                readable_key = str(key).replace("_", " ").strip()

                parts.append(f"{readable_key}: {text}")

        return "\n".join(parts)

    return str(value).strip()


# ============================================================
# TEXT CHUNKING
# ============================================================


def _split_long_text(
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> List[str]:
    """
    Split text into overlapping chunks.

    Paragraphs and sentences are preferred as boundaries
    before falling back to character-based splitting.
    """

    text = re.sub(
        r"\r\n?",
        "\n",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    ).strip()

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    # --------------------------------------------------------
    # First split by paragraphs
    # --------------------------------------------------------

    paragraphs = [
        paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:

        # If paragraph itself is too large,
        # handle it separately.
        if len(paragraph) > chunk_size:

            if current:
                chunks.append(current.strip())
                current = ""

            start = 0

            while start < len(paragraph):

                end = min(
                    start + chunk_size,
                    len(paragraph),
                )

                piece = paragraph[start:end].strip()

                if piece:
                    chunks.append(piece)

                if end >= len(paragraph):
                    break

                start = max(
                    end - chunk_overlap,
                    start + 1,
                )

            continue

        proposed = paragraph if not current else current + "\n\n" + paragraph

        if len(proposed) <= chunk_size:

            current = proposed

        else:

            if current:
                chunks.append(current.strip())

            # Preserve overlap from previous chunk.
            overlap_text = ""

            if chunks:

                previous = chunks[-1]

                overlap_text = previous[
                    max(
                        0,
                        len(previous) - chunk_overlap,
                    ) :
                ].strip()

            if overlap_text:

                current = overlap_text + "\n\n" + paragraph

            else:

                current = paragraph

    if current:
        chunks.append(current.strip())

    return chunks


# ============================================================
# DOCUMENT FILE LOADING
# ============================================================


def _load_text_file(path: Path) -> str:
    """
    Load a plain text / markdown file.
    """

    try:

        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).strip()

    except Exception:

        return ""


def _load_pdf_file(path: Path) -> str:
    """
    Extract text from a PDF using pypdf.
    """

    try:

        from pypdf import PdfReader

        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:

            try:

                text = page.extract_text() or ""

                if text.strip():
                    pages.append(text)

            except Exception:
                continue

        return "\n\n".join(pages).strip()

    except Exception:

        # Fallback to pdfplumber if available.
        try:

            import pdfplumber

            pages = []

            with pdfplumber.open(str(path)) as pdf:

                for page in pdf.pages:

                    text = page.extract_text() or ""

                    if text.strip():
                        pages.append(text)

            return "\n\n".join(pages).strip()

        except Exception:

            return ""


def _load_docx_file(path: Path) -> str:
    """
    Extract text from a DOCX file.
    """

    try:

        from docx import Document as DocxDocument

        document = DocxDocument(str(path))

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n\n".join(paragraphs).strip()

    except Exception:

        return ""


def _load_document_file(path: Path) -> str:
    """
    Load supported knowledge-base document formats.
    """

    suffix = path.suffix.lower()

    if suffix in {
        ".txt",
        ".md",
        ".markdown",
        ".rst",
    }:

        return _load_text_file(path)

    if suffix == ".pdf":

        return _load_pdf_file(path)

    if suffix == ".docx":

        return _load_docx_file(path)

    return ""


# ============================================================
# CAREER KNOWLEDGE DOCUMENTS
# ============================================================


def _make_knowledge_documents() -> List[Document]:
    """
    Load all supported files from:

        app/documents

    These documents contain general career knowledge,
    AI/ML information, role descriptions, learning paths,
    etc.
    """

    documents = []

    if not DOCUMENTS_DIR.exists():

        return documents

    supported_extensions = {
        ".txt",
        ".md",
        ".markdown",
        ".rst",
        ".pdf",
        ".docx",
    }

    files = sorted(
        [
            path
            for path in DOCUMENTS_DIR.rglob("*")
            if path.is_file() and path.suffix.lower() in supported_extensions
        ]
    )

    for path in files:

        text = _load_document_file(path)

        if not text:
            continue

        chunks = _split_long_text(
            text,
            chunk_size=1200,
            chunk_overlap=200,
        )

        relative_path = path.relative_to(DOCUMENTS_DIR)

        for index, chunk in enumerate(chunks):

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": str(relative_path),
                        "source_type": "knowledge",
                        "section": "career_knowledge",
                        "chunk": index,
                        "file_name": path.name,
                    },
                )
            )

    return documents


# ============================================================
# RESUME / ANALYSIS DOCUMENTS
# ============================================================


def _make_analysis_documents(
    analysis_result: Dict[str, Any],
) -> List[Document]:
    """
    Convert the existing TalentPulse analysis result
    into RAG documents.
    """

    documents = []

    if not analysis_result:
        return documents

    # --------------------------------------------------------
    # Resume text
    # --------------------------------------------------------

    resume_text = ""

    possible_resume_keys = [
        "resume_text",
        "resumeText",
        "extracted_text",
        "text",
        "resume",
    ]

    for key in possible_resume_keys:

        value = analysis_result.get(key)

        if isinstance(value, str) and value.strip():

            resume_text = value.strip()

            break

    if resume_text:

        chunks = _split_long_text(
            resume_text,
            chunk_size=1200,
            chunk_overlap=200,
        )

        for index, chunk in enumerate(chunks):

            documents.append(
                Document(
                    page_content=("Candidate Resume\n\n" + chunk),
                    metadata={
                        "source": "resume",
                        "source_type": "candidate",
                        "section": "resume",
                        "chunk": index,
                    },
                )
            )

    # --------------------------------------------------------
    # Important structured fields
    # --------------------------------------------------------

    important_fields = [
        (
            "resume_skills",
            "Candidate Resume Skills",
            "resume_skills",
        ),
        (
            "skills",
            "Candidate Skills",
            "resume_skills",
        ),
        (
            "job_required_skills",
            "Required Job Skills",
            "job_requirements",
        ),
        (
            "required_skills",
            "Required Job Skills",
            "job_requirements",
        ),
        (
            "matched_skills",
            "Matched Skills",
            "skill_match",
        ),
        (
            "missing_skills",
            "Missing Skills",
            "skill_gap",
        ),
        (
            "job_description",
            "Job Description",
            "job_description",
        ),
        (
            "entities",
            "Resume Named Entities",
            "entities",
        ),
        (
            "experience",
            "Candidate Experience",
            "experience",
        ),
        (
            "education",
            "Candidate Education",
            "education",
        ),
        (
            "projects",
            "Candidate Projects",
            "projects",
        ),
        (
            "ats_score",
            "ATS Score",
            "ats",
        ),
        (
            "match_score",
            "Resume Job Match Score",
            "matching",
        ),
        (
            "skill_match_percentage",
            "Skill Match Percentage",
            "skill_match",
        ),
    ]

    processed_keys = set()

    for key, title, section in important_fields:

        if key in processed_keys:
            continue

        if key not in analysis_result:
            continue

        value = analysis_result.get(key)

        text = _clean_text(value)

        if not text:
            continue

        processed_keys.add(key)

        chunks = _split_long_text(
            text,
            chunk_size=1200,
            chunk_overlap=200,
        )

        for index, chunk in enumerate(chunks):

            documents.append(
                Document(
                    page_content=(f"{title}\n\n" f"{chunk}"),
                    metadata={
                        "source": key,
                        "source_type": "candidate",
                        "section": section,
                        "chunk": index,
                    },
                )
            )

    # --------------------------------------------------------
    # Remaining useful analysis fields
    # --------------------------------------------------------

    excluded_keys = {
        "resume_text",
        "resumeText",
        "extracted_text",
        "text",
        "resume",
    }

    for key, value in analysis_result.items():

        if key in processed_keys:
            continue

        if key in excluded_keys:
            continue

        text = _clean_text(value)

        if not text:
            continue

        readable_key = str(key).replace("_", " ").strip()

        chunks = _split_long_text(
            text,
            chunk_size=1200,
            chunk_overlap=200,
        )

        for index, chunk in enumerate(chunks):

            documents.append(
                Document(
                    page_content=(f"{readable_key.title()}\n\n" f"{chunk}"),
                    metadata={
                        "source": key,
                        "source_type": "candidate",
                        "section": "analysis",
                        "chunk": index,
                    },
                )
            )

    return documents


# ============================================================
# CACHE KEY
# ============================================================


def _get_cache_key(
    analysis_result: Dict[str, Any],
) -> str:
    """
    Generate a cache key using:

    - analysis result
    - documents directory contents

    This means changing a document causes
    the FAISS index to rebuild.
    """

    serialized_analysis = json.dumps(
        analysis_result or {},
        sort_keys=True,
        default=str,
    )

    document_signature = []

    if DOCUMENTS_DIR.exists():

        for path in sorted(DOCUMENTS_DIR.rglob("*")):

            if not path.is_file():
                continue

            if path.suffix.lower() not in {
                ".txt",
                ".md",
                ".markdown",
                ".rst",
                ".pdf",
                ".docx",
            }:
                continue

            try:

                stat = path.stat()

                document_signature.append(
                    (
                        str(path.relative_to(DOCUMENTS_DIR)),
                        stat.st_size,
                        stat.st_mtime_ns,
                    )
                )

            except OSError:
                continue

    cache_data = {
        "analysis": serialized_analysis,
        "documents": document_signature,
    }

    serialized = json.dumps(
        cache_data,
        sort_keys=True,
        default=str,
    )

    return hashlib.md5(serialized.encode("utf-8")).hexdigest()


# ============================================================
# BUILD VECTOR STORE
# ============================================================


def build_vector_store(
    analysis_result: Dict[str, Any],
) -> FAISS:
    """
    Build one FAISS vector store containing:

        1. Career knowledge documents
        2. Resume
        3. Job description
        4. Skills
        5. Experience
        6. Education
        7. Projects
        8. Other analysis information
    """

    cache_key = _get_cache_key(analysis_result)

    if cache_key in _VECTOR_STORE_CACHE:

        return _VECTOR_STORE_CACHE[cache_key]

    # --------------------------------------------------------
    # Load career knowledge
    # --------------------------------------------------------

    knowledge_documents = _make_knowledge_documents()

    # --------------------------------------------------------
    # Load candidate information
    # --------------------------------------------------------

    analysis_documents = _make_analysis_documents(analysis_result)

    # --------------------------------------------------------
    # Combine both sources
    # --------------------------------------------------------

    documents = knowledge_documents + analysis_documents

    if not documents:

        raise ValueError(
            "No career knowledge or resume " "information was available for RAG."
        )

    print(f"[Career RAG] Knowledge documents: " f"{len(knowledge_documents)}")

    print(f"[Career RAG] Candidate documents: " f"{len(analysis_documents)}")

    print(f"[Career RAG] Total chunks: " f"{len(documents)}")

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    embeddings = get_embeddings()

    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    vector_store = FAISS.from_documents(
        documents,
        embeddings,
    )

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    _VECTOR_STORE_CACHE.clear()

    _VECTOR_STORE_CACHE[cache_key] = vector_store

    return vector_store
