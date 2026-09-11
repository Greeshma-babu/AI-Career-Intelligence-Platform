import os

from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI(
    title="TalentPulse API",
    version="1.0.0",
)

RESUME_DIR = "data/resume"
JOB_DIR = "data/job"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TalentPulse",
    }


@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
):
    # Preserve the real extension instead of hardcoding .pdf
    _, ext = os.path.splitext(file.filename or "")
    ext = ext.lower() if ext else ".pdf"
    if ext not in (".pdf", ".docx"):
        return {"message": f"Error - Unsupported file type '{ext}'."}
    os.makedirs(RESUME_DIR, exist_ok=True)
    resume_path = os.path.join(RESUME_DIR, f"uploaded_resume{ext}")
    file_content = await file.read()
    if not file_content:
        return {"message": "Error - Uploaded file is empty !!!"}
    with open(resume_path, "wb") as f:
        f.write(file_content)

    # The frontend sends job_description alongside the file in the same
    # request, so save it here instead of relying on a second call.
    if job_description.strip():
        job_path = os.path.join(JOB_DIR, "description.txt")
        with open(job_path, "w", encoding="utf-8") as f:
            f.write(job_description)
    return {
        "message": "Resume and job description saved successfully.",
        "resume_path": resume_path,
    }


@app.post("/api/job/description")
async def upload_job_description(job_description: str = Form(...)):
    if not job_description.strip():
        return {"message": "Error - No job description provided !!!"}
    os.makedirs(JOB_DIR, exist_ok=True)
    with open(os.path.join(JOB_DIR, "description.txt"), "w", encoding="utf-8") as f:
        f.write(job_description)
    return {"message": "Job description written to the file successfully."}
