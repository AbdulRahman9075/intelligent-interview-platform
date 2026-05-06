import pytest

def test_upload_resume_success(client):
    # Create a dummy text file
    file_content = b"I am a software engineer with 5 years of experience in Python and Java."
    files = {"file": ("resume.txt", file_content, "text/plain")}
    
    response = client.post("/api/v1/upload-resume", files=files)
    print(f"Upload Response: {response.json()}")
    
    assert response.status_code == 201

    data = response.json()
    assert "resume_id" in data
    assert data["filename"] == "resume.txt"
    assert "Python" in data["extracted_skills"]
    assert "Java" in data["extracted_skills"]

def test_upload_resume_invalid_type(client):
    file_content = b"Some image data"
    files = {"file": ("image.png", file_content, "image/png")}
    
    response = client.post("/api/v1/upload-resume", files=files)
    
    assert response.status_code == 415
    assert "Only PDF and plain text files are supported" in response.json()["detail"]

def test_get_resume_not_found(client):
    response = client.get("/api/v1/resume/non-existent-id")
    assert response.status_code == 404
    assert "Resume not found" in response.json()["detail"]

def test_get_resume_success(client):
    # Upload first
    file_content = b"Python Java C++"
    files = {"file": ("test.txt", file_content, "text/plain")}
    upload_response = client.post("/api/v1/upload-resume", files=files)
    resume_id = upload_response.json()["resume_id"]
    
    # Get it
    response = client.get(f"/api/v1/resume/{resume_id}")
    print(f"Get Resume Response: {response.json()}")
    assert response.status_code == 200

    data = response.json()
    assert data["resume_id"] == resume_id
    assert data["filename"] == "test.txt"
    assert "Python" in data["extracted_skills"]
