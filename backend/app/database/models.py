import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.db import Base


def generate_uuid():
    return str(uuid.uuid4())


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=list)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("InterviewSession", back_populates="resume")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    resume_id = Column(UUID(as_uuid=False), ForeignKey("resumes.id"), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(20), default="medium")
    is_completed = Column(Boolean, default=False)
    overall_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    resume = relationship("Resume", back_populates="sessions")
    questions = relationship("Question", back_populates="session")


class Question(Base):
    __tablename__ = "questions"
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("interview_sessions.id"), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(20), nullable=False)
    question_text = Column(Text, nullable=False)
    ideal_answer = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("InterviewSession", back_populates="questions")
    evaluation = relationship("Evaluation", back_populates="question", uselist=False)


class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    question_id = Column(UUID(as_uuid=False), ForeignKey("questions.id"), nullable=False)
    session_id = Column(UUID(as_uuid=False), ForeignKey("interview_sessions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=True)
    normalized_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    weak_areas = Column(JSON, default=list)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    question = relationship("Question", back_populates="evaluation")
