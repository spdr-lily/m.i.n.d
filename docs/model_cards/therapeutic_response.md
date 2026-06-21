# Model Card: Resposta Terapêutica (Therapeutic Response)

## 1. Identificação
- **ID do modelo:** `therapeutic_response_{algorithm}`
- **Objective:** `therapeutic_response` (binário)
- **Algoritmos:** Logistic Regression, Random Forest, XGBoost
- **Registro:** MLflow `mind-cdss` + `ml.registered_models`
- **Stage:** Produção (auto-promovido pós-treino)

## 2. Task
Classificação binária que prediz se o paciente apresentará melhora na consulta seguinte, definida como redução no escore PHQ-9.

**Classes (2):**
- `0` — Sem melhora (PHQ-9 estável ou aumentou)
- `1` — Melhora (PHQ-9 diminuiu na consulta subsequente)

**Critério de melhora:** `next_phq9 < current_phq9`, considerando apenas pares consecutivos de consultas do mesmo paciente.

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
- **Natureza: ⚠️ Sintéticos** — gerados por `scripts/seed_clinical_data.py`
- **Tamanho:** ~945 consultas rotuladas (depende do número de pacientes com ≥ 2 consultas e PHQ-9 registrado)
- **Label (proxy):** `therapeutic_response_target = 1` quando `next_phq9 < current_phq9` (agrupado por `patient_uuid`, ordenado por `consultation_date`)
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
1. **Proxy limitado de melhora:** Redução no PHQ-9 é uma proxy restrita; não captura domínios funcionais, qualidade de vida ou remissão sindrômica
2. **PHQ-9 como única âncora:** Transtornos que não cursam com sintomas depressivos podem ter PHQ-9 basal baixo e teto para melhora, tornando o alvo ruidoso
3. **Label condicionado a dados pareados:** Pacientes com única consulta ou com PHQ-9 faltante são excluídos (viés de amostra)
4. **Regressão à média:** Redução no PHQ-9 pode refletir regressão à média em escores extremos, não efeito terapêutico verdadeiro
5. **Sem controle para duração do tratamento:** O intervalo entre consultas não é uniforme; uma consulta após 7 dias pode ter dinâmica diferente de uma após 90 dias
6. **Efeito placebo não modelado:** Dados sintéticos não incorporam resposta placebo, que corresponde a 30–40% da melhora observada em ensaios clínicos reais

## 8. ⚠️ Aviso Clínico (Clinical Warning)
**Este modelo é uma ferramenta de apoio à decisão clínica, não um dispositivo diagnóstico autônomo.**
- A predição de resposta terapêutica deve ser um dos múltiplos insumos na tomada de decisão clínica, não o único
- Baixa probabilidade de melhora prevista **não justifica** abandono, troca abrupta de medicação, ou suspensão de tratamento sem avaliação clínica
- Alta probabilidade de melhora prevista **não substitui** o monitoramento sistemático com escalas validadas e acompanhamento presencial
- O modelo foi treinado exclusivamente em **dados sintéticos** — métricas são ilustrativas, não preditivas de cenários reais
- Decisões terapêuticas devem seguir as diretrizes da APA, ABP, e o julgamento clínico do profissional responsável (CRM/CRP)
