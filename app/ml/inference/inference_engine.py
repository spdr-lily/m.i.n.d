import unicodedata
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

    # A symptom is considered "generic" when it is part of the criteria of
    # more than this many disorders (e.g. depressed mood, avoidance, worry).
    GENERIC_SYMPTOM_THRESHOLD = 2
    # Discount applied when *every* matched symptom is generic.  Kept mild
    # because a well-supported diagnosis may legitimately match generic
    # symptoms together with specific ones.
    GENERIC_MATCH_PENALTY = 0.85
    # Catch-all ("unspecified"/"other") disorders should only be used when
    # no specific disorder is supported; demote them when they have no
    # criteria groups of their own.
    CATCH_ALL_PENALTY = 0.6
    CATCH_ALL_TERMS = (
        "não especificad",
        "nao especificad",
        "outro transtorno",
        "outros transtornos",
    )
    # Residual diagnoses ("unspecified"/"other") and subtype/etiology variants
    # are secondary descriptions of another disorder.  When a more specific
    # diagnosis is already supported, they are demoted so that marking the
    # criteria of one disorder does not bring a trail of "posterior"
    # reference disorders along with it.
    RESIDUAL_TERMS = CATCH_ALL_TERMS + (
        "outra apresentação especificada",
        "outra apresentacao especificada",
    )
    VARIANT_TERMS = (
        "apresentação combinada",
        "apresentacao combinada",
        "apresentação predominante",
        "apresentacao predominante",
        "induzido por substância",
        "induzido por substancia",
        "induzida por substância",
        "induzida por substancia",
        "devido a outra condição médica",
        "devido a outra condicao medica",
    )
    RESIDUAL_SECONDARY_PENALTY = 0.5
    VARIANT_SECONDARY_PENALTY = 0.6
    # Only demote when there is at least a minimal specific signal.
    MIN_SPECIFIC_PROBABILITY = 0.1
    # A disorder matched by only one or two symptoms has weak absolute
    # evidence, even if its required criteria are met.  Scale the probability
    # linearly up to this number of distinct matched symptoms.
    MIN_ABSOLUTE_EVIDENCE = 3

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
        symptom_disorder_count = self._symptom_disorder_counts(disorders_with_criteria)

        evaluations = self.criteria_evaluator.evaluate_all(
            disorders_with_criteria, observations
        )

        results = []
        for eval_result in evaluations:
            result = self._build_result(eval_result, symptom_disorder_count)
            results.append(result)

        if scale_scores:
            results = self._apply_scale_adjustments(results, scale_scores)
            results = self._apply_ml_scale_prediction(results, scale_scores)

        results = self._demote_secondary_disorders(results)

        if relationships:
            results = self._apply_exclusion_rules(results, relationships)
            results = self._apply_comorbidity_weights(results, relationships)

        results.sort(key=lambda r: r.probability, reverse=True)
        return results

    def _build_result(
        self,
        eval_result: DisorderEvaluation,
        symptom_disorder_count: Optional[Dict[int, int]] = None,
    ) -> InferenceResult:
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

        # Weak absolute evidence cannot sustain a high probability even when
        # the required criteria happen to be satisfied.
        if 0 < eval_result.met_criteria < self.MIN_ABSOLUTE_EVIDENCE:
            probability *= eval_result.met_criteria / self.MIN_ABSOLUTE_EVIDENCE

        has_group_support = (
            bool(eval_result.group_evaluations)
            and eval_result.all_groups_satisfied
        )

        if not has_group_support and self._is_catch_all(eval_result.disorder_name):
            probability *= self.CATCH_ALL_PENALTY

        if symptom_disorder_count:
            # Do not penalize a disorder that is fully supported by its own
            # DSM criteria groups; the penalty targets spurious matches that
            # rely only on symptoms shared across many disorders.
            matched_symptom_ids = {r.symptom_id for r in matched}
            if not has_group_support and len(matched_symptom_ids) >= 2:
                generic = [
                    sid for sid in matched_symptom_ids
                    if symptom_disorder_count.get(sid, 0) > self.GENERIC_SYMPTOM_THRESHOLD
                ]
                if len(generic) == len(matched_symptom_ids):
                    probability *= self.GENERIC_MATCH_PENALTY

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

    @classmethod
    def _is_catch_all(cls, disorder_name: Optional[str]) -> bool:
        normalized = cls._normalize_name(disorder_name)
        return any(
            cls._normalize_name(term) in normalized for term in cls.CATCH_ALL_TERMS
        )

    @staticmethod
    def _normalize_name(disorder_name: Optional[str]) -> str:
        """Lowercase and strip accents for robust Portuguese name matching."""
        if not disorder_name:
            return ""
        decomposed = unicodedata.normalize("NFKD", disorder_name.lower())
        return "".join(ch for ch in decomposed if not unicodedata.combining(ch))

    @classmethod
    def _secondary_penalty(cls, disorder_name: Optional[str]) -> Optional[float]:
        """Return the demotion factor for residual/variant diagnoses."""
        normalized = cls._normalize_name(disorder_name)
        if not normalized:
            return None
        if any(cls._normalize_name(term) in normalized for term in cls.RESIDUAL_TERMS):
            return cls.RESIDUAL_SECONDARY_PENALTY
        if any(cls._normalize_name(term) in normalized for term in cls.VARIANT_TERMS):
            return cls.VARIANT_SECONDARY_PENALTY
        return None

    @classmethod
    def _demote_secondary_disorders(
        cls, results: List[InferenceResult]
    ) -> List[InferenceResult]:
        """Demote residual/variant diagnoses when a specific one is stronger.

        Residual ("não especificado"/"outro transtorno") and variant
        ("apresentação ...", "induzido por substância", "devido a outra
        condição médica") diagnoses exist to label cases that do not fit a
        specific disorder.  When the specific disorder is already supported
        they should not compete with it, otherwise marking one disorder's
        criteria activates a whole tail of reference disorders.
        """
        specific = [
            r
            for r in results
            if not r.excluded and cls._secondary_penalty(r.disorder_name) is None
        ]
        best_specific = max((r.probability for r in specific), default=0.0)
        if best_specific < cls.MIN_SPECIFIC_PROBABILITY:
            return results

        for result in results:
            if result.excluded or result.probability <= 0.0:
                continue
            penalty = cls._secondary_penalty(result.disorder_name)
            if penalty is None:
                continue
            # Only demote secondary diagnoses that do not already lead.
            if result.probability <= best_specific:
                result.probability = round(result.probability * penalty, 4)

        return results

    @staticmethod
    def _symptom_disorder_counts(disorders_with_criteria: List[tuple]) -> Dict[int, int]:
        """Count in how many distinct disorders each symptom appears."""
        counts: Dict[int, int] = {}
        for item in disorders_with_criteria:
            criteria_list = item[2] if len(item) >= 3 else []
            seen = set()
            for criterion in criteria_list:
                symptom_id = criterion.symptom_id
                if symptom_id in seen:
                    continue
                seen.add(symptom_id)
                counts[symptom_id] = counts.get(symptom_id, 0) + 1
        return counts

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
