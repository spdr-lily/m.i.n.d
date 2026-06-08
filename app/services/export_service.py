from typing import Dict, List, Optional
from uuid import UUID
import csv
import io
from sqlalchemy.orm import Session, joinedload
from app.models.base import (
    PatientIdentity, PatientProfile, ClinicalConsultation,
    SymptomObservation, DiagnosticInference, ClinicalNote,
    Prescription, PrescriptionItem, Medication,
)
from fpdf import FPDF


class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self._consultations: List[ClinicalConsultation] = []
        self._identity: Optional[PatientIdentity] = None
        self._profile: Optional[PatientProfile] = None

    def _load(self, patient_uuid: UUID) -> None:
        self._identity = self.db.query(PatientIdentity).filter(
            PatientIdentity.patient_uuid == patient_uuid
        ).first()
        if not self._identity:
            raise ValueError("Patient not found")

        self._profile = self.db.query(PatientProfile).filter(
            PatientProfile.patient_uuid == patient_uuid
        ).first()

        self._consultations = self.db.query(ClinicalConsultation).filter(
            ClinicalConsultation.profile_uuid == self._profile.profile_uuid
        ).options(
            joinedload(ClinicalConsultation.healthcare_professional),
            joinedload(ClinicalConsultation.symptom_observations).joinedload(SymptomObservation.symptom),
            joinedload(ClinicalConsultation.diagnostic_inferences).joinedload(DiagnosticInference.disorder),
            joinedload(ClinicalConsultation.clinical_note),
            joinedload(ClinicalConsultation.prescriptions).joinedload(Prescription.items).joinedload(PrescriptionItem.medication),
        ).order_by(ClinicalConsultation.consultation_date).all()

    def _sexo(self) -> str:
        if not self._profile:
            return ""
        st = self._profile.sex_type
        return st.description if st else (str(self._profile.sex_type_id) if self._profile.sex_type_id else "")

    def export_patient_csv(self, patient_uuid: UUID) -> str:
        self._load(patient_uuid)
        id_, profile, consultations = self._identity, self._profile, self._consultations

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Paciente", "Data Nascimento", "Sexo", "Ocupação",
            "Data Consulta", "Profissional", "Observações",
            "Sintomas", "Escalas", "Inferências Diagnósticas",
            "Queixa Principal", "Avaliação Clínica", "Plano Terapêutico",
            "Prescrições",
        ])

        for c in consultations:
            writer.writerow(self._row(c))

        return output.getvalue()

    def export_patient_pdf(self, patient_uuid: UUID) -> bytes:
        self._load(patient_uuid)
        id_, profile, consultations = self._identity, self._profile, self._consultations

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Prontuario Clinico - {id_.full_name}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)

        pdf.set_font("Helvetica", "", 10)
        sexo = self._sexo()
        nasc = profile.birth_date.isoformat() if profile and profile.birth_date else "-"
        ocup = profile.occupation if profile else "-"
        pdf.cell(0, 6, f"Nascimento: {nasc}  |  Sexo: {sexo}  |  Ocupacao: {ocup}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        for i, c in enumerate(consultations, 1):
            if pdf.y > 230:
                pdf.add_page()
            row = self._row(c)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, f"Consulta #{i} - {c.consultation_date.isoformat() if c.consultation_date else '-'}",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)

            labels = [
                ("Profissional", 4),
                ("Observacoes", 5),
                ("Queixa Principal", 6),
                ("Avaliacao Clinica", 7),
                ("Plano Terapeutico", 8),
                ("Sintomas", 9),
                ("Escalas", 10),
                ("Inferencias", 11),
                ("Prescricoes", 13),
            ]
            for label, idx in labels:
                val = row[idx]
                if val:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(0, 5, label + ":", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 9)
                    pdf.multi_cell(0, 5, str(val))
            pdf.ln(3)

        return pdf.output()

    def _row(self, c: ClinicalConsultation) -> List[str]:
        symptoms = "; ".join(
            f"{s.symptom.symptom_name if s.symptom else '?'} "
            f"({s.intensity or 0}%, {s.frequency or 'N/I'})"
            for s in (c.symptom_observations or [])
        )

        scales_raw: Dict[int, List[float]] = {}
        for sr in c.scale_responses or []:
            if sr.response_value is not None and sr.scale_question:
                sid = sr.scale_question.scale_id
                scales_raw.setdefault(sid, []).append(float(sr.response_value))
        scale_scores = "; ".join(
            f"Scale-{sid}: {sum(vals):.1f}" for sid, vals in scales_raw.items()
        )

        inferences = "; ".join(
            f"{di.disorder.disorder_name if di.disorder else '?'} "
            f"({float(di.inference_probability) * 100:.1f}%)"
            for di in (c.diagnostic_inferences or [])
        )

        prescriptions = "; ".join(
            f"{item.medication.name if item.medication else '?'} "
            f"{item.dosage} {item.frequency}"
            for p in (c.prescriptions or [])
            for item in (p.items or [])
        )

        note = c.clinical_note
        return [
            self._identity.full_name if self._identity else "",
            self._profile.birth_date.isoformat() if self._profile and self._profile.birth_date else "",
            self._sexo(),
            self._profile.occupation if self._profile else "",
            c.consultation_date.isoformat() if c.consultation_date else "",
            c.healthcare_professional.full_name if c.healthcare_professional else "",
            c.consultation_notes or "",
            symptoms,
            scale_scores,
            inferences,
            note.chief_complaint if note else "",
            note.clinical_assessment if note else "",
            note.treatment_plan if note else "",
            prescriptions,
        ]
