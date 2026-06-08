from typing import List, Optional
from dataclasses import dataclass, field
from app.ml.evaluation.criteria_evaluator import CriteriaEvaluator, DisorderEvaluation
from app.ml.models.dsm_icd_mapper import DSMICDMapper
from app.ml.inference.confidence_calculator import calculate_criteria_confidence
from app.models.base import DiagnosticCriteria, SymptomObservation, DiagnosisRelationship


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
        relationships: Optional[List[DiagnosisRelationship]] = None
    ) -> List[InferenceResult]:
        evaluations = self.criteria_evaluator.evaluate_all(
            disorders_with_criteria, observations
        )

        results = []
        for eval_result in evaluations:
            result = self._build_result(eval_result)
            results.append(result)

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

        if not eval_result.required_met:
            probability *= 0.3

        if not eval_result.duration_met:
            probability *= 0.5

        confidence = calculate_criteria_confidence(probability, eval_result)

        return InferenceResult(
            disorder_id=eval_result.disorder_id,
            disorder_name=eval_result.disorder_name,
            probability=round(probability, 4),
            confidence_level=round(confidence, 4),
            required_met=eval_result.required_met,
            duration_met=eval_result.duration_met,
            criteria_met=eval_result.met_criteria,
            criteria_total=eval_result.total_criteria
        )

    def _apply_exclusion_rules(
        self,
        results: List[InferenceResult],
        relationships: List[DiagnosisRelationship]
    ) -> List[InferenceResult]:
        exclusion_rules = [
            r for r in relationships
            if r.relationship_type and "exclusion" in r.relationship_type.lower()
        ]

        for rule in exclusion_rules:
            source = next(
                (r for r in results if r.disorder_id == rule.source_disorder_id),
                None
            )
            target = next(
                (r for r in results if r.disorder_id == rule.target_disorder_id),
                None
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
        relationships: List[DiagnosisRelationship]
    ) -> List[InferenceResult]:
        for rel in relationships:
            if rel.relationship_type and "comorbidity" in rel.relationship_type.lower():
                source = next(
                    (r for r in results if r.disorder_id == rel.source_disorder_id),
                    None
                )
                target = next(
                    (r for r in results if r.disorder_id == rel.target_disorder_id),
                    None
                )
                if source and target and not source.excluded and not target.excluded:
                    if rel.relationship_weight:
                        boost = float(rel.relationship_weight) * 0.1
                        source.probability = min(source.probability + boost, 1.0)
                        target.probability = min(target.probability + boost, 1.0)

        return results
