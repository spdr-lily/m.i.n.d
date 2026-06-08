from typing import List, Optional
from dataclasses import dataclass, field
from app.models.base import DiagnosticCriteria, SymptomObservation, CriteriaGroup, CriteriaRule


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
    group_label: Optional[str] = None


@dataclass
class GroupEvaluation:
    group_label: str
    total_in_group: int = 0
    met_in_group: int = 0
    required_count: int = 0
    group_satisfied: bool = False
    min_duration_days: Optional[int] = None
    duration_met: bool = True


@dataclass
class DisorderEvaluation:
    disorder_id: int
    disorder_name: Optional[str] = None
    criteria_results: List[CriteriaResult] = field(default_factory=list)
    group_evaluations: List[GroupEvaluation] = field(default_factory=list)
    total_criteria: int = 0
    met_criteria: int = 0
    all_groups_satisfied: bool = False
    all_durations_met: bool = True
    probability: float = 0.0


class CriteriaEvaluator:

    def evaluate_disorder(
        self,
        disorder_id: int,
        disorder_name: Optional[str],
        criteria_list: List[DiagnosticCriteria],
        observations: List[SymptomObservation],
        groups: Optional[List[CriteriaGroup]] = None,
    ) -> DisorderEvaluation:
        eval_result = DisorderEvaluation(
            disorder_id=disorder_id,
            disorder_name=disorder_name,
        )

        if not criteria_list:
            return eval_result

        eval_result.total_criteria = len(criteria_list)
        group_map: dict[Optional[str], list[DiagnosticCriteria]] = {}
        group_rules: dict[Optional[str], CriteriaRule] = {}

        if groups:
            for g in groups:
                group_map[g.group_label] = []
                for rule in g.rules:
                    group_rules[g.group_label] = rule

        for criterion in criteria_list:
            label = None
            if groups:
                for g in groups:
                    crit_ids = [c.criteria_id for c in group_map.get(g.group_label, [])]
                    if criterion.criteria_id not in crit_ids:
                        group_map.setdefault(g.group_label, []).append(criterion)
                        label = g.group_label
                        break

            matching_obs = [
                o for o in observations if o.symptom_id == criterion.symptom_id
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
                notes=notes,
                group_label=label,
            )
            eval_result.criteria_results.append(result)

            if present and duration_met:
                eval_result.met_criteria += 1

        if groups:
            for g in groups:
                rule = group_rules.get(g.group_label)
                group_criteria = [r for r in eval_result.criteria_results if r.group_label == g.group_label]
                met_in_group = sum(1 for r in group_criteria if r.present and r.duration_met)
                total_in_group = len(group_criteria)
                required_count = rule.required_count if rule else total_in_group
                min_duration = rule.min_duration_days if rule else None

                group_duration_met = True
                if min_duration:
                    group_duration_met = all(
                        r.duration_met for r in group_criteria if r.present
                    )

                group_eval = GroupEvaluation(
                    group_label=g.group_label,
                    total_in_group=total_in_group,
                    met_in_group=met_in_group,
                    required_count=required_count,
                    group_satisfied=met_in_group >= required_count,
                    min_duration_days=min_duration,
                    duration_met=group_duration_met,
                )
                eval_result.group_evaluations.append(group_eval)

                if not group_eval.group_satisfied:
                    eval_result.all_groups_satisfied = False

            if not eval_result.group_evaluations:
                all_required_met = all(
                    r.present and r.duration_met
                    for r in eval_result.criteria_results
                    if r.required_presence
                )
                eval_result.all_groups_satisfied = all_required_met
        else:
            all_required_met = all(
                r.present and r.duration_met
                for r in eval_result.criteria_results
                if r.required_presence
            )
            eval_result.all_groups_satisfied = all_required_met

        all_durations_met = all(
            r.duration_met for r in eval_result.criteria_results if r.present
        )
        eval_result.all_durations_met = all_durations_met

        if eval_result.total_criteria > 0:
            eval_result.probability = eval_result.met_criteria / eval_result.total_criteria

        return eval_result

    def evaluate_all(
        self,
        disorders_with_criteria: List[tuple],
        observations: List[SymptomObservation],
    ) -> List[DisorderEvaluation]:
        results = []
        for disorder_id, disorder_name, criteria_list, groups in disorders_with_criteria:
            eval_result = self.evaluate_disorder(
                disorder_id, disorder_name, criteria_list, observations, groups,
            )
            results.append(eval_result)
        return sorted(results, key=lambda r: r.probability, reverse=True)
