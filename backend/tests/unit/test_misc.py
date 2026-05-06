import pytest
from app.database.db import get_db
from app.services.resume_analyzer import ResumeAnalyzer
from app.system_optimiser.job_scheduler import JobScheduler
from unittest.mock import patch, MagicMock

def test_get_db_generator():
    # Just iterate through the generator to cover it
    gen = get_db()
    db = next(gen)
    print(f"DB Session Object: {db}")
    assert db is not None

    # We don't call next(gen) again because it would raise StopIteration after yield

def test_resume_analyzer_pdf():
    analyzer = ResumeAnalyzer()
    # conftest mocks fitz.open to return "Python developer with Java"
    text = analyzer.extract_text("fake.pdf", "application/pdf")
    print(f"Extracted PDF Text: {text}")
    assert "Python" in text

    assert "Java" in text

@pytest.mark.asyncio
async def test_job_scheduler_failure():
    from app.system_optimiser.job_scheduler import JobScheduler
    scheduler = JobScheduler()
    def failing_fn(): raise ValueError("job failed")
    
    with pytest.raises(RuntimeError) as exc:
        await scheduler.submit(1, "fail_id", "fail_type", failing_fn)
    assert "job failed" in str(exc.value)

@pytest.mark.asyncio
async def test_job_scheduler_history_limit():
    from app.system_optimiser.job_scheduler import JobScheduler
    scheduler = JobScheduler()
    # Fill history
    for i in range(250):
        scheduler._history.append({"job_id": str(i)})
    
    async def dummy(): return 1
    await scheduler.submit(1, "trim_id", "trim_type", dummy)
    assert len(scheduler._history) <= 200

@pytest.mark.asyncio
async def test_answer_evaluator_exception():
    from app.services.answer_evaluator import AnswerEvaluator
    evaluator = AnswerEvaluator()
    # Mock _get_model to raise error
    with patch.object(evaluator, '_get_model', side_effect=Exception("model error")):
        with pytest.raises(Exception):
            evaluator.evaluate("a", "b", "c")

