from typing import Dict, List, Optional
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
    observed_duration_days: Optional[int] = None
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
    """Evaluate observed symptoms against DSM-5-TR criteria.

    Scoring counts *unique symptoms* instead of raw criteria rows so that
    duplicated mappings (e.g. the same symptom registered twice for a
    disorder) cannot inflate the match ratio.

    When criteria groups/rules are available, each group is satisfied only
    when its required number of distinct symptoms is met.  This avoids the
    "vacuously satisfied" problem of disorders that have no required
    criterion and prevents a single generic symptom from activating a whole
    disorder.
    """

    # Minimum number of distinct symptoms required when a disorder has no
    # groups and no required criteria (only meaningful for 3+ criteria).
    MIN_EVIDENCE_WHEN_UNCONSTRAINED = 2

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

        ordered_groups = self._order_groups(groups or [])
        group_labels = self._assign_group_labels(criteria_list, ordered_groups)

        group_rules: Dict[str, CriteriaRule] = {}
        for group in ordered_groups:
            rules = list(getattr(group, "rules", None) or [])
            if rules:
                group_rules[group.group_label] = rules[0]

        for index, criterion in enumerate(criteria_list):
            label = group_labels[index] if index < len(group_labels) else None

            matching_obs = [
                o for o in observations if o.symptom_id == criterion.symptom_id
            ]
            present = len(matching_obs) > 0

            duration_met = True
            intensity_score = None
            observed_duration_days = None
            notes = None

            if present:
                obs = matching_obs[0]
                if obs.intensity is not None:
                    intensity_score = float(obs.intensity)
                if obs.duration_days is not None:
                    observed_duration_days = int(obs.duration_days)
                if criterion.minimum_duration_days and observed_duration_days is not None:
                    duration_met = observed_duration_days >= criterion.minimum_duration_days
                notes = obs.clinical_notes

            result = CriteriaResult(
                disorder_id=disorder_id,
                criteria_id=criterion.criteria_id,
                symptom_id=criterion.symptom_id,
                required_presence=criterion.required_presence,
                minimum_duration_days=criterion.minimum_duration_days,
                present=present,
                duration_met=duration_met,
                observed_duration_days=observed_duration_days,
                intensity_score=intensity_score,
                notes=notes,
                group_label=label,
            )
            eval_result.criteria_results.append(result)

        # Count distinct symptoms, not raw criteria rows.
        met_symptom_ids = {
            r.symptom_id
            for r in eval_result.criteria_results
            if r.present and r.duration_met
        }
        total_symptom_ids = {c.symptom_id for c in criteria_list}
        eval_result.met_criteria = len(met_symptom_ids)
        eval_result.total_criteria = len(total_symptom_ids)

        # Evaluate each group using distinct symptoms as well.
        for group in ordered_groups:
            label = group.group_label
            group_criteria = [
                r for r in eval_result.criteria_results if r.group_label == label
            ]
            if not group_criteria:
                continue

            met_in_group = len(
                {r.symptom_id for r in group_criteria if r.present and r.duration_met}
            )
            total_in_group = len({r.symptom_id for r in group_criteria})
            rule = group_rules.get(label)
            required_count = (
                min(rule.required_count, total_in_group)
                if rule and rule.required_count is not None
                else total_in_group
            )
            min_duration = rule.min_duration_days if rule else None

            group_duration_met = True
            if min_duration:
                for r in group_criteria:
                    if (
                        r.present
                        and r.observed_duration_days is not None
                        and r.observed_duration_days < min_duration
                    ):
                        group_duration_met = False
                        break

            eval_result.group_evaluations.append(
                GroupEvaluation(
                    group_label=label,
                    total_in_group=total_in_group,
                    met_in_group=met_in_group,
                    required_count=required_count,
                    group_satisfied=met_in_group >= required_count,
                    min_duration_days=min_duration,
                    duration_met=group_duration_met,
                )
            )

        required_criteria = [
            r for r in eval_result.criteria_results if r.required_presence
        ]

        if eval_result.group_evaluations:
            eval_result.all_groups_satisfied = all(
                group.group_satisfied for group in eval_result.group_evaluations
            )
        elif required_criteria:
            eval_result.all_groups_satisfied = all(
                r.present and r.duration_met for r in required_criteria
            )
        else:
            # No groups and no required criteria: require a minimum amount of
            # evidence instead of returning True for zero matches.
            min_evidence = (
                self.MIN_EVIDENCE_WHEN_UNCONSTRAINED
                if eval_result.total_criteria >= 3
                else 1
            )
            eval_result.all_groups_satisfied = (
                eval_result.total_criteria > 0
                and eval_result.met_criteria >= min_evidence
            )

        all_durations_met = all(
            r.duration_met for r in eval_result.criteria_results if r.present
        )
        all_durations_met = all_durations_met and all(
            group.duration_met for group in eval_result.group_evaluations
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
        for item in disorders_with_criteria:
            if len(item) == 4:
                disorder_id, disorder_name, criteria_list, groups = item
            else:
                disorder_id, disorder_name, criteria_list = item
                groups = None
            eval_result = self.evaluate_disorder(
                disorder_id, disorder_name, criteria_list, observations, groups,
            )
            results.append(eval_result)
        return sorted(results, key=lambda r: r.probability, reverse=True)

    # ── Group helpers ──────────────────────────────────────────────────

    @staticmethod
    def _order_groups(groups: List[CriteriaGroup]) -> List[CriteriaGroup]:
        """Order groups by explicit sort_order, then by primary key."""
        return sorted(
            groups,
            key=lambda g: (
                getattr(g, "sort_order", 0) or 0,
                getattr(g, "group_id", 0) or 0,
            ),
        )

    @staticmethod
    def _assign_group_labels(
        criteria_list: List[DiagnosticCriteria],
        ordered_groups: List[CriteriaGroup],
    ) -> List[Optional[str]]:
        """Assign each criterion to a group using the rule's ``total_count``.

        Criteria are ordered by ``criteria_id`` (the order in which DSM
        criteria were seeded), and groups are filled sequentially.  The last
        group absorbs any remaining criteria when the configured totals do
        not add up to the exact number of rows.
        """
        if not ordered_groups:
            return [None for _ in criteria_list]

        totals: List[int] = []
        for group in ordered_groups:
            rules = list(getattr(group, "rules", None) or [])
            rule = rules[0] if rules else None
            totals.append(int(rule.total_count) if rule and rule.total_count else 0)

        capacity: List[int] = []
        remaining = len(criteria_list)

        if any(total > 0 for total in totals):
            for index, total in enumerate(totals):
                if index == len(totals) - 1:
                    cap = remaining
                else:
                    cap = min(max(total, 0), remaining)
                capacity.append(cap)
                remaining -= cap
        else:
            # No usable totals: distribute evenly across groups.
            group_count = len(ordered_groups)
            base = len(criteria_list) // group_count
            extra = len(criteria_list) % group_count
            capacity = [base + (1 if i < extra else 0) for i in range(group_count)]

        labels: List[Optional[str]] = []
        for group, cap in zip(ordered_groups, capacity):
            labels.extend([group.group_label] * cap)
        labels.extend([None] * (len(criteria_list) - len(labels)))
        return labels[: len(criteria_list)]
