# Model Card: Resposta Terapêutica (Therapeutic Response)

## 1. Identificação
- **ID do modelo:** `therapeutic_response_{algorithm}`
- **Objective:** `therapeutic_response` (binário)
- **Algoritmos:** Logistic Regression, Random Forest, XGBoost
- **Registro:** MLflow `mind-cdss` + `ml.registered_models`
- **Stage:** Produção (auto-promovido pós-treino)

## 2. Task
Classificação binária que prediz resposta terapêutica com base em perfil clínico sintético.

**Classes (2):**
- `0` — Sem resposta
- `1` — Respondeu ao tratamento

**Critério de melhora:** Label gerado por modelo probabilístico (`generate_therapeutic_response` em `app/ml/training/label_builder.py`) com baseline de ~30%, modificado por gravidade (PHQ-9), duração do tratamento, número de consultas e tipo de transtorno. Alvo: 35–50% de positivos.

## 3. Uso Pretendido (Intended Use)
- **Cenário principal:** Monitorar probabilidade de resposta ao tratamento ao longo do tempo, permitindo ajuste terapêutico precoce
- **Input:** Vetor de 51 features (demográficas, sintomas, 21 escalas, flags, temporais, histórico)
- **Output:** Probabilidade de resposta favorável + classe binária
- **Usuários-alvo:** Clínicos que desejam identificar pacientes com baixa probabilidade de resposta para intensificar ou modificar a conduta

## 4. Usos Não Pretendidos (Out-of-Scope)
- **Predição de resposta a medicamento específico:** O modelo não distingue entre intervenções farmacológicas, psicoterápicas ou combinadas
- **Substituto para escalas de desfecho validadas:** Não substitui CGI-I, MADRS, HAM-D ou QIDS-SR na avaliação de resposta
- **Primeira consulta:** Pacientes sem consulta subsequente não geram alvo
- **Resposta em transtornos não depressivos:** A métrica de melhora usa exclusivamente PHQ-9; resposta em ansiedade, bipolaridade ou psicose não é capturada
- **Previsão de longo prazo (> 1 consulta):** O modelo prediz apenas a consulta imediatamente seguinte

## 5. Dados de Treino
- **Natureza: ⚠️ Sintéticos** — gerados por `app/ml/training/label_builder.py:generate_therapeutic_response()`
- **Tamanho:** ~189–200 consultas rotuladas (todas as consultas recebem label, não apenas as com pares consecutivos)
- **Label (probabilístico):** `therapeutic_response_target` gerado via `np.random.binomial(1, p)` onde `p` é calculado por:
  - Base: ~0.30
  - PHQ-9 < 10: +0.05; PHQ-9 ≥ 20: -0.05
  - `days_since_last_consult > 60`: +0.07; `< 14`: -0.05
  - `consult_num >= 3`: +0.05
  - Transtornos depressivos/TAG: +0.03
  - Transtornos psicóticos/bipolares: -0.08
  - Clipping: [0.10, 0.80]
- **Distribuição alvo:** 35–50% positivos
- **Features (22):** Demográficas (age, sex, education, marital) + sintomas (count, intensity) + escalas (PHQ-9, GAD-7) + temporais (consult_num, days_since_last_consult) + histórico (avg_phq9_per_item)
- **Split:** 75% treino / 25% teste com estratificação

## 6. Métricas de Performance

| Métrica | Descrição |
|---------|-----------|
| `accuracy` | Acurácia global |
| `precision_macro` | Média macro da precisão |
| `recall_macro` | Média macro da revocação |
| `f1_score` | F1-score macro médio |
| `roc_auc` | AUC-ROC (disponível por ser binário) |
| `pr_auc` | **PR-AUC** — métrica primária para classes desbalanceadas |
| `brier_score` | **Brier Score** — calibração das probabilidades (0 = perfeita) |

> **Nota:** Consulte `notebooks/model_evaluation.ipynb` para curvas ROC, Precision-Recall, calibração (Brier score), e matriz de confusão.

## 7. Limitações Conhecidas
1. **Label probabilístico, não observacional:** O alvo é gerado por função determinística+aleatória, não derivado de acompanhamento clínico real
2. **Modificadores limitados:** O gerador usa apenas PHQ-9, intervalo entre consultas e tipo de transtorno; não incorpora adesão, efeito placebo, comorbidades nem resposta diferencial por medicamento
3. **Baseado em dados sintéticos:** A distribuição de 35–50% positivos é uma conveniência do gerador, não um dado epidemiológico real
4. **Sem variáveis de tratamento:** O dataset não inclui medicação específica, dose, adesão nem tipo de psicoterapia — fatores críticos para resposta terapêutica
5. **Dataset pequeno:** ~189–200 amostras com 22 features — alta varianza e risco de overfitting, especialmente para XGBoost
6. **Sem controle para duração do tratamento:** O intervalo entre consultas não é uniforme; uma consulta após 7 dias pode ter dinâmica diferente de uma após 90 dias

## 8. ⚠️ Aviso Clínico (Clinical Warning)
**Este modelo é uma ferramenta de apoio à decisão clínica, não um dispositivo diagnóstico autônomo.**
- A predição de resposta terapêutica deve ser um dos múltiplos insumos na tomada de decisão clínica, não o único
- Baixa probabilidade de melhora prevista **não justifica** abandono, troca abrupta de medicação, ou suspensão de tratamento sem avaliação clínica
- Alta probabilidade de melhora prevista **não substitui** o monitoramento sistemático com escalas validadas e acompanhamento presencial
- O modelo foi treinado exclusivamente em **dados sintéticos** — métricas são ilustrativas, não preditivas de cenários reais
- Decisões terapêuticas devem seguir as diretrizes da APA, ABP, e o julgamento clínico do profissional responsável (CRM/CRP)
