from app.ml.criteria_evaluator import CriteriaEvaluator


class TestCriteriaEvaluator:

    def setup_method(self):
        self.evaluator = CriteriaEvaluator()

    def test_mdd_positive_case_meets_criteria(self, mdd_criteria, mdd_symptoms_positive):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, mdd_symptoms_positive)

        assert result.required_met, "Required symptoms (depressed mood + anhedonia) should be met"
        assert result.duration_met, "Duration criteria should be met"
        assert result.met_criteria >= 5, "DSM-5 requires >= 5 symptoms for MDD"
        assert result.probability >= 0.5
        assert len(result.criteria_results) == len(mdd_criteria)

    def test_mdd_partial_case_low_probability(self, mdd_criteria, mdd_symptoms_partial):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, mdd_symptoms_partial)

        assert result.required_met is False, "Not all required symptoms present"
        assert result.duration_met is False, "Duration < 14 days"
        assert result.met_criteria <= 2, "Only 2 symptoms present"
        assert result.probability < 0.5

    def test_bipolar_positive_case(self, bipolar_criteria, bipolar_symptoms_positive):
        result = self.evaluator.evaluate_disorder(2, "Bipolar I", bipolar_criteria, bipolar_symptoms_positive)

        assert result.required_met, "Required manic symptoms should be met"
        assert result.probability > 0.5
        assert result.met_criteria >= 3, "≥3 manic symptoms required"

    def test_no_criteria_returns_zero_probability(self, mdd_symptoms_positive):
        result = self.evaluator.evaluate_disorder(99, "Unknown", [], mdd_symptoms_positive)

        assert result.total_criteria == 0
        assert result.probability == 0.0
        assert len(result.criteria_results) == 0

    def test_empty_observations_returns_zero(self, mdd_criteria):
        result = self.evaluator.evaluate_disorder(1, "MDD", mdd_criteria, [])

        assert result.required_met is False
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
