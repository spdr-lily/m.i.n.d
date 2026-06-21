# Model Card: Classificação de Diagnóstico (Diagnosis)

## 1. Identificação
- **ID do modelo:** `diagnosis_{algorithm}`
- **Objective:** `diagnosis` (multiclasse, 20 classes)
- **Algoritmos:** Logistic Regression, Random Forest, XGBoost
- **Registro:** MLflow `mind-cdss` + `ml.registered_models`
- **Stage:** Produção (auto-promovido pós-treino)

## 2. Task
Classificação multirrótulo que prediz qual dos 19 transtornos do núcleo DSM-5-TR melhor explica uma consulta clínica.

**Classes (20):**
| # | Classe | Descrição |
|---|--------|-----------|
| 0–18 | Transtornos núcleo | 19 transtornos definidos em `KNOWN_DISORDERS` (Depressivo Maior, TAG, Pânico, TEPT, Bipolar I/II, TOC, Distimia, Ansiedade Social, Agorafobia, Substâncias, Anorexia, Bulimia, Compulsão Alimentar, Insônia, Esquizofrenia, Sintomas Somáticos, TEA, TDAH) |
| 19 | `Other` | Nenhum dos 19 núcleos (catch-all) |

## 3. Uso Pretendido (Intended Use)
- **Cenário principal:** Segunda opinião diagnóstica baseada em sintomas reportados + escores de escalas + histórico do paciente
- **Input:** Vetor de 51 features (demográficas, agregações de sintomas, 21 escores brutos de escalas, 10 flags binárias de severidade, 3 temporais, 10 de histórico)
- **Output:** Probabilidade por classe (20); classe com maior probabilidade é a predição primária
- **Usuários-alvo:** Psiquiatras, psicólogos clínicos, residentes em saúde mental — como ferramenta de apoio, não substituta

## 4. Usos Não Pretendidos (Out-of-Scope)
- **Diagnóstico autônomo sem supervisão clínica:** O modelo não substitui avaliação presencial
- **Triagem populacional sem validação prospectiva:** Não validado para uso em larga escala não supervisionada
- **Crianças e adolescentes:** Dados sintéticos baseados em população adulta (18–65 anos)
- **Transtornos fora do núcleo:** As 172 classes de referência não são preditas diretamente (caem em `Other`)
- **Decisões legais ou judiciais:** Não apto para laudo pericial sem revisão clínica

## 5. Dados de Treino
- **Natureza: ⚠️ Sintéticos** — gerados por `scripts/seed_clinical_data.py`
- **Tamanho:** ~945 consultas rotuladas (após remoção de `NaN` no alvo)
- **Features (51):** 4 demográficas (idade, sexo, escolaridade, estado civil), 5 agregações de sintomas (contagem, intensidade média/total, severos, diários), 21 escalas clínicas e neuropsicológicas, 10 flags binárias, 6 temporais/histórico
- **Split temporal:** 80% treino (mais antigas) / 20% teste (mais recentes)
- **Label:** Obtido do `top_inferences` gerado pelo motor de inferência `InferenceEngine` (regras + Bayes); primeiro transtorno da string parseada; `Other` se não estiver em `KNOWN_DISORDERS`

## 6. Arquitetura dos Algoritmos

### Logistic Regression
- `LogisticRegression` (sklearn), `max_iter=5000`, `C=1.0`, `solver='lbfgs'`
- Regularização L2, `class_weight='balanced'`
- Grid: `C ∈ [0.01, 0.1, 1.0, 10.0]`, `max_iter ∈ [1000, 2000, 5000]`

### Random Forest
- `RandomForestClassifier` (sklearn), `n_estimators=200`, `max_depth=10`
- `min_samples_leaf=4`, `class_weight='balanced'`, `n_jobs=-1`
- Grid: `n_estimators ∈ [100, 200, 300]`, `max_depth ∈ [5, 10, 15, None]`, `min_samples_leaf ∈ [2, 4, 8]`

### XGBoost
- `XGBClassifier`, `n_estimators=200`, `max_depth=6`, `learning_rate=0.1`
- `subsample=0.8`, `colsample_bytree=0.8`, `eval_metric='logloss'`
- Grid: `n_estimators ∈ [100, 200, 300]`, `max_depth ∈ [4, 6, 8]`, `learning_rate ∈ [0.01, 0.1, 0.2]`, `subsample ∈ [0.7, 0.8, 1.0]`

## 7. Métricas de Performance

| Métrica | Descrição |
|---------|-----------|
| `accuracy` | Acurácia global |
| `precision_macro` | Média macro da precisão por classe |
| `recall_macro` | Média macro da revocação por classe |
| `f1_score` | F1-score macro médio |
| `roc_auc` | **Não disponível** (multiclasse 20 classes — usa-se macro AUC one-vs-rest no notebook de avaliação) |

> **Nota:** As métricas individuais de cada versão estão armazenadas em `ml.model_versions.metrics` (JSON). Consulte `notebooks/model_evaluation.ipynb` para análise completa com AUC-ROC por classe, matriz de confusão, e comparação entre algoritmos.

## 8. Limitações Conhecidas
1. **Dados sintéticos:** As métricas refletem correlações programáticas, não validade clínica real
2. **Desequilíbrio de classes:** Transtornos raros (ex.: Anorexia) podem ter baixa representatividade mesmo em dados sintéticos
3. **Label ruidoso:** O alvo `diagnosis_target` deriva do motor de inferência (`InferenceEngine`), não de gold standard clínico (entrevista estruturada SCID-5)
4. **Cat-all `Other`:** 172 transtornos de referência são comprimidos em uma única classe, perdendo granularidade
5. **Sem calibração probabilística:** As probabilidades de saída não são calibradas (sem Platt scaling ou isotonic regression)

## 9. ⚠️ Aviso Clínico (Clinical Warning)
**Este modelo é uma ferramenta de apoio à decisão clínica, não um dispositivo diagnóstico autônomo.**
- Todas as predições devem ser revisadas por um profissional de saúde mental habilitado (CRM/CRP)
- O modelo foi treinado exclusivamente em **dados sintéticos** — suas métricas de performance são ilustrativas
- A classificação `Other` não implica ausência de transtorno; indica apenas que o quadro não se enquadra nos 19 núcleos conhecidos pelo modelo
- Em caso de discrepância entre a predição do modelo e a avaliação clínica, a avaliação clínica sempre prevalece
- Este sistema não substitui uma entrevista diagnóstica estruturada (SCID-5, MINI)
