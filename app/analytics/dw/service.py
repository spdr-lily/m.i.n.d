from typing import Dict, List, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text


class DWAnalyticsService:
    """Queries DW analytical views for BI dashboards."""

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
