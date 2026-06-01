# M.I.N.D Project Structure

## Directory Organization

```
project/
├── alembic/                       # Database migration scripts (Alembic)
│   ├── versions/                  # Versioned migration files
│   └── env.py                     # Alembic environment configuration
│
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   │
│   ├── core/                      # Core utilities and configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Application settings (BaseSettings)
│   │   └── exceptions.py          # Domain-specific exceptions
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                # Base model with UUID PKs
│   │   ├── patient.py             # Patient profile model
│   │   ├── disorder.py            # Disorder registry
│   │   ├── symptoms.py            # Symptom catalog
│   │   ├── consultation.py        # Clinical consultation records
│   │   ├── assessment_scales.py   # Psychometric instruments
│   │   └── diagnosis.py           # Diagnosis results
│   │
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── patient.py             # Patient DTOs
│   │   ├── diagnosis.py           # Diagnosis request/response schemas
│   │   ├── assessment.py          # Assessment scale schemas
│   │   └── consultation.py        # Consultation schemas
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── patient_service.py     # Patient management
│   │   ├── diagnosis_service.py   # Diagnosis calculation orchestration
│   │   ├── assessment_service.py  # Psychometric assessment scoring
│   │   └── consultation_service.py # Consultation workflow
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository with CRUD
│   │   ├── patient_repository.py
│   │   ├── disorder_repository.py
│   │   ├── consultation_repository.py
│   │   └── assessment_repository.py
│   │
│   ├── ml/                        # Machine Learning & Inference
│   │   ├── __init__.py
│   │   ├── bayesian_network.py    # Probabilistic graphical models
│   │   ├── inference_engine.py    # Conditional probability calculations
│   │   ├── dsm_icd_mapper.py      # DSM-5-TR ↔ ICD-11 mapping logic
│   │   └── criteria_evaluator.py  # Diagnostic criteria rule engine
│   │
│   ├── api/                       # FastAPI routes
│   │   ├── __init__.py
│   │   ├── patients.py            # POST/GET patient endpoints
│   │   ├── diagnoses.py           # POST /calculate-diagnosis
│   │   ├── consultations.py       # POST/GET consultation endpoints
│   │   ├── assessment_scales.py   # GET/POST assessment endpoints
│   │   └── health.py              # Health check routes
│   │
│   └── security/                  # Authentication & Authorization
│       ├── __init__.py
│       ├── auth.py                # JWT token management
│       ├── rbac.py                # Role-based access control
│       └── encryption.py          # AES encryption utilities (LGPD)
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures & configuration
│   ├── unit/                      # Unit tests
│   │   ├── test_criteria_evaluator.py
│   │   ├── test_inference_engine.py
│   │   └── test_assessment_scoring.py
│   │
│   └── integration/               # Integration tests
│       ├── test_consultation_workflow.py
│       ├── test_diagnosis_calculation.py
│       └── test_patient_flow.py
│
├── migrations/                    # Manual SQL migration scripts
│   └── 001_initial_schema.sql     # Initial database schema
│
├── alembic.ini                    # Alembic configuration file
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Local PostgreSQL + pgAdmin
├── .env.example                   # Environment variables template
├── pyproject.toml                 # Project metadata (poetry/build)
└── README.md                      # Project documentation
```

## Key Files Descriptions

### Configuration & Setup
- **app/core/config.py** — Application settings from environment variables
- **app/core/exceptions.py** — Domain-specific exceptions for error handling
- **requirements.txt** — Python package dependencies
- **.env.example** — Template for environment variables (LGPD: no secrets in repo)

### Database Layer
- **app/models/** — SQLAlchemy ORM models (all use UUID primary keys for LGPD compliance)
- **app/repositories/** — Data access layer (pure data operations)
- **migrations/** — SQL scripts for database schema versioning
- **alembic/** — Alembic migration management

### Business Logic
- **app/services/** — Business logic & orchestration (uses repositories + ML pipelines)
- **app/ml/** — Bayesian inference, probability calculations, DSM/ICD mapping

### API & Web Layer
- **app/api/** — FastAPI route handlers
- **app/schemas/** — Pydantic DTOs for request/response validation
- **app/security/** — Authentication, authorization, encryption

### Testing
- **tests/conftest.py** — pytest configuration and shared fixtures
- **tests/unit/** — Unit tests for individual components
- **tests/integration/** — End-to-end workflow tests

## Development Workflow

### 1. Setting Up the Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your settings
```

### 2. Database Setup
```bash
# Start PostgreSQL (docker)
docker-compose up -d

# Create migrations
alembic revision --autogenerate -m "Add patient table"

# Apply migrations
alembic upgrade head
```

### 3. Running the Application
```bash
# From root directory
uvicorn app.main:app --reload
```

### 4. Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_criteria_evaluator.py -v
```

## LGPD/GDPR Compliance Notes

- **UUIDs Only** — All patient data uses UUID identifiers, never names
- **PII Separation** — Patient names/contact info stored in separate encrypted table
- **Encryption** — Sensitive fields (consultation notes) use AES-256
- **Audit Trail** — All diagnoses logged with timestamp, clinician, rationale
- **Data Retention** — 5-year retention period per Brazilian healthcare regulations
- **Deletion** — Archive and anonymization procedures in `app/security/`

## Clinical Safeguards

- ✅ **Human-in-the-loop** — All diagnoses flagged for clinician review
- ✅ **Probabilistic** — Results include confidence intervals, not definitive diagnosis
- ✅ **DSM-5-TR & ICD-11** — All criteria validated against official standards
- ✅ **Comorbidity Logic** — Exclusionary rules prevent conflicting diagnoses
- ✅ **Differential Diagnoses** — Multiple possibilities ranked by probability

## External Resources

- [DSM-5-TR Official](https://dsm.psychiatryonline.org/)
- [ICD-11 Browser](https://icd.who.int/browse11/)
- [MIMIC-IV Dataset](https://mimic.physionet.org/)
- [Brazilian LGPD](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
