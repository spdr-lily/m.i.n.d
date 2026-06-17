from typing import Dict, List
import pytest
from app.ml.inference.inference_engine import InferenceEngine, InferenceResult
from app.ml.inference.confidence_calculator import calculate_criteria_confidence


class TestInferenceEngine:

    def setup_method(self):
        self.engine = InferenceEngine()

    def test_calculate_returns_sorted_results(self, mdd_criteria, mdd_symptoms_positive, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]

        results = self.engine.calculate(disorders_data, mdd_symptoms_positive)

        assert len(results) == 3
        assert results[0].probability >= results[1].probability
        assert results[1].probability >= results[2].probability

    def test_mdd_highest_probability_with_depression_symptoms(self, mdd_criteria, mdd_symptoms_positive, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]

        results = self.engine.calculate(disorders_data, mdd_symptoms_positive)

        mdd_result = next(r for r in results if r.disorder_id == 1)
        assert mdd_result.probability > 0.3
        assert mdd_result.required_met is True
        assert mdd_result.criteria_met >= 5

    def test_exclusion_rule_applied(self, mdd_criteria, mdd_symptoms_positive, mdd_exclusion_relationship, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]

        results = self.engine.calculate(disorders_data, mdd_symptoms_positive, mdd_exclusion_relationship)

        excluded_disorders = [r for r in results if r.excluded]
        kept_disorders = [r for r in results if not r.excluded]

        assert any(r.disorder_id == 1 for r in kept_disorders) or any(r.disorder_id == 2 for r in kept_disorders)
        if excluded_disorders:
            assert all(r.exclusion_reason for r in excluded_disorders)

    def test_comorbidity_boost(self, mdd_criteria, mdd_symptoms_positive, mdd_gad_comorbidity, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]

        results_without = self.engine.calculate(disorders_data, mdd_symptoms_positive)
        results_with = self.engine.calculate(disorders_data, mdd_symptoms_positive, mdd_gad_comorbidity)

        mdd_without = next(r for r in results_without if r.disorder_id == 1)
        mdd_with = next(r for r in results_with if r.disorder_id == 1)
        gad_with = next(r for r in results_with if r.disorder_id == 3)
        gad_without = next(r for r in results_without if r.disorder_id == 3)

        assert mdd_with.probability >= mdd_without.probability
        assert gad_with.probability >= gad_without.probability

    def test_empty_observations_returns_zero_probability(self, mdd_criteria, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]

        results = self.engine.calculate(disorders_data, [])

        for r in results:
            assert r.probability == 0.0

    def test_required_not_met_reduces_probability(self, mdd_criteria, mdd_symptoms_partial, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]

        results = self.engine.calculate(disorders_data, mdd_symptoms_partial)

        mdd_result = next(r for r in results if r.disorder_id == 1)
        assert mdd_result.required_met is False
        assert mdd_result.probability < 0.3

    # New inference engine tests
    def test_scale_adjustment_no_match_no_boost(self, mdd_criteria, mdd_symptoms_positive, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]
        results = self.engine.calculate(disorders_data, mdd_symptoms_positive, scale_scores={"PHQ-9": 25.0})
        assert all(r.probability > 0.0 for r in results)

    def test_apply_scale_adjustments_boost_matching_name(self):
        results = [
            InferenceResult(disorder_id=1, disorder_name="Transtorno Depressivo Maior", probability=0.5),
            InferenceResult(disorder_id=2, disorder_name="Transtorno Bipolar", probability=0.5),
        ]
        results = self.engine._apply_scale_adjustments(results, {"PHQ-9": 20.0})
        assert results[0].probability == pytest.approx(0.63, rel=0.01)
        assert results[1].probability == 0.5

    def test_apply_scale_adjustments_below_threshold(self):
        results = [InferenceResult(disorder_id=1, disorder_name="Transtorno Depressivo Maior", probability=0.5)]
        results = self.engine._apply_scale_adjustments(results, {"PHQ-9": 5.0})
        assert results[0].probability == 0.5

    def test_apply_scale_adjustments_caps_at_098(self):
        results = [InferenceResult(disorder_id=1, disorder_name="Transtorno Depressivo Maior", probability=0.95)]
        results = self.engine._apply_scale_adjustments(results, {"PHQ-9": 20.0})
        assert results[0].probability <= 0.98

    def test_scale_adjustments_no_matching_scale(self):
        results = [InferenceResult(disorder_id=1, disorder_name="Teste", probability=0.5)]
        results = self.engine._apply_scale_adjustments(results, {"SCALA_INEXISTENTE": 99.0})
        assert results[0].probability == 0.5

    def test_build_result_duration_not_met(self, mdd_criteria, mdd_symptoms_partial, disorders):
        disorders_data = [(d.disorder_id, d.disorder_name, mdd_criteria) for d in disorders]
        results = self.engine.calculate(disorders_data, mdd_symptoms_partial)
        mdd = next(r for r in results if r.disorder_id == 1)
        assert mdd.duration_met is False

    def test_inference_result_defaults(self):
        r = InferenceResult(disorder_id=1)
        assert r.probability == 0.0
        assert r.confidence_level == 0.0
        assert r.required_met is False
        assert r.duration_met is True
        assert r.criteria_met == 0
        assert r.excluded is False
        assert r.requires_human_review is True

    def test_calculate_criteria_confidence_zero_total(self):
        mock_eval = _make_mock_evaluation(total_criteria=0)
        assert calculate_criteria_confidence(0.5, mock_eval) == 0.0

    def test_calculate_criteria_confidence_full_match(self):
        mock_eval = _make_mock_evaluation(met_criteria=6, total_criteria=6, intensity_scores=[8.0])
        conf = calculate_criteria_confidence(0.8, mock_eval)
        assert conf > 0.8

    def test_calculate_criteria_confidence_no_intensity(self):
        mock_eval = _make_mock_evaluation(met_criteria=4, total_criteria=8, intensity_scores=[])
        conf = calculate_criteria_confidence(0.5, mock_eval)
        expected = min((0.5 + 4/8) / 2 + 0.05, 1.0)
        assert conf == pytest.approx(expected, rel=0.01)

    def test_exclusion_low_probability_no_exclusion(self, disorders, bipolar_criteria):
        from tests.ml.conftest import MockDiagnosisRelationship, MockSymptomObservation
        from uuid import uuid4
        rels = [MockDiagnosisRelationship(1, 1, 2, "exclusion", 0.0, "Mutual exclusion")]
        empty_obs = [MockSymptomObservation(1, str(uuid4()), 1, 1.0, "daily", 2, "Very mild")]
        disorders_data = [(d.disorder_id, d.disorder_name, []) for d in disorders]
        results = self.engine.calculate(disorders_data, empty_obs, rels)
        excluded = [r for r in results if r.excluded]
        assert len(excluded) == 0


def _make_mock_evaluation(met_criteria: int = 0, total_criteria: int = 0, intensity_scores: List[float] = None):
    class MockCriteriaResult:
        def __init__(self, present: bool, intensity_score: float = None):
            self.present = present
            self.intensity_score = intensity_score

    class MockEval:
        total_criteria = total_criteria
        met_criteria = met_criteria
        all_groups_satisfied = met_criteria >= (total_criteria // 2) if total_criteria > 0 else False
        all_durations_met = True
        disorder_id = 1
        disorder_name = "Test Disorder"
        criteria_results = []

    mock = MockEval()
    if intensity_scores:
        mock.criteria_results = [MockCriteriaResult(True, s) for s in intensity_scores]
        if met_criteria > len(mock.criteria_results):
            for _ in range(met_criteria - len(mock.criteria_results)):
                mock.criteria_results.append(MockCriteriaResult(True, None))
    else:
        mock.criteria_results = [MockCriteriaResult(True, None) for _ in range(met_criteria)]
    mock.all_groups_satisfied = met_criteria >= (total_criteria // 2) if total_criteria > 0 else False
    return mock
