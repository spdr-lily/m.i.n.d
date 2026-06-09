# Manual Clínico — M.I.N.D CDSS

## 1. Visão Geral

M.I.N.D (Mental Intelligence & Network Data) é um Sistema de Suporte à Decisão Clínica (CDSS) para diagnóstico em saúde mental. Opera com dois motores de inferência complementares:

| Motor | Endpoint | Base |
|---|---|---|
| Critérios Diagnósticos | `POST /api/v1/inferences/run` | DSM-5-TR (contagem de sintomas + regras de exclusão/comorbidade) |
| Bayesiano | `POST /api/v1/inferences/bayesian` | Redes Bayesianas (Naive Bayes) com priors epidemiológicos |

Ambos são **suporte à decisão** — o diagnóstico final é sempre do clínico responsável (human-in-the-loop).

### Autoridades de Classificação

| Autoridade | Código | Website |
|---|---|---|
| World Health Organization (WHO) | CID-11 | https://icd.who.int |
| American Psychiatric Association (APA) | DSM-5-TR | https://www.psychiatry.org |

---

## 2. Motor de Critérios Diagnósticos

### 2.1 Funcionamento

O `CriteriaEvaluator` implementa a lógica DSM-5-TR:

1. Para cada transtorno, avalia cada critério (sintoma) como **presente/ausente**
2. Verifica **critérios obrigatórios** (ex.: TDM precisa de `depressed_mood` OU `loss_of_interest`)
3. Verifica **duração mínima** (ex.: ≥2 semanas para TDM, ≥1 semana para mania)
4. Calcula `probability = met_criteria / total_criteria`
5. Penaliza se critérios obrigatórios não preenchidos (×0.3) ou duração insuficiente (×0.5)
6. Aplica **regras de exclusão** (ex.: não diagnosticar TDM durante episódio maníaco)
7. Aplica **pesos de comorbidade** (ex.: TAG + TDM têm boost de probabilidade)

### 2.2 Os 19 Transtornos Suportados

| # | Transtorno (pt-BR) | CID-11 | DSM-5-TR | Critérios-chave | Duração mínima |
|---|---|---|---|---|---|
| 1 | Transtorno Depressivo Maior | 6A70 | 296.22 | ≥5 de 9 sintomas, obrigatório humor deprimido ou anedonia | ≥2 semanas |
| 2 | Transtorno Ansiedade Generalizada | 6B00 | 300.02 | Preocupação excessiva + ≥3 sintomas | ≥6 meses |
| 3 | Transtorno de Pânico | 6B01 | 300.01 | Ataques de pânico recorrentes e inesperados | — |
| 4 | Transtorno de Estresse Pós-Traumático | 6B40 | 309.81 | Exposição traumática + intrusão + evitação + alterações | ≥1 mês |
| 5 | Transtorno Depressivo Persistente (Distimia) | 6A71 | 300.4 | Humor deprimido crônico + ≥2 sintomas | ≥2 anos |
| 6 | Transtorno de Ansiedade Social | 6B04 | 300.23 | Medo de situações sociais | ≥6 meses |
| 7 | Transtorno Bipolar Tipo I | 6A60 | 296.41 | Episódio maníaco (humor elevado + ≥3 sintomas) | ≥1 semana |
| 8 | Transtorno Bipolar Tipo II | 6A61 | 296.89 | Hipomania + episódios depressivos | ≥4 dias (hipomania) |
| 9 | Transtorno Obsessivo-Compulsivo | 6B20 | 300.3 | Obsessões e/ou compulsões | ≥1 hora/dia |
| 10 | Agorafobia | 6B02 | 300.22 | Medo de espaços abertos/aglomerações | ≥6 meses |
| 11 | Transtorno por Uso de Substâncias | 6C40 | 305.00 | Padrão problemático de uso | ≥12 meses |
| 12 | Anorexia Nervosa | 6B80 | 307.1 | Restrição alimentar + medo de ganho de peso | — |
| 13 | Bulimia Nervosa | 6B81 | 307.51 | Compulsão + purgação | ≥3 meses |
| 14 | Transtorno de Compulsão Alimentar | 6B82 | 307.59 | Episódios de compulsão sem purgação | ≥3 meses |
| 15 | Transtorno de Insônia | 7A00 | 307.42 | Dificuldade de iniciar/manter o sono | ≥3 meses |
| 16 | Esquizofrenia / Transtorno Psicótico | 6A20 | 295.90 | Delírios + alucinações + discurso desorganizado | ≥1 mês |
| 17 | Transtorno de Sintomas Somáticos | 6C20 | 300.82 | Sintomas físicos angustiantes sem causa médica | ≥6 meses |
| 18 | Transtorno do Espectro Autista (TEA) | 6A02 | 299.00 | Déficits na comunicação + comportamentos repetitivos | — |
| 19 | Transtorno de Déficit de Atenção/Hiperatividade (TDAH) | 6A05 | 314.01 | Desatenção + hiperatividade/impulsividade | ≥6 meses |

### 2.3 Exemplo de Uso

```json
POST /api/v1/inferences/run
{
  "observations": [
    {"symptom_id": 1, "present": true, "duration_days": 30},
    {"symptom_id": 2, "present": true, "duration_days": 30},
    {"symptom_id": 3, "present": true, "duration_days": 20},
    {"symptom_id": 5, "present": true, "duration_days": 25},
    {"symptom_id": 6, "present": true, "duration_days": 15},
    {"symptom_id": 7, "present": true, "duration_days": 30}
  ]
}
```

Resposta inclui:
- `probability` (0-1) — proporção de critérios preenchidos
- `confidence_level` — média entre probability e proportion
- `required_met` — critérios obrigatórios satisfeitos
- `excluded` / `exclusion_reason` — se foi excluído por regra
- `requires_human_review` — sempre `true` (LGPD/GDPR)

---

## 3. Motor Bayesiano

### 3.1 Arquitetura

Rede Naive Bayes com 19 nós de transtorno e 54 nós de sintoma:

```
[Transtorno] → Sintoma1
             → Sintoma2
             → Sintoma3
             ...
```

Cada aresta tem uma **CPT** (Conditional Probability Table):
- `P(Sintoma | Transtorno presente)` — probabilidade do sintoma dado o transtorno
- `P(Sintoma | Transtorno ausente)` — taxa base populacional

### 3.2 Priors Epidemiológicos

Fontes: Kessler et al. (2005) NCS-R, WHO World Mental Health Surveys

| Transtorno | Prevalência (prior) |
|---|---|
| Transtorno de Ansiedade Social | 7.0% |
| Transtorno Depressivo Maior | 5.2% |
| TEPT | 3.7% |
| Transtorno de Ansiedade Generalizada | 3.1% |
| Transtorno de Pânico | 2.2% |
| Transtorno Depressivo Persistente | 2.0% |
| TOC | 1.2% |
| Transtorno Bipolar Tipo I | 1.0% |
| Transtorno Bipolar Tipo II | 0.3% |

### 3.3 Exemplo de Uso

```json
POST /api/v1/inferences/bayesian
{
  "evidence": [
    {"symptom_name": "depressed_mood", "present": true},
    {"symptom_name": "loss_of_interest", "present": true},
    {"symptom_name": "fatigue", "present": true},
    {"symptom_name": "sleep_disturbance", "present": true},
    {"symptom_name": "guilt_feelings", "present": true},
    {"symptom_name": "euphoric_mood", "present": false}
  ],
  "top_k": 3
}
```

### 3.4 Interpretação dos Resultados

```json
[
  {
    "disorder_name": "Transtorno Depressivo Maior",
    "prior_probability": 0.0520,
    "posterior_probability": 0.7832,
    "bayes_factor": 68.45,
    "odds_ratio": 3.76
  }
]
```

| Campo | Significado | Uso Clínico |
|---|---|---|
| `prior_probability` | Prevalência populacional | Linha de base antes dos sintomas |
| `posterior_probability` | Probabilidade após evidências | Principal métrica diagnóstica |
| `bayes_factor` | Quanto a evidência favorece o diagnóstico | >10 = evidência forte, >30 = muito forte |
| `odds_ratio` | Chance do diagnóstico vs. não diagnóstico | Razão de chances |

### 3.5 Faixas de Interpretação

| Posterior | Interpretação |
|---|---|
| ≥ 0.80 | Alta probabilidade clínica — fortemente sugestivo |
| ≥ 0.50 | Probabilidade moderada — considerar diagnóstico diferencial |
| ≥ 0.20 | Baixa probabilidade — improvável, mas não excluído |
| < 0.20 | Muito baixa — diagnóstico improvável |

---

## 4. Escalas de Avaliação

### 4.1 As 10 Escalas Implementadas

| Escala | Endpoint | Itens | Pontuação | Interpretação |
|---|---|---|---|---|
| PHQ-9 | `POST /api/v1/assessments/score` | 9 (0-3) | 0-27 | 0-4: mínimo, 5-9: leve, 10-14: moderado, 15-19: moderado-grave, 20-27: grave |
| GAD-7 | `POST /api/v1/assessments/score` | 7 (0-3) | 0-21 | 0-4: mínimo, 5-9: leve, 10-14: moderado, 15-21: grave |
| MADRS | `POST /api/v1/assessments/score` | 10 (0-6) | 0-60 | 0-6: ausente, 7-19: leve, 20-34: moderado, 35-60: grave |
| MDQ | `POST /api/v1/assessments/score` | 13 (sim/não) | 0-13 | ≥7 = screening positivo para bipolaridade |
| PCL-5 | `POST /api/v1/assessments/score` | 20 (0-4) | 0-80 | ≥31-33 = provável TEPT |
| Y-BOCS | `POST /api/v1/assessments/score` | 10 (0-4) | 0-40 | 0-7: subclínico, 8-15: leve, 16-23: moderado, 24-31: grave, 32-40: extremo |
| AUDIT | `POST /api/v1/assessments/score` | 10 (0-4) | 0-40 | 0-7: baixo risco, 8-15: uso de risco, 16-19: uso nocivo, ≥20: provável dependência |
| ASRM | `POST /api/v1/assessments/score` | 5 (0-4) | 0-20 | ≥6 = possível episódio maníaco/hipomaníaco |
| ASRS | `POST /api/v1/assessments/score` | 18 (0-4) | 0-72 | Parte A ≥4 = screening positivo para TDAH |
| AQ-10 | `POST /api/v1/assessments/score` | 10 (1-4) | 10-40 | ≥6 = screening positivo para TEA |

### 4.2 Exemplo

```json
POST /api/v1/assessments/score
{
  "scale_name": "PHQ-9",
  "responses": [2, 3, 1, 2, 0, 2, 1, 0, 0]
}
```

Resposta:
```json
{
  "scale_name": "PHQ-9",
  "total_score": 11.0,
  "severity": "Moderate",
  "interpretation": "Moderate depressive symptoms. Recommend further evaluation and possible treatment.",
  "max_score": 27
}
```

### 4.3 Histórico do Paciente

`GET /api/v1/assessments/patient/{patient_uuid}/history`

Retorna todos os scores do paciente agregados por consulta, com data, escala e cor por gravidade.

---

## 5. Mapeamento DSM-5-TR ↔ ICD-11

### 5.1 Endpoint

`GET /api/map?code=F32.1`

Retorna o mapeamento bidirecional entre códigos DSM-5-TR e CID-11 para todos os 19 transtornos, incluindo exclusões e diagnósticos diferenciais.

### 5.2 Cobertura

29+ mapeamentos cobrindo todos os 19 transtornos com:
- Critérios diagnósticos completos do DSM-5-TR
- Exclusões CID-11 e DSM-5-TR
- Diagnósticos diferenciais CID-11 e DSM-5-TR
- Relações de comorbidade

---

## 6. Alertas Clínicos

Endpoint: `GET /api/v1/alerts/check-all`

Quatro categorias de alerta:

| Alerta | Descrição | Trigger |
|---|---|---|
| Scale Threshold | Pontuação acima do limiar clínico | PHQ-9 ≥ 15, GAD-7 ≥ 10, MADRS ≥ 20 |
| Suicidal Ideation | Ideação suicida em avaliações | Item 9 do PHQ-9 > 0 |
| Missed Follow-up | Paciente sem consulta há ≥30 dias | Última consulta > 30 dias |
| High Confidence Deterioration | Piora com alta confiança diagnóstica | Probabilidade bayesiana ≥ 0.8 |

---

## 7. Métricas e Dashboards

Endpoint: `GET /api/v1/metrics/*`

| Endpoint | Retorna |
|---|---|
| `/api/v1/metrics/overview` | Total de pacientes, consultas, diagnósticos, avaliações |
| `/api/v1/metrics/scales/{name}/trends` | Tendência temporal de uma escala |
| `/api/v1/metrics/correlations` | Correlações entre escalas |

---

## 8. Validação de Integridade Clínica

Sistema de 3 camadas:

| Camada | Local | Função |
|---|---|---|
| 1. Pydantic | Schemas (`patient_profile.py`, `consultation.py`) | Validadores de campo (birth_date future reject, intensity 0-10, frequency enum, duration_days ≥ 1) |
| 2. Business Logic | `ClinicalIntegrityService` | Valida pacientes (birth_date, age ≤ 120), consultas (date not future, min age 3), sintomas (intensity 0-10, duration ≥ 1), escalas (value 0-10), inferências (probability/confidence 0-1, sum ≤ 1.0) |
| 3. DB Constraints | 7 CHECK constraints (Alembic `c1d2e3f4a5b6`) | `birth_date ≤ today`, `intensity 0-10`, `duration_days ≥ 1`, frequency enum, `response_value 0-10`, `probability/confidence 0-1` |

Relatório de qualidade: `python scripts/check_integrity.py` → `data/reports/clinical_integrity_report.json`

---

## 9. Segurança e Auditoria

### 9.1 Controle de Acesso

| Role | Permissões |
|---|---|
| `admin` | CRUD total + gerenciamento de usuários + auditoria |
| `clinician` | CRUD em pacientes, episódios, inferências; sem deletar |
| `viewer` | Leitura apenas |

### 9.2 Middleware de Segurança

- **CSP** (Content-Security-Policy) — restringe fontes de conteúdo
- **HSTS** — Strict-Transport-Security com max-age=31536000
- **Rate Limit** — 100 requisições/minuto por IP
- **SQL Injection Protection** — bloqueio de padrões suspeitos em query params
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **Referrer-Policy**: strict-origin-when-cross-origin

### 9.3 Auditoria

Todas as operações em registros clínicos são logadas com:
- `entity_name`, `entity_id`, `operation_type` (READ/CREATE/UPDATE/DELETE)
- `performed_by` (UUID do profissional)
- `old_data`, `new_data` (snapshot completo)
- `ip_address`, `user_agent`
- `created_at` (timestamp)

Acesso: `GET /api/v1/audit/logs` (apenas admin)

### 9.4 Privacidade (LGPD/GDPR)

- Pacientes identificados por UUID (não por dados pessoais)
- Dados de identidade armazenados separadamente dos perfis clínicos
- CPF e email pseudonimizados via SHA-256
- Criptografia Fernet AES para campos sensíveis
- Registro de consentimento do paciente (`/api/v1/consent/`)
- Human-in-the-loop: nenhum diagnóstico automático sem validação clínica

---

## 10. Guia de Interpretação Clínica

### 10.1 Quando usar cada motor

| Situação | Motor Recomendado |
|---|---|
| Suspeita de transtorno específico, sintomas bem definidos | Critérios (`/api/v1/inferences/run`) |
| Diagnóstico diferencial entre múltiplos transtornos | Bayesiano (`/api/v1/inferences/bayesian`) |
| Paciente com sintomas atípicos ou sobrepostos | Ambos, comparar resultados |
| Reavaliação longitudinal (monitorar resposta ao tratamento) | Escalas (`/api/v1/assessments/score`) |
| Suspeita de ideação suicida | Escalas + Alerta de ideação |

### 10.2 Limitações Conhecidas

- Os **priors bayesianos** são baseados em população geral dos EUA (NCS-R) — podem não refletir a prevalência local
- O **criteria evaluator** não pondera gravidade dos sintomas — apenas presença/ausência
- Não há diferenciação entre **primeiro episódio** e **recorrência**
- Comorbidades são modeladas como boost simples — não como redes Bayesianas completas com dependências entre transtornos
- Crianças e adolescentes podem apresentar sintomatologia diferente (não validado para <18 anos)

---

## 11. Pipeline de Machine Learning

4 objetivos × 3 algoritmos = 12 modelos treinados e registrados no MLflow:

| Objetivo | LR | RF | XGB |
|---|---|---|---|
| Diagnóstico | ✓ | ✓ | ✓ |
| Predição de Recaída | ✓ | ✓ | ✓ |
| Risco de Suicídio | ✓ | ✓ | ✓ |
| Resposta Terapêutica | ✓ | ✓ | ✓ |

Todos promovidos para Production no MLflow Model Registry.

---

## 12. Data Warehouse (Star Schema)

Tabelas do DW (`dw_loader.py`):
- `dim_disorder` — 19 transtornos
- `dim_patient` — Pacientes
- `dim_date` — Datas
- `fact_diagnosis` — Diagnósticos
- `fact_symptom` — Sintomas
- `fact_consultation` — Consultas
- `fact_scale_response` — Respostas de escalas

ETL: `python -c "from app.etl.dw_loader import run_full_etl; run_full_etl()"`

---

## 13. Referências

1. American Psychiatric Association. (2022). *Diagnostic and Statistical Manual of Mental Disorders* (5th ed., text rev.).
2. World Health Organization. (2019). *ICD-11: International Classification of Diseases* (11th ed.).
3. Kessler, R. C., et al. (2005). *Lifetime prevalence and age-of-onset distributions of DSM-IV disorders in the NCS-R.* Archives of General Psychiatry.
4. Kroenke, K., et al. (2001). *The PHQ-9: validity of a brief depression severity measure.* Journal of General Internal Medicine.
5. Spitzer, R. L., et al. (2006). *A brief measure for assessing generalized anxiety disorder: the GAD-7.* Archives of Internal Medicine.
6. Montgomery, S. A., & Åsberg, M. (1979). *A new depression scale designed to be sensitive to change.* British Journal of Psychiatry.
7. Lei Geral de Proteção de Dados (LGPD) — Lei nº 13.709/2018.
8. General Data Protection Regulation (GDPR) — Regulation (EU) 2016/679.
