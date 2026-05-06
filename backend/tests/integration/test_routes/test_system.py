import pytest
from app.system_optimiser.job_scheduler import job_scheduler
from app.system_optimiser.store import metrics_store

def test_predict_load(client):
    response = client.get("/api/v1/load/predict")
    print(f"Prediction Response: {response.json()}")
    assert response.status_code == 200

    assert "status" in response.json()

def test_load_summary(client):
    response = client.get("/api/v1/load/summary")
    assert response.status_code == 200
    assert "status" in response.json()

def test_recommend_resources(client):
    response = client.get("/api/v1/resources/recommend")
    print(f"Recommendation Response: {response.json()}")
    assert response.status_code == 200

    data = response.json()
    assert "recommended_workers" in data or "fallback_recommendation" in data

def test_detect_anomalies(client):
    response = client.get("/api/v1/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "endpoint_breakdown" in data

def test_scheduler_status(client):
    response = client.get("/api/v1/scheduler/status")
    assert response.status_code == 200
    assert "queued_jobs" in response.json()

def test_raw_metrics(client):
    response = client.get("/api/v1/metrics/raw")
    assert response.status_code == 200
    assert "metrics" in response.json()

def test_reset_metrics(client):
    response = client.delete("/api/v1/metrics/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "cleared"

def test_dashboard(client):
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "load_prediction" in data
    assert "resource_allocation" in data
    assert "anomaly_detection" in data
    assert "scheduler" in data
