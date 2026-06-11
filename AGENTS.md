## Goal
- Transform MVP into a hardened CDSS with formal diagnostic engine, probabilistic Bayesian inference, clinical DW, RBAC, LGPD compliance, full ML pipeline (4 objectives × 3 algorithms), fully populated clinical reference data (DSM-5-TR, ICD-11, APA/WHO authorities, criteria/exclusions/differentials, scales, medications), professional CRM/CRP management with patient assignments, and multi-layer clinical data integrity validation.

## Constraints & Preferences
- LGPD compliance for mental health data (consent, pseudonymization, encryption, audit, retention).
- DSM-5-TR and ICD-11 as formal clinical criteria sources; APA and WHO as first-class classification authorities.
- Portuguese (BR) as project language — all 19 disorder names unified to Portuguese, API field `profissional_license` for CRM/CRP.
- Diagnostic engine: rule-based + probabilistic dual pipeline.
- DW star schema, separate from transactional DB.
- ML: Logistic Regression, Random Forest, XGBoost — no deep learning.
- MLOps: MLflow + DVC for registry, tracking, versioning.
- Clinical validation enforced at 3 layers: Pydantic schema → service business rules → DB CHECK constraints.

## Progress
### Done
- **Disorder naming unified to Portuguese (BR, 19 disorders)** — `scripts/seed_clinical_data.py` updated: `DISORDER_DEFS` uses Portuguese names, `BN_TO_PT` mapping bridges Bayesian network English → DB Portuguese, scale severity checks check for "Depressiv"/"Ansiedade", inference lookup uses `BN_TO_PT.get()`. 9 English-named disorders renamed in-place, 10 added. `db/seed.py` updated: disorder list and `criteria_map` keys changed to Portuguese names. **Transtorno Depressivo Maior** added as 19th disorder (F32.9, 296.22).
- **Clinical dataset rebuilt**: `data/datasets/clinical_dataset.csv` (187 rows, 31 columns) with Portuguese disorder names.
- **DW ETL reloaded**: 19 Portuguese disorders in `dim_disorder`, 930 diagnoses, 885 symptoms, 50 patients, 187 consultations, 2 scales (PHQ-9, GAD-7 with 374 responses).
- **SSD (Secure Software Development) certification implemented**: security middlewares (CSP, HSTS, rate-limit 100 req/min, SQL injection blocking), Bandit-Safety-CI pipeline, `.pre-commit-config.yaml`, `SECURITY.md`, Bandit zeroed.
- **Login fixed**: `VITE_API_URL=/api/v1` (path match), frontend rebuilt, login + `/auth/me` verified.
- **Base reference data seeded**: sex types, gender identities, education levels, ethnicities, 113 symptoms, 19 disorders, diagnostic criteria, relationships, 1 professional, 5 users, 20 medications.
- **CID-11 codes, criteria groups, scales seeded**: 19 ICD-11 codes, 29 criteria groups/29 rules/30 thresholds, 10 assessment scales (PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10).
- **ML pipeline**: 12 models (4 objectives × 3 algorithms) trained, registered in MLflow, promoted to Production.
- **Clinical integrity system complete**:
  - `ClinicalIntegrityService`: validates patients (birth date, age ≤ 120), consultations (date not future, min age 3), symptoms (intensity 0–10, duration ≥ 1, valid frequencies), scale responses (value 0–10), inferences (probability/confidence 0–1, sum ≤ 1.0), plus `full_report()` for bulk integrity reporting.
  - Pydantic validators added to `patient_profile.py` (birth_date future reject) and `consultation.py` (consultation_date future reject, intensity 0–10, frequency enum, duration_days ≥ 1, response_value 0–10).
  - Alembic migration `c1d2e3f4a5b6`: 7 DB CHECK constraints (birth_date ≤ today, intensity 0–10, duration_days ≥ 1, valid frequencies, response_value 0–10, probability/confidence 0–1).
  - `scripts/check_integrity.py`: CLI data quality reporter, outputs JSON report.
- **Classification authorities implemented**:
  - `ClassificationAuthority` model: WHO (authority_id=1) and APA (authority_id=2) with name, short_name, website_url.
  - `authority_id` FK added to `ICD11Code` linking ICD-11 codes to WHO.
  - Migration `d4e5f6a7b8c9`: creates table + FK + 5 new `Disorder` columns.
- **DSM-5-TR criteria data mined and seeded**:
  - `scripts/seed_diagnostic_data.py`: full DSM-5-TR diagnostic criteria, ICD-11 exclusions, ICD-11 differentials, DSM-5-TR exclusions, DSM-5-TR differentials for all 19 disorders.
  - Columns added to `Disorder`: `dsm_criteria`, `dsm_exclusions`, `dsm_differentials`, `icd11_exclusions`, `icd11_differentials`.
  - ICD-11 exclusion and differential records populated from parsed data.
  - `seed_icd11.py` fixed: uses `SHORT_TO_PT` mapping for Portuguese disorder names.
- **Professional management with patient assignments**:
  - `ProfessionalPatientAssignment` model (professional_uuid × patient_uuid, unique constraint, active flag).
  - Migration `e5f6a7b8c9d0`: creates `professional_patient_assignments` table in `clinical` schema.
  - `app/api/v1/clinical/professionals.py` updated: `_sync_assignments()` manages caseload on create/update, `_enrich_assignments()` adds patient name to response.
  - Schemas updated: `HealthcareProfessionalCreate/Update` accept `assigned_patient_uuids`, `HealthcareProfessionalResponse` includes `patient_assignments` with patient name.
  - The existing fields `professional_license` (CRM/CRP), `profession`, `specialty`, `start_date` were already in the model and schema — now fully functional via API routes.
- **Professional form UI completed**: `ProfessionalsPage.tsx` now has multi-select "Pacientes Associados" with search, and "Pacientes" column in table showing count badge.
- **Disorders admin page enhanced**: `DisordersPage.tsx` now shows DSM-5-TR criteria, exclusions, differentials (DSM-5 and ICD-11) as collapsible panels in the expanded row.
- **Inference page overhauled**: `InferencePage.tsx` now groups 113 symptoms into 14 clinical categories (Depressão, Ansiedade, Pânico, Bipolar, TOC, PTSD, Substâncias, Alimentar, Sono, Psicótico, Somático, Agorafobia, TEA, TDAH) with color-coded collapsible sections and per-group counters. Added patient inference history panel loading on patient select. Tooltip on probability column.
- **Assessment page enhanced**: `AssessmentPage.tsx` now includes patient selector and "Histórico do Paciente" panel showing all past scale scores with date, scale name, and color-coded score. Auto-refreshes history after scoring.
- **Patient-scale history API**: `GET /api/v1/assessments/patient/{patient_uuid}/history` — aggregates scale scores per consultation for a patient. Backend: `assessment_service.get_patient_assessment_history()`.
- **Frontend API additions**: `inferencesApi.listByConsultation()`, `consultationsApi.listByProfile()`, `scalesApi.patientHistory()`.
- **All seeds idempotent**: `db/seed.py` skips sections if data already exists. Migration `b3c4d5e6f7a8` (`add_clinical_notes_table`) made idempotent with inspector check. All disorder name mismatches fixed in criteria_map keys and relationships (accents, hyphens).
- **Spark container operational**:
  - `docker/spark/Dockerfile` uses `apache/spark:3.5.0` (Python 3.8-compatible) with `requirements-spark.txt` (no scipy/numpy/pandas which are incompatible with CPython 3.8).
  - `spark/config.py` uses `PG_HOST` env var (defaults to `mind-postgres`) instead of hardcoded `localhost`.
  - `postgresql-42.7.1.jar` (1 MB) downloaded for PostgreSQL JDBC connectivity; mounted at `/opt/spark/work-dir/postgresql-42.7.1.jar`.
  - All Spark job schema/table references fixed to match actual DB: `clinical.patient_profile`, `diagnostic.diagnostic_inference`, `diagnostic.disorders`, `clinical.scale_responses`, `diagnostic.scale_questions`, `diagnostic.assessment_scales`; also `security.patient_identity` and `diagnostic.symptoms` in `data_import.py`.
  - `spark/submit.py` adds `sys.path.insert(0, ...)` so `from spark.jobs import ...` resolves.
  - Spark jobs run with `--driver-class-path /opt/spark/work-dir/postgresql-42.7.1.jar` on `mind_mind-network` with `PG_HOST=mind-postgres`.
  - `population_metrics` job verified: connects via JDBC, reads all 6 tables, computes age distribution + disorder prevalence + scale statistics, exits cleanly (exit code 0).

### In Progress
- *(none)*

### Blocked
- *(none)*

## Key Decisions
- Disorder unification done via `scripts/seed_clinical_data.py` as single source of truth for all 19 Portuguese disorders — `scripts/unify_disorders_pt.py` was a one-time migration script (since deleted).
- BN disorder names remain English internally; `BN_TO_PT` mapping in seed script bridges to DB Portuguese names.
- Security scanning integrated into CI pipeline, not just local — ensures blocking on PRs.
- Rate limiting is in-memory (not Redis) — sufficient for single-container deployment; upgrade to Redis if horizontally scaled.
- Clinical validation uses 3 defense layers: Pydantic (input) → IntegrityService (business) → DB CHECK constraints (storage).
- APA and WHO stored as `ClassificationAuthority` records — all future classification systems (e.g., future ICD-12) can reuse the same structure.
- Patient–professional assignments use explicit `professional_patient_assignments` table (not inferred from consultation history) to support caseload management independent of clinical activity.
- Symptom categorization on InferencePage uses a static `SYMPTOM_GROUPS` map keyed by symptom name — keeps grouping logic in the UI without backend changes.

## Next Steps
- Add remaining 8 scale scores (MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10) to clinical dataset (currently only PHQ-9/GAD-7).
- Create analytics views/queries on DW (prevalence trends, comorbidity heatmaps, score distributions).
- Add API tests for professionals routes (assignment CRUD, assignment sync edge cases).
- Run clinical data seeds in `mind` database so Spark jobs have non-zero data to analyze.
- Run Alembic migrations + seed scripts in correct order: `alembic upgrade head` → `python db/seed.py` → `python scripts/seed_icd11.py` → `python scripts/seed_diagnostic_data.py`.

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

## Critical Context
- **Python 3.14.5** is the active runtime; install security tools via `python -m pip install bandit safety`.
- **Bandit scan command**: `python -m bandit -c .bandit -r app/ scripts/ db/` — zero issues after fixes.
- **19 Portuguese disorder names** complete: Transtorno Depressivo Maior, T. Ansiedade Generalizada, T. Pânico, T. Estresse Pós-Traumático, T. Depressivo Persistente (Distimia), T. Ansiedade Social, T. Bipolar Tipo I/II, T. Obsessivo-Compulsivo, Agorafobia, T. Uso Substâncias, Anorexia Nervosa, Bulimia Nervosa, T. Compulsão Alimentar, T. Insônia, Esquizofrenia/T. Psicótico, T. Sintomas Somáticos, TEA, TDAH.
- **DW ETL** truncates all tables in FK-safe order at start. Run with `python -c "from app.etl.dw_loader import run_full_etl; run_full_etl()"`.
- **Alembic chain**: `05ecbb7b2bc1` (initial) → … → `c1d2e3f4a5b6` (CHECK constraints) → `d4e5f6a7b8c9` (authorities + DSM columns) → `e5f6a7b8c9d0` (professional assignments). Head is `e5f6a7b8c9d0`.
- **Seed order**: `db/seed.py` (authorities + base data) → `scripts/seed_icd11.py` → `scripts/seed_scales_groups.py` → `scripts/seed_diagnostic_data.py` (criteria/exclusions/differentials). All seeds now idempotent.
- **Spark jobs**: run via `docker run --rm --network mind_mind-network ... --entrypoint /opt/spark/bin/spark-submit mind-spark /app/spark/submit.py <job_name>`
- **`postgresql-42.7.1.jar`** must be mounted at `/opt/spark/work-dir/postgresql-42.7.1.jar` for JDBC; use `--driver-class-path` option with `spark-submit`

## Relevant Files
- `app/services/assessment_service.py`: `get_patient_assessment_history()` — queries scale scores per patient across consultations
- `app/api/v1/clinical/assessments.py`: `GET /api/v1/assessments/patient/{patient_uuid}/history` endpoint
- `app/services/integrity_service.py`: `ClinicalIntegrityService` with 15+ validation methods
- `scripts/check_integrity.py`: data quality CLI, outputs JSON report to `data/reports/clinical_integrity_report.json`
- `migrations/versions/b3c4d5e6f7a8_add_clinical_notes_table.py`: made idempotent (inspector check)
- `migrations/versions/c1d2e3f4a5b6_add_clinical_check_constraints.py`: 7 DB CHECK constraints
- `migrations/versions/d4e5f6a7b8c9_add_classification_authorities.py`: authorities table + DSM columns
- `migrations/versions/e5f6a7b8c9d0_add_professional_patient_assignments.py`: professional–patient assignment table
- `app/models/base.py`: `ClassificationAuthority`, `ProfessionalPatientAssignment`, DSM columns on `Disorder`, `authority_id` on `ICD11Code`
- `app/schemas/professional.py`: `HealthcareProfessionalCreate/Update` with `assigned_patient_uuids`; `HealthcareProfessionalResponse` with `patient_assignments` (incl. patient name); `PatientAssignmentResponse`
- `app/api/v1/clinical/professionals.py`: CRUD routes with `_sync_assignments()` and `_enrich_assignments()`
- `app/schemas/disorder.py`: `ClassificationAuthorityResponse`, `ICD11CodeResponse`, `ICD11ExclusionResponse`, `ICD11DifferentialResponse`, DSM-column fields in `DisorderBase/Update/Response`
- `app/schemas/patient_profile.py`: `@field_validator("birth_date")` future-date rejection
- `app/schemas/consultation.py`: validators for consultation_date, intensity 0–10, frequency enum, duration_days ≥ 1, response_value 0–10
- `scripts/seed_diagnostic_data.py` (new): seeds full DSM-5-TR criteria + ICD-11/DSM-5 exclusions + differentials for 19 disorders
- `scripts/seed_icd11.py`: fixed with `SHORT_TO_PT` mapping
- `db/seed.py`: seeds `ClassificationAuthority` (WHO, APA) + added `Transtorno Depressivo Maior` as 19th disorder; all sections idempotent; disorder name mismatches fixed
- `mind-ui/src/pages/inferences/InferencePage.tsx`: symptom grouped into 14 categories with collapsible sections, patient inference history panel
- `mind-ui/src/pages/assessments/AssessmentPage.tsx`: patient selector, scale history display, auto-refresh after scoring
- `mind-ui/src/pages/admin/DisordersPage.tsx`: collapsible DSM-5/ICD-11 criteria, exclusions, differentials
- `mind-ui/src/pages/professionals/ProfessionalsPage.tsx`: patient assignment multi-select, count badge column
- `mind-ui/src/api/inferences.ts`: added `listByConsultation()`
- `mind-ui/src/api/consultations.ts`: added `listByProfile()`
- `mind-ui/src/api/scales.ts`: added `patientHistory()`
- `mind-ui/src/types/index.ts`: `Disorder`, `DisorderResponse`, `HealthcareProfessionalResponse` extended with new fields
- `spark/config.py`: `PG_HOST` env var instead of hardcoded `localhost`
- `spark/submit.py`: added `sys.path.insert(0, ...)` so `from spark.jobs import ...` works
- `spark/jobs/population_metrics.py`: JDBC reads from `clinical.patient_profile`, `diagnostic.diagnostic_inference`, `diagnostic.disorders`, `clinical.scale_responses`, `diagnostic.scale_questions`, `diagnostic.assessment_scales`
- `spark/jobs/batch_inference.py`: JDBC batch inference engine reading `clinical.clinical_consultation`, `clinical.symptom_observation`, `diagnostic.disorders`
- `spark/jobs/data_import.py`: bulk CSV import into `security.patient_identity`, `clinical.patient_profile`, `diagnostic.symptoms`
- `postgresql-42.7.1.jar`: PostgreSQL JDBC driver for Spark (1 MB)
- `requirements-spark.txt`: production deps without scipy/numpy/pandas (Python 3.8 compatible)

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
**Solução**: Corrigir senha em `.env` para `137_Cmspelo`; iniciar PostgreSQL.

### E05 — Docker build: bitnami/spark image not found
**Sintoma**: `docker compose build` falha com `bitnami/spark:3.5.0 not found`.
**Causa**: Bitnami removeu a imagem do Docker Hub.
**Solução**: Substituir por `apache/spark:3.5.0` e ajustar env vars para Apache Spark default.

### E06 — Docker build lento (instalação de dependências pesadas)
**Sintoma**: Build de `airflow` e `spark` excede timeout.
**Causa**: `requirements.txt` inclui PySpark (~455MB), DVC, MLflow, PyMC, Airflow.
**Solução**: Criar `requirements-prod.txt` com apenas o necessário para produção. Containers usam este arquivo.

### E07 — TypeScript errors travando Docker build
**Sintoma**: Frontend build falha com TS errors.
**Causa**: `MedicationsPage.tsx` — `error` sem tipo, `onFilter` sem `value: unknown`, `classifications` sem type guard. `PatientTimelinePage.tsx` — `<Text block>` não existe no antd; deve ser `<Text style={{ display: 'block' }}>`.
**Solução**: Corrigir tipagens e componente deprecated.

### E08 — Alembic migration falha em DB fresco (schema não existe)
**Sintoma**: `psycopg2.errors.InsufficientPrivilege: permission denied to create schema` ou `relation "diagnostic.icd11_codes" does not exist`.
**Causa**: Migration inicial (`05ecbb7b2bc1`) não cria os schemas (`audit`, `clinical`, `ml`, `diagnostic`, `security`, `core`). Migration `d4e5f6a7b8c9` referência `icd11_codes` sem tê-la criado.
**Solução**: Adicionar `CREATE SCHEMA IF NOT EXISTS` para todos os 6 schemas na migration inicial. Adicionar `op.create_table("icd11_codes", ...)` na migration `d4e5f6a7b8c9`. Tornar ambas idempotentes com `inspector.has_table()`.

### E09 — entrypoint.sh CRLF line endings
**Sintoma**: Container reinicia com `exec ./entrypoint.sh: no such file or directory`.
**Causa**: Arquivo com `\r\n` (Windows). Shebang `#!/bin/sh\r` não é executável no Linux.
**Solução**: Converter para LF: `Get-Content entrypoint.sh -Raw | % { $_ -replace "\`r\`n", "\`n" } | Set-Content entrypoint.sh -NoNewLine -Encoding ASCII`

### E10 — ML imports quebram startup (mlflow, sklearn, xgboost)
**Sintoma**: Uvicorn falha com `ModuleNotFoundError: No module named 'mlflow'`.
**Causa**: `app/api/v1/ml/training.py` importa `Trainer` no módulo, que importa `mlflow`, `sklearn`, `xgboost` — pacotes não instalados no container de produção.
**Solução**: Mover imports para dentro dos endpoints (lazy import):
```python
@router.post("/train")
def train_model(...):
    from app.ml.training.trainer import Trainer  # lazy
```

### E11 — pgAdmin reject email (.local / .localhost TLD)
**Sintoma**: pgAdmin reinicia com `'admin@mind.local' does not appear to be a valid email address`.
**Causa**: pgAdmin 8+ valida email e rejeita TLDs especiais (`.local`, `.localhost`, `.example`).
**Solução**: Usar `admin@mind.example.com`.

### E12 — Logo em branco (logo.png servindo index.html)
**Sintoma**: Logo do login aparece como quadrado vazio.
**Causa**: `app/main.py` monta apenas `/assets` como static files. `/logo.png` não é servido → 404 → SPAFallbackMiddleware retorna `index.html` (HTML renderizado como imagem).
**Solução**: Modificar SPAFallbackMiddleware para verificar se o arquivo existe no `dist/` antes de cair no SPA:
```python
if response.status_code == 404 and not request.url.path.startswith("/api/"):
    file_path = os.path.join(frontend_dir, request.url.path.lstrip("/"))
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_dir, "index.html"))
```

### E13 — Página em branco após login
**Sintoma**: Login bem-sucedido, mas tela fica branca.
**Causas múltiplas**:
1. **ProtectedRoute retorna `null`**: após login, `user` ainda não carregou no store → `if (!user) return null`.
2. **CSP bloqueia React**: `script-src` sem `'unsafe-eval'` — React usa `eval()` internamente.
3. **Sem ErrorBoundary**: qualquer erro de renderização desmonta a árvore React inteira.
**Soluções**:
1. `ProtectedRoute.tsx`: Trocar `if (!user) return null` por `if (loading || (!user && token)) return <Spin />`
2. `index.html`: Adicionar `'unsafe-eval'` ao CSP; adicionar `ws:` ao `connect-src`
3. `App.tsx`: Envolver `<BrowserRouter>` em `<ErrorBoundary>` com botão "Recarregar"

### E14 — Cannot convert undefined or null to object
**Sintoma**: ErrorBoundary exibe "Erro na aplicação: Cannot convert undefined or null to object".
**Causa**: `DashboardPage.tsx:69` — `Object.entries(demographics.gender_identity_distribution)` e `demographics` é um objeto não-nulo, mas `gender_identity_distribution` está `undefined` (API não retorna esse campo quando não há pacientes).
**Solução**:
1. Backend (`statistics/service.py`): Adicionar `gender_identity_distribution: {}` ao retorno de 0 pacientes.
2. Frontend (`DashboardPage.tsx`): Trocar `demographics ? Object.entries(...)` por `demographics?.sex_distribution ? Object.entries(...)` — fallback por campo, não por objeto inteiro. Usar optional chaining em `moving_avg_7d?.[date]`.

### E15 — HTTPS setup com mkcert + Caddy
**Sintoma**: Necessário HTTPS local para cadeado verde.
**Solução**:
1. Instalar mkcert: `winget install mkcert` (ou baixar do GitHub)
2. Instalar CA: `mkcert -install` (admin)
3. Gerar cert: `mkcert mind.local` → move para `certificates/`
4. Adicionar ao hosts: `127.0.0.1 mind.local` em `C:\Windows\System32\drivers\etc\hosts`
5. Adicionar Caddy ao `docker-compose.yml` como reverse proxy com TLS
6. CSP do servidor: adicionar `'unsafe-eval'` em `middleware/security_middleware.py` (cobre APIs via Caddy)

### E16 — favicon.svg inexistente
**Sintoma**: Erro 404 para `/favicon.svg` no console.
**Causa**: `index.html` referencia `/favicon.svg` mas `public/favicon.svg` não existe.
**Solução**: Trocar para `<link rel="icon" type="image/png" href="/logo.png">`.

### E17 — Caddy 502 Bad Gateway após restart
**Sintoma**: `https://mind.local` retorna 502 após `docker compose up -d --force-recreate`.
**Causa**: Caddy tenta conectar na API antes dela estar pronta (janela entre restart e healthy).
**Solução**: Aguardar API ficar healthy (segundos). Se persistir, `docker compose restart caddy`.

### E18 — dvc-postgres package does not exist
**Sintoma**: `pip install dvc-postgres` falha.
**Causa**: Pacote `dvc-postgres` não existe no PyPI. Suporte PostgreSQL é via `dvc[postgres]`.
**Solução**: Usar `dvc[postgres]>=3.48.0` em `requirements.txt`.

### E19 — CORS bloqueando após deploy com proxy
**Sintoma**: Requisições cross-origin bloqueadas.
**Causa**: `VITE_API_URL=/api/v1` resolve para `http://localhost:8000/api/v1/` via proxy, mas em produção com Caddy a origem muda.
**Solução**: Manter `connect-src 'self'` no CSP (frontend e API no mesmo domínio via Caddy). Ajustar `CORS_ORIGINS` em produção.

### E20 — Spark JDBC driver ClassNotFound / wrong table names
**Sintoma**: `docker run mind-spark` falha com `ClassNotFoundException: org.postgresql.Driver`.
**Causa 1**: Driver JAR (`postgresql-42.7.1.jar`) não baixado nem montado no container.
**Solução 1**: Baixar `postgresql-42.7.1.jar` (1 MB) do Maven Central para a raiz do projeto e montá-lo em `/opt/spark/work-dir/`:
```bash
curl -o postgresql-42.7.1.jar https://jdbc.postgresql.org/download/postgresql-42.7.1.jar
docker run ... -v "${PWD}\postgresql-42.7.1.jar:/opt/spark/work-dir/postgresql-42.7.1.jar:ro" ...
```
**Causa 2**: Container tenta conectar em `localhost:5432` (dentro do container) em vez do host `mind-postgres`.
**Solução 2**: `spark/config.py` usa `PG_HOST=os.getenv("PG_HOST", "mind-postgres")`; passar `-e PG_HOST=mind-postgres` no `docker run` e conectar à network `mind_mind-network`.

**Sintoma**: `PSQLException: relation "X" does not exist` para alguma tabela.
**Causa**: Spark jobs usam nomes schema.tabela errados (ex: `core.patient_profile` em vez de `clinical.patient_profile`, `diagnostic.disorder` em vez de `diagnostic.disorders`).
**Solução**: Mapear todos os schemas e tabelas reais no PostgreSQL (`\dt *.*` na DB `mind`). Tabelas corretas:
- `clinical.patient_profile`, `diagnostic.diagnostic_inference`, `diagnostic.disorders`
- `clinical.scale_responses`, `diagnostic.scale_questions`, `diagnostic.assessment_scales`
- `security.patient_identity`, `diagnostic.symptoms`
- `clinical.clinical_consultation`, `clinical.symptom_observation`
