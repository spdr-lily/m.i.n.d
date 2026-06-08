from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from app.ml.inference.bayesian_network import BayesianNetwork, InferenceEvidence, BayesianInferenceResult
from app.ml.models.network_definition import build_mood_disorder_network
from app.ml.models.dsm_icd_mapper import DSMICDMapper
from app.repositories.inference_repository import InferenceRepository
from app.repositories.disorder_repository import DisorderRepository
from app.repositories.consultation_repository import ConsultationRepository
from app.models.base import DiagnosticInference


SYMPTOM_TO_NODE: Dict[str, str] = {
    "depressed_mood": "depressed_mood",
    "loss_of_interest": "loss_of_interest",
    "sleep_disturbance": "sleep_disturbance",
    "fatigue": "fatigue",
    "appetite_changes": "appetite_changes",
    "guilt_feelings": "guilt_feelings",
    "concentration_problems": "concentration_problems",
    "psychomotor_changes": "psychomotor_changes",
    "suicidal_ideation": "suicidal_ideation",
    "euphoric_mood": "euphoric_mood",
    "increased_energy": "increased_energy",
    "grandiosity": "grandiosity",
    "decreased_sleep": "decreased_sleep",
    "rapid_speech": "rapid_speech",
    "racing_thoughts": "racing_thoughts",
    "distractibility": "distractibility",
    "risk_behavior": "risk_behavior",
    "hypomanic_mood": "hypomanic_mood",
    "mildly_increased_energy": "mildly_increased_energy",
    "reduced_sleep_hypomania": "reduced_sleep_hypomania",
    "bipolar_depressed_mood": "bipolar_depressed_mood",
    "bipolar_loss_of_interest": "bipolar_loss_of_interest",
    "excessive_worry": "excessive_worry",
    "restlessness": "restlessness",
    "fatigue_gad": "fatigue_gad",
    "muscle_tension": "muscle_tension",
    "sleep_disturbance_gad": "sleep_disturbance_gad",
    "irritability": "irritability",
    "concentration_difficulty_gad": "concentration_difficulty_gad",
    "panic_attacks": "panic_attacks",
    "palpitations": "palpitations",
    "chest_pain": "chest_pain",
    "shortness_of_breath": "shortness_of_breath",
    "fear_of_dying": "fear_of_dying",
    "derealization": "derealization",
    "avoidance_behavior": "avoidance_behavior",
    "traumatic_exposure": "traumatic_exposure",
    "intrusive_memories": "intrusive_memories",
    "nightmares": "nightmares",
    "hypervigilance": "hypervigilance",
    "avoidance_ptsd": "avoidance_ptsd",
    "negative_cognitions": "negative_cognitions",
    "startle_response": "startle_response",
    "chronic_low_mood": "chronic_low_mood",
    "poor_appetite_dysthymia": "poor_appetite_dysthymia",
    "low_self_esteem": "low_self_esteem",
    "hopelessness": "hopelessness",
    "low_energy_dysthymia": "low_energy_dysthymia",
    "social_fear": "social_fear",
    "avoidance_social": "avoidance_social",
    "performance_anxiety": "performance_anxiety",
    "blushing": "blushing",
    "obsessions": "obsessions",
    "compulsions": "compulsions",
    "repetitive_behavior": "repetitive_behavior",
    "intrusive_thoughts": "intrusive_thoughts",
}

DISORDER_NAME_REVERSE: Dict[str, str] = {
    "Major Depressive Disorder": "Major Depressive Disorder",
    "Bipolar I Disorder": "Bipolar I Disorder",
    "Bipolar II Disorder": "Bipolar II Disorder",
    "Generalized Anxiety Disorder": "Generalized Anxiety Disorder",
    "Panic Disorder": "Panic Disorder",
    "Post-Traumatic Stress Disorder": "Post-Traumatic Stress Disorder",
    "Persistent Depressive Disorder": "Persistent Depressive Disorder",
    "Social Anxiety Disorder": "Social Anxiety Disorder",
    "Obsessive-Compulsive Disorder": "Obsessive-Compulsive Disorder",
}


class DisorderPredictor:
    def __init__(self, session: Session):
        self.session = session
        self.network: BayesianNetwork = build_mood_disorder_network()
        self.dsm_icd_mapper = DSMICDMapper()

    def build_evidence(
        self,
        observations: List,
        symptom_id_to_name: Optional[Dict[int, str]] = None,
    ) -> List[InferenceEvidence]:
        evidence = []
        for obs in observations:
            symptom_name = None
            if symptom_id_to_name:
                symptom_name = symptom_id_to_name.get(obs.symptom_id)
            if not symptom_name:
                symptom_name = getattr(obs, "symptom_name", None) or getattr(obs, "symptom", None)
                if symptom_name and hasattr(symptom_name, "symptom_name"):
                    symptom_name = symptom_name.symptom_name

            node_name = SYMPTOM_TO_NODE.get(symptom_name)
            if node_name:
                intensity = float(obs.intensity) if obs.intensity is not None else None
                present = intensity is not None and intensity > 0 if intensity is not None else True
                evidence.append(InferenceEvidence(
                    symptom_name=node_name,
                    present=present,
                    intensity=intensity,
                ))
        return evidence

    def infer_from_observations(
        self,
        observations: List,
        symptom_id_to_name: Optional[Dict[int, str]] = None,
        top_k: int = 5,
    ) -> List[BayesianInferenceResult]:
        evidence = self.build_evidence(observations, symptom_id_to_name)
        if not evidence:
            return []
        return self.network.infer(evidence, top_k=top_k)

    def infer_from_consultation(
        self,
        consultation_uuid: UUID,
        top_k: int = 5,
    ) -> List[BayesianInferenceResult]:
        consultation_repo = ConsultationRepository(self.session)
        consultation = consultation_repo.get_consultation(consultation_uuid)
        if not consultation:
            raise ValueError(f"Consultation {consultation_uuid} not found")

        observations = consultation.symptom_observations or []
        return self.infer_from_observations(observations, top_k=top_k)

    def persist_inferences(
        self,
        consultation_uuid: UUID,
        results: List[BayesianInferenceResult],
        model_version: str = "bayesian-net-v1",
    ) -> List[DiagnosticInference]:
        repo = InferenceRepository(self.session)
        disorder_repo = DisorderRepository(self.session)
        disorders = disorder_repo.list_disorders()

        disorder_map = {}
        for d in disorders:
            key = DISORDER_NAME_REVERSE.get(d.disorder_name, d.disorder_name)
            disorder_map[key] = d

        inferences = []
        for result in results:
            disorder = disorder_map.get(result.disorder_name)
            if not disorder:
                continue

            inference = repo.create_inference(
                consultation_uuid=consultation_uuid,
                disorder_id=disorder.disorder_id,
                inference_probability=result.posterior_probability,
                confidence_level=result.posterior_probability,
                generated_by_model="bayesian-network",
                model_version=model_version,
            )
            inferences.append(inference)

        self.session.commit()
        return inferences

    def get_explanation(
        self,
        consultation_uuid: UUID,
    ) -> Optional[Dict]:
        consultation_repo = ConsultationRepository(self.session)
        consultation = consultation_repo.get_consultation(consultation_uuid)
        if not consultation:
            return None

        observations = consultation.symptom_observations or []
        evidence = self.build_evidence(observations)
        results = self.network.infer(evidence, top_k=9)

        explanations = []
        for result in results:
            explanations.append(
                self.network.calculate_explanation(result.disorder_name, evidence)
            )

        return {
            "consultation_uuid": str(consultation_uuid),
            "total_symptoms_observed": len(observations),
            "total_symptoms_matched": len(evidence),
            "network_version": "mood-disorder-bn-v1",
            "inference_method": "naive_bayes_variable_elimination",
            "results": explanations,
        }
