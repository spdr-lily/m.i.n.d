# Projeto: M.I.N.D (Mental Intelligence & Network Data)
**Sistema de Inteligência para Apoio Diagnóstico em Saúde Mental**
<br/>*A decomposição conceitual liga a cognição humana (Mental Intelligence) à infraestrutura de dados conectados (Network Data).*<br/>

Este documento apresenta a especificação e o escopo atualizados do projeto de cruzamento entre **Ciência de Dados** e **Psicologia/Psiquiatria**, idealizado para otimizar processos clínicos, mitigar erros de diagnóstico em saúde mental e estruturar uma modelagem probabilística rigorosa baseada em evidências científicas.

---

## 1. Contexto e Motivação
O processo de diagnóstico em saúde mental enfrenta desafios severos e estruturais que impactam diretamente a vida dos pacientes. Entre os principais problemas identificados estão:
* **Alta Taxa de Erros Diagnósticos:** Diversos transtornos possuem sintomas sobrepostos (comorbidades e manifestações similares), gerando tratamentos e prescrições iniciais ineficazes.
* **Barreiras de Acesso e Custo:** Avaliações neuropsicológicas completas possuem custo elevado, planos de saúde frequentemente não cobrem e as filas de espera no sistema público (SUS) são extensas.
* **Morosidade:** O atraso na identificação correta do transtorno retarda o início de intervenções eficientes, prolongando o sofrimento do paciente.

## 2. Escopo e Objetivos do Projeto (Foco do MVP)
O projeto consiste no desenvolvimento de um **software de apoio à decisão clínica** direcionado exclusivamente a profissionais da saúde mental (psicólogos, psiquiatras e neurologistas).

**Objetivo Principal:**
Utilizar algoritmos de *Machine Learning*, estatística aplicada e modelagem probabilística para calcular a probabilidade de diagnósticos específicos baseados de forma unificada na **CID-11 (Classificação Internacional de Doenças)** e no **DSM-5-TR (Manual Diagnóstico e Estatístico de Transtornos Mentais)**, funcionando como uma ferramenta complementar à análise do profissional.

---

# 3. Funcionalidades Principais do Sistema

## Fase 1 MVP (Minimum Viable Product)
O foco inicial do projeto será a construção de um Clinical Decision Support System (CDSS) voltado para apoio probabilístico à tomada de decisão clínica em saúde mental, utilizando critérios estruturados do DSM-5-TR e da CID-11.

O MVP prioriza:
* interpretabilidade clínica;
* rastreabilidade diagnóstica;
* modelagem probabilística explicável;
* validação longitudinal;
* conformidade ética e regulatória.

### 3.1 Inferência Probabilística Diagnóstica
O núcleo do sistema será um motor de inferência clínica responsável por calcular a distribuição probabilística entre hipóteses diagnósticas possíveis a partir de sintomas observados, critérios temporais e regras de exclusão diagnóstica.

A inferência será baseada em:
* lógica diagnóstica estruturada;
* pesos probabilísticos condicionais;
* modelagem heurística inicial;
* futura expansão para Redes Bayesianas.

> O sistema não realizará diagnóstico definitivo, funcionando exclusivamente como ferramenta de apoio clínico.

### 3.2 Motor Lógico DSM-5-TR / CID-11
Implementação computacional dos critérios operacionais presentes no DSM-5-TR e CID-11, incluindo:
* critérios obrigatórios;
* cardinalidade mínima de sintomas;
* duração mínima dos episódios;
* regras de exclusão diagnóstica;
* relações de comorbidade;
* conflitos diagnósticos.

Essa camada transforma os critérios clínicos em estruturas computáveis e auditáveis.

---

### 3.3 Estrutura Longitudinal de Episódios Clínicos
O sistema utilizará uma modelagem longitudinal baseada em episódios clínicos, permitindo acompanhar:
* persistência sintomática;
* remissão;
* recorrência;
* evolução temporal;
* resposta terapêutica.

A estrutura longitudinal será especialmente relevante para transtornos do humor, como:
* Episódio Depressivo Maior;
* Transtorno Bipolar I;
* Transtorno Bipolar II;
* Distimia;
* Ciclotimia.

### 3.4 Ingestão Estruturada de Dados Clínicos
A coleta inicial de dados será baseada em instrumentos estruturados e escalas psicométricas padronizadas.

Os dados poderão incluir:
* checklists clínicos;
* escalas Likert;
* escalas transversais do DSM-5-TR;
* PHQ-9;
* GAD-7;
* observações clínicas estruturadas.

A arquitetura foi projetada para futura expansão multimodal via NLP clínico.

### 3.5 Explicabilidade Diagnóstica
Toda inferência produzida pelo sistema deverá possuir rastreabilidade completa.

O sistema armazenará:
* sintomas utilizados;
* critérios ativados;
* regras de exclusão aplicadas;
* pesos probabilísticos;
* conflitos diagnósticos;
* trilha lógica da inferência.

Essa abordagem visa garantir:
* transparência;
* auditoria clínica;
* confiabilidade;
* validação profissional.

---

### 3.6 Modelagem de Relações Diagnósticas
O sistema será capaz de representar:
* comorbidades;
* relações hierárquicas;
* exclusões diagnósticas;
* relações espectrais entre transtornos.

Essa camada permitirá análises probabilísticas mais próximas da prática clínica real.

### 3.7 Painel Longitudinal e Métricas Clínicas
O sistema disponibilizará dashboards interativos para acompanhamento temporal do paciente, incluindo:
* evolução sintomática;
* severidade clínica;
* frequência de sintomas;
* impacto funcional;
* adesão terapêutica;
* mudanças entre consultas.

Os painéis serão desenvolvidos inicialmente utilizando:
* Power BI;
* Apache Superset;
* métricas DAX;
* consultas analíticas SQL.

### 3.8 Arquitetura Preparada para Redes Bayesianas
Embora o MVP inicial utilize inferência heurística e lógica probabilística estruturada, toda a arquitetura foi planejada para futura migração para:
* Redes Bayesianas;
* inferência causal;
* aprendizado probabilístico;
* calibração epidemiológica dinâmica.

Essa evolução permitirá modelar relações condicionais complexas entre sintomas, episódios e transtornos.

---

### 3.9 Segurança, LGPD e Governança Clínica
A arquitetura do sistema foi projetada considerando:
* segregação entre identidade e camada analítica;
* anonimização de dados sensíveis;
* rastreabilidade de alterações;
* versionamento clínico;
* auditoria de inferência;
* controle de acesso;
* conformidade com LGPD.

O sistema sará o princípio de:
"Human-in-the-loop".

Toda decisão clínica permanecerá integralmente sob responsabilidade do profissional habilitado.

---

# 4. Arquitetura Tecnológica e Engenharia de Dados (Stack)

## 4.1 Banco de Dados Relacional (PostgreSQL)
A modelagem relacional foi estruturada para suportar:
* integridade clínica;
* inferência probabilística;
* modelagem longitudinal;
* explicabilidade diagnóstica;
* rastreabilidade completa.

Principais entidades:
* pacientes;
* episódios clínicos;
* consultas;
* sintomas;
* critérios diagnósticos;
* inferências;
* escalas psicométricas;
* relações bayesianas.

---

## 4.2 Backend e APIs Clínicas
O backend será desenvolvido utilizando:
* Python;
* FastAPI;
* SQLAlchemy;
* Pydantic.

A API será responsável por:
* ingestão de dados clínicos;
* execução das regras diagnósticas;
* cálculo probabilístico;
* rastreabilidade de inferências;
* integração futura com dashboards e NLP.

## 4.3 Modelagem Estatística e Inferência

### Python
Responsável por:
* pipelines de inferência;
* cálculo probabilístico;
* modelagem heurística;
* Redes Bayesianas futuras;
* engenharia de features clínicas.

Bibliotecas previstas:
* pandas;
* NumPy;
* scipy;
* statsmodels;
* pgmpy;
* PyMC.

### R
Responsável por:
* análise exploratória;
* validação psicométrica;
* testes estatísticos;
* análise de consistência interna;
* análise de classes latentes (LCA).

---

## 4.4 Dashboards e Visualização Analítica
Os painéis analíticos serão desenvolvidos com:
* Power BI;
* Apache Superset;
* consultas SQL analíticas;
* métricas DAX.

O objetivo é permitir:
* monitoramento longitudinal;
* visualização probabilística;
* acompanhamento clínico;
* interpretação rápida por profissionais de saúde.

## 4.5 Expansão Arquitetural Futura
A arquitetura foi desenhada para futura integração com:
* NLP clínico;
* ingestão multimodal;
* sistemas especialistas híbridos;
* inferência causal;
* pipelines MLOps;
* aprendizado longitudinal;
* integração interoperável com prontuários eletrônicos.

---

## 5. Fontes de Dados e Referências Científicas

### Critérios Diagnósticos Oficiais
* **CID-11:** *Capítulo 06 - Mental, behavioural or neurodevelopmental disorders*. Organização Mundial da Saúde (OMS). [Link oficial](https://icd.who.int/en).
* **DSM-5-TR:** *Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision*. American Psychiatric Association (APA). [Link oficial](https://dsm.psychiatryonline.org).
* **DSM-5-TR Online Assessment Measures:** Escalas transversais de sintomas (Level 1 e Level 2 Cross-Cutting Measures) utilizadas como padrão de dados de entrada do sistema. [Link oficial](https://www.psychiatry.org/psychiatrists/practice/dsm/educational-resources/assessment-measures).

### Repositórios de Microdados para Treinamento de Modelos
* **MIMIC-IV (Medical Information Mart for Intensive Care):** Prontuários eletrônicos anonimizados com históricos clínicos reais e códigos CID. PhysioNet / MIT Laboratory for Computational Physiology. [Link oficial](https://physionet.org/content/mimiciv/).
* **UCI Machine Learning Repository:** Conjuntos de dados tabulares e surveys consolidadas sobre saúde mental e comportamento. [Link oficial](https://archive.ics.uci.edu/).
* **UMLS Metathesaurus (Unified Medical Language System):** Base de dados integradora da U.S. National Library of Medicine (NLM) usada para crosswalks lógicos e unificação de termos biomédicos. [Link oficial](https://www.nlm.nih.gov/research/umls/index.html).

### Dados Epidemiológicos (Calibração de Probabilidades *a Priori*)
* **VIGITEL:** Vigilância de Fatores de Risco e Proteção para Doenças Crônicas por Inquérito Telefônico. Ministério da Saúde do Brasil. [Link oficial](https://www.gov.br/saude/pt-br).
* **Global Burden of Disease Study (GBD):** Dados globais e regionais de prevalência e incidência de transtornos mentais. Institute for Health Metrics and Evaluation (IHME), University of Washington. [Link oficial](https://www.healthdata.org/gbd).

---

## 6. Aspectos Éticos, Segurança e LGPD
* **Protagonismo Humano:** O sistema atua estritamente como um assistente de validação estatística. A metodologia e a decisão clínica final permanecem 100% sob a responsabilidade do profissional de saúde habilitado.
* **Conformidade com a LGPD (Lei nº 13.709/2018):** Anonimização obrigatória e irreversível de dados sensíveis dos pacientes (Artigo 11). Identificadores pessoais são completamente dissociados da camada analítica e preditiva.
* **Segurança e Sigilo:** Criptografia ponta a ponta e aderência estrita às resoluções do CFM (Conselho Federal de Medicina) e CFP (Conselho Federal de Psicologia) relativas à segurança do prontuário eletrônico.
