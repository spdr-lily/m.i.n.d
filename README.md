# M.I.N.D (Mental Intelligence & Network Data)

**Sistema de Apoio à Decisão Clínica (CDSS) para Diagnóstico em Saúde Mental**

Motor probabilístico de inferência diagnóstica baseado em DSM-5-TR e CID-11, com suporte a escalas psicométricas, dashboards clínicos, orquestração Airflow, processamento distribuído PySpark, pipeline de ML (12 modelos) e interface web React.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 18 + TypeScript + Vite 5 + Ant Design 5 + Recharts + Zustand |
| API | FastAPI + Pydantic v2 + SQLAlchemy 2.0 |
| Banco | PostgreSQL 16 + Alembic (21 revisões) |
| Inferência | Motor duplo (critérios DSM-5-TR + Naive Bayes + escalas + ML blending) |
| Escalas | 21 escalas: PHQ-9, GAD-7, MADRS, MDQ, PCL-5, Y-BOCS, AUDIT, ASRM, ASRS, AQ-10, BFP, DT-12, MEMÓRIA, QI-RASTREIO, RECONHECIMENTO DE ROSTOS, FLUÊNCIA VERBAL, TESTE DO RELÓGIO, TRILHAS, STROOP, CANCELAMENTO, FIGURA COMPLEXA DE REY |
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
5. **21 Escalas Psicométricas** — Scoring completo com interpretação por gravidade (inclui BFP 25 itens, DT-12, 10 neuropsicológicas)
6. **Pipeline de ML** — 12 modelos treinados (diagnóstico, recaída, risco de suicídio, resposta terapêutica), registrados no MLflow
7. **Gestão de Prescrições** — CRUD de prescrições por consulta com rastreabilidade (itens, notas, vínculo com medicações)
8. **Gestão de Profissionais** — CRM/CRP, especialidade, atribuição de pacientes
9. **Validação de Integridade Clínica** — 3 camadas: Pydantic → Service → DB CHECK constraints
10. **Data Warehouse** — Star schema com ETL dedicado
11. **Segurança em Camadas** — CSP, HSTS, Rate Limit (100 req/min), proteção SQL injection, Bandit zero
12. **LGPD Compliance** — UUID, pseudonimização, criptografia Fernet AES, auditoria, retenção configurável (5 anos, implementado via `is_within_retention`)
13. **Frontend Web** — 27 páginas React com sidebar responsiva por role
14. **Vínculo Sintoma ↔ Transtorno** — `SymptomResponse.disorders` expõe os transtornos vinculados a cada sintoma (capítulo DSM, CID-11, presença requerida, duração mínima) via `DisorderService.list_symptom_criteria()`

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
- `PATCH /api/v1/patients/{uuid}/profile` — Atualizar perfil do paciente
- `GET /api/v1/patients/{uuid}/export?format=csv|pdf` — Exportar dados
- `GET /api/v1/patients/{uuid}/timeline` — Timeline de eventos
- `GET/POST /api/v1/patients/{uuid}/reports` — Relatórios médicos (listar/criar)
- `GET/PATCH/DELETE /api/v1/patients/reports/{uuid}` — Obter/atualizar/excluir relatório
- `POST /api/v1/patients/reports/{uuid}/toggle-pin` — Fixar relatório

### Consultas
- `POST /api/v1/consultations/` — Criar consulta
- `POST /api/v1/consultations/with-data` — Criar consulta com sintomas + respostas de escalas
- `GET /api/v1/consultations/{uuid}` — Obter consulta
- `GET /api/v1/consultations/patient/{profile_uuid}` — Consultas do paciente
- `GET /api/v1/consultations/` — Listar consultas
- `GET /api/v1/consultations/{uuid}/completeness` — Completude dos dados clínicos
- `PUT /api/v1/consultations/{uuid}/clinical-note` — Nota clínica
- `DELETE /api/v1/consultations/{uuid}` — Excluir consulta

### Inferência
- `POST /api/v1/inferences/run` — Inferência por critérios DSM-5-TR
- `POST /api/v1/inferences/bayesian` — Inferência Bayesiana
- `GET /api/v1/inferences/{uuid}` — Histórico de inferências por consulta
- `GET /api/v1/inferences/{uuid}/explanation` — Explicação step-by-step (PII redigida)
- `GET /api/v1/inferences/{uuid}/bayesian-explanation` — Explicação bayesiana

### Escalas
- `GET/POST /api/v1/scales/` — Listar/criar escalas
- `GET/PATCH/DELETE /api/v1/scales/{id}` — Obter/atualizar/excluir escala
- `GET/POST /api/v1/scales/{id}/questions` — Questões da escala
- `POST /api/v1/assessments/score` — Calcular score
- `POST /api/v1/assessments/apply` — Aplicar escala a um paciente
- `GET /api/v1/assessments/detail/{scale_name}` — Questões por nome da escala
- `GET /api/v1/assessments/patient/{patient_uuid}/history` — Histórico de scores do paciente
- `GET /api/v1/assessments/patient/{patient_uuid}/scale/{scale_name}` — Histórico por escala
- `GET /api/v1/assessments/patient/{patient_uuid}/personality-factors` — Fatores de personalidade
- `GET /api/v1/assessments/patient/{patient_uuid}/personality-timeline` — Evolução dos fatores

### Transtornos e Sintomas
- `GET/POST /api/v1/disorders/` — Listar/criar transtornos (com DSM-5-TR criteria, exclusões, diferenciais)
- `GET/PATCH/DELETE /api/v1/disorders/{id}` — Detalhes do transtorno
- `GET /api/v1/disorders/{id}/criteria` — Critérios DSM-5-TR do transtorno
- `GET/POST /api/v1/symptoms` — Sintomas (com vínculos a transtornos)
- `GET/PATCH/DELETE /api/v1/symptoms/{id}` — Obter/atualizar/excluir sintoma

### Prescrições e Tratamento
- `GET/POST /api/v1/consultations/{uuid}/prescriptions` — Prescrições por consulta
- `GET/DELETE /api/v1/prescriptions/{uuid}` — Obter/excluir prescrição
- `GET/POST /api/v1/treatment/associations` — Associações medicação–transtorno
- `POST /api/v1/treatment/predict` — Predição de eficácia terapêutica
- `GET /api/v1/treatment/stats/{disorder_id}` — Estatísticas por transtorno

### Profissionais
- `GET/POST /api/v1/professionals/` — CRUD com atribuição de pacientes
- `PUT/DELETE /api/v1/professionals/{uuid}` — Atualizar/excluir profissional

### Métricas e Alertas
- `GET /api/v1/metrics/overview` — Visão geral
- `GET /api/v1/metrics/scales/{name}/trends` — Tendências temporais
- `GET /api/v1/metrics/correlations` — Correlações entre escalas
- `GET /api/v1/alerts/` — Listar alertas clínicos
- `PATCH /api/v1/alerts/{id}/resolve` — Resolver alerta

### Auditoria
- `GET /api/v1/audit/logs` — Logs de auditoria (filtros: entidade, operação, data)

### Administração
- `GET/POST /api/v1/admin/roles` — Gerenciar roles
- `GET/POST /api/v1/admin/permissions` — Gerenciar permissões
- `GET/POST/DELETE /api/v1/admin/route-permissions` — Gerenciar permissões de rota
- `PATCH /api/v1/admin/users/{uuid}/password` — Alterar senha do usuário
- `GET /api/v1/admin/monitoring/*` — Métricas de desempenho em tempo real

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
| MIA (chatbot) | `/mia` | Assistente diagnóstico com IA |
| Personalidade | `/personality` | Fatores BFP e DT-12 com radar chart |
| Admin | `/admin/*` | Usuários, permissões, transtornos, monitoramento |
| Auditoria | `/audit` | Logs de auditoria |

```bash
cd mind-ui
npm install
npm run dev    # http://localhost:8000 (API em http://127.0.0.1:8000/api/v1)
```

---

## Testes

**548 testes** (unitários + integração):

```bash
pytest tests/ -v                     # 548 testes
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
# ⚠️ Dados clínicos de pacientes e consultas gerados pelos seeds são SINTÉTICOS.
#    Destinados exclusivamente a desenvolvimento, testes e demonstração de ML.
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
