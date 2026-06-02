import math
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class BayesianNode:
    name: str
    node_type: str  # "disorder" or "symptom"
    probability: float = 0.0  # prior for disorder, P(S) for symptom
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class CPTEntry:
    disorder_present: float  # P(symptom | disorder=present)
    disorder_absent: float   # P(symptom | disorder=absent)


@dataclass
class InferenceEvidence:
    symptom_name: str
    present: bool
    intensity: Optional[float] = None


@dataclass
class BayesianInferenceResult:
    disorder_name: str
    prior_probability: float
    posterior_probability: float
    bayes_factor: float
    odds_ratio: float


class BayesianNetwork:
    def __init__(self):
        self.nodes: Dict[str, BayesianNode] = {}
        self.cpts: Dict[str, Dict[str, CPTEntry]] = {}
        self.disorder_list: List[str] = []
        self.symptom_list: List[str] = []

    def add_disorder_node(self, name: str, prior_probability: float) -> BayesianNode:
        node = BayesianNode(name=name, node_type="disorder", probability=prior_probability)
        self.nodes[name] = node
        self.disorder_list.append(name)
        self.cpts[name] = {}
        return node

    def add_symptom_node(
        self,
        name: str,
        parents: List[str],
        prob_given_disorder: float,
        prob_given_no_disorder: float,
    ) -> BayesianNode:
        node = BayesianNode(
            name=name,
            node_type="symptom",
            parents=parents,
        )
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

    def get_prior(self, disorder_name: str) -> float:
        return self.nodes[disorder_name].probability

    def get_cpt(self, disorder_name: str, symptom_name: str) -> Optional[CPTEntry]:
        return self.cpts.get(disorder_name, {}).get(symptom_name)

    def compute_posterior(
        self,
        disorder_name: str,
        evidence: List[InferenceEvidence],
    ) -> BayesianInferenceResult:
        prior = self.get_prior(disorder_name)
        prior_odds = prior / (1 - prior + 1e-10)

        log_p_given_d = 0.0
        log_p_given_nd = 0.0

        for ev in evidence:
            cpt = self.get_cpt(disorder_name, ev.symptom_name)
            if cpt is None:
                continue

            w = (ev.intensity / 100.0) if ev.intensity is not None else 1.0
            w = max(0.1, min(w, 1.0))

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

        log_bayes_factor = log_p_given_d - log_p_given_nd
        log_bayes_factor = max(min(log_bayes_factor, 100), -100)

        bayes_factor = math.exp(log_bayes_factor)
        posterior_odds = prior_odds * bayes_factor
        posterior = posterior_odds / (1 + posterior_odds)
        posterior = max(0.0, min(1.0, posterior))

        return BayesianInferenceResult(
            disorder_name=disorder_name,
            prior_probability=round(prior, 6),
            posterior_probability=round(posterior, 6),
            bayes_factor=round(bayes_factor, 4),
            odds_ratio=round(posterior_odds, 4),
        )

    def infer(
        self,
        evidence: List[InferenceEvidence],
        top_k: int = 15,
    ) -> List[BayesianInferenceResult]:
        results = []
        for disorder_name in self.disorder_list:
            result = self.compute_posterior(disorder_name, evidence)
            results.append(result)

        results.sort(key=lambda r: r.posterior_probability, reverse=True)
        return results[:top_k]

    def compute_all_posteriors(
        self,
        evidence: List[InferenceEvidence],
    ) -> Dict[str, float]:
        results = {}
        for disorder_name in self.disorder_list:
            result = self.compute_posterior(disorder_name, evidence)
            results[disorder_name] = result.posterior_probability
        return results

    def calculate_explanation(
        self,
        disorder_name: str,
        evidence: List[InferenceEvidence],
    ) -> Dict:
        result = self.compute_posterior(disorder_name, evidence)
        symptom_impacts = []
        for ev in evidence:
            cpt = self.get_cpt(disorder_name, ev.symptom_name)
            if cpt is None:
                continue
            w = (ev.intensity / 100.0) if ev.intensity is not None else 1.0
            if ev.present:
                contrib = (cpt.disorder_present ** w) / (cpt.disorder_absent ** w + 1e-10)
            else:
                contrib = ((1 - cpt.disorder_present) ** w) / ((1 - cpt.disorder_absent) ** w + 1e-10)
            symptom_impacts.append({
                "symptom": ev.symptom_name,
                "present": ev.present,
                "intensity": ev.intensity,
                "likelihood_ratio": round(contrib, 4),
            })
        symptom_impacts.sort(key=lambda x: x["likelihood_ratio"], reverse=True)
        return {
            "disorder": disorder_name,
            "prior": result.prior_probability,
            "posterior": result.posterior_probability,
            "bayes_factor": result.bayes_factor,
            "symptom_contributions": symptom_impacts,
            "interpretation": self._interpret_result(result),
        }

    def _interpret_result(self, result: BayesianInferenceResult) -> str:
        if result.posterior_probability >= 0.8:
            return "Alta probabilidade clinica — fortemente sugestivo do diagnostico"
        elif result.posterior_probability >= 0.5:
            return "Probabilidade moderada — considerar como diagnostico diferencial"
        elif result.posterior_probability >= 0.2:
            return "Baixa probabilidade — improvavel, mas nao excluido"
        else:
            return "Probabilidade muito baixa — diagnostico improvavel"

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
        return errors
