import re
import fitz
import spacy
from pathlib import Path
from app.utils.skill_dictionary import SKILL_DICTIONARY


class ResumeAnalyzer:
    def __init__(self):
        self._nlp = None

    def _get_nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                from spacy.cli import download
                download("en_core_web_sm")
                self._nlp = spacy.load("en_core_web_sm")
        return self._nlp

    def extract_text(self, file_path: str, content_type: str) -> str:
        if content_type == "application/pdf":
            return self._extract_pdf_text(file_path)
        return self._extract_plain_text(file_path)

    def _extract_pdf_text(self, path: str) -> str:
        pages = []
        with fitz.open(path) as doc:
            for page in doc:
                pages.append(page.get_text("text"))
        return self._clean_text("\n".join(pages))

    def _extract_plain_text(self, path: str) -> str:
        return self._clean_text(Path(path).read_text(encoding="utf-8", errors="ignore"))

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"[^\x20-\x7E\n]", " ", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract_skills(self, text: str) -> list[str]:
        found: set[str] = set()
        text_lower = text.lower()
        for skill in SKILL_DICTIONARY:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found.add(skill)
        nlp = self._get_nlp()
        doc = nlp(text[:120_000])
        skill_lower_map = {s.lower(): s for s in SKILL_DICTIONARY}
        for token in doc:
            if token.lemma_.lower() in skill_lower_map:
                found.add(skill_lower_map[token.lemma_.lower()])
        for chunk in doc.noun_chunks:
            ct = chunk.text.lower().strip()
            if ct in skill_lower_map:
                found.add(skill_lower_map[ct])
        return sorted(found)
