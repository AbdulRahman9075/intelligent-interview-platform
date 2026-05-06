from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database.db import get_db
from app.database.models import Question, Evaluation, InterviewSession
from app.services.answer_evaluator import AnswerEvaluator
from app.system_optimiser.job_scheduler import job_scheduler

router = APIRouter()
evaluator = AnswerEvaluator()


class EvaluateAnswerRequest(BaseModel):
    question_id: str
    session_id: str
    user_answer: str


class EvaluateAnswerResponse(BaseModel):
    evaluation_id: str
    question_id: str
    session_id: str
    similarity_score: float
    normalized_score: float
    feedback: str
    weak_areas: list[str]


@router.post("/evaluate-answer", response_model=EvaluateAnswerResponse, status_code=status.HTTP_201_CREATED)
async def evaluate_answer(body: EvaluateAnswerRequest, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == body.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    if not question.ideal_answer:
        raise HTTPException(status_code=422, detail="No ideal answer available.")
    if db.query(Evaluation).filter(Evaluation.question_id == body.question_id).first():
        raise HTTPException(status_code=409, detail="Answer already evaluated.")




    # SentenceTransformer embedding + evaluation routed through the job scheduler
    # PRIORITY_HIGH = 2 (user is waiting on evaluation result)
    result = await job_scheduler.submit(
        job_scheduler.PRIORITY_HIGH,
        f"eval_{body.question_id}",
        "answer_evaluation",
        evaluator.evaluate,
        body.user_answer,
        question.ideal_answer,
        question.topic,
    )




    evaluation = Evaluation(question_id=body.question_id, session_id=body.session_id,
        user_answer=body.user_answer, similarity_score=result["similarity_score"],
        normalized_score=result["normalized_score"], feedback=result["feedback"],
        weak_areas=result["weak_areas"])
    db.add(evaluation)
    session = db.query(InterviewSession).filter(InterviewSession.id == body.session_id).first()
    if session:
        questions = db.query(Question).filter(Question.session_id == body.session_id).all()
        evaluated = [q for q in questions if q.evaluation is not None]
        if evaluated:
            session.overall_score = round(sum(q.evaluation.normalized_score for q in evaluated) / len(evaluated), 2)
        if len(evaluated) + 1 >= len(questions):
            session.is_completed = True; session.completed_at = datetime.utcnow()
    db.commit(); db.refresh(evaluation)
    return EvaluateAnswerResponse(evaluation_id=evaluation.id, question_id=evaluation.question_id,
        session_id=evaluation.session_id, similarity_score=evaluation.similarity_score,
        normalized_score=evaluation.normalized_score, feedback=evaluation.feedback,
        weak_areas=evaluation.weak_areas)
