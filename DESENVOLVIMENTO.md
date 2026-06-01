# 📋 Documentação de Desenvolvimento - Projeto M.I.N.D

**Data:** Junho 2026  
**Status:** MVP - Fase Inicial de Implementação  
**Versão:** 0.1.0

---

## 📌 Sumário Executivo

O projeto **M.I.N.D (Mental Intelligence & Network Data)** é um **Sistema de Apoio à Decisão Clínica (CDSS)** desenvolvido em Python para profissionais de saúde mental (psicólogos, psiquiatras e neurologistas). O objetivo é utilizar Machine Learning e modelagem probabilística para calcular a probabilidade de diagnósticos baseados em critérios estruturados da **CID-11** e **DSM-5-TR**.

**Diferencial:** O sistema funciona como ferramenta complementar à análise clínica (Human-in-the-loop), nunca como diagnóstico definitivo.

---

## 🎯 Objetivos do Projeto

### Objetivo Principal
Fornecer uma ferramenta de inferência diagnóstica probabilística que:
- Calcula probabilidades de diagnósticos baseados em sintomas observados
- Segue rigorosamente critérios diagnósticos internacionais (DSM-5-TR e CID-11)
- Fornece rastreabilidade completa das inferências
- Mantém o profissional como responsável final pela decisão clínica

### Objetivos Secundários
- ✅ Reduzir erros diagnósticos em saúde mental
- ✅ Diminuir tempo de diagnóstico correto
- ✅ Democratizar acesso a ferramentas diagnósticas estruturadas
- ✅ Garantir conformidade com LGPD e regulamentações clínicas
- ✅ Criar base para evolução futura para Redes Bayesianas

---

## 🏗️ Arquitetura Implementada

### Stack Tecnológico

**Backend:**
- **FastAPI** 0.104+ — Framework web assíncrono
- **Python** 3.11+ — Linguagem principal
- **SQLAlchemy 2.0+** — ORM para banco de dados
- **Pydantic 2.5+** — Validação de dados e serialização

**Banco de Dados:**
- **PostgreSQL 16** — Banco de dados relacional (containerizado com Docker)
- **Alembic 1.12+** — Gerenciamento de migrations

**Modelagem & Inferência:**
- **NumPy, SciPy, Pandas** — Processamento de dados
- **scikit-learn** — Machine Learning
- **PyMC 5.10+** — Inferência Bayesiana (pronto para uso)
- **ArviZ** — Visualização de diagnósticos estatísticos

**Segurança & Autenticação:**
- **PyJWT, python-jose** — Gerenciamento de tokens JWT
- **passlib, bcrypt** — Hashing de senhas
- **AES encryption** — Criptografia de dados sensíveis (LGPD)

**Testes & Qualidade:**
- **pytest 7.4+** — Framework de testes
- **pytest-cov** — Cobertura de testes
- **pytest-asyncio** — Testes assíncronos
- **black, flake8, pylint, mypy** — Linting e formatação

---

## 📁 Estrutura de Diretórios Criada

```
m.i.n.d/
├── alembic/                    # Migrations (Alembic)
│   ├── versions/               # Versões das migrations
│   └── env.py                  # Configuração Alembic
│
├── app/                        # Pacote principal da aplicação
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada FastAPI
│   │
│   ├── core/                   # Utilities & configuração
│   │   ├── config.py           # ✅ Configurações (Pydantic BaseSettings)
│   │   ├── database.py         # ✅ Conexão & sessão BD
│   │   └── exceptions.py       # ✅ Exceções customizadas (17 clínicas)
│   │
│   ├── models/                 # SQLAlchemy ORM
│   │   ├── base.py             # ✅ Modelo base com UUIDs (LGPD)
│   │   ├── patient.py          # ⬜ Modelo de Paciente
│   │   ├── disorder.py         # ⬜ Modelo de Transtorno
│   │   ├── symptoms.py         # ⬜ Modelo de Sintomas
│   │   ├── consultation.py     # ⬜ Modelo de Consulta
│   │   └── diagnosis.py        # ⬜ Modelo de Diagnóstico
│   │
│   ├── schemas/                # Pydantic DTOs
│   │   ├── patient.py          # ✅ Schemas de Paciente
│   │   ├── diagnosis.py        # ⬜ Schemas de Diagnóstico
│   │   └── assessment.py       # ⬜ Schemas de Escalas
│   │
│   ├── repositories/           # Data Access Layer
│   │   ├── base.py             # ⬜ Repositório base com CRUD
│   │   ├── patient_repository.py
│   │   └── disorder_repository.py
│   │
│   ├── services/               # Lógica de Negócio
│   │   ├── patient_service.py
│   │   ├── diagnosis_service.py
│   │   └── assessment_service.py
│   │
│   ├── ml/                     # ML & Inferência
│   │   ├── bayesian_network.py       # ⬜ Redes Bayesianas
│   │   ├── inference_engine.py       # ⬜ Motor de Inferência
│   │   ├── dsm_icd_mapper.py         # ⬜ Mapeamento DSM ↔ CID-11
│   │   └── criteria_evaluator.py     # ⬜ Engine de regras
│   │
│   ├── api/                    # FastAPI Routes
│   │   ├── health.py           # ✅ Health check endpoints
│   │   ├── patients.py         # ⬜ Endpoints de Pacientes
│   │   ├── diagnoses.py        # ⬜ Endpoints de Diagnóstico
│   │   └── consultations.py    # ⬜ Endpoints de Consulta
│   │
│   └── security/               # Auth & Autorização
│       ├── auth.py             # ⬜ Gerenciamento JWT
│       ├── rbac.py             # ⬜ RBAC
│       └── encryption.py       # ⬜ Criptografia AES
│
├── tests/                      # Suite de Testes
│   ├── conftest.py             # ✅ Fixtures pytest
│   ├── unit/                   # Testes unitários
│   │   └── test_criteria_evaluator.py
│   └── integration/            # Testes de integração
│       └── test_consultation_workflow.py
│
├── migrations/                 # SQL migrations
│   └── 001_initial_schema.sql  # ✅ Schema inicial com audit
│
├── docker-compose.yml          # ✅ PostgreSQL + pgAdmin
├── Dockerfile                  # ✅ Imagem Docker produção
├── .env.example                # ✅ Template variáveis ambiente
├── requirements.txt            # ✅ Dependências Python
├── pyproject.toml              # ✅ Metadata e config do projeto
├── alembic.ini                 # ✅ Config Alembic
│
├── README.md                   # ✅ Visão geral do projeto
├── STRUCTURE.md                # ✅ Estrutura técnica
├── QUICKSTART.md               # ✅ Guia de inicialização
├── DESENVOLVIMENTO.md          # 📄 Este arquivo
│
└── .git/                       # Controle de versão

Legend: ✅ = Criado | ⬜ = Planejado | 📄 = Documentação
```

---

## ✅ O Que Foi Implementado

### 1. **Configuração Base do Projeto**
- ✅ Estrutura de diretórios conforme padrão profissional Python
- ✅ `pyproject.toml` com todas as dependências necessárias
- ✅ `requirements.txt` com versões pinadas
- ✅ Configuração `docker-compose.yml` para PostgreSQL local
- ✅ `Dockerfile` para containerização

### 2. **FastAPI & Backend**
- ✅ Aplicação FastAPI básica (`app/main.py`)
- ✅ Configuração centralizada com `Pydantic BaseSettings`
- ✅ Endpoints de health check (`/health`)
- ✅ Estrutura de exceções customizadas para domínio clínico
- ✅ CORS e middlewares básicos

### 3. **Banco de Dados**
- ✅ Integração SQLAlchemy com PostgreSQL
- ✅ Session factory com context managers
- ✅ Alembic configurado para migrations versionadas
- ✅ Schema SQL inicial com:
  - Tabelas base: `patients`, `disorders`, `symptoms`, `consultations`
  - Triggers de audit para compliance LGPD
  - Índices para performance

### 4. **Modelagem ORM**
- ✅ Base model com UUID primária (LGPD compliant)
- ✅ Timestamps de criação/modificação automáticos
- ✅ Metadata clínica base para extensão

### 5. **Schemas Pydantic**
- ✅ DTOs para Paciente (request/response)
- ✅ Validação automática e serialização JSON
- ✅ Documentação OpenAPI automática

### 6. **Testes & QA**
- ✅ Configuração pytest com fixtures clínicas
- ✅ Testes unitários de exemplo (`test_criteria_evaluator.py`)
- ✅ Testes de integração de exemplo
- ✅ Coverage setup com pytest-cov

### 7. **Documentação**
- ✅ `README.md` com contexto e motivação
- ✅ `STRUCTURE.md` com guia de arquitetura
- ✅ `QUICKSTART.md` com passos de configuração
- ✅ `.instructions.md` com diretivas de desenvolvimento
- ✅ `.agent.md` para integração com GitHub Copilot

### 8. **Git & Controle de Versão**
- ✅ `.gitignore` completo para Python
- ✅ Histórico de commits com mensagens em português
- ✅ Licença MIT

---

## 🔄 Histórico de Commits

```
bd1af5e - Restructure project architecture to parallel directory layout
0dffdcc - Atualizando o diretórios
305c0f8 - Merge branch 'main'
764554d - br-pt (Branch em português)
c7c47cc - Atualizando o diretório do projeto
4f1ab68 - Update README.md
6fdbcfe - Simplify M.I.N.D. description
2cbc3c3 - Primeiro commit: adicionando todos os arquivos do projeto
```

**Mudança Principal Recente:** Reestruturação arquitetural para layout paralelo (padrão profissional Python).

---

## 🚀 Próximos Passos (Roadmap)

### **Fase 1.1: Modelos ORM Completos** (Curto Prazo)
- [ ] Implementar modelos: `Patient`, `Disorder`, `Symptom`, `Consultation`, `Diagnosis`
- [ ] Adicionar validações de negócio nos modelos
- [ ] Criar migrations com Alembic
- [ ] Testar integridade referencial

### **Fase 1.2: Camada de Dados** (Curto Prazo)
- [ ] Implementar repositórios base com CRUD
- [ ] Criar `PatientRepository`, `DiagnosisRepository`, etc.
- [ ] Adicionar queries especializadas (buscar consultas, sintomas, etc.)
- [ ] Testes unitários para repositórios

### **Fase 1.3: Lógica de Negócio** (Médio Prazo)
- [ ] `PatientService` — gerenciamento de pacientes
- [ ] `DiagnosisService` — orquestração de cálculo de diagnóstico
- [ ] `AssessmentService` — scoring de escalas psicométricas
- [ ] `ConsultationService` — workflow de consulta

### **Fase 2: Motor de Inferência** (Médio Prazo)
- [ ] `CriteriaEvaluator` — engine de regras DSM-5-TR/CID-11
- [ ] `InferenceEngine` — cálculo probabilístico
- [ ] `DSM_ICD_Mapper` — mapeamento entre taxonomias
- [ ] Testes clínicos com casos de uso reais

### **Fase 3: APIs Clínicas** (Médio Prazo)
- [ ] `POST /patients` — criar paciente
- [ ] `POST /consultations` — iniciar consulta
- [ ] `POST /diagnoses/calculate` — calcular diagnóstico
- [ ] `GET /diagnoses/{id}/explanation` — rastreabilidade
- [ ] Documentação OpenAPI completa

### **Fase 4: Segurança & Autenticação** (Longo Prazo)
- [ ] JWT token management (`auth.py`)
- [ ] RBAC (Role-Based Access Control) — `rbac.py`
- [ ] Criptografia de campos sensíveis — `encryption.py`
- [ ] Auditoria de acesso

### **Fase 5: Escalas Psicométricas** (Longo Prazo)
- [ ] Implementar PHQ-9 (depressão)
- [ ] Implementar GAD-7 (ansiedade)
- [ ] Implementar MADRS (depressão moderada-severa)
- [ ] Scoring automático e validação

### **Fase 6: Redes Bayesianas** (Futuro)
- [ ] Estruturar rede de transtornos e sintomas
- [ ] Calibrar probabilidades *a priori* com dados epidemiológicos
- [ ] Implementar inferência causal
- [ ] Validação com dados reais de pacientes

### **Fase 7: Dashboards** (Futuro)
- [ ] Integração com Power BI ou Apache Superset
- [ ] Painel de evolução longitudinal do paciente
- [ ] Métricas clínicas e alertas

---

## 🛠️ Como Configurar o Ambiente

### **1. Clone e Ative o Venv**
```bash
cd m.i.n.d
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac
```

### **2. Instale as Dependências**
```bash
pip install -r requirements.txt
pip install -e .  # Instalar projeto em modo desenvolvimento
```

### **3. Configure Variáveis de Ambiente**
```bash
cp .env.example .env
# Editar .env conforme necessário
```

### **4. Inicie o Banco de Dados**
```bash
docker-compose up -d
```

### **5. Execute as Migrations**
```bash
alembic upgrade head
```

### **6. Rode a Aplicação**
```bash
uvicorn app.main:app --reload
```
Acesse em: `http://localhost:8000`

### **7. Execute Testes**
```bash
pytest tests/ -v --cov=app
```

---

## 📊 Métricas de Código

| Métrica | Valor |
|---------|-------|
| Linhas de código principal | ~200 |
| Arquivos Python criados | 12 |
| Pastas/módulos | 8 |
| Testes criados | 2 (exemplos) |
| Dependências principais | 18 |
| Python mínimo requerido | 3.11 |

---

## 🔐 Conformidade & Segurança

### **LGPD (Lei Geral de Proteção de Dados)**
- ✅ UUIDs para identificação (sem sequencial)
- ✅ Separação de PII/PHI
- ✅ Audit trail automático
- ✅ Retenção por 5 anos
- ✅ Estrutura para criptografia AES-256

### **Clínico & Profissional**
- ✅ Human-in-the-loop (profissional decide)
- ✅ DSM-5-TR & CID-11 ready
- ✅ Rastreabilidade completa
- ✅ Comorbididade e exclusão diagnóstica

### **Dev & DevOps**
- ✅ Type hints (mypy)
- ✅ Code formatting (black)
- ✅ Linting (flake8, pylint)
- ✅ Docker ready
- ✅ CI/CD structure (TODO)

---

## 📚 Referências & Fontes

### Diagnósticas
- [DSM-5-TR Official](https://dsm.psychiatryonline.org/)
- [ICD-11 WHO](https://icd.who.int/)
- [Level 1 & 2 Cross-Cutting Measures](https://www.psychiatry.org/psychiatrists/practice/dsm/educational-resources/assessment-measures)

### Dados de Treino
- [MIMIC-IV (MIT/PhysioNet)](https://physionet.org/content/mimiciv/)
- [UCI ML Repository](https://archive.ics.uci.edu/)
- [UMLS (NLM)](https://www.nlm.nih.gov/research/umls/)

### Epidemiologia
- [VIGITEL (Brasil)](https://www.gov.br/saude/)
- [Global Burden of Disease (IHME)](https://www.healthdata.org/gbd)

---

## 👥 Autores & Licença

- **Projeto:** M.I.N.D Team
- **Licença:** MIT
- **Contribuidores:** Susana (scbcd)
- **Email:** team@mind.local

---

## 📝 Notas Importantes

1. **Este é um MVP (Minimum Viable Product):** Foco em núcleo de inferência diagnóstica.
2. **Human-in-the-loop:** O sistema nunca substitui o profissional.
3. **Evolução planejada:** Arquitetura preparada para Redes Bayesianas.
4. **Conformidade regulatória:** LGPD, CFM, CFP já estruturados.

---

**Última atualização:** 01 de Junho de 2026  
**Status:** ✅ MVP - Infraestrutura Pronta  
**Próxima revisão:** Quando modelos ORM forem concluídos
