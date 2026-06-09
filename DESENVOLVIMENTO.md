# M.I.N.D — Documentação de Desenvolvimento

**Data:** Junho 2026
**Versão:** 1.0.0
**Status:** CDSS Completo — 12 fases implementadas
**Testes:** 174+ (unitários + integração)
**Stack:** FastAPI + PostgreSQL 16 + React + Pandas + Airflow + PySpark + MLflow

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
- **Alembic** — 12 revisões lineares
- **30+ tabelas** — Pacientes, profissionais, consultas, episódios, sintomas, transtornos, inferências, escalas, notas clínicas, medicações, prescrições, relatórios, auditoria, permissões, consentimento, autoridades de classificação, atribuições profissional-paciente, DW

### Inferência & ML
- **Rede Bayesiana (Naive Bayes)** — `app/ml/bayesian_network.py`
- **CriteriaEvaluator** — Lógica DSM-5-TR (contagem mínima, duração, exclusão, comorbidade)
- **DSM-ICD Mapper** — Mapeamento bidirecional DSM-5-TR ↔ CID-11
- **10 escalas psicométricas** — PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10
- **ML Pipeline** — 12 modelos (4 objetivos × 3 algoritmos: Logistic Regression, Random Forest, XGBoost)
- **MLflow** — Experiment tracking e model registry
- **DVC** — Versionamento de datasets

### Métricas & Analytics
- **Pandas** — `metrics_service.py`: faixas etárias, moving averages, correlação de Pearson
- **Apache Airflow** — 4 DAGs (inferência em lote, qualidade, métricas, alertas)
- **PySpark 3.5** — 3 jobs (batch inference, population metrics, data import CSV)
- **Data Warehouse** — Star schema (`dim_disorder`, `dim_patient`, `dim_date`, `fact_diagnosis`, `fact_symptom`, `fact_consultation`, `fact_scale_response`)

### Segurança
- **JWT** — Login, refresh, verificação de token
- **RBAC** — Roles: `admin`, `clinician`, `viewer`
- **Fernet AES** — Criptografia de campos sensíveis (LGPD)
- **Audit Middleware** — Log de todas as requisições a entidades clínicas
- **Security Middleware Stack** — CSP, HSTS (1 ano), Rate Limit (100 req/min), Proteção SQL Injection
- **Bandit SAST** — Zero issues
- **Safety CLI** — Verificação de dependências
- **Pre-commit hooks** — Security checks automatizados

### Administração
- **RolePermission** — Permissões granulares por role
- **RoutePermission** — Controle de acesso por rota
- **MonitorService** — Métricas de desempenho em tempo real (in-memory)
- **12+ endpoints** `/api/v1/admin/`

### Qualidade & DevOps
- **pytest** — 174+ testes
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
| PUT | `/api/v1/patients/{uuid}/profile` | Atualizar perfil |
| GET | `/api/v1/patients/{uuid}/export?format=csv\|pdf` | Exportar dados |
| GET | `/api/v1/patients/{uuid}/timeline` | Timeline de eventos |
| GET | `/api/v1/patients/{uuid}/reports` | Relatórios médicos |

### Consultas (`/api/v1/consultations`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/consultations/` | Criar consulta |
| GET | `/api/v1/consultations/{uuid}` | Obter consulta |
| GET | `/api/v1/consultations/?patient_uuid={uuid}` | Listar por paciente |

### Inferência (`/api/v1/inferences`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/inferences/run` | Inferência por critérios DSM-5-TR |
| POST | `/api/v1/inferences/bayesian` | Inferência Bayesiana |
| GET | `/api/v1/inferences/{uuid}/by-consultation` | Histórico de inferências |

### Escalas (`/api/v1/scales`, `/api/v1/assessments`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/scales/` | Listar escalas |
| GET | `/api/v1/scales/{name}` | Detalhes da escala |
| POST | `/api/v1/scales/{name}/apply` | Aplicar escala |
| POST | `/api/v1/assessments/` | Submeter avaliação |
| GET | `/api/v1/assessments/patient/{uuid}/history` | Histórico de scores |

### Transtornos (`/api/v1/disorders`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/disorders/` | Listar (DSM-5 criteria, exclusões, diferenciais) |
| GET | `/api/v1/disorders/{uuid}` | Detalhes |

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

### Auditoria (`/api/v1/audit`)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/audit/logs` | Logs de auditoria (filtros) |

### Administração (`/api/v1/admin`)
| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/admin/roles/` | Gerenciar roles |
| GET/POST | `/api/v1/admin/permissions/` | Gerenciar permissões |
| GET/POST/DELETE | `/api/v1/admin/route-permissions/` | Gerenciar permissões de rota |
| GET | `/api/v1/admin/monitoring/` | Métricas de desempenho |

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
├── api/           # 16 módulos (client.ts + Axios)
├── components/    # MainLayout, MindLogo
├── pages/         # 10 páginas por domínio
├── store/         # Zustand (auth, theme)
├── types/         # Interfaces TypeScript
└── utils/         # Constantes
```

### Páginas
| Rota | Página | Descrição |
|---|---|---|
| `/login` | LoginPage | Autenticação com gradiente escuro |
| `/` | Dashboard | Cards de resumo + gráficos Recharts |
| `/patients` | PatientList | Lista com Ant Design Table |
| `/patients/:uuid` | PatientDetail | Detalhes + consultas |
| `/consultations` | ConsultationList | Histórico de consultas |
| `/assessments` | AssessmentPage | Escalas + histórico do paciente |
| `/inferences` | InferencePage | 14 categorias de sintomas + histórico |
| `/professionals` | ProfessionalsPage | Gestão com atribuição de pacientes |
| `/alerts` | AlertList | Alertas clínicos |
| `/admin/*` | AdminPages | Transtornos (DSM-5/ICD-11 collapsible), permissões, monitoramento |
| `/audit` | AuditLog | Logs de auditoria |

### Build
```bash
cd mind-ui
npm install
npm run dev       # Dev server (porta 3000)
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

**174+ testes** (7 unitários + 5 de integração):

```
tests/
├── unit/
│   ├── test_assessment_scales.py   — Scoring das 10 escalas
│   ├── test_auth.py                — JWT, RBAC
│   ├── test_bayesian_network.py    — Naive Bayes
│   ├── test_criteria_evaluator.py  — Regras DSM-5-TR
│   ├── test_dsm_icd_mapper.py      — Mapeamento DSM ↔ CID
│   ├── test_inference_engine.py    — Cálculo probabilístico
│   └── test_metrics.py             — Métricas e correlações
└── integration/
    ├── test_admin.py               — Sistema administrativo
    ├── test_api.py                 — End-to-end API
    ├── test_audit.py               — Auditoria
    ├── test_audit_api.py           — API de auditoria
    └── test_repositories.py        — Camada de dados
```

```bash
pytest tests/ -v           # Todos
pytest tests/unit/ -v      # Unitários
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
- **Retenção** — 5 anos (previsto)
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
uvicorn app.main:app --reload --port 8008
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
