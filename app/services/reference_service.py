from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import SexType, GenderIdentity, EducationLevel, Ethnicity


class ReferenceService:
    def __init__(self, db: Session):
        self.db = db

    def list_sex_types(self) -> List[SexType]:
        return self.db.query(SexType).all()

    def get_sex_type(self, sex_type_id: int) -> Optional[SexType]:
        return self.db.query(SexType).filter(SexType.sex_type_id == sex_type_id).first()

    def create_sex_type(self, code: str, description: str) -> SexType:
        sex_type = SexType(code=code, description=description)
        self.db.add(sex_type)
        self.db.commit()
        self.db.refresh(sex_type)
        return sex_type

    def list_gender_identities(self) -> List[GenderIdentity]:
        return self.db.query(GenderIdentity).all()

    def get_gender_identity(self, gender_identity_id: int) -> Optional[GenderIdentity]:
        return self.db.query(GenderIdentity).filter(
            GenderIdentity.gender_identity_id == gender_identity_id
        ).first()

    def create_gender_identity(self, code: str, description: str) -> GenderIdentity:
        identity = GenderIdentity(code=code, description=description)
        self.db.add(identity)
        self.db.commit()
        self.db.refresh(identity)
        return identity

    def list_education_levels(self) -> List[EducationLevel]:
        return self.db.query(EducationLevel).all()

    def get_education_level(self, education_level_id: int) -> Optional[EducationLevel]:
        return self.db.query(EducationLevel).filter(
            EducationLevel.education_level_id == education_level_id
        ).first()

    def create_education_level(self, code: str, description: str) -> EducationLevel:
        level = EducationLevel(code=code, description=description)
        self.db.add(level)
        self.db.commit()
        self.db.refresh(level)
        return level

    def list_ethnicities(self) -> List[Ethnicity]:
        return self.db.query(Ethnicity).all()

    def get_ethnicity(self, ethnicity_id: int) -> Optional[Ethnicity]:
        return self.db.query(Ethnicity).filter(
            Ethnicity.ethnicity_id == ethnicity_id
        ).first()

    def create_ethnicity(self, code: str, description: str) -> Ethnicity:
        ethnicity = Ethnicity(code=code, description=description)
        self.db.add(ethnicity)
        self.db.commit()
        self.db.refresh(ethnicity)
        return ethnicity
