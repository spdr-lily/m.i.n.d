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

**Saída esperada:**

| Comando | Saída esperada |
|---|---|
| `python --version` | `Python 3.14.x` |
| `node --version` | `v20.x.x` ou superior |
| `npm --version` | `10.x.x` ou superior |
| `git --version` | `git version 2.x.x` |
| `docker --version` | `Docker version 2x.x.x, build <hash>` |
| `psql --version` | `psql (PostgreSQL) 16.x` |

> Se um dos comandos falhar com `não é reconhecido como cmdlet/função` (`not recognized`), a ferramenta não está no `PATH` — instale-a ou adicione ao `PATH` (ver [Solução de problemas](#solução-de-problemas)).

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

**Saída esperada:**

| Comando | Saída esperada |
|---|---|
| `git clone` | Pasta `m.i.n.d` criada; no final, `done.` |
| `python -m venv .venv` | Nenhuma saída; pasta `.venv\` criada no projeto |
| `.venv\Scripts\Activate.ps1` | O prompt passa a exibir `(.venv)` antes do caminho |
| `pip install -e . --no-deps` | `Successfully installed mind-cdss-0.2.2` |
| `pip install -r requirements.txt` | `Successfully installed <pacotes>...` e nenhuma mensagem de erro |

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

**Saída esperada:**

```
Status   Name               DisplayName
------   ----               -----------
Running  postgresql-x64-16  postgresql-x64-16 - PostgreSQL Server 16
```

> Se o `Status` for `Stopped`, inicie com `Start-Service postgresql-x64-16` (ou pelo app `pgAdmin` / Serviços do Windows).

### Passo A2 — Configurar o `.env`

```powershell
Copy-Item .env.example -Destination .env
```

**Saída esperada:** nenhuma saída em caso de sucesso — o arquivo `.env` é criado na raiz do projeto. Confirme com `Get-ChildItem -Force .env`.

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

**Saída esperada:**

```
Password:
CREATE DATABASE
```

> **Erro comum:** `ERROR: database "mind" already exists` — banco já criado em execução anterior; pode ignorar (os seeds são idempotentes).
> **Erro comum:** `psql: error: connection to server at "localhost" ... failed: Connection refused` — o serviço PostgreSQL não está rodando (volte ao Passo A1).

Se o banco já existir, ignore o aviso de erro "já existe".

### Passo A4 — Rodar as migrations

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
```

**Saída esperada:**

```
INFO  [alembic.runtime.migration] Running upgrade  -> 05ecbb7b2bc1, initial migration
INFO  [alembic.runtime.migration] Running upgrade 05ecbb7b2bc1 -> 031c8a8ec7b8, ...
...
INFO  [alembic.runtime.migration] Running upgrade  -> head
```

Encerra sem erros e o prompt volta ao normal. Para conferir, reexecute o mesmo comando — deve sair **sem** novas linhas `Running upgrade` (tudo já aplicado).

> **Erro comum (E04):** `UnicodeDecodeError` / `password authentication failed` — senha errada no `.env` ou PostgreSQL não iniciado. Corrija `DATABASE_URL` no `.env` e verifique o serviço (Passo A1).

### Passo A5 — Rodar os seeds (ordem correta — todos idempotentes)

```powershell
.venv\Scripts\python.exe db/seed.py
.venv\Scripts\python.exe scripts/seed_icd11.py
.venv\Scripts\python.exe scripts/seed_scales_groups.py
.venv\Scripts\python.exe scripts/seed_diagnostic_data.py
.venv\Scripts\python.exe scripts/seed_clinical_data.py   # 200 pacientes, 21 escalas, 272k+ respostas
```

**Saída esperada:** cada seed imprime um resumo curto, por exemplo `db/seed.py`:

```
Seed concluído. Referência: sex_types=..., disorders=191, symptoms=528, users=6, professionals=5
```

`seed_clinical_data.py` é o mais demorado (200 pacientes) e termina com o total de registros criados:

```
200 pacientes, 813 consultas, 4065 sintomas, 272355 respostas de escala, 4020 inferências
```

> **Idempotência:** rodar os seeds mais de uma vez **não** duplica dados — cada script atualiza/ignora o que já existe. Se um seed falhar no meio (ex.: conexão caiu), basta executá-lo novamente.

### Passo A6 — Subir o backend (API)

```powershell
.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

**Saída esperada:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     (Press CTRL+C to quit)
INFO:     Application startup complete.
```

> O comando **não termina** — o servidor fica rodando. Acesse http://localhost:8000/docs para confirmar que o Swagger carrega.
> **Erro comum:** `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): address already in use` — a porta 8000 já está ocupada por outro processo; ou feche o processo que a usa ou troque a porta (`--port 8001`).
> **Erro comum:** `ModuleNotFoundError: No module named 'app'` — rode com `.venv\Scripts\python.exe -m uvicorn app.main:app ...` após `pip install -e . --no-deps` (ver E02).

### Passo A7 — Subir o frontend

Em um **segundo terminal** (com o backend rodando):

```powershell
cd mind-ui
npm install
npm run dev    # http://localhost:8000
```

> O Vite usa proxy para `/api` → `localhost:8000`. Sempre use `http://localhost:8000` no navegador (porta 3000 foi removida — ver erro E01).

**Saída esperada:**

| Comando | Saída esperada |
|---|---|
| `npm install` | `added <n> packages in <t>s` e nenhuma mensagem de erro |
| `npm run dev` | `VITE v5.x.x ready in <t> ms` + `➜ Local: http://localhost:8000/` |

> **Erro comum (E01):** `npm run dev` sobe na porta **3000** (e não em 8000) — existe um `vite.config.js` conflitante na raiz. Deixe **apenas** `vite.config.ts` (deletar `vite.config.js` e `vite.config.d.ts`).
> **Erro comum:** erros de tipo no terminal (`TypeScript errors`) — ver [E07](#solução-de-problemas).

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

**Saída esperada:**

| Comando | Saída esperada |
|---|---|
| `pytest tests/ -q` | `548 passed in <tempo>s` |
| `bandit ...` | `Run started: ...` / `No issues identified.` (zero violações) |

> **Erro comum:** alguns testes falham com `assert` de seed/contagem — rode os seeds na ordem do Passo A5 antes de testar.

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

**Saída esperada:** nenhuma saída em caso de sucesso — o arquivo `.env` é criado na raiz do projeto. Confirme com `Get-ChildItem -Force .env`.

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

**Saída esperada:**

```
[+] Running 3/3
 ✔ Network mind_mind-network  Created
 ✔ Container mind-postgres    Started
 ✔ Container mind-redis       Started
```

> **Erro comum:** `Error response from daemon: driver failed programming external connectivity on endpoint mind-postgres (... bind: An attempt was made to access a socket in a way forbidden by its access permissions.)` — a porta **5433** do host está ocupada; ajuste o mapeamento em `docker-compose.yml` (linha `"5433:5432"`) ou use `docker compose down` e suba apenas o que falta.

### Passo B3 — Construir a imagem da API

```powershell
docker compose build api
```

**Saída esperada:**

```
[+] Building <t>s (N/N) FINISHED
...
 => exporting to image
 => => naming to docker.io/library/mind-api:latest
```

Termina com a imagem nomeada `mind-api:latest` e o prompt volta ao normal.

### Passo B4 — Subir a aplicação completa

```powershell
docker compose up -d api pgadmin caddy
```

Veja o status dos containers:

```powershell
docker compose ps
```

**Saída esperada:**

| Comando | Saída esperada |
|---|---|
| `docker compose up -d api pgadmin caddy` | `Container mind-api ... Started`, `Container mind-pgadmin ... Started`, `Container mind-caddy ... Started` |
| `docker compose ps` | Tabela com `mind-postgres`, `mind-redis`, `mind-api`, `mind-pgadmin`, `mind-caddy` todos com `STATUS` = `Up` / `Healthy` |

> **Erro comum:** o `mind-api` reinicia em loop (`Restarting`) — veja o log real com `docker compose logs api` (ex.: senha do `.env` errada, porta ocupada ou problema no `entrypoint.sh` — ver E09/E04).
> **Erro comum:** `mind-caddy` retorna 502 (`Bad Gateway`) logo após subir — o Caddy conectou antes da API ficar pronta. Aguarde a API ficar `Healthy` e `docker compose restart caddy` (ver E17).

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

**Saída esperada:** igual ao Cenário A — `docker exec` sem saída indica sucesso dos seeds; cada script imprime seu resumo (`Seed concluído...`, contagens de pacientes/consultas/etc.).

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

**Saída esperada:**

| Comando | Saída esperada |
|---|---|
| `npm install` | `added <n> packages in <t>s` |
| `npm run build` | `✓ built in <t>s` — gera a pasta `mind-ui/dist/` com os assets (`index.html`, `assets/...`) |
| `docker cp mind-ui/dist/. mind-api:/app/mind-ui/dist/` | Nenhuma saída em caso de sucesso |

> **Erro comum (E25):** as alterações do frontend não aparecem no navegador mesmo após o build — o container serve os arquivos antigos. Copie o `dist` com `docker cp` e faça **hard refresh** (Ctrl+F5).
> **Erro comum (E07):** `npm run build` falha com erros de TypeScript — corrija as tipagens e rode o build novamente.

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

**Saída esperada:** igual ao Cenário A — `548 passed` e `No issues identified.`

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

## Solução de problemas (resumo E1–E26)

> Referências completas no Error Log do `AGENTS.md`. `E##` = entrada do log.

### Instalação e ambiente

| Erro | Solução |
|---|---|
| Comando `python`/`node`/etc. não reconhecido | Adicionar a ferramenta ao `PATH` do Windows |
| `ModuleNotFoundError: No module named 'app'` | `pip install -e . --no-deps` (E02) |
| `pydantic_core._pydantic_core` / `psycopg2._psycopg` corrompidos | `pip install --force-reinstall pydantic-core psycopg2-binary fpdf2 passlib` (E03) |
| `UnicodeDecodeError` no alembic / senha errada | Corrigir senha no `.env` e iniciar o PostgreSQL (E04) |
| Login redireciona para porta 3000 | Deletar `vite.config.js`; manter só `vite.config.ts` (E01) |
| Frontend build falha com erros TypeScript | Corrigir tipagens e rebuild (E07) |
| `bitnami/spark` image not found no build | Usar `apache/spark:3.5.0` (E05) |
| Build Docker muito lento (timeout) | Usar `requirements-prod.txt` só com o essencial (E06) |

### Docker e serviços

| Erro | Solução |
|---|---|
| `mind-api` não sobe / reinicia em loop | `docker compose logs api` para ver o erro real (senha, porta, entrypoint) |
| Container reinicia com `no such file or directory` | Converter `entrypoint.sh` de CRLF para LF (E09) |
| Uvicorn falha: `address already in use` (porta 8000) | Fechar o processo que usa a porta ou trocar para `--port 8001` |
| Porta 5433 do host ocupada | Ajustar `"5433:5432"` em `docker-compose.yml` |
| Caddy 502 Bad Gateway | Aguardar API `Healthy` e `docker compose restart caddy` (E17) |
| Alterações do frontend não aparecem no Docker | `docker cp mind-ui/dist/. mind-api:/app/mind-ui/dist/` + Ctrl+F5 (E25) |
| pgAdmin rejeita email | Usar `admin@mind.example.com` (E11) |
| HTTPS não funciona | Seguir o setup mkcert + Caddy (E15) |
| `favicon.svg` 404 no console | Referenciar `/logo.png` no `index.html` (E16) |

### Banco de dados e DW

| Erro | Solução |
|---|---|
| `ERROR: database "mind" already exists` | Pode ignorar — seeds são idempotentes |
| Alembic falha em DB fresco (`permission denied to create schema`) | Migrations com `CREATE SCHEMA IF NOT EXISTS` / `has_table()` (E08) |
| Migrations de views DW falham em DB fresco (schema `dw` ausente) | Views criadas pelo ETL (`run_full_etl`) com verificações `to_regnamespace`/`to_regclass`; reexecute o ETL (E26) |
| Spark: `ClassNotFoundException: org.postgresql.Driver` | Montar `postgresql-42.7.1.jar` em `/opt/spark/work-dir/` + `--driver-class-path` (E20) |
| Spark: `relation "X" does not exist` | Usar nomes completos `clinical.patient_profile`, `diagnostic.disorders` etc. (E20) |
| `pip install dvc-postgres` falha | Usar `dvc[postgres]>=3.48.0` (E18) |

### Frontend e API

| Erro | Solução |
|---|---|
| Página em branco após login | ProtectedRoute com `Spin`, CSP com `'unsafe-eval'`, ErrorBoundary (E13) |
| `Cannot convert undefined or null to object` no dashboard | Resposta vazia deve incluir `gender_identity_distribution: {}`; usar optional chaining (E14) |
| Gráficos de Escolaridade/Etnia não aparecem | Endpoint usa `StatisticsService` — incluir `education_level_distribution`/`ethnicity_distribution` no retorno (E23) |
| Cores do gráfico de gênero erradas | Usar função `getGenderColor()` com comparação direta de string (E24) |
| Logo em branco no login | Middleware de SPA deve verificar `os.path.isfile()` antes do fallback (E12) |
| CORS bloqueando requisições | Manter `connect-src 'self'` no CSP e ajustar `CORS_ORIGINS` (E19) |
| API não sobe: `No module named 'mlflow'/'sklearn'` | Imports lazy dentro dos endpoints (E10) |
| Inferência retorna erro 500: `NameError: calculate_criteria_confidence` | Import correto do `confidence_calculator` (E21) |
| Explanation retorna 500: `scale_scores` indefinido | Consultar `scale_scores` dentro do método `get_explanation()` (E22) |

---

## Documentação relacionada

- `QUICKSTART.md` — guia rápido condensado
- `README.md` — visão geral do projeto
- `DESENVOLVIMENTO.md` — documentação de desenvolvimento
- `CLINICAL_MANUAL.md` — manual clínico (19 transtornos, 21 escalas)
- `STRUCTURE.md` — estrutura do projeto
- `AGENTS.md` — decisões técnicas e contexto do projeto
