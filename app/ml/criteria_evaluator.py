from typing import List, Optional
from dataclasses import dataclass, field
from app.models.base import DiagnosticCriteria, SymptomObservation


@dataclass
class CriteriaResult:
    disorder_id: int
    criteria_id: int
    symptom_id: int
    symptom_name: Optional[str] = None
    required_presence: bool = True
    minimum_duration_days: Optional[int] = None
    present: bool = False
    duration_met: bool = True
    intensity_score: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class DisorderEvaluation:
    disorder_id: int
    disorder_name: Optional[str] = None
    criteria_results: List[CriteriaResult] = field(default_factory=list)
    total_criteria: int = 0
    met_criteria: int = 0
    required_met: bool = False
    duration_met: bool = True
    probability: float = 0.0


class CriteriaEvaluator:

    # DSM-5-TR: MDD requires at least 1 of these 2 core symptoms
    DSM5_MDD_REQUIRED_SYMPTOMS = {1, 2}
    MDD_MINIMUM_COUNT = 5

    def evaluate_disorder(
        self,
        disorder_id: int,
        disorder_name: Optional[str],
        criteria_list: List[DiagnosticCriteria],
        observations: List[SymptomObservation]
    ) -> DisorderEvaluation:
        eval_result = DisorderEvaluation(
            disorder_id=disorder_id,
            disorder_name=disorder_name
        )

        if not criteria_list:
            return eval_result

        eval_result.total_criteria = len(criteria_list)

        for criterion in criteria_list:
            matching_obs = [
                o for o in observations
                if o.symptom_id == criterion.symptom_id
            ]

            present = len(matching_obs) > 0

            duration_met = True
            intensity_score = None
            notes = None

            if present:
                obs = matching_obs[0]
                if obs.intensity is not None:
                    intensity_score = float(obs.intensity)
                if criterion.minimum_duration_days and obs.duration_days:
                    duration_met = obs.duration_days >= criterion.minimum_duration_days
                notes = obs.clinical_notes

            result = CriteriaResult(
                disorder_id=disorder_id,
                criteria_id=criterion.criteria_id,
                symptom_id=criterion.symptom_id,
                required_presence=criterion.required_presence,
                minimum_duration_days=criterion.minimum_duration_days,
                present=present,
                duration_met=duration_met,
                intensity_score=intensity_score,
                notes=notes
            )

            eval_result.criteria_results.append(result)

            if present and duration_met:
                eval_result.met_criteria += 1

        all_required_met = all(
            r.present and r.duration_met
            for r in eval_result.criteria_results
            if r.required_presence
        )
        eval_result.required_met = all_required_met

        # DSM-5-TR MDD: 5+ symptoms AND at least 1 of depressed mood or anhedonia
        if disorder_name and disorder_name.upper() in ("MDD", "MAJOR DEPRESSIVE DISORDER"):
            core_symptom_ids = self.DSM5_MDD_REQUIRED_SYMPTOMS
            core_present = any(
                r.symptom_id in core_symptom_ids and r.present and r.duration_met
                for r in eval_result.criteria_results
            )
            eval_result.required_met = core_present and eval_result.met_criteria >= self.MDD_MINIMUM_COUNT

        all_durations_met = all(
            r.duration_met for r in eval_result.criteria_results if r.present
        )
        eval_result.duration_met = all_durations_met

        if eval_result.total_criteria > 0:
            eval_result.probability = eval_result.met_criteria / eval_result.total_criteria

        return eval_result

    def evaluate_all(
        self,
        disorders_with_criteria: List[tuple],
        observations: List[SymptomObservation]
    ) -> List[DisorderEvaluation]:
        results = []
        for disorder_id, disorder_name, criteria_list in disorders_with_criteria:
            eval_result = self.evaluate_disorder(
                disorder_id, disorder_name, criteria_list, observations
            )
            results.append(eval_result)
        return sorted(results, key=lambda r: r.probability, reverse=True)
