from fastapi import APIRouter
from app.system_optimiser.load_predictor import load_predictor
from app.system_optimiser.resource_allocator import resource_allocator
from app.system_optimiser.anomaly_detector import anomaly_detector
from app.system_optimiser.job_scheduler import job_scheduler
from app.system_optimiser.store import metrics_store
router = APIRouter()


@router.get("/load/predict")
def predict_load():
    """
    AI-Based Load Prediction.
    Returns predicted request load for the next 5 minutes using LinearRegression
    trained on historical per-minute request counts.
    """
    return load_predictor.predict_next_n_minutes(n=5)


@router.get("/load/summary")
def load_summary():
    """Current load snapshot — total requests, recent error rate."""
    return load_predictor.current_load_summary()


@router.get("/resources/recommend")
def recommend_resources():
    """
    Resource Allocation Prediction.
    Recommends Uvicorn worker count and memory based on predicted peak load.
    """
    return resource_allocator.recommend()


@router.get("/anomalies")
def detect_anomalies():
    """
    Performance Anomaly Detection.
    Runs Isolation Forest + Z-score analysis on logged response times.
    Returns flagged anomalies and per-endpoint breakdown.
    """
    result = anomaly_detector.detect()
    result["endpoint_breakdown"] = anomaly_detector.endpoint_breakdown()
    return result


@router.get("/scheduler/status")
def scheduler_status():
    """
    Smart Scheduler Status.
    Shows queued jobs, running jobs, available slots, and recent job history.
    """
    return job_scheduler.queue_status()


@router.get("/metrics/raw")
def raw_metrics(limit: int = 50):
    """Last N raw request metrics logged by the middleware."""
    return {
        "total_logged": metrics_store.total_requests(),
        "metrics": metrics_store.get_recent(limit),
    }


@router.delete("/metrics/reset")
def reset_metrics():
    """Clear all logged metrics (useful for testing)."""
    metrics_store.clear()
    return {"status": "cleared"}


@router.get("/dashboard")
def dashboard():
    """
    Single endpoint that aggregates all 4 optimizer outputs.
    Used by the frontend System Dashboard tab.
    """
    load = load_predictor.predict_next_n_minutes(n=5)
    resources = resource_allocator.recommend()
    anomalies = anomaly_detector.detect()
    scheduler = job_scheduler.queue_status()

    return {
        "load_prediction": load,
        "resource_allocation": resources,
        "anomaly_detection": {
            "health": anomalies.get("health", "unknown"),
            "anomaly_count": anomalies.get("anomaly_count", 0),
            "anomaly_rate_pct": anomalies.get("anomaly_rate_pct", 0),
            "summary": anomalies.get("summary", {}),
        },
        "scheduler": scheduler,
    }
