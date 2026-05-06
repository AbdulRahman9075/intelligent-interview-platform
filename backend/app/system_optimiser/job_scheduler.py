import asyncio
import heapq
import time
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime, timezone
from app.system_optimiser.resource_allocator import resource_allocator


class ScheduledJob:
    """A single job in the scheduler's priority queue."""

    def __init__(self, priority: int, job_id: str, job_type: str, fn: Callable, *args, **kwargs):
        self.priority = priority       # lower = higher priority
        self.job_id = job_id
        self.job_type = job_type
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.queued_at = datetime.now(timezone.utc).isoformat()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.status = "queued"         # queued | running | done | failed
        self.result: Any = None
        self.error: Optional[str] = None

    def __lt__(self, other):
        return self.priority < other.priority


class JobScheduler:
    """
    Smart Scheduling Algorithm — Requirement 3.

    Manages a priority queue of NLP-heavy jobs (resume parsing, embedding
    generation). Instead of running every NLP call immediately and blocking
    workers, jobs are queued and dispatched based on:

      - Job priority     (resume parse > answer eval > batch jobs)
      - Available slots  (derived from resource_allocator recommendation)
      - System load      (fewer concurrent jobs when load is high)

    Priority levels:
      1 = CRITICAL  (resume upload — user is waiting)
      2 = HIGH      (answer evaluation — user is waiting)
      3 = NORMAL    (session init, topic loading)
      5 = LOW       (background analytics, batch retraining)

    Usage (in your existing services):
        result = await job_scheduler.submit(
            priority=1,
            job_id=f"resume_{user_id}",
            job_type="resume_parse",
            fn=your_nlp_function,
            *args
        )
    """

    PRIORITY_CRITICAL = 1
    PRIORITY_HIGH = 2
    PRIORITY_NORMAL = 3
    PRIORITY_LOW = 5

    def __init__(self):
        self._queue: List[ScheduledJob] = []
        self._lock = asyncio.Lock()
        self._history: List[Dict] = []
        self._running_count = 0

    def _get_max_concurrent(self) -> int:
        """Ask resource_allocator how many workers are available."""
        try:
            rec = resource_allocator.recommend()
            workers = rec.get("recommended_workers", 2)
            # Reserve at least 1 worker for HTTP — NLP gets the rest
            return max(1, workers - 1)
        except Exception:
            return 2  # safe fallback

    async def submit(
        self,
        priority: int,
        job_id: str,
        job_type: str,
        fn: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """
        Submit a job and await its result.
        Blocks the caller until the job completes (or raises on failure).
        """
        job = ScheduledJob(priority, job_id, job_type, fn, *args, **kwargs)

        async with self._lock:
            heapq.heappush(self._queue, job)

        # Poll until this job is picked up and completed
        while True:
            async with self._lock:
                max_slots = self._get_max_concurrent()

                # Try to run next job if slots are free
                if self._running_count < max_slots and self._queue:
                    next_job = heapq.heappop(self._queue)
                    if next_job.job_id == job.job_id:
                        self._running_count += 1
                        job.status = "running"
                        job.started_at = datetime.now(timezone.utc).isoformat()

            if job.status == "running":
                try:
                    start = time.perf_counter()
                    job.result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: job.fn(*job.args, **job.kwargs)
                    )
                    job.status = "done"
                except Exception as e:
                    job.status = "failed"
                    job.error = str(e)
                finally:
                    job.completed_at = datetime.now(timezone.utc).isoformat()
                    duration_ms = (time.perf_counter() - start) * 1000
                    async with self._lock:
                        self._running_count -= 1
                        self._history.append({
                            "job_id": job.job_id,
                            "job_type": job.job_type,
                            "priority": job.priority,
                            "status": job.status,
                            "queued_at": job.queued_at,
                            "started_at": job.started_at,
                            "completed_at": job.completed_at,
                            "duration_ms": round(duration_ms, 2),
                            "error": job.error,
                        })
                        # Keep only last 200 history entries
                        if len(self._history) > 200:
                            self._history = self._history[-200:]

                if job.status == "failed":
                    raise RuntimeError(f"Job {job.job_id} failed: {job.error}")
                return job.result

            await asyncio.sleep(0.05)  # yield and check again

    def queue_status(self) -> Dict:
        return {
            "queued_jobs": len(self._queue),
            "running_jobs": self._running_count,
            "max_concurrent_slots": self._get_max_concurrent(),
            "recent_history": self._history[-10:],
        }


# Singleton
job_scheduler = JobScheduler()
