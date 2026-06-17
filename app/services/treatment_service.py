from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sa_func, case as sa_case
from app.models.base import (
    DisorderMedication, TreatmentOutcome, Medication, Disorder, PatientProfile
)


class TreatmentService:
    def __init__(self, db: Session):
        self.db = db

    # --- Disorder-Medication associations ---

    def list_associations(
        self, disorder_id: Optional[int] = None, medication_id: Optional[int] = None
    ) -> List[DisorderMedication]:
        q = self.db.query(DisorderMedication).options(
            joinedload(DisorderMedication.medication),
            joinedload(DisorderMedication.disorder)
        )
        if disorder_id:
            q = q.filter(DisorderMedication.disorder_id == disorder_id)
        if medication_id:
            q = q.filter(DisorderMedication.medication_id == medication_id)
        return q.order_by(
            DisorderMedication.line_of_treatment,
            DisorderMedication.success_rate.desc().nullslast()
        ).all()

    def get_association(self, dm_id: int) -> Optional[DisorderMedication]:
        return self.db.query(DisorderMedication).options(
            joinedload(DisorderMedication.medication),
            joinedload(DisorderMedication.disorder)
        ).filter(DisorderMedication.dm_id == dm_id).first()

    def create_association(self, data: dict) -> DisorderMedication:
        dm = DisorderMedication(**data)
        self.db.add(dm)
        self.db.flush()
        return dm

    def update_association(self, dm_id: int, data: dict) -> Optional[DisorderMedication]:
        dm = self.get_association(dm_id)
        if not dm:
            return None
        for k, v in data.items():
            if v is not None:
                setattr(dm, k, v)
        self.db.flush()
        return dm

    def delete_association(self, dm_id: int) -> bool:
        dm = self.db.query(DisorderMedication).filter(DisorderMedication.dm_id == dm_id).first()
        if not dm:
            return False
        self.db.delete(dm)
        self.db.flush()
        return True

    # --- Treatment outcomes ---

    def list_outcomes(
        self, patient_uuid: Optional[UUID] = None, medication_id: Optional[int] = None,
        disorder_id: Optional[int] = None
    ) -> List[TreatmentOutcome]:
        q = self.db.query(TreatmentOutcome).options(
            joinedload(TreatmentOutcome.medication),
            joinedload(TreatmentOutcome.disorder)
        )
        if patient_uuid:
            q = q.filter(TreatmentOutcome.patient_uuid == patient_uuid)
        if medication_id:
            q = q.filter(TreatmentOutcome.medication_id == medication_id)
        if disorder_id:
            q = q.filter(TreatmentOutcome.disorder_id == disorder_id)
        return q.order_by(TreatmentOutcome.start_date.desc()).all()

    def get_outcome(self, outcome_uuid: UUID) -> Optional[TreatmentOutcome]:
        return self.db.query(TreatmentOutcome).options(
            joinedload(TreatmentOutcome.medication),
            joinedload(TreatmentOutcome.disorder)
        ).filter(TreatmentOutcome.outcome_uuid == outcome_uuid).first()

    def create_outcome(self, data: dict) -> TreatmentOutcome:
        outcome = TreatmentOutcome(**data)
        self.db.add(outcome)
        self.db.flush()
        return outcome

    def delete_outcome(self, outcome_uuid: UUID) -> bool:
        outcome = self.db.query(TreatmentOutcome).filter(
            TreatmentOutcome.outcome_uuid == outcome_uuid
        ).first()
        if not outcome:
            return False
        self.db.delete(outcome)
        self.db.flush()
        return True

    def get_disorder_outcome_stats(self, disorder_id: int, medication_id: Optional[int] = None) -> List[Dict]:
        q = self.db.query(
            TreatmentOutcome.medication_id,
            Medication.name.label("medication_name"),
            sa_func.count(TreatmentOutcome.outcome_uuid).label("total_cases"),
            sa_func.sum(
                sa_case((TreatmentOutcome.outcome.in_(["improved", "remission"]), 1), else_=0)
            ).label("success_count"),
            sa_func.sum(
                sa_case((TreatmentOutcome.outcome == "worsened", 1), else_=0)
            ).label("worsened_count"),
            sa_func.sum(
                sa_case((TreatmentOutcome.outcome == "discontinued", 1), else_=0)
            ).label("discontinued_count"),
            sa_func.avg(TreatmentOutcome.response_weeks).label("avg_response_weeks"),
        ).join(Medication, TreatmentOutcome.medication_id == Medication.medication_id)
        q = q.filter(TreatmentOutcome.disorder_id == disorder_id)
        if medication_id:
            q = q.filter(TreatmentOutcome.medication_id == medication_id)
        q = q.group_by(TreatmentOutcome.medication_id, Medication.name)
        rows = q.all()
        result = []
        for row in rows:
            total = row.total_cases or 0
            success = row.success_count or 0
            result.append({
                "medication_id": row.medication_id,
                "medication_name": row.medication_name,
                "total_cases": total,
                "success_rate": round(success / total, 4) if total > 0 else 0,
                "worsened_count": row.worsened_count or 0,
                "discontinued_count": row.discontinued_count or 0,
                "avg_response_weeks": round(float(row.avg_response_weeks), 2) if row.avg_response_weeks else None,
            })
        return result


class TreatmentMLPredictor:
    def __init__(self, db: Session):
        self.db = db
        self.service = TreatmentService(db)

    def predict_efficacy(
        self, patient_uuid: UUID, disorder_id: int, medication_ids: List[int]
    ) -> List[dict]:
        predictions = []
        disorder = self.db.query(Disorder).filter(Disorder.disorder_id == disorder_id).first()
        disorder_name = disorder.disorder_name if disorder else "Desconhecido"
        patient = self.db.query(PatientProfile).filter(
            PatientProfile.profile_uuid == patient_uuid
        ).first()

        for med_id in medication_ids:
            med = self.db.query(Medication).filter(Medication.medication_id == med_id).first()
            if not med:
                continue

            success_prob, resp_weeks, rec_strength = self._predict_single(
                patient, disorder_id, med_id, med
            )

            predictions.append({
                "medication_id": med_id,
                "medication_name": med.name,
                "success_probability": round(success_prob, 4),
                "expected_response_weeks": round(resp_weeks, 1) if resp_weeks else None,
                "recommendation_strength": rec_strength,
            })

        return predictions

    def _predict_single(self, patient, disorder_id: int, med_id: int, med) -> tuple:
        assoc = self.db.query(DisorderMedication).filter(
            DisorderMedication.medication_id == med_id,
            DisorderMedication.disorder_id == disorder_id
        ).first()

        outcome_stats = self.service.get_disorder_outcome_stats(disorder_id, med_id)
        stats = outcome_stats[0] if outcome_stats else {}

        literature_sr = float(assoc.success_rate) if assoc and assoc.success_rate else 0.5
        literature_fr = float(assoc.failure_rate) if assoc and assoc.failure_rate else 0.2
        literature_rw = float(assoc.avg_response_weeks) if assoc and assoc.avg_response_weeks else None
        rec_strength = assoc.recommendation_strength if assoc else "C"

        real_sr = stats.get("success_rate", 0)
        n_real = stats.get("total_cases", 0)

        if n_real >= 3:
            blended = literature_sr * 0.4 + real_sr * 0.6
        elif n_real > 0:
            blended = literature_sr * 0.7 + real_sr * 0.3
        else:
            blended = literature_sr

        if stats.get("avg_response_weeks"):
            resp_weeks = float(stats["avg_response_weeks"])
        elif literature_rw:
            resp_weeks = literature_rw
        else:
            resp_weeks = 4.0

        return blended, resp_weeks, rec_strength
