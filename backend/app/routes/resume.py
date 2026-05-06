import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.database.models import Resume
from app.services.resume_analyzer import ResumeAnalyzer
from app.config import settings
from app.system_optimiser.job_scheduler import job_scheduler

router = APIRouter()
analyzer = ResumeAnalyzer()


class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    extracted_skills: list[str]
    skill_count: int
    message: str


@router.post("/upload-resume", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in {"application/pdf", "text/plain"}:
        raise HTTPException(status_code=415, detail="Only PDF and plain text files are supported.")
    contents = await file.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb}MB limit.")
    os.makedirs(settings.upload_dir, exist_ok=True)
    temp_path = os.path.join(settings.upload_dir, file.filename)
    with open(temp_path, "wb") as f:
        f.write(contents)
    try:
        raw_text = analyzer.extract_text(temp_path, file.content_type)



        # NLP skill extraction routed through the job scheduler
        # PRIORITY_CRITICAL = 1 (user is waiting on upload result)
        skills = await job_scheduler.submit(
            job_scheduler.PRIORITY_CRITICAL,
            f"resume_extract_{file.filename}",
            "resume_skill_extraction",
            analyzer.extract_skills,
            raw_text,
        )



    finally:
        os.remove(temp_path)

    resume = Resume(filename=file.filename, raw_text=raw_text, extracted_skills=skills)
    db.add(resume); db.commit(); db.refresh(resume)
    return ResumeUploadResponse(resume_id=resume.id, filename=resume.filename,
        extracted_skills=skills, skill_count=len(skills), message="Resume uploaded and skills extracted.")


@router.get("/resume/{resume_id}")
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"resume_id": resume.id, "filename": resume.filename,
            "extracted_skills": resume.extracted_skills, "uploaded_at": resume.uploaded_at}
