from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI(
    title="TalentPulse API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TalentPulse",
    }


@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if file:
        file_content = await file.read()
        with open("data/resume/uploaded_resume.pdf", "wb") as f:
            f.write(file_content)
        return {"message": "Resume written to the file successfully."}
    else:
        return {"message": "Error - No file uploaded !!!"}


@app.post("/api/job/description")
async def upload_job_description(job_description: str = Form(...)):
    if job_description:
        with open("data/job/description.txt", "w") as f:
            f.write(job_description)
        return {"message": "Job description written to the file successfully."}
    else:
        return {"message": "Error - No job description provided !!!"}
