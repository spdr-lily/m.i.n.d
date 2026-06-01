from app.ml.inference_engine import InferenceEngine


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
        assert mdd_result.probability > 0.5
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
