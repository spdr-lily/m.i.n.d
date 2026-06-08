"""
Network topology definition for the Bayesian Network.

References:
- DSM-5-TR diagnostic criteria for MDD, Bipolar, GAD, Panic, PTSD
- Kessler et al. (2005) — NCS-R prevalence estimates
- Andrews et al. (2018) — symptom-level conditional probabilities
- Kendler et al. (2021) — risk factor epidemiological data
- Kessler et al. (2015) — comorbidity patterns in mental disorders
"""

from app.ml.inference.bayesian_network import BayesianNetwork, InferenceEvidence, BayesianInferenceResult


def build_mood_disorder_network() -> BayesianNetwork:
    """
    Build a Bayesian Network for mood and anxiety disorders.

    Topology:
      Disorder nodes (priors) → Symptom nodes (P(S|D), P(S|¬D))
      Disorder nodes → Risk Factor nodes (P(RF|D), P(RF|¬D))
      Comorbidity links between disorder nodes P(D2|D1)

    Conditional probabilities derived from clinical literature and DSM-5-TR criteria.
    """
    bn = BayesianNetwork()

    # =========================================================================
    # DISORDER NODES (priors = epidemiological prevalence)
    # =========================================================================
    # Sources: Kessler et al. (2005) NCS-R, WHO World Mental Health Surveys

    bn.add_disorder_node("Major Depressive Disorder", prior_probability=0.052)
    bn.add_disorder_node("Bipolar I Disorder", prior_probability=0.010)
    bn.add_disorder_node("Bipolar II Disorder", prior_probability=0.003)
    bn.add_disorder_node("Generalized Anxiety Disorder", prior_probability=0.031)
    bn.add_disorder_node("Panic Disorder", prior_probability=0.022)
    bn.add_disorder_node("Post-Traumatic Stress Disorder", prior_probability=0.037)
    bn.add_disorder_node("Persistent Depressive Disorder", prior_probability=0.020)
    bn.add_disorder_node("Social Anxiety Disorder", prior_probability=0.070)
    bn.add_disorder_node("Obsessive-Compulsive Disorder", prior_probability=0.012)

    # =========================================================================
    # RISK FACTOR NODES
    # =========================================================================
    # Sources: Kendler et al. (2021), WHO World Mental Health Surveys
    # P(RF|D) and P(RF|¬D) for each disorder-risk factor pair
    # Shared risk factors (family history, trauma, stress) apply across disorders

    bn.add_risk_factor_node("family_history_mdd", ["Major Depressive Disorder"],
                            prob_given_disorder=0.35, prob_given_no_disorder=0.08)
    bn.add_risk_factor_node("family_history_bipolar", ["Bipolar I Disorder", "Bipolar II Disorder"],
                            prob_given_disorder=0.40, prob_given_no_disorder=0.05)
    bn.add_risk_factor_node("childhood_trauma", ["Major Depressive Disorder", "Post-Traumatic Stress Disorder"],
                            prob_given_disorder=0.45, prob_given_no_disorder=0.12)
    bn.add_risk_factor_node("chronic_stress", ["Generalized Anxiety Disorder", "Major Depressive Disorder"],
                            prob_given_disorder=0.55, prob_given_no_disorder=0.18)
    bn.add_risk_factor_node("substance_use", ["Bipolar I Disorder", "Major Depressive Disorder"],
                            prob_given_disorder=0.30, prob_given_no_disorder=0.08)
    bn.add_risk_factor_node("social_isolation", ["Social Anxiety Disorder", "Major Depressive Disorder"],
                            prob_given_disorder=0.40, prob_given_no_disorder=0.10)
    bn.add_risk_factor_node("recent_loss", ["Major Depressive Disorder", "Persistent Depressive Disorder"],
                            prob_given_disorder=0.50, prob_given_no_disorder=0.15)
    bn.add_risk_factor_node("physical_illness", ["Major Depressive Disorder", "Generalized Anxiety Disorder"],
                            prob_given_disorder=0.25, prob_given_no_disorder=0.10)

    # =========================================================================
    # COMORBIDITY LINKS
    # =========================================================================
    # Sources: Kessler et al. (2005, 2015) NCS-R comorbidity patterns
    # P(Target | Source) — conditional probability of target disorder given source

    bn.add_comorbidity_link("Major Depressive Disorder", "Generalized Anxiety Disorder",
                            prob_given_source=0.55, prob_without_source=0.15)
    bn.add_comorbidity_link("Generalized Anxiety Disorder", "Major Depressive Disorder",
                            prob_given_source=0.60, prob_without_source=0.12)
    bn.add_comorbidity_link("Major Depressive Disorder", "Panic Disorder",
                            prob_given_source=0.30, prob_without_source=0.08)
    bn.add_comorbidity_link("Panic Disorder", "Major Depressive Disorder",
                            prob_given_source=0.45, prob_without_source=0.10)
    bn.add_comorbidity_link("Major Depressive Disorder", "Persistent Depressive Disorder",
                            prob_given_source=0.25, prob_without_source=0.05)
    bn.add_comorbidity_link("Post-Traumatic Stress Disorder", "Major Depressive Disorder",
                            prob_given_source=0.50, prob_without_source=0.10)
    bn.add_comorbidity_link("Major Depressive Disorder", "Post-Traumatic Stress Disorder",
                            prob_given_source=0.20, prob_without_source=0.05)
    bn.add_comorbidity_link("Generalized Anxiety Disorder", "Panic Disorder",
                            prob_given_source=0.25, prob_without_source=0.06)
    bn.add_comorbidity_link("Social Anxiety Disorder", "Major Depressive Disorder",
                            prob_given_source=0.40, prob_without_source=0.10)
    bn.add_comorbidity_link("Bipolar I Disorder", "Generalized Anxiety Disorder",
                            prob_given_source=0.35, prob_without_source=0.10)
    bn.add_comorbidity_link("Obsessive-Compulsive Disorder", "Major Depressive Disorder",
                            prob_given_source=0.40, prob_without_source=0.10)

    # =========================================================================
    # MDD SYMPTOMS (DSM-5-TR: Criterion A — >=5 symptoms, >=2 weeks)
    # =========================================================================
    # P(S|MDD) derived from DSM-5-TR field trials; P(S|¬MDD) from general population base rates

    bn.add_symptom_node("depressed_mood", ["Major Depressive Disorder"],
                        prob_given_disorder=0.90, prob_given_no_disorder=0.05)
    bn.add_symptom_node("loss_of_interest", ["Major Depressive Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.04)
    bn.add_symptom_node("sleep_disturbance", ["Major Depressive Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.10)
    bn.add_symptom_node("fatigue", ["Major Depressive Disorder"],
                        prob_given_disorder=0.80, prob_given_no_disorder=0.08)
    bn.add_symptom_node("appetite_changes", ["Major Depressive Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.05)
    bn.add_symptom_node("guilt_feelings", ["Major Depressive Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.03)
    bn.add_symptom_node("concentration_problems", ["Major Depressive Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.06)
    bn.add_symptom_node("psychomotor_changes", ["Major Depressive Disorder"],
                        prob_given_disorder=0.50, prob_given_no_disorder=0.04)
    bn.add_symptom_node("suicidal_ideation", ["Major Depressive Disorder"],
                        prob_given_disorder=0.40, prob_given_no_disorder=0.01)

    # =========================================================================
    # BIPOLAR I SYMPTOMS (DSM-5-TR: manic episode — elevated mood + >=3 symptoms, >=1 week)
    # =========================================================================
    bn.add_symptom_node("euphoric_mood", ["Bipolar I Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.02)
    bn.add_symptom_node("increased_energy", ["Bipolar I Disorder"],
                        prob_given_disorder=0.80, prob_given_no_disorder=0.03)
    bn.add_symptom_node("grandiosity", ["Bipolar I Disorder"],
                        prob_given_disorder=0.60, prob_given_no_disorder=0.01)
    bn.add_symptom_node("decreased_sleep", ["Bipolar I Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.05)
    bn.add_symptom_node("rapid_speech", ["Bipolar I Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.02)
    bn.add_symptom_node("racing_thoughts", ["Bipolar I Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.03)
    bn.add_symptom_node("distractibility", ["Bipolar I Disorder"],
                        prob_given_disorder=0.60, prob_given_no_disorder=0.04)
    bn.add_symptom_node("risk_behavior", ["Bipolar I Disorder"],
                        prob_given_disorder=0.55, prob_given_no_disorder=0.02)

    # =========================================================================
    # BIPOLAR II SYMPTOMS (DSM-5-TR: hypomanic + depressive episodes)
    # =========================================================================
    bn.add_symptom_node("hypomanic_mood", ["Bipolar II Disorder"],
                        prob_given_disorder=0.80, prob_given_no_disorder=0.04)
    bn.add_symptom_node("mildly_increased_energy", ["Bipolar II Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.05)
    bn.add_symptom_node("reduced_sleep_hypomania", ["Bipolar II Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.06)
    bn.add_symptom_node("bipolar_depressed_mood", ["Bipolar II Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.05)
    bn.add_symptom_node("bipolar_loss_of_interest", ["Bipolar II Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.04)

    # =========================================================================
    # GAD SYMPTOMS (DSM-5-TR: excessive worry >=6 months + >=3 symptoms)
    # =========================================================================
    bn.add_symptom_node("excessive_worry", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.92, prob_given_no_disorder=0.08)
    bn.add_symptom_node("restlessness", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.05)
    bn.add_symptom_node("fatigue_gad", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.06)
    bn.add_symptom_node("muscle_tension", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.60, prob_given_no_disorder=0.04)
    bn.add_symptom_node("sleep_disturbance_gad", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.08)
    bn.add_symptom_node("irritability", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.05)
    bn.add_symptom_node("concentration_difficulty_gad", ["Generalized Anxiety Disorder"],
                        prob_given_disorder=0.60, prob_given_no_disorder=0.05)

    # =========================================================================
    # PANIC DISORDER SYMPTOMS (DSM-5-TR: recurrent unexpected panic attacks)
    # =========================================================================
    bn.add_symptom_node("panic_attacks", ["Panic Disorder"],
                        prob_given_disorder=0.95, prob_given_no_disorder=0.03)
    bn.add_symptom_node("palpitations", ["Panic Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.04)
    bn.add_symptom_node("chest_pain", ["Panic Disorder"],
                        prob_given_disorder=0.55, prob_given_no_disorder=0.02)
    bn.add_symptom_node("shortness_of_breath", ["Panic Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.03)
    bn.add_symptom_node("fear_of_dying", ["Panic Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.01)
    bn.add_symptom_node("derealization", ["Panic Disorder"],
                        prob_given_disorder=0.50, prob_given_no_disorder=0.02)
    bn.add_symptom_node("avoidance_behavior", ["Panic Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.04)

    # =========================================================================
    # PTSD SYMPTOMS (DSM-5-TR: exposure + intrusion + avoidance + cognition/mood + arousal)
    # =========================================================================
    bn.add_symptom_node("traumatic_exposure", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=1.00, prob_given_no_disorder=0.30)
    bn.add_symptom_node("intrusive_memories", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.02)
    bn.add_symptom_node("nightmares", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.03)
    bn.add_symptom_node("hypervigilance", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.04)
    bn.add_symptom_node("avoidance_ptsd", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=0.80, prob_given_no_disorder=0.03)
    bn.add_symptom_node("negative_cognitions", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=0.65, prob_given_no_disorder=0.05)
    bn.add_symptom_node("startle_response", ["Post-Traumatic Stress Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.04)

    # =========================================================================
    # PERSISTENT DEPRESSIVE DISORDER (Dysthymia — chronic >=2 years, fewer symptoms than MDD)
    # =========================================================================
    bn.add_symptom_node("chronic_low_mood", ["Persistent Depressive Disorder"],
                        prob_given_disorder=0.90, prob_given_no_disorder=0.04)
    bn.add_symptom_node("poor_appetite_dysthymia", ["Persistent Depressive Disorder"],
                        prob_given_disorder=0.55, prob_given_no_disorder=0.04)
    bn.add_symptom_node("low_self_esteem", ["Persistent Depressive Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.05)
    bn.add_symptom_node("hopelessness", ["Persistent Depressive Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.04)
    bn.add_symptom_node("low_energy_dysthymia", ["Persistent Depressive Disorder"],
                        prob_given_disorder=0.70, prob_given_no_disorder=0.06)

    # =========================================================================
    # SOCIAL ANXIETY DISORDER (DSM-5-TR: marked fear of social situations >=6 months)
    # =========================================================================
    bn.add_symptom_node("social_fear", ["Social Anxiety Disorder"],
                        prob_given_disorder=0.92, prob_given_no_disorder=0.06)
    bn.add_symptom_node("avoidance_social", ["Social Anxiety Disorder"],
                        prob_given_disorder=0.80, prob_given_no_disorder=0.04)
    bn.add_symptom_node("performance_anxiety", ["Social Anxiety Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.05)
    bn.add_symptom_node("blushing", ["Social Anxiety Disorder"],
                        prob_given_disorder=0.60, prob_given_no_disorder=0.03)

    # =========================================================================
    # OCD SYMPTOMS (DSM-5-TR: obsessions and/or compulsions, time-consuming)
    # =========================================================================
    bn.add_symptom_node("obsessions", ["Obsessive-Compulsive Disorder"],
                        prob_given_disorder=0.90, prob_given_no_disorder=0.02)
    bn.add_symptom_node("compulsions", ["Obsessive-Compulsive Disorder"],
                        prob_given_disorder=0.85, prob_given_no_disorder=0.02)
    bn.add_symptom_node("repetitive_behavior", ["Obsessive-Compulsive Disorder"],
                        prob_given_disorder=0.80, prob_given_no_disorder=0.03)
    bn.add_symptom_node("intrusive_thoughts", ["Obsessive-Compulsive Disorder"],
                        prob_given_disorder=0.75, prob_given_no_disorder=0.04)

    errors = bn.validate_network()
    if errors:
        raise ValueError(f"Network validation errors: {errors}")

    return bn
