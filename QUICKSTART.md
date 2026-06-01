# M.I.N.D — Guia Rápido

## Pré-requisitos

- Python 3.12+
- PostgreSQL 16 (ou Docker)
- Java 8+ (para PySpark)

## Setup

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

## Serviços

| Serviço | URL | Auth |
|---|---|---|
| API (FastAPI) | http://localhost:8001/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.com` / `admin` |
| Airflow | http://localhost:8080 | `admin` / `admin` |

## Testes

```bash
pytest tests/ -v                     # 140 testes
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

**Status:** MVP completo — 8 fases implementadas, 140 testes, CI/CD ativo.
