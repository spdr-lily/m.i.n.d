# Model Card: Risco de Suicídio (Suicide Risk)

## 1. Identificação
- **ID do modelo:** `suicide_risk_{algorithm}`
- **Objective:** `suicide_risk` (binário)
- **Algoritmos:** Logistic Regression, Random Forest, XGBoost
- **Registro:** MLflow `mind-cdss` + `ml.registered_models`
- **Stage:** Produção (auto-promovido pós-treino)

## 2. Task
Classificação binária que prediz risco de suicídio com base em regras heurísticas de gravidade de sintomas.

**Classes (2):**
- `0` — Risco baixo
- `1` — Risco alto

**Regras de rotulagem (label heurístico):**
- `(symptom_count >= 6 AND severe_symptom_count >= 2)`
- `OR (avg_intensity >= 6 AND symptom_count >= 5)`
- `OR (severe_symptom_count >= 3 AND daily_symptom_count >= 2)`

## 3. Uso Pretendido (Intended Use)
- **Cenário principal:** Sinalizar pacientes com alta carga sintomática que podem necessitar de avaliação de risco suicida imediata
- **Input:** Vetor de 51 features (demográficas, sintomas, 21 escalas, flags, temporais, histórico)
- **Output:** Probabilidade de risco + classe binária
- **Usuários-alvo:** Psiquiatras e psicólogos em contexto de triagem e monitoramento ambulatorial

## 4. Usos Não Pretendidos (Out-of-Scope)
- **Substituto para avaliação de risco presencial:** O modelo não substitui a Columbia-Suicide Severity Rating Scale (C-SSRS) ou entrevista clínica
- **Decisão de alta hospitalar:** Não validado para liberação de pacientes internados
- **Predição de tentativa de suicídio:** O alvo mede _carga sintomática_, não ideação, planejamento ou tentativa
- **Crise aguda:** Em contextos de emergência, nenhuma ferramenta automatizada substitui avaliação imediata presencial
- **População infanto-juvenil:** Modelo treinado com features baseadas em população adulta

## 5. Dados de Treino
- **Natureza: ⚠️ Sintéticos** — gerados por `scripts/seed_clinical_data.py`
- **Tamanho:** ~945 consultas rotuladas
- **Label (heurístico):** O alvo `suicide_risk_target` é derivado de regras fixas sobre as features de sintoma (contagem, intensidade, severidade, diários) — **não de avaliação clínica real**
- **Features (51):** Idênticas aos demais objetivos (ver `docs/model_cards/diagnosis.md` seção 5)
- **Split temporal:** 80% treino / 20% teste

## 6. Métricas de Performance

| Métrica | Descrição |
|---------|-----------|
| `accuracy` | Acurácia global |
| `precision_macro` | Média macro da precisão |
| `recall_macro` | Média macro da revocação |
| `f1_score` | F1-score macro médio |
| `roc_auc` | AUC-ROC (disponível por ser binário) |

> **Nota:** Consulte `notebooks/model_evaluation.ipynb` para curvas ROC, Precision-Recall, calibração (Brier score), e matriz de confusão.

## 7. Limitações Conhecidas
1. **Label tautológico:** O alvo é derivado das próprias features de sintoma — o modelo essencialmente aprende a replicar regras if-then. Isso infla as métricas e não reflete capacidade preditiva real
2. **Nenhum dado de ideação suicida:** As features não incluem escalas específicas de ideação suicida (C-SSRS, item 9 do PHQ-9 desagregado, Beck Scale for Suicide Ideation)
3. **Falso negativo perigoso:** Um paciente com ideação suicida ativa mas baixa carga sintomática global pode ser classificado como baixo risco
4. **Viés de severidade:** O modelo pode superestimar risco em pacientes com múltiplos sintomas crônicos de baixa intensidade
5. **Sem validação externa:** Não testado contra desfechos reais de tentativa ou suicídio consumado

## 8. ⚠️ Aviso Clínico (Clinical Warning)
**Este modelo é uma ferramenta de apoio à decisão clínica, não um dispositivo diagnóstico autônomo.**
- 🚨 **Risco de suicídio é uma emergência médica.** Nenhum modelo preditivo substitui avaliação clínica presencial imediata
- Um resultado de **baixo risco não elimina** a possibilidade de ideação ou tentativa suicida
- Um resultado de **alto risco exige avaliação clínica compulsória**, não ação automatizada
- O modelo foi treinado com **dados sintéticos** usando regras heurísticas como rótulo — não houve validação contra desfechos reais
- Em caso de qualquer suspeita clínica de risco suicida, siga os protocolos institucionais e as diretrizes da Associação Brasileira de Psiquiatria (ABP) ou OMS
- **Este sistema não substitui a C-SSRS, a avaliação de risco padronizada, ou o julgamento clínico**
