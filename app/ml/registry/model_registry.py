"""Model versioning registry backed by SQLAlchemy + MLflow."""
import json
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base, Session, relationship
import enum

RegistryBase = declarative_base()


class ModelStage(str, enum.Enum):
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ObjectiveType(str, enum.Enum):
    DIAGNOSIS = "diagnosis"
    RELAPSE = "relapse"
    SUICIDE_RISK = "suicide_risk"
    THERAPEUTIC_RESPONSE = "therapeutic_response"


class AlgorithmType(str, enum.Enum):
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"


class RegisteredModel(RegistryBase):
    __tablename__ = "registered_models"
    __table_args__ = {"schema": "ml"}

    model_id = Column(Integer, primary_key=True)
    model_uuid = Column(PostgresUUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    objective = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False)
    model_name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")


class ModelVersion(RegistryBase):
    __tablename__ = "model_versions"
    __table_args__ = {"schema": "ml"}

    version_id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("ml.registered_models.model_id"), nullable=False)
    version = Column(Integer, nullable=False)
    mlflow_run_id = Column(String(100))
    mlflow_model_uri = Column(String(500))
    stage = Column(String(50), default=ModelStage.STAGING.value)
    metrics = Column(Text)
    params = Column(Text)
    feature_list = Column(Text)
    feature_count = Column(Integer)
    train_size = Column(Integer)
    test_size = Column(Integer)
    is_baseline = Column(Boolean, default=False)
    artifact_path = Column(String(500))
    dvc_hash = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("RegisteredModel", back_populates="versions")


class ModelRegistry:

    def __init__(self, engine):
        RegistryBase.metadata.create_all(bind=engine)
        self.session = Session(bind=engine)

    def register_model(
        self, objective: str, algorithm: str, description: str = ""
    ) -> RegisteredModel:
        model_name = f"{objective}_{algorithm}"
        existing = self.session.query(RegisteredModel).filter_by(
            objective=objective, algorithm=algorithm
        ).first()
        if existing:
            return existing

        rm = RegisteredModel(
            model_uuid=uuid4(),
            objective=objective,
            algorithm=algorithm,
            model_name=model_name,
            description=description,
        )
        self.session.add(rm)
        self.session.commit()
        return rm

    def create_version(
        self,
        model_id: int,
        mlflow_run_id: str,
        mlflow_model_uri: str,
        metrics: dict,
        params: dict,
        feature_list: list,
        train_size: int,
        test_size: int,
        artifact_path: str = "",
        dvc_hash: str = "",
        stage: str = "staging",
        is_baseline: bool = False,
    ) -> ModelVersion:
        last = self.session.query(ModelVersion).filter_by(model_id=model_id).order_by(
            ModelVersion.version.desc()
        ).first()
        next_ver = (last.version + 1) if last else 1

        mv = ModelVersion(
            model_id=model_id,
            version=next_ver,
            mlflow_run_id=mlflow_run_id,
            mlflow_model_uri=mlflow_model_uri,
            stage=stage,
            metrics=json.dumps(metrics),
            params=json.dumps(params),
            feature_list=json.dumps(feature_list),
            feature_count=len(feature_list),
            train_size=train_size,
            test_size=test_size,
            artifact_path=artifact_path,
            dvc_hash=dvc_hash,
            is_baseline=is_baseline,
        )
        self.session.add(mv)
        self.session.commit()
        return mv

    def promote_to_production(self, model_id: int, version: int):
        self.session.query(ModelVersion).filter(
            ModelVersion.model_id == model_id,
            ModelVersion.stage == ModelStage.PRODUCTION.value,
        ).update({"stage": ModelStage.ARCHIVED.value})
        mv = self.session.query(ModelVersion).filter_by(
            model_id=model_id, version=version
        ).first()
        if mv:
            mv.stage = ModelStage.PRODUCTION.value
            self.session.commit()

    def get_production_model(self, objective: str, algorithm: str) -> Optional[ModelVersion]:
        rm = self.session.query(RegisteredModel).filter_by(
            objective=objective, algorithm=algorithm
        ).first()
        if not rm:
            return None
        return self.session.query(ModelVersion).filter_by(
            model_id=rm.model_id, stage=ModelStage.PRODUCTION.value
        ).order_by(ModelVersion.version.desc()).first()

    def get_best_version(self, objective: str, algorithm: str, metric: str = "f1_score") -> Optional[ModelVersion]:
        rm = self.session.query(RegisteredModel).filter_by(
            objective=objective, algorithm=algorithm
        ).first()
        if not rm:
            return None
        versions = self.session.query(ModelVersion).filter_by(model_id=rm.model_id).all()
        best = None
        best_val = -1.0
        for v in versions:
            m = json.loads(v.metrics)
            val = m.get(metric, 0)
            if val > best_val:
                best_val = val
                best = v
        return best
