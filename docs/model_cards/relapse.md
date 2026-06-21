# Model Card: Predição de Recaída (Relapse)

## 1. Identificação
- **ID do modelo:** `relapse_{algorithm}`
- **Objective:** `relapse` (binário)
- **Algoritmos:** Logistic Regression, Random Forest, XGBoost
- **Registro:** MLflow `mind-cdss` + `ml.registered_models`
- **Stage:** Produção (auto-promovido pós-treino)

## 2. Task
Classificação binária que prediz se o paciente terá uma nova consulta em até 60 dias (proxy de recaída).

**Classes (2):**
- `0` — Sem recaída (próxima consulta > 60 dias ou sem consulta subsequente)
- `1` — Recaída (próxima consulta ≤ 60 dias)

## 3. Uso Pretendido (Intended Use)
- **Cenário principal:** Sinalizar pacientes com maior probabilidade de recaída precoce para permitir intervenção proativa (reforço de adesão, alta monitorada, contato telefônico)
- **Input:** Vetor de 51 features (mesma engenharia dos demais objetivos)
- **Output:** Probabilidade de recaída + classe binária
- **Threshold clínico sugerido:** Probabilidade > 0.5 para ativação de alerta; centros com baixa tolerância a falso positivo podem usar > 0.7

## 4. Usos Não Pretendidos (Out-of-Scope)
- **Predição de recaída em transtornos específicos:** O modelo não distingue tipo de recaída (depressiva, psicótica, ansiosa)
- **Prazo diferente de 60 dias:** O limiar de 60 dias é arbitrário e calibrado para dados sintéticos
- **Alta psiquiátrica:** Não validado para predizer readmissão hospitalar
- **Primeira consulta:** Pacientes sem histórico de consultas anteriores não têm predição (feature `consult_num` = 1)

## 5. Dados de Treino
- **Natureza: ⚠️ Sintéticos** — gerados por `scripts/seed_clinical_data.py`
- **Tamanho:** ~945 consultas rotuladas (depende do número de pacientes com ≥ 2 consultas)
- **Label (proxy):** `relapse_target = 1` quando `days_diff` entre consulta atual e próxima ≤ 60 dias (agrupado por `patient_uuid`)
- **Features (51):** Idênticas ao objetivo `diagnosis` (ver `docs/model_cards/diagnosis.md` seção 5)
- **Split temporal:** 80% treino / 20% teste

## 6. Métricas de Performance

| Métrica | Descrição |
|---------|-----------|
| `accuracy` | Acurácia global |
| `precision_macro` | Média macro da precisão |
| `recall_macro` | Média macro da revocação |
| `f1_score` | F1-score macro médio |
| `roc_auc` | AUC-ROC (disponível por ser binário) — curva ROC e AUC calculadas no notebook de avaliação |

> **Nota:** Consulte `notebooks/model_evaluation.ipynb` para curvas ROC, Precision-Recall, e gráficos de calibração (Brier score).

## 7. Limitações Conhecidas
1. **Proxy de recaída impreciso:** `relapse_target` usa intervalo entre consultas como proxy; pacientes podem retornar cedo por outros motivos (retorno agendado, renovação de receita)
2. **Label sintético:** A definição de "recaída" (≤ 60 dias) não tem validação clínica — é um hiperparâmetro arbitrário
3. **Dados sintéticos com baixa variabilidade temporal:** Consultas sintéticas tendem a ter intervalos regulares, não refletindo a imprevisibilidade de recaídas reais
4. **Viés de sobrevivência:** Pacientes com apenas uma consulta não contribuem para o alvo (sem par consecutivo)
5. **Sem fatores contextuais externos:** O modelo ignora eventos de vida, adesão medicamentosa, suporte familiar — preditores conhecidos de recaída

## 8. ⚠️ Aviso Clínico (Clinical Warning)
**Este modelo é uma ferramenta de apoio à decisão clínica, não um dispositivo diagnóstico autônomo.**
- A predição de recaída deve ser interpretada no contexto da relação terapêutica, adesão ao tratamento e suporte psicossocial
- Um valor preditivo baixo não elimina a possibilidade de recaída; um valor alto não substitui monitoramento clínico
- A intervenção proativa baseada neste modelo deve ser sempre supervisionada por profissional responsável (CRM/CRP)
- Dados sintéticos limitam a generalização; métricas de performance são ilustrativas
- Este sistema não substitui instrumentos validados de monitoramento de recaída (ex.: LIFE, PSP, CGI)
