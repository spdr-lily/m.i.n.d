# M.I.N.D — Estrutura do Projeto

```
m.i.n.d/
│
├── app/                           # Pacote principal (FastAPI)
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
│   │   ├── admin.py               # RolePermission, RoutePermission
│   │   └── __init__.py
│   │
│   ├── schemas/                   # Pydantic v2
│   │   ├── admin.py               # Schemas do sistema administrativo
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
│   │   ├── admin_service.py        # Lógica de permissões e monitoramento
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
│   │   ├── admin.py               # 12 endpoints administrativos
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
├── mind-ui/                       # Frontend (React + TypeScript + Vite)
│   ├── src/
│   │   ├── api/                   # Axios API client
│   │   │   ├── auth.ts
│   │   │   ├── patients.ts
│   │   │   └── consultations.ts
│   │   ├── components/
│   │   │   ├── MainLayout.tsx     # Sidebar + Header (Ant Design)
│   │   │   └── MindLogo.tsx       # Logo componente
│   │   ├── pages/
│   │   │   ├── auth/LoginPage.tsx
│   │   │   ├── dashboard/
│   │   │   ├── patients/
│   │   │   ├── consultations/
│   │   │   ├── assessments/
│   │   │   ├── inferences/
│   │   │   ├── alerts/
│   │   │   ├── admin/
│   │   │   └── audit/
│   │   ├── store/
│   │   │   ├── authStore.ts       # Zustand auth state
│   │   │   └── themeStore.ts
│   │   ├── utils/
│   │   │   └── constants.ts
│   │   ├── types/
│   │   │   └── index.ts           # Interfaces TypeScript
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   └── logo.png               # Logo da aplicação
│   ├── index.html
│   ├── vite.config.ts             # Proxy /api → :8001
│   ├── tsconfig.json
│   └── package.json
│
├── db/                            # Scripts de banco de dados
│   ├── seed.py                    # Dados de referência (sintomas, transtornos, critérios)
│   ├── populate_clinical.py       # Dados clínicos de exemplo (7 pacientes, consultas, escalas)
│   ├── add_patient.py             # Utilitário para inserir paciente
│   └── check_data.py              # Utilitário para verificar registros
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
│       ├── 05ecbb7b2bc1_initial_schema.py       # 22 tabelas (core, clinical, diagnostic, ml, audit, security)
│       ├── 005f85846e88_admin_system.py         # Admin (RolePermission, RoutePermission)
│       ├── 9e4c2f8a1b3d_add_trans_status.py      # trans_status em patient_profile
│       ├── 7a1b3c5d8e9f_add_medications.py        # Medications, Prescriptions, PrescriptionItems
│       ├── 2c8a1e3fae51_add_medical_reports.py    # MedicalReports
│       ├── a29a8fdd7159_add_profession_fields.py  # profession, start_date em healthcare_professionals
│       ├── b3c4d5e6f7a8_add_clinical_notes.py     # ClinicalNotes
│       └── 41991f22ee27_noop_audit_columns.py     # No-op (colunas já existentes)
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
│       ├── test_admin.py          # 18 testes do sistema administrativo
│       ├── test_api.py
│       ├── test_audit.py
│       ├── test_audit_api.py
│       └── test_repositories.py
│
├── .certs/                        # Certificados SSL (desenvolvimento)
│   ├── mind-dev.key               # Chave privada RSA
│   ├── mind-dev.pem               # Certificado autoassinado
│   ├── mind-dev-cert.pem          # Certificado PEM (HTTPS)
│   └── mind-dev.pfx               # PKCS#12 (alternativa)
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
- **Schemas PostgreSQL** — `core` (pacientes), `clinical` (consultas, escalas), `diagnostic` (transtornos, inferências), `audit` (logs), `admin` (permissões)
- **Pydantic v2** — Schemas com `model_validator` e `field_serializer`
- **Human-in-the-loop** — Toda inferência requer validação clínica

## Serviços Docker

| Serviço | Porta | Credenciais |
|---|---|---|
| postgres | 5432 | configurar via `.env` |
| pgadmin | 5050 | `admin@mind.com` / `admin` |
| app | 8001 | — |
| airflow-webserver | 8080 | `admin` / `admin` |
| airflow-scheduler | — | — |
