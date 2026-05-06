from typing import Dict
from app.system_optimiser.load_predictor import load_predictor


# Tuning constants — based on FastAPI + Uvicorn typical benchmarks
REQUESTS_PER_WORKER = 10       # requests/min a single worker handles comfortably
MIN_WORKERS = 1
MAX_WORKERS = 16
BASE_MEMORY_MB = 256           # base memory for the app itself
MEMORY_PER_WORKER_MB = 128     # additional memory per worker
NLP_JOB_MEMORY_MB = 512        # SentenceTransformer model footprint


class ResourceAllocator:
    """
    Resource Allocation Prediction — Requirement 2.

    Takes the predicted load from LoadPredictor and recommends:
      - Number of Uvicorn workers to run
      - Estimated memory requirement
      - Whether NLP-heavy endpoints need dedicated worker headroom

    This directly feeds into job_scheduler.py which uses the worker
    recommendation to decide how many concurrent NLP jobs to allow.
    """

    def recommend(self) -> Dict:
        load = load_predictor.predict_next_n_minutes(n=5)

        if load["status"] == "insufficient_data":
            return {
                "status": "insufficient_data",
                "message": load["message"],
                "fallback_recommendation": self._build_recommendation(
                    peak_rpm=10, workers=2
                ),
            }

        # Use the peak predicted RPM as the planning target
        predictions = load["predictions"]
        peak_rpm = max(p["predicted_requests"] for p in predictions) if predictions else 10
        peak_level = load_predictor._load_level(peak_rpm)

        workers = self._calculate_workers(peak_rpm)
        memory_mb = self._calculate_memory(workers)

        recommendation = self._build_recommendation(peak_rpm, workers)
        recommendation.update({
            "status": "ok",
            "peak_predicted_rpm": round(peak_rpm, 1),
            "load_level": peak_level,
            "estimated_memory_mb": memory_mb,
            "nlp_worker_headroom": workers >= 4,  # reserve a worker for NLP if enough capacity
            "reasoning": self._reasoning(peak_rpm, workers, peak_level),
        })

        return recommendation

    def _calculate_workers(self, peak_rpm: float) -> int:
        needed = max(MIN_WORKERS, int(peak_rpm / REQUESTS_PER_WORKER) + 1)
        return min(needed, MAX_WORKERS)

    def _calculate_memory(self, workers: int) -> int:
        return BASE_MEMORY_MB + (workers * MEMORY_PER_WORKER_MB) + NLP_JOB_MEMORY_MB

    def _build_recommendation(self, peak_rpm: float, workers: int) -> Dict:
        return {
            "recommended_workers": workers,
            "uvicorn_command": f"uvicorn app.main:app --workers {workers}",
        }

    def _reasoning(self, peak_rpm: float, workers: int, level: str) -> str:
        return (
            f"At {round(peak_rpm, 1)} req/min ({level} load), "
            f"{workers} worker(s) recommended "
            f"({REQUESTS_PER_WORKER} req/min per worker). "
            f"Memory estimate includes {NLP_JOB_MEMORY_MB}MB reserved for SentenceTransformer."
        )


# Singleton
resource_allocator = ResourceAllocator()
