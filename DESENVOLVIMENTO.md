# M.I.N.D — Documentação de Desenvolvimento

**Data:** Junho 2026
**Versão:** 0.9.0
**Status:** MVP Completo — 10 fases implementadas
**Testes:** 174 (unitários + integração)
**Stack:** FastAPI + PostgreSQL + React + Pandas + Airflow + PySpark

---

## Stack Tecnológico

### Backend
- **FastAPI** — Framework web assíncrono
- **Python 3.12** — Linguagem principal
- **SQLAlchemy 2.0** — ORM
- **Pydantic v2** — Validação e serialização

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
- **Alembic** — Migrations versionadas
- **19 tabelas** — Pacientes, profissionais, consultas, episódios, sintomas, transtornos, inferências, escalas, auditoria, permissões

### Inferência & ML
- **Rede Bayesiana (Naive Bayes)** — `app/ml/bayesian_network.py`
- **CriteriaEvaluator** — Lógica DSM-5-TR (contagem mínima, duração, exclusão, comorbidade)
- **DSM-ICD Mapper** — Mapeamento bidirecional DSM-5-TR ↔ CID-11
- **10 escalas psicométricas** — PHQ-9, GAD-7, MADRS, ASRM, MDQ, AUDIT, DAST-10, C-SSRS, WHODAS 2.0, ISI

### Métricas & Analytics
- **Pandas** — `metrics_service.py`: faixas etárias (`pd.cut`), moving averages, correlação de Pearson, `pd.read_sql` em bulk
- **Apache Airflow** — 4 DAGs (inferência em lote, qualidade, métricas, alertas)
- **PySpark 3.5** — 3 jobs (batch inference, population metrics, data import CSV)

### Segurança
- **JWT** — Login, refresh, verificação de token
- **RBAC** — Roles: `admin`, `clinician`, `viewer`
- **Fernet AES** — Criptografia de campos sensíveis (LGPD)
- **Audit Middleware** — Log de todas as requisições a entidades clínicas

### Administração
- **RolePermission** — Permissões granulares por role
- **RoutePermission** — Controle de acesso por rota
- **MonitorService** — Métricas de desempenho em tempo real (in-memory)
- **12 endpoints** `/api/admin/` — CRUD de roles, permissões, monitoramento

### Qualidade & DevOps
- **pytest** — 174 testes (7 unitários + 5 integração, incluindo admin)
- **black, isort** — Formatação
- **flake8, mypy** — Lint e tipos
- **GitHub Actions** — CI com PostgreSQL service, flake8, black --check, mypy, pytest + codecov
- **Docker Compose** — 5 serviços

---

## Banco de Dados — Schemas

### `core`
- `patient_identity` — UUID, nome, CPF hash, email hash
- `patient_profile` — Data de nascimento, sexo, escolaridade, etnia
- `education_levels`, `ethnicities`, `gender_identities`, `sex_types` — Tabelas de domínio

### `clinical`
- `healthcare_professionals` — Profissionais cadastrados
- `consultations` — Consultas (motivo, anamnese, status)
- `clinical_episodes` — Episódios clínicos (depressivo, maníaco, etc.)
- `episode_symptoms` — Sintomas por episódio
- `assessment_scales` — Metadados das escalas
- `scale_questions` — Itens/questões de cada escala
- `scale_responses` — Respostas dos pacientes

### `diagnostic`
- `disorders` — Transtornos (DSM-5-TR + CID-11)
- `diagnostic_criteria` — Critérios por transtorno
- `disorder_relationships` — Comorbidades, exclusões, hierarquias
- `diagnostic_inferences` — Resultados das inferências

### `audit`
- `audit_logs` — Log de auditoria completo

### `admin`
- `role_permissions` — Permissões por role
- `route_permissions` — Permissões por rota

---

## API — Endpoints

### Auth
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/register` | Cadastro de profissional (requer MANAGE_USERS) |
| POST | `/api/auth/login` | Login (retorna JWT) |

### Pacientes
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/patients/` | Criar paciente |
| GET | `/api/patients/{uuid}` | Obter paciente (identity + profile com refs aninhadas) |
| GET | `/api/patients/` | Listar pacientes (com profile join: idade, sexo, ocupação) |
| PUT | `/api/patients/{uuid}/profile` | Atualizar perfil do paciente |

### Consultas
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/consultations/` | Criar consulta |
| GET | `/api/consultations/{uuid}` | Obter consulta |
| GET | `/api/consultations/?patient_uuid={uuid}` | Listar consultas por paciente |

### Inferência
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/inferences/run` | Inferência por critérios DSM-5-TR |
| POST | `/api/inferences/bayesian` | Inferência Bayesiana |

### Escalas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/scales/` | Listar escalas |
| GET | `/api/scales/{name}` | Detalhes da escala |
| POST | `/api/scales/{name}/apply` | Aplicar escala |
| POST | `/api/assessments/` | Submeter avaliação |

### Métricas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/metrics/overview` | Visão geral (total pacientes, inferências, distribuição etária) |
| GET | `/api/metrics/scales/{name}/trends` | Tendência temporal de uma escala |
| GET | `/api/metrics/correlations` | Correlações entre escalas |

### Auditoria
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/audit/logs` | Consultar logs de auditoria (filtros: entidade, operação, data) |

### Alertas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/alerts/` | Listar alertas clínicos |
| PUT | `/api/alerts/{id}/acknowledge` | Reconhecer alerta |

### Administração
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/admin/roles/` | Listar roles |
| POST | `/api/admin/roles/` | Criar role |
| GET | `/api/admin/permissions/` | Listar permissões |
| POST | `/api/admin/permissions/` | Criar permissão |
| GET | `/api/admin/role-permissions/` | Listar permissões de role |
| POST | `/api/admin/role-permissions/` | Atribuir permissão a role |
| DELETE | `/api/admin/role-permissions/{id}` | Remover permissão de role |
| GET | `/api/admin/route-permissions/` | Listar permissões de rota |
| POST | `/api/admin/route-permissions/` | Criar permissão de rota |
| DELETE | `/api/admin/route-permissions/{id}` | Remover permissão de rota |
| GET | `/api/admin/monitoring/` | Métricas de desempenho (status_code, latency_ms) |
| GET | `/api/admin/monitoring/summary` | Sumário do monitoramento |

### Referência
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/reference/sex-types` | Tipos de sexo biológico |
| GET | `/api/reference/education-levels` | Níveis de escolaridade |
| GET | `/api/reference/ethnicities` | Etnias |
| GET | `/api/reference/gender-identities` | Identidades de gênero |

### CRUD Padrão
| Entidade | Rotas |
|---|---|
| Profissionais | `/api/professionals/` |
| Transtornos | `/api/disorders/` |
| Episódios | `/api/episodes/` |

---

## Frontend

### Estrutura
```
mind-ui/src/
├── api/           # API client (Axios com interceptor JWT)
├── components/    # Componentes reutilizáveis (MainLayout, MindLogo)
├── pages/         # Páginas por domínio
├── store/         # Zustand stores (auth, theme)
├── types/         # Interfaces TypeScript
└── utils/         # Constantes e helpers
```

### Páginas
| Rota | Página | Descrição |
|---|---|---|
| `/login` | LoginPage | Autenticação com gradiente escuro, "Lembrar-me" |
| `/` | Dashboard | Cards de resumo + gráficos Recharts |
| `/patients` | PatientList | Lista com Ant Design Table |
| `/patients/:uuid` | PatientDetail | Detalhes + consultas do paciente |
| `/consultations` | ConsultationList | Histórico de consultas |
| `/assessments` | AssessmentList | Escalas psicométricas |
| `/inferences` | InferencePage | Motor de diagnóstico |
| `/alerts` | AlertList | Alertas clínicos |
| `/admin/users` | AdminUsers | Gerenciamento de usuários |
| `/admin/permissions` | AdminPermissions | Gerenciamento de permissões |
| `/admin/monitoring` | AdminMonitoring | Monitoramento em tempo real |
| `/audit` | AuditLog | Logs de auditoria |

### Build
```bash
cd mind-ui
npm install
npm run dev       # Dev server (porta 3000, proxy /api → :8001)
npm run build     # Produção (dist/)
npx tsc --noEmit  # Type check
```

### Logo
A logo em `public/logo.png` é servida em:
- **LoginPage:** 64×64 centralizada
- **Sidebar:** 180px expanded / 40px collapsed via `MindLogo.tsx`

---

## Airflow — DAGs

| DAG | Schedule | Descrição |
|---|---|---|
| `clinical_inference_pipeline` | 02h diário | Inferência Bayesiana em lote para consultas pendentes |
| `data_quality_checks` | 03h diário | 6 checagens: duplicatas, nulls, consistência, C-SSRS |
| `metrics_aggregation` | 04h diário | Agregação de métricas clínicas |
| `alert_generation` | 6/6h | Geração de alertas (ideação suicida, deterioração) |

Conexão com PostgreSQL via `AIRFLOW_CONN_MIND_POSTGRES`.

---

## PySpark — Jobs

| Job | Descrição |
|---|---|
| `batch_inference` | Lê consultas pendentes via JDBC e executa inferência distribuída |
| `population_metrics` | Age distribution, disorder prevalence, scale statistics |
| `data_import` | ETL de CSV para PostgreSQL (symptoms e patients) |

Uso: `python spark/submit.py <job_name> [--csv path]`

---

## Testes

**174 testes** (7 unitários + 5 de integração):

```
tests/
├── unit/                           (7 arquivos)
│   ├── test_assessment_scales.py   — Scoring e validação das 10 escalas
│   ├── test_auth.py                — JWT, RBAC, autenticação
│   ├── test_bayesian_network.py    — Naive Bayes classifier
│   ├── test_criteria_evaluator.py  — Regras DSM-5-TR
│   ├── test_dsm_icd_mapper.py      — Mapeamento DSM ↔ CID
│   ├── test_inference_engine.py    — Cálculo probabilístico
│   └── test_metrics.py             — Métricas e correlações
└── integration/                    (5 arquivos)
    ├── test_admin.py               — 18 testes do sistema administrativo
    ├── test_api.py                 — End-to-end API
    ├── test_audit.py               — Auditoria
    ├── test_audit_api.py           — API de auditoria
    └── test_repositories.py        — Camada de dados
```

```bash
pytest tests/ -v           # Todos (174)
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

## LGPD / GDPR

- **UUIDs** — Identificadores não sequenciais, sem PII
- **PII isolado** — `patient_identity` separado de `patient_profile`
- **Fernet AES** — Criptografia de campos sensíveis
- **Audit trail** — `audit_logs` com timestamp, profissional, operação
- **Retenção** — 5 anos (previsto)
- **Human-in-the-loop** — Nenhum diagnóstico é definitivo sem validação clínica

---

## Serviços Docker

```yaml
services:
  postgres:     # PostgreSQL 16, porta 5432
  pgadmin:      # Adminer web, porta 5050
  app:          # FastAPI, porta 8001, healthcheck
  airflow-webserver:  # Airflow UI, porta 8080
  airflow-scheduler:  # Executor de DAGs
```

```bash
docker compose up -d           # Iniciar todos
docker compose down            # Parar
docker compose logs -f app     # Logs da aplicação
```

---

## Dados de Exemplo

```bash
# Seed de referências (obrigatório antes de usar o sistema)
python db/seed.py

# Dados clínicos populados (7 pacientes, 6 consultas, PHQ-9, GAD-7)
python db/populate_clinical.py
```

Usuários criados pelo seed:
- `admin` (role admin)
- `clinician` (role clinician)
- Senha: `Cmspelo_137`

---

## Comandos Rápidos

```bash
.venv\Scripts\Activate.ps1     # Ativar venv (Windows)
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
pytest tests/ -v
black app/ tests/
flake8 app/ tests/
mypy app/
python spark/submit.py population_metrics
```

### Frontend
```powershell
cd mind-ui
$env:Path = "$env:TEMP\node-portable\node-v20.12.0-win-x64;$env:Path"  # Node portable
npm run dev
```

---

## Histórico de Commits (resumo)

- Fase 1–8: Models → Schemas → Repositories → Services → API → Auth/Audit → Escalas/Bayes → Métricas/Airflow/Spark
- Fase 9: Admin System (RolePermission, RoutePermission, monitoramento)
- Fase 10: Frontend React + TypeScript + Vite + Ant Design (13 páginas)
- SSL: Certificado autoassinado para desenvolvimento
- Dados: Seed de referências + população clínica (7 pacientes, escalas)
- Bug fixes: encoding, PYTHONPATH, healthcheck, credenciais
- PySpark 3.5 instalado, jobs de inferência em lote + métricas + ETL
