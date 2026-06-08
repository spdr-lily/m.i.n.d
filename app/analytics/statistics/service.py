from typing import Dict, Any
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.base import (
    PatientIdentity, PatientProfile, AssessmentScale,
)

AGE_BINS = [0, 18, 35, 50, 65, 200]
AGE_LABELS = ["0-18", "19-35", "36-50", "51-65", "65+"]


class StatisticsService:
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

        return {
            "total_patients": total,
            "sex_distribution": sex_dist,
            "age_distribution": age_dist,
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
