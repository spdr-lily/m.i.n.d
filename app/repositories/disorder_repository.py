from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship, CriteriaGroup, CriteriaRule, CriteriaThreshold, ICD11Code, ICD11Exclusion, ICD11Differential


class DisorderRepository:
    def __init__(self, session: Session):
        self.session = session

    # Symptoms
    def create_symptom(self, symptom_name: str, symptom_description: Optional[str] = None) -> Symptom:
        symptom = Symptom(symptom_name=symptom_name, symptom_description=symptom_description)
        self.session.add(symptom)
        self.session.flush()
        self.session.refresh(symptom)
        return symptom

    def get_symptom(self, symptom_id: int) -> Optional[Symptom]:
        return self.session.query(Symptom).filter(Symptom.symptom_id == symptom_id).first()

    def list_symptoms(self, skip: int = 0, limit: int = 100) -> List[Symptom]:
        return self.session.query(Symptom).offset(skip).limit(limit).all()

    def update_symptom(self, symptom_id: int, **updates) -> Optional[Symptom]:
        symptom = self.get_symptom(symptom_id)
        if symptom:
            for key, value in updates.items():
                if value is not None and hasattr(symptom, key):
                    setattr(symptom, key, value)
            self.session.flush()
            self.session.refresh(symptom)
        return symptom

    def delete_symptom(self, symptom_id: int) -> bool:
        symptom = self.get_symptom(symptom_id)
        if symptom:
            self.session.delete(symptom)
            self.session.flush()
            return True
        return False

    # Disorders
    def create_disorder(
        self,
        disorder_name: str,
        cid_code: Optional[str] = None,
        dsm_code: Optional[str] = None,
        disorder_description: Optional[str] = None
    ) -> Disorder:
        disorder = Disorder(
            disorder_name=disorder_name,
            cid_code=cid_code,
            dsm_code=dsm_code,
            disorder_description=disorder_description
        )
        self.session.add(disorder)
        self.session.flush()
        self.session.refresh(disorder)
        return disorder

    def get_disorder(self, disorder_id: int) -> Optional[Disorder]:
        return self.session.query(Disorder).filter(Disorder.disorder_id == disorder_id).first()

    def list_disorders(self, skip: int = 0, limit: int = 100) -> List[Disorder]:
        return self.session.query(Disorder).offset(skip).limit(limit).all()

    def update_disorder(self, disorder_id: int, **updates) -> Optional[Disorder]:
        disorder = self.get_disorder(disorder_id)
        if disorder:
            for key, value in updates.items():
                if value is not None and hasattr(disorder, key):
                    setattr(disorder, key, value)
            self.session.flush()
            self.session.refresh(disorder)
        return disorder

    def delete_disorder(self, disorder_id: int) -> bool:
        disorder = self.get_disorder(disorder_id)
        if disorder:
            self.session.delete(disorder)
            self.session.flush()
            return True
        return False

    # Diagnostic Criteria
    def create_criteria(
        self,
        disorder_id: int,
        symptom_id: int,
        required_presence: bool = True,
        minimum_duration_days: Optional[int] = None,
        clinical_notes: Optional[str] = None
    ) -> DiagnosticCriteria:
        criteria = DiagnosticCriteria(
            disorder_id=disorder_id,
            symptom_id=symptom_id,
            required_presence=required_presence,
            minimum_duration_days=minimum_duration_days,
            clinical_notes=clinical_notes
        )
        self.session.add(criteria)
        self.session.flush()
        self.session.refresh(criteria)
        return criteria

    def list_criteria_by_disorder(self, disorder_id: int) -> List[DiagnosticCriteria]:
        return self.session.query(DiagnosticCriteria).filter(
            DiagnosticCriteria.disorder_id == disorder_id
        ).all()

    def delete_criteria(self, criteria_id: int) -> bool:
        criteria = self.session.query(DiagnosticCriteria).filter(
            DiagnosticCriteria.criteria_id == criteria_id
        ).first()
        if criteria:
            self.session.delete(criteria)
            self.session.flush()
            return True
        return False

    # Diagnosis Relationships
    def create_relationship(
        self,
        source_disorder_id: int,
        target_disorder_id: int,
        relationship_type: Optional[str] = None,
        relationship_weight: Optional[float] = None,
        clinical_description: Optional[str] = None
    ) -> DiagnosisRelationship:
        rel = DiagnosisRelationship(
            source_disorder_id=source_disorder_id,
            target_disorder_id=target_disorder_id,
            relationship_type=relationship_type,
            relationship_weight=relationship_weight,
            clinical_description=clinical_description
        )
        self.session.add(rel)
        self.session.flush()
        self.session.refresh(rel)
        return rel

    def list_relationships(self, disorder_id: Optional[int] = None) -> List[DiagnosisRelationship]:
        query = self.session.query(DiagnosisRelationship)
        if disorder_id is not None:
            query = query.filter(
                (DiagnosisRelationship.source_disorder_id == disorder_id) |
                (DiagnosisRelationship.target_disorder_id == disorder_id)
            )
        return query.all()

    # Criteria Groups
    def list_criteria_groups(self, disorder_id: int) -> List[CriteriaGroup]:
        return self.session.query(CriteriaGroup).filter(
            CriteriaGroup.disorder_id == disorder_id
        ).all()

    def create_criteria_group(
        self, disorder_id: int, group_label: str, description: Optional[str] = None, sort_order: int = 0
    ) -> CriteriaGroup:
        group = CriteriaGroup(
            disorder_id=disorder_id, group_label=group_label,
            description=description, sort_order=sort_order,
        )
        self.session.add(group)
        self.session.flush()
        self.session.refresh(group)
        return group

    def delete_criteria_group(self, group_id: int) -> bool:
        group = self.session.query(CriteriaGroup).filter(CriteriaGroup.group_id == group_id).first()
        if group:
            self.session.delete(group)
            self.session.flush()
            return True
        return False

    # Criteria Rules
    def create_criteria_rule(
        self, group_id: int, required_count: int, total_count: int,
        min_duration_days: Optional[int] = None, severity_threshold: Optional[float] = None,
    ) -> CriteriaRule:
        rule = CriteriaRule(
            group_id=group_id, required_count=required_count, total_count=total_count,
            min_duration_days=min_duration_days, severity_threshold=severity_threshold,
        )
        self.session.add(rule)
        self.session.flush()
        self.session.refresh(rule)
        return rule

    # Criteria Thresholds
    def list_criteria_thresholds(self, disorder_id: int) -> List[CriteriaThreshold]:
        return self.session.query(CriteriaThreshold).filter(
            CriteriaThreshold.disorder_id == disorder_id
        ).all()

    def create_criteria_threshold(
        self, disorder_id: int, severity_level: str,
        min_criteria_met: Optional[int] = None, min_duration_days: Optional[int] = None,
        min_intensity: Optional[float] = None, description: Optional[str] = None,
    ) -> CriteriaThreshold:
        threshold = CriteriaThreshold(
            disorder_id=disorder_id, severity_level=severity_level,
            min_criteria_met=min_criteria_met, min_duration_days=min_duration_days,
            min_intensity=min_intensity, description=description,
        )
        self.session.add(threshold)
        self.session.flush()
        self.session.refresh(threshold)
        return threshold

    # ICD-11
    def create_icd11_code(
        self, disorder_id: int, icd11_code: str, icd11_title: Optional[str] = None,
        chapter: Optional[str] = None, chapter_code: Optional[str] = None,
        who_url: Optional[str] = None, clinical_description: Optional[str] = None,
        diagnostic_requirements: Optional[str] = None,
    ) -> ICD11Code:
        code = ICD11Code(
            disorder_id=disorder_id, icd11_code=icd11_code, icd11_title=icd11_title,
            chapter=chapter, chapter_code=chapter_code, who_url=who_url,
            clinical_description=clinical_description,
            diagnostic_requirements=diagnostic_requirements,
        )
        self.session.add(code)
        self.session.flush()
        self.session.refresh(code)
        return code

    def list_icd11_codes(self, disorder_id: Optional[int] = None) -> List[ICD11Code]:
        query = self.session.query(ICD11Code)
        if disorder_id is not None:
            query = query.filter(ICD11Code.disorder_id == disorder_id)
        return query.all()

    def get_icd11_code(self, code_id: int) -> Optional[ICD11Code]:
        return self.session.query(ICD11Code).filter(ICD11Code.code_id == code_id).first()

    def add_icd11_exclusion(
        self, code_id: int, excluded_code: str,
        excluded_title: Optional[str] = None, reason: Optional[str] = None,
    ) -> ICD11Exclusion:
        excl = ICD11Exclusion(
            code_id=code_id, excluded_code=excluded_code,
            excluded_title=excluded_title, reason=reason,
        )
        self.session.add(excl)
        self.session.flush()
        self.session.refresh(excl)
        return excl

    def add_icd11_differential(
        self, code_id: int, differential_code: str,
        differential_title: Optional[str] = None,
        distinguishing_features: Optional[str] = None,
    ) -> ICD11Differential:
        diff = ICD11Differential(
            code_id=code_id, differential_code=differential_code,
            differential_title=differential_title,
            distinguishing_features=distinguishing_features,
        )
        self.session.add(diff)
        self.session.flush()
        self.session.refresh(diff)
        return diff
