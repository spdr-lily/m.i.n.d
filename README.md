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

## 3. Funcionalidades Principais do Sistema

### Fase 1: Mínimo Produto Viável (MVP)
* **Cálculo Probabilístico Unificado (CID-11 & DSM-5-TR):** Cruzamento de dados de entrada estruturados com uma base de conhecimento para apontar a probabilidade estatística de diferentes laudos e comorbidades.
* **Mapeamento Clínico de Restrições (Árvores Lógicas):** Aplicação automatizada dos critérios operacionais, temporais e de exclusão estipulados pelo DSM-5-TR (ex: tempo mínimo de persistência de sintomas e regras eliminatórias).
* **Ingestão de Dados Clínicos Estruturados:** Formulários digitais padronizados baseados em escalas transversais de sintomas (como as do próprio DSM-5-TR) e checklists binários/Likert preenchidos pelo profissional.
* **Painel de Evolução Longitudinal:** Painéis interativos para o profissional acompanhar graficamente a distribuição de sintomas ao longo do tempo e o histórico de resposta do paciente.

### Fase 2: Expansão Pós-Validação
* **Ingestão de Dados Multimodais:** Processamento de Linguagem Natural (NLP) para extração de entidades clínicas a partir de notas textuais livres e relatórios médicos anteriores.
* **Mapeamento de Perfis Fenotípicos Avançados:** Triagem refinada de dados epidemiológicos para identificar padrões de cronicidade ou remissão. *(A recomendação ou intervenção farmacológica ativa foi descontinuada do escopo inicial devido a restrições regulatórias de alto risco).*

---

## 4. Arquitetura Tecnológica e Engenharia de Dados (Stack)

### 1. Armazenamento e Estruturação de Dados (SQL)
Criação de um banco de dados relacional robusto estruturado em tabelas de entidades clínicas, garantindo integridade referencial para mapear sintomas e taxonomias:
* **Tabela de Sintomas e Diagnósticos:** Catalogação padronizada dos códigos da CID-11 e do DSM-5-TR.
* **Tabela de Critérios Operacionais:** Parâmetros de controle de tempo (meses/semanas) e regras lógicas do DSM-5-TR.
* **Tabela de Mapeamento (Crosswalks):** Equivalência e coeficientes de correlação entre sintomas da CID-11 e constructos do DSM-5-TR utilizando chaves conceituais baseadas no padrão UMLS (*Unified Medical Language System*).

### 2. Modelagem Estatística e Inteligência Artificial (Python / R)
* **R (Validação Estatística):** Análise exploratória profunda (EDA), testes de hipóteses, validação de consistência interna das escalas (Alfa de Cronbach) e Análise de Classes Latentes (LCA) sobre microdados de estudos de caso.
* **Python (Cálculo Probabilístico e ML):** Construção das pipelines de processamento de dados e desenvolvimento de modelos de **Redes Bayesianas** ou inferência lógica para calcular probabilidades condicionais baseadas nos sintomas ativados.

### 3. Métricas e Dashboards (DAX / Power BI)
* Criação de indicadores de performance clínica e painéis visuais interativos. Utilização de fórmulas DAX avançadas para calcular a variação percentual de severidade de sintomas entre consultas e taxas de adesão terapêutica.

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

---

## 7. Próximos Passos Recomendados (Plano de Ação Prático)
1. **Modelagem de Dados Inicial (SQL):** Implementar o schema relacional contendo o mapeamento de dependências entre CID-11 e DSM-5-TR focado no primeiro grupo de transtornos do MVP.
2. **Curadoria e Simulação (Data Sourcing):** Ingestão de microdados das fontes validadas (UCI/UMLS) ou estruturação de uma base sintética rigorosa baseada nos critérios de corte das duas taxonomias.
3. **Desenvolvimento do MVP (Python):** Codificação da árvore lógica de restrições do DSM e do modelo de probabilidades condicionais para o módulo de Transtornos do Humor (Depressão e Bipolaridade).
4. **Calibragem Clínica:** Validação dos outputs probabilísticos do modelo junto a profissionais da área para ajuste fino dos pesos das variáveis.
