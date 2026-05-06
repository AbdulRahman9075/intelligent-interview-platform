import pytest
from unittest.mock import patch
from app.system_optimiser.anomaly_detector import AnomalyDetector
from app.system_optimiser.store import metrics_store

@pytest.fixture(autouse=True)
def reset_store():
    # Setup: clear store before each test
    metrics_store.clear()
    yield
    # Teardown: clear store after each test
    metrics_store.clear()

def test_detect_insufficient_data():
    detector = AnomalyDetector()
    for i in range(3):
        metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api/v1/test", "method": "GET", "response_time_ms": 100, "status_code": 200})
    
    result = detector.detect()
    print(f"Insufficient Data Result: {result}")
    assert result["status"] == "insufficient_data"

    assert "Need at least 5 requests" in result["message"]

def test_detect_anomalies_and_spikes():
    detector = AnomalyDetector()
    # Add 40 normal requests
    for i in range(40):
        metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api/v1/normal", "method": "GET", "response_time_ms": 100 + i, "status_code": 200})
    
    # Add 2 anomalous requests
    metrics_store.log_request({"timestamp": "2024-05-01T10:01:00", "endpoint": "/api/v1/heavy", "method": "POST", "response_time_ms": 5000, "status_code": 200})
    metrics_store.log_request({"timestamp": "2024-05-01T10:01:05", "endpoint": "/api/v1/heavy", "method": "POST", "response_time_ms": 5200, "status_code": 200})

    result = detector.detect()
    print(f"Anomaly Detection Results: {result}")
    assert result["status"] == "ok"

    assert result["total_requests_analysed"] == 42
    assert result["anomaly_count"] > 0
    assert result["spike_count"] > 0
    assert result["health"] != "healthy"

def test_endpoint_breakdown():
    detector = AnomalyDetector()
    metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api/v1/A", "method": "GET", "response_time_ms": 100, "status_code": 200})
    metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api/v1/A", "method": "GET", "response_time_ms": 200, "status_code": 200})
    metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api/v1/B", "method": "GET", "response_time_ms": 500, "status_code": 200})

    breakdown = detector.endpoint_breakdown()
    print(f"Endpoint Breakdown: {breakdown}")
    assert len(breakdown) == 2

    # B should be first because it has higher p95_ms
    assert breakdown[0]["endpoint"] == "/api/v1/B"
    assert breakdown[1]["endpoint"] == "/api/v1/A"
    assert breakdown[1]["avg_ms"] == 150.0

def test_z_score_zero_std():
    detector = AnomalyDetector()
    data = [100, 100, 100]
    # np.std is mocked to return 1.0 in conftest, so we patch it locally to return 0
    with patch('app.system_optimiser.anomaly_detector.np.std', return_value=0.0):
        # We pass the list directly; the internal np.mean/std mocks handle lists correctly
        res = detector._z_scores(data)
        assert len(res) == 3
        assert all(x == 0 for x in res)


def test_detect_empty():
    metrics_store.clear()
    detector = AnomalyDetector()
    res = detector.detect()
    assert res["status"] == "insufficient_data"
