# Manual Clínico — M.I.N.D CDSS

## 1. Visão Geral

M.I.N.D (Mental Intelligence & Network Data) é um Sistema de Suporte à Decisão Clínica (CDSS) para diagnóstico em saúde mental. Opera com dois motores de inferência complementares:

| Motor | Endpoint | Base |
|---|---|---|
| Critérios Diagnósticos | `POST /api/inferences/run` | DSM-5-TR (contagem de sintomas + regras de exclusão/comorbidade) |
| Bayesiano | `POST /api/inferences/bayesian` | Redes Bayesianas (Naive Bayes) com priors epidemiológicos |

Ambos são **suporte à decisão** — o diagnóstico final é sempre do clínico responsável (human-in-the-loop).

---

## 2. Motor de Critérios Diagnósticos

### 2.1 Funcionamento

O `CriteriaEvaluator` implementa a lógica DSM-5-TR:

1. Para cada transtorno, avalia cada critério (sintoma) como **presente/ausente**
2. Verifica **critérios obrigatórios** (ex.: MDD precisa de `depressed_mood` OU `loss_of_interest`)
3. Verifica **duração mínima** (ex.: ≥2 semanas para MDD, ≥1 semana para mania)
4. Calcula `probability = met_criteria / total_criteria`
5. Penaliza se critérios obrigatórios não preenchidos (×0.3) ou duração insuficiente (×0.5)
6. Aplica **regras de exclusão** (ex.: não diagnosticar MDD durante episódio maníaco)
7. Aplica **pesos de comorbidade** (ex.: GAD + MDD têm boost de probabilidade)

### 2.2 Transtornos Suportados

| Transtorno | Critérios-chave | Duração mínima |
|---|---|---|
| MDD (F32/F33) | ≥5 de 9 sintomas, obrigatório humor deprimido ou anedonia | ≥2 semanas |
| Bipolar I (F31) | Episódio maníaco (humor elevado + ≥3 sintomas) | ≥1 semana |
| Bipolar II (F31.81) | Hipomania + episódios depressivos | ≥4 dias (hipomania) |
| GAD (F41.1) | Preocupação excessiva + ≥3 sintomas | ≥6 meses |
| Panico (F41.0) | Ataques de pânico recorrentes e inesperados | — |
| PTSD (F43.10) | Exposição traumática + intrusão + evitação + alterações | ≥1 mês |
| Distimia (F34.1) | Humor deprimido crônico + ≥2 sintomas | ≥2 anos |
| Fobia Social (F40.10) | Medo de situações sociais | ≥6 meses |
| TOC (F42) | Obsessões e/ou compulsões | ≥1 hora/dia |

### 2.3 Exemplo de Uso

```json
POST /api/inferences/run
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

Rede Naive Bayes com 9 nós de transtorno e 54 nós de sintoma:

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
| Social Anxiety Disorder | 7.0% |
| Major Depressive Disorder | 5.2% |
| PTSD | 3.7% |
| GAD | 3.1% |
| Panic Disorder | 2.2% |
| Persistent Depressive Disorder | 2.0% |
| OCD | 1.2% |
| Bipolar I Disorder | 1.0% |
| Bipolar II Disorder | 0.3% |

### 3.3 Exemplo de Uso

```json
POST /api/inferences/bayesian
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
    "disorder_name": "Major Depressive Disorder",
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

### 3.5 Explicação por Transtorno

```json
GET /api/inferences/bayesian-explanation?disorder=Major Depressive Disorder&symptoms=depressed_mood:true,loss_of_interest:true,fatigue:true
```

Retorna:
- `prior` / `posterior`
- `bayes_factor`
- `symptom_contributions` — lista de sintomas ordenada por impacto na probabilidade
- `interpretation` — texto legível: "High clinical probability — strongly suggestive of diagnosis"

Faixas de interpretação:
| Posterior | Interpretação |
|---|---|
| ≥ 0.80 | Alta probabilidade clínica — fortemente sugestivo |
| ≥ 0.50 | Probabilidade moderada — considerar diagnóstico diferencial |
| ≥ 0.20 | Baixa probabilidade — improvável, mas não excluído |
| < 0.20 | Muito baixa — diagnóstico improvável |

---

## 4. Escalas de Avaliação

### 4.1 Escalas Implementadas

| Escala | Endpoint | Itens | Pontuação | Interpretação |
|---|---|---|---|---|
| PHQ-9 | `POST /api/assessments/score` | 9 (0-3) | 0-27 | 0-4: mínimo, 5-9: leve, 10-14: moderado, 15-19: moderado-grave, 20-27: grave |
| GAD-7 | `POST /api/assessments/score` | 7 (0-3) | 0-21 | 0-4: mínimo, 5-9: leve, 10-14: moderado, 15-21: grave |
| MADRS | `POST /api/assessments/score` | 10 (0-6) | 0-60 | 0-6: ausente, 7-19: leve, 20-34: moderado, 35-60: grave |

### 4.2 Exemplo

```json
POST /api/assessments/score
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

---

## 5. Mapeamento DSM-5-TR ↔ ICD-11

### 5.1 Endpoint

`GET /api/symptoms/map?code=F32.1`

Retorna o mapeamento bidirecional entre códigos:
```
F32.1 ↔ 296.22 (Major Depressive Disorder, Moderate)
```

### 5.2 Cobertura

29 mapeamentos cobrindo:
- MDD (simples e recorrente, todos os níveis de gravidade)
- Bipolar I (maníaco, depressivo, com/sem psicose)
- Bipolar II
- Distimia, Ciclotimia
- GAD, Panico, PTSD, Fobia Social, TOC

---

## 6. Alertas Clínicos

Endpoint: `GET /api/alerts/check-all`

Quatro categorias de alerta:

| Alerta | Descrição | Trigger |
|---|---|---|
| Scale Threshold | Pontuação acima do limiar clínico | PHQ-9 ≥ 15, GAD-7 ≥ 10, MADRS ≥ 20 |
| Suicidal Ideation | Ideação suicida em avaliações | Item 9 do PHQ-9 > 0 |
| Missed Follow-up | Paciente sem consulta há ≥30 dias | Última consulta > 30 dias |
| High Confidence Deterioration | Piora com alta confiança diagnóstica | Probabilidade bayesiana ≥ 0.8 |

---

## 7. Métricas e Dashboards

Endpoint: `GET /api/metrics/*`

| Endpoint | Retorna |
|---|---|
| `/api/metrics/general` | Total de pacientes, consultas, diagnósticos, avaliações |
| `/api/metrics/demographics` | Distribuição por faixa etária e gênero |
| `/api/metrics/consultations` | Consultas por período |
| `/api/metrics/disorders` | Prevalência de transtornos na base |
| `/api/metrics/scales/{name}` | Distribuição de pontuações (PHQ-9, GAD-7, MADRS) |
| `/api/metrics/patients/{uuid}/longitudinal` | Evolução temporal de um paciente |

---

## 8. Segurança e Auditoria

### 8.1 Controle de Acesso

| Role | Permissões |
|---|---|
| `admin` | CRUD total + gerenciamento de usuários + auditoria |
| `clinician` | CRUD em pacientes, episódios, inferências; sem deletar |
| `viewer` | Leitura apenas |

### 8.2 Auditoria

Todas as operações em registros clínicos são logadas com:
- `entity_name`, `entity_id`, `operation_type`
- `performed_by` (UUID do profissional)
- `old_data`, `new_data` (snapshot completo)
- `ip_address`, `user_agent`
- `created_at` (timestamp)

Acesso: `GET /api/audit/logs` (apenas admin)

### 8.3 Privacidade (LGPD/GDPR)

- Pacientes identificados por UUID (não por dados pessoais)
- Dados de identidade armazenados separadamente dos perfis clínicos
- Email mascarado na auditoria: `joao.silva@email.com` → `joa***@email.com`
- Criptografia Fernet AES para campos sensíveis

---

## 9. Guia de Interpretação Clínica

### 9.1 Quando usar cada motor

| Situação | Motor Recomendado |
|---|---|
| Suspeita de transtorno específico, sintomas bem definidos | Critérios (`/inferences/run`) |
| Diagnóstico diferencial entre múltiplos transtornos | Bayesiano (`/inferences/bayesian`) |
| Paciente com sintomas atípicos ou sobrepostos | Ambos, comparar resultados |
| Reavaliação longitudinal (monitorar resposta ao tratamento) | Escalas (`/assessments/score`) |
| Suspeita de ideação suicida | Escalas + Alerta de ideação |

### 9.2 Limitações Conhecidas

- Os **priors bayesianos** são baseados em população geral dos EUA (NCS-R) — podem não refletir a prevalência local
- O **criteria evaluator** não pondera gravidade dos sintomas — apenas presença/ausência
- Não há diferenciação entre **primeiro episódio** e **recorrência**
- Comorbidades são modeladas como boost simples — não como redes Bayesianas completas com dependências entre transtornos
- Crianças e adolescentes podem apresentar sintomatologia diferente (não validado para <18 anos)

---

## 10. Referências

1. American Psychiatric Association. (2022). *Diagnostic and Statistical Manual of Mental Disorders* (5th ed., text rev.).
2. World Health Organization. (2019). *ICD-11: International Classification of Diseases* (11th ed.).
3. Kessler, R. C., et al. (2005). *Lifetime prevalence and age-of-onset distributions of DSM-IV disorders in the NCS-R.* Archives of General Psychiatry.
4. Kroenke, K., et al. (2001). *The PHQ-9: validity of a brief depression severity measure.* Journal of General Internal Medicine.
5. Spitzer, R. L., et al. (2006). *A brief measure for assessing generalized anxiety disorder: the GAD-7.* Archives of Internal Medicine.
6. Montgomery, S. A., & Åsberg, M. (1979). *A new depression scale designed to be sensitive to change.* British Journal of Psychiatry.
7. Lei Geral de Proteção de Dados (LGPD) — Lei nº 13.709/2018.
8. General Data Protection Regulation (GDPR) — Regulation (EU) 2016/679.
