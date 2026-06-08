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
- Run Alembic migrations + seed scripts in correct order: `alembic upgrade head` → `python db/seed.py` → `python scripts/seed_icd11.py` → `python scripts/seed_diagnostic_data.py`.

## Critical Context
- **Python 3.14.5** is the active runtime; install security tools via `python -m pip install bandit safety`.
- **Bandit scan command**: `python -m bandit -c .bandit -r app/ scripts/ db/` — zero issues after fixes.
- **19 Portuguese disorder names** complete: Transtorno Depressivo Maior, T. Ansiedade Generalizada, T. Pânico, T. Estresse Pós-Traumático, T. Depressivo Persistente (Distimia), T. Ansiedade Social, T. Bipolar Tipo I/II, T. Obsessivo-Compulsivo, Agorafobia, T. Uso Substâncias, Anorexia Nervosa, Bulimia Nervosa, T. Compulsão Alimentar, T. Insônia, Esquizofrenia/T. Psicótico, T. Sintomas Somáticos, TEA, TDAH.
- **DW ETL** truncates all tables in FK-safe order at start. Run with `python -c "from app.etl.dw_loader import run_full_etl; run_full_etl()"`.
- **Alembic chain**: `05ecbb7b2bc1` (initial) → … → `c1d2e3f4a5b6` (CHECK constraints) → `d4e5f6a7b8c9` (authorities + DSM columns) → `e5f6a7b8c9d0` (professional assignments). Head is `e5f6a7b8c9d0`.
- **Seed order**: `db/seed.py` (authorities + base data) → `scripts/seed_icd11.py` → `scripts/seed_scales_groups.py` → `scripts/seed_diagnostic_data.py` (criteria/exclusions/differentials). All seeds now idempotent.

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
