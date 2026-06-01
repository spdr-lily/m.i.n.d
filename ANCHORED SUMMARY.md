## Goal
Complete M.I.N.D CDSS — probabilistic diagnostic inference engine for mental health, LGPD/GDPR compliant, DSM-5-TR and ICD-11.

## Constraints & Preferences
- GitHub: `spdr-lily/m.i.n.d`
- Pydantic v2 only
- LGPD/GDPR: UUID-based, PII separated, Fernet AES encryption
- Human-in-the-loop for all diagnostic outputs
- Stack completo integrado: PostgreSQL, SQLAlchemy, Alembic, Pydantic, FastAPI, Pandas, Apache Airflow, PySpark

## Progress
### Done
- **Todas as fases 1–8 concluídas:** models, schemas, repositories, services, API, auth/rbac, audit middleware, assessment scales, Bayesian Network, dashboards/metrics, clinical documentation
- **PySpark (2 novos jobs):**
  - `spark/jobs/population_metrics.py` — age distribution, disorder prevalence, scale statistics (média/std), agregados em lote via JDBC
  - `spark/jobs/data_import.py` — ETL de CSV para PostgreSQL: symptoms e patients com geração de UUID via `expr("uuid()")`
  - `spark/submit.py` — CLI para submissão dos 3 jobs (batch_inference, population_metrics, data_import)
  - PySpark 3.5.0 instalado e compilado no `.venv` (Python 3.12)
- **Credenciais:** `mind_user`/`mind_password`/`mind_db` → `postgres`/`137_Cmspelo`/`mind` em todos os arquivos
- **.env de produção:** `JWT_SECRET_KEY` e `ENCRYPTION_KEY` gerados
- **CI/CD:** `.github/workflows/ci.yml` — PostgreSQL 16 service, flake8, black, mypy, pytest (unit + integration), codecov
- **Documentação Clínica:** `CLINICAL_MANUAL.md` — manual completo em pt-BR
- **Pandas:** `metrics_service.py` refatorado — `pd.cut()`, `pd.read_sql()`, moving averages, correlações
- **Apache Airflow:** 4 DAGs em `dags/` com `docker-compose.yml` (webserver + scheduler, porta 8080, admin/admin)
- **Bug fixes:** emoji removido, PYTHONPATH resolvido, healthcheck corrigido, `QUICKSTART.md` corrigido, test key name corrigida

### In Progress
- (none)

### Blocked
- Docker Desktop não está rodando no ambiente local (serviço `com.docker.service` parado) — necessário iniciar manualmente para testar `docker compose up -d`

## Key Decisions
- PySpark 3.5.0 (compatível com Windows + Python 3.12); 4.x exige build from source sem wheel disponível
- `uuid()` ausente no PySpark 3.x → substituído por `expr("uuid()")` (SQL expression)
- JDBC driver `postgresql-42.7.1.jar` esperado em `spark.jars`; se ausente, SparkSession falha ao escrever/ler no PostgreSQL

## Next Steps
1. Iniciar Docker Desktop manualmente e testar `docker compose up -d`
2. Se deploy em cloud: configurar Render/Railway/Fly.io com CI/CD

## Critical Context
- **140/140 testes passando** (unit + integration) com PySpark 3.5.0 instalado
- PostgreSQL `postgresql-x64-18` rodando em `localhost:5432`; DBs: `mind` (prod), `mind_test` (testes)
- Servidor FastAPI testado em `http://localhost:8001` — health, docs, scales respondendo
- Docker compose tem 5 serviços: `postgres`, `app`, `pgadmin`, `airflow-webserver`, `airflow-scheduler`
- `.venv` usa Python 3.12.13 via Anaconda; `pip install -e .` instalou o pacote em editable mode

## Relevant Files
- `spark/jobs/population_metrics.py`: PySpark job de métricas populacionais
- `spark/jobs/data_import.py`: PySpark ETL job (CSV → PostgreSQL)
- `spark/submit.py`: CLI helper para submissão de jobs Spark
- `spark/config.py`: Config compartilhada (JDBC URL, DB_PROPERTIES, SPARK_MASTER)
- `spark/jobs/batch_inference.py`: PySpark batch inference job (criado anteriormente)
- `.github/workflows/ci.yml`: CI pipeline completo
- `CLINICAL_MANUAL.md`: documentação clínica (Fase 8)
- `docker-compose.yml`: 5 serviços, healthcheck corrigido, Airflow integrado
- `dags/`: 4 DAGs (inference, quality, metrics, alerts) + `config.py`
- `app/services/metrics_service.py`: refatorado com Pandas
- `app/main.py`, `app/core/config.py`, `migrations/`, `alembic.ini`, `QUICKSTART.md` — todos corrigidos