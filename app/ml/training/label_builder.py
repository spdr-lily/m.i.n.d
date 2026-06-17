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


def build_therapeutic_response_labels(df: pd.DataFrame) -> pd.DataFrame:
    df_target = df.copy()
    df_target["therapeutic_response_target"] = 0

    patients = df_target.groupby("patient_uuid")
    for pid, group in patients:
        group = group.sort_values("consultation_date")
        indices = group.index.tolist()
        for i in range(len(indices) - 1):
            current_idx = indices[i]
            next_idx = indices[i + 1]
            curr_phq = group.loc[current_idx].get("phq9_score", 0)
            next_phq = group.loc[next_idx].get("phq9_score", 0)
            if pd.notna(curr_phq) and pd.notna(next_phq):
                if next_phq < curr_phq:
                    df_target.loc[current_idx, "therapeutic_response_target"] = 1
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
