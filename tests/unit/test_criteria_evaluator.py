from app.ml.evaluation.criteria_evaluator import CriteriaEvaluator


class TestCriteriaEvaluator:

    def setup_method(self):
        self.evaluator = CriteriaEvaluator()

    def test_mdd_positive_case_meets_criteria(self, mdd_criteria, mdd_symptoms_positive):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, mdd_symptoms_positive)

        assert result.all_groups_satisfied, "Required symptoms (depressed mood + anhedonia) should be met"
        assert result.all_durations_met, "Duration criteria should be met"
        assert result.met_criteria >= 5, "DSM-5 requires >= 5 symptoms for MDD"
        assert result.probability >= 0.5
        assert len(result.criteria_results) == len(mdd_criteria)

    def test_mdd_partial_case_low_probability(self, mdd_criteria, mdd_symptoms_partial):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, mdd_symptoms_partial)

        assert result.all_groups_satisfied is False, "Not all required symptoms present"
        assert result.all_durations_met is False, "Duration < 14 days"
        assert result.met_criteria <= 2, "Only 2 symptoms present"
        assert result.probability < 0.5

    def test_bipolar_positive_case(self, bipolar_criteria, bipolar_symptoms_positive):
        result = self.evaluator.evaluate_disorder(2, "Bipolar I", bipolar_criteria, bipolar_symptoms_positive)

        assert result.all_groups_satisfied, "Required manic symptoms should be met"
        assert result.probability > 0.5
        assert result.met_criteria >= 3, "≥3 manic symptoms required"

    def test_no_criteria_returns_zero_probability(self, mdd_symptoms_positive):
        result = self.evaluator.evaluate_disorder(99, "Unknown", [], mdd_symptoms_positive)

        assert result.total_criteria == 0
        assert result.probability == 0.0
        assert len(result.criteria_results) == 0

    def test_empty_observations_returns_zero(self, mdd_criteria):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, [])

        assert result.all_groups_satisfied is False
        assert result.met_criteria == 0
        assert result.probability == 0.0

    def test_evaluate_all_sorts_by_probability(self, mdd_criteria, mdd_symptoms_positive, bipolar_criteria, bipolar_symptoms_positive):
        disorders_data = [
            (1, "MDD", mdd_criteria),
            (2, "Bipolar I", bipolar_criteria),
        ]

        results = self.evaluator.evaluate_all(disorders_data, mdd_symptoms_positive)

        assert len(results) == 2
        assert results[0].probability >= results[1].probability

    def test_criteria_detail_accuracy(self, mdd_criteria, mdd_symptoms_positive):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, mdd_symptoms_positive)

        symptom_ids_present = {r.symptom_id for r in result.criteria_results if r.present}
        assert 1 in symptom_ids_present
        assert 2 in symptom_ids_present
        assert 3 not in symptom_ids_present
        assert 4 in symptom_ids_present


# ── Group/dedup/specificity refinements ──────────────────────────────

from dataclasses import dataclass
from typing import List, Optional
from uuid import uuid4
from tests.unit.conftest import MockDiagnosticCriteria, MockSymptomObservation


@dataclass
class _Rule:
    required_count: int
    total_count: int
    min_duration_days: Optional[int] = None


@dataclass
class _Group:
    group_label: str
    rules: List[_Rule]
    sort_order: int = 0
    group_id: int = 0


def _criteria(disorder_id: int, symptom_ids: List[int], required=()) -> List[MockDiagnosticCriteria]:
    return [
        MockDiagnosticCriteria(i + 1, disorder_id, sid, sid in required, None, "")
        for i, sid in enumerate(symptom_ids)
    ]


def _obs(symptom_ids: List[int], duration: int = 30, intensity: float = 10.0) -> List[MockSymptomObservation]:
    return [
        MockSymptomObservation(i + 1, str(uuid4()), sid, intensity, "daily", duration, "")
        for i, sid in enumerate(symptom_ids)
    ]


class TestCriteriaEvaluatorRefinements:

    def setup_method(self):
        self.evaluator = CriteriaEvaluator()

    def test_duplicate_symptom_criteria_counted_once(self):
        criteria = [
            MockDiagnosticCriteria(1, 1, 1, True, None, ""),
            MockDiagnosticCriteria(2, 1, 1, False, None, ""),
        ]
        result = self.evaluator.evaluate_disorder(1, "X", criteria, _obs([1]))
        assert result.total_criteria == 1
        assert result.met_criteria == 1
        assert result.probability == 1.0

    def test_group_rule_overrides_legacy_required_flags(self):
        criteria = _criteria(1, list(range(1, 10)), required=(1, 2))
        groups = [_Group("A", [_Rule(5, 9)])]
        result = self.evaluator.evaluate_disorder(
            1, "MDD", criteria, _obs([1, 2]), groups
        )
        assert result.met_criteria == 2
        assert result.all_groups_satisfied is False

    def test_group_rule_satisfied_with_minimum_symptoms(self):
        criteria = _criteria(1, list(range(1, 10)), required=(1, 2))
        groups = [_Group("A", [_Rule(5, 9)])]
        result = self.evaluator.evaluate_disorder(
            1, "MDD", criteria, _obs([1, 2, 4, 5, 6, 8]), groups
        )
        assert result.met_criteria == 6
        assert result.all_groups_satisfied is True

    def test_ordered_group_assignment_uses_total_count(self):
        criteria = _criteria(2, list(range(1, 7)))
        groups = [
            _Group("A", [_Rule(1, 1)], sort_order=1, group_id=1),
            _Group("B", [_Rule(3, 5)], sort_order=2, group_id=2),
        ]
        labels = {r.criteria_id: r.group_label for r in self.evaluator.evaluate_disorder(
            2, "Bipolar", criteria, [], groups
        ).criteria_results}
        assert labels == {1: "A", 2: "B", 3: "B", 4: "B", 5: "B", 6: "B"}

        partial = self.evaluator.evaluate_disorder(2, "Bipolar", criteria, _obs([1]), groups)
        assert partial.all_groups_satisfied is False

        full = self.evaluator.evaluate_disorder(2, "Bipolar", criteria, _obs([1, 2, 3, 4]), groups)
        assert full.all_groups_satisfied is True

    def test_no_required_criteria_requires_minimum_evidence(self):
        criteria = _criteria(3, [1, 2, 3])
        one = self.evaluator.evaluate_disorder(3, "X", criteria, _obs([1]))
        two = self.evaluator.evaluate_disorder(3, "X", criteria, _obs([1, 2]))
        assert one.all_groups_satisfied is False
        assert two.all_groups_satisfied is True

    def test_single_criterion_without_required_flag(self):
        criteria = _criteria(4, [1])
        result = self.evaluator.evaluate_disorder(4, "X", criteria, _obs([1]))
        assert result.all_groups_satisfied is True
