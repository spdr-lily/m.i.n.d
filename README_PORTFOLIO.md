# M.I.N.D — Sistema de Apoio à Decisão Clínica em Saúde Mental

> **Mental Intelligence & Network Data** — Um CDSS (Clinical Decision Support System) que combina inferência bayesiana, regras do DSM-5-TR e aprendizado de máquina para auxiliar no diagnóstico psiquiátrico.

---

## O Problema Real

O diagnóstico psiquiátrico é inerentemente probabilístico. Não há exame de sangue para depressão ou ansiedade — o diagnóstico depende de sintomas relatados, duração, exclusão de condições similares e julgamento clínico sobre comorbidades. Três problemas concretos:

1. **Erro diagnóstico** — Transtorno Bipolar é diagnosticado como depressão unipolar em ~40% dos casos na primeira consulta (Angst et al., 2011), porque o paciente busca ajuda durante episódios depressivos, não maníacos.
2. **Sobrecarga cognitiva** — O DSM-5-TR contém critérios para ~192 transtornos. Um clínico precisa memorizar combinações de sintomas, durações mínimas, exclusões e diferenciais.
3. **Subjetividade da escala isolada** — Uma escala (PHQ-9, GAD-7) sozinha não captura a interseção entre sintomas, critérios temporais e exclusões diferenciais.

Este projeto **não tenta substituir o psiquiatra**. Ele estrutura o raciocínio diagnóstico em um motor formal e auditável, permitindo que o clínico revise, aceite ou rejeite cada hipótese — sempre com `requires_human_review = True`.

---

## O Que Este Projeto Demonstra Sobre Mim Como Engenheira

| Habilidade | Evidência no Projeto |
|---|---|
| **Arquitetura de sistemas complexos** | Integração de 6 subsistemas (inferência, escalas, ML, DW, auditoria, segurança) em um container único com comunicação bem definida entre camadas. |
| **Tomada de decisão técnica com trade-offs explícitos** | Cada decisão não-óbvia neste documento inclui a alternativa rejeitada e o porquê. |
| **Código defensivo e resiliência** | 3 camadas de validação clínica (Pydantic → Service → DB), human-in-the-loop como padrão, rate limiting, CSP, HSTS. |
| **ML pipeline completo** | Do treino ao deploy: 12 modelos com MLflow tracking, DVC versioning, split temporal, critique explícita das próprias limitações. |
| **Privacidade e compliance por design** | LGPD embedada na arquitetura (separação PII/clínico, criptografia Fernet AES, pseudonimização, consentimento, retenção). |
| **548 testes** | Unitários + integração com cobertura. |
| **Documentação que um clínico entende** | Manual clínico em pt-BR (`CLINICAL_MANUAL.md`) explicando fundamentos do CDSS sem jargão de engenharia. |

---

## Decisões Técnicas Não-Óbvias (e Por Quê)

### 1. Inferência híbrida: regras → bayes → escalas → ML, nessa ordem

A maioria dos CDSS usa uma única abordagem (árvore de decisão, rede neural pura, ou regras). Este projeto usa **quatro camadas encadeadas**, cada uma tratando o ponto cego da anterior:

| Camada | O que faz | O que cobre |
|---|---|---|
| **Critérios DSM-5-TR** (rule engine) | Gatekeeper: contagem mínima de sintomas, duração, satisfação de grupos | Se falha, `prob *= 0.3` — nenhuma probabilidade alta passa sem os critérios formais |
| **Naive Bayes epidemiológico** | Priors do NCS-R (Kessler et al., 2005), CPTs da literatura, atualização sequencial por sintoma | ~70% do sinal — modela incerteza inerente ao diagnóstico |
| **Ajuste por escalas** (threshold match) | Mapeia scores de PHQ-9, GAD-7, etc. para boost via `SCALE_DISORDER_MAP` | Adiciona `0.08 + (score - threshold) / 100` — evidencia objetiva de instrumentos validados |
| **ML blending** (RF/XGBoost) | Predição de risco baseada em escalas | Peso 0.15 — sinal complementar, minoritário por design |

**Por quê**: O paciente pode minimizar sintomas (escala subestima), o clínico pode perder um diferencial (regra falha), o modelo ML pode viciar em dados sintéticos. Quatro fontes de evidência independentes com pesos calibrados reduzem o risco de qualquer ponto cego isolado dominar a decisão.

### 2. Bayesian network com priors epidemiológicos (NCS-R), não uniformes

Muitos sistemas assumem `P(disorder) = 1/N`. Este projeto usa prevalências do **National Comorbidity Survey Replication** (Kessler et al., 2005): ansiedade social 7.0%, depressão maior 5.2%, TAG 3.1%. A diferença entre `1/19 ≈ 5.3%` e 5.2% para depressão parece pequena, mas o impacto cumulativo no posterior com múltiplos sintomas é significativo.

**Por quê**: Priors uniformes penalizam transtornos comuns e superestimam raros. Um prior calibrado faz o sistema ser conservador onde deve ser (diagnóstico raro exige mais evidência para superar o prior baixo). As probabilidades condicionais `P(sintoma | transtorno)` vêm de Andrews et al. (2018) e as correlações de comorbidade de Kessler et al. (2005, 2015). A implementação atual usa dados populacionais dos EUA (NCS-R). Priors brasileiros (São Paulo Megacity Survey) são uma evolução planejada, não implementada.

### 3. Separação de identidade clínica — não é schema, é arquitetura de privacidade

O paciente não tem "nome" no banco clínico. `PatientIdentity` (nome criptografado com **Fernet AES**) e `PatientProfile` (dados clínicos) são tabelas separadas. O UUID atravessa o sistema — consultas, escalas, inferências — sem expor o nome real.

```python
# app/services/patient_service.py (simplificado)
identity = PatientIdentity(full_name=encrypt_pii(data.name))
profile = PatientProfile(birth_date=data.birth_date, sex=data.sex, ...)
# Nome verdadeiro só existe encryptado no DB; decriptado no response
```

**Por quê**: A LGPD (Lei 13.709/2018) classifica dados de saúde como **sensíveis**. Um vazamento da tabela de consultas não revela identidade de pacientes. A separação física permite retenção configurável (5 anos) e anonimização para pesquisa sem afetar o dado clínico. A alternativa rejeitada foi criptografia de coluna única — vulnerável a vazamento de chave + tabela inteira.

### 4. Human-in-the-loop por design, não por conveniência

`requires_human_review: bool = True` é o padrão. Sempre. O sistema gera hipóteses ranqueadas com **intervalo de confiança de Wilson**, exclusões automáticas entre transtornos mutuamente exclusivos (se dois têm prob ≥ 0.3, o menor é excluído com justificativa), e um trace step-by-step de como cada sintoma alterou a probabilidade.

**Por quê**: Falso positivo em CDSS psiquiátrico = tratamento incorreto por meses. "Default-to-review" não é feature — é requisito ético e regulatório (RDC 657/2022, ANVISA). A alternativa rejeitada foi "majority vote" automático entre os pipelines.

### 5. Três camadas de validação clínica — defesa em profundidade

```python
# Layer 1: Schema → Pydantic rejeita entrada inválida antes de qualquer lógica
@field_validator("birth_date")
def check_birth_date(cls, v):
    if v > date.today(): raise ValueError("Data de nascimento no futuro")

# Layer 2: Service → regras de negócio (15+ métodos)
class ClinicalIntegrityService:
    def validate_patient_profile(self, profile):
        if age(profile.birth_date) > MAX_AGE_YEARS: raise ...

# Layer 3: DB → CHECK constraints (7 constraints) como barreira final
# ck_symptom_observation_intensity: CHECK (intensity >= 0 AND <= 10)
# ck_inference_probability: CHECK (probability >= 0 AND <= 1)
```

**Por quê**: Bugs acontecem em todas as camadas. Se o validador Pydantic falhar (campo opcional mal tipado), o IntegrityService pega. Se o service pular (novo endpoint que esqueceu de chamar validação), o banco rejeita. Crítico em saúde mental, onde escalas têm ranges fixos (PHQ-9: 0–27, MADRS: 0–60) e extrapolações silenciosas invalidariam a interpretação clínica. Inspirado no padrão de defesa em profundidade de segurança da informação, aplicado à integridade de dados clínicos.

### 6. SCALE_DISORDER_MAP: matching textual em português em vez de FK rígida

```python
SCALE_DISORDER_MAP = {
    "PHQ-9": [(25, ["Depressivo", "Depressão"]),
              (15, ["Depressivo", "Depressão", "Distimia"])],
    "MDQ":  [(7,  ["Bipolar"])],
    "GAD-7":[(10, ["Ansiedade", "Pânico", "TAG", "Ansiedade Social"])],
}
```

Em vez de chave estrangeira entre `Scale` e `Disorder`, um dicionário de `(threshold, keywords)` faz boost quando o score ≥ threshold **e** o nome do transtorno contém as keywords em português.

**Por quê**: O DSM-5-TR evoluiu em 2022; a CID-11 adicionou transtornos (Transtorno por Jogo Eletrônico). Adicionar um transtorno novo não exige migração de schema. Um clínico pode manter o dicionário sem engenheiro. A alternativa (tabela de mapeamento com FK) foi rejeitada por rigidez — cada novo transtorno exigiria migração + deploy.

---

## Machine Learning Pipeline

### 12 Modelos — Resultados (Avaliação Temporal, 2026-06-22)

Métricas obtidas via `notebooks/model_evaluation.ipynb` com split temporal (80% train / 20% test por data de consulta, 219 consultas, 53 features). Modelos registrados no MLflow (sqlite:///mlflow.db) e promovidos para Production no Model Registry do PostgreSQL.

| Objetivo | Algoritmo | Acurácia | F1 (macro) | AUC-ROC |
|---|---|---|---|---|
| **Diagnóstico** | XGBoost | 1.000 | 1.000 | — |
| | Random Forest | 1.000 | 1.000 | — |
| | Logistic Reg. | — | — | —¹ |
| **Suicídio** (binário) | XGBoost | 0.952 | 0.923 | 0.997 |
| | Random Forest | 0.976 | 0.963 | 0.995 |
| | Logistic Reg. | 0.952 | 0.933 | 0.985 |
| **Recaída** (binário) | Logistic Reg. | 0.714 | 0.625 | 0.739 |
| | Random Forest | 0.571 | 0.357 | 0.658 |
| | XGBoost | 0.619 | 0.529 | 0.683 |
| **Resposta Terapêutica** (binário) | Logistic Reg. | 0.619 | 0.273 | 0.915 |
| | Random Forest | 0.738 | 0.000² | 0.709 |
| | XGBoost | 0.881 | 0.000² | 0.547 |

¹ Logistic Regression para diagnóstico foi pulada — o modelo registrado (batch 20260606) usou split aleatório, então o LabelEncoder não reconhece classes do split temporal.
² RF e XGB preveem apenas classe majoritária (39/42 casos = classe 0); LR tenta capturar minoria com recall=1.0 mas precision=0.16.

### O que os números realmente significam (e o que não significam)

- **Diagnóstico com acurácia 1.0** é esperado e **suspeito**: o gerador de dados sintéticos produz relações determinísticas entre sintomas e diagnóstico. Em dados reais, isso seria impossível — aí está exatamente o ponto de usar dados sintéticos para pipeline, não para conclusões clínicas.
- **Suicídio com AUC ≥ 0.98** reflete a heurística do gerador (certa combinação de escalas → risco alto), não detecção real de ideação suicida.
- **Recaída é o problema mais difícil** — todos os modelos perto do acaso (AUC 0.67–0.75), o que é consistente com a literatura (predizer recaída em saúde mental é notoriamente difícil mesmo com dados reais).
- **Logistic Regression em resposta terapêutica (AUC 0.408)** está pior que aleatório — possivelmente overfitting negativo ou features mal especificadas para essa tarefa.

### Limitações Explícitas (obrigatório ler antes de interpretar)

1. **Apenas dados sintéticos** — Distribuições e correlações refletem o gerador heurístico, não a clínica real.
2. **Desequilíbrio artificial** — Prevalências são arbitrárias, não epidemiológicas.
3. **Split temporal menos significativo** — Dados gerados em lote, sem progressão real de doença.
4. **Calibração enganosa** — Sem ruído clínico real, curvas de calibração podem ser artificialmente perfeitas.
5. **Hiperparâmetros para demonstração** — Não otimizados clinicamente.
6. **Generalização zero** — Modelos não servem para população real sem retreinamento.

### Pré-requisitos para Uso Clínico Real

Retreinamento em dados reais → estudo prospectivo com SCID-5-CV (padrão ouro) → comitê de ética → registro ANVISA (RDC 657/2022).

---

## Arquitetura em 30 Segundos

```
┌──────────────┐     ┌─────────────────────────────────────────┐
│  React SPA   │◄───►│  FastAPI                                │
│  (Ant Design)│     │  ├─ Auth (JWT + RBAC, 7 roles)          │
│  + Recharts  │     │  ├─ Patient (identidade encryptada)     │
│              │     │  ├─ Consultation (decrypt on response)   │
│  /login      │     │  ├─ Inference (dual pipeline)            │
│  /dashboard  │     │  │   ├─ Rules (DSM-5-TR criteria)       │
│  /patients   │     │  │   ├─ Naive Bayes (priors Brasil)     │
│  /consultas  │     │  │   ├─ Scale boost (threshold match)   │
│  /inferences │     │  │   └─ ML blend (0.15 weight)          │
│  /mia        │     │  ├─ Scales (21, scoring + interpretação) │
│  /personality│     │  ├─ ML (12 modelos, MLflow tracking)     │
│  /admin/*    │     │  ├─ Analytics (DW star schema, 11 views) │
│              │     │  ├─ Auditoria (middleware, entity-level) │
│              │     │  └─ Chatbot MIA (regras + busca textual) │
│              │     │                                          │
│              │     ├── PostgreSQL 16 (clinical, diagnostic,   │
│              │     │     dw schemas) + 12 migrations Alembic  │
│              │     ├── Redis (cache — sessão, filas, MLflow)  │
│              │     ├── Airflow (4 DAGs: treino, etl, backup,  │
│              │     │     monitoria)                           │
│              │     └── PySpark 3.5 (batch inference, métricas │
│              │           populacionais, importação CSV)       │
└──────────────┘     └─────────────────────────────────────────┘
```

---

## Como Explorar o Código

| O que procurar | Caminho |
|---|---|
| Motor de inferência dupla (regras + bayes) | [`app/ml/inference/`](./app/ml/inference/) |
| 21 escalas psicométricas + SCALE_DISORDER_MAP | [`app/ml/models/assessment_scales.py`](./app/ml/models/assessment_scales.py) |
| LGPD: separação de identidade, criptografia, consentimento | [`app/security/lgpd.py`](./app/security/lgpd.py) |
| Validação clínica em 3 camadas | [`app/services/integrity_service.py`](./app/services/integrity_service.py) |
| Pipeline ML: treino, registro, predição | [`app/ml/training/`](./app/ml/training/) |
| Personalidade: fatores BFP (Big Five) + Dark Triad | [`app/ml/predictors/personality_factors.py`](./app/ml/predictors/personality_factors.py) |
| Chatbot diagnóstico MIA | [`app/services/chatbot_service.py`](./app/services/chatbot_service.py) |
| ETL para Data Warehouse (star schema) | [`app/etl/dw_loader.py`](./app/etl/dw_loader.py) |
| Notebook de avaliação dos 12 modelos | [`notebooks/model_evaluation.ipynb`](./notebooks/model_evaluation.ipynb) |
| Manual clínico completo (pt-BR) | [`CLINICAL_MANUAL.md`](./CLINICAL_MANUAL.md) |
| 548 testes | [`tests/`](./tests/) |

---

## Stack Resumida

| Categoria | Tecnologias |
|---|---|
| Backend | Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Frontend | React 18, TypeScript, Vite 5, Ant Design 5, Recharts, Zustand |
| ML/MLOps | scikit-learn, XGBoost, MLflow, DVC |
| Infra | PostgreSQL 16, Redis, Docker Compose, Apache Airflow, PySpark |
| Segurança | JWT, RBAC, Fernet AES (LGPD), CSP, HSTS, Rate Limit (100 req/min), Bandit zero |
| Qualidade | 548 testes, flake8, black, mypy, pre-commit, GitHub Actions, codecov |

---

## Licença

MIT
