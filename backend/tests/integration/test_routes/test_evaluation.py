import pytest
from app.database.models import Resume, InterviewSession, Question

def test_evaluate_answer_success(client, db_session):
    # Setup: Create resume, session, and question
    resume = Resume(filename="test.pdf", raw_text="Python", extracted_skills=["Python"])
    db_session.add(resume)
    db_session.flush()
    
    session = InterviewSession(resume_id=resume.id, topic="Python", difficulty="medium")
    db_session.add(session)
    db_session.flush()
    
    question = Question(
        session_id=session.id, 
        topic="Python", 
        difficulty="medium", 
        question_text="What is a decorator?", 
        ideal_answer="A decorator is a design pattern in Python that allows a user to add new functionality to an existing object without modifying its structure."
    )
    db_session.add(question)
    db_session.commit()
    
    payload = {
        "question_id": question.id,
        "session_id": session.id,
        "user_answer": "It is a way to add functionality to a function without changing its code."
    }
    
    response = client.post("/api/v1/evaluate-answer", json=payload)
    print(f"Evaluation Response: {response.json()}")
    
    assert response.status_code == 201

    data = response.json()
    assert "evaluation_id" in data
    assert data["similarity_score"] > 0
    assert "feedback" in data

def test_evaluate_answer_question_not_found(client):
    payload = {
        "question_id": "00000000-0000-0000-0000-000000000000",
        "session_id": "00000000-0000-0000-0000-000000000000",
        "user_answer": "Test"
    }
    response = client.post("/api/v1/evaluate-answer", json=payload)
    assert response.status_code == 404
    assert "Question not found" in response.json()["detail"]
