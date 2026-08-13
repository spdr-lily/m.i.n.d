# M.I.N.D — Guia de Instalação Passo a Passo

Guia completo para rodar o projeto **M.I.N.D** (CDSS — Clinical Decision Support System) em dois cenários:

1. **[Cenário A — PostgreSQL nativo](#cenário-a--postgresql-nativo)** — PostgreSQL instalado na sua máquina + API/Frontend rodando localmente (uvicorn + Vite).
2. **[Cenário B — Docker](#cenário-b--docker)** — Tudo rodando em containers via Docker Compose.

> **Idioma:** Português (BR), como o restante do projeto.
> **Plataforma:** Windows (PowerShell). Comandos equivalentes para Linux/macOS indicados quando necessário.

---

## Pré-requisitos (ambos os cenários)

| Ferramenta | Versão | Cenário |
|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.14+ | A e B (A obrigatório, B só p/ seeds/frontend) |
| [Git](https://git-scm.com/) | qualquer | A e B |
| [PostgreSQL](https://www.postgresql.org/download/) | 16 | A (obrigatório) |
| [Node.js](https://nodejs.org/) | 20+ | A e B (frontend) |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | qualquer | B |

Verifique as versões instaladas:

```powershell
python --version
node --version
npm --version
git --version
docker --version        # só para o Cenário B
psql --version          # só para o Cenário A
```

---

## Preparação comum (clone + ambiente virtual)

Execute **antes de escolher o cenário**. O clone pode ser pulado se você já tem o repositório.

```powershell
# 1. Clonar o repositório
git clone https://github.com/SEU_USUARIO/m.i.n.d.git
cd m.i.n.d

# 2. Criar e ativar o ambiente virtual Python
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate         # Linux/macOS

# 3. Instalar dependências do backend (editable + produção)
pip install -e . --no-deps
pip install -r requirements.txt
```

> ⚠️ **Erro comum (E02/E03):** se `pip install` falhar com `No module named 'app'` ou `pydantic_core`, reinstale:
> ```powershell
> pip install --force-reinstall pydantic-core psycopg2-binary fpdf2 passlib
> pip install -e . --no-deps
> ```

---

## Cenário A — PostgreSQL nativo

Neste cenário o **PostgreSQL é instalado diretamente na máquina** (porta **5432**) e a API/Frontend rodam localmente, sem Docker para o app.

### Passo A1 — Instalar e iniciar o PostgreSQL 16

1. Baixe o instalador em <https://www.postgresql.org/download/windows/> e instale.
2. Durante a instalação, **defina a senha do usuário `postgres`** (você vai usá-la no `.env`).
3. Confirme que o serviço está rodando:

```powershell
# O serviço "postgresql-x64-16" deve estar em "Running"
Get-Service *postgres*
```

### Passo A2 — Configurar o `.env`

```powershell
Copy-Item .env.example -Destination .env
```

Edite o `.env` e ajuste **obrigatoriamente** a senha e, se quiser, o nome do banco:

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA_AQUI@localhost:5432/mind
POSTGRES_PASSWORD=SUA_SENHA_AQUI
POSTGRES_DB=mind
JWT_SECRET_KEY=gerar-chave-aleatoria-aqui
ENCRYPTION_KEY=gerar-outra-chave-aqui
```

> **Porta 5432** = PostgreSQL nativo. No Docker a porta é **5433** (ver Cenário B).
> Se usar nome de banco diferente, o banco também precisa ser criado com esse nome.

### Passo A3 — Criar o banco `mind`

```powershell
# Prompt de comando do PostgreSQL (adiciona o bin\ do PG no PATH) ou PowerShell
$env:Path = "$env:ProgramFiles\PostgreSQL\16\bin;$env:Path"
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE mind;"
# Será pedida a senha do usuário postgres definida no Passo A1
```

Se o banco já existir, ignore o aviso de erro "já existe".

### Passo A4 — Rodar as migrations

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
```

### Passo A5 — Rodar os seeds (ordem correta — todos idempotentes)

```powershell
.venv\Scripts\python.exe db/seed.py
.venv\Scripts\python.exe scripts/seed_icd11.py
.venv\Scripts\python.exe scripts/seed_scales_groups.py
.venv\Scripts\python.exe scripts/seed_diagnostic_data.py
.venv\Scripts\python.exe scripts/seed_clinical_data.py   # 200 pacientes, 21 escalas, 272k+ respostas
```

### Passo A6 — Subir o backend (API)

```powershell
.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

### Passo A7 — Subir o frontend

Em um **segundo terminal** (com o backend rodando):

```powershell
cd mind-ui
npm install
npm run dev    # http://localhost:8000
```

> O Vite usa proxy para `/api` → `localhost:8000`. Sempre use `http://localhost:8000` no navegador (porta 3000 foi removida — ver erro E01).

### Passo A8 — Acessar

| Recurso | URL |
|---|---|
| App | http://localhost:8000 |
| Swagger (docs) | http://localhost:8000/docs |
| Login | `admin` / `admin` |

### Passo A9 — Testes e qualidade (opcional)

```powershell
.venv\Scripts\python.exe -m pytest tests/ -q          # 548 testes
.venv\Scripts\python.exe -m bandit -c .bandit -r app/ scripts/ db/
```

### Encerrar o Cenário A

```powershell
# Parar uvicorn: Ctrl+C no terminal do backend
# Parar o frontend: Ctrl+C no terminal do frontend
# O PostgreSQL continua como serviço do Windows (opcional parar):
Stop-Service postgresql-x64-16
```

---

## Cenário B — Docker

Neste cenário **tudo roda em containers** (PostgreSQL, Redis, API, Airflow, Spark, pgAdmin, Caddy). O único serviço local é o frontend (Node) — ou você pode servir o frontend já compilado dentro do container da API.

### Passo B1 — Configurar o `.env`

```powershell
Copy-Item .env.example -Destination .env
```

Edite o `.env` e defina **obrigatoriamente** a senha e as chaves:

```env
POSTGRES_PASSWORD=SUA_SENHA_AQUI
POSTGRES_DB=mind
JWT_SECRET_KEY=gerar-chave-aleatoria-aqui
ENCRYPTION_KEY=gerar-outra-chave-aqui
```

> A `DATABASE_URL` do container é montada pelo `docker-compose.yml` usando `POSTGRES_PASSWORD` — não precisa apontar para `localhost`.

### Passo B2 — Subir banco e cache

```powershell
docker compose up -d postgres redis
```

> Se a porta **5433** do host estiver ocupada, ajuste o mapeamento em `docker-compose.yml` (linha `"5433:5432"`).

### Passo B3 — Construir a imagem da API

```powershell
docker compose build api
```

### Passo B4 — Subir a aplicação completa

```powershell
docker compose up -d api pgadmin caddy
```

Veja o status dos containers:

```powershell
docker compose ps
```

### Passo B5 — Rodar migrations e seeds dentro do container

```powershell
docker exec mind-api pip install -e . --no-deps

docker exec mind-api alembic upgrade head

docker exec mind-api python db/seed.py
docker exec mind-api python scripts/seed_icd11.py
docker exec mind-api python scripts/seed_scales_groups.py
docker exec mind-api python scripts/seed_diagnostic_data.py
docker exec mind-api python scripts/seed_clinical_data.py
```

> ⚠️ Os containers `api` e `airflow` já rodam `alembic upgrade head` automaticamente no startup (`entrypoint.sh`). O passo acima garante que está tudo aplicado.

### Passo B6 — Frontend (duas opções)

**Opção 1 (recomendada): frontend já servido pela API.**

O container da API já serve o frontend compilado em `/app/mind-ui/dist/`. Se você **alterou** o frontend localmente:

```powershell
cd mind-ui
npm install
npm run build
docker cp mind-ui/dist/. mind-api:/app/mind-ui/dist/
# Depois: hard refresh no navegador (Ctrl+F5) para limpar o cache
```

**Opção 2: modo dev com Vite.**

```powershell
cd mind-ui
npm install
npm run dev    # http://localhost:8000 (proxy /api → container)
```

### Passo B7 — Acessar

| Serviço | URL | Auth |
|---|---|---|
| App / API | http://localhost:8000 | JWT (`admin` / `admin`) |
| Swagger | http://localhost:8000/docs | JWT |
| pgAdmin | http://localhost:5050 | `admin@mind.example.com` / `admin` |
| PostgreSQL (host) | `localhost:5433` — senha em `POSTGRES_PASSWORD` | `postgres` |
| Airflow | http://localhost:8080 | `admin` / `admin` |
| Spark (Web UI) | http://localhost:9090 | — |

### Passo B8 — Testes e qualidade (opcional)

```powershell
docker exec mind-api python -m pytest tests/ -q          # 548 testes
docker exec mind-api python -m bandit -c .bandit -r app/ scripts/ db/
```

### Encerrar o Cenário B

```powershell
# Parar tudo
docker compose down

# Parar tudo E remover os volumes (⚠️ apaga os dados do banco, cache e logs)
docker compose down -v
```

> Depois de alterar a senha em `.env`, recrie o volume do banco:
> ```powershell
> docker compose down postgres
> docker volume rm mind_postgres_data
> docker compose up -d postgres
> ```

---

## Comparativo rápido

| Aspecto | Cenário A (PostgreSQL nativo) | Cenário B (Docker) |
|---|---|---|
| Instalação do banco | PostgreSQL instalado na máquina | Imagem `postgres:16-alpine` |
| Porta do banco | **5432** | **5433** |
| Redis | — (não usado localmente) | Container `redis:7-alpine` |
| API | `uvicorn` local | Container `mind-api` |
| Frontend | Vite local | Vite local ou `dist` no container |
| Migrations/seeds | via `.venv\Scripts\python.exe` | via `docker exec mind-api` |
| Isolamento | baixo | alto |
| Uso recomendado | Desenvolvimento rápido | Produção/equipe/consistência |

---

## Solução de problemas (resumo)

| Erro | Solução |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | `pip install -e . --no-deps` (ver E02) |
| `pydantic_core._pydantic_core` / `psycopg2._psycopg` | `pip install --force-reinstall pydantic-core psycopg2-binary` (ver E03) |
| `UnicodeDecodeError` no alembic | Corrigir senha no `.env` e iniciar o PostgreSQL (ver E04) |
| Login redireciona para porta 3000 | Deletar `vite.config.js`; usar só `vite.config.ts` (ver E01) |
| Alterações do frontend não aparecem no Docker | `docker cp mind-ui/dist/. mind-api:/app/mind-ui/dist/` + Ctrl+F5 (ver E25) |
| pgAdmin rejeita email | Usar `admin@mind.example.com` (ver E11) |
| HTTPS não funciona | Seguir o setup mkcert + Caddy (ver E15) |
| `mind-api` não sobe | `docker compose logs api` para ver o erro real |

---

## Documentação relacionada

- `QUICKSTART.md` — guia rápido condensado
- `README.md` — visão geral do projeto
- `DESENVOLVIMENTO.md` — documentação de desenvolvimento
- `CLINICAL_MANUAL.md` — manual clínico (19 transtornos, 21 escalas)
- `STRUCTURE.md` — estrutura do projeto
- `AGENTS.md` — decisões técnicas e contexto do projeto
