from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from app.ml.evaluation.criteria_evaluator import CriteriaEvaluator, DisorderEvaluation
from app.ml.models.dsm_icd_mapper import DSMICDMapper
from app.ml.models.assessment_scales import SCALE_DISORDER_MAP
from app.ml.inference.confidence_calculator import calculate_criteria_confidence
from app.ml.predictors.scale_predictor import predict_disorder_risk_from_scales
from app.models.base import SymptomObservation, DiagnosisRelationship, CriteriaGroup


@dataclass
class InferenceResult:
    disorder_id: int
    disorder_name: Optional[str] = None
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    probability: float = 0.0
    confidence_level: float = 0.0
    required_met: bool = False
    duration_met: bool = True
    criteria_met: int = 0
    criteria_total: int = 0
    excluded: bool = False
    exclusion_reason: Optional[str] = None
    requires_human_review: bool = True


class InferenceEngine:

    def __init__(self):
        self.criteria_evaluator = CriteriaEvaluator()
        self.dsm_icd_mapper = DSMICDMapper()

    def calculate(
        self,
        disorders_with_criteria: List[tuple],
        observations: List[SymptomObservation],
        relationships: Optional[List[DiagnosisRelationship]] = None,
        scale_scores: Optional[Dict[str, float]] = None,
    ) -> List[InferenceResult]:
        evaluations = self.criteria_evaluator.evaluate_all(
            disorders_with_criteria, observations
        )

        results = []
        for eval_result in evaluations:
            result = self._build_result(eval_result)
            results.append(result)

        if scale_scores:
            results = self._apply_scale_adjustments(results, scale_scores)
            results = self._apply_ml_scale_prediction(results, scale_scores)

        if relationships:
            results = self._apply_exclusion_rules(results, relationships)
            results = self._apply_comorbidity_weights(results, relationships)

        results.sort(key=lambda r: r.probability, reverse=True)
        return results

    def _build_result(self, eval_result: DisorderEvaluation) -> InferenceResult:
        probability = eval_result.probability

        matched = [r for r in eval_result.criteria_results if r.present]
        if matched:
            scores = [r.intensity_score for r in matched if r.intensity_score is not None]
            if scores:
                avg_intensity = sum(scores) / len(scores)
                intensity_factor = 0.5 + (avg_intensity / 100.0) * 0.5
                probability *= intensity_factor

        if not eval_result.all_groups_satisfied:
            probability *= 0.3

        if not eval_result.all_durations_met:
            probability *= 0.5

        confidence = calculate_criteria_confidence(probability, eval_result)

        return InferenceResult(
            disorder_id=eval_result.disorder_id,
            disorder_name=eval_result.disorder_name,
            probability=round(probability, 4),
            confidence_level=round(confidence, 4),
            required_met=eval_result.all_groups_satisfied,
            duration_met=eval_result.all_durations_met,
            criteria_met=eval_result.met_criteria,
            criteria_total=eval_result.total_criteria,
        )

    def _apply_scale_adjustments(
        self,
        results: List[InferenceResult],
        scale_scores: Dict[str, float],
    ) -> List[InferenceResult]:
        for scale_name, total_score in scale_scores.items():
            thresholds = SCALE_DISORDER_MAP.get(scale_name, [])
            for threshold, disorder_keywords in thresholds:
                if total_score >= threshold:
                    for result in results:
                        if result.disorder_name and any(
                            kw.lower() in result.disorder_name.lower()
                            for kw in disorder_keywords
                        ):
                            boost = 0.08 + (total_score - threshold) / 100.0
                            result.probability = min(round(result.probability + boost, 4), 0.98)
        return results

    def _apply_ml_scale_prediction(
        self,
        results: List[InferenceResult],
        scale_scores: Dict[str, float],
    ) -> List[InferenceResult]:
        """Apply ML/heuristic scale-based disorder risk as a complementary signal.

        Predicts disorder probabilities from scale scores using the heuristic
        scale risk predictor, then blends with existing probabilities.
        Blending weight: 0.15 (ML signal accounts for 15% of final probability).
        """
        ml_risks = predict_disorder_risk_from_scales(scale_scores)
        if not ml_risks:
            return results

        ml_weight = 0.15
        for result in results:
            if result.excluded:
                continue
            ml_prob = ml_risks.get(result.disorder_name, 0.0)
            if ml_prob > 0.01:
                blended = (1.0 - ml_weight) * result.probability + ml_weight * ml_prob
                result.probability = min(round(blended, 4), 0.98)
        return results

    def _apply_exclusion_rules(
        self,
        results: List[InferenceResult],
        relationships: List[DiagnosisRelationship],
    ) -> List[InferenceResult]:
        exclusion_rules = [
            r for r in relationships
            if r.relationship_type and "exclusion" in r.relationship_type.lower()
        ]

        for rule in exclusion_rules:
            source = next(
                (r for r in results if r.disorder_id == rule.source_disorder_id),
                None,
            )
            target = next(
                (r for r in results if r.disorder_id == rule.target_disorder_id),
                None,
            )
            if source and target and source.probability >= 0.3 and target.probability >= 0.3:
                if source.probability > target.probability:
                    lower = target
                    higher_name = source.disorder_name
                else:
                    lower = source
                    higher_name = target.disorder_name
                lower.excluded = True
                lower.exclusion_reason = f"Excluded by higher probability of {higher_name}"

        return results

    def _apply_comorbidity_weights(
        self,
        results: List[InferenceResult],
        relationships: List[DiagnosisRelationship],
    ) -> List[InferenceResult]:
        for rel in relationships:
            if rel.relationship_type and "comorbidity" in rel.relationship_type.lower():
                source = next(
                    (r for r in results if r.disorder_id == rel.source_disorder_id),
                    None,
                )
                target = next(
                    (r for r in results if r.disorder_id == rel.target_disorder_id),
                    None,
                )
                if source and target and not source.excluded and not target.excluded:
                    if rel.relationship_weight:
                        boost = float(rel.relationship_weight) * 0.1
                        source.probability = min(source.probability + boost, 1.0)
                        target.probability = min(target.probability + boost, 1.0)

        return results
