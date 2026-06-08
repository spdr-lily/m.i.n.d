import pytest
from app.ml.inference.bayesian_network import BayesianNetwork, InferenceEvidence, BayesianInferenceResult
from app.ml.models.network_definition import build_mood_disorder_network


class TestBayesianNetworkStructure:
    def test_network_has_disorder_nodes(self):
        bn = build_mood_disorder_network()
        expected_disorders = [
            "Major Depressive Disorder",
            "Bipolar I Disorder",
            "Bipolar II Disorder",
            "Generalized Anxiety Disorder",
            "Panic Disorder",
            "Post-Traumatic Stress Disorder",
            "Persistent Depressive Disorder",
            "Social Anxiety Disorder",
            "Obsessive-Compulsive Disorder",
        ]
        for d in expected_disorders:
            assert d in bn.nodes, f"Missing disorder node: {d}"

    def test_network_has_symptom_nodes(self):
        bn = build_mood_disorder_network()
        assert len(bn.symptom_list) >= 10, f"Too few symptoms: {len(bn.symptom_list)}"

    def test_all_symptoms_have_parents(self):
        bn = build_mood_disorder_network()
        errors = bn.validate_network()
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_priors_sum_less_than_one(self):
        bn = build_mood_disorder_network()
        total_prior = sum(bn.get_prior(d) for d in bn.disorder_list)
        assert total_prior < 1.0, f"Total prior {total_prior} >= 1.0 (comorbidity allowed)"


class TestBayesianInference:
    def test_posterior_higher_than_prior_with_supporting_evidence(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("loss_of_interest", present=True),
            InferenceEvidence("fatigue", present=True),
            InferenceEvidence("sleep_disturbance", present=True),
            InferenceEvidence("guilt_feelings", present=True),
        ]
        result = bn.compute_posterior("Major Depressive Disorder", evidence)
        assert result.posterior_probability > result.prior_probability

    def test_posterior_lower_with_contradicting_evidence(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=False),
            InferenceEvidence("loss_of_interest", present=False),
            InferenceEvidence("fatigue", present=False),
        ]
        result = bn.compute_posterior("Major Depressive Disorder", evidence)
        assert result.posterior_probability < result.prior_probability

    def test_mdd_depression_evidence_high_probability(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("loss_of_interest", present=True),
            InferenceEvidence("sleep_disturbance", present=True),
            InferenceEvidence("fatigue", present=True),
            InferenceEvidence("appetite_changes", present=True),
            InferenceEvidence("guilt_feelings", present=True),
            InferenceEvidence("concentration_problems", present=True),
            InferenceEvidence("psychomotor_changes", present=True),
            InferenceEvidence("suicidal_ideation", present=True),
        ]
        result = bn.compute_posterior("Major Depressive Disorder", evidence)
        assert result.posterior_probability > 0.7, f"Posterior too low: {result.posterior_probability}"

    def test_bipolar_manic_evidence_high_probability(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("euphoric_mood", present=True),
            InferenceEvidence("increased_energy", present=True),
            InferenceEvidence("grandiosity", present=True),
            InferenceEvidence("decreased_sleep", present=True),
            InferenceEvidence("rapid_speech", present=True),
            InferenceEvidence("racing_thoughts", present=True),
            InferenceEvidence("risk_behavior", present=True),
        ]
        result = bn.compute_posterior("Bipolar I Disorder", evidence)
        assert result.posterior_probability > 0.6

    def test_gad_worry_evidence(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("excessive_worry", present=True),
            InferenceEvidence("restlessness", present=True),
            InferenceEvidence("fatigue_gad", present=True),
            InferenceEvidence("muscle_tension", present=True),
            InferenceEvidence("sleep_disturbance_gad", present=True),
        ]
        result = bn.compute_posterior("Generalized Anxiety Disorder", evidence)
        assert result.posterior_probability > 0.3

    def test_panic_disorder_evidence(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("panic_attacks", present=True),
            InferenceEvidence("palpitations", present=True),
            InferenceEvidence("shortness_of_breath", present=True),
            InferenceEvidence("fear_of_dying", present=True),
        ]
        result = bn.compute_posterior("Panic Disorder", evidence)
        assert result.posterior_probability > 0.4

    def test_empty_evidence_returns_prior(self):
        bn = build_mood_disorder_network()
        result = bn.compute_posterior("Major Depressive Disorder", [])
        assert result.posterior_probability == pytest.approx(result.prior_probability, rel=0.01)

    def test_absent_symptom_reduces_posterior(self):
        bn = build_mood_disorder_network()
        evidence_absent = [
            InferenceEvidence("depressed_mood", present=False),
            InferenceEvidence("loss_of_interest", present=False),
        ]
        result = bn.compute_posterior("Major Depressive Disorder", evidence_absent)
        assert result.posterior_probability < result.prior_probability


class TestBayesianInfer:
    def test_infer_returns_top_k_results(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("loss_of_interest", present=True),
        ]
        results = bn.infer(evidence, top_k=3)
        assert len(results) == 3

    def test_mdd_ranks_highest_for_depression_symptoms(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("loss_of_interest", present=True),
            InferenceEvidence("sleep_disturbance", present=True),
            InferenceEvidence("fatigue", present=True),
            InferenceEvidence("guilt_feelings", present=True),
        ]
        results = bn.infer(evidence, top_k=5)
        assert results[0].disorder_name == "Major Depressive Disorder"

    def test_bipolar_ranks_highest_for_manic_symptoms(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("euphoric_mood", present=True),
            InferenceEvidence("increased_energy", present=True),
            InferenceEvidence("grandiosity", present=True),
            InferenceEvidence("decreased_sleep", present=True),
        ]
        results = bn.infer(evidence, top_k=5)
        assert results[0].disorder_name == "Bipolar I Disorder"

    def test_evidence_with_nonexistent_symptom_ignored(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("nonexistent_symptom", present=True),
        ]
        results = bn.infer(evidence, top_k=3)
        assert len(results) == 3


class TestBayesianExplanation:
    def test_explanation_contains_expected_fields(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
        ]
        explanation = bn.calculate_explanation("Major Depressive Disorder", evidence)
        assert "disorder" in explanation
        assert "prior" in explanation
        assert "posterior" in explanation
        assert "bayes_factor" in explanation
        assert "evidence_contributions" in explanation
        assert explanation["disorder"] == "Major Depressive Disorder"

    def test_explanation_symptoms_ordered_by_impact(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("loss_of_interest", present=True),
            InferenceEvidence("suicidal_ideation", present=True),
        ]
        explanation = bn.calculate_explanation("Major Depressive Disorder", evidence)
        impacts = [s["likelihood_ratio"] for s in explanation["evidence_contributions"]]
        assert impacts == sorted(impacts, reverse=True)

    def test_explanation_interpretation_high(self):
        bn = build_mood_disorder_network()
        evidence = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("loss_of_interest", present=True),
            InferenceEvidence("sleep_disturbance", present=True),
            InferenceEvidence("fatigue", present=True),
            InferenceEvidence("guilt_feelings", present=True),
        ]
        explanation = bn.calculate_explanation("Major Depressive Disorder", evidence)
        assert "Alta" in explanation["interpretation"] or "moderada" in explanation["interpretation"]


class TestBayesianInferenceResult:
    def test_result_fields_populated(self):
        result = BayesianInferenceResult(
            disorder_name="Test",
            prior_probability=0.05,
            posterior_probability=0.80,
            bayes_factor=16.0,
            odds_ratio=4.0,
        )
        assert result.disorder_name == "Test"
        assert result.posterior_probability == 0.80
        assert result.bayes_factor == 16.0
        assert result.prior_probability == 0.05


class TestNetworkEdgeCases:
    def test_network_cpt_values_in_range(self):
        bn = build_mood_disorder_network()
        for disorder in bn.disorder_list:
            for symptom, cpt in bn.cpts.get(disorder, {}).items():
                assert 0 <= cpt.disorder_present <= 1, f"{disorder}/{symptom} present={cpt.disorder_present}"
                assert 0 <= cpt.disorder_absent <= 1, f"{disorder}/{symptom} absent={cpt.disorder_absent}"

    def test_compute_all_posteriors_returns_all_disorders(self):
        bn = build_mood_disorder_network()
        evidence = [InferenceEvidence("depressed_mood", present=True)]
        posteriors = bn.compute_all_posteriors(evidence)
        assert len(posteriors) == len(bn.disorder_list)
        for d in bn.disorder_list:
            assert d in posteriors

    def test_no_evidence_all_prior(self):
        bn = build_mood_disorder_network()
        posteriors = bn.compute_all_posteriors([])
        for d in bn.disorder_list:
            prior = bn.get_prior(d)
            assert posteriors[d] == pytest.approx(prior, rel=0.01)
