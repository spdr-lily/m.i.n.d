# M.I.N.D — Guia Rápido

## Pré-requisitos

- Python 3.14+
- PostgreSQL 16 (ou Docker)
- Node.js 20+ (para frontend)
- Java 8+ (para PySpark, opcional)

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
# Editar — alterar senha e nome do banco antes de usar

# 4. Iniciar serviços
docker compose up -d

# 5. Migrations
alembic upgrade head

# 6. Seed (ordem correta — todos idempotentes)
python db/seed.py
python scripts/seed_icd11.py
python scripts/seed_scales_groups.py
python scripts/seed_diagnostic_data.py

# 7. Servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd mind-ui
npm install
npm run dev    # http://localhost:8000
```

```bash
# Ou com Node.js portable (Windows)
$env:Path = "$env:TEMP\node-portable\node-v20.12.0-win-x64;$env:Path"
npm run dev
```

### Dados de Exemplo

```bash
python db/populate_clinical.py
python scripts/check_integrity.py    # Verificar qualidade dos dados
```

## Serviços

| Serviço | URL | Auth |
|---|---|---|
| Frontend (Vite) | http://localhost:8000 | JWT |
| API (FastAPI) | http://localhost:8000/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.com` / `admin` |
| Airflow | http://localhost:8080 | `admin` / `admin` |

Usuários padrão: `admin` / `clinician` — senha definida via `.env`

## Escalas

Todas as 10 escalas estão traduzidas para português (itens, gravidade e interpretação):

| Escala | Itens | Português |
|---|---|---|
| PHQ-9 | 9 (0-3) | Questionário de Saúde do Paciente-9 |
| GAD-7 | 7 (0-3) | Transtorno de Ansiedade Generalizada-7 |
| MADRS | 10 (0-6) | Escala de Depressão de Montgomery-Åsberg |
| MDQ | 13 (0-1) | Questionário de Transtorno do Humor |
| PCL-5 | 20 (0-4) | Lista de Verificação de TEPT para DSM-5 |
| Y-BOCS | 10 (0-4) | Escala Obsessivo-Compulsiva de Yale-Brown |
| AUDIT | 10 (0-4) | Teste de Identificação de Transtornos por Uso de Álcool |
| ASRM | 5 (0-4) | Escala de Autoavaliação de Mania de Altman |
| ASRS | 18 (0-4) | Escala de Autorrelato de TDAH em Adultos |
| AQ-10 | 10 (0-1) | Quociente do Espectro Autista |

## Testes

```bash
pytest tests/ -v                     # 174+ testes
pytest tests/ --cov=app --cov-report=html
```

## Segurança (QA)

```bash
python -m bandit -c .bandit -r app/ scripts/ db/
python -m safety check
```

## ML Pipeline

```bash
python scripts/train_all.py          # Treinar 12 modelos
mlflow ui                            # http://localhost:5000
```

## DW ETL

```bash
python -c "from app.etl.dw_loader import run_full_etl; run_full_etl()"
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

- `CLINICAL_MANUAL.md` — Manual clínico completo (19 transtornos, 10 escalas em português)
- `STRUCTURE.md` — Estrutura detalhada do projeto
- `DESENVOLVIMENTO.md` — Documentação de desenvolvimento
- `SECURITY.md` — Política de segurança

**Status:** CDSS completo — 19 transtornos, 10 escalas em português, 12 modelos ML, 3 camadas de validação clínica.
