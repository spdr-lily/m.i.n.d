# M.I.N.D (Mental Intelligence & Network Data)

**Sistema de Apoio à Decisão Clínica (CDSS) para Diagnóstico em Saúde Mental**

Motor probabilístico de inferência diagnóstica baseado em DSM-5-TR e CID-11, com escalas psicométricas, dashboards clínicos, pipeline de ML e interface web React.

> **Aviso:** projeto de portfólio/pesquisa — não autorizado para uso clínico real. Dados clínicos gerados por seeds são **sintéticos**.

## Visão geral

- **API:** FastAPI + Pydantic v2 + SQLAlchemy 2.0
- **Banco:** PostgreSQL 16 + Alembic
- **Frontend:** React 18 + TypeScript + Vite + Ant Design (em `mind-ui/`)
- **Inferência:** motor híbrido (critérios DSM-5-TR + Bayesiano + escalas + blending ML)
- **ML/MLOps:** scikit-learn/XGBoost, MLflow, DVC (pipeline de 12 modelos)
- **DW/Analytics:** star schema + ETL (`app/etl/dw_loader.py`)
- **Segurança/LGPD:** JWT, RBAC, criptografia Fernet, auditoria, middlewares de segurança

## Início rápido (Docker)

Pré-requisitos: Docker Desktop. Crie um `.env` a partir de `.env.example` e defina **obrigatoriamente** `POSTGRES_PASSWORD`, `JWT_SECRET_KEY` e `ENCRYPTION_KEY` (e `FERNET_KEY` se for usar o profile de orquestração).

```bash
# Núcleo (postgres + redis + api)
docker compose up -d

# Perfis opcionais
docker compose --profile tools up -d           # pgAdmin
docker compose --profile proxy up -d           # Caddy/HTTPS (mind.local)
docker compose --profile orchestration up -d   # Airflow
docker compose --profile spark up -d          # Spark
```

Seeds (após a API/banco estarem prontos; ordem idempotente):
```bash
docker exec mind-api pip install -e . --no-deps
docker exec mind-api python db/seed.py
docker exec mind-api python scripts/seed_icd11.py
docker exec mind-api python scripts/seed_diagnostic_data.py
docker exec mind-api python scripts/seed_full_catalog.py
docker exec mind-api python scripts/seed_scales_groups.py
```

Acesso (padrão): API/Swagger em `http://localhost:8000/docs`, app em `http://localhost:8000`. Login padrão de desenvolvimento: `admin` / `admin`. Serviços opcionais por profile: pgAdmin `http://localhost:5050`, Airflow `http://localhost:8080`, HTTPS via Caddy em `https://mind.local` (profile `proxy`, requer configuração de hosts/certificados).

## Desenvolvimento local

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# API + testes + ML/MLOps (desenvolvimento completo)
pip install -e ".[dev,ml,mlops]"
# ou: pip install -r requirements.txt

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> Instalação mínima da API: `pip install -e .` (ou `pip install -r requirements-prod.txt`). Extras opcionais: `.[ml]`, `.[mlops]`, `.[orchestration]`, `.[spark]`.

Frontend: `cd mind-ui && npm install && npm run dev`. Testes: `python -m pytest tests/ -q`.

## Documentação

- [Guia de instalação](docs/GUIA_INSTALACAO.md) — cenários A/B, HTTPS, seeds e troubleshooting
- [Guia rápido](docs/QUICKSTART.md) — setup resumido
- [Desenvolvimento](docs/DESENVOLVIMENTO.md) — notas e diário técnico
- [Estrutura do projeto](docs/STRUCTURE.md) — organização de diretórios e convenções
- [Manual clínico](docs/CLINICAL_MANUAL.md) — referência clínica/funcional
- [Segurança](docs/SECURITY.md) — políticas e práticas
- [Portfólio](docs/README_PORTFOLIO.md) — visão para apresentação
- [AGENTS.md](AGENTS.md) — contexto operacional para agentes de IA
- Histórico/arquivos legados: [docs/archive/](docs/archive/)

## Licença

MIT
