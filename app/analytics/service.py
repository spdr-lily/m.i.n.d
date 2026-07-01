from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.base import (
    PatientIdentity, PatientProfile, AssessmentScale, GenderIdentity,
    EducationLevel, Ethnicity, ClinicalConsultation, DiagnosticInference,
    Disorder, Symptom, ScaleResponse, ScaleQuestion, TreatmentOutcome,
    DisorderMedication,
)
from app.repositories import PatientRepository
from app.services.alerts_service import AlertsService

AGE_BINS = [0, 18, 35, 50, 65, 200]
AGE_LABELS = ["0-18", "19-35", "36-50", "51-65", "65+"]


class StatisticsService:
    def __init__(self, session: Session):
        self.session = session

    def get_patient_demographics(self) -> Dict[str, Any]:
        total = self.session.query(PatientIdentity).count()
        if total == 0:
            return {"total_patients": 0, "sex_distribution": {}, "gender_identity_distribution": {}, "age_distribution": {}}

        sex_query = (
            self.session.query(
                func.coalesce(PatientProfile.sex_type_id, 0).label("sex_type_id"),
                func.count().label("count"),
            )
            .select_from(PatientProfile)
            .group_by(PatientProfile.sex_type_id)
            .all()
        )
        sex_dist = {str(row.sex_type_id): row.count for row in sex_query}

        gender_query = (
            self.session.query(
                GenderIdentity.description,
                func.count().label("count"),
            )
            .select_from(PatientProfile)
            .join(GenderIdentity, PatientProfile.gender_identity_id == GenderIdentity.gender_identity_id, isouter=True)
            .group_by(GenderIdentity.description)
            .all()
        )
        gender_dist = {row.description or "Não informado": row.count for row in gender_query}

        sql = text("SELECT birth_date FROM clinical.patient_profile")
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty or df["birth_date"].isna().all():
            age_dist = {}
        else:
            now = datetime.now(timezone.utc)
            df["age"] = (now.year - pd.to_datetime(df["birth_date"]).dt.year)
            bins = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LABELS, right=True)
            age_dist = bins.value_counts().reindex(AGE_LABELS, fill_value=0).to_dict()

        edu_query = (
            self.session.query(
                func.coalesce(PatientProfile.education_level_id, 0).label("edu_id"),
                func.count().label("count"),
            )
            .select_from(PatientProfile)
            .group_by(PatientProfile.education_level_id)
            .all()
        )
        edu_labels = {0: "Não informado"}
        for r in self.session.query(EducationLevel).all():
            edu_labels[r.education_level_id] = r.description
        edu_dist = {edu_labels.get(row.edu_id, f"ID {row.edu_id}"): row.count for row in edu_query}

        eth_query = (
            self.session.query(
                func.coalesce(PatientProfile.ethnicity_id, 0).label("eth_id"),
                func.count().label("count"),
            )
            .select_from(PatientProfile)
            .group_by(PatientProfile.ethnicity_id)
            .all()
        )
        eth_labels = {0: "Não informado"}
        for r in self.session.query(Ethnicity).all():
            eth_labels[r.ethnicity_id] = r.description
        eth_dist = {eth_labels.get(row.eth_id, f"ID {row.eth_id}"): row.count for row in eth_query}

        return {
            "total_patients": total,
            "sex_distribution": sex_dist,
            "gender_identity_distribution": gender_dist,
            "age_distribution": age_dist,
            "education_level_distribution": edu_dist,
            "ethnicity_distribution": eth_dist,
        }

    def get_scale_score_distribution(self, scale_name: str) -> Dict[str, Any]:
        scale = self.session.query(AssessmentScale).filter(
            AssessmentScale.scale_name == scale_name
        ).first()
        if not scale:
            return {"scale_name": scale_name, "total_responses": 0, "distribution": {}}

        sql = text("""
            SELECT sr.consultation_uuid, sum(sr.response_value) as total_score
            FROM clinical.scale_responses sr
            JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
            WHERE sq.scale_id = :scale_id
            GROUP BY sr.consultation_uuid
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={"scale_id": scale.scale_id})
        if df.empty:
            return {"scale_name": scale_name, "total_responses": 0, "distribution": {}}

        from app.ml.models.assessment_scales import get_scale as get_scale_def
        scale_def = get_scale_def(scale_name)
        if not scale_def:
            return {"scale_name": scale_name, "total_responses": 0, "distribution": {}}

        stats = df["total_score"].describe().to_dict()
        df["severity"] = df["total_score"].apply(
            lambda s: scale_def.interpret(float(s))[0]
        )
        bands = {
            "minimal": 0, "mild": 0, "moderate": 0,
            "moderately_severe": 0, "severe": 0,
        }
        dist = df["severity"].value_counts().to_dict()
        bands.update({k: int(v) for k, v in dist.items() if k in bands})

        return {
            "scale_name": scale_name,
            "total_assessments": len(df),
            "distribution": bands,
            "statistics": {k: round(v, 2) for k, v in stats.items()},
        }


class ConsultationMetricsService:
    def __init__(self, session: Session):
        self.session = session

    def get_consultation_metrics(self, days: int = 30) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        total = self.session.query(ClinicalConsultation).filter(
            ClinicalConsultation.created_at >= since
        ).count()
        unique_patients = (
            self.session.query(ClinicalConsultation.profile_uuid)
            .filter(ClinicalConsultation.created_at >= since)
            .distinct()
            .count()
        )
        sql = text("""
            SELECT date(created_at) as date, count(*) as count
            FROM clinical.clinical_consultation
            WHERE created_at >= :since
            GROUP BY date(created_at)
            ORDER BY date(created_at)
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={"since": since})
        if df.empty:
            daily_breakdown = {}
            trend = {}
        else:
            daily_breakdown = dict(zip(df["date"].astype(str), df["count"]))
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").asfreq("D", fill_value=0)
            df["ma7"] = df["count"].rolling(7, min_periods=1).mean().round(2)
            trend = {
                "daily_counts": df["count"].to_dict(),
                "moving_avg_7d": df["ma7"].dropna().to_dict(),
            }

        return {
            "period_days": days,
            "total_consultations": total,
            "unique_patients": unique_patients,
            "avg_per_day": round(total / max(days, 1), 2),
            "daily_breakdown": daily_breakdown,
            "trend": trend,
        }

    def get_general_stats(self) -> Dict[str, Any]:
        patients = self.session.query(PatientIdentity).count()
        consultations = self.session.query(ClinicalConsultation).count()
        inferences = self.session.query(DiagnosticInference).count()
        disorders = self.session.query(Disorder).count()
        symptoms = self.session.query(Symptom).count()

        return {
            "total_patients": patients,
            "total_consultations": consultations,
            "total_inferences": inferences,
            "total_disorders": disorders,
            "total_symptoms": symptoms,
            "avg_inferences_per_consultation": round(inferences / max(consultations, 1), 2),
        }


class BIService:
    def __init__(self, session: Session):
        self.session = session

    def get_scale_trends(self, scale_name: str, days: int = 90) -> Dict[str, Any]:
        scale = self.session.query(AssessmentScale).filter(
            AssessmentScale.scale_name == scale_name
        ).first()
        if not scale:
            return {"scale_name": scale_name, "error": "Scale not found"}

        since = datetime.now(timezone.utc) - timedelta(days=days)
        sql = text("""
            SELECT consultation_date::date, ROUND(AVG(total), 2) as avg_score
            FROM (
                SELECT c2.consultation_date, sum(sr.response_value) as total
                FROM clinical.scale_responses sr
                JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
                JOIN clinical.clinical_consultation c2 ON sr.consultation_uuid = c2.consultation_uuid
                WHERE sq.scale_id = :scale_id AND c2.consultation_date >= :since
                GROUP BY c2.consultation_uuid, c2.consultation_date
            ) sub
            GROUP BY consultation_date::date
            ORDER BY consultation_date::date
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={
            "scale_id": scale.scale_id, "since": since,
        })
        if df.empty:
            return {"scale_name": scale_name, "total_records": 0, "trend": {}}

        stats = df["avg_score"].describe().to_dict()
        df = df.set_index("consultation_date")
        df = df.sort_index()
        df["ma3"] = df["avg_score"].rolling(3, min_periods=1).mean().round(2)

        return {
            "scale_name": scale_name,
            "total_records": len(df),
            "statistics": {k: round(v, 2) for k, v in stats.items()},
            "trend": {
                "scores": df["avg_score"].to_dict(),
                "moving_avg_3": df["ma3"].dropna().to_dict(),
            },
        }

    def get_scale_correlations(self) -> List[Dict[str, Any]]:
        scales = self.session.query(AssessmentScale).all()
        scale_map = {s.scale_name: s.scale_id for s in scales}
        if len(scale_map) < 2:
            return []

        scale_data = {}
        for name, sid in scale_map.items():
            sql = text("""
                SELECT c.consultation_uuid, sum(sr.response_value) as total
                FROM clinical.scale_responses sr
                JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
                JOIN clinical.clinical_consultation c ON sr.consultation_uuid = c.consultation_uuid
                WHERE sq.scale_id = :sid
                GROUP BY c.consultation_uuid
            """)
            df = pd.read_sql_query(sql, self.session.bind, params={"sid": sid})
            if not df.empty:
                scale_data[name] = df.set_index("consultation_uuid")["total"]

        if len(scale_data) < 2:
            return []

        combined = pd.DataFrame(scale_data)
        corr_matrix = combined.corr(min_periods=1)
        pairs = []
        for i, s1 in enumerate(corr_matrix.columns):
            for s2 in corr_matrix.columns[i + 1:]:
                val = corr_matrix.loc[s1, s2]
                if not pd.isna(val):
                    pairs.append({
                        "scale_1": s1,
                        "scale_2": s2,
                        "pearson_r": round(val, 4),
                        "sample_size": int(combined[[s1, s2]].dropna().shape[0]),
                    })
        return sorted(pairs, key=lambda x: abs(x["pearson_r"]), reverse=True)

    def get_disorder_prevalence(self, top_n: int = 10) -> List[Dict[str, Any]]:
        results = (
            self.session.query(
                DiagnosticInference.disorder_id,
                Disorder.disorder_name,
                Disorder.cid_code,
                func.count().label("inference_count"),
                func.avg(DiagnosticInference.inference_probability).label("avg_probability"),
            )
            .join(Disorder, DiagnosticInference.disorder_id == Disorder.disorder_id)
            .group_by(DiagnosticInference.disorder_id, Disorder.disorder_name, Disorder.cid_code)
            .order_by(func.count().desc())
            .limit(top_n)
            .all()
        )
        return [
            {
                "disorder_id": r.disorder_id,
                "disorder_name": r.disorder_name,
                "cid_code": r.cid_code,
                "inference_count": r.inference_count,
                "avg_probability": round(float(r.avg_probability), 4) if r.avg_probability else 0,
            }
            for r in results
        ]

    def get_prevalence_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        sql = text(f"""
            SELECT
                dd.disorder_name,
                d.year || '-' || LPAD(d.month::text, 2, '0') AS year_month,
                COUNT(*) AS diagnosis_count,
                AVG(fd.probability)::float AS avg_probability
            FROM dw.fact_diagnosis fd
            JOIN dw.dim_disorder dd ON fd.disorder_key = dd.disorder_key
            JOIN dw.dim_date d ON fd.date_key = d.date_key
            WHERE d.full_date >= CURRENT_DATE - INTERVAL '{months} months'
            GROUP BY dd.disorder_name, d.year, d.month
            ORDER BY dd.disorder_name, year_month
        """)
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return []
        result = []
        for disorder_name, group in df.groupby("disorder_name"):
            group = group.sort_values("year_month")
            result.append({
                "disorder_name": disorder_name,
                "monthly_counts": [
                    {"month": r.year_month, "count": int(r.diagnosis_count), "avg_probability": r.avg_probability}
                    for r in group.itertuples()
                ],
                "total_count": int(group["diagnosis_count"].sum()),
            })
        return sorted(result, key=lambda x: x["total_count"], reverse=True)

    def get_comorbidity_heatmap(self, top_n: int = 10) -> Dict[str, Any]:
        sql = text("""
            WITH consult_disorders AS (
                SELECT fd.consultation_key, dd.disorder_name
                FROM dw.fact_diagnosis fd
                JOIN dw.dim_disorder dd ON fd.disorder_key = dd.disorder_key
                GROUP BY fd.consultation_key, dd.disorder_name
            ),
            disorder_pairs AS (
                SELECT a.disorder_name AS disorder_a,
                       b.disorder_name AS disorder_b,
                       COUNT(*) AS co_occurrence_count
                FROM consult_disorders a
                JOIN consult_disorders b ON a.consultation_key = b.consultation_key
                    AND a.disorder_name < b.disorder_name
                GROUP BY a.disorder_name, b.disorder_name
            )
            SELECT disorder_a, disorder_b, co_occurrence_count
            FROM disorder_pairs
            ORDER BY co_occurrence_count DESC
            LIMIT :limit
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={"limit": top_n ** 2})
        if df.empty:
            return {"disorders": [], "pairs": []}

        disorders = sorted(set(df["disorder_a"].tolist() + df["disorder_b"].tolist()))
        matrix = pd.DataFrame(0, index=disorders, columns=disorders)
        for _, row in df.iterrows():
            matrix.loc[row.disorder_a, row.disorder_b] = row.co_occurrence_count
            matrix.loc[row.disorder_b, row.disorder_a] = row.co_occurrence_count

        return {
            "disorders": disorders,
            "pairs": [
                {"disorder_a": r.disorder_a, "disorder_b": r.disorder_b, "count": int(r.co_occurrence_count)}
                for r in df.itertuples()
            ],
            "matrix": matrix.to_dict(),
        }


class DashboardService:
    def __init__(self, session: Session):
        self.session = session

    def get_overview_stats(self) -> Dict[str, Any]:
        general = ConsultationMetricsService(self.session).get_general_stats()
        alerts_service = AlertsService(self.session)
        alerts = alerts_service.run_all_checks()
        avg_confidence = self.session.query(
            func.avg(DiagnosticInference.confidence_level)
        ).scalar() or 0
        return {
            "total_patients": general["total_patients"],
            "total_consultations": general["total_consultations"],
            "total_inferences": general["total_inferences"],
            "active_alerts": alerts["total_alerts"],
            "avg_confidence": round(float(avg_confidence), 4),
        }

    def get_patient_longitudinal(
        self,
        patient_uuid: UUID,
        days: int = 365,
    ) -> Dict[str, Any]:
        repo = PatientRepository(self.session)
        identity = repo.get_patient_identity(patient_uuid)
        profile = repo.get_patient_profile(patient_uuid)
        if not identity or not profile:
            return {"error": "Patient not found"}

        since = datetime.now(timezone.utc) - timedelta(days=days)

        scale_sql = text("""
            SELECT c.consultation_uuid, c.consultation_date, a.scale_name,
                   sum(sr.response_value) as total_score
            FROM clinical.clinical_consultation c
            JOIN clinical.scale_responses sr ON c.consultation_uuid = sr.consultation_uuid
            JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
            JOIN diagnostic.assessment_scales a ON sq.scale_id = a.scale_id
            WHERE c.profile_uuid = :profile_uuid AND c.created_at >= :since
            GROUP BY c.consultation_uuid, c.consultation_date, a.scale_name
            ORDER BY c.consultation_date
        """)
        scale_df = pd.read_sql_query(scale_sql, self.session.bind, params={
            "profile_uuid": profile.profile_uuid, "since": since,
        })

        infer_sql = text("""
            SELECT c.consultation_uuid, c.consultation_date, d.disorder_name,
                   di.inference_probability
            FROM clinical.clinical_consultation c
            JOIN clinical.diagnostic_inference di ON c.consultation_uuid = di.consultation_uuid
            JOIN diagnostic.disorder d ON di.disorder_id = d.disorder_id
            WHERE c.profile_uuid = :profile_uuid AND c.created_at >= :since
            ORDER BY c.consultation_date, di.inference_probability DESC
        """)
        infer_df = pd.read_sql_query(infer_sql, self.session.bind, params={
            "profile_uuid": profile.profile_uuid, "since": since,
        })

        consultations = self.session.query(ClinicalConsultation).filter(
            ClinicalConsultation.profile_uuid == profile.profile_uuid,
            ClinicalConsultation.created_at >= since,
        ).order_by(ClinicalConsultation.created_at).all()

        timeline = []
        for c in consultations:
            cuuid = str(c.consultation_uuid)
            scale_row = scale_df[scale_df["consultation_uuid"] == cuuid] if not scale_df.empty else pd.DataFrame()
            infer_row = infer_df[infer_df["consultation_uuid"] == cuuid] if not infer_df.empty else pd.DataFrame()

            timeline.append({
                "consultation_uuid": cuuid,
                "date": c.consultation_date.isoformat() if c.consultation_date else None,
                "scale_scores": dict(zip(scale_row["scale_name"], scale_row["total_score"])) if not scale_row.empty else {},
                "top_diagnoses": [
                    {"disorder": r["disorder_name"], "probability": float(r["inference_probability"])}
                    for _, r in infer_row.iterrows()
                ] if not infer_row.empty else [],
            })

        return {
            "patient_uuid": str(patient_uuid),
            "total_consultations": len(consultations),
            "period_days": days,
            "timeline": timeline,
        }


class DWAnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def query_view(self, view_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        sql = text(f"SELECT * FROM dw.{view_name} ORDER BY 1 LIMIT :lim")
        df = pd.read_sql_query(sql, self.session.bind, params={"lim": limit})
        if df.empty:
            return []
        return df.fillna(0).to_dict(orient="records")

    def get_prevalence_trends(self, months: int = 12, top_n: int = 10) -> Dict[str, Any]:
        sql = text("""
            SELECT disorder_name, disorder_category, year_month, diagnosis_count,
                   avg_probability, unique_patients
            FROM dw.vw_prevalence_trends
            WHERE year_month >= to_char(CURRENT_DATE - INTERVAL ':months months', 'YYYY-MM')
            ORDER BY diagnosis_count DESC
        """.replace(":months", str(months)))
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return {"disorders": [], "total": 0}

        top_disorders = df.groupby("disorder_name")["diagnosis_count"].sum().nlargest(top_n).index.tolist()
        df = df[df["disorder_name"].isin(top_disorders)]

        result = []
        for disorder_name, group in df.groupby("disorder_name"):
            group = group.sort_values("year_month")
            result.append({
                "disorder_name": disorder_name,
                "data": [
                    {"month": r.year_month, "count": int(r.diagnosis_count),
                     "avg_probability": float(r.avg_probability)}
                    for r in group.itertuples()
                ],
                "total": int(group["diagnosis_count"].sum()),
            })
        return {"disorders": sorted(result, key=lambda x: x["total"], reverse=True), "total": len(result)}

    def get_comorbidity_pairs(self, top_n: int = 15) -> Dict[str, Any]:
        sql = text("""
            SELECT disorder_a, category_a, disorder_b, category_b,
                   co_occurrence_count, prevalence_pct
            FROM dw.vw_comorbidity_pairs
            ORDER BY co_occurrence_count DESC
            LIMIT :lim
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={"lim": top_n})
        if df.empty:
            return {"pairs": [], "total_pairs": 0}
        return {
            "pairs": df.fillna(0).to_dict(orient="records"),
            "total_pairs": len(df),
        }

    def get_score_distributions(self) -> Dict[str, Any]:
        sql = text("""
            SELECT scale_name, total_responses, mean_score, stddev_score,
                   min_score, max_score, median_score, mean_pct, unique_patients
            FROM dw.vw_score_distribution
            ORDER BY total_responses DESC
        """)
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return {"scales": []}
        return {"scales": df.fillna(0).to_dict(orient="records")}

    def get_scale_severity_distribution(self) -> Dict[str, Any]:
        sql = text("SELECT scale_name, severity_level, response_count, avg_score FROM dw.vw_scale_severity_distribution")
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return {"scales": []}
        result = []
        for scale_name, group in df.groupby("scale_name"):
            result.append({
                "scale_name": scale_name,
                "severity_levels": [
                    {"severity": r.severity_level, "count": int(r.response_count), "avg_score": float(r.avg_score)}
                    for r in group.itertuples()
                ],
            })
        return {"scales": sorted(result, key=lambda x: x["scale_name"])}

    def get_patient_summary(self, limit: int = 50) -> Dict[str, Any]:
        data = self.query_view("vw_patient_summary", limit=limit)
        return {"patients": data, "total": len(data)}

    def get_professional_workload(self) -> Dict[str, Any]:
        data = self.query_view("vw_professional_workload")
        return {"professionals": data, "total": len(data)}

    def get_demographic_summary(self) -> Dict[str, Any]:
        data = self.query_view("vw_demographic_summary")
        return {"demographics": data, "total": len(data)}

    def get_monthly_consultation_stats(self, months: int = 12) -> Dict[str, Any]:
        sql = text("""
            SELECT year_month, total_consultations, unique_patients,
                   avg_symptoms, avg_total_intensity,
                   consultations_with_inference, avg_max_probability
            FROM dw.vw_monthly_consultation_stats
            WHERE year_month >= to_char(CURRENT_DATE - INTERVAL ':months months', 'YYYY-MM')
            ORDER BY year_month
        """.replace(":months", str(months)))
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return {"months": [], "total_months": 0}
        return {
            "months": df.fillna(0).to_dict(orient="records"),
            "total_months": len(df),
        }

    def get_symptom_prevalence_by_disorder(self, top_n: int = 10) -> Dict[str, Any]:
        sql = text("""
            SELECT disorder_name, disorder_category, symptom_name,
                   consultation_count, avg_intensity, prevalence_pct
            FROM dw.vw_symptom_prevalence_by_disorder
            ORDER BY prevalence_pct DESC
            LIMIT :lim
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={"lim": top_n * 20})
        if df.empty:
            return {"disorders": []}
        result = []
        for dname, group in df.groupby("disorder_name"):
            group = group.sort_values("prevalence_pct", ascending=False).head(top_n)
            result.append({
                "disorder_name": dname,
                "symptoms": [
                    {"symptom": r.symptom_name, "consultation_count": int(r.consultation_count),
                     "avg_intensity": float(r.avg_intensity), "prevalence_pct": float(r.prevalence_pct)}
                    for r in group.itertuples()
                ],
            })
        return {"disorders": sorted(result, key=lambda x: x["disorder_name"])}

    def get_scale_trends_monthly(self, months: int = 12) -> Dict[str, Any]:
        sql = text("""
            SELECT scale_name, year_month, response_count, avg_score,
                   avg_pct, stddev_score, min_score, max_score, unique_patients
            FROM dw.vw_scale_trends_monthly
            WHERE year_month >= to_char(CURRENT_DATE - INTERVAL ':months months', 'YYYY-MM')
            ORDER BY scale_name, year_month
        """.replace(":months", str(months)))
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return {"scales": []}
        result = []
        for sname, group in df.groupby("scale_name"):
            group = group.sort_values("year_month")
            result.append({
                "scale_name": sname,
                "months": [
                    {"month": r.year_month, "avg_score": float(r.avg_score),
                     "avg_pct": float(r.avg_pct), "response_count": int(r.response_count),
                     "stddev_score": float(r.stddev_score), "unique_patients": int(r.unique_patients)}
                    for r in group.itertuples()
                ],
            })
        return {"scales": sorted(result, key=lambda x: x["scale_name"])}

    def get_disorder_by_demographic(self) -> Dict[str, Any]:
        sql = text("""
            SELECT disorder_name, disorder_category, age_group, sex,
                   patient_count, diagnosis_count, avg_probability, penetration_pct
            FROM dw.vw_disorder_by_demographic
            ORDER BY patient_count DESC
        """)
        df = pd.read_sql_query(sql, self.session.bind)
        if df.empty:
            return {"demographics": []}
        return {"demographics": df.fillna(0).to_dict(orient="records")}


class MLDashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_personality_averages(self) -> dict:
        bfp_factors = ["Abertura", "Conscienciosidade", "Extroversão", "Amabilidade", "Neuroticismo"]
        dt12_subscales = ["Maquiavelismo", "Narcisismo", "Psicopatia"]
        hexaco_factors = ["Honestidade-Humildade", "Emotionalidade", "Extroversão", "Amabilidade", "Conscienciosidade", "Abertura à Experiência"]
        bis11_subscales = ["Atenção", "Motor", "Não-planejamento"]
        tas20_subscales = ["DIF", "DDF", "EOT"]

        def _factor_avg(prefix: str) -> float:
            sq = (
                self.db.query(
                    ScaleResponse.consultation_uuid,
                    func.sum(ScaleResponse.response_value).label("factor_total"),
                )
                .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
                .filter(
                    ScaleQuestion.question_text.like(f"{prefix}%"),
                    ScaleResponse.response_value.isnot(None),
                )
                .group_by(ScaleResponse.consultation_uuid)
                .subquery()
            )
            avg = self.db.query(func.avg(sq.c.factor_total)).scalar()
            return round(float(avg), 2) if avg else 0.0

        bfp = {f: _factor_avg(f"{f} -") for f in bfp_factors}
        dt12 = {s: _factor_avg(f"{s} -") for s in dt12_subscales}
        hexaco = {f: _factor_avg(f"{f} -") for f in hexaco_factors}
        bis11 = {s: _factor_avg(f"{s} -") for s in bis11_subscales}
        tas20 = {s: _factor_avg(f"{s} -") for s in tas20_subscales}
        rses = _factor_avg("Autoestima -")

        total_with_data = (
            self.db.query(func.count(func.distinct(ScaleResponse.consultation_uuid)))
            .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
            .filter(ScaleQuestion.question_text.like("Abertura -%"))
            .scalar()
        ) or 0

        return {
            "bfp_averages": bfp, "dt12_averages": dt12, "hexaco_averages": hexaco,
            "bis11_averages": bis11, "tas20_averages": tas20,
            "rses_averages": {"Autoestima": rses},
            "total_assessments": total_with_data,
        }

    def get_efficacy_summary(self) -> dict:
        total_outcomes = self.db.query(func.count(TreatmentOutcome.outcome_uuid)).scalar() or 0
        total_associations = self.db.query(func.count(DisorderMedication.dm_id)).scalar() or 0
        outcome_stats = (
            self.db.query(TreatmentOutcome.outcome, func.count(TreatmentOutcome.outcome_uuid))
            .group_by(TreatmentOutcome.outcome).all()
        )
        outcome_dist = {row[0]: row[1] for row in outcome_stats}

        line_stats = (
            self.db.query(
                DisorderMedication.line_of_treatment,
                func.avg(DisorderMedication.success_rate),
                func.count(DisorderMedication.dm_id),
            )
            .group_by(DisorderMedication.line_of_treatment).all()
        )
        by_line = [
            {"line": row[0], "avg_success_rate": round(float(row[1]), 3) if row[1] else 0, "count": row[2]}
            for row in line_stats
        ]

        return {
            "total_outcomes": total_outcomes, "total_associations": total_associations,
            "outcome_distribution": outcome_dist, "by_line_of_treatment": by_line,
        }

    def get_models_info(self) -> List[dict]:
        return [
            {"name": "Big Five (RF)", "objective": "personality_bfp", "algorithm": "random_forest", "stage": "Production", "r2": 0.468, "mae": 2.10, "description": "Prediz 5 fatores BFP a partir de escalas clínicas"},
            {"name": "Big Five (XGB)", "objective": "personality_bfp", "algorithm": "xgboost", "stage": "Production", "r2": 0.366, "mae": 2.25, "description": "Prediz 5 fatores BFP via XGBoost"},
            {"name": "Tríade Sombria (RF)", "objective": "personality_dt12", "algorithm": "random_forest", "stage": "Production", "r2": 0.499, "mae": 1.62, "description": "Prediz 3 subescalas DT-12 a partir de escalas clínicas"},
            {"name": "Tríade Sombria (XGB)", "objective": "personality_dt12", "algorithm": "xgboost", "stage": "Production", "r2": 0.176, "mae": 1.89, "description": "Prediz 3 subescalas DT-12 via XGBoost"},
        ]

    def get_ml_dashboard(self) -> dict:
        return {
            "personality": self.get_personality_averages(),
            "efficacy": self.get_efficacy_summary(),
            "models": self.get_models_info(),
        }


class AggregationService:
    def __init__(self, session: Session):
        self.session = session

    def query(self, sql: str, params: Optional[Dict] = None) -> pd.DataFrame:
        return pd.read_sql_query(text(sql), self.session.bind, params=params or {})
