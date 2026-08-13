# M.I.N.D — Documentação de Desenvolvimento

**Data:** Junho 2026
**Versão:** 0.2.2
**Status:** CDSS Completo — 12 fases implementadas
**Testes:** 548 (unitários + integração)
**Stack:** FastAPI + PostgreSQL 16 + React + Pandas + Airflow + PySpark + MLflow

---

## Diário de Desenvolvimento

### 2026-08-13 — API RESTful no frontend, vínculo sintoma–transtorno e versionamento
- **Versão 0.2.2** — bump de `0.2.1 → 0.2.2` em `pyproject.toml`, `app/core/config.py`, `app/api/v1/diagnostic/inferences.py`, `app/services/inference_service.py`, `.env.example` e `mind-ui/package.json`/`package-lock.json`.
- **Normalização da API no frontend:** `mind-ui/src/api/endpoints.ts` realinhado às rotas reais do backend — update de paciente via `PATCH /patients/{uuid}/profile`, consultas por perfil via `GET /consultations/patient/{profileUuid}`, detalhe de escala via `GET /assessments/detail/{name}`, scoring via `POST /assessments/score` e `POST /assessments/apply`, histórico via `GET /assessments/patient/{uuid}/history` e `/scale/{scaleName}`, inferências via `GET /inferences/{uuid}`, `POST /inferences/run` e `POST /inferences/bayesian`, senha de usuário via `PATCH /admin/users/{uuid}/password`, sintomas sob `/symptoms`, prescrições sob `/consultations/{uuid}/prescriptions` e `/prescriptions/{id}`, treatment/reports/timeline/alerts/audit com rotas aninhadas reais. Métodos mortos removidos (`updatePermission`, `listRoles`, `monitoring`, `search`). `DisordersPage` usa paginação (`limit: 300/600`); `ConsultationDetailPage` normaliza `rx?.prescriptions`.
- **Vínculo sintoma ↔ transtorno:** novo schema `SymptomDisorderLink` e campo `disorders` em `SymptomResponse`; `DisorderRepository.list_symptom_criteria()` (JOIN `DiagnosticCriteria` × `Disorder`) exposto via `DisorderService`.
- **ESLint + TypeScript:** `@typescript-eslint/eslint-plugin` + `parser` (devDependencies) e novo `.eslintrc.cjs`.
- **Test DB configurável:** `tests/conftest.py` lê `TEST_DATABASE_URL` do ambiente (com default) em vez de URL hardcoded.

---

### 2026-08-10 — Tema escuro (dark mode) no frontend
- **Novidade:** Implementado tema claro/escuro em toda a UI com toggle persistente entre sessões.
- **Arquivos novos:**
  - `mind-ui/src/store/themeStore.ts` — Zustand store com persistência em `localStorage` (chave `mind-theme`); aplica `data-theme` no `<html>`, `color-scheme` e cor de fundo do `<body>`.
  - `mind-ui/src/utils/chartTheme.ts` — hook `useChartTheme()` que mapeia tokens do Ant Design para gráficos Recharts (grid, ticks, tooltip).
- **Integrações:**
  - `App.tsx` — `ConfigProvider` alterna entre `theme.darkAlgorithm` e `theme.defaultAlgorithm` conforme `darkMode`.
  - `MainLayout.tsx` — botão lua/sol no header (toggle) + Sider com `theme="dark"`/`"light"` e bordas via token.
  - `LoginPage.tsx` — toggle de tema no canto superior direito.
  - `index.css` — estilos `html[data-theme='dark']` (fundo `#0f1115`, scrollbar escuro, transição de cores).
- **Páginas adaptadas:** Dashboard, Analytics, PatientDetail, PatientTimeline, Personality, Inference, Disorders e Mia (bubbles do bot) — cores via tokens (`colorBorderSecondary`, `colorFillSecondary`, `colorBgElevated`, `colorPrimaryBg`, `colorSplit`) e gráficos Recharts via `useChartTheme()`.
- **Build:** `npm run build` + `npx tsc --noEmit` sem erros.

---

## Stack Tecnológico

### Backend
- **FastAPI** — Framework web assíncrono
- **Python 3.14.5** — Linguagem principal
- **SQLAlchemy 2.0** — ORM
- **Pydantic v2** — Validação e serialização (3 camadas de validação clínica)

### Frontend
- **React 18** — UI components
- **TypeScript** — Tipagem estática
- **Vite 5** — Build tool e dev server
- **Ant Design 5** — Componentes UI (Table, Form, DatePicker, Layout)
- **Recharts** — Gráficos e dashboards
- **Zustand** — Gerenciamento de estado
- **Axios** — HTTP client com interceptor JWT

### Banco de Dados
- **PostgreSQL 16** — Relacional com schemas (`core`, `clinical`, `diagnostic`, `audit`, `admin`)
- **Alembic** — 21 revisões lineares
- **30+ tabelas** — Pacientes, profissionais, consultas, episódios, sintomas, transtornos, inferências, escalas, notas clínicas, medicações, prescrições, relatórios, auditoria, permissões, consentimento, autoridades de classificação, atribuições profissional-paciente, DW

### Inferência & ML
- **Motor de inferência dupla** — `app/ml/inference/`: critérios DSM-5-TR + Naive Bayes + ajuste por escalas + ML blending
- **21 escalas psicométricas** — 10 clínicas (PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10) + 11 neuropsicológicas/personalidade (BFP 25 itens, DT-12, MEMÓRIA, QI-RASTREIO, RECONHECIMENTO DE ROSTOS, FLUÊNCIA VERBAL, TESTE DO RELÓGIO, TRILHAS, STROOP, CANCELAMENTO, FIGURA COMPLEXA DE REY)
- **ML Pipeline** — 12 modelos (4 objetivos × 3 algoritmos: Logistic Regression, Random Forest, XGBoost)
- **MLflow** — Experiment tracking e model registry
- **DVC** — Versionamento de datasets

### Métricas & Analytics
- **Analytics consolidado** — `app/analytics/service.py`: demographics, BI, dashboards, métricas, ML dashboard
- **Pandas** — `app/services/metrics_service.py`: faixas etárias, moving averages, correlação de Pearson
- **Apache Airflow** — 4 DAGs (inferência em lote, qualidade, métricas, alertas)
- **PySpark 3.5** — 3 jobs (batch inference, population metrics, data import CSV)
- **Data Warehouse** — Star schema (`dim_disorder`, `dim_patient`, `dim_date`, `fact_diagnosis`, `fact_symptom`, `fact_consultation`, `fact_scale_response`)

### Segurança
- **JWT** — Login, refresh, verificação de token
- **RBAC** — 7 roles: `admin`, `clinician`, `viewer`, `psychiatrist`, `psychologist`, `researcher`, `clinical_supervisor`
- **Fernet AES** — Criptografia de campos sensíveis (LGPD)
- **Audit Middleware** — Log de todas as requisições a entidades clínicas
- **Security Middleware Stack** — CSP, HSTS (1 ano), Rate Limit (100 req/min), Proteção SQL Injection
- **Bandit SAST** — Zero issues
- **Safety CLI** — Verificação de dependências
- **Pre-commit hooks** — Security checks automatizados

### Administração
- **RolePermission** — Permissões granulares por role (7 roles: admin, clinician, viewer, psychiatrist, psychologist, researcher, clinical_supervisor)
- **RoutePermission** — Controle de acesso por rota
- **MonitorService** — Métricas de desempenho em tempo real (in-memory)
- **12+ endpoints** `/api/v1/admin/`

### Qualidade & DevOps
- **pytest** — 548 testes
- **black, isort** — Formatação
- **flake8, mypy** — Lint e tipos
- **GitHub Actions** — CI completo
- **Docker Compose** — 5 serviços

---

## Banco de Dados — Schemas

### `core`
- `patient_identity` — UUID, nome, CPF hash, email hash
- `patient_profile` — Data de nascimento, sexo, escolaridade, etnia (com CHECK constraints)
- `education_levels`, `ethnicities`, `gender_identities`, `sex_types` — Tabelas de domínio

### `clinical`
- `healthcare_professionals` — CRM/CRP, especialidade, profissão
- `professional_patient_assignments` — Atribuições profissional-paciente
- `consultations` — Consultas (motivo, anamnese, status)
- `clinical_notes` — Notas clínicas
- `clinical_episodes` — Episódios clínicos
- `episode_symptoms` — Sintomas por episódio (intensity 0-10, duration ≥ 1)
- `assessment_scales`, `scale_questions`, `scale_responses` — Escalas e respostas
- `medical_reports` — Relatórios médicos
- `medications`, `prescriptions`, `prescription_items` — Medicações
- `clinical_alerts` — Alertas clínicos

### `diagnostic`
- `classification_authorities` — APA (DSM-5-TR) e WHO (CID-11)
- `disorders` — 19 transtornos (DSM-5 criteria, exclusões, diferenciais)
- `icd11_codes` — Códigos CID-11 vinculados à autoridade WHO
- `diagnostic_criteria`, `criteria_groups`, `criteria_rules`, `criteria_thresholds`
- `disorder_relationships` — Comorbidades, exclusões, hierarquias
- `diagnostic_inferences` — Resultados das inferências
- `icd11_exclusions`, `icd11_differentials` — Exclusões e diferenciais CID-11

### `audit`
- `audit_logs` — Log de auditoria completo (entity_id, operation_type, new_data, ip_address, user_agent)

### `admin`
- `role_permissions` — Permissões por role
- `route_permissions` — Permissões por rota

---

## API — Endpoints

### Auth (`/api/v1/auth`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/auth/register` | Cadastro de profissional (requer MANAGE_USERS) |
| POST | `/api/v1/auth/login` | Login (retorna JWT) |
| GET | `/api/v1/auth/me` | Perfil do usuário logado |

### Pacientes (`/api/v1/patients`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/patients/` | Criar paciente |
| GET | `/api/v1/patients/{uuid}` | Obter paciente (profile com refs aninhadas) |
| GET | `/api/v1/patients/` | Listar pacientes |
| PATCH | `/api/v1/patients/{uuid}/profile` | Atualizar perfil |
| DELETE | `/api/v1/patients/{uuid}` | Excluir paciente |
| GET | `/api/v1/patients/{uuid}/export?format=csv\|pdf` | Exportar dados |
| GET | `/api/v1/patients/{uuid}/timeline` | Timeline de eventos |
| GET | `/api/v1/patients/{uuid}/reports` | Listar relatórios médicos |
| POST | `/api/v1/patients/{uuid}/reports` | Criar relatório médico |
| GET/PATCH/DELETE | `/api/v1/patients/reports/{uuid}` | Obter/atualizar/excluir relatório |
| POST | `/api/v1/patients/reports/{uuid}/toggle-pin` | Fixar/desafixar relatório |

### Consultas (`/api/v1/consultations`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/consultations/` | Criar consulta |
| POST | `/api/v1/consultations/with-data` | Criar consulta com sintomas e respostas de escalas |
| GET | `/api/v1/consultations/{uuid}` | Obter consulta |
| GET | `/api/v1/consultations/patient/{profile_uuid}` | Listar por paciente |
| GET | `/api/v1/consultations/` | Listar consultas |
| GET | `/api/v1/consultations/{uuid}/completeness` | Completude dos dados clínicos |
| GET | `/api/v1/consultations/{uuid}/symptoms` | Sintomas da consulta |
| GET | `/api/v1/consultations/{uuid}/scale-responses` | Respostas de escalas da consulta |
| PUT | `/api/v1/consultations/{uuid}/clinical-note` | Nota clínica |
| DELETE | `/api/v1/consultations/{uuid}` | Excluir consulta |

### Inferência (`/api/v1/inferences`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/inferences/run` | Inferência por critérios DSM-5-TR |
| POST | `/api/v1/inferences/bayesian` | Inferência Bayesiana |
| GET | `/api/v1/inferences/{uuid}` | Histórico de inferências por consulta |
| GET | `/api/v1/inferences/{uuid}/explanation` | Explicação step-by-step (PII redigida) |
| GET | `/api/v1/inferences/{uuid}/bayesian-explanation` | Explicação bayesiana |
| POST | `/api/v1/inferences/list` | Busca avançada de inferências |

### Escalas (`/api/v1/scales`, `/api/v1/assessments`)
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/scales/` | Listar/criar escalas |
| GET/PATCH/DELETE | `/api/v1/scales/{id}` | Obter/atualizar/excluir escala |
| GET/POST | `/api/v1/scales/{id}/questions` | Listar/adicionar questões |
| PATCH/DELETE | `/api/v1/scales/questions/{id}` | Atualizar/excluir questão |
| POST | `/api/v1/assessments/score` | Calcular score |
| POST | `/api/v1/assessments/apply` | Aplicar escala a um paciente |
| GET | `/api/v1/assessments/detail/{scale_name}` | Questões da escala por nome |
| GET | `/api/v1/assessments/patient/{uuid}/history` | Histórico de scores do paciente |
| GET | `/api/v1/assessments/patient/{uuid}/scale/{scale_name}` | Histórico por escala |
| GET | `/api/v1/assessments/patient/{uuid}/personality-factors` | Fatores de personalidade |
| GET | `/api/v1/assessments/patient/{uuid}/personality-timeline` | Evolução dos fatores por consulta |

### Transtornos (`/api/v1/disorders`) e Sintomas (`/api/v1/symptoms`)
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/disorders/` | Listar/criar transtornos |
| GET/PATCH/DELETE | `/api/v1/disorders/{id}` | Detalhes/atualizar/excluir |
| GET | `/api/v1/disorders/{id}/criteria` | Critérios DSM-5-TR do transtorno |
| GET/POST | `/api/v1/symptoms` | Listar/criar sintomas (com vínculos a transtornos) |
| GET/PATCH/DELETE | `/api/v1/symptoms/{id}` | Obter/atualizar/excluir sintoma |
| GET/POST | `/api/v1/diagnosis-relationships` | Relações entre transtornos |

### Prescrições (`/api/v1/consultations/{uuid}/prescriptions`, `/api/v1/prescriptions`)
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/consultations/{uuid}/prescriptions` | Listar/criar prescrição por consulta |
| GET | `/api/v1/prescriptions/{uuid}` | Obter prescrição |
| DELETE | `/api/v1/prescriptions/{uuid}` | Excluir prescrição |

### Tratamento (`/api/v1/treatment`)
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/treatment/associations` | Associações medicação–transtorno |
| PATCH/DELETE | `/api/v1/treatment/associations/{id}` | Atualizar/excluir associação |
| POST | `/api/v1/treatment/predict` | Predição de eficácia terapêutica |
| GET | `/api/v1/treatment/stats/{disorder_id}` | Estatísticas por transtorno |
| GET/POST | `/api/v1/treatment/outcomes` | Desfechos terapêuticos |

### Profissionais (`/api/v1/professionals`)
| Método | Rota | Descrição |
|---|---|---|
| CRUD | `/api/v1/professionals/` | Com atribuição de pacientes |

### Métricas (`/api/v1/metrics`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/metrics/overview` | Visão geral |
| GET | `/api/v1/metrics/scales/{name}/trends` | Tendência temporal |
| GET | `/api/v1/metrics/correlations` | Correlações |

### Alertas (`/api/v1/alerts`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/alerts/` | Listar alertas |
| GET | `/api/v1/alerts/check-all` | Disparar verificação de alertas |
| GET | `/api/v1/alerts/scale-thresholds` | Alertas de thresholds de escala |
| GET | `/api/v1/alerts/suicidal-ideation` | Alertas de ideação suicida |
| GET | `/api/v1/alerts/missed-follow-up` | Alertas de follow-up perdido |
| GET | `/api/v1/alerts/high-confidence` | Alertas de alta confiança diagnóstica |
| PATCH | `/api/v1/alerts/{id}/resolve` | Resolver alerta |

### Auditoria (`/api/v1/audit`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/audit/logs` | Logs de auditoria (filtros) |

### Administração (`/api/v1/admin`)
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/admin/roles/` | Gerenciar roles |
| GET/POST/DELETE | `/api/v1/admin/permissions/` | Gerenciar permissões |
| GET/POST/PATCH/DELETE | `/api/v1/admin/route-permissions/` | Gerenciar permissões de rota |
| PATCH | `/api/v1/admin/users/{uuid}/password` | Alterar senha do usuário |
| GET | `/api/v1/admin/monitoring/stats` | Métricas de desempenho |
| GET | `/api/v1/admin/monitoring/health` | Health check |
| GET | `/api/v1/admin/monitoring/requests` | Requisições recentes |

### Consentimento (`/api/v1/consent`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/consent/` | Registro de consentimento LGPD |
| GET | `/api/v1/consent/{patient_uuid}` | Histórico |

### Referência (`/api/v1/reference`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/reference/sex-types` | Tipos de sexo |
| GET | `/api/v1/reference/education-levels` | Escolaridade |
| GET | `/api/v1/reference/ethnicities` | Etnias |
| GET | `/api/v1/reference/gender-identities` | Identidades de gênero |

### ML (`/training`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/training/start` | Iniciar treinamento |
| GET | `/training/status` | Status do treinamento |

---

## Frontend

### Estrutura
```
mind-ui/src/
├── api/           # 4 módulos (client.ts, endpoints.ts, auth.ts, chatbot.ts)
├── components/    # MainLayout, MindLogo
├── pages/         # 27 .tsx em 11 domínios
├── store/         # Zustand (auth, theme)
├── types/         # Interfaces TypeScript
└── utils/         # Constantes
```

### Páginas (27 .tsx, ~16 rotas)
| Rota | Página | Descrição |
|---|---|---|
| `/login` | LoginPage | Autenticação com gradiente escuro |
| `/` | Dashboard | Cards de resumo + gráficos Recharts |
| `/patients` | PatientList | Lista com Ant Design Table |
| `/patients/:uuid` | PatientDetail | Detalhes + consultas |
| `/patients/:uuid/edit` | PatientEdit | Edição de paciente |
| `/patients/:uuid/timeline` | PatientTimeline | Timeline de eventos |
| `/patients/:uuid/reports` | PatientReports | Relatórios médicos |
| `/patients/new` | PatientCreate | Criação de paciente |
| `/consultations` | ConsultationList | Histórico de consultas |
| `/consultations/:uuid` | ConsultationDetail | Detalhes da consulta |
| `/consultations/new` | ConsultationCreate | Criar consulta |
| `/assessments` | AssessmentPage | Escalas + histórico do paciente |
| `/inferences` | InferencePage | 14 categorias de sintomas + histórico |
| `/personality` | PersonalityPage | Perfil BFP + Dark Triad |
| `/professionals` | ProfessionalsPage | Gestão com atribuição de pacientes |
| `/treatments` | TreatmentEfficacyPage | Eficácia terapêutica |
| `/analytics` | AnalyticsPage | Análises avançadas |
| `/alerts` | AlertList | Alertas clínicos |
| `/mia` | MiaPage | Chatbot diagnóstico MIA |
| `/admin/disorders` | DisordersPage | DSM-5-TR/ICD-11 catalog |
| `/admin/medications` | MedicationsPage | Gerenciar medicações |
| `/admin/scales` | ScalesPage | Gerenciar escalas |
| `/admin/symptoms` | SymptomsPage | Gerenciar sintomas |
| `/admin/permissions` | PermissionsPage | Permissões de roles |
| `/admin/monitoring` | MonitoringPage | Monitoramento do sistema |
| `/admin/users` | UsersPage | Gerenciar usuários |
| `/audit` | AuditLog | Logs de auditoria |

### Build
```bash
cd mind-ui
npm install
npm run dev       # Dev server (porta 8000)
npm run build     # Produção (dist/)
npx tsc --noEmit  # Type check
```

---

## Airflow — DAGs

| DAG | Schedule | Descrição |
|---|---|---|
| `clinical_inference_pipeline` | 02h diário | Inferência Bayesiana em lote |
| `data_quality_checks` | 03h diário | 6 checagens de qualidade |
| `metrics_aggregation` | 04h diário | Agregação de métricas clínicas |
| `alert_generation` | 6/6h | Geração de alertas (ideação, deterioração) |

---

## PySpark — Jobs

| Job | Descrição |
|---|---|
| `batch_inference` | Inferência distribuída via JDBC |
| `population_metrics` | Age distribution, disorder prevalence, scale statistics |
| `data_import` | ETL de CSV para PostgreSQL |

Uso: `python spark/submit.py <job_name> [--csv path]`

---

## Testes

**548 testes** (API + ML + segurança + integração):

```
tests/
├── api/
│   └── v1/
│       ├── clinical/              # Escalas, consultas, profissionais, etc.
│       ├── diagnostic/            # Chatbot MIA
│       └── auth/                  # Admin, auditoria
├── ml/
│   ├── inference/                 # Motor de inferência dupla
│   ├── evaluation/                # Avaliação de critérios
│   └── models/                    # Modelos de escalas
├── security/                      # Auth, LGPD, consent, encryption
├── analytics/                     # Métricas
└── integration/                   # Testes de integração
```

```bash
pytest tests/ -v           # Todos
pytest tests/api/ -v       # API
pytest tests/integration/ -v  # Integração
pytest --cov=app --cov-report=html  # Cobertura
```

---

## CI/CD — GitHub Actions

`.github/workflows/ci.yml` executa em push/PR para `main`:

1. PostgreSQL 16 service container
2. `pip install -e .`
3. `flake8 app/ tests/`
4. `black --check app/ tests/`
5. `mypy app/`
6. `pytest tests/ --cov=app --cov-report=xml`
7. Codecov upload

---

## Segurança (SSD)

- **Security Headers**: CSP, HSTS (max-age=31536000), X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- **Rate Limiting**: 100 requisições/min por IP (in-memory)
- **SQL Injection**: Bloqueio de padrões suspeitos em query params
- **Bandit SAST**: `python -m bandit -c .bandit -r app/ scripts/ db/` — zero issues
- **Safety CLI**: `python -m safety check` — scan de dependências
- **Pre-commit**: `pre-commit run --all-files` — validação antes de commits

---

## LGPD / GDPR

- **UUIDs** — Identificadores não sequenciais, sem PII
- **PII isolado** — `patient_identity` separado de `patient_profile`
- **Fernet AES** — Criptografia de campos sensíveis
- **Audit trail** — `audit_logs` com timestamp, profissional, operação, IP, user-agent
- **Consentimento** — `consent_logs` com registro de consentimento do paciente
- **Retenção** — 5 anos (configurável, implementado via `is_within_retention()` + `data_retention_days` em config)
- **Pseudonimização** — SHA-256 de CPF e email
- **Human-in-the-loop** — Nenhum diagnóstico é definitivo sem validação clínica

---

## Dados de Exemplo

```bash
# Seed de referências (ordem correta — todos idempotentes)
python db/seed.py                          # Autoridades, sintomas, transtornos, critérios
python scripts/seed_icd11.py               # Códigos CID-11
python scripts/seed_scales_groups.py       # Grupos de critérios + escalas
python scripts/seed_diagnostic_data.py     # Critérios DSM-5-TR, exclusões, diferenciais

# Dados clínicos populados
python db/populate_clinical.py

# Verificação de integridade
python scripts/check_integrity.py
```

---

## Comandos Rápidos

```bash
.venv\Scripts\Activate.ps1                   # Ativar venv (Windows)
pip install -e .
pip install -r requirements.txt
alembic upgrade head
python db/seed.py
uvicorn app.main:app --reload --port 8000
pytest tests/ -v
black app/ tests/
flake8 app/ tests/
mypy app/
python -m bandit -c .bandit -r app/ scripts/ db/
python scripts/train_all.py                  # ML Pipeline
python spark/submit.py population_metrics    # PySpark (opcional)
```

### Frontend
```powershell
cd mind-ui
npm install
npm run dev
```
