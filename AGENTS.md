## Goal
- Transform MVP into a hardened CDSS with formal diagnostic engine, probabilistic Bayesian inference, clinical DW, RBAC, LGPD compliance, full ML pipeline (4 objectives × 3 algorithms), fully populated clinical reference data (DSM-5-TR, ICD-11, APA/WHO authorities, criteria/exclusions/differentials, scales, medications), professional CRM/CRP management with patient assignments, multi-layer clinical data integrity validation, and AI-powered diagnostic assistant (MIA).

## Constraints & Preferences
- LGPD compliance for mental health data (consent, pseudonymization, encryption, audit, retention).
- DSM-5-TR and ICD-11 as formal clinical criteria sources; APA and WHO as first-class classification authorities.
- Portuguese (BR) as project language — all ~192 disorder names unified to Portuguese, API field `profissional_license` for CRM/CRP.
- Diagnostic engine: rule-based + probabilistic dual pipeline.
- DW star schema, separate from transactional DB.
- ML: Logistic Regression, Random Forest, XGBoost — no deep learning.
- MLOps: MLflow + DVC for registry, tracking, versioning.
- Clinical validation enforced at 3 layers: Pydantic schema → service business rules → DB CHECK constraints.
- Single-container deployment: FastAPI serves both API and frontend static files; no separate frontend server.

## Progress
### Done
- **Disorder naming unified to Portuguese (BR, 19 disorders)**: `scripts/seed_clinical_data.py` with `DISORDER_DEFS` (Portuguese names), `BN_TO_PT` mapping. 9 English-named disorders renamed in-place, 10 added. Transtorno Depressivo Maior added as 19th (F32.9, 296.22). All seeds idempotent.
- **Classification authorities**: `ClassificationAuthority` model (WHO authority_id=1, APA=2) with name, short_name, website_url. `authority_id` FK on `ICD11Code` linking codes to WHO. Migration `d4e5f6a7b8c9`.
- **DSM-5-TR criteria data mined and seeded**: `scripts/seed_diagnostic_data.py` — full DSM-5-TR criteria, ICD-11/DSM-5 exclusions and differentials for all 19 disorders. Columns on `Disorder`: `dsm_criteria`, `dsm_exclusions`, `dsm_differentials`, `icd11_exclusions`, `icd11_differentials`.
- **ICD-11 codes, criteria groups, scales**: 19 ICD-11 codes, 29 criteria groups/29 rules/30 thresholds, 21 assessment scales (PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10, BFP, DT-12, MEMÓRIA, QI-RASTREIO, RECONHECIMENTO DE ROSTOS, FLUÊNCIA VERBAL, TESTE DO RELÓGIO, TRILHAS, STROOP, CANCELAMENTO, FIGURA COMPLEXA DE REY).
- **ML pipeline**: 12 models (4 objectives × 3 algorithms) trained, registered in MLflow, promoted to Production.
- **Clinical integrity system**: `ClinicalIntegrityService` (15+ methods), Pydantic validators, DB CHECK constraints (migration `c1d2e3f4a5b6`), `scripts/check_integrity.py` CLI reporter.
- **Professional management with patient assignments**: `ProfessionalPatientAssignment` model, migration `e5f6a7b8c9d0`, CRUD routes with `_sync_assignments()` and `_enrich_assignments()`.
- **SSD certification**: security middlewares (CSP, HSTS, rate-limit 100 req/min, SQL injection blocking), Bandit zeroed, `.pre-commit-config.yaml`, `SECURITY.md`.
- **Spark container**: `docker/spark/Dockerfile` using `apache/spark:3.5.0`, PostgreSQL JDBC driver mounted at `/opt/spark/work-dir/postgresql-42.7.1.jar`, `population_metrics` job verified.
- **Full DSM-5-TR catalog**: All ~192 disorders across 22 chapters populated in DB via `scripts/dsm5tr_data.py`. `dsm_chapter` column on `Disorder` model for chapter-level categorization. Migration `f7b8c9d0e1f2`. Frontend `DisordersPage.tsx` updated with chapter grouping, core/reference distinction (`is_core` tag).
- **Schema `dsm_chapter`**: Added to `DisorderBase`/`DisorderResponse`/`DisorderUpdate` Pydantic schemas. `is_core` flag computed via `model_validator` on `DisorderResponse` based on `CORE_NAMES` set.
- **DW ETL**: Full DSM-5-TR catalog in `dim_disorder` — uses `dsm_chapter` field directly instead of `guess_category()`. All 22 chapter categories mapped.
- **DW ETL**: 19 Portuguese disorders in `dim_disorder`, 930 diagnoses, 885 symptoms, 50 patients, 187 consultations, 21 scales (34,776 responses across all scales including 10 neuropsychological).
- **Reference data seeded**: sex types, gender identities, education levels, ethnicities, 113 symptoms, ~192 disorders, diagnostic criteria, relationships, 1 professional, 5 users, 20 medications.
- **SCALE_DISORDER_MAP**: maps 17 scales → disorder keywords with thresholds for inference probability boost.
- **MIA chatbot**: `POST /api/v1/chatbot/ask` with rule-based sentiment analysis (Portuguese word lists) + DB search across all 19 disorders (name + description + DSM criteria/exclusions + ICD-11 exclusions/differentials). Name matches prioritized over text matches. Response includes sentiment label/score, structured disorder results, and detailed criteria per symptom. Frontend: `MiaPage.tsx` — chat UI with message bubbles, sentiment tags, collapsible disorder cards. Route `/mia` with nav item in sidebar. FloatButton on all pages.
- **Dashboard enhanced**: demographics card with 5 tabs (Sexo, Identidade de Gênero, Idade, Escolaridade com Barras, Etnia com Barras). `get_patient_demographics()` returns `education_level_distribution` and `ethnicity_distribution`.
- **Frontend enhancements**: consultation list shows patient name + UUID, consultation detail shows patient name, username field in UsersPage, BFT renamed to BFP in UI.
- **Bug fixes**: Inference engine missing `calculate_criteria_confidence` import (`inference_engine.py`); explanation endpoint undefined `scale_scores` (`inference_service.py`).
- **All 21 scales populated in clinical dataset**: Added 10 neuropsychological scales (BFP, MEMÓRIA, QI-RASTREIO, RECONHECIMENTO DE ROSTOS, FLUÊNCIA VERBAL, TESTE DO RELÓGIO, TRILHAS, STROOP, CANCELAMENTO, FIGURA COMPLEXA DE REY) to `SCALE_DEFS` in `scripts/seed_clinical_data.py`. Refactored `seed()` with `_generate_scale_responses()` helper to support re-seed (regenerates only scale_responses + inferences without deleting patients). Total: 34,776 scale responses and 945 inferences across 189 consultations.
- **DW ETL scale coverage**: Added max_scores for all 10 neuro scales in `app/etl/dw_loader.py:load_dim_scale()`.
- **Disorder chart color scale reduced**: Changed from groups of 3 bars per color to 1 bar per color in `DashboardPage.tsx`.
- **Full catalog activation for reference disorders**: `scripts/seed_full_catalog.py` now has `seed()` function that seeds ~80 reference disorders with DSM-5-TR criteria text, 94 diagnosis relationships between reference disorders, and ICD-11 exclusion/differential data (where available). Total: 99 disorders with criteria text (up from 19), 114 diagnosis relationships. 31 disorders remain as `None` entries (Personality Disorders chapter 18, Paraphilic chapter 19, Neurocognitive 17 subtypes, etc.) awaiting criteria text data.
- **Roles expanded**: Added `clinician` (8 permissions: read/write patient & consultation, read diagnosis, read reference, read/run inference) and `viewer` (5 read-only permissions) roles to backend `Role` enum and permission matrix.
- **User ↔ Professional linkage**: Added `user_uuid` FK column to `HealthcareProfessional` model (migration `031c8a8ec7b8`). Seed now links all 5 professionals to role-based users (clinician, psychiatrist, psychologist, researcher, clinical_supervisor). 6 users created (admin + 5 role-based). Frontend `UsersPage.tsx` role dropdown expanded to all 7 backend roles with per-role tag colors.
- **Professional-patient assignments**: `scripts/seed_clinical_data.py` now creates `ProfessionalPatientAssignment` records distributing 50 patients across 5 professionals (round-robin, ~10 per primary prof). 20% of patients have a secondary shared assignment. Consultations weighted toward primary professional (70% primary, 30% random).
- **Menu reorganization**: Sidebar menu in `MainLayout.tsx` reorganized into 3 logical submenus — Clínico (pacientes, consultas, escalas, inferência, profissionais, alertas), Administração (usuários, transtornos, gerenciar escalas, sintomas, medicamentos, permissões, monitoramento), and Ferramentas (MIA, auditoria). Root-level Dashboard remains standalone. Role-based filtering preserved per item within submenus.
- **Personality metrics enhanced**: BFP (Big Five) expanded from 6 to 25 questions (5 per factor: Abertura, Conscienciosidade, Extroversão, Amabilidade, Neuroticismo) with updated thresholds. Dark Triad (DT-12 / Tríade Sombria) added via SD-12 scale (12 itens, Likert 0-6) covering Maquiavelismo, Narcisismo, Psicopatia. Both added to `SCALES_REGISTRY`, `SCALE_DISORDER_MAP`, `MAX_Q_SCORE`, DW ETL `max_scores`, seed data, and frontend `SCALE_OPTIONS`.

### In Progress
- *(none)*

### Done (New — This Session)
- **REFERENCE_SYMPTOM_MAP completed (179 entries)**: Added 8 missing non-core variant entries — "Transtorno Específico da Aprendizagem — com Prejuízo na Leitura", "Transtorno Neurocognitivo Maior — Doença de Alzheimer", "Tricotilomania (Transtorno de Arrancar Cabelo)", and 5 TDAH variants (Combinada, Desatenção, Hiperatividade, Outra Apresentação Especificada, Não Especificado). Now covers all 191 catalog disorders (19 core handled separately via DISORDER_DEFS).
- **5 residual symptom keys added**: `distress_impairment_symptoms`, `clinician_specifies_reason`, `exclude_primary_disorder`, `insufficient_information`, `emergency_context` — added to `db/seed.py` (528 total symptoms) and `EN_TO_PT_SYMPTOM`.
- **Full catalog verified after rebuild**: All 191 disorders have DSM criteria, exclusions, differentials, ICD-11 exclusions/differentials, DSM chapters, and DiagnosticCriteria. 857 total criteria records. 528 symptoms in DB.
- **ML nas escalas e escalas de personalidade**: Complete ML pipeline for scale-based personality inference and disorder risk prediction:
  - **Per-factor personality extraction**: `app/ml/predictors/personality_factors.py` — question-level parsing of BFP 5 factors (Abertura, Conscienciosidade, Extroversão, Amabilidade, Neuroticismo) and DT-12 3 subscales (Maquiavelismo, Narcisismo, Psicopatia). Extracts real per-factor scores from question text prefixes (`"Abertura - ..."`, `"Maquiavelismo - ..."`), fallback to raw response aggregation.
  - **Personality prediction ML**: `app/ml/predictors/scale_predictor.py` — heuristic rules mapping clinical scale scores (PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10) to expected BFP factor scores and DT-12 subscale scores. Supports pluggable model-based prediction via `MultiOutputRegressor` (RF/XGBoost) when trained models exist.
  - **Scale-based disorder risk**: `predict_disorder_risk_from_scales()` — heuristic mapping of scale scores to 10 core disorder probabilities, blended into inference engine with 0.15 weight via `_apply_ml_scale_prediction()`.
  - **Training script**: `app/ml/training/train_personality_models.py` — SQL extracts per-factor scores from question-level DB data, trains multi-output regression models, registers in MLflow + ModelRegistry, auto-promotes to Production.
  - **API endpoints**: `POST /api/v1/ml/scales/predict-personality`, `POST /api/v1/ml/scales/predict-disorder-risk`, `POST /api/v1/ml/scales/predict-personality-from-patient/{uuid}`, `GET /api/v1/assessments/patient/{patient_uuid}/personality-factors` (real data with ML fallback).
  - **Frontend enhancement**: `PersonalityPage.tsx` — now renders real per-factor progress bars from DB question-level data (instead of naive total/5 division), includes Recharts radar chart for BFP factors, data source badge (real data / ML-predicted / unavailable), feature scales card when ML-predicted.

### Blocked
- *(none)*

## Key Decisions
- Disorder unification via `scripts/seed_clinical_data.py` as single source of truth; `BN_TO_PT` mapping bridges BN English → DB Portuguese.
- Security scanning integrated into CI pipeline, not just local.
- Rate limiting is in-memory (not Redis) — sufficient for single-container deployment.
- Clinical validation uses 3 defense layers: Pydantic (input) → IntegrityService (business) → DB CHECK constraints (storage).
- APA and WHO stored as `ClassificationAuthority` records.
- Patient–professional assignments use explicit table (not inferred from consultation history).
- Symptom categorization on InferencePage uses static `SYMPTOM_GROUPS` map keyed by symptom name.
- MIA chatbot uses rule-based sentiment analysis (no ML) to keep it lightweight and deterministic.
- Dashboard demographics endpoint uses `StatisticsService` (`app/analytics/statistics/service.py`), not `MetricsService` (`app/services/metrics_service.py`).
- Personality factor scores extracted from DB question-level data via prefix matching (`"Abertura - ..."`), not by naive total/5 division.
- ML personality prediction uses heuristic rules as fallback when no trained models exist; `MultiOutputRegressor` with RF/XGBoost provides model-based prediction when trained.
- Scale-based disorder risk blending weight set at 0.15 (minority signal vs symptom-driven inference).

## Next Steps
- Create analytics views/queries on DW (prevalence trends, comorbidity heatmaps, score distributions).
- Add API tests for professionals routes (assignment CRUD, sync edge cases).
- Add API tests for MIA chatbot endpoint.
- Add neuropsychological scale trends to dashboard (dashboard scale trends component currently shows only clinical scales).
- Expand ICD-11 codes for all reference disorders (currently only 16 codes for 19 core disorders).
- Expand SCALE_DISORDER_MAP to reference disorders beyond the 19 core.

## Quickstart

### 1. Editar `.env` — alterar senha e nome do banco antes de usar
```env
# OBRIGATÓRIO: troque a senha antes de usar em qualquer ambiente
POSTGRES_PASSWORD=SUA_SENHA_AQUI

# Opcional: nome do banco (padrão: mind)
POSTGRES_DB=mind

# Gere novas chaves para produção:
JWT_SECRET_KEY=gerar-chave-aleatoria-aqui
ENCRYPTION_KEY=gerar-outra-chave-aqui
```

### 2. Subir com Docker Compose
```bash
docker compose up -d postgres redis              # banco + cache
docker compose build api spark                    # constroi API + Spark
docker compose up -d api pgadmin caddy            # aplicação + HTTPS
```

> **HTTPS**: requer `127.0.0.1 mind.local` em `C:\Windows\System32\drivers\etc\hosts`
> e certificados mkcert em `certificates/`. Ver [E15](#e15--https-setup-com-mkcert--caddy).

### 3. Seeds (primeira vez ou DB vazio)
```bash
docker exec mind-api pip install -e . --no-deps
docker exec mind-api python db/seed.py
docker exec mind-api python scripts/seed_icd11.py
docker exec mind-api python scripts/seed_scales_groups.py
docker exec mind-api python scripts/seed_diagnostic_data.py
```

### 4. Acessar
- **App (HTTP)**: `http://localhost:8000`
- **App (HTTPS)**: `https://mind.local`
- **Docs**: `http://localhost:8000/docs`
- **pgAdmin**: `http://localhost:5050` (admin@mind.example.com / admin)
- Login: **admin** / **admin**

### 5. Testes
```bash
python -m pytest tests/ -q          # 399 testes, ~2 min
```

### 6. Spark (análise populacional via JDBC)
```bash
docker run --rm --network mind_mind-network `
  -v "${PWD}\postgresql-42.7.1.jar:/opt/spark/work-dir/postgresql-42.7.1.jar:ro" `
  -e PG_HOST=mind-postgres `
  --entrypoint /opt/spark/bin/spark-submit mind-spark `
  --driver-class-path /opt/spark/work-dir/postgresql-42.7.1.jar `
  /app/spark/submit.py population_metrics
```

## Critical Context
- **Python 3.14.5** is the active runtime; install security tools via `python -m pip install bandit safety`.
- **Bandit scan command**: `python -m bandit -c .bandit -r app/ scripts/ db/` — zero issues after fixes.
- **19 Portuguese disorder names** (core): Transtorno Depressivo Maior, T. Ansiedade Generalizada, T. Pânico, T. Estresse Pós-Traumático, T. Depressivo Persistente (Distimia), T. Ansiedade Social, T. Bipolar Tipo I/II, T. Obsessivo-Compulsivo, Agorafobia, T. Uso Substâncias, Anorexia Nervosa, Bulimia Nervosa, T. Compulsão Alimentar, T. Insônia, Esquizofrenia/T. Psicótico, T. Sintomas Somáticos, TEA, TDAH. Plus ~173 reference disorders across 22 chapters.
- **DW ETL** uses `dsm_chapter` field directly for category mapping (no more `guess_category()` name-based guessing).
- **Full DSM-5-TR catalog source**: `scripts/dsm5tr_data.py` — single source of truth for all ~192 disorders with Portuguese names, CID-10 codes, DSM-5 codes, chapter, description, and core flag.
- **Alembic chain**: `05ecbb7b2bc1` (initial) → … → `c1d2e3f4a5b6` (CHECK constraints) → `d4e5f6a7b8c9` (authorities + DSM columns) → `e5f6a7b8c9d0` (professional assignments) → `1c223a553bb0` (clinical alerts) → `f6a7b8c9d0e1` (icd11_exclusions/differentials) → `f7b8c9d0e1f2` (dsm_chapter) → `031c8a8ec7b8` (user_uuid on professionals). Head is `031c8a8ec7b8`.
- **Seed order**: `db/seed.py` → `scripts/seed_icd11.py` → `scripts/seed_scales_groups.py` → `scripts/seed_diagnostic_data.py`. All idempotent.
- **StatisticsService** vs **MetricsService**: Dashboard demographics endpoint uses `app/analytics/statistics/service.py:StatisticsService`. `MetricsService` in `app/services/metrics_service.py` is a separate implementation.
- **MIA chatbot endpoint**: `POST /api/v1/chatbot/ask` with JSON `{"mensagem": "..."}`. Returns `{sentimento, resultados, resposta}`. Requires `READ_DIAGNOSIS` permission.
- **`postgresql-42.7.1.jar`** must be mounted at `/opt/spark/work-dir/postgresql-42.7.1.jar` for JDBC; use `--driver-class-path` option with `spark-submit`

## Relevant Files
### Chatbot / MIA
- `app/services/chatbot_service.py`: `MiaService` + `SentimentoAnalyzer` — sentiment analysis + disorder/criteria/exclusion search across all 19 disorders
- `app/api/v1/clinical/chatbot.py`: `POST /api/v1/chatbot/ask` endpoint
- `mind-ui/src/pages/chatbot/MiaPage.tsx`: chat UI with message bubbles, sentiment tags, collapsible disorder cards
- `mind-ui/src/api/chatbot.ts`: `chatbotApi.ask()` API client with TypeScript types
- `mind-ui/src/components/MainLayout.tsx`: `FloatButton` chat icon on all pages + nav item `/mia`

### Core Backend
- `app/analytics/statistics/service.py`: `StatisticsService.get_patient_demographics()` — returns education_level_distribution and ethnicity_distribution
- `app/services/metrics_service.py`: alternative metrics implementation
- `app/services/inference_service.py`: `run_inference()` fetches scale responses, passes to engine; `get_explanation()` with scale_scores
- `app/ml/inference/inference_engine.py`: `InferenceEngine.calculate()` with `_apply_scale_adjustments()` via SCALE_DISORDER_MAP + `_apply_ml_scale_prediction()` via heuristic risk blending
- `app/ml/inference/confidence_calculator.py`: `calculate_criteria_confidence()` function
- `app/ml/models/assessment_scales.py`: 21 ScaleDefinitions + SCALE_DISORDER_MAP
- `app/ml/predictors/personality_factors.py`: per-factor BFP/DT-12 extraction from question-level response data
- `app/ml/predictors/scale_predictor.py`: `predict_personality_from_scales()`, `predict_disorder_risk_from_scales()`, `build_personality_feature_vector()`
- `app/ml/training/train_personality_models.py`: `train_personality_model()` with multi-output regression
- `app/api/v1/ml/scale_predictions.py`: scale ML API endpoints (personality prediction, disorder risk)
- `app/api/v1/clinical/assessments.py`: `GET /patient/{patient_uuid}/personality-factors` endpoint
- `app/services/consultation_service.py`: `list_all_consultations()` decrypts patient name
- `app/services/assessment_service.py`: `get_patient_assessment_history()`
- `app/services/integrity_service.py`: `ClinicalIntegrityService` with 15+ validation methods

### Models
- `app/models/base.py`: `Disorder`, `ICD11Code`, `DiagnosticCriteria`, `CriteriaGroup`, `CriteriaRule`, `ScaleResponse`, `ClassificationAuthority`, `ProfessionalPatientAssignment`, `Symptom`

### Schemas
- `app/schemas/consultation.py`: `ClinicalConsultationResponse` model_validator decrypts patient name
- `app/schemas/admin.py`: `AdminUserUpdate` with `username: Optional[str]`
- `app/schemas/disorder.py`: DSM-column fields, ICD11Code/Exclusion/Differential responses
- `app/schemas/professional.py`: `HealthcareProfessionalCreate/Update` with `assigned_patient_uuids`
- `app/schemas/patient_profile.py`: `@field_validator("birth_date")` future-date rejection

### Frontend Pages
- `mind-ui/src/pages/dashboard/DashboardPage.tsx`: 5-tab demographics card (Sexo, Gênero, Idade, Escolaridade, Etnia)
- `mind-ui/src/pages/inferences/InferencePage.tsx`: symptom groups (14 categories), patient inference history
- `mind-ui/src/pages/assessments/AssessmentPage.tsx`: patient selector, scale history
- `mind-ui/src/pages/consultations/ConsultationListPage.tsx`: patient name + UUID
- `mind-ui/src/pages/consultations/ConsultationDetailPage.tsx`: patient name prominent at top
- `mind-ui/src/pages/admin/DisordersPage.tsx`: full DSM-5-TR catalog grouped by chapter, core/reference tags, collapsible DSM/ICD criteria, exclusions, differentials
- `mind-ui/src/pages/professionals/ProfessionalsPage.tsx`: patient assignment multi-select
- `mind-ui/src/pages/admin/UsersPage.tsx`: edit modal with username field
- `mind-ui/src/pages/personality/PersonalityPage.tsx`: BFP factor + DT-12 subscale display, real per-factor progress bars, radar chart, ML prediction fallback with data source badge, feature scales card

### Frontend API
- `mind-ui/src/api/chatbot.ts`, `inferences.ts`, `consultations.ts`, `scales.ts`, `metrics.ts`, `disorders.ts`, `patients.ts`
- `mind-ui/src/types/index.ts`: `ChatResponse`, `TranstornoResultado`, `DemographicsResponse`, `ConsultationResponse`, `PersonalityFactorsResponse`, `DisorderRiskResponse`

### Seeds & Scripts
- `db/seed.py`: base reference data, disorders, criteria, professionals, users
- `scripts/seed_icd11.py`: ICD-11 codes with `SHORT_TO_PT` mapping
- `scripts/seed_scales_groups.py`: assessment scales + criteria groups
- `scripts/seed_diagnostic_data.py`: DSM-5-TR criteria, ICD-11/DSM-5 exclusions + differentials
- `scripts/seed_clinical_data.py`: clinical dataset generation with `_generate_scale_responses()` — supports full seed and re-seed modes (idempotent)
- `scripts/seed_full_catalog.py`: full DSM-5-TR catalog activation — seeds criteria text, ICD-11 exclusion/differential data, diagnosis relationships, and Phase 4 (DiagnosticCriteria); contains `DSM5TR_ALL` dict (~111 entries), `REFERENCE_RELATIONSHIPS` (94 entries), `_NAME_MAP` for name resolution, and `seed()` function
- `scripts/reference_symptom_data.py`: `REFERENCE_SYMPTOM_MAP` dict (426 symptom keys across 109 disorders) consumed by `seed_full_catalog.py` Phase 4
- `scripts/check_integrity.py`: data quality CLI reporter
- `scripts/dsm5tr_data.py`: full DSM-5-TR disorder catalog (~192 entries across 22 chapters), used by `db/seed.py`

### DW ETL
- `app/etl/dw_loader.py`: `run_full_etl()` with `load_dim_scale()`, `load_fact_scale_response()` — loads all 20 scales

### Spark
- `spark/config.py`, `spark/submit.py`, `spark/jobs/population_metrics.py`, `spark/jobs/batch_inference.py`, `spark/jobs/data_import.py`
- `postgresql-42.7.1.jar`: PostgreSQL JDBC driver for Spark
- `requirements-spark.txt`: production deps without scipy/numpy/pandas (Python 3.8 compatible)

### Migrations
- `migrations/versions/b3c4d5e6f7a8_add_clinical_notes_table.py`, `c1d2e3f4a5b6_add_clinical_check_constraints.py`, `d4e5f6a7b8c9_add_classification_authorities.py`, `e5f6a7b8c9d0_add_professional_patient_assignments.py`

## Error Log

### E01 — Frontend port conflict (vite.config.js port 3000 vs vite.config.ts proxy)
**Sintoma**: Login redireciona para localhost:3000 que não responde.
**Causa**: `vite.config.js` (porta 3000) e `vite.config.ts` (proxy /api → 8000) coexistiam; Vite usava o `.js`.
**Solução**: Deletar `vite.config.js` e `vite.config.d.ts`. Manter apenas `vite.config.ts`.

### E02 — ModuleNotFoundError: No module named 'app'
**Sintoma**: Scripts (seed, alembic) não encontram `app`.
**Causa**: Pacote `mind-cdss` não instalado em modo editable.
**Solução**: `pip install -e . --no-deps`

### E03 — .venv com wheels corrompidos (pydantic_core, psycopg2)
**Sintoma**: `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` ou `psycopg2._psycopg`.
**Causa**: Binários C compilados para versão diferente do Python; `.venv` danificado.
**Solução**: Reinstalar pacotes nativos: `pip install --force-reinstall pydantic-core psycopg2-binary fpdf2 passlib`

### E04 — Alembic UnicodeDecodeError / password wrong
**Sintoma**: `UnicodeDecodeError` ao rodar `alembic upgrade head`.
**Causa**: `DATABASE_URL` com senha placeholder `SUA_SENHA_AQUI` e PostgreSQL não rodando.
**Solução**: Corrigir senha em `.env`; iniciar PostgreSQL.

### E05 — Docker build: bitnami/spark image not found
**Sintoma**: `docker compose build` falha com `bitnami/spark:3.5.0 not found`.
**Causa**: Bitnami removeu a imagem do Docker Hub.
**Solução**: Substituir por `apache/spark:3.5.0` e ajustar env vars.

### E06 — Docker build lento (instalação de dependências pesadas)
**Sintoma**: Build de `airflow` e `spark` excede timeout.
**Causa**: `requirements.txt` inclui PySpark (~455MB), DVC, MLflow, PyMC, Airflow.
**Solução**: Criar `requirements-prod.txt` com apenas o necessário para produção.

### E07 — TypeScript errors travando Docker build
**Sintoma**: Frontend build falha com TS errors.
**Causa**: Tipagens ausentes, componentes deprecated.
**Solução**: Corrigir tipagens e componente `<Text block>` → `<Text style={{ display: 'block' }}>`.

### E08 — Alembic migration falha em DB fresco (schema não existe)
**Sintoma**: `psycopg2.errors.InsufficientPrivilege: permission denied to create schema`.
**Causa**: Migrations não criam schemas nem tabelas ausentes.
**Solução**: Adicionar `CREATE SCHEMA IF NOT EXISTS` e `op.create_table()` com `inspector.has_table()`.

### E09 — entrypoint.sh CRLF line endings
**Sintoma**: Container reinicia com `exec ./entrypoint.sh: no such file or directory`.
**Causa**: Arquivo com `\r\n` (Windows). Shebang `#!/bin/sh\r` não executável no Linux.
**Solução**: Converter para LF.

### E10 — ML imports quebram startup (mlflow, sklearn, xgboost)
**Sintoma**: Uvicorn falha com `ModuleNotFoundError: No module named 'mlflow'`.
**Causa**: Imports no nível do módulo de pacotes não instalados em produção.
**Solução**: Usar lazy imports dentro dos endpoints.

### E11 — pgAdmin reject email (.local / .localhost TLD)
**Sintoma**: pgAdmin rejeita `admin@mind.local`.
**Causa**: pgAdmin 8+ valida email e rejeita TLDs especiais.
**Solução**: Usar `admin@mind.example.com`.

### E12 — Logo em branco (logo.png servindo index.html)
**Sintoma**: Logo do login aparece como quadrado vazio.
**Causa**: SPAFallbackMiddleware retorna index.html para 404 de arquivos estáticos.
**Solução**: Verificar `os.path.isfile()` antes de cair no SPA fallback.

### E13 — Página em branco após login
**Sintoma**: Login bem-sucedido, mas tela fica branca.
**Causas**: ProtectedRoute retorna null, CSP sem `'unsafe-eval'`, sem ErrorBoundary.
**Solução**: ProtectedRoute mostra Spin em vez de null; CSP adiciona `'unsafe-eval'`; ErrorBoundary envolve BrowserRouter.

### E14 — Cannot convert undefined or null to object
**Sintoma**: ErrorBoundary exibe erro em `Object.entries(demographics.gender_identity_distribution)`.
**Causa**: `gender_identity_distribution` undefined no response de 0 pacientes.
**Solução**: Adicionar `gender_identity_distribution: {}` ao retorno vazio; usar optional chaining.

### E15 — HTTPS setup com mkcert + Caddy
**Sintoma**: Necessário HTTPS local para cadeado verde.
**Solução**: Instalar mkcert, gerar certificado para `mind.local`, adicionar ao hosts, configurar Caddy.

### E16 — favicon.svg inexistente
**Sintoma**: Erro 404 para `/favicon.svg`.
**Causa**: `index.html` referencia `/favicon.svg` mas arquivo não existe.
**Solução**: Trocar para `<link rel="icon" type="image/png" href="/logo.png">`.

### E17 — Caddy 502 Bad Gateway após restart
**Sintoma**: `https://mind.local` retorna 502.
**Causa**: Caddy tenta conectar na API antes dela estar pronta.
**Solução**: Aguardar API ficar healthy; `docker compose restart caddy` se persistir.

### E18 — dvc-postgres package does not exist
**Sintoma**: `pip install dvc-postgres` falha.
**Causa**: Pacote não existe no PyPI; suporte PostgreSQL é via `dvc[postgres]`.
**Solução**: Usar `dvc[postgres]>=3.48.0`.

### E19 — CORS bloqueando após deploy com proxy
**Sintoma**: Requisições cross-origin bloqueadas.
**Causa**: Origem muda com Caddy em produção.
**Solução**: Manter `connect-src 'self'` no CSP; ajustar `CORS_ORIGINS`.

### E20 — Spark JDBC driver ClassNotFound / wrong table names
**Sintoma**: Spark falha com `ClassNotFoundException: org.postgresql.Driver` ou `relation "X" does not exist`.
**Causa 1**: Driver JAR não montado.
**Solução 1**: Baixar `postgresql-42.7.1.jar` e montar em `/opt/spark/work-dir/`.
**Causa 2**: Nomes de schema/tabela errados.
**Solução 2**: Usar `clinical.patient_profile`, `diagnostic.disorders`, etc.

### E21 — Inference engine NameError (calculate_criteria_confidence)
**Sintoma**: Inferências retornam erro 500; `NameError: name 'calculate_criteria_confidence' is not defined`.
**Causa**: `app/ml/inference/inference_engine.py` linha 75 chama função sem import.
**Solução**: Adicionar `from app.ml.inference.confidence_calculator import calculate_criteria_confidence`.

### E22 — Explanation endpoint undefined variable (scale_scores)
**Sintoma**: `GET /api/v1/inferences/{uuid}/explanation` retorna erro 500.
**Causa**: `get_explanation()` em `inference_service.py` referencia `scale_scores` que não está no escopo.
**Solução**: Adicionar lógica de consulta de scale_scores dentro do método.

### E23 — Dashboard charts não aparecem (education_level_distribution / ethnicity_distribution ausentes)
**Sintoma**: Gráficos de Escolaridade e Etnia no dashboard não renderizam.
**Causa**: `/api/v1/metrics/demographics` usa `StatisticsService` (`app/analytics/statistics/service.py`) que não retornava `education_level_distribution` nem `ethnicity_distribution`. O `MetricsService` (`app/services/metrics_service.py`) tinha os campos, mas não era o service usado pelo endpoint.
**Solução**: Adicionar queries de EducationLevel e Ethnicity no `StatisticsService.get_patient_demographics()` e incluir ambos no return dict.
