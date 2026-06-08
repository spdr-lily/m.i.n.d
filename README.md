# M.I.N.D (Mental Intelligence & Network Data)

**Sistema de Apoio à Decisão Clínica (CDSS) para Diagnóstico em Saúde Mental**

Motor probabilístico de inferência diagnóstica baseado em DSM-5-TR e CID-11, com suporte a escalas psicométricas, dashboards clínicos, orquestração Airflow, processamento distribuído PySpark e interface web React.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 18 + TypeScript + Vite 5 + Ant Design 5 + Recharts + Zustand |
| API | FastAPI + Pydantic v2 + SQLAlchemy 2.0 |
| Banco | PostgreSQL 16 + Alembic |
| Inferência | Rede Bayesiana (Naive Bayes) + Critérios DSM-5-TR |
| Escalas | PHQ-9, GAD-7, MADRS, ASRM, MDQ, AUDIT, DAST-10, C-SSRS, WHODAS 2.0, ISI |
| Métricas | Pandas (moving averages, correlações) |
| Orquestração | Apache Airflow (4 DAGs) |
| Batch/ETL | PySpark 3.5 (inferência, métricas populacionais, importação CSV) |
| Segurança | JWT + RBAC + Fernet AES (LGPD) |
| Auditoria | Middleware com rastreabilidade (entity_id, request body, operação semântica) |
| CI/CD | GitHub Actions (flake8, black, mypy, pytest, codecov) |
| Deploy | Docker Compose (5 serviços) |

---

## Fases Implementadas

1. **Modelos e Schema** — 17 tabelas, UUIDs, LGPD, Alembic
2. **Schemas Pydantic** — Validação de todas as entradas/saídas
3. **Repositories** — CRUD com SQLAlchemy 2.0
4. **Services** — Lógica de negócio (pacientes, consultas, diagnóstico, escalas)
5. **API REST** — Endpoints para todas as entidades clínicas
6. **Auth + RBAC + Auditoria** — JWT, roles (admin/clinician/viewer), middleware de auditoria
7. **Escalas + Rede Bayesiana** — 10 instrumentos psicométricos, Naive Bayes, inferência probabilística
8. **Métricas + Dashboards** — Pandas (faixas etárias, correlações, moving averages), Airflow (4 DAGs), PySpark (batch inference + population metrics + ETL)
9. **Admin System** — Gerenciamento de permissões dinâmicas (RolePermission, RoutePermission), 12 endpoints `/api/admin/`, monitoramento em tempo real
10. **Frontend Web** — 13 páginas React com sidebar responsiva por role, login com JWT, consultas, pacientes, escalas, inferência, dashboards, administração

---

## API Endpoints

### Autenticação
- `POST /api/auth/login` — Login (JWT)
- `POST /api/auth/register` — Cadastro de profissional (requer `MANAGE_USERS`)

### Pacientes
- `POST /api/patients/` — Criar paciente
- `GET /api/patients/{uuid}` — Obter paciente (dados de identidade + perfil)
- `GET /api/patients/` — Listar pacientes (com profile join: idade, sexo, ocupação)
- `PUT /api/patients/{uuid}/profile` — Atualizar perfil do paciente

### Consultas
- `POST /api/consultations/` — Criar consulta
- `GET /api/consultations/{uuid}` — Obter consulta
- `GET /api/consultations/?patient_uuid={uuid}` — Listar consultas por paciente

### Inferência
- `POST /api/inferences/run` — Inferência por critérios (DSM-5-TR)
- `POST /api/inferences/bayesian` — Inferência Bayesiana

### Escalas
- `GET /api/scales/` — Listar escalas
- `POST /api/scales/{name}/apply` — Aplicar escala
- `POST /api/assessments/` — Submeter avaliação

### Métricas
- `GET /api/metrics/overview` — Visão geral
- `GET /api/metrics/scales/{name}/trends` — Tendências temporais
- `GET /api/metrics/correlations` — Correlações entre escalas

### Alertas
- `GET /api/alerts/` — Listar alertas clínicos

### Auditoria
- `GET /api/audit/logs` — Logs de auditoria (filtros: entidade, operação, data)

### Administração
- `GET/POST /api/admin/roles` — Gerenciar roles
- `GET/POST /api/admin/permissions` — Gerenciar permissões
- `GET/POST /api/admin/route-permissions` — Gerenciar permissões de rota
- `GET /api/admin/monitoring` — Métricas de desempenho em tempo real

### Referência (dados de domínio)
- `GET /api/reference/sex-types`, `/education-levels`, `/ethnicities`, `/gender-identities`

### Profissionais / Transtornos / Episódios
- CRUD completo em `/api/professionals/`, `/api/disorders/`, `/api/episodes/`

---

## Frontend

Aplicação React + TypeScript + Vite em `mind-ui/`:

| Página | Rota | Descrição |
|---|---|---|
| Login | `/login` | Autenticação JWT com gradiente escuro e logo |
| Dashboard | `/` | Visão geral com cards e gráficos |
| Pacientes | `/patients` | Lista e detalhes do paciente |
| Consultas | `/consultations` | Registro e histórico |
| Escalas | `/assessments` | Aplicação de escalas psicométricas |
| Inferência | `/inferences` | Motor de diagnóstico probabilístico |
| Alertas | `/alerts` | Alertas clínicos |
| Admin | `/admin/*` | Usuários, permissões, monitoramento |
| Auditoria | `/audit` | Logs de auditoria |

```bash
cd mind-ui
npm install
npm run dev    # http://localhost:3000 (API em http://127.0.0.1:8008/api via CORS)
```

---

## Testes

**174 testes** (unitários + integração) com cobertura:

```
tests/
├── unit/
│   ├── test_assessment_scales.py
│   ├── test_auth.py
│   ├── test_bayesian_network.py
│   ├── test_criteria_evaluator.py
│   ├── test_dsm_icd_mapper.py
│   ├── test_inference_engine.py
│   └── test_metrics.py
└── integration/
    ├── test_admin.py
    ├── test_api.py
    ├── test_audit.py
    ├── test_audit_api.py
    └── test_repositories.py
```

```bash
pytest tests/ -v          # Todos os testes
pytest tests/unit/ -v     # Unitários
pytest tests/integration/ -v  # Integração
```

---

## Como Rodar

### Backend
```bash
# 1. Ambiente
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -e .
pip install -r requirements.txt

# 2. Banco
docker compose up -d          # postgres + pgadmin + airflow
alembic upgrade head

# 3. Servidor
uvicorn app.main:app --host 0.0.0.0 --port 8008
```

### Frontend
```bash
cd mind-ui
npm install
npm run dev    # http://localhost:3000
```

### Acesso
| Serviço | URL | Auth |
|---|---|---|---|
| Frontend (Vite dev) | http://localhost:3000 | JWT |
| Frontend (produção) | http://localhost:8000 | JWT |
| API (Swagger) | http://localhost:8008/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.com` / `admin` |
| Airflow | http://localhost:8080 | `admin` / `admin` |

Usuários padrão: `admin` / `clinician` — senha altere no `.env`

> **Nota sobre CORS + Proxy:** O Vite não usa mais proxy. Configure `VITE_API_URL=http://127.0.0.1:8008/api` em `mind-ui/.env` para desenvolvimento. O backend deve estar em `0.0.0.0:8008`.

### PySpark (opcional)
```bash
pip install pyspark==3.5.0
python spark/submit.py batch_inference
python spark/submit.py population_metrics
python spark/submit.py data_import --csv data/pacientes.csv
```

---

## Documentação

- `CLINICAL_MANUAL.md` — Manual clínico completo (pt-BR)
- `STRUCTURE.md` — Estrutura de diretórios detalhada
- `QUICKSTART.md` — Guia rápido de configuração
- `DESENVOLVIMENTO.md` — Documentação de desenvolvimento

---

## Changelog

### 2026-06-03 — Correções de infraestrutura e auditoria

- **Proxy removido**: Vite agora chama backend diretamente via `VITE_API_URL=http://127.0.0.1:8008/api`. Causa raiz: Node.js resolvia `localhost` para IPv6 (`::1`), backend escutava apenas IPv4.
- **CORS**: `allow_origins=["*"]` com porta 8008; frontend sem proxy.
- **Export CSV/PDF**: Endpoint `GET /api/patients/{uuid}/export?format=csv|pdf` com `fpdf2`.
- **Medical Reports**: Modelo `MedicalReport`, migration, schemas, service CRUD + togglePin, API com 6 endpoints, frontend `PatientReportsPage.tsx`.
- **Audit fix**: Migration `41991f22ee27` adicionou colunas `entity_id`, `ip_address`, `user_agent` à tabela `audit_logs`.
- **Atomicidade transacional**: Todos os repositórios agora usam `flush()` em vez de `commit()`. O `get_db()` faz auto-commit no sucesso e auto-rollback em exceção — a transação é a requisição HTTP inteira.
- **Auditoria aprimorada**: Middleware captura `entity_id` (UUID da URL), `new_data` (corpo da requisição), `operation_type` semântico (READ/CREATE/UPDATE/DELETE). `db.close()` movido para `finally` (elimina leak).
- **`ConsultationService`**: `create_or_update_clinical_note()` usa `flush()` para não quebrar atomicidade da criação de consulta multi-step.
- **`InferenceService.run_inference()`**: Adicionado try/except/rollback.
- **scale_options**: `constants.ts` unificado com todas as 10 escalas e chaves corretas. `ConsultationCreatePage.tsx` agora importa `SCALE_OPTIONS` em vez de definições locais duplicadas.
- **Docker Compose**: `entrypoint.sh` executa `alembic upgrade head` antes do uvicorn. `requirements-prod.txt` inclui `fpdf2`.

---

## Licença

MIT
