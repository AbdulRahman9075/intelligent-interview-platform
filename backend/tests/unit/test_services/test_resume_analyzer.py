import pytest
import os
from app.services.resume_analyzer import ResumeAnalyzer

def test_extract_plain_text(tmp_path):
    analyzer = ResumeAnalyzer()
    test_file = tmp_path / "resume.txt"
    test_file.write_text("I am a software engineer with 5 years of experience in Python and Java.")
    
    text = analyzer.extract_text(str(test_file), "text/plain")
    assert "Python" in text
    assert "Java" in text

def test_extract_skills():
    analyzer = ResumeAnalyzer()
    # It might take a moment to load the spacy model the first time
    text = "I have strong skills in Python, Java, REST APIs, and PostgreSQL. I also know React."
    skills = analyzer.extract_skills(text)
    
    # Check that at least some known skills were found (depends on SKILL_DICTIONARY)
    # We convert to lower to make the assertion more robust
    skills_lower = [s.lower() for s in skills]
    
    # We assume 'python', 'java', 'postgresql' or 'react' are in the dictionary
    assert any(expected in skills_lower for expected in ["python", "java", "postgresql", "react"])

def test_clean_text():
    analyzer = ResumeAnalyzer()
    dirty = "This   is \n\n\n a \t dirty text \x00"
    clean = analyzer._clean_text(dirty)
    assert "  " not in clean
    assert "\n\n\n" not in clean
    assert "\x00" not in clean
