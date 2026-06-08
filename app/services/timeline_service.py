from typing import List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.base import (
    PatientIdentity, PatientProfile, ClinicalConsultation,
    ClinicalEpisode, SymptomObservation, ScaleResponse,
    DiagnosticInference, ClinicalNote, Prescription,
    PrescriptionItem, Medication, HealthcareProfessional,
    AssessmentScale, ScaleQuestion, Disorder, Symptom,
)
from app.schemas.timeline import (
    TimelineResponse, TimelineEvent,
    ConsultationTimelineEvent, EpisodeTimelineEvent,
    SymptomObservationBrief, DiagnosticInferenceBrief,
    PrescriptionBrief, ClinicalNoteBrief, ScaleScoreBrief,
)


class TimelineService:
    def __init__(self, db: Session):
        self.db = db

    def get_patient_timeline(self, patient_uuid: UUID) -> TimelineResponse:
        identity = self.db.query(PatientIdentity).filter(
            PatientIdentity.patient_uuid == patient_uuid
        ).first()
        if not identity:
            raise ValueError("Patient not found")

        profile = self.db.query(PatientProfile).filter(
            PatientProfile.patient_uuid == patient_uuid
        ).first()
        if not profile:
            raise ValueError("Patient profile not found")

        consultations = self._get_consultations(profile.profile_uuid)
        episodes = self.db.query(ClinicalEpisode).filter(
            ClinicalEpisode.profile_uuid == profile.profile_uuid
        ).all()

        events: list[TimelineEvent] = []

        for c in consultations:
            symptoms = []
            for obs in c.symptom_observations or []:
                symptoms.append(SymptomObservationBrief(
                    symptom_name=obs.symptom.symptom_name if obs.symptom else "?",
                    intensity=float(obs.intensity) if obs.intensity else None,
                    frequency=obs.frequency,
                ))

            scale_scores = self._compute_scale_scores(c.scale_responses or [])

            inferences = []
            for di in c.diagnostic_inferences or []:
                inferences.append(DiagnosticInferenceBrief(
                    disorder_name=di.disorder.disorder_name if di.disorder else "?",
                    inference_probability=float(di.inference_probability),
                ))

            prescriptions = []
            for p in c.prescriptions or []:
                for item in p.items or []:
                    prescriptions.append(PrescriptionBrief(
                        medication_name=item.medication.name if item.medication else "?",
                        dosage=item.dosage,
                        frequency=item.frequency,
                        route=item.route,
                        duration_days=item.duration_days,
                    ))

            clinical_note = None
            if c.clinical_note:
                clinical_note = ClinicalNoteBrief(
                    chief_complaint=c.clinical_note.chief_complaint,
                    clinical_assessment=c.clinical_note.clinical_assessment,
                    treatment_plan=c.clinical_note.treatment_plan,
                )

            professional_name = c.healthcare_professional.full_name if c.healthcare_professional else None

            events.append(TimelineEvent(
                date=c.consultation_date,
                event_type="consultation",
                consultation=ConsultationTimelineEvent(
                    consultation_uuid=c.consultation_uuid,
                    consultation_date=c.consultation_date,
                    professional_name=professional_name,
                    consultation_notes=c.consultation_notes,
                    symptoms=symptoms,
                    scale_scores=scale_scores,
                    inferences=inferences,
                    prescriptions=prescriptions,
                    clinical_note=clinical_note,
                ),
            ))

        for e in episodes:
            events.append(TimelineEvent(
                date=e.episode_start or e.created_at,
                event_type="episode",
                episode=EpisodeTimelineEvent(
                    episode_uuid=e.episode_uuid,
                    episode_start=e.episode_start,
                    episode_end=e.episode_end,
                    episode_type=e.episode_type,
                    clinical_description=e.clinical_description,
                ),
            ))

        events.sort(key=lambda ev: (ev.date or datetime.min))
        return TimelineResponse(
            patient_uuid=patient_uuid,
            patient_name=identity.full_name,
            events=events,
        )

    def _get_consultations(self, profile_uuid: UUID) -> list[ClinicalConsultation]:
        return self.db.query(ClinicalConsultation).filter(
            ClinicalConsultation.profile_uuid == profile_uuid
        ).options(
            joinedload(ClinicalConsultation.healthcare_professional),
            joinedload(ClinicalConsultation.symptom_observations).joinedload(SymptomObservation.symptom),
            joinedload(ClinicalConsultation.scale_responses),
            joinedload(ClinicalConsultation.diagnostic_inferences).joinedload(DiagnosticInference.disorder),
            joinedload(ClinicalConsultation.clinical_note),
            joinedload(ClinicalConsultation.prescriptions).joinedload(Prescription.items).joinedload(PrescriptionItem.medication),
        ).order_by(ClinicalConsultation.consultation_date.desc()).all()

    def _compute_scale_scores(self, scale_responses: list[ScaleResponse]) -> list[ScaleScoreBrief]:
        if not scale_responses:
            return []

        scores: dict[str, list[float]] = {}
        for sr in scale_responses:
            if sr.response_value is None:
                continue
            q = self.db.query(ScaleQuestion).filter(
                ScaleQuestion.question_id == sr.question_id
            ).first()
            if not q:
                continue
            scale = self.db.query(AssessmentScale).filter(
                AssessmentScale.scale_id == q.scale_id
            ).first()
            if not scale:
                continue
            scores.setdefault(scale.scale_name, []).append(float(sr.response_value))

        result = []
        for scale_name, values in scores.items():
            result.append(ScaleScoreBrief(
                scale_name=scale_name,
                total_score=sum(values),
            ))
        return result
