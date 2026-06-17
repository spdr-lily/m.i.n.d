# M.I.N.D (Mental Intelligence & Network Data)

**Sistema de Apoio à Decisão Clínica (CDSS) para Diagnóstico em Saúde Mental**

Motor probabilístico de inferência diagnóstica baseado em DSM-5-TR e CID-11, com suporte a escalas psicométricas, dashboards clínicos, orquestração Airflow, processamento distribuído PySpark, pipeline de ML (12 modelos) e interface web React.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 18 + TypeScript + Vite 5 + Ant Design 5 + Recharts + Zustand |
| API | FastAPI + Pydantic v2 + SQLAlchemy 2.0 |
| Banco | PostgreSQL 16 + Alembic (12 revisões) |
| Inferência | Rede Bayesiana (Naive Bayes) + Critérios DSM-5-TR |
| Escalas | 20 escalas: PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10, BFP, MEMÓRIA, QI-RASTREIO, RECONHECIMENTO DE ROSTOS, FLUÊNCIA VERBAL, TESTE DO RELÓGIO, TRILHAS, STROOP, CANCELAMENTO, FIGURA COMPLEXA DE REY |
| ML Pipeline | Logistic Regression, Random Forest, XGBoost (4 objetivos × 3 algoritmos = 12 modelos) |
| MLOps | MLflow + DVC |
| DW | Star schema (dim_fato), ETL via `dw_loader.py` |
| Métricas | Pandas (moving averages, correlações) + Analytics dedicado |
| Orquestração | Apache Airflow (4 DAGs) |
| Batch/ETL | PySpark 3.5 (inferência, métricas populacionais, importação CSV) |
| Segurança | JWT + RBAC + Fernet AES (LGPD) + CSP + HSTS + Rate Limit + Proteção SQL Injection |
| Auditoria | Middleware com rastreabilidade (entity_id, request body, operação semântica) |
| CI/CD | GitHub Actions (flake8, black, mypy, pytest, codecov) + Bandit + Safety |
| Deploy | Docker Compose (5 serviços) |

---

## Funcionalidades Implementadas

1. **19 Transtornos (Português BR)** — Nomes unificados com DSM-5-TR e CID-11, critérios diagnósticos completos, exclusões e diagnósticos diferenciais
2. **Classificação Dual** — APA (DSM-5-TR) e WHO (CID-11) como autoridades de primeira classe
3. **Motor de Critérios Diagnósticos** — Avaliação baseada em regras DSM-5-TR (contagem mínima, duração, exclusão, comorbidade)
4. **Motor Bayesiano** — Naive Bayes com priors epidemiológicos (Kessler NCS-R, WHO WMHS)
5. **10 Escalas Psicométricas** — Scoring completo com interpretação por gravidade
6. **Pipeline de ML** — 12 modelos treinados (diagnóstico, recaída, risco de suicídio, resposta terapêutica), registrados no MLflow
7. **Gestão de Profissionais** — CRM/CRP, especialidade, atribuição de pacientes
8. **Validação de Integridade Clínica** — 3 camadas: Pydantic → Service → DB CHECK constraints
9. **Data Warehouse** — Star schema com ETL dedicado
10. **Segurança em Camadas** — CSP, HSTS, Rate Limit (100 req/min), proteção SQL injection, Bandit zero
11. **LGPD Compliance** — UUID, pseudonimização, criptografia Fernet AES, auditoria, retenção
12. **Frontend Web** — 10 páginas React com sidebar responsiva por role

---

## API Endpoints (`/api/v1/...`)

### Autenticação
- `POST /api/v1/auth/login` — Login (JWT)
- `POST /api/v1/auth/register` — Cadastro de profissional (requer `MANAGE_USERS`)
- `GET /api/v1/auth/me` — Perfil do usuário logado

### Pacientes
- `POST /api/v1/patients/` — Criar paciente
- `GET /api/v1/patients/{uuid}` — Obter paciente (dados de identidade + perfil)
- `GET /api/v1/patients/` — Listar pacientes (com profile join)
- `PUT /api/v1/patients/{uuid}/profile` — Atualizar perfil do paciente
- `GET /api/v1/patients/{uuid}/export?format=csv|pdf` — Exportar dados
- `GET /api/v1/patients/{uuid}/timeline` — Timeline de eventos
- `GET /api/v1/patients/{uuid}/reports` — Relatórios médicos

### Consultas
- `POST /api/v1/consultations/` — Criar consulta
- `GET /api/v1/consultations/{uuid}` — Obter consulta
- `GET /api/v1/consultations/?patient_uuid={uuid}` — Listar consultas por paciente

### Inferência
- `POST /api/v1/inferences/run` — Inferência por critérios DSM-5-TR
- `POST /api/v1/inferences/bayesian` — Inferência Bayesiana
- `GET /api/v1/inferences/{uuid}/by-consultation` — Histórico de inferências por consulta

### Escalas
- `GET /api/v1/scales/` — Listar escalas
- `GET /api/v1/scales/{name}` — Detalhes da escala
- `POST /api/v1/scales/{name}/apply` — Aplicar escala
- `POST /api/v1/assessments/` — Submeter avaliação
- `GET /api/v1/assessments/patient/{patient_uuid}/history` — Histórico de scores do paciente

### Transtornos
- `GET /api/v1/disorders/` — Listar transtornos (com DSM-5-TR criteria, exclusões, diferenciais)
- `GET /api/v1/disorders/{uuid}` — Detalhes do transtorno

### Profissionais
- `GET/POST /api/v1/professionals/` — CRUD com atribuição de pacientes
- `PUT/DELETE /api/v1/professionals/{uuid}` — Atualizar/excluir profissional

### Métricas
- `GET /api/v1/metrics/overview` — Visão geral
- `GET /api/v1/metrics/scales/{name}/trends` — Tendências temporais
- `GET /api/v1/metrics/correlations` — Correlações entre escalas

### Auditoria
- `GET /api/v1/audit/logs` — Logs de auditoria (filtros: entidade, operação, data)

### Administração
- `GET/POST /api/v1/admin/roles` — Gerenciar roles
- `GET/POST /api/v1/admin/permissions` — Gerenciar permissões
- `GET/POST/DELETE /api/v1/admin/route-permissions` — Gerenciar permissões de rota
- `GET /api/v1/admin/monitoring` — Métricas de desempenho em tempo real

### Consentimento
- `POST /api/v1/consent/` — Registro de consentimento LGPD
- `GET /api/v1/consent/{patient_uuid}` — Histórico de consentimento

### ML (Treinamento)
- `POST /training/start` — Iniciar treinamento de modelos
- `GET /training/status` — Status do treinamento

---

## Frontend

Aplicação React + TypeScript + Vite em `mind-ui/`:

| Página | Rota | Descrição |
|---|---|---|
| Login | `/login` | Autenticação JWT com gradiente escuro |
| Dashboard | `/` | Visão geral com cards e gráficos |
| Pacientes | `/patients` | Lista e detalhes do paciente |
| Consultas | `/consultations` | Registro e histórico |
| Escalas | `/assessments` | Aplicação de escalas com histórico do paciente |
| Inferência | `/inferences` | Sintomas em 14 categorias clínicas, histórico do paciente |
| Profissionais | `/professionals` | Gestão com atribuição de pacientes |
| Alertas | `/alerts` | Alertas clínicos |
| Admin | `/admin/*` | Usuários, permissões, transtornos, monitoramento |
| Auditoria | `/audit` | Logs de auditoria |

```bash
cd mind-ui
npm install
npm run dev    # http://localhost:8000 (API em http://127.0.0.1:8000/api/v1)
```

---

## Testes

**174+ testes** (unitários + integração):

```bash
pytest tests/ -v                     # Todos os testes
pytest tests/unit/ -v                # Unitários
pytest tests/integration/ -v         # Integração
pytest --cov=app --cov-report=html   # Cobertura
```

---

## Como Rodar

### Backend
```bash
# 1. Ambiente (Python 3.14+)
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -e .
pip install -r requirements.txt

# 2. Banco
docker compose up -d          # postgres + pgadmin + airflow
alembic upgrade head

# 3. Seed (ordem correta)
python db/seed.py
python scripts/seed_icd11.py
python scripts/seed_scales_groups.py
python scripts/seed_diagnostic_data.py

# 4. Servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd mind-ui
npm install
npm run dev    # http://localhost:8000
```

### Acesso
| Serviço | URL | Auth |
|---|---|---|
| Frontend (Vite dev) | http://localhost:8000 | JWT |
| API (Swagger) | http://localhost:8000/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.com` / `admin` |
| Airflow | http://localhost:8080 | `admin` / `admin` |

### DW ETL
```bash
python -c "from app.etl.dw_loader import run_full_etl; run_full_etl()"
```

### Segurança (QA)
```bash
python -m bandit -c .bandit -r app/ scripts/ db/
python -m safety check
```

### ML Pipeline
```bash
# Treinar todos os modelos
python scripts/train_all.py

# Verificar modelos no MLflow
mlflow ui  # http://localhost:5000
```

---

## Documentação

- `CLINICAL_MANUAL.md` — Manual clínico completo (pt-BR)
- `STRUCTURE.md` — Estrutura de diretórios detalhada
- `DESENVOLVIMENTO.md` — Documentação de desenvolvimento
- `QUICKSTART.md` — Guia rápido de configuração
- `SECURITY.md` — Política de segurança
- `AGENTS.md` — Instruções para agentes de IA

---

## Licença

MIT
