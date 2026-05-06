import pytest
from app.database.models import Resume

def test_generate_questions_success(client, db_session):
    # Setup: Create a resume directly in the database
    resume = Resume(filename="test.pdf", raw_text="Experienced in Python and Django", extracted_skills=["Python", "Django"])
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)
    
    # Test generation
    payload = {
        "resume_id": resume.id,
        "topic": "Python",
        "difficulty": "medium",
        "num_questions": 3
    }
    response = client.post("/api/v1/generate-questions", json=payload)
    print(f"Generation Response: {response.json()}")
    
    assert response.status_code == 201

    data = response.json()
    assert "session_id" in data
    assert len(data["questions"]) == 3
    assert data["topic"] == "Python"
    assert "question_id" in data["questions"][0]

def test_generate_questions_resume_not_found(client):
    payload = {
        "resume_id": "00000000-0000-0000-0000-000000000000",
        "topic": "Python",
        "difficulty": "medium"
    }
    response = client.post("/api/v1/generate-questions", json=payload)
    assert response.status_code == 404
    assert "Resume not found" in response.json()["detail"]

def test_get_results_success(client, db_session):
    # Setup: Create resume and generate questions
    resume = Resume(filename="test.pdf", raw_text="Python dev", extracted_skills=["Python"])
    db_session.add(resume)
    db_session.commit()
    
    response = client.post("/api/v1/generate-questions", json={
        "resume_id": resume.id,
        "topic": "Python",
        "num_questions": 1
    })
    session_id = response.json()["session_id"]
    
    # Test getting results
    res_response = client.get(f"/api/v1/results/{session_id}")
    print(f"Results Response: {res_response.json()}")
    assert res_response.status_code == 200

    data = res_response.json()
    assert data["session_id"] == session_id
    assert len(data["questions"]) == 1
    assert data["questions"][0]["evaluation"] is None

def test_get_results_not_found(client):
    response = client.get("/api/v1/results/non-existent-session")
    assert response.status_code == 404
