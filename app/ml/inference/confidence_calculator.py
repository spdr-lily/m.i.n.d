from typing import List, Optional
from app.ml.evaluation.criteria_evaluator import DisorderEvaluation


def calculate_criteria_confidence(probability: float, eval_result: DisorderEvaluation) -> float:
    """Confidence based on criteria match ratio and symptom intensity."""
    if eval_result.total_criteria == 0:
        return 0.0
    ratio = eval_result.met_criteria / eval_result.total_criteria
    base_confidence = (probability + ratio) / 2
    matched = [r for r in eval_result.criteria_results if r.present]
    scores = [r.intensity_score for r in matched if r.intensity_score is not None]
    if scores:
        avg = sum(scores) / len(scores)
        intensity_bonus = (avg / 100.0) * 0.1
        base_confidence += intensity_bonus
    return min(base_confidence + 0.05, 1.0)


def calculate_bayesian_confidence(posterior_probability: float) -> float:
    """Confidence derived directly from Bayesian posterior."""
    return round(posterior_probability, 4)
