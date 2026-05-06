import pytest
from app.services.answer_evaluator import AnswerEvaluator

def test_evaluate_answer_high_similarity():
    evaluator = AnswerEvaluator()
    # Provide an answer that closely matches the ideal answer
    ideal = "The core concept of REST is that it is a stateless architecture that uses standard HTTP methods."
    user = "REST is an architecture that is stateless and uses standard HTTP methods."
    
    result = evaluator.evaluate(user, ideal, "REST Architecture")
    print(f"High Similarity Result: {result}")
    
    assert result["similarity_score"] > 0.7  # Should have high cosine similarity

    assert result["normalized_score"] > 70
    assert isinstance(result["feedback"], str)
def test_evaluate_answer_low_similarity():
    evaluator = AnswerEvaluator()
    ideal = "The core concept of REST is that it is a stateless architecture that uses standard HTTP methods."
    user = "I like eating apples and bananas for breakfast."
    
    result = evaluator.evaluate(user, ideal, "REST Architecture")
    print(f"Low Similarity Result: {result}")
    
    assert result["similarity_score"] < 0.4  # Should be very low

    assert result["normalized_score"] < 40
    assert isinstance(result["feedback"], str)
    assert isinstance(result["weak_areas"], list)

def test_evaluate_answer_empty_user_answer():
    evaluator = AnswerEvaluator()
    ideal = "A binary search tree is a node-based binary tree data structure."
    user = ""
    
    result = evaluator.evaluate(user, ideal, "Data Structures")
    print(f"Empty Answer Result: {result}")
    
    assert result["normalized_score"] < 30

    assert "Weak answer" in result["feedback"] or "Answer did not align" in result["feedback"]
