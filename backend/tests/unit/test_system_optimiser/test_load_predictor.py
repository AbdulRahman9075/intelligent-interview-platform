import pytest
from unittest.mock import patch, MagicMock
from app.system_optimiser.load_predictor import LoadPredictor
from app.system_optimiser.store import metrics_store
import numpy as np

@pytest.fixture(autouse=True)
def clear_store():
    metrics_store.clear()
    yield
    metrics_store.clear()

def test_load_predictor_insufficient_data():
    predictor = LoadPredictor()
    metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api", "method": "GET", "response_time_ms": 100, "status_code": 200})
    result = predictor.predict_next_n_minutes(n=5)
    assert result["status"] == "insufficient_data"

def test_load_predictor_success():
    predictor = LoadPredictor()
    # Need at least 3 minutes (actually len(buckets) < 2 check in code says 3 minutes needed)
    # 10:00, 10:01, 10:02
    for i in range(3):
        ts = f"2024-05-01T10:{i:02d}:00"
        metrics_store.log_request({"timestamp": ts, "endpoint": "/api", "method": "GET", "response_time_ms": 100, "status_code": 200})
    
    with patch('app.system_optimiser.load_predictor.LinearRegression') as mock_lr:
        mock_model = MagicMock()
        mock_model.predict.return_value = [50.0, 50.0, 50.0, 50.0, 50.0]
        mock_model.coef_ = [1.5]
        mock_lr.return_value = mock_model
        
        result = predictor.predict_next_n_minutes(n=5)
        print(f"Prediction Result: {result}")
        
        assert result["status"] == "ok"
        assert result["current_rpm"] == 1.0
        assert len(result["predictions"]) == 5
        assert result["predictions"][0]["predicted_requests"] == 50.0
        assert result["trend"] == "increasing"

def test_current_load_summary():
    predictor = LoadPredictor()
    # Empty
    assert predictor.current_load_summary()["status"] == "no_data"
    
    # One request
    metrics_store.log_request({"timestamp": "2024-05-01T10:00:00", "endpoint": "/api", "method": "GET", "response_time_ms": 100, "status_code": 200})
    res = predictor.current_load_summary()
    assert res["status"] == "ok"
    assert res["total_requests_logged"] == 1
    assert res["recent_error_rate_pct"] == 0.0
    
    # One error
    metrics_store.log_request({"timestamp": "2024-05-01T10:01:00", "endpoint": "/api", "method": "GET", "response_time_ms": 100, "status_code": 500})
    res = predictor.current_load_summary()
    assert res["recent_error_count"] == 1
    assert res["recent_error_rate_pct"] == 50.0

def test_load_levels():
    predictor = LoadPredictor()
    assert predictor._load_level(5) == "low"
    assert predictor._load_level(25) == "medium"
    assert predictor._load_level(75) == "high"
    assert predictor._load_level(150) == "critical"

def test_trends():
    predictor = LoadPredictor()
    assert predictor._trend(2.0) == "increasing"
    assert predictor._trend(-2.0) == "decreasing"
    assert predictor._trend(0.5) == "stable"

