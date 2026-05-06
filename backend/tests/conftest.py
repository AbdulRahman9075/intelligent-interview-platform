import sys
import os
from unittest.mock import MagicMock, patch

os.environ["DATABASE_URL"] = "postgresql://postgres:admin123@localhost:5432/interview-platform"

# 1. Mock the heavy dependencies for imports
sys.modules['numpy'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.ensemble'] = MagicMock()
sys.modules['sklearn.linear_model'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['spacy'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['fitz'] = MagicMock()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database.db import Base, get_db
from app.main import app as fastapi_app
from app.services.answer_evaluator import AnswerEvaluator
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.question_engine import QuestionEngine
from app.system_optimiser.anomaly_detector import AnomalyDetector

# 2. Database Fixtures (with StaticPool for SQLite threads)
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2.5 Force application to use the test engine/session globally
import app.database.db
app.database.db.engine = engine
app.database.db.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


# 3. Global Patches for ML Internals (to allow real method code to execute for 100% coverage)
def mock_cosine_similarity(a, b):
    # Dummy logic to support the unit test requirements
    if getattr(a, "mock_flag", "") == "bad" or getattr(b, "mock_flag", "") == "bad":
        return [[0.2]]
    if getattr(a, "mock_flag", "") == "empty" or getattr(b, "mock_flag", "") == "empty":
        return [[0.0]]
    return [[0.85]]

class DummyModel:
    def encode(self, texts, **kwargs):
        # Return mock arrays that support .reshape() and can carry a flag for cosine_similarity
        class MockArray:
            def __init__(self, val):
                self.mock_flag = val
            def reshape(self, *args): return self
        return [MockArray("empty" if not t else "bad" if "apples" in t else "good") for t in texts]

class DummyIsolationForest:
    def __init__(self, *args, **kwargs): pass
    def fit_predict(self, data):
        # return -1 for the last 2 items if length >= 2
        labels = [1] * len(data)
        if len(data) >= 2:
            labels[-1] = -1
            labels[-2] = -1
        return labels

@pytest.fixture(autouse=True)
def patch_ml_internals():
    from app.services.answer_evaluator import AnswerEvaluator
    from app.system_optimiser.anomaly_detector import AnomalyDetector
    
    with patch('app.services.answer_evaluator.cosine_similarity', side_effect=mock_cosine_similarity), \
         patch.object(AnswerEvaluator, '_get_model', return_value=DummyModel()), \
         patch('app.system_optimiser.anomaly_detector.IsolationForest', DummyIsolationForest), \
         patch('app.system_optimiser.anomaly_detector.np.array') as mock_np_array, \
         patch('app.system_optimiser.anomaly_detector.np.mean', side_effect=lambda x: sum(x)/len(x) if len(x)>0 else 0), \
         patch('app.system_optimiser.anomaly_detector.np.std', return_value=1.0), \
         patch('app.system_optimiser.anomaly_detector.np.percentile', side_effect=lambda x, q: max(x)), \
         patch('app.system_optimiser.anomaly_detector.np.zeros_like', side_effect=lambda x: [0.0]*len(x)), \
         patch('app.system_optimiser.load_predictor.np.clip', side_effect=lambda x, a, b: x), \
         patch('app.services.resume_analyzer.fitz.open') as mock_fitz, \
         patch('app.services.resume_analyzer.spacy.load') as mock_spacy:
        
        # Mock numpy operations used in anomaly detector
        class MockNumpyArray:
            def __init__(self, data): self.data = data
            def reshape(self, *args, **kwargs): return self
            def flatten(self): return self
            def __sub__(self, other): return MockNumpyArray([x - other for x in self.data])
            def __truediv__(self, other): return MockNumpyArray([x / other for x in self.data])
            def __len__(self): return len(self.data)
            def __iter__(self): return iter(self.data)
            def __getitem__(self, idx): return self.data[idx]
        
        mock_np_array.side_effect = lambda x, *args, **kwargs: MockNumpyArray(x)
        
        # Mock spacy used in resume analyzer
        class MockToken:
            def __init__(self, text): self.lemma_ = text.lower()
        class MockDoc:
            def __init__(self, text): 
                self.noun_chunks = []
                self.tokens = [MockToken(t) for t in text.split()]
            def __iter__(self): return iter(self.tokens)
        mock_spacy.return_value = lambda text: MockDoc(text)
        
        # Mock fitz used in resume analyzer
        class MockPage:
            def get_text(self, *args): return "Python developer with Java"
        class MockDocCtx:
            def __enter__(self): return [MockPage()]
            def __exit__(self, *args): pass
        mock_fitz.return_value = MockDocCtx()
        
        yield
