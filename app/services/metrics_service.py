from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.base import (
    PatientIdentity, PatientProfile, ClinicalConsultation,
    DiagnosticInference, ScaleResponse, Disorder, Symptom,
    AssessmentScale, ScaleQuestion, EducationLevel, Ethnicity,
)
from app.repositories.patient_repository import PatientRepository


AGE_BINS = [0, 18, 35, 50, 65, 200]
AGE_LABELS = ["0-18", "19-35", "36-50", "51-65", "65+"]


class MetricsService:
    def __init__(self, session: Session):
        self.session = session

    def get_patient_demographics(self) -> Dict[str, Any]:
        total = self.session.query(PatientIdentity).count()
        if total == 0:
            return {"total_patients": 0, "sex_distribution": {}, "age_distribution": {}}

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
        edu_rows = self.session.query(EducationLevel).all()
        for r in edu_rows:
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
        eth_rows = self.session.query(Ethnicity).all()
        for r in eth_rows:
            eth_labels[r.ethnicity_id] = r.description
        eth_dist = {eth_labels.get(row.eth_id, f"ID {row.eth_id}"): row.count for row in eth_query}

        return {
            "total_patients": total,
            "sex_distribution": sex_dist,
            "age_distribution": age_dist,
            "education_level_distribution": edu_dist,
            "ethnicity_distribution": eth_dist,
        }

    def get_consultation_metrics(
        self,
        days: int = 30,
    ) -> Dict[str, Any]:
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

    def get_scale_trends(self, scale_name: str, days: int = 90) -> Dict[str, Any]:
        scale = self.session.query(AssessmentScale).filter(
            AssessmentScale.scale_name == scale_name
        ).first()
        if not scale:
            return {"scale_name": scale_name, "error": "Scale not found"}

        since = datetime.now(timezone.utc) - timedelta(days=days)
        sql = text("""
            SELECT c.consultation_date, sum(sr.response_value) as total_score
            FROM clinical.scale_responses sr
            JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
            JOIN clinical.clinical_consultation c ON sr.consultation_uuid = c.consultation_uuid
            WHERE sq.scale_id = :scale_id AND c.consultation_date >= :since
            GROUP BY c.consultation_uuid, c.consultation_date
            ORDER BY c.consultation_date
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={
            "scale_id": scale.scale_id, "since": since,
        })
        if df.empty:
            return {"scale_name": scale_name, "total_records": 0, "trend": {}}

        df["consultation_date"] = pd.to_datetime(df["consultation_date"])
        stats = df["total_score"].describe().to_dict()
        df = df.set_index("consultation_date")
        df["ma3"] = df["total_score"].rolling(3, min_periods=1).mean().round(2)

        return {
            "scale_name": scale_name,
            "total_records": len(df),
            "statistics": {k: round(v, 2) for k, v in stats.items()},
            "trend": {
                "scores": df["total_score"].to_dict(),
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

    def get_overview_stats(self) -> Dict[str, Any]:
        from app.services.alerts_service import AlertsService
        general = self.get_general_stats()
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
