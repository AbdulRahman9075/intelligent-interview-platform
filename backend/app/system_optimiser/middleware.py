import time
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.system_optimiser.store import metrics_store

# Endpoints to skip logging (noisy, not useful for analysis)
EXCLUDED_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}


class SystemMetricsMiddleware(BaseHTTPMiddleware):
    """
    Passively intercepts every request — no changes needed to existing routes.

    Logs per request:
      - timestamp        → used by load_predictor to build time-series
      - endpoint         → used to track per-route performance
      - method           → GET/POST breakdown
      - status_code      → error rate tracking
      - response_time_ms → used by anomaly_detector for latency analysis

    Attaches X-Response-Time-Ms header to every response for debugging.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        timestamp = datetime.now(timezone.utc)

        response = await call_next(request)

        response_time_ms = (time.perf_counter() - start_time) * 1000

        metrics_store.log_request({
            "timestamp": timestamp.isoformat(),
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "response_time_ms": round(response_time_ms, 2),
        })

        response.headers["X-Response-Time-Ms"] = str(round(response_time_ms, 2))
        return response
