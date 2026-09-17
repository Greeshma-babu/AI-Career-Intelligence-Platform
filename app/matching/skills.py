# app/matching/skills.py
import os

from app.nlp.preprocessing import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_job_description,
)

# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {
    "python": ["python"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": [
        "deep learning",
        "cnn",
        "convolutional neural network",
    ],
    "nlp": [
        "nlp",
        "natural language processing",
    ],
    "generative ai": [
        "generative ai",
        "genai",
    ],
    "llm": [
        "llm",
        "large language model",
        "large language models",
    ],
    "rag": [
        "rag",
        "retrieval augmented generation",
        "retrieval augmented",
    ],
    "langchain": [
        "langchain",
    ],
    "langgraph": [
        "langgraph",
    ],
    "ai agents": [
        "ai agent",
        "ai agents",
        "agentic ai",
        "agentic rag",
    ],
    "vector database": [
        "vector database",
        "vector db",
        "faiss",
        "vector search",
    ],
    "embeddings": [
        "embedding",
        "embeddings",
        "vector embeddings",
    ],
    "prompt engineering": [
        "prompt engineering",
        "prompt engineering techniques",
    ],
    "fine tuning": [
        "fine tuning",
        "fine-tuning",
        "fine tune",
    ],
    "fastapi": [
        "fastapi",
    ],
    "docker": [
        "docker",
    ],
    "pytorch": [
        "pytorch",
    ],
    "hugging face": [
        "hugging face",
        "huggingface",
    ],
    "mlops": [
        "mlops",
        "ml ops",
    ],
    "cloud": [
        "cloud",
        "cloud platform",
        "cloud computing",
    ],
}


# ============================================================
# 1. EXTRACT SKILLS FROM TEXT
# ============================================================


def extract_skills(text):
    """
    Detect known technical skills from text.

    Args:
        text: Resume text or Job Description text.

    Returns:
        Sorted list of detected skills.
    """

    if not text:
        return []

    text = text.lower()

    found_skills = []

    for skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            if alias.lower() in text:
                found_skills.append(skill)
                break

    return sorted(set(found_skills))


# ============================================================
# 2. SKILLS DETECTED IN RESUME
# ============================================================


def get_resume_skills(resume_text):
    """
    Get skills detected in the resume.

    Args:
        resume_text: Extracted resume text.

    Returns:
        List of skills found in the resume.
    """

    return extract_skills(resume_text)


# ============================================================
# 3. SKILLS REQUIRED BY JOB
# ============================================================


def get_job_required_skills(job_description_text):
    """
    Get skills required by the job description.

    Args:
        job_description_text: Extracted job description text.

    Returns:
        List of skills required by the job.
    """

    return extract_skills(job_description_text)


# ============================================================
# 4. MATCHED SKILLS
# ============================================================


def get_matched_skills(resume_skills, job_skills):
    """
    Find skills that exist in both resume and job description.

    Args:
        resume_skills: Skills detected in resume.
        job_skills: Skills required by job.

    Returns:
        List of matched skills.
    """

    resume_skill_set = {skill.lower() for skill in resume_skills}

    job_skill_set = {skill.lower() for skill in job_skills}

    matched_skills = resume_skill_set.intersection(job_skill_set)

    return sorted(matched_skills)


# ============================================================
# 5. MISSING SKILLS
# ============================================================


def get_missing_skills(resume_skills, job_skills):
    """
    Find skills required by the job but missing from the resume.

    Args:
        resume_skills: Skills detected in resume.
        job_skills: Skills required by job.

    Returns:
        List of missing skills.
    """

    resume_skill_set = {skill.lower() for skill in resume_skills}

    job_skill_set = {skill.lower() for skill in job_skills}

    missing_skills = job_skill_set.difference(resume_skill_set)

    return sorted(missing_skills)


# ============================================================
# 6. SKILL MATCH PERCENTAGE
# ============================================================


def calculate_skill_match_percentage(
    resume_skills,
    job_skills,
):
    """
    Calculate percentage of required job skills
    that are present in the resume.

    Formula:

        Matched Skills
        ------------------------ × 100
        Required Job Skills

    Returns:
        Skill match percentage.
    """

    if not job_skills:
        return 0

    matched_skills = get_matched_skills(
        resume_skills,
        job_skills,
    )

    percentage = (len(matched_skills) / len(job_skills)) * 100

    return round(percentage, 2)


# ============================================================
# 7. COMPLETE SKILL ANALYSIS
# ============================================================


def analyze_skills(resume_text, job_description_text):
    """
    Perform complete resume-vs-job skill analysis.

    Returns:

        {
            "resume_skills": [...],
            "job_required_skills": [...],
            "matched_skills": [...],
            "missing_skills": [...],
            "skill_match_percentage": 75.0
        }
    """

    # Skills detected in resume
    resume_skills = get_resume_skills(resume_text)

    # Skills required by job
    job_required_skills = get_job_required_skills(job_description_text)

    # Skills present in both
    matched_skills = get_matched_skills(
        resume_skills,
        job_required_skills,
    )

    # Skills required by job but absent in resume
    missing_skills = get_missing_skills(
        resume_skills,
        job_required_skills,
    )

    # Percentage match
    skill_match_percentage = calculate_skill_match_percentage(
        resume_skills,
        job_required_skills,
    )

    return {
        "resume_skills": resume_skills,
        "job_required_skills": job_required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": skill_match_percentage,
    }


# ============================================================
# 8. COMPLETE RESUME + JOB ANALYSIS
# ============================================================


def analyze_resume_and_job(
    resume_path,
    job_description_path,
):
    """
    Complete TalentPulse analysis pipeline.

    Flow:

        main.py
            ↓
        skills.py
            ↓
        preprocessing.py
            ↓
        Resume Text + Job Description Text
            ↓
        skills.py
            ↓
        Skill Analysis
    """

    # --------------------------------------------------------
    # Validate resume file
    # --------------------------------------------------------

    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    # --------------------------------------------------------
    # Validate job description
    # --------------------------------------------------------

    if not os.path.exists(job_description_path):
        raise FileNotFoundError(
            f"Job description file not found: " f"{job_description_path}"
        )

    # --------------------------------------------------------
    # Extract resume text
    # --------------------------------------------------------

    _, extension = os.path.splitext(resume_path)

    extension = extension.lower()

    if extension == ".pdf":

        resume_text = extract_text_from_pdf(resume_path)

    elif extension == ".docx":

        resume_text = extract_text_from_docx(resume_path)

    else:

        raise ValueError(f"Unsupported resume format: {extension}")

    # --------------------------------------------------------
    # Extract job description
    # --------------------------------------------------------

    job_description_text = extract_text_from_job_description(job_description_path)

    # --------------------------------------------------------
    # Validate extracted text
    # --------------------------------------------------------

    if not resume_text.strip():
        raise ValueError("No text could be extracted from the resume.")

    if not job_description_text.strip():
        raise ValueError("No text could be extracted from the " "job description.")

    # --------------------------------------------------------
    # Perform skill analysis
    # --------------------------------------------------------

    result = analyze_skills(
        resume_text,
        job_description_text,
    )

    return result
