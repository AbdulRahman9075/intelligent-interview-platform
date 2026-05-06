import numpy as np
from datetime import datetime, timezone
from typing import Dict
from sklearn.linear_model import LinearRegression

from app.system_optimiser.store import metrics_store


class LoadPredictor:
    """
    AI-Based Load Prediction — Requirement 1.

    Uses a LinearRegression model trained on historical per-minute request
    counts from the metrics store. Predicts the expected number of requests
    for the next N minutes.

    Follows the same lazy-init pattern as AnswerEvaluator — model is only
    trained when first needed, and re-trained on each prediction call so it
    always reflects the latest traffic data.
    """

    def predict_next_n_minutes(self, n: int = 5) -> Dict:
        buckets = metrics_store.get_by_minute()

        if len(buckets) < 2:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 3 minutes of traffic data. Currently have {len(buckets)} minute(s).",
                "predictions": [],
            }

        # Build time-series: X = minute index, y = request count
        sorted_keys = sorted(buckets.keys())
        y = np.array([buckets[k] for k in sorted_keys], dtype=float)
        X = np.arange(len(y)).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        # Predict next n minutes
        last_index = len(y)
        future_X = np.arange(last_index, last_index + n).reshape(-1, 1)
        predictions = model.predict(future_X)
        predictions = np.clip(predictions, 0, None)  # no negative predictions

        now = datetime.now(timezone.utc)
        current_minute = now.strftime("%Y-%m-%dT%H:%M")

        predicted_load = [
            {
                "minute_offset": i + 1,
                "predicted_requests": round(float(p), 1),
                "level": self._load_level(float(p)),
            }
            for i, p in enumerate(predictions)
        ]

        total_predicted = sum(p["predicted_requests"] for p in predicted_load)

        return {
            "status": "ok",
            "current_minute": current_minute,
            "historical_minutes_used": len(sorted_keys),
            "current_rpm": float(y[-1]),             # requests in last logged minute
            "trend": self._trend(float(model.coef_[0])),
            "predictions": predicted_load,
            "total_predicted_next_{}_min".format(n): round(total_predicted, 1),
        }

    def current_load_summary(self) -> Dict:
        """Returns a quick snapshot of current load without prediction."""
        all_metrics = metrics_store.get_all()
        total = len(all_metrics)

        if total == 0:
            return {"status": "no_data", "total_requests_logged": 0}

        recent = metrics_store.get_recent(60)
        error_count = sum(1 for m in recent if m["status_code"] >= 400)

        return {
            "status": "ok",
            "total_requests_logged": total,
            "recent_60_requests": len(recent),
            "recent_error_count": error_count,
            "recent_error_rate_pct": round((error_count / len(recent)) * 100, 1) if recent else 0,
        }

    @staticmethod
    def _load_level(rpm: float) -> str:
        if rpm < 10:
            return "low"
        if rpm < 50:
            return "medium"
        if rpm < 100:
            return "high"
        return "critical"

    @staticmethod
    def _trend(coef: float) -> str:
        if coef > 1:
            return "increasing"
        if coef < -1:
            return "decreasing"
        return "stable"


# Singleton
load_predictor = LoadPredictor()
