"""Scale-based ML prediction service: personality inference and disorder risk from scale scores."""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.ml.models.assessment_scales import SCALES_REGISTRY


CLINICAL_SCALE_NAMES = [
    "PHQ-9", "GAD-7", "MADRS", "MDQ", "PCL-5",
    "Y-BOCS", "AUDIT", "ASRM", "ASRS", "AQ-10",
]
NEURO_SCALE_NAMES = [
    "MEMÓRIA", "QI - RASTREIO", "RECONHECIMENTO DE ROSTOS",
    "FLUÊNCIA VERBAL", "TESTE DO RELÓGIO", "TRILHAS",
    "STROOP", "CANCELAMENTO", "FIGURA COMPLEXA DE REY",
]
ALL_SCALE_NAMES = CLINICAL_SCALE_NAMES + NEURO_SCALE_NAMES


def build_personality_feature_vector(
    db_session: Session, patient_uuid: str
) -> Optional[Dict[str, float]]:
    """Build feature vector from latest clinical scale scores for a patient.

    Uses the most recent consultation's scale scores as features.
    """
    from app.models.base import (
        ClinicalConsultation, PatientProfile, PatientIdentity,
        ScaleResponse, ScaleQuestion, AssessmentScale,
    )
    from sqlalchemy import func as sa_func

    latest = (
        db_session.query(
            AssessmentScale.scale_name,
            sa_func.sum(ScaleResponse.response_value).label("total_score"),
        )
        .select_from(ClinicalConsultation)
        .join(PatientProfile, PatientProfile.profile_uuid == ClinicalConsultation.profile_uuid)
        .join(PatientIdentity, PatientIdentity.patient_uuid == PatientProfile.patient_uuid)
        .join(ScaleResponse, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
        .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
        .join(AssessmentScale, AssessmentScale.scale_id == ScaleQuestion.scale_id)
        .filter(PatientIdentity.patient_uuid == patient_uuid)
        .filter(AssessmentScale.scale_name.in_(ALL_SCALE_NAMES))
        .group_by(AssessmentScale.scale_name)
        .all()
    )

    if not latest:
        return None

    features = {}
    for r in latest:
        features[r.scale_name] = float(r.total_score)
    # Ensure all scale features are present (fill missing with 0)
    for name in ALL_SCALE_NAMES:
        features.setdefault(name, 0.0)

    return features


def predict_personality_from_scales(
    scale_scores: Dict[str, float],
    personality_model: Optional[dict] = None,
) -> dict:
    """Predict BFP 5 factors and DT-12 3 subscales from clinical scale scores.

    Uses trained regression models if available; falls back to heuristic rules.
    """
    if personality_model:
        return _predict_with_model(scale_scores, personality_model)
    return _predict_heuristic(scale_scores)


def _predict_with_model(scale_scores: Dict[str, float], artifact: dict) -> dict:
    model = artifact["model"]
    feature_cols = artifact["feature_cols"]

    X = np.array([[scale_scores.get(c, 0.0) for c in feature_cols]])
    preds = model.predict(X)[0]

    target_names = artifact.get("target_names", [
        "bfp_abertura", "bfp_conscienciosidade", "bfp_extroversao",
        "bfp_amabilidade", "bfp_neuroticismo",
        "dt12_maquiavelismo", "dt12_narcisismo", "dt12_psicopatia",
    ])

    result = {}
    for i, name in enumerate(target_names):
        result[name] = round(float(preds[i]), 2)

    # Compute total scores
    bfp_total = sum(result.get(k, 0) for k in [
        "bfp_abertura", "bfp_conscienciosidade", "bfp_extroversao",
        "bfp_amabilidade", "bfp_neuroticismo",
    ])
    dt12_total = sum(result.get(k, 0) for k in [
        "dt12_maquiavelismo", "dt12_narcisismo", "dt12_psicopatia",
    ])

    return {
        "bfp": {
            f: {"score": round(result.get(f"bfp_{target}", 0), 2), "max_possible": 20.0}
            for f, target in [
                ("Abertura", "abertura"), ("Conscienciosidade", "conscienciosidade"),
                ("Extroversão", "extroversao"), ("Amabilidade", "amabilidade"),
                ("Neuroticismo", "neuroticismo"),
            ]
        },
        "bfp_total": round(bfp_total, 2),
        "dt12": {
            s: {"score": round(result.get(f"dt12_{target}", 0), 2), "max_possible": 24.0}
            for s, target in [
                ("Maquiavelismo", "maquiavelismo"), ("Narcisismo", "narcisismo"),
                ("Psicopatia", "psicopatia"),
            ]
        },
        "dt12_total": round(dt12_total, 2),
        "ml_source": "model",
    }


def _predict_heuristic(scale_scores: Dict[str, float]) -> dict:
    """Heuristic personality inference from clinical scale scores.

    Maps clinical scale patterns to expected personality factor scores.
    Used when no ML model is available.
    """
    phq9 = scale_scores.get("PHQ-9", 0)
    gad7 = scale_scores.get("GAD-7", 0)
    madrs = scale_scores.get("MADRS", 0)
    mdq = scale_scores.get("MDQ", 0)
    pcl5 = scale_scores.get("PCL-5", 0)
    audit = scale_scores.get("AUDIT", 0)
    asrm = scale_scores.get("ASRM", 0)

    # Neuroticism is strongly associated with depression and anxiety scores
    neuroticism = min(20.0, (phq9 / 27 * 8) + (gad7 / 21 * 6) + (madrs / 60 * 6))
    neuroticism = round(max(0, neuroticism), 2)

    # Extroversão: inversely related to social anxiety, depression
    # Lower PHQ-9 and higher ASRM suggest more extraversion
    extroversao = min(20.0, max(0, 10 - (phq9 / 27 * 4) + (asrm / 20 * 4)))
    extroversao = round(extroversao, 2)

    # Conscienciosidade: inversely related to AUDIT, ASRS (impulsivity)
    conscienciosidade = min(20.0, max(0, 12 - (audit / 40 * 4) - (scale_scores.get("ASRS", 0) / 72 * 2)))
    conscienciosidade = round(conscienciosidade, 2)

    # Abertura: positively related to MDQ (bipolar creativity), inversely to rigidity
    abertura = min(20.0, max(0, 10 + (mdq / 13 * 3) - (pcl5 / 80 * 2)))
    abertura = round(abertura, 2)

    # Amabilidade: inversely related to AUDIT, PCL-5 hostility
    amabilidade = min(20.0, max(0, 12 - (audit / 40 * 3) - (pcl5 / 80 * 2)))
    amabilidade = round(amabilidade, 2)

    # DT-12 subscales
    maquiavelismo = min(24.0, max(0, audit / 40 * 12 + mdq / 13 * 4))
    maquiavelismo = round(maquiavelismo, 2)

    narcisismo = min(24.0, max(0, asrm / 20 * 10 + mdq / 13 * 6))
    narcisismo = round(narcisismo, 2)

    psicopatia = min(24.0, max(0, audit / 40 * 10 + pcl5 / 80 * 4))
    psicopatia = round(psicopatia, 2)

    bfp_total = round(neuroticism + extroversao + conscienciosidade + abertura + amabilidade, 2)
    dt12_total = round(maquiavelismo + narcisismo + psicopatia, 2)

    return {
        "bfp": {
            "Abertura": {"score": abertura, "max_possible": 20.0},
            "Conscienciosidade": {"score": conscienciosidade, "max_possible": 20.0},
            "Extroversão": {"score": extroversao, "max_possible": 20.0},
            "Amabilidade": {"score": amabilidade, "max_possible": 20.0},
            "Neuroticismo": {"score": neuroticism, "max_possible": 20.0},
        },
        "bfp_total": bfp_total,
        "dt12": {
            "Maquiavelismo": {"score": maquiavelismo, "max_possible": 24.0},
            "Narcisismo": {"score": narcisismo, "max_possible": 24.0},
            "Psicopatia": {"score": psicopatia, "max_possible": 24.0},
        },
        "dt12_total": dt12_total,
        "ml_source": "heuristic",
    }


def predict_disorder_risk_from_scales(
    scale_scores: Dict[str, float],
) -> Dict[str, float]:
    """Predict disorder risk probabilities from scale scores using heuristic rules.

    Returns dict of { disorder_name: probability } for core disorders.
    """
    phq9 = scale_scores.get("PHQ-9", 0)
    gad7 = scale_scores.get("GAD-7", 0)
    madrs = scale_scores.get("MADRS", 0)
    mdq = scale_scores.get("MDQ", 0)
    pcl5 = scale_scores.get("PCL-5", 0)
    ybocs = scale_scores.get("Y-BOCS", 0)
    audit = scale_scores.get("AUDIT", 0)
    asrm = scale_scores.get("ASRM", 0)
    asrs = scale_scores.get("ASRS", 0)
    aq10 = scale_scores.get("AQ-10", 0)

    risks = {}

    # Depression (PHQ-9 + MADRS)
    depression_score = (phq9 / 27 * 0.4) + (madrs / 60 * 0.4)
    if phq9 >= 15:
        depression_score += 0.2
    risks["Transtorno Depressivo Maior"] = min(0.95, depression_score)

    # Anxiety (GAD-7)
    risks["Transtorno de Ansiedade Generalizada"] = min(0.95, gad7 / 21 * 0.8)

    # Bipolar (MDQ + ASRM)
    bipolar_score = (mdq / 13 * 0.4) + (asrm / 20 * 0.4)
    if mdq >= 7 and asrm >= 6:
        bipolar_score += 0.2
    risks["Transtorno Bipolar Tipo I"] = min(0.95, bipolar_score)

    # PTSD (PCL-5)
    risks["Transtorno de Estresse Pós-Traumático"] = min(0.95, pcl5 / 80 * 0.8)

    # OCD (Y-BOCS)
    risks["Transtorno Obsessivo-Compulsivo"] = min(0.95, ybocs / 40 * 0.8)

    # Substance Use (AUDIT)
    risks["Transtorno por Uso de Substâncias"] = min(0.95, audit / 40 * 0.8)

    # ADHD (ASRS)
    risks["Transtorno de Déficit de Atenção/Hiperatividade"] = min(0.95, asrs / 72 * 0.8)

    # Autism (AQ-10)
    risks["Transtorno do Espectro Autista"] = min(0.95, aq10 / 10 * 0.8)

    # Panic (GAD-7 + ASRM)
    panic_score = (gad7 / 21 * 0.3) + (asrm / 20 * 0.3)
    if gad7 >= 10:
        panic_score += 0.2
    risks["Transtorno do Pânico"] = min(0.95, panic_score)

    return {k: round(v, 4) for k, v in sorted(risks.items(), key=lambda x: x[1], reverse=True)}
