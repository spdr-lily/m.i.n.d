"""Label generation for each prediction objective."""

import pandas as pd
import numpy as np

KNOWN_DISORDERS = [
    "Transtorno Depressivo Maior", "Transtorno de Ansiedade Generalizada",
    "Transtorno do Pânico", "Transtorno de Estresse Pós-Traumático",
    "Transtorno Bipolar Tipo I", "Transtorno Bipolar Tipo II",
    "Transtorno Obsessivo-Compulsivo", "Transtorno Depressivo Persistente (Distimia)",
    "Transtorno de Ansiedade Social", "Agorafobia",
    "Transtorno por Uso de Substâncias", "Anorexia Nervosa",
    "Bulimia Nervosa", "Transtorno de Compulsão Alimentar",
    "Transtorno de Insônia", "Esquizofrenia / Transtorno Psicótico",
    "Transtorno de Sintomas Somáticos", "Transtorno do Espectro Autista",
    "Transtorno de Déficit de Atenção/Hiperatividade",
]


def build_diagnosis_labels(df: pd.DataFrame) -> pd.DataFrame:
    top_diag = df["top_inferences"].str.split(";").str[0].str.split(":").str[0]
    df_target = df.copy()
    df_target["diagnosis_target"] = top_diag.where(top_diag.isin(KNOWN_DISORDERS), "Other")
    return df_target


def build_relapse_labels(df: pd.DataFrame) -> pd.DataFrame:
    df_target = df.copy()
    df_target["relapse_target"] = 0

    patients = df_target.groupby("patient_uuid")
    for pid, group in patients:
        group = group.sort_values("consultation_date")
        indices = group.index.tolist()
        for i in range(len(indices) - 1):
            current_idx = indices[i]
            next_idx = indices[i + 1]
            days_diff = (group.loc[next_idx, "consultation_date"] - group.loc[current_idx, "consultation_date"]).days
            if days_diff <= 60:
                df_target.loc[current_idx, "relapse_target"] = 1
    return df_target


def build_suicide_risk_labels(df: pd.DataFrame) -> pd.DataFrame:
    df_target = df.copy()
    severe = df_target.get("severe_symptom_count", pd.Series([0] * len(df_target)))
    daily = df_target.get("daily_symptom_count", pd.Series([0] * len(df_target)))
    symptom_count = df_target.get("symptom_count", pd.Series([0] * len(df_target)))
    avg_intensity = df_target.get("avg_intensity", pd.Series([0] * len(df_target)))

    df_target["suicide_risk_target"] = (
        ((symptom_count >= 6) & (severe >= 2))
        | ((avg_intensity >= 6) & (symptom_count >= 5))
        | ((severe >= 3) & (daily >= 2))
    ).astype(int)
    return df_target


def generate_therapeutic_response(
    phq9_score: float,
    days_since_last_consult: float,
    consult_num: int,
    top_inferences: str,
    rng: np.random.Generator = np.random.default_rng(),
) -> int:
    """
    Simula resposta terapêutica com distribuição clinicamente plausível.
    Alvo: ~45% resposta geral, variando por perfil clínico.

    Modificadores baseados em evidência clínica sintética:
      - Casos leves (PHQ-9 < 10): +5pp (não +15pp, para evitar inflação
        quando a maioria das observações tem PHQ-9 baixo)
      - Acompanhamento prolongado (>60d): +7pp
      - Múltiplas consultas (>=3): +5pp
      - Transtornos depressivos/TAG: +3pp
      - Transtornos psicóticos/bipolares: -8pp
      - Intervalo muito curto (<14d, proxy de crise): -5pp

    Retorna 1 (respondeu) ou 0 (não respondeu).
    """
    base_prob = 0.30

    if pd.notna(phq9_score):
        if phq9_score < 10:
            base_prob += 0.05
        elif phq9_score < 20:
            base_prob += 0.10
        else:
            base_prob -= 0.05

    if pd.notna(days_since_last_consult):
        if days_since_last_consult > 60:
            base_prob += 0.07
        elif days_since_last_consult < 14:
            base_prob -= 0.05

    if consult_num >= 3:
        base_prob += 0.05

    if pd.notna(top_inferences):
        ti = top_inferences.lower()
        if any(k in ti for k in ["depressiv", "ansiedade generalizada", "tag"]):
            base_prob += 0.03
        if any(k in ti for k in ["bipolar", "esquizofrenia", "psicótico"]):
            base_prob -= 0.08

    base_prob = np.clip(base_prob, 0.10, 0.80)
    return int(rng.binomial(1, base_prob))


def build_therapeutic_response_labels(df: pd.DataFrame) -> pd.DataFrame:
    df_target = df.copy()
    rng = np.random.default_rng(42)
    labels = []
    for _, row in df_target.iterrows():
        label = generate_therapeutic_response(
            phq9_score=row.get("phq9_score"),
            days_since_last_consult=row.get("days_since_last_consult"),
            consult_num=row.get("consult_num", 1),
            top_inferences=row.get("top_inferences", ""),
            rng=rng,
        )
        labels.append(label)
    df_target["therapeutic_response_target"] = labels
    return df_target


LABEL_BUILDERS = {
    "diagnosis": build_diagnosis_labels,
    "relapse": build_relapse_labels,
    "suicide_risk": build_suicide_risk_labels,
    "therapeutic_response": build_therapeutic_response_labels,
}

TARGET_COLUMNS = {
    "diagnosis": "diagnosis_target",
    "relapse": "relapse_target",
    "suicide_risk": "suicide_risk_target",
    "therapeutic_response": "therapeutic_response_target",
}
