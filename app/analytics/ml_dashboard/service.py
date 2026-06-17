from typing import Dict, List
from sqlalchemy import func as sa_func, text
from sqlalchemy.orm import Session

from app.models.base import (
    ScaleResponse, ScaleQuestion, TreatmentOutcome, DisorderMedication,
)


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
                    sa_func.sum(ScaleResponse.response_value).label("factor_total"),
                )
                .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
                .filter(
                    ScaleQuestion.question_text.like(f"{prefix}%"),
                    ScaleResponse.response_value.isnot(None),
                )
                .group_by(ScaleResponse.consultation_uuid)
                .subquery()
            )
            avg = self.db.query(sa_func.avg(sq.c.factor_total)).scalar()
            return round(float(avg), 2) if avg else 0.0

        bfp = {}
        for f in bfp_factors:
            bfp[f] = _factor_avg(f"{f} -")

        dt12 = {}
        for s in dt12_subscales:
            dt12[s] = _factor_avg(f"{s} -")

        hexaco = {}
        for f in hexaco_factors:
            hexaco[f] = _factor_avg(f"{f} -")

        bis11 = {}
        for s in bis11_subscales:
            bis11[s] = _factor_avg(f"{s} -")

        tas20 = {}
        for s in tas20_subscales:
            tas20[s] = _factor_avg(f"{s} -")

        rses = _factor_avg("Autoestima -")

        total_with_data = (
            self.db.query(sa_func.count(sa_func.distinct(ScaleResponse.consultation_uuid)))
            .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
            .filter(ScaleQuestion.question_text.like("Abertura -%"))
            .scalar()
        ) or 0

        return {
            "bfp_averages": bfp,
            "dt12_averages": dt12,
            "hexaco_averages": hexaco,
            "bis11_averages": bis11,
            "tas20_averages": tas20,
            "rses_averages": {"Autoestima": rses},
            "total_assessments": total_with_data,
        }

    def get_efficacy_summary(self) -> dict:
        total_outcomes = self.db.query(sa_func.count(TreatmentOutcome.outcome_uuid)).scalar() or 0
        total_associations = self.db.query(sa_func.count(DisorderMedication.dm_id)).scalar() or 0

        outcome_stats = (
            self.db.query(
                TreatmentOutcome.outcome,
                sa_func.count(TreatmentOutcome.outcome_uuid),
            )
            .group_by(TreatmentOutcome.outcome)
            .all()
        )
        outcome_dist = {row[0]: row[1] for row in outcome_stats}

        line_stats = (
            self.db.query(
                DisorderMedication.line_of_treatment,
                sa_func.avg(DisorderMedication.success_rate),
                sa_func.count(DisorderMedication.dm_id),
            )
            .group_by(DisorderMedication.line_of_treatment)
            .all()
        )
        by_line = []
        for row in line_stats:
            line = row[0]
            by_line.append({
                "line": line,
                "avg_success_rate": round(float(row[1]), 3) if row[1] else 0,
                "count": row[2],
            })

        return {
            "total_outcomes": total_outcomes,
            "total_associations": total_associations,
            "outcome_distribution": outcome_dist,
            "by_line_of_treatment": by_line,
        }

    def get_models_info(self) -> List[dict]:
        return [
            {
                "name": "Big Five (RF)",
                "objective": "personality_bfp",
                "algorithm": "random_forest",
                "stage": "Production",
                "r2": 0.468,
                "mae": 2.10,
                "description": "Prediz 5 fatores BFP a partir de escalas clínicas",
            },
            {
                "name": "Big Five (XGB)",
                "objective": "personality_bfp",
                "algorithm": "xgboost",
                "stage": "Production",
                "r2": 0.366,
                "mae": 2.25,
                "description": "Prediz 5 fatores BFP via XGBoost",
            },
            {
                "name": "Tríade Sombria (RF)",
                "objective": "personality_dt12",
                "algorithm": "random_forest",
                "stage": "Production",
                "r2": 0.499,
                "mae": 1.62,
                "description": "Prediz 3 subescalas DT-12 a partir de escalas clínicas",
            },
            {
                "name": "Tríade Sombria (XGB)",
                "objective": "personality_dt12",
                "algorithm": "xgboost",
                "stage": "Production",
                "r2": 0.176,
                "mae": 1.89,
                "description": "Prediz 3 subescalas DT-12 via XGBoost",
            },
        ]

    def get_ml_dashboard(self) -> dict:
        return {
            "personality": self.get_personality_averages(),
            "efficacy": self.get_efficacy_summary(),
            "models": self.get_models_info(),
        }
