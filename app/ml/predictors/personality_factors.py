"""Per-factor personality extraction from scale question-level data.
Supports BFP (5 factors), DT-12 (3 subscales), HEXACO-60 (6 factors),
BIS-11 (3 subscales), TAS-20 (3 subscales), RSES (1 dimension).
"""

from typing import Dict, List, Tuple
from uuid import UUID
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session
from app.models.base import ScaleResponse, ScaleQuestion, AssessmentScale, ClinicalConsultation, PatientProfile, PatientIdentity


BFP_FACTORS: Dict[str, str] = {
    "Abertura": "Abertura à Experiência — criatividade, curiosidade intelectual, apreço estético",
    "Conscienciosidade": "Conscienciosidade — organização, disciplina, responsabilidade, persistência",
    "Extroversão": "Extroversão — sociabilidade, energia social, assertividade, busca de estímulos",
    "Amabilidade": "Amabilidade — cooperação, empatia, confiança, cordialidade nas relações",
    "Neuroticismo": "Neuroticismo — instabilidade emocional, ansiedade, preocupação, vulnerabilidade ao estresse",
}

DT12_SUBSCALES: Dict[str, str] = {
    "Maquiavelismo": "Maquiavelismo — manipulação interpessoal, exploração dos outros, cinismo estratégico",
    "Narcisismo": "Narcisismo — grandiosidade, necessidade de admiração, senso de superioridade",
    "Psicopatia": "Psicopatia — insensibilidade afetiva, impulsividade, falta de remorso, busca de emoções",
}

HEXACO_FACTORS: Dict[str, str] = {
    "Honestidade-Humildade": "Honestidade-Humildade — sinceridade, justiça, modéstia, aversão à ganância e status",
    "Emotionalidade": "Emotionalidade — ansiedade, medo, dependência emocional, sensibilidade afetiva, empatia",
    "Extroversão": "Extroversão — sociabilidade, energia social, otimismo, liderança, busca de contato social",
    "Amabilidade": "Amabilidade — tolerância, perdão, cooperação, paciência, baixa agressividade",
    "Conscienciosidade": "Conscienciosidade — organização, disciplina, diligência, prudência, persistência",
    "Abertura à Experiência": "Abertura à Experiência — curiosidade intelectual, criatividade, apreço estético, inovação",
}

BIS11_SUBSCALES: Dict[str, str] = {
    "Atenção": "Impulsividade Atencional — dificuldade de concentração, pensamentos intrusivos, distração",
    "Motor": "Impulsividade Motora — ação sem pensar, agitação, comportamentos de risco, urgência",
    "Não-planejamento": "Impulsividade de Não-planejamento — falta de previsão, desorganização, imprevidência",
}

TAS20_SUBSCALES: Dict[str, str] = {
    "DIF": "Dificuldade em Identificar Sentimentos — confusão sobre emoções, sensações físicas sem rótulo emocional",
    "DDF": "Dificuldade em Descrever Sentimentos — pobreza de vocabulário emocional, inibição na comunicação afetiva",
    "EOT": "Pensamento Externamente Orientado — foco em fatos concretos, evitação da introspecção emocional",
}

RSES_DIMENSION: Dict[str, str] = {
    "Autoestima": "Autoestima Global — autovalorização, autoaceitação, respeito por si mesmo",
}


def _all_factor_names() -> list:
    return list(BFP_FACTORS.keys()) + list(DT12_SUBSCALES.keys()) + list(HEXACO_FACTORS.keys()) + list(BIS11_SUBSCALES.keys()) + list(TAS20_SUBSCALES.keys()) + list(RSES_DIMENSION.keys())


def _parse_factor_from_question(question_text: str) -> str:
    for name in _all_factor_names():
        if question_text.startswith(f"{name} -"):
            return name
    return ""


SCALE_NAMES = ["BFP", "DT-12 (Tríade Sombria)", "HEXACO-60", "BIS-11", "TAS-20", "RSES"]


def get_patient_personality_factors(db: Session, patient_uuid: UUID) -> dict:
    """Extract per-factor/subscale scores from question-level ScaleResponse data.

    Returns dict with:
      bfp, dt12, hexaco, bis11, tas20, rses
    each with respective factor/subscale dict, total_score, total_max.
    """
    results = (
        db.query(
            AssessmentScale.scale_name,
            ScaleQuestion.question_text,
            ScaleQuestion.question_order,
            sa_func.sum(ScaleResponse.response_value).label("total_score"),
        )
        .select_from(ClinicalConsultation)
        .join(PatientProfile, PatientProfile.profile_uuid == ClinicalConsultation.profile_uuid)
        .join(PatientIdentity, PatientIdentity.patient_uuid == PatientProfile.patient_uuid)
        .join(ScaleResponse, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
        .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
        .join(AssessmentScale, AssessmentScale.scale_id == ScaleQuestion.scale_id)
        .filter(PatientIdentity.patient_uuid == patient_uuid)
        .filter(AssessmentScale.scale_name.in_(SCALE_NAMES))
        .group_by(
            AssessmentScale.scale_name,
            ScaleQuestion.question_text,
            ScaleQuestion.question_order,
        )
        .order_by(AssessmentScale.scale_name, ScaleQuestion.question_order)
        .all()
    )

    scale_defs = {
        "BFP": (BFP_FACTORS, {"total_max": 100.0, "max_per_factor": 20.0, "per_item_max": 4.0}),
        "DT-12 (Tríade Sombria)": (DT12_SUBSCALES, {"total_max": 72.0, "max_per_factor": 24.0, "per_item_max": 6.0}),
        "HEXACO-60": (HEXACO_FACTORS, {"total_max": 300.0, "max_per_factor": 50.0, "per_item_max": 5.0}),
        "BIS-11": (BIS11_SUBSCALES, {"total_max": 120.0, "max_per_factor": 44.0, "per_item_max": 4.0}),
        "TAS-20": (TAS20_SUBSCALES, {"total_max": 100.0, "max_per_factor": 40.0, "per_item_max": 5.0}),
        "RSES": (RSES_DIMENSION, {"total_max": 40.0, "max_per_factor": 40.0, "per_item_max": 4.0}),
    }
    scale_keys = {
        "BFP": "bfp", "DT-12 (Tríade Sombria)": "dt12",
        "HEXACO-60": "hexaco", "BIS-11": "bis11",
        "TAS-20": "tas20", "RSES": "rses",
    }
    scale_factor_type = {
        "BFP": "factors", "DT-12 (Tríade Sombria)": "subscales",
        "HEXACO-60": "factors", "BIS-11": "subscales",
        "TAS-20": "subscales", "RSES": "dimensions",
    }

    result_dict = {}
    for sname in SCALE_NAMES:
        key = scale_keys[sname]
        ftype = scale_factor_type[sname]
        result_dict[key] = {ftype: {}, "total_score": 0.0, "total_max": scale_defs[sname][1]["total_max"]}

    if not results:
        return _try_raw_responses(db, patient_uuid, scale_defs, scale_keys, scale_factor_type)

    accum: Dict[str, Dict[str, list]] = {}
    for sname in SCALE_NAMES:
        key = scale_keys[sname]
        ftype = scale_factor_type[sname]
        fmap = scale_defs[sname][0]
        accum[f"{sname}_{key}"] = {f: [] for f in fmap}

    for r in results:
        factor = _parse_factor_from_question(r.question_text)
        score = float(r.total_score) if r.total_score is not None else 0.0
        for sname in SCALE_NAMES:
            if r.scale_name == sname:
                key = scale_keys[sname]
                fmap = scale_defs[sname][0]
                if factor in fmap:
                    accum[f"{sname}_{key}"][factor].append(score)

    for sname in SCALE_NAMES:
        key = scale_keys[sname]
        ftype = scale_factor_type[sname]
        fmap, cfg = scale_defs[sname]
        acc = accum[f"{sname}_{key}"]
        for fname, scores in acc.items():
            total = sum(scores)
            max_p = min(len(scores) * cfg["per_item_max"], cfg["max_per_factor"])
            result_dict[key][ftype][fname] = {
                "score": total,
                "max_possible": max_p,
                "percentage": round(total / max_p * 100, 1) if max_p > 0 else 0,
                "description": fmap.get(fname, ""),
            }
            result_dict[key]["total_score"] += total
        result_dict[key]["total_score"] = round(result_dict[key]["total_score"], 2)

    return result_dict


def _try_raw_responses(
    db: Session, patient_uuid: UUID,
    scale_defs: dict, scale_keys: dict, scale_factor_type: dict,
) -> dict:
    """Fallback: query all personality-scale responses without grouping by question_text."""
    raw = (
        db.query(
            AssessmentScale.scale_name,
            ScaleQuestion.question_text,
            ScaleResponse.response_value,
        )
        .select_from(ClinicalConsultation)
        .join(PatientProfile, PatientProfile.profile_uuid == ClinicalConsultation.profile_uuid)
        .join(PatientIdentity, PatientIdentity.patient_uuid == PatientProfile.patient_uuid)
        .join(ScaleResponse, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
        .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
        .join(AssessmentScale, AssessmentScale.scale_id == ScaleQuestion.scale_id)
        .filter(PatientIdentity.patient_uuid == patient_uuid)
        .filter(AssessmentScale.scale_name.in_(SCALE_NAMES))
        .all()
    )

    result_dict = {}
    for sname in SCALE_NAMES:
        key = scale_keys[sname]
        ftype = scale_factor_type[sname]
        result_dict[key] = {ftype: {}, "total_score": 0.0, "total_max": scale_defs[sname][1]["total_max"]}

    by_factor: Dict[str, Dict[str, list]] = {}
    for sname in SCALE_NAMES:
        key = scale_keys[sname]
        by_factor[f"{sname}_{key}"] = {}

    for r in raw:
        factor = _parse_factor_from_question(r.question_text)
        val = float(r.response_value) if r.response_value is not None else 0.0
        for sname in SCALE_NAMES:
            if r.scale_name == sname:
                key = scale_keys[sname]
                fmap = scale_defs[sname][0]
                if factor in fmap:
                    by_factor[f"{sname}_{key}"].setdefault(factor, []).append(val)

    for sname in SCALE_NAMES:
        key = scale_keys[sname]
        ftype = scale_factor_type[sname]
        fmap, cfg = scale_defs[sname]
        acc = by_factor[f"{sname}_{key}"]
        for fname, scores in acc.items():
            total = sum(scores)
            max_p = min(len(scores) * cfg["per_item_max"], cfg["max_per_factor"])
            result_dict[key][ftype][fname] = {
                "score": total,
                "max_possible": max_p,
                "percentage": round(total / max_p * 100, 1) if max_p > 0 else 0,
                "description": fmap.get(fname, ""),
            }
            result_dict[key]["total_score"] += total
        result_dict[key]["total_score"] = round(result_dict[key]["total_score"], 2)

    return result_dict


def get_patient_personality_timeline(db: Session, patient_uuid: UUID) -> dict:
    """Extract per-factor personality scores grouped by consultation (timeline).

    Returns dict with each personality scale containing a list of chronological
    snapshots with per-factor scores, date, and total.
    """
    results = (
        db.query(
            AssessmentScale.scale_name,
            ScaleQuestion.question_text,
            ScaleQuestion.question_order,
            ClinicalConsultation.consultation_uuid,
            ClinicalConsultation.consultation_date,
            sa_func.sum(ScaleResponse.response_value).label("total_score"),
        )
        .select_from(ClinicalConsultation)
        .join(PatientProfile, PatientProfile.profile_uuid == ClinicalConsultation.profile_uuid)
        .join(PatientIdentity, PatientIdentity.patient_uuid == PatientProfile.patient_uuid)
        .join(ScaleResponse, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
        .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
        .join(AssessmentScale, AssessmentScale.scale_id == ScaleQuestion.scale_id)
        .filter(PatientIdentity.patient_uuid == patient_uuid)
        .filter(AssessmentScale.scale_name.in_(SCALE_NAMES))
        .group_by(
            AssessmentScale.scale_name,
            ScaleQuestion.question_text,
            ScaleQuestion.question_order,
            ClinicalConsultation.consultation_uuid,
            ClinicalConsultation.consultation_date,
        )
        .order_by(ClinicalConsultation.consultation_date.asc())
        .all()
    )

    scale_defs = {
        "BFP": (BFP_FACTORS, {"total_max": 100.0, "max_per_factor": 20.0, "per_item_max": 4.0}),
        "DT-12 (Tríade Sombria)": (DT12_SUBSCALES, {"total_max": 72.0, "max_per_factor": 24.0, "per_item_max": 6.0}),
        "HEXACO-60": (HEXACO_FACTORS, {"total_max": 300.0, "max_per_factor": 50.0, "per_item_max": 5.0}),
        "BIS-11": (BIS11_SUBSCALES, {"total_max": 120.0, "max_per_factor": 44.0, "per_item_max": 4.0}),
        "TAS-20": (TAS20_SUBSCALES, {"total_max": 100.0, "max_per_factor": 40.0, "per_item_max": 5.0}),
        "RSES": (RSES_DIMENSION, {"total_max": 40.0, "max_per_factor": 40.0, "per_item_max": 4.0}),
    }
    scale_keys = {
        "BFP": "bfp", "DT-12 (Tríade Sombria)": "dt12",
        "HEXACO-60": "hexaco", "BIS-11": "bis11",
        "TAS-20": "tas20", "RSES": "rses",
    }
    scale_factor_type = {
        "BFP": "factors", "DT-12 (Tríade Sombria)": "subscales",
        "HEXACO-60": "factors", "BIS-11": "subscales",
        "TAS-20": "subscales", "RSES": "dimensions",
    }

    if not results:
        return {sk: {"timeline": [], "total_max": scale_defs[sn][1]["total_max"]}
                for sn, sk in scale_keys.items()}

    by_consultation: Dict[str, dict] = {}
    for r in results:
        cuuid = str(r.consultation_uuid)
        if cuuid not in by_consultation:
            by_consultation[cuuid] = {
                "consultation_uuid": cuuid,
                "date": r.consultation_date.isoformat(),
                "data": {},
            }
        factor = _parse_factor_from_question(r.question_text)
        score = float(r.total_score) if r.total_score is not None else 0.0
        sn = r.scale_name
        key = scale_keys.get(sn)
        fmap = scale_defs.get(sn, ({}, {}))[0]
        if key and factor in fmap:
            by_consultation[cuuid]["data"].setdefault(sn, {}).setdefault(key, {}).setdefault("items", []).append(
                (factor, score, fmap[factor])
            )

    output = {}
    for sn in SCALE_NAMES:
        key = scale_keys[sn]
        ftype = scale_factor_type[sn]
        fmap, cfg = scale_defs[sn]
        timeline = []
        for cuuid in sorted(by_consultation.keys()):
            entry = by_consultation[cuuid]
            scale_data = entry["data"].get(sn, {}).get(key, {})
            items = scale_data.get("items", [])
            if not items:
                continue
            factor_scores = {}
            total = 0.0
            seen: Dict[str, list] = {}
            for fname, sc, _ in items:
                seen.setdefault(fname, []).append(sc)
            for fname, scores in seen.items():
                f_total = sum(scores)
                max_p = min(len(scores) * cfg["per_item_max"], cfg["max_per_factor"])
                factor_scores[fname] = {
                    "score": f_total,
                    "max_possible": max_p,
                    "percentage": round(f_total / max_p * 100, 1) if max_p > 0 else 0,
                }
                total += f_total
            timeline.append({
                "consultation_uuid": entry["consultation_uuid"],
                "date": entry["date"],
                ftype: factor_scores,
                "total_score": round(total, 2),
                "total_max": cfg["total_max"],
            })
        output[key] = {"timeline": timeline, "total_max": cfg["total_max"]}

    return output


FACTOR_QUESTION_INDICES: Dict[str, Dict[str, List[int]]] = {
    "BFP": {
        "Abertura": [0, 1, 2, 3, 4],
        "Conscienciosidade": [5, 6, 7, 8, 9],
        "Extroversão": [10, 11, 12, 13, 14],
        "Amabilidade": [15, 16, 17, 18, 19],
        "Neuroticismo": [20, 21, 22, 23, 24],
    },
    "DT-12 (Tríade Sombria)": {
        "Maquiavelismo": [0, 1, 2, 3],
        "Narcisismo": [4, 5, 6, 7],
        "Psicopatia": [8, 9, 10, 11],
    },
    "HEXACO-60": {
        "Honestidade-Humildade": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Emotionalidade": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        "Extroversão": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
        "Amabilidade": [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "Conscienciosidade": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49],
        "Abertura à Experiência": [50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
    },
    "BIS-11": {
        "Atenção": [0, 1, 2, 3, 4, 5, 6, 7],
        "Motor": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        "Não-planejamento": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    },
    "TAS-20": {
        "DIF": [0, 1, 2, 3, 4, 5, 6],
        "DDF": [7, 8, 9, 10, 11],
        "EOT": [12, 13, 14, 15, 16, 17, 18, 19],
    },
}
