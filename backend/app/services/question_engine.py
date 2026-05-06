import json
import random
from pathlib import Path

_DATASET_PATH = Path(__file__).parent.parent / "utils" / "questions_dataset.json"


class QuestionEngine:
    DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}

    def __init__(self):
        self._bank: list[dict] = []

    def _get_bank(self) -> list[dict]:
        if not self._bank:
            if not _DATASET_PATH.exists():
                raise FileNotFoundError(f"Dataset not found at {_DATASET_PATH}")
            with open(_DATASET_PATH, "r", encoding="utf-8") as f:
                self._bank = json.load(f)
        return self._bank

    _SKILL_TOPIC_MAP = {
        "python": "Python", "javascript": "JavaScript", "typescript": "JavaScript",
        "java": "Java", "sql": "Databases", "postgresql": "Databases",
        "mysql": "Databases", "mongodb": "Databases", "machine learning": "Machine Learning",
        "deep learning": "Machine Learning", "nlp": "Machine Learning",
        "data structures": "Data Structures", "algorithms": "Algorithms",
        "react": "Web Development", "vue": "Web Development", "docker": "DevOps",
        "aws": "Cloud Computing", "system design": "System Design", "oop": "Object-Oriented Programming",
    }

    def select_topic(self, skills: list[str]) -> str:
        for skill in skills:
            topic = self._SKILL_TOPIC_MAP.get(skill.lower())
            if topic:
                return topic
        return "General"

    def generate(self, skills: list[str], topic: str, difficulty: str = "medium", num_questions: int = 5) -> list[dict]:
        bank = self._get_bank()
        selected, seen_ids = [], set()

        def _pick(filter_topic, filter_diff, n):
            candidates = [
                q for q in bank
                if (filter_topic is None or q.get("topic", "").lower() == filter_topic.lower())
                and (filter_diff is None or q.get("difficulty", "") == filter_diff)
                and q.get("id", q["question"]) not in seen_ids
            ]
            draw = random.sample(candidates, min(n, len(candidates)))
            for q in draw:
                seen_ids.add(q.get("id", q["question"]))
                selected.append(q)

        _pick(topic, difficulty, num_questions)
        if len(selected) < num_questions:
            for adj in (["easy","medium","hard"] if difficulty == "medium" else ["medium","easy","hard"]):
                if len(selected) >= num_questions: break
                _pick(topic, adj, num_questions - len(selected))
        if len(selected) < num_questions:
            _pick("General", difficulty, num_questions - len(selected))
        if len(selected) < num_questions:
            _pick(None, None, num_questions - len(selected))

        selected.sort(key=lambda q: self.DIFFICULTY_ORDER.get(q.get("difficulty","medium"), 1))
        return selected[:num_questions]
