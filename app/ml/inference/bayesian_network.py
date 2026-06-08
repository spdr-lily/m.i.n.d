import math
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


# ============================================================================
# Wilson confidence interval for a proportion
# ============================================================================

def wilson_interval(p: float, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score confidence interval for a binomial proportion."""
    if n == 0:
        return (p, p)
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (max(0.0, center - margin), min(1.0, center + margin))


# ============================================================================
# Core data structures
# ============================================================================

@dataclass
class BayesianNode:
    name: str
    node_type: str  # "disorder", "symptom", or "risk_factor"
    probability: float = 0.0  # prior for disorder, P(S) for symptom, P(RF) for risk factor
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class CPTEntry:
    disorder_present: float  # P(symptom/risk_factor | disorder=present)
    disorder_absent: float   # P(symptom/risk_factor | disorder=absent)


@dataclass
class ComorbidityEntry:
    prob_given_other: float   # P(target | source)
    prob_without_other: float # P(target | ¬source)


@dataclass
class InferenceEvidence:
    symptom_name: str
    present: bool
    intensity: Optional[float] = None
    evidence_type: str = "symptom"  # "symptom", "risk_factor"


@dataclass
class BayesianInferenceResult:
    disorder_name: str
    prior_probability: float
    posterior_probability: float
    bayes_factor: float
    odds_ratio: float
    confidence_interval_lower: float = 0.0
    confidence_interval_upper: float = 0.0
    evidence_count: int = 0
    sequential_updates: List[Dict] = field(default_factory=list)


# ============================================================================
# Bayesian Network
# ============================================================================

class BayesianNetwork:
    def __init__(self):
        self.nodes: Dict[str, BayesianNode] = {}
        self.cpts: Dict[str, Dict[str, CPTEntry]] = {}
        self.risk_factor_cpts: Dict[str, Dict[str, CPTEntry]] = {}
        self.comorbidity_links: Dict[str, Dict[str, ComorbidityEntry]] = {}
        self.disorder_list: List[str] = []
        self.symptom_list: List[str] = []
        self.risk_factor_list: List[str] = []

    # ---- Disorder nodes ----

    def add_disorder_node(self, name: str, prior_probability: float) -> BayesianNode:
        node = BayesianNode(name=name, node_type="disorder", probability=prior_probability)
        self.nodes[name] = node
        self.disorder_list.append(name)
        self.cpts[name] = {}
        self.risk_factor_cpts[name] = {}
        return node

    # ---- Symptom nodes ----

    def add_symptom_node(
        self,
        name: str,
        parents: List[str],
        prob_given_disorder: float,
        prob_given_no_disorder: float,
    ) -> BayesianNode:
        node = BayesianNode(name=name, node_type="symptom", parents=parents)
        self.nodes[name] = node
        self.symptom_list.append(name)
        for parent in parents:
            if parent not in self.disorder_list:
                raise ValueError(f"Parent {parent} is not a registered disorder node")
            self.cpts[parent][name] = CPTEntry(
                disorder_present=prob_given_disorder,
                disorder_absent=prob_given_no_disorder,
            )
            self.nodes[parent].children.append(name)
        return node

    # ---- Risk factor nodes ----

    def add_risk_factor_node(
        self,
        name: str,
        parents: List[str],
        prob_given_disorder: float,
        prob_given_no_disorder: float,
    ) -> BayesianNode:
        node = BayesianNode(name=name, node_type="risk_factor", parents=parents)
        self.nodes[name] = node
        self.risk_factor_list.append(name)
        for parent in parents:
            if parent not in self.disorder_list:
                raise ValueError(f"Parent {parent} is not a registered disorder node")
            self.risk_factor_cpts[parent][name] = CPTEntry(
                disorder_present=prob_given_disorder,
                disorder_absent=prob_given_no_disorder,
            )
            self.nodes[parent].children.append(name)
        return node

    # ---- Comorbidity links ----

    def add_comorbidity_link(
        self,
        source_disorder: str,
        target_disorder: str,
        prob_given_source: float,
        prob_without_source: float,
    ) -> None:
        if source_disorder not in self.disorder_list:
            raise ValueError(f"Source disorder {source_disorder} not registered")
        if target_disorder not in self.disorder_list:
            raise ValueError(f"Target disorder {target_disorder} not registered")
        if source_disorder not in self.comorbidity_links:
            self.comorbidity_links[source_disorder] = {}
        self.comorbidity_links[source_disorder][target_disorder] = ComorbidityEntry(
            prob_given_other=prob_given_source,
            prob_without_other=prob_without_source,
        )

    # ---- Accessors ----

    def get_prior(self, disorder_name: str) -> float:
        return self.nodes[disorder_name].probability

    def get_cpt(self, disorder_name: str, symptom_name: str) -> Optional[CPTEntry]:
        return self.cpts.get(disorder_name, {}).get(symptom_name)

    def get_risk_factor_cpt(self, disorder_name: str, risk_factor_name: str) -> Optional[CPTEntry]:
        return self.risk_factor_cpts.get(disorder_name, {}).get(risk_factor_name)

    def get_comorbidity(self, source: str, target: str) -> Optional[ComorbidityEntry]:
        return self.comorbidity_links.get(source, {}).get(target)

    # ---- Core posterior computation ----

    def compute_posterior(
        self,
        disorder_name: str,
        evidence: List[InferenceEvidence],
        apply_comorbidity: bool = False,
        all_results: Optional[Dict[str, 'BayesianInferenceResult']] = None,
    ) -> BayesianInferenceResult:
        prior = self.get_prior(disorder_name)
        prior_odds = prior / (1 - prior + 1e-10)

        log_p_given_d = 0.0
        log_p_given_nd = 0.0
        evidence_count = 0

        for ev in evidence:
            if ev.evidence_type == "risk_factor":
                cpt = self.get_risk_factor_cpt(disorder_name, ev.symptom_name)
            else:
                cpt = self.get_cpt(disorder_name, ev.symptom_name)
            if cpt is None:
                continue

            w = (ev.intensity / 100.0) if ev.intensity is not None else 1.0
            w = max(0.1, min(w, 1.0))
            if not ev.present:
                w = 1.0  # absence is binary

            if ev.present:
                p_d = cpt.disorder_present ** w
                p_nd = cpt.disorder_absent ** w
            else:
                p_d = (1 - cpt.disorder_present) ** w
                p_nd = (1 - cpt.disorder_absent) ** w

            p_d = max(p_d, 1e-10)
            p_nd = max(p_nd, 1e-10)

            log_p_given_d += math.log(p_d)
            log_p_given_nd += math.log(p_nd)
            evidence_count += 1

        log_bayes_factor = log_p_given_d - log_p_given_nd
        log_bayes_factor = max(min(log_bayes_factor, 100), -100)

        bayes_factor = math.exp(log_bayes_factor)
        posterior_odds = prior_odds * bayes_factor
        posterior = posterior_odds / (1 + posterior_odds)
        posterior = max(0.0, min(1.0, posterior))

        # Comorbidity adjustment
        if apply_comorbidity and all_results is not None:
            posterior = self._adjust_for_comorbidity(
                disorder_name, posterior, all_results
            )

        ci_lower, ci_upper = wilson_interval(posterior, max(evidence_count, 1))

        return BayesianInferenceResult(
            disorder_name=disorder_name,
            prior_probability=round(prior, 6),
            posterior_probability=round(posterior, 6),
            bayes_factor=round(bayes_factor, 4),
            odds_ratio=round(posterior_odds, 4),
            confidence_interval_lower=round(ci_lower, 4),
            confidence_interval_upper=round(ci_upper, 4),
            evidence_count=evidence_count,
        )

    def _adjust_for_comorbidity(
        self,
        disorder_name: str,
        posterior: float,
        all_results: Dict[str, 'BayesianInferenceResult'],
    ) -> float:
        for src_name, src_result in all_results.items():
            if src_name == disorder_name:
                continue
            entry = self.get_comorbidity(src_name, disorder_name)
            if entry is None:
                entry = self.get_comorbidity(disorder_name, src_name)
            if entry is None:
                continue

            src_posterior = src_result.posterior_probability
            if src_posterior < 0.3:
                continue

            boost = entry.prob_given_other * src_posterior * 0.15
            posterior = min(posterior + boost, 1.0)
        return posterior

    # ---- Sequential update ----

    def compute_posterior_sequential(
        self,
        disorder_name: str,
        evidence: List[InferenceEvidence],
    ) -> BayesianInferenceResult:
        updates = []
        current_prior = self.get_prior(disorder_name)

        for ev in evidence:
            single_ev = [ev]
            step_result = self._compute_step(disorder_name, single_ev, current_prior)
            updates.append({
                "evidence": ev.symptom_name,
                "evidence_type": ev.evidence_type,
                "present": ev.present,
                "intensity": ev.intensity,
                "prior": round(current_prior, 4),
                "posterior": round(step_result, 4),
                "likelihood_ratio": round(
                    step_result / (1 - step_result + 1e-10) /
                    (current_prior / (1 - current_prior + 1e-10) + 1e-10),
                    4,
                ),
            })
            current_prior = step_result

        final = self.compute_posterior(disorder_name, evidence)
        final.sequential_updates = updates
        return final

    def _compute_step(self, disorder_name: str, evidence: List[InferenceEvidence], prior: float) -> float:
        prior_odds = prior / (1 - prior + 1e-10)
        log_p_given_d = 0.0
        log_p_given_nd = 0.0

        for ev in evidence:
            cpt = self.get_cpt(disorder_name, ev.symptom_name)
            if cpt is None:
                cpt = self.get_risk_factor_cpt(disorder_name, ev.symptom_name)
            if cpt is None:
                continue

            w = (ev.intensity / 100.0) if ev.intensity is not None else 1.0
            w = max(0.1, min(w, 1.0))
            if not ev.present:
                w = 1.0

            if ev.present:
                p_d = cpt.disorder_present ** w
                p_nd = cpt.disorder_absent ** w
            else:
                p_d = (1 - cpt.disorder_present) ** w
                p_nd = (1 - cpt.disorder_absent) ** w

            p_d = max(p_d, 1e-10)
            p_nd = max(p_nd, 1e-10)
            log_p_given_d += math.log(p_d)
            log_p_given_nd += math.log(p_nd)

        log_bf = max(min(log_p_given_d - log_p_given_nd, 100), -100)
        posterior_odds = prior_odds * math.exp(log_bf)
        posterior = posterior_odds / (1 + posterior_odds)
        return max(0.0, min(1.0, posterior))

    # ---- Batch inference ----

    def infer(
        self,
        evidence: List[InferenceEvidence],
        top_k: int = 15,
        apply_comorbidity: bool = False,
    ) -> List[BayesianInferenceResult]:
        all_results: Dict[str, BayesianInferenceResult] = {}

        for disorder_name in self.disorder_list:
            result = self.compute_posterior(
                disorder_name, evidence,
                apply_comorbidity=False,
            )
            all_results[disorder_name] = result

        if apply_comorbidity:
            for disorder_name in self.disorder_list:
                adjusted = self._adjust_for_comorbidity(
                    disorder_name,
                    all_results[disorder_name].posterior_probability,
                    all_results,
                )
                all_results[disorder_name].posterior_probability = round(adjusted, 6)
                ci_l, ci_u = wilson_interval(
                    adjusted,
                    max(all_results[disorder_name].evidence_count, 1),
                )
                all_results[disorder_name].confidence_interval_lower = round(ci_l, 4)
                all_results[disorder_name].confidence_interval_upper = round(ci_u, 4)

        results = sorted(
            all_results.values(),
            key=lambda r: r.posterior_probability,
            reverse=True,
        )
        return results[:top_k]

    def compute_all_posteriors(
        self,
        evidence: List[InferenceEvidence],
        apply_comorbidity: bool = False,
    ) -> Dict[str, float]:
        results = self.infer(evidence, top_k=len(self.disorder_list), apply_comorbidity=apply_comorbidity)
        return {r.disorder_name: r.posterior_probability for r in results}

    # ---- Explanation ----

    def calculate_explanation(
        self,
        disorder_name: str,
        evidence: List[InferenceEvidence],
    ) -> Dict:
        result = self.compute_posterior_sequential(disorder_name, evidence)
        impacts = []
        for ev in evidence:
            if ev.evidence_type == "risk_factor":
                cpt = self.get_risk_factor_cpt(disorder_name, ev.symptom_name)
            else:
                cpt = self.get_cpt(disorder_name, ev.symptom_name)
            if cpt is None:
                continue
            w = (ev.intensity / 100.0) if ev.intensity is not None else 1.0
            if ev.present:
                contrib = (cpt.disorder_present ** w) / (cpt.disorder_absent ** w + 1e-10)
            else:
                contrib = ((1 - cpt.disorder_present) ** w) / ((1 - cpt.disorder_absent) ** w + 1e-10)
            impacts.append({
                "evidence": ev.symptom_name,
                "type": ev.evidence_type,
                "present": ev.present,
                "intensity": ev.intensity,
                "likelihood_ratio": round(contrib, 4),
            })
        impacts.sort(key=lambda x: x["likelihood_ratio"], reverse=True)

        comorbidity_effects = []
        for src in self.disorder_list:
            entry = self.get_comorbidity(src, disorder_name)
            if entry:
                comorbidity_effects.append({
                    "source": src,
                    "prob_given_source": entry.prob_given_other,
                    "prob_without_source": entry.prob_without_other,
                })

        return {
            "disorder": disorder_name,
            "prior": result.prior_probability,
            "posterior": result.posterior_probability,
            "bayes_factor": result.bayes_factor,
            "confidence_interval": {
                "lower": result.confidence_interval_lower,
                "upper": result.confidence_interval_upper,
            },
            "evidence_count": result.evidence_count,
            "sequential_updates": result.sequential_updates,
            "evidence_contributions": impacts,
            "comorbidity_effects": comorbidity_effects,
            "interpretation": self._interpret_result(result),
        }

    def _interpret_result(self, result: BayesianInferenceResult) -> str:
        pct = result.posterior_probability * 100
        lo = result.confidence_interval_lower * 100
        hi = result.confidence_interval_upper * 100
        if result.posterior_probability >= 0.8:
            return f"Probabilidade: {pct:.0f}% (IC {lo:.0f}%-{hi:.0f}%) — Alta probabilidade clinica, fortemente sugestivo do diagnostico"
        elif result.posterior_probability >= 0.5:
            return f"Probabilidade: {pct:.0f}% (IC {lo:.0f}%-{hi:.0f}%) — Probabilidade moderada, considerar como diagnostico diferencial"
        elif result.posterior_probability >= 0.2:
            return f"Probabilidade: {pct:.0f}% (IC {lo:.0f}%-{hi:.0f}%) — Baixa probabilidade, improvavel mas nao excluido"
        else:
            return f"Probabilidade: {pct:.0f}% (IC {lo:.0f}%-{hi:.0f}%) — Probabilidade muito baixa, diagnostico improvavel"

    # ---- Validation ----

    def validate_network(self) -> List[str]:
        errors = []
        for disorder in self.disorder_list:
            if disorder not in self.nodes:
                errors.append(f"Disorder node '{disorder}' not registered")
                continue
            prior = self.nodes[disorder].probability
            if not (0 < prior < 1):
                errors.append(f"Disorder '{disorder}' prior {prior} outside (0,1)")
        for symptom in self.symptom_list:
            if symptom not in self.nodes:
                errors.append(f"Symptom node '{symptom}' not registered")
                continue
            if not self.nodes[symptom].parents:
                errors.append(f"Symptom '{symptom}' has no parent disorder")
        for rf in self.risk_factor_list:
            if rf not in self.nodes:
                errors.append(f"Risk factor node '{rf}' not registered")
                continue
            if not self.nodes[rf].parents:
                errors.append(f"Risk factor '{rf}' has no parent disorder")
        for src in self.comorbidity_links:
            if src not in self.disorder_list:
                errors.append(f"Comorbidity source '{src}' not a registered disorder")
            for tgt in self.comorbidity_links[src]:
                if tgt not in self.disorder_list:
                    errors.append(f"Comorbidity target '{tgt}' not a registered disorder")
        return errors
