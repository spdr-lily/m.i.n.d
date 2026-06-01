# M.I.N.D — Estrutura do Projeto

```
m.i.n.d/
│
├── app/                           # Pacote principal
│   ├── main.py                    # FastAPI entry point (uvicorn)
│   │
│   ├── core/
│   │   ├── config.py              # BaseSettings (DB, JWT, CORS, etc.)
│   │   ├── database.py            # Engine + SessionLocal
│   │   ├── exceptions.py          # Exceções clínicas customizadas
│   │   └── logging_config.py      # Configuração de logging
│   │
│   ├── models/
│   │   ├── base.py                # Base ORM (UUID pk, timestamps)
│   │   └── __init__.py
│   │
│   ├── schemas/                   # Pydantic v2
│   │   ├── assessment.py
│   │   ├── audit.py
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── consultation.py
│   │   ├── disorder.py
│   │   ├── episode.py
│   │   ├── inference.py
│   │   ├── patient_identity.py
│   │   ├── patient_profile.py
│   │   ├── professional.py
│   │   └── scale.py
│   │
│   ├── services/
│   │   ├── alerts_service.py       # Geração de alertas clínicos
│   │   ├── assessment_service.py   # Scoring de escalas
│   │   ├── audit_service.py        # Logs de auditoria
│   │   ├── consultation_service.py
│   │   ├── disorder_service.py
│   │   ├── episode_service.py
│   │   ├── inference_service.py    # Orquestração de inferência
│   │   ├── metrics_service.py      # Pandas: trends, correlações
│   │   ├── patient_service.py
│   │   ├── professional_service.py
│   │   └── scale_service.py
│   │
│   ├── repositories/              # Data access layer
│   │   ├── base.py                # Base CRUD genérico
│   │   ├── auth_repository.py
│   │   ├── consultation_repository.py
│   │   ├── disorder_repository.py
│   │   ├── episode_repository.py
│   │   ├── inference_repository.py
│   │   ├── patient_repository.py
│   │   ├── professional_repository.py
│   │   └── scale_repository.py
│   │
│   ├── ml/                        # Machine Learning & Inferência
│   │   ├── assessment_scales.py   # 10 escalas psicométricas
│   │   ├── bayesian_inference_service.py
│   │   ├── bayesian_network.py    # Naive Bayes classifier
│   │   ├── criteria_evaluator.py  # Regras DSM-5-TR
│   │   ├── dsm_icd_mapper.py      # Mapeamento DSM-5 ↔ CID-11
│   │   ├── inference_engine.py    # Cálculo probabilístico
│   │   └── network_definition.py  # Estrutura da rede
│   │
│   ├── api/                       # FastAPI routes
│   │   ├── alerts.py
│   │   ├── assessments.py
│   │   ├── audit.py
│   │   ├── auth.py
│   │   ├── consultations.py
│   │   ├── disorders.py
│   │   ├── episodes.py
│   │   ├── health.py
│   │   ├── inferences.py
│   │   ├── metrics.py
│   │   ├── patients.py
│   │   ├── professionals.py
│   │   ├── reference.py
│   │   └── scales.py
│   │
│   ├── middleware/
│   │   └── audit_middleware.py    # Auditoria de requisições
│   │
│   └── security/
│       ├── auth.py                # JWT (login, refresh, verify)
│       ├── rbac.py                # Role-based access control
│       └── encryption.py          # Fernet AES (LGPD)
│
├── dags/                          # Apache Airflow DAGs
│   ├── config.py                  # Shared config (DB connection)
│   ├── clinical_inference_dag.py  # 02h - inferência em lote
│   ├── data_quality_dag.py        # 03h - 6 checagens de qualidade
│   ├── metrics_aggregation_dag.py # 04h - agregação de métricas
│   └── alert_generation_dag.py    # 6/6h - ideação + deterioração
│
├── spark/                         # PySpark jobs
│   ├── config.py                  # JDBC URL, DB_PROPERTIES
│   ├── submit.py                  # CLI helper
│   └── jobs/
│       ├── batch_inference.py     # Inferência em lote
│       ├── population_metrics.py  # Métricas populacionais
│       └── data_import.py         # ETL CSV → PostgreSQL
│
├── migrations/                    # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 05ecbb7b2bc1_initial_schema.py  # 17 tabelas iniciais
│
├── tests/
│   ├── conftest.py                # Fixtures globais
│   ├── unit/
│   │   ├── conftest.py
│   │   ├── test_assessment_scales.py
│   │   ├── test_auth.py
│   │   ├── test_bayesian_network.py
│   │   ├── test_criteria_evaluator.py
│   │   ├── test_dsm_icd_mapper.py
│   │   ├── test_inference_engine.py
│   │   └── test_metrics.py
│   └── integration/
│       ├── test_api.py
│       ├── test_audit.py
│       ├── test_audit_api.py
│       └── test_repositories.py
│
├── .github/workflows/
│   └── ci.yml                     # CI: flake8, black, mypy, pytest, codecov
│
├── docker-compose.yml             # 5 serviços: postgres, app, pgadmin, airflow-webserver, airflow-scheduler
├── Dockerfile                     # Python 3.12 + entrypoint.sh
├── entrypoint.sh                  # Alembic upgrade + uvicorn
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .env                           # Credenciais + chaves (não versionado)
│
├── CLINICAL_MANUAL.md             # Manual clínico (pt-BR)
├── README.md
├── QUICKSTART.md
├── STRUCTURE.md                   # Este arquivo
├── DESENVOLVIMENTO.md
└── ANCHORED SUMMARY.md            # Sumário executivo da sessão
```

## Convenções

- **UUIDs** — Todas as PKs de pacientes usam UUID (LGPD)
- **PII isolado** — Identidade do paciente separada dos dados analíticos
- **Schemas PostgreSQL** — `core` (pacientes), `clinical` (consultas, escalas), `diagnostic` (transtornos, inferências), `audit` (logs)
- **Pydantic v2** — Schemas com `model_validator` e `field_serializer`
- **Human-in-the-loop** — Toda inferência requer validação clínica

## Serviços Docker

| Serviço | Porta | Credenciais |
|---|---|---|
| postgres | 5432 | `postgres` / `137_Cmspelo` / `mind` |
| pgadmin | 5050 | `admin@mind.com` / `admin` |
| app | 8001 | — |
| airflow-webserver | 8080 | `admin` / `admin` |
| airflow-scheduler | — | — |
