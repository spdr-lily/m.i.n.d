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
│   │   ├── base.py                # Base ORM + todas as entidades (LGPD, UUID)
│   │   ├── dw.py                  # Modelos do Data Warehouse (star schema)
│   │   └── ml.py                  # Modelos MLflow
│   │
│   ├── schemas/                   # Pydantic v2
│   │   ├── admin.py               # Schemas do sistema administrativo
│   │   ├── assessment.py          # Schemas de avaliação
│   │   ├── audit.py               # Schemas de auditoria
│   │   ├── auth.py                # Schemas de autenticação
│   │   ├── common.py              # Schemas compartilhados
│   │   ├── consultation.py        # Schemas de consulta (com validadores)
│   │   ├── disorder.py            # Schemas de transtorno (DSM-5, CID-11, autoridades)
│   │   ├── episode.py             # Schemas de episódio
│   │   ├── inference.py           # Schemas de inferência
│   │   ├── patient_identity.py    # Schemas de identidade do paciente
│   │   ├── patient_profile.py     # Schemas de perfil do paciente
│   │   ├── professional.py        # Schemas de profissional (CRM/CRP, atribuições)
│   │   └── scale.py               # Schemas de escalas
│   │
│   ├── services/                  # 24 serviços de negócio
│   │   ├── admin_service.py       # Permissões e monitoramento
│   │   ├── alerts_service.py      # Geração de alertas clínicos
│   │   ├── assessment_service.py  # Scoring de escalas + histórico
│   │   ├── audit_service.py       # Logs de auditoria
│   │   ├── consent_service.py     # Consentimento LGPD
│   │   ├── consultation_service.py
│   │   ├── disorder_service.py
│   │   ├── episode_service.py
│   │   ├── export_service.py      # Exportação CSV/PDF
│   │   ├── inference_service.py   # Orquestração de inferência
│   │   ├── inference_log_service.py
│   │   ├── integrity_service.py   # Validação clínica em 3 camadas
│   │   ├── medical_report_service.py
│   │   ├── medication_service.py
│   │   ├── metrics_service.py     # Pandas: trends, correlações
│   │   ├── monitor_service.py     # Monitoramento em tempo real
│   │   ├── patient_service.py
│   │   ├── professional_service.py
│   │   ├── reference_service.py
│   │   ├── scale_service.py
│   │   ├── access_log_service.py
│   │   └── timeline_service.py
│   │
│   ├── repositories/             # Data access layer
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
│   ├── ml/                       # Machine Learning & Inferência
│   │   ├── assessment_scales.py   # 10 escalas psicométricas
│   │   ├── bayesian_inference_service.py
│   │   ├── bayesian_network.py    # Naive Bayes classifier
│   │   ├── criteria_evaluator.py  # Regras DSM-5-TR
│   │   ├── dsm_icd_mapper.py      # Mapeamento DSM-5 ↔ CID-11
│   │   ├── inference_engine.py    # Cálculo probabilístico
│   │   ├── network_definition.py  # Estrutura da rede
│   │   └── training/              # Pipeline de ML
│   │       ├── trainer.py         # Treinador (4 objetivos × 3 algoritmos)
│   │       ├── label_builder.py   # Construtor de labels
│   │       └── estimators.py      # Estimadores (LR, RF, XGB)
│   │
│   ├── api/                      # FastAPI routes (legado, prefixo /api/)
│   │   ├── health.py
│   │   ├── admin.py, auth.py, audit.py, ...
│   │   └── v1/                   # Rotas atuais (prefixo /api/v1/)
│   │       ├── auth/
│   │       │   ├── auth.py       # POST /api/v1/auth/login, register, me
│   │       │   ├── admin.py      # /api/v1/admin/*
│   │       │   ├── audit.py      # /api/v1/audit/logs
│   │       │   └── consent.py    # /api/v1/consent/*
│   │       ├── clinical/
│   │       │   ├── patients.py       # /api/v1/patients/*
│   │       │   ├── consultations.py  # /api/v1/consultations/*
│   │       │   ├── professionals.py  # /api/v1/professionals/*
│   │       │   ├── episodes.py       # /api/v1/episodes/*
│   │       │   ├── scales.py         # /api/v1/scales/*
│   │       │   ├── assessments.py    # /api/v1/assessments/*
│   │       │   ├── metrics.py        # /api/v1/metrics/*
│   │       │   ├── alerts.py         # /api/v1/alerts/*
│   │       │   ├── medications.py    # /api/v1/medications/*
│   │       │   └── reference.py      # /api/v1/reference/*
│   │       ├── diagnostic/
│   │       │   ├── disorders.py  # /api/v1/disorders/*
│   │       │   └── inferences.py # /api/v1/inferences/*
│   │       └── ml/
│   │           └── training.py   # /training/*
│   │
│   ├── middleware/
│   │   ├── audit_middleware.py    # Auditoria de requisições
│   │   └── security_middleware.py # CSP, HSTS, Rate Limit, SQL Injection
│   │
│   ├── security/
│   │   ├── auth.py               # JWT (login, refresh, verify)
│   │   ├── rbac.py               # Role-based access control
│   │   └── encryption.py         # Fernet AES (LGPD)
│   │
│   ├── etl/
│   │   └── dw_loader.py          # ETL para Data Warehouse (star schema)
│   │
│   └── analytics/
│       ├── aggregations/
│       ├── bi/
│       ├── dashboards/
│       ├── metrics/
│       └── statistics/
│
├── mind-ui/                      # Frontend (React + TypeScript + Vite)
│   ├── src/
│   │   ├── api/                  # 16 módulos Axios
│   │   │   ├── client.ts         # Axios instance com interceptor JWT
│   │   │   ├── auth.ts, patients.ts, consultations.ts, ...
│   │   │   ├── inferences.ts, scales.ts, disorders.ts
│   │   │   ├── professionals.ts, medications.ts, reports.ts
│   │   │   ├── alerts.ts, audit.ts, metrics.ts
│   │   │   ├── admin.ts, reference.ts, timeline.ts
│   │   ├── components/
│   │   │   ├── MainLayout.tsx    # Sidebar + Header (Ant Design)
│   │   │   └── MindLogo.tsx      # Logo componente
│   │   ├── pages/
│   │   │   ├── auth/LoginPage.tsx
│   │   │   ├── dashboard/
│   │   │   ├── patients/
│   │   │   ├── consultations/
│   │   │   ├── assessments/     # Com histórico do paciente
│   │   │   ├── inferences/      # 14 categorias de sintomas
│   │   │   ├── professionals/   # Atribuição de pacientes
│   │   │   ├── alerts/
│   │   │   ├── admin/           # Transtornos com DSM-5/ICD-11 collapsible
│   │   │   └── audit/
│   │   ├── store/
│   │   │   ├── authStore.ts     # Zustand auth state
│   │   │   └── themeStore.ts
│   │   ├── utils/
│   │   │   └── constants.ts     # SCALE_OPTIONS, etc.
│   │   ├── types/
│   │   │   └── index.ts         # Interfaces TypeScript
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   └── logo.png
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── db/                          # Scripts de banco de dados
│   ├── seed.py                  # Dados de referência (idempotente)
│   ├── populate_clinical.py     # Dados clínicos de exemplo
│   ├── add_patient.py           # Utilitário
│   └── check_data.py            # Verificação de registros
│
├── scripts/                     # Scripts de manutenção
│   ├── seed_clinical_data.py    # Dados clínicos (fonte única 19 transtornos)
│   ├── seed_icd11.py            # Códigos CID-11
│   ├── seed_scales_groups.py    # Grupos de critérios e escalas
│   ├── seed_diagnostic_data.py  # Critérios DSM-5-TR, exclusões, diferenciais
│   ├── seed_ml_symptoms.py      # Sintomas para ML
│   ├── train_all.py             # Treinar pipeline ML (12 modelos)
│   ├── check_integrity.py       # Relatório de qualidade de dados
│   ├── check_current_state.py   # Diagnóstico do estado atual
│   ├── build_clinical_dataset.py
│   └── export_training_data.py
│
├── dags/                       # Apache Airflow DAGs
│   ├── config.py
│   ├── clinical_inference_dag.py  # 02h - inferência em lote
│   ├── data_quality_dag.py        # 03h - 6 checagens de qualidade
│   ├── metrics_aggregation_dag.py # 04h - agregação de métricas
│   └── alert_generation_dag.py    # 6/6h - ideação + deterioração
│
├── spark/                      # PySpark jobs
│   ├── config.py
│   ├── submit.py               # CLI helper
│   └── jobs/
│       ├── batch_inference.py
│       ├── population_metrics.py
│       └── data_import.py
│
├── data/                       # Dados e datasets
│   ├── datasets/
│   │   ├── clinical_dataset.csv       # 187 linhas, 31 colunas
│   │   ├── features_diagnosis.csv     # Features para ML (versionado DVC)
│   │   ├── features_relapse.csv
│   │   ├── features_suicide_risk.csv
│   │   └── features_therapeutic_response.csv
│   ├── metrics/
│   └── models/
│
├── migrations/                 # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # 12 revisões lineares
│       ├── 05ecbb7b2bc1_initial_schema.py
│       ├── 005f85846e88_admin_permissions_routes.py
│       ├── 9e4c2f8a1b3d_add_trans_status.py
│       ├── 7a1b3c5d8e9f_add_medications.py
│       ├── 2c8a1e3fae51_add_medical_reports.py
│       ├── a29a8fdd7159_add_profession_and_start_date.py
│       ├── b3c4d5e6f7a8_add_clinical_notes.py
│       ├── 41991f22ee27_add_audit_logs_columns.py
│       ├── 1c223a553bb0_add_clinical_alerts_table.py
│       ├── c1d2e3f4a5b6_add_clinical_check_constraints.py
│       ├── d4e5f6a7b8c9_add_classification_authorities.py
│       └── e5f6a7b8c9d0_add_professional_patient_assignments.py
│
├── mlruns/                     # MLflow experiment tracking
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_assessment_scales.py
│   │   ├── test_auth.py
│   │   ├── test_bayesian_network.py
│   │   ├── test_criteria_evaluator.py
│   │   ├── test_dsm_icd_mapper.py
│   │   ├── test_inference_engine.py
│   │   └── test_metrics.py
│   └── integration/
│       ├── test_admin.py
│       ├── test_api.py
│       ├── test_audit.py
│       ├── test_audit_api.py
│       └── test_repositories.py
│
├── .certs/                     # Certificados SSL (desenvolvimento)
│
├── .github/workflows/
│   └── ci.yml                  # CI: flake8, black, mypy, pytest, codecov
│
├── .bandit                     # Configuração Bandit SAST
├── .pre-commit-config.yaml     # Pre-commit hooks de segurança
├── docker-compose.yml          # 5 serviços
├── Dockerfile
├── entrypoint.sh
├── alembic.ini
├── pyproject.toml
├── requirements.txt
├── requirements-prod.txt
├── .env.example
├── mlflow.db                   # MLflow tracking (SQLite)
│
├── AGENTS.md                   # Instruções para agentes de IA
├── README.md
├── STRUCTURE.md                # Este arquivo
├── DESENVOLVIMENTO.md
├── CLINICAL_MANUAL.md
├── QUICKSTART.md
├── SECURITY.md
└── ANCHORED SUMMARY.md         # Sumário executivo da sessão
```

## Convenções

- **UUIDs** — Todas as PKs usam UUID (LGPD)
- **PII isolado** — Identidade do paciente separada dos dados analíticos
- **Schemas PostgreSQL** — `core` (pacientes), `clinical` (consultas, escalas), `diagnostic` (transtornos, inferências), `audit` (logs), `admin` (permissões)
- **Pydantic v2** — Schemas com `model_validator` e `field_serializer`
- **Human-in-the-loop** — Toda inferência requer validação clínica
- **3 camadas de validação clínica** — Pydantic → IntegrityService → DB CHECK constraints
- **Autoridades de classificação** — APA (DSM-5-TR) e WHO (CID-11) como first-class citizens

## Serviços Docker

| Serviço | Porta | Credenciais |
|---|---|---|
| postgres | 5432 | configurar via `.env` |
| pgadmin | 5050 | `admin@mind.com` / `admin` |
| app | 8001/8008 | — |
| airflow-webserver | 8080 | `admin` / `admin` |
| airflow-scheduler | — | — |
