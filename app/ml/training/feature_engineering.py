"""Feature extraction from Data Warehouse for ML models."""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from app.core.config import settings


def extract_consultation_features(engine) -> pd.DataFrame:
    query = """
    WITH symptom_agg AS (
        SELECT c.consultation_uuid,
               count(*)                                              AS symptom_count,
               round(avg(so.intensity)::numeric, 2)                  AS avg_intensity,
               round(sum(so.intensity)::numeric, 2)                  AS total_intensity,
               count(*) FILTER (WHERE so.intensity >= 7)             AS severe_symptom_count,
               count(*) FILTER (WHERE so.frequency = 'daily')        AS daily_symptom_count,
               string_agg(DISTINCT sym.symptom_name, ', ')           AS symptom_names
        FROM clinical.clinical_consultation c
        JOIN clinical.symptom_observation so ON c.consultation_uuid = so.consultation_uuid
        JOIN diagnostic.symptoms sym ON so.symptom_id = sym.symptom_id
        GROUP BY c.consultation_uuid
    ),
    scale_agg AS (
        SELECT sr.consultation_uuid,
               s.scale_name,
               sum(sr.response_value) AS total_score
        FROM clinical.scale_responses sr
        JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
        JOIN diagnostic.assessment_scales s ON sq.scale_id = s.scale_id
        GROUP BY sr.consultation_uuid, s.scale_name
    ),
    scale_pivot AS (
        SELECT consultation_uuid,
               max(CASE WHEN scale_name='PHQ-9' THEN total_score END)          AS phq9_score,
               max(CASE WHEN scale_name='GAD-7' THEN total_score END)          AS gad7_score,
               max(CASE WHEN scale_name='MADRS' THEN total_score END)          AS madrs_score,
               max(CASE WHEN scale_name='MDQ' THEN total_score END)            AS mdq_score,
               max(CASE WHEN scale_name='PCL-5' THEN total_score END)          AS pcl5_score,
               max(CASE WHEN scale_name='Y-BOCS' THEN total_score END)         AS ybocs_score,
               max(CASE WHEN scale_name='AUDIT' THEN total_score END)          AS audit_score,
               max(CASE WHEN scale_name='ASRM' THEN total_score END)           AS asrm_score,
               max(CASE WHEN scale_name='ASRS' THEN total_score END)           AS asrs_score,
               max(CASE WHEN scale_name='AQ-10' THEN total_score END)          AS aq10_score,
               max(CASE WHEN scale_name='BFP' THEN total_score END)            AS bfp_score,
               max(CASE WHEN scale_name='DT-12 (Tríade Sombria)' THEN total_score END) AS dt12_score,
               max(CASE WHEN scale_name='MEMÓRIA' THEN total_score END)        AS memoria_score,
               max(CASE WHEN scale_name='QI - RASTREIO' THEN total_score END)  AS qi_rastreio_score,
               max(CASE WHEN scale_name='RECONHECIMENTO DE ROSTOS' THEN total_score END) AS reconhecimento_rostos_score,
               max(CASE WHEN scale_name='FLUÊNCIA VERBAL' THEN total_score END) AS fluencia_verbal_score,
               max(CASE WHEN scale_name='TESTE DO RELÓGIO' THEN total_score END) AS teste_relogio_score,
               max(CASE WHEN scale_name='TRILHAS' THEN total_score END)        AS trilhas_score,
               max(CASE WHEN scale_name='STROOP' THEN total_score END)         AS stroop_score,
               max(CASE WHEN scale_name='CANCELAMENTO' THEN total_score END)   AS cancelamento_score,
               max(CASE WHEN scale_name='FIGURA COMPLEXA DE REY' THEN total_score END) AS rey_score,
               max(CASE WHEN scale_name='PHQ-9' AND total_score >= 15 THEN 1 ELSE 0 END) AS phq9_moderate_severe,
               max(CASE WHEN scale_name='GAD-7' AND total_score >= 10 THEN 1 ELSE 0 END) AS gad7_moderate_severe,
               max(CASE WHEN scale_name='MADRS' AND total_score >= 20 THEN 1 ELSE 0 END) AS madrs_moderate_severe,
               max(CASE WHEN scale_name='PCL-5' AND total_score >= 45 THEN 1 ELSE 0 END) AS pcl5_moderate_severe,
               max(CASE WHEN scale_name='Y-BOCS' AND total_score >= 16 THEN 1 ELSE 0 END) AS ybocs_moderate_severe,
               max(CASE WHEN scale_name='AUDIT' AND total_score >= 16 THEN 1 ELSE 0 END) AS audit_harmful,
               max(CASE WHEN scale_name='MDQ' AND total_score >= 7 THEN 1 ELSE 0 END) AS mdq_positive,
               max(CASE WHEN scale_name='ASRM' AND total_score >= 6 THEN 1 ELSE 0 END) AS asrm_positive,
               max(CASE WHEN scale_name='ASRS' AND total_score >= 17 THEN 1 ELSE 0 END) AS asrs_positive,
               max(CASE WHEN scale_name='AQ-10' AND total_score >= 6 THEN 1 ELSE 0 END) AS aq10_positive
        FROM scale_agg
        GROUP BY consultation_uuid
    ),
    inference_agg AS (
        SELECT consultation_uuid,
               max(inference_probability)                                  AS max_prob,
               count(*)                                                    AS inference_count,
               string_agg(d.disorder_name || ':' || round(inference_probability::numeric,4)::text, '; ' ORDER BY inference_probability DESC) AS top_inferences
        FROM diagnostic.diagnostic_inference di
        JOIN diagnostic.disorders d ON di.disorder_id = d.disorder_id
        GROUP BY consultation_uuid
    ),
    patient_info AS (
        SELECT c.consultation_uuid,
               pp.patient_uuid,
               extract(year from age(pp.birth_date))::int                 AS age,
               st.description                                             AS sex,
               el.description                                             AS education_level,
               et.description                                             AS ethnicity,
               pp.marital_status,
               pp.occupation,
               c.consultation_date
        FROM clinical.clinical_consultation c
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        LEFT JOIN core.sex_types st ON pp.sex_type_id = st.sex_type_id
        LEFT JOIN core.education_levels el ON pp.education_level_id = el.education_level_id
        LEFT JOIN core.ethnicities et ON pp.ethnicity_id = et.ethnicity_id
    ),
    consult_order AS (
        SELECT consultation_uuid, patient_uuid, consultation_date,
               row_number() OVER (PARTITION BY patient_uuid ORDER BY consultation_date) AS consult_num,
               count(*)       OVER (PARTITION BY patient_uuid)                           AS total_consults,
               lag(consultation_date) OVER (PARTITION BY patient_uuid ORDER BY consultation_date) AS prev_consult_date
        FROM patient_info
    ),
    days_since_prev AS (
        SELECT consultation_uuid,
               extract(day from (consultation_date - prev_consult_date))::int AS days_since_last_consult
        FROM consult_order
    )
    SELECT pi.consultation_uuid                                                                        AS consultation_uuid,
           pi.patient_uuid                                                                             AS patient_uuid,
           co.consult_num                                                                              AS consult_num,
           co.total_consults                                                                           AS total_consults,
           dsp.days_since_last_consult                                                                  AS days_since_last_consult,
           pi.age                                                                                      AS age,
           CASE WHEN pi.sex = 'Masculino' THEN 1 WHEN pi.sex = 'Feminino' THEN 0 ELSE NULL END         AS sex_male,
           CASE WHEN pi.education_level = 'Ensino Superior' THEN 1 ELSE 0 END                          AS higher_education,
           CASE WHEN pi.marital_status = 'Casado' THEN 1 ELSE 0 END                                    AS married,
           sa.symptom_count                                                                            AS symptom_count,
           sa.avg_intensity                                                                            AS avg_intensity,
           sa.total_intensity                                                                          AS total_intensity,
           sa.severe_symptom_count                                                                     AS severe_symptom_count,
           sa.daily_symptom_count                                                                      AS daily_symptom_count,
            sp.phq9_score                                                                               AS phq9_score,
            sp.gad7_score                                                                               AS gad7_score,
            sp.madrs_score                                                                              AS madrs_score,
            sp.mdq_score                                                                                AS mdq_score,
            sp.pcl5_score                                                                               AS pcl5_score,
            sp.ybocs_score                                                                              AS ybocs_score,
            sp.audit_score                                                                              AS audit_score,
            sp.asrm_score                                                                               AS asrm_score,
            sp.asrs_score                                                                               AS asrs_score,
            sp.aq10_score                                                                               AS aq10_score,
            sp.bfp_score                                                                                AS bfp_score,
            sp.dt12_score                                                                               AS dt12_score,
            sp.memoria_score                                                                            AS memoria_score,
            sp.qi_rastreio_score                                                                        AS qi_rastreio_score,
            sp.reconhecimento_rostos_score                                                              AS reconhecimento_rostos_score,
            sp.fluencia_verbal_score                                                                    AS fluencia_verbal_score,
            sp.teste_relogio_score                                                                      AS teste_relogio_score,
            sp.trilhas_score                                                                            AS trilhas_score,
            sp.stroop_score                                                                             AS stroop_score,
            sp.cancelamento_score                                                                       AS cancelamento_score,
            sp.rey_score                                                                                AS rey_score,
            sp.phq9_moderate_severe                                                                     AS phq9_moderate_severe,
            sp.gad7_moderate_severe                                                                     AS gad7_moderate_severe,
            sp.madrs_moderate_severe                                                                    AS madrs_moderate_severe,
            sp.pcl5_moderate_severe                                                                     AS pcl5_moderate_severe,
            sp.ybocs_moderate_severe                                                                    AS ybocs_moderate_severe,
            sp.audit_harmful                                                                            AS audit_harmful,
            sp.mdq_positive                                                                             AS mdq_positive,
            sp.asrm_positive                                                                            AS asrm_positive,
            sp.asrs_positive                                                                            AS asrs_positive,
            sp.aq10_positive                                                                            AS aq10_positive,
           ia.max_prob                                                                                 AS max_inference_prob,
           ia.inference_count                                                                          AS inference_count,
           ia.top_inferences                                                                           AS top_inferences,
           pi.consultation_date                                                                        AS consultation_date
    FROM patient_info pi
    JOIN consult_order co ON pi.consultation_uuid = co.consultation_uuid
    JOIN symptom_agg sa ON pi.consultation_uuid = sa.consultation_uuid
    LEFT JOIN scale_pivot sp ON pi.consultation_uuid = sp.consultation_uuid
    LEFT JOIN inference_agg ia ON pi.consultation_uuid = ia.consultation_uuid
    LEFT JOIN days_since_prev dsp ON pi.consultation_uuid = dsp.consultation_uuid
    ORDER BY pi.patient_uuid, pi.consultation_date
    """
    return pd.read_sql(query, engine)


def extract_patient_history_features(engine) -> pd.DataFrame:
    query = """
    WITH prev_diagnoses AS (
        SELECT pp.patient_uuid, d.disorder_name,
               count(*) AS diagnosis_count
        FROM diagnostic.diagnostic_inference di
        JOIN clinical.clinical_consultation c ON di.consultation_uuid = c.consultation_uuid
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        JOIN diagnostic.disorders d ON di.disorder_id = d.disorder_id
        WHERE di.inference_probability > 0.3
        GROUP BY pp.patient_uuid, d.disorder_name
    ),
    prev_diag_pivot AS (
        SELECT patient_uuid,
               count(*) AS distinct_prev_diagnoses,
               string_agg(disorder_name, ', ') AS prev_disorder_names
        FROM prev_diagnoses
        GROUP BY patient_uuid
    ),
    prev_scale_traj AS (
        SELECT pp.patient_uuid,
               avg(CASE WHEN s.scale_name='PHQ-9' THEN sr.response_value END) AS avg_phq9_per_item,
               avg(CASE WHEN s.scale_name='GAD-7' THEN sr.response_value END) AS avg_gad7_per_item,
               avg(CASE WHEN s.scale_name='MADRS' THEN sr.response_value END) AS avg_madrs_per_item,
               avg(CASE WHEN s.scale_name='PCL-5' THEN sr.response_value END) AS avg_pcl5_per_item,
               avg(CASE WHEN s.scale_name='Y-BOCS' THEN sr.response_value END) AS avg_ybocs_per_item,
               avg(CASE WHEN s.scale_name='AUDIT' THEN sr.response_value END) AS avg_audit_per_item,
               avg(CASE WHEN s.scale_name='ASRS' THEN sr.response_value END) AS avg_asrs_per_item,
               avg(CASE WHEN s.scale_name='BFP' THEN sr.response_value END) AS avg_bfp_per_item,
               avg(CASE WHEN s.scale_name='DT-12 (Tríade Sombria)' THEN sr.response_value END) AS avg_dt12_per_item
        FROM clinical.scale_responses sr
        JOIN clinical.clinical_consultation c ON sr.consultation_uuid = c.consultation_uuid
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
        JOIN diagnostic.assessment_scales s ON sq.scale_id = s.scale_id
        GROUP BY pp.patient_uuid
    )
    SELECT pdp.patient_uuid,
           pdp.distinct_prev_diagnoses,
           pdp.prev_disorder_names,
           pst.avg_phq9_per_item,
           pst.avg_gad7_per_item,
           pst.avg_madrs_per_item,
           pst.avg_pcl5_per_item,
           pst.avg_ybocs_per_item,
           pst.avg_audit_per_item,
           pst.avg_asrs_per_item,
           pst.avg_bfp_per_item,
           pst.avg_dt12_per_item
    FROM prev_diag_pivot pdp
    LEFT JOIN prev_scale_traj pst ON pdp.patient_uuid = pst.patient_uuid
    """
    return pd.read_sql(query, engine)


def build_feature_matrix(engine):
    df_main = extract_consultation_features(engine)
    df_pat = extract_patient_history_features(engine)

    df = df_main.merge(df_pat, on="patient_uuid", how="left")
    df = df.sort_values(["patient_uuid", "consultation_date"]).reset_index(drop=True)

    demo_cols = ["age", "sex_male", "higher_education", "married"]
    symptom_cols = [
        "symptom_count", "avg_intensity", "total_intensity",
        "severe_symptom_count", "daily_symptom_count",
    ]
    scale_cols = [
        "phq9_score", "gad7_score", "madrs_score", "mdq_score", "pcl5_score",
        "ybocs_score", "audit_score", "asrm_score", "asrs_score", "aq10_score",
        "bfp_score", "dt12_score", "memoria_score", "qi_rastreio_score",
        "reconhecimento_rostos_score", "fluencia_verbal_score", "teste_relogio_score",
        "trilhas_score", "stroop_score", "cancelamento_score", "rey_score",
        "phq9_moderate_severe", "gad7_moderate_severe", "madrs_moderate_severe",
        "pcl5_moderate_severe", "ybocs_moderate_severe", "audit_harmful",
        "mdq_positive", "asrm_positive", "asrs_positive", "aq10_positive",
    ]
    temporal_cols = ["consult_num", "total_consults", "days_since_last_consult"]
    history_cols = [
        "distinct_prev_diagnoses",
        "avg_phq9_per_item", "avg_gad7_per_item", "avg_madrs_per_item",
        "avg_pcl5_per_item", "avg_ybocs_per_item", "avg_audit_per_item",
        "avg_asrs_per_item", "avg_bfp_per_item", "avg_dt12_per_item",
    ]

    feature_cols = demo_cols + symptom_cols + scale_cols + temporal_cols + history_cols
    feature_cols = [c for c in feature_cols if c in df.columns]

    df["consultation_date"] = pd.to_datetime(df["consultation_date"])

    for c in feature_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df[feature_cols] = df[feature_cols].fillna(0)

    return df, feature_cols
