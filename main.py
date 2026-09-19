import os


from fastapi import FastAPI, File, Form, UploadFile
from app.matching.skills import analyze_resume_and_job
from app.api.news import router as news_router
from app.api.career import router as career_router
from app.api.market import router as market_router

# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="TalentPulse API",
    version="1.0.0",
)


# ============================================================
# REGISTER MARKET TRENDS ROUTER
# ============================================================

app.include_router(market_router)
app.include_router(news_router)
app.include_router(career_router)

RESUME_DIR = "data/resume"
JOB_DIR = "data/job"


# ============================================================
# HEALTH CHECK
# ============================================================


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TalentPulse",
    }


# ============================================================
# RESUME + JOB DESCRIPTION
# ============================================================


@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
):

    # --------------------------------------------------------
    # Validate resume
    # --------------------------------------------------------

    if not file.filename:
        return {"message": "Error - No resume file provided."}

    _, ext = os.path.splitext(file.filename)

    ext = ext.lower()

    if ext not in (".pdf", ".docx"):
        return {
            "message": (
                f"Error - Unsupported file type '{ext}'. "
                "Only PDF and DOCX are supported."
            )
        }

    # --------------------------------------------------------
    # Validate job description
    # --------------------------------------------------------

    if not job_description.strip():
        return {"message": "Error - No job description provided."}

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    os.makedirs(RESUME_DIR, exist_ok=True)
    os.makedirs(JOB_DIR, exist_ok=True)

    # --------------------------------------------------------
    # Save resume
    # --------------------------------------------------------

    resume_path = os.path.join(
        RESUME_DIR,
        f"uploaded_resume{ext}",
    )

    file_content = await file.read()

    if not file_content:
        return {"message": "Error - Uploaded file is empty."}

    with open(resume_path, "wb") as f:
        f.write(file_content)

    # --------------------------------------------------------
    # Save job description
    # --------------------------------------------------------

    job_path = os.path.join(
        JOB_DIR,
        "description.txt",
    )

    with open(
        job_path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(job_description)

    # --------------------------------------------------------
    # RUN COMPLETE ANALYSIS
    #
    # main.py
    #     ↓
    # skills.py
    #     ↓
    # preprocessing.py
    # --------------------------------------------------------

    try:

        result = analyze_resume_and_job(
            resume_path,
            job_path,
        )

        return result

    except Exception as error:

        return {
            "message": "Error during resume analysis.",
            "error": str(error),
        }


# ============================================================
# JOB DESCRIPTION ENDPOINT
# ============================================================


@app.post("/api/job/description")
async def upload_job_description(
    job_description: str = Form(...),
):

    if not job_description.strip():
        return {"message": "Error - No job description provided."}

    os.makedirs(
        JOB_DIR,
        exist_ok=True,
    )

    job_path = os.path.join(
        JOB_DIR,
        "description.txt",
    )

    with open(
        job_path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(job_description)

    return {"message": "Job description written to the file successfully."}
