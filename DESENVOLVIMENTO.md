# M.I.N.D — Documentação de Desenvolvimento

**Data:** Junho 2026
**Versão:** 0.8.0
**Status:** MVP Completo — 8 fases implementadas
**Testes:** 140 (unitários + integração)
**Stack:** FastAPI + PostgreSQL + Pandas + Airflow + PySpark

---

## Stack Tecnológico

### Backend
- **FastAPI** — Framework web assíncrono
- **Python 3.12** — Linguagem principal
- **SQLAlchemy 2.0** — ORM
- **Pydantic v2** — Validação e serialização

### Banco de Dados
- **PostgreSQL 16** — Relacional com schemas (`core`, `clinical`, `diagnostic`, `audit`)
- **Alembic** — Migrations versionadas
- **17 tabelas** — Pacientes, profissionais, consultas, episódios, sintomas, transtornos, inferências, escalas, auditoria

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

### Qualidade & DevOps
- **pytest** — 140 testes
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

---

## API — Endpoints

### Auth
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/register` | Cadastro de profissional |
| POST | `/api/auth/login` | Login (retorna JWT) |

### Pacientes
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/patients/` | Criar paciente |
| GET | `/api/patients/{uuid}` | Obter paciente |
| GET | `/api/patients/` | Listar pacientes |
| PUT | `/api/patients/{uuid}` | Atualizar paciente |

### Consultas
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/consultations/` | Criar consulta |
| GET | `/api/consultations/{uuid}` | Obter consulta |

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

### CRUD Padrão
| Entidade | Rotas |
|---|---|
| Profissionais | `/api/professionals/` |
| Transtornos | `/api/disorders/` |
| Episódios | `/api/episodes/` |

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
└── integration/                    (4 arquivos)
    ├── test_api.py                 — End-to-end API
    ├── test_audit.py               — Auditoria
    ├── test_audit_api.py           — API de auditoria
    └── test_repositories.py        — Camada de dados
```

```bash
pytest tests/ -v           # Todos (140)
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

---

## Histórico de Commits (resumo)

- Fase 1–8: Models → Schemas → Repositories → Services → API → Auth/Audit → Escalas/Bayes → Métricas/Airflow/Spark
- CI/CD, Docker Compose (5 serviços), Clinical Manual
- Bug fixes: encoding, PYTHONPATH, healthcheck, credenciais
- PySpark 3.5 instalado, jobs de inferência em lote + métricas + ETL
