from collections import deque
from threading import Lock
from typing import List, Dict


class MetricsStore:
    """
    Thread-safe in-memory store for request metrics.
    Shared across load_predictor, anomaly_detector, and resource_allocator.
    Keeps last 1000 requests in memory — no DB changes needed.
    """

    def __init__(self, maxlen: int = 1000):
        self._requests: deque = deque(maxlen=maxlen)
        self._lock = Lock()

    def log_request(self, metric: Dict):
        with self._lock:
            self._requests.append(metric)

    def get_all(self) -> List[Dict]:
        with self._lock:
            return list(self._requests)

    def get_recent(self, n: int) -> List[Dict]:
        with self._lock:
            return list(self._requests)[-n:]

    def get_by_minute(self) -> Dict[str, int]:
        """Returns request count bucketed per minute."""
        with self._lock:
            buckets: Dict[str, int] = {}
            for m in self._requests:
                minute_key = m["timestamp"][:16]  # "YYYY-MM-DDTHH:MM"
                buckets[minute_key] = buckets.get(minute_key, 0) + 1
            return buckets

    def get_response_times(self) -> List[float]:
        with self._lock:
            return [m["response_time_ms"] for m in self._requests]

    def total_requests(self) -> int:
        with self._lock:
            return len(self._requests)

    def clear(self):
        with self._lock:
            self._requests.clear()


# Singleton — imported by all other optimizer modules
metrics_store = MetricsStore()
