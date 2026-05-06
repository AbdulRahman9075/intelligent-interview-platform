import numpy as np
from typing import Dict, List
from sklearn.ensemble import IsolationForest

from app.system_optimiser.store import metrics_store

# Minimum samples needed before anomaly detection is meaningful
MIN_SAMPLES = 5


class AnomalyDetector:
    """
    Performance Anomaly Detection — Requirement 4.

    Uses Isolation Forest (scikit-learn) on API response times logged
    by the middleware. Flags requests where the response time is
    statistically anomalous compared to the recent baseline.

    Also provides Z-score based spike detection as a lightweight
    fallback when sample size is small.

    Isolation Forest is ideal here because:
      - It works on unlabelled data (no need to manually label anomalies)
      - It's efficient on small to medium windows of time-series data
      - It handles multi-modal distributions (fast GETs vs slow NLP POSTs)
    """

    def detect(self) -> Dict:
        metrics = metrics_store.get_all()

        if len(metrics) < MIN_SAMPLES:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {MIN_SAMPLES} requests. Currently have {len(metrics)}.",
                "anomalies": [],
            }

        response_times = np.array(
            [m["response_time_ms"] for m in metrics]
        ).reshape(-1, 1)

        # Isolation Forest — contamination=0.05 means we expect ~5% anomalies
        model = IsolationForest(contamination=0.05, random_state=42)
        labels = model.fit_predict(response_times)  # -1 = anomaly, 1 = normal

        anomalies = []
        for i, (label, metric) in enumerate(zip(labels, metrics)):
            if label == -1:
                anomalies.append({
                    "index": i,
                    "timestamp": metric["timestamp"],
                    "endpoint": metric["endpoint"],
                    "method": metric["method"],
                    "response_time_ms": metric["response_time_ms"],
                    "status_code": metric["status_code"],
                    "detection_method": "isolation_forest",
                })

        # Z-score spike detection as secondary signal
        z_scores = self._z_scores(response_times.flatten())
        spikes = [
            {
                "index": i,
                "timestamp": metrics[i]["timestamp"],
                "endpoint": metrics[i]["endpoint"],
                "response_time_ms": metrics[i]["response_time_ms"],
                "z_score": round(float(z_scores[i]), 2),
                "detection_method": "z_score",
            }
            for i in range(len(metrics))
            if abs(z_scores[i]) > 3.0
        ]

        avg_rt = float(np.mean(response_times))
        p95_rt = float(np.percentile(response_times, 95))
        p99_rt = float(np.percentile(response_times, 99))

        return {
            "status": "ok",
            "total_requests_analysed": len(metrics),
            "anomaly_count": len(anomalies),
            "anomaly_rate_pct": round((len(anomalies) / len(metrics)) * 100, 1),
            "spike_count": len(spikes),
            "summary": {
                "avg_response_time_ms": round(avg_rt, 2),
                "p95_response_time_ms": round(p95_rt, 2),
                "p99_response_time_ms": round(p99_rt, 2),
            },
            "anomalies": anomalies[-20:],   # last 20 anomalies
            "spikes": spikes[-10:],          # last 10 z-score spikes
            "health": self._health_label(len(anomalies), len(metrics)),
        }

    def endpoint_breakdown(self) -> List[Dict]:
        """Per-endpoint anomaly summary — useful for the dashboard."""
        metrics = metrics_store.get_all()
        if not metrics:
            return []

        endpoints: Dict[str, List[float]] = {}
        for m in metrics:
            endpoints.setdefault(m["endpoint"], []).append(m["response_time_ms"])

        breakdown = []
        for endpoint, times in endpoints.items():
            arr = np.array(times)
            breakdown.append({
                "endpoint": endpoint,
                "request_count": len(times),
                "avg_ms": round(float(np.mean(arr)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "max_ms": round(float(np.max(arr)), 2),
            })

        return sorted(breakdown, key=lambda x: x["p95_ms"], reverse=True)

    @staticmethod
    def _z_scores(data: np.ndarray) -> np.ndarray:
        mean, std = np.mean(data), np.std(data)
        if std == 0:
            return np.zeros_like(data)
        return (data - mean) / std

    @staticmethod
    def _health_label(anomaly_count: int, total: int) -> str:
        rate = anomaly_count / total if total > 0 else 0
        if rate < 0.03:
            return "healthy"
        if rate < 0.08:
            return "degraded"
        return "critical"


# Singleton
anomaly_detector = AnomalyDetector()
