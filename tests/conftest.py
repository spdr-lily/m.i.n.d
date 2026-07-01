import os
os.environ["RATE_LIMIT_MAX"] = "10000"

from typing import Generator
from uuid import uuid4
from datetime import date
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base, SexType, GenderIdentity, EducationLevel, Ethnicity
from app.core.database import get_db

TEST_DATABASE_URL = "postgresql://postgres:02051310VMCmspelo@localhost:5433/mind_test"

test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

SCHEMAS = ["security", "core", "clinical", "diagnostic", "ml", "audit", "admin", "chat"]


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    with test_engine.begin() as conn:
        for schema in SCHEMAS:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    Base.metadata.create_all(bind=test_engine)
    with TestSessionLocal() as session:
        if not session.query(SexType).first():
            session.add_all([
                SexType(sex_type_id=1, code="M", description="Masculino"),
                SexType(sex_type_id=2, code="F", description="Feminino"),
                GenderIdentity(gender_identity_id=1, code="M", description="Masculino"),
                GenderIdentity(gender_identity_id=2, code="F", description="Feminino"),
                GenderIdentity(gender_identity_id=3, code="NB", description="Não-Binário"),
                GenderIdentity(gender_identity_id=4, code="GF", description="Gênero Fluido"),
                GenderIdentity(gender_identity_id=5, code="AG", description="Agênero"),
                GenderIdentity(gender_identity_id=6, code="OT", description="Outro"),
                GenderIdentity(gender_identity_id=7, code="PN", description="Prefiro não informar"),
                EducationLevel(education_level_id=1, code="EF", description="Ensino Fundamental"),
                EducationLevel(education_level_id=2, code="EM", description="Ensino Médio"),
                EducationLevel(education_level_id=3, code="ES", description="Ensino Superior"),
                Ethnicity(ethnicity_id=1, code="BRANCA", description="Branca"),
                Ethnicity(ethnicity_id=2, code="PRETA", description="Preta"),
                Ethnicity(ethnicity_id=3, code="PARDA", description="Parda"),
            ])
            session.commit()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        event.remove(session, "after_transaction_end", restart_savepoint)
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    import app.core.database as db_mod
    original_engine = db_mod.engine
    db_mod.engine = test_engine

    def override_get_db():
        yield db_session
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    db_mod.engine = original_engine


@pytest.fixture
def admin_token(client, db_session) -> str:
    """Create an admin user and return a valid JWT token."""
    from app.repositories import AuthRepository
    from app.security.hashing import get_password_hash
    import uuid
    uname = f"admin_{uuid.uuid4().hex[:8]}"
    repo = AuthRepository(db_session)
    repo.create_user(
        username=uname,
        hashed_password=get_password_hash("testpass"),
        full_name="Test Admin",
        role="admin",
    )
    resp = client.post("/api/v1/auth/login", json={"username": uname, "password": "testpass"})
    return resp.json()["access_token"]


@pytest.fixture
def auth_client(client, admin_token):
    """Client with admin auth header pre-set."""
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client


@pytest.fixture
def sample_patient_data() -> dict:
    return {
        "identity": {
            "full_name": "Maria Silva",
            "cpf_hash": "hash123456",
            "email_hash": "maria@example.com",
        },
        "profile": {
            "birth_date": str(date(1990, 5, 15)),
            "sex_type_id": 1,
            "gender_identity_id": 1,
            "education_level_id": 3,
            "ethnicity_id": 1,
            "marital_status": "single",
            "occupation": "Engineer",
        },
    }


@pytest.fixture
def sample_professional_data() -> dict:
    return {
        "full_name": "Dr. Carlos Souza",
        "professional_license": "CRM-12345",
        "specialty": "Psychiatry",
    }


@pytest.fixture
def sample_disorder_data() -> dict:
    return {
        "disorder_name": "Major Depressive Disorder",
        "cid_code": "F32.1",
        "dsm_code": "296.22",
        "disorder_description": "Single episode, moderate severity",
    }
