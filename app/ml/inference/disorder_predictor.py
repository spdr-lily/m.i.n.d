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
    # English keys (original)
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
    # Portuguese (BR) keys — map from DB symptom names
    "humor_deprimido": "depressed_mood",
    "anhedonia": "loss_of_interest",
    "alteracao_peso": "appetite_changes",
    "insonia_hipersonia": "sleep_disturbance",
    "agitacao_retardo": "psychomotor_changes",
    "fadiga": "fatigue",
    "sentimento_inutilidade": "low_self_esteem",
    "concentracao": "concentration_problems",
    "pensamento_morte": "suicidal_ideation",
    "lentificacao": "psychomotor_changes",
    "hipersonia_atipica": "sleep_disturbance",
    "choro_frequente": "depressed_mood",
    "preocupacao_excessiva": "excessive_worry",
    "inquietacao": "restlessness",
    "tensao_muscular": "muscle_tension",
    "irritabilidade": "irritability",
    "sono_prejudicado": "sleep_disturbance_gad",
    "fadiga_constante": "fatigue_gad",
    "palpitacoes": "palpitations",
    "sudorese": "panic_attacks",
    "tremores": "panic_attacks",
    "sensacao_sufocamento": "shortness_of_breath",
    "medo_morrer": "fear_of_dying",
    "dor_peito": "chest_pain",
    "nausea_abdominal": "panic_attacks",
    "tontura_vertigem": "panic_attacks",
    "parestesias": "panic_attacks",
    "desrealizacao": "derealization",
    "medo_enlouquecer": "panic_attacks",
    "calafrios_ondas_calor": "panic_attacks",
    "medo_morrer_panico": "fear_of_dying",
    "euforia": "euphoric_mood",
    "grandiosidade": "grandiosity",
    "logorreia": "rapid_speech",
    "reducao_sono": "decreased_sleep",
    "fuga_ideias": "racing_thoughts",
    "comportamento_risco": "risk_behavior",
    "hiperssexualidade": "risk_behavior",
    "gastos_excessivos": "risk_behavior",
    "planos_grandiosos": "grandiosity",
    "obsessoes": "obsessions",
    "compulsoes": "compulsions",
    "simetria_ordenacao": "repetitive_behavior",
    "verificacao_repetitiva": "compulsions",
    "lavagem_limpeza": "compulsions",
    "contagem_ritualistica": "compulsions",
    "acumulo_objetos": "repetitive_behavior",
    "reexperiencia": "intrusive_memories",
    "esquiva": "avoidance_behavior",
    "hipervigilancia": "hypervigilance",
    "sonhos_angustia": "nightmares",
    "flashbacks_dissociativos": "intrusive_memories",
    "sobresalto_acentuado": "startle_response",
    "culpa_merito": "guilt_feelings",
    "desesperanca_futuro": "hopelessness",
    "amnesia_traumatica": "intrusive_memories",
    "amnésia_traumática": "intrusive_memories",
    "crencas_negativas": "negative_cognitions",
    "crenças_negativas": "negative_cognitions",
}

DISORDER_NAME_REVERSE: Dict[str, str] = {
    # English (Bayesian network) → Portuguese (DB)
    "Major Depressive Disorder": "Transtorno Depressivo Maior",
    "Bipolar I Disorder": "Transtorno Bipolar Tipo I",
    "Bipolar II Disorder": "Transtorno Bipolar Tipo II",
    "Generalized Anxiety Disorder": "Transtorno de Ansiedade Generalizada",
    "Panic Disorder": "Transtorno do Pânico",
    "Post-Traumatic Stress Disorder": "Transtorno de Estresse Pós-Traumático",
    "Persistent Depressive Disorder": "Transtorno Depressivo Persistente (Distimia)",
    "Social Anxiety Disorder": "Transtorno de Ansiedade Social",
    "Obsessive-Compulsive Disorder": "Transtorno Obsessivo-Compulsivo",
}


class DisorderPredictor:
    def __init__(self, session: Session):
        self.session = session
        self.network: BayesianNetwork = build_mood_disorder_network()
        self.dsm_icd_mapper = DSMICDMapper()
        self._symptom_id_to_name: Optional[Dict[int, str]] = None

    def _load_symptom_id_to_name(self) -> Dict[int, str]:
        if self._symptom_id_to_name is None:
            from app.models.base import Symptom
            symptoms = self.session.query(Symptom).all()
            self._symptom_id_to_name = {s.symptom_id: s.symptom_name for s in symptoms}
        return self._symptom_id_to_name

    def build_evidence(
        self,
        observations: List,
        symptom_id_to_name: Optional[Dict[int, str]] = None,
    ) -> List[InferenceEvidence]:
        if symptom_id_to_name is None:
            symptom_id_to_name = self._load_symptom_id_to_name()
        evidence = []
        for obs in observations:
            symptom_name = symptom_id_to_name.get(obs.symptom_id)
            if not symptom_name:
                symptom_name = getattr(obs, "symptom", None)
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

        db_by_name = {d.disorder_name: d for d in disorders}
        disorder_map = {}
        for en_name, pt_name in DISORDER_NAME_REVERSE.items():
            disorder = db_by_name.get(pt_name)
            if disorder:
                disorder_map[en_name] = disorder

        inferences = []
        for result in results:
            disorder = disorder_map.get(result.disorder_name) or db_by_name.get(result.disorder_name)
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
