from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.db import get_db
from app.database.models import Resume, InterviewSession, Question
from app.services.question_engine import QuestionEngine

router = APIRouter()
engine = QuestionEngine()


class GenerateQuestionsRequest(BaseModel):
    resume_id: str
    topic: Optional[str] = None
    difficulty: Optional[str] = "medium"
    num_questions: Optional[int] = 5


class QuestionOut(BaseModel):
    question_id: str
    topic: str
    difficulty: str
    question_text: str
    order_index: int


class GenerateQuestionsResponse(BaseModel):
    session_id: str
    resume_id: str
    topic: str
    difficulty: str
    questions: list[QuestionOut]


@router.post("/generate-questions", response_model=GenerateQuestionsResponse, status_code=status.HTTP_201_CREATED)
def generate_questions(body: GenerateQuestionsRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == body.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    topic = body.topic or engine.select_topic(resume.extracted_skills)
    session = InterviewSession(resume_id=resume.id, topic=topic, difficulty=body.difficulty)
    db.add(session); db.flush()
    raw_questions = engine.generate(skills=resume.extracted_skills, topic=topic,
                                    difficulty=body.difficulty, num_questions=body.num_questions)
    questions_out = []
    for idx, q in enumerate(raw_questions):
        question = Question(session_id=session.id, topic=topic, difficulty=body.difficulty,
                            question_text=q["question"], ideal_answer=q.get("ideal_answer"), order_index=idx)
        db.add(question); db.flush()
        questions_out.append(QuestionOut(question_id=question.id, topic=topic,
            difficulty=body.difficulty, question_text=q["question"], order_index=idx))
    db.commit()
    return GenerateQuestionsResponse(session_id=session.id, resume_id=resume.id,
        topic=topic, difficulty=body.difficulty, questions=questions_out)


@router.get("/results/{session_id}")
def get_results(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    questions = db.query(Question).filter(Question.session_id == session_id).all()
    results = []
    for q in questions:
        entry = {"question_id": q.id, "question_text": q.question_text,
                 "topic": q.topic, "difficulty": q.difficulty, "evaluation": None}
        if q.evaluation:
            entry["evaluation"] = {"user_answer": q.evaluation.user_answer,
                "similarity_score": q.evaluation.similarity_score,
                "normalized_score": q.evaluation.normalized_score,
                "feedback": q.evaluation.feedback, "weak_areas": q.evaluation.weak_areas}
        results.append(entry)
    return {"session_id": session.id, "topic": session.topic, "difficulty": session.difficulty,
            "overall_score": session.overall_score, "is_completed": session.is_completed,
            "created_at": session.created_at, "questions": results}
