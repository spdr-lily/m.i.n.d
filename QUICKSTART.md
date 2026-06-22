# M.I.N.D — Guia Rápido

## Pré-requisitos

- Python 3.14+
- PostgreSQL 16 (Docker recomendado)
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
.venv\Scripts\python.exe -m alembic upgrade head

# 6. Seed (ordem correta — todos idempotentes)
.venv\Scripts\python.exe db/seed.py
.venv\Scripts\python.exe scripts/seed_icd11.py
.venv\Scripts\python.exe scripts/seed_scales_groups.py
.venv\Scripts\python.exe scripts/seed_diagnostic_data.py
.venv\Scripts\python.exe scripts/seed_clinical_data.py     # 50 pacientes, 20 escalas, 3k+ respostas

# 7. Servidor
.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
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
.venv\Scripts\python.exe scripts/seed_clinical_data.py          # 50 pacientes, 20 escalas
.venv\Scripts\python.exe scripts/check_integrity.py             # Verificar qualidade dos dados
```

## Serviços

| Serviço | URL | Auth |
|---|---|---|---|
| Frontend / API | http://localhost:8000 | JWT |
| API Docs (Swagger) | http://localhost:8000/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.example.com` / `admin` |
| PostgreSQL (host) | `localhost:5433` — senha em `POSTGRES_PASSWORD` no `.env` |

Usuários padrão: `admin` / `admin` — senha definida via seed (`db/seed.py`)

## Escalas

Todas as 20 escalas estão traduzidas para português (itens, gravidade e interpretação):

### Escalas Clínicas

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

### Escalas Neuropsicológicas

| Escala | Itens | Português |
|---|---|---|
| BFP | 6 (0-4) | Bateria Fatorial da Personalidade (Big Five) |
| MEMÓRIA | 8 (0-2) | Teste de Rastreio de Funções Mnêmicas |
| QI - RASTREIO | 10 (0-3) | Teste de Rastreio Cognitivo |
| RECONHECIMENTO DE ROSTOS | 6 (0-2) | Teste de Reconhecimento de Rostos |
| FLUÊNCIA VERBAL | 8 (0-2) | Teste de Fluência Verbal (FAS + semântica) |
| TESTE DO RELÓGIO | 6 (0-3) | Teste do Desenho do Relógio |
| TRILHAS | 6 (0-3) | Teste de Trilhas A e B (TMT) |
| STROOP | 8 (0-2) | Teste de Stroop (Victoria Version) |
| CANCELAMENTO | 6 (0-2) | Teste de Cancelamento |
| FIGURA COMPLEXA DE REY | 8 (0-3) | Figura Complexa de Rey-Osterrieth |

## Testes

```bash
.venv\Scripts\python.exe -m pytest tests/ -v          # 548 testes
.venv\Scripts\python.exe -m pytest tests/ --cov=app --cov-report=html
```

## Segurança (QA)

```bash
.venv\Scripts\python.exe -m bandit -c .bandit -r app/ scripts/ db/
.venv\Scripts\python.exe -m safety check
```

## ML Pipeline

```bash
.venv\Scripts\python.exe scripts/train_all.py          # Treinar 12 modelos
.venv\Scripts\mlflow.exe ui                            # http://localhost:5000
```

## DW ETL

```bash
.venv\Scripts\python.exe -c "from app.etl.dw_loader import run_full_etl; run_full_etl()"
```

## ⚠️ Notas importantes

- **Porta 5433**: O PostgreSQL do Docker mapeia `5433:5432`. Se tiver PostgreSQL local na porta 5432, use `localhost:5433` para conexões do host (alembic, scripts, pgAdmin).
- **`alembic` via venv**: Sempre use `.venv\Scripts\python.exe -m alembic` no lugar de `alembic` direto para evitar conflito com Python global.
- **Senha no `.env`**: Adicione `POSTGRES_PASSWORD=sua_senha` no `.env` — tanto o container quanto a `DATABASE_URL` usam essa variável. Após alterar, recrie o container: `docker compose down postgres; docker volume rm mind_postgres_data; docker compose up -d postgres`.

## PySpark (opcional)

```bash
pip install pyspark==3.5.0
.venv\Scripts\python.exe spark/submit.py population_metrics
.venv\Scripts\python.exe spark/submit.py data_import --csv data/pacientes.csv
```

## Comandos úteis

```bash
.venv\Scripts\python.exe -m black app/ tests/                    # Formatar
.venv\Scripts\python.exe -m flake8 app/ tests/                   # Lint
.venv\Scripts\python.exe -m mypy app/                            # Type check
.venv\Scripts\python.exe -m alembic revision --autogenerate -m "desc"  # Nova migration
.venv\Scripts\python.exe -m alembic upgrade head                 # Aplicar migrations
```

## Documentação

- `CLINICAL_MANUAL.md` — Manual clínico completo (19 transtornos, 20 escalas em português)
- `STRUCTURE.md` — Estrutura detalhada do projeto
- `DESENVOLVIMENTO.md` — Documentação de desenvolvimento
- `SECURITY.md` — Política de segurança

**Status:** CDSS completo — ~192 transtornos DSM-5-TR (19 com pipeline clínico completo), 20 escalas em português, 12 modelos ML, 3 camadas de validação clínica.
