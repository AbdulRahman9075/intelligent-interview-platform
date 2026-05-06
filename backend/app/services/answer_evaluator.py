from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings

BAND_EXCELLENT, BAND_GOOD, BAND_PARTIAL = 80, 65, 45


class AnswerEvaluator:
    def __init__(self):
        self._model = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def evaluate(self, user_answer: str, ideal_answer: str, topic: str) -> dict:
        model = self._get_model()
        embeddings = model.encode(
            [user_answer[:2000], ideal_answer[:2000]],
            batch_size=2, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False,
        )
        raw = float(cosine_similarity(embeddings[0].reshape(1,-1), embeddings[1].reshape(1,-1))[0][0])
        raw = max(0.0, min(1.0, raw))
        score = round(raw * 100, 2)
        return {
            "similarity_score": round(raw, 4),
            "normalized_score": score,
            "grade": "A" if score>=80 else "B" if score>=65 else "C" if score>=45 else "D" if score>=30 else "F",
            "feedback": self._feedback(score, topic),
            "weak_areas": self._weak_areas(score, topic),
        }

    def _feedback(self, score: float, topic: str) -> str:
        if score >= BAND_EXCELLENT:
            return f"Excellent! Your answer on {topic} closely matches the expected response. Strong understanding shown."
        if score >= BAND_GOOD:
            return f"Good answer on {topic}. You covered key concepts but missed some nuances. Review edge cases."
        if score >= BAND_PARTIAL:
            return f"Partial answer on {topic}. Basic understanding present but lacks technical depth and examples."
        if score >= 30:
            return f"Weak answer on {topic}. Only a few relevant points identified. Revisit the fundamentals."
        return f"Answer did not align well with {topic}. Consider studying this topic from scratch."

    def _weak_areas(self, score: float, topic: str) -> list[str]:
        weak = []
        if score < BAND_GOOD: weak.append(topic)
        if score < BAND_PARTIAL: weak.append("Conceptual Clarity")
        if score < 35: weak.extend(["Technical Depth", "Communication of Technical Concepts"])
        return weak
