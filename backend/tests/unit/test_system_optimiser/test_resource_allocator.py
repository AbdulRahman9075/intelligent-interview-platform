import pytest
from app.system_optimiser.resource_allocator import ResourceAllocator

def test_resource_allocator_calculate_workers():
    allocator = ResourceAllocator()
    assert allocator._calculate_workers(peak_rpm=5) == 1
    assert allocator._calculate_workers(peak_rpm=50) == 6
    assert allocator._calculate_workers(peak_rpm=500) == 16 # Max workers

def test_resource_allocator_calculate_memory():
    allocator = ResourceAllocator()
    # BASE(256) + 2*128 + NLP(512) = 256 + 256 + 512 = 1024
    assert allocator._calculate_memory(workers=2) == 1024

def test_resource_allocator_recommend_insufficient_data():
    allocator = ResourceAllocator()
    res = allocator.recommend()
    assert res["status"] == "insufficient_data"

def test_resource_allocator_recommend_ok():
    from unittest.mock import patch
    allocator = ResourceAllocator()
    mock_load = {
        "status": "ok",
        "predictions": [{"predicted_requests": 50}],
    }
    with patch('app.system_optimiser.resource_allocator.load_predictor.predict_next_n_minutes', return_value=mock_load), \
         patch('app.system_optimiser.resource_allocator.load_predictor._load_level', return_value="medium"):
        res = allocator.recommend()
        print(f"Recommendation: {res}")
        assert res["status"] == "ok"

        assert res["recommended_workers"] == 6
        assert "Memory estimate includes" in res["reasoning"]

