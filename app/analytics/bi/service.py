from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.base import (
    AssessmentScale, DiagnosticInference, Disorder,
)


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
