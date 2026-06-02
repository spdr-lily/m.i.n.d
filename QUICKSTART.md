# M.I.N.D — Guia Rápido

## Pré-requisitos

- Python 3.12+
- PostgreSQL 16 (ou Docker)
- Node.js 20+ (para frontend)
- Java 8+ (para PySpark)

## Setup

### Backend

```powershell
# 1. Ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -e .
pip install -r requirements.txt

# 3. Configurar .env
Copy-Item .env.example -Destination .env
# Editar se necessário (padrão: postgres:137_Cmspelo@localhost:5432/mind)

# 4. Iniciar serviços
docker compose up -d

# 5. Migrations
alembic upgrade head

# 6. Servidor
uvicorn app.main:app --reload --port 8001
```

### Frontend

```powershell
cd mind-ui
npm install
npm run dev    # http://localhost:3000
```

```bash
# Ou com Node.js portable (Windows)
$env:Path = "$env:TEMP\node-portable\node-v20.12.0-win-x64;$env:Path"
npm run dev
```

### Dados de Exemplo

```bash
# Seed de referências (sintomas, transtornos, critérios, profissional)
python db/seed.py

# Dados clínicos (7 pacientes, 6 consultas, escalas PHQ-9/GAD-7)
python db/populate_clinical.py
```

## Serviços

| Serviço | URL | Auth |
|---|---|---|
| Frontend (Vite) | http://localhost:3000 | JWT |
| API (FastAPI) | http://localhost:8001/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.com` / `admin` |
| Airflow | http://localhost:8080 | `admin` / `admin` |

Usuários padrão: `admin` / `clinician` — senha `Cmspelo_137`

## Testes

```bash
pytest tests/ -v                     # 174 testes
pytest tests/ --cov=app --cov-report=html
```

## PySpark (opcional)

```bash
pip install pyspark==3.5.0
python spark/submit.py population_metrics
python spark/submit.py data_import --csv data/pacientes.csv
```

## Comandos úteis

```bash
black app/ tests/                    # Formatar
flake8 app/ tests/                   # Lint
mypy app/                            # Type check
alembic revision --autogenerate -m "desc"  # Nova migration
alembic upgrade head                 # Aplicar migrations
```

## Documentação

- `CLINICAL_MANUAL.md` — Manual clínico completo
- `STRUCTURE.md` — Estrutura detalhada
- `DESENVOLVIMENTO.md` — Documentação dev

**Status:** MVP completo — 10 fases implementadas, 174 testes, frontend React + backend FastAPI, CI/CD ativo.
