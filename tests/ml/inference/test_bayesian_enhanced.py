from math import isclose
from app.ml.inference.bayesian_network import (
    BayesianNetwork,
    InferenceEvidence,
    BayesianInferenceResult,
    wilson_interval,
)


class TestWilsonInterval:

    def test_wilson_interval_50pct_10samples(self):
        lo, hi = wilson_interval(0.5, 10)
        assert lo < 0.5 < hi
        assert isclose(lo, 0.2366, abs_tol=0.01)
        assert isclose(hi, 0.7634, abs_tol=0.01)

    def test_wilson_interval_82pct_24samples(self):
        lo, hi = wilson_interval(0.82, 24)
        assert lo < 0.82 < hi
        assert lo > 0.60
        assert hi > 0.90
        assert isclose(lo, 0.6265, abs_tol=0.01)
        assert isclose(hi, 0.9252, abs_tol=0.01)

    def test_wilson_interval_0_evidence(self):
        lo, hi = wilson_interval(0.5, 0)
        assert lo == 0.5
        assert hi == 0.5

    def test_wilson_interval_always_in_01(self):
        for p in [0.0, 0.001, 0.5, 0.999, 1.0]:
            lo, hi = wilson_interval(p, 10)
            assert 0.0 <= lo <= hi <= 1.0


class TestRiskFactors:

    def test_simple_network_with_risk_factors(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_risk_factor_node("family_history", ["MDD"],
                                prob_given_disorder=0.35, prob_given_no_disorder=0.08)
        assert "family_history" in bn.risk_factor_list
        assert "family_history" in bn.nodes

    def test_risk_factor_boosts_posterior(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_risk_factor_node("family_history", ["MDD"],
                                prob_given_disorder=0.35, prob_given_no_disorder=0.08)

        ev_symptom = [InferenceEvidence("depressed_mood", present=True)]
        ev_both = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("family_history", present=True, evidence_type="risk_factor"),
        ]

        r1 = bn.compute_posterior("MDD", ev_symptom)
        r2 = bn.compute_posterior("MDD", ev_both)
        assert r2.posterior_probability > r1.posterior_probability

    def test_risk_factor_evidence_type_detected(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_risk_factor_node("stress", ["MDD"],
                                prob_given_disorder=0.55, prob_given_no_disorder=0.18)

        ev = [InferenceEvidence("stress", present=True, evidence_type="risk_factor")]
        r = bn.compute_posterior("MDD", ev)
        assert r.posterior_probability > 0.05

    def test_missing_risk_factor_cpt_ignored(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_risk_factor_node("stress", ["MDD"],
                                prob_given_disorder=0.55, prob_given_no_disorder=0.18)

        ev = [InferenceEvidence("nonexistent", present=True, evidence_type="risk_factor")]
        r = bn.compute_posterior("MDD", ev)
        assert isclose(r.posterior_probability, 0.05, abs_tol=0.001)

    def test_risk_factor_validated(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_risk_factor_node("stress", ["MDD"],
                                prob_given_disorder=0.55, prob_given_no_disorder=0.18)
        errors = bn.validate_network()
        assert len(errors) == 0


class TestComorbidityLinks:

    def test_simple_network_with_comorbidity(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_disorder_node("GAD", prior_probability=0.03)
        bn.add_comorbidity_link("MDD", "GAD",
                                prob_given_source=0.55, prob_without_source=0.15)
        assert "MDD" in bn.comorbidity_links
        assert "GAD" in bn.comorbidity_links["MDD"]

    def test_comorbidity_boosts_target_when_source_high(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_disorder_node("GAD", prior_probability=0.03)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_comorbidity_link("MDD", "GAD",
                                prob_given_source=0.55, prob_without_source=0.15)

        ev = [InferenceEvidence("depressed_mood", present=True)]

        r_no_com = bn.infer(ev, top_k=2, apply_comorbidity=False)
        r_yes_com = bn.infer(ev, top_k=2, apply_comorbidity=True)

        mdd_no = next(r for r in r_no_com if r.disorder_name == "MDD")
        gad_no = next(r for r in r_no_com if r.disorder_name == "GAD")
        mdd_yes = next(r for r in r_yes_com if r.disorder_name == "MDD")
        gad_yes = next(r for r in r_yes_com if r.disorder_name == "GAD")

        assert mdd_yes.posterior_probability == mdd_no.posterior_probability
        assert gad_yes.posterior_probability > gad_no.posterior_probability

    def test_comorbidity_validated(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_disorder_node("GAD", prior_probability=0.03)
        bn.add_comorbidity_link("MDD", "GAD",
                                prob_given_source=0.55, prob_without_source=0.15)
        errors = bn.validate_network()
        assert len(errors) == 0

    def test_comorbidity_in_explanation(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_disorder_node("GAD", prior_probability=0.03)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_comorbidity_link("MDD", "GAD",
                                prob_given_source=0.55, prob_without_source=0.15)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        expl = bn.calculate_explanation("GAD", ev)
        assert len(expl["comorbidity_effects"]) == 1
        assert expl["comorbidity_effects"][0]["source"] == "MDD"
        assert expl["comorbidity_effects"][0]["prob_given_source"] == 0.55


class TestConfidenceInterval:

    def test_result_contains_ci_fields(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        r = bn.compute_posterior("MDD", ev)
        assert hasattr(r, "confidence_interval_lower")
        assert hasattr(r, "confidence_interval_upper")
        assert r.confidence_interval_lower < r.posterior_probability < r.confidence_interval_upper

    def test_ci_narrows_with_more_evidence(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_symptom_node("fatigue", ["MDD"],
                            prob_given_disorder=0.80, prob_given_no_disorder=0.08)
        bn.add_symptom_node("sleep_disturbance", ["MDD"],
                            prob_given_disorder=0.75, prob_given_no_disorder=0.10)

        r1 = bn.compute_posterior("MDD", [InferenceEvidence("depressed_mood", present=True)])
        r3 = bn.compute_posterior("MDD", [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("fatigue", present=True),
            InferenceEvidence("sleep_disturbance", present=True),
        ])
        ci_width_1 = r1.confidence_interval_upper - r1.confidence_interval_lower
        ci_width_3 = r3.confidence_interval_upper - r3.confidence_interval_lower
        assert ci_width_3 < ci_width_1

    def test_ci_in_explanation(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        expl = bn.calculate_explanation("MDD", ev)
        assert "confidence_interval" in expl
        assert "lower" in expl["confidence_interval"]
        assert "upper" in expl["confidence_interval"]

    def test_interpretation_includes_ci(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        r = bn.compute_posterior("MDD", ev)
        text = bn._interpret_result(r)
        assert "Probabilidade" in text
        assert "IC" in text
        assert "%" in text


class TestSequentialUpdate:

    def test_sequential_returns_steps(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_symptom_node("fatigue", ["MDD"],
                            prob_given_disorder=0.80, prob_given_no_disorder=0.08)

        ev = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("fatigue", present=True),
        ]
        r = bn.compute_posterior_sequential("MDD", ev)
        assert len(r.sequential_updates) == 2
        assert r.sequential_updates[0]["evidence"] == "depressed_mood"
        assert r.sequential_updates[1]["evidence"] == "fatigue"
        assert r.sequential_updates[0]["posterior"] > r.sequential_updates[0]["prior"]
        assert r.sequential_updates[1]["prior"] == r.sequential_updates[0]["posterior"]

    def test_sequential_final_matches_full(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_symptom_node("fatigue", ["MDD"],
                            prob_given_disorder=0.80, prob_given_no_disorder=0.08)

        ev = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("fatigue", present=True),
        ]
        r_seq = bn.compute_posterior_sequential("MDD", ev)
        r_full = bn.compute_posterior("MDD", ev)
        assert isclose(r_seq.posterior_probability, r_full.posterior_probability, abs_tol=0.001)

    def test_sequential_with_risk_factor(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_risk_factor_node("family_history", ["MDD"],
                                prob_given_disorder=0.35, prob_given_no_disorder=0.08)

        ev = [
            InferenceEvidence("depressed_mood", present=True),
            InferenceEvidence("family_history", present=True, evidence_type="risk_factor"),
        ]
        r = bn.compute_posterior_sequential("MDD", ev)
        assert len(r.sequential_updates) == 2
        assert r.sequential_updates[1]["evidence_type"] == "risk_factor"

    def test_sequential_likelihood_ratios(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        r = bn.compute_posterior_sequential("MDD", ev)
        assert len(r.sequential_updates) == 1
        assert r.sequential_updates[0]["likelihood_ratio"] > 1.0


class TestInferWithComorbidity:

    def test_infer_default_no_comorbidity(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_disorder_node("GAD", prior_probability=0.03)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_comorbidity_link("MDD", "GAD",
                                prob_given_source=0.55, prob_without_source=0.15)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        results = bn.infer(ev, top_k=2)
        gad = next(r for r in results if r.disorder_name == "GAD")
        mdd = next(r for r in results if r.disorder_name == "MDD")
        assert isclose(gad.posterior_probability, 0.03, abs_tol=0.001)
        assert mdd.posterior_probability > 0.03

    def test_compute_all_posteriors_with_comorbidity(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_disorder_node("GAD", prior_probability=0.03)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        bn.add_comorbidity_link("MDD", "GAD",
                                prob_given_source=0.55, prob_without_source=0.15)

        ev = [InferenceEvidence("depressed_mood", present=True)]
        posteriors = bn.compute_all_posteriors(ev, apply_comorbidity=True)
        assert posteriors["GAD"] > 0.03
        assert posteriors["MDD"] > posteriors["GAD"]
        assert len(posteriors) == 2


class TestFullNetworkIntegration:

    def test_network_builds_with_all_features(self):
        from app.ml.models.network_definition import build_mood_disorder_network
        bn = build_mood_disorder_network()
        assert len(bn.disorder_list) == 9
        assert len(bn.symptom_list) == 56
        assert len(bn.risk_factor_list) == 8
        assert len(bn.comorbidity_links) == 7
        errors = bn.validate_network()
        assert len(errors) == 0

    def test_multiple_symptoms_with_comorbidity(self):
        from app.ml.models.network_definition import build_mood_disorder_network
        bn = build_mood_disorder_network()
        ev = [
            InferenceEvidence("depressed_mood", present=True, intensity=80),
            InferenceEvidence("loss_of_interest", present=True, intensity=70),
            InferenceEvidence("excessive_worry", present=True, intensity=85),
            InferenceEvidence("restlessness", present=True, intensity=60),
        ]
        results = bn.infer(ev, top_k=3, apply_comorbidity=True)
        names = [r.disorder_name for r in results]
        assert "Major Depressive Disorder" in names
        assert "Generalized Anxiety Disorder" in names
        assert results[0].posterior_probability > 0.5

    def test_risk_factors_in_full_network(self):
        from app.ml.models.network_definition import build_mood_disorder_network
        bn = build_mood_disorder_network()
        ev = [
            InferenceEvidence("depressed_mood", present=True, intensity=80),
            InferenceEvidence("loss_of_interest", present=True, intensity=70),
            InferenceEvidence("family_history_mdd", present=True, evidence_type="risk_factor"),
            InferenceEvidence("chronic_stress", present=True, evidence_type="risk_factor"),
        ]
        r = bn.compute_posterior("Major Depressive Disorder", ev)
        assert r.posterior_probability > 0.5
        assert r.confidence_interval_upper > r.posterior_probability
        assert r.evidence_count == 4

    def test_explanation_includes_all_new_fields(self):
        from app.ml.models.network_definition import build_mood_disorder_network
        bn = build_mood_disorder_network()
        ev = [
            InferenceEvidence("depressed_mood", present=True, intensity=80),
            InferenceEvidence("family_history_mdd", present=True, evidence_type="risk_factor"),
        ]
        expl = bn.calculate_explanation("Major Depressive Disorder", ev)
        assert "confidence_interval" in expl
        assert "sequential_updates" in expl
        assert "evidence_contributions" in expl
        assert "comorbidity_effects" in expl
        assert len(expl["sequential_updates"]) == 2
        assert expl["sequential_updates"][0]["evidence_type"] == "symptom"
        assert expl["sequential_updates"][1]["evidence_type"] == "risk_factor"


class TestEdgeCases:

    def test_absent_evidence_risk_factor(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_risk_factor_node("family_history", ["MDD"],
                                prob_given_disorder=0.35, prob_given_no_disorder=0.08)
        ev_present = [InferenceEvidence("family_history", present=True, evidence_type="risk_factor")]
        ev_absent = [InferenceEvidence("family_history", present=False, evidence_type="risk_factor")]
        r_present = bn.compute_posterior("MDD", ev_present)
        r_absent = bn.compute_posterior("MDD", ev_absent)
        assert r_present.posterior_probability > r_absent.posterior_probability

    def test_zero_intensity_handled(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.90, prob_given_no_disorder=0.05)
        ev = [InferenceEvidence("depressed_mood", present=True, intensity=0)]
        r = bn.compute_posterior("MDD", ev)
        assert r.posterior_probability > 0.05

    def test_high_intensity_saturates(self):
        bn = BayesianNetwork()
        bn.add_disorder_node("MDD", prior_probability=0.05)
        bn.add_symptom_node("depressed_mood", ["MDD"],
                            prob_given_disorder=0.50, prob_given_no_disorder=0.10)
        r_low = bn.compute_posterior("MDD", [InferenceEvidence("depressed_mood", present=True, intensity=10)])
        r_high = bn.compute_posterior("MDD", [InferenceEvidence("depressed_mood", present=True, intensity=100)])
        assert r_high.posterior_probability >= r_low.posterior_probability
