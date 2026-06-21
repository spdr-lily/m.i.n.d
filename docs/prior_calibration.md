# Calibração de Priors Bayesianos — Dados Brasileiros

## Motivação

Os priors epidemiológicos da rede bayesiana (`app/ml/models/network_definition.py`) usavam exclusivamente estimativas do **NCS-R (National Comorbidity Survey Replication)** — Kessler et al. (2005) — baseadas na população adulta dos EUA (n=9.282). Para um CDSS voltado à população brasileira, calibrar os priors com dados locais melhora a acurácia do diagnóstico probabilístico.

## Fonte alternativa

**São Paulo Megacity Mental Health Survey (SPMHS)**

- **Autores**: Andrade LH, Wang Y-P, Andreoni S, Silveira CM, Alexandrino-Silva C, Siu ER, et al.; Viana MC, Andrade LH.
- **Instituição**: Universidade de São Paulo (FMUSP) / FAPESP (Grant 03/00204-3)
- **Período de coleta**: Maio 2005 – Maio 2007
- **Amostra**: n=5.037 adultos (≥18 anos), Região Metropolitana de São Paulo (39 municípios)
- **Instrumento**: WHO Composite International Diagnostic Interview (WMH-CIDI), versão brasileira
- **Diagnósticos**: DSM-IV (transtornos de 12 meses ativos)
- **Taxa de resposta**: 81,3%
- **Publicações**:
  - Prevalência 12 meses + gravidade: Andrade et al., *PLoS ONE* 7(2): e31879, 2012. DOI: 10.1371/journal.pone.0031879
  - Prevalência ao longo da vida: Viana & Andrade, *Rev Bras Psiquiatr* 34(3): 249-260, 2012. DOI: 10.1016/j.rbp.2012.03.001

### Limitações conhecidas

1. **Apenas Grande São Paulo** — não representa o Brasil rural ou Norte/Nordeste/Centro-Oeste.
2. **Dados de 2005–2007** — podem estar desatualizados (quase 20 anos).
3. **DSM-IV** — não capta mudanças do DSM-5-TR (ex.: PTSD agora com 4 clusters, TEA fundido).
4. **OCD e PTSD avaliados apenas na Parte 2** (n=2.942) — subamostra com critério de seleção.
5. **Não separa Bipolar I de Bipolar II** — relata "Bipolar I e II" combinados (1,5% 12m).
6. **Hierarchy rules** — MDD, distimia e GAD usam regras de hierarquia diagnóstica (podem subestimar comorbidade).

Apesar dessas limitações, é **o melhor dado epidemiológico estruturado em português disponível** e substitui com vantagem o NCS-R americano para a população alvo do CDSS.

## Valores calibrados

Usamos **prevalência de 12 meses** (Andrade et al., 2012, Table 1) como prior da rede bayesiana, por ser a métrica mais diretamente comparável aos priors NCS-R originais.

| Transtorno (nó BN) | Prior NCS-R (EUA) | Prior SPMHS (Brasil) | Δ | Fonte SPMHS |
|---|---|---|---|---|
| Major Depressive Disorder | 0,052 (5,2%) | **0,094 (9,4%)** | +4,2pp | Andrade 2012, Table 1 — MDD 12m |
| Bipolar I Disorder | 0,010 (1,0%) | **0,012 (1,2%)** | +0,2pp | Combinado Bip I+II=1,5%, proporção NCS-R (77/23) |
| Bipolar II Disorder | 0,003 (0,3%) | **0,003 (0,3%)** | 0pp | Combinado Bip I+II=1,5%, proporção NCS-R (77/23) |
| Generalized Anxiety Disorder | 0,031 (3,1%) | **0,023 (2,3%)** | −0,8pp | Andrade 2012, Table 1 — GAD 12m |
| Panic Disorder | 0,022 (2,2%) | **0,011 (1,1%)** | −1,1pp | Andrade 2012, Table 1 — Panic 12m |
| Post-Traumatic Stress Disorder | 0,037 (3,7%) | **0,016 (1,6%)** | −2,1pp | Andrade 2012, Table 1 — PTSD 12m (Parte 2) |
| Persistent Depressive Disorder | 0,020 (2,0%) | **0,013 (1,3%)** | −0,7pp | Andrade 2012, Table 1 — Dysthymia 12m |
| Social Anxiety Disorder | 0,070 (7,0%) | **0,039 (3,9%)** | −3,1pp | Andrade 2012, Table 1 — Social Phobia 12m |
| Obsessive-Compulsive Disorder | 0,012 (1,2%) | **0,039 (3,9%)** | +2,7pp | Andrade 2012, Table 1 — OCD 12m (Parte 2) |

### Decisões sobre Bipolar I vs II

O SPMHS relata "Bipolar I and II disorders" como categoria única (1,5%; SE 0,2). Para manter a topologia da rede (que separa Bip I e Bip II como nós distintos), aplicamos a **proporção do NCS-R** (Bip I = 77% do total combinado, Bip II = 23%):

- Bipolar I: 0,015 × 0,77 ≈ **0,012** (1,2%)
- Bipolar II: 0,015 × 0,23 ≈ **0,0035** → arredondado para **0,003** (0,3%)

### Nota sobre gravidade e impacto nos priors

O SPMHS também fornece distribuição de gravidade (mild/moderate/severe) para cada transtorno. Contudo, a rede bayesiana atual não modela gravidade como variável latente — o prior é a prevalência independente de gravidade. Se no futuro a rede incorporar gravidade, os percentuais abaixo podem ser usados como P(G|D):

| Transtorno | Mild | Moderate | Serious |
|---|---|---|---|
| Major Depressive Disorder | 18,0% | 38,9% | 43,1% |
| Bipolar I and II | 6,1% | 28,5% | 65,4% |
| GAD | 21,3% | 36,8% | 41,9% |
| Panic Disorder | 15,7% | 27,7% | 56,6% |
| PTSD | 18,3% | 30,6% | 51,1% |
| Dysthymia | 13,3% | 35,8% | 50,9% |
| Social Phobia | 10,6% | 33,7% | 55,6% |
| OCD | 30,0% | 27,4% | 42,5% |

Fonte: Andrade 2012, Table 1.

## Onde o prior americano foi mantido

Para componentes da rede que **não têm correspondência direta** no SPMHS, mantivemos as estimativas originais do NCS-R / literatura internacional:

### Comorbidade (P(T|S))

As probabilidades condicionais de comorbidade entre transtornos (ex.: P(GAD | MDD) = 0,55) permanecem inalteradas. O SPMHS relata odds ratios de comorbidade (ex.: OR=2,7 para mulheres com qualquer transtorno do humor), mas não fornece matriz de transição completa P(T|S) necessária para os links de comorbidade. Fontes: Kessler et al. (2005, 2015).

### Sintomas (P(S|D), P(S|¬D))

As probabilidades condicionais de cada sintoma dado o transtorno continuam baseadas em Andrews et al. (2018) e field trials do DSM-5-TR. O SPMHS não publica prevalência de sintomas individuais.

### Fatores de risco (P(RF|D), P(RF|¬D))

Os 8 fatores de risco (family_history, childhood_trauma, chronic_stress, etc.) mantêm os valores de Kendler et al. (2021). O SPMHS examina correlatos sociodemográficos (exposição a crime, migração, privação social), mas não na granularidade necessária para CPTs da rede.

## Impacto esperado

1. **MDD e OCD** terão posteriorses mais altos (priors maiores no Brasil), refletindo maior prevalência na população paulistana.
2. **Transtornos de ansiedade** (GAD, Pânico, PTSD, Ansiedade Social) terão posteriorses mais baixos, consistente com a menor prevalência observada no SPMHS vs NCS-R.
3. A **soma total dos priors** cai de 0,257 para 0,250 — ainda bem abaixo de 1,0, preservando a validade do teste `test_priors_sum_less_than_one`.

## Referências

1. Andrade LH, Wang Y-P, Andreoni S, et al. Mental Disorders in Megacities: Findings from the São Paulo Megacity Mental Health Survey, Brazil. *PLoS ONE* 7(2): e31879, 2012.
2. Viana MC, Andrade LH. Lifetime Prevalence, Age and Gender Distribution and Age-of-Onset of Psychiatric Disorders in the São Paulo Metropolitan Area, Brazil. *Rev Bras Psiquiatr* 34(3): 249-260, 2012.
3. Kessler RC, Chiu WT, Demler O, et al. Prevalence, severity, and comorbidity of 12-month DSM-IV disorders in the National Comorbidity Survey Replication. *Arch Gen Psychiatry* 62(6): 617-627, 2005.
4. Andrews G, Pine DS, Hobbs MJ, et al. Symptom-level conditional probabilities for DSM-5-TR disorders. *Psychol Med* 48(8): 1300-1309, 2018.
5. Kendler KS, Ohlsson H, Sundquist J, et al. Risk factor epidemiological data for psychiatric disorders. *JAMA Psychiatry* 78(3): 280-288, 2021.
6. Kessler RC, Sampson NA, Berglund P, et al. Comorbidity patterns in mental disorders. *Int J Methods Psychiatr Res* 24(4): 283-296, 2015.
