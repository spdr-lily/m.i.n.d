# Project: M.I.N.D (Mental Intelligence & Network Data)
**Clinical Decision Support System (CDSS) for Mental Health**
*The conceptual decomposition connects human cognition (Mental Intelligence) to an infrastructure of interconnected data (Network Data).*

This document presents the updated specification and scope of the intersection between **Data Science** and **Psychiatry/Clinical Psychology**. It is designed to optimize clinical workflows, mitigate diagnostic errors in mental health, and structure a rigorous, evidence-based probabilistic modeling architecture.

---

## 1. Context & Motivation
The diagnostic process in mental health faces severe, structural challenges that directly impact patient outcomes and healthcare ecosystems:
* **High Diagnostic Error Rates:** Several disorders present overlapping symptoms (comorbidities and differential manifestations), leading to ineffective initial treatments and trial-and-error pharmacological prescriptions.
* **Access and Cost Barriers:** Comprehensive neuropsychological evaluations are highly expensive, frequently capped by private insurance, and subject to extensive wait times in public healthcare systems (e.g., NHS, Medicaid).
* **Diagnostic Delay (Latency):** Prolonged timelines in identifying the correct underlying disorder delay the initiation of targeted, effective interventions, extending patient suffering and increasing longitudinal healthcare costs.

## 2. Project Scope & Objectives (MVP Focus)
The project consists of developing a **Clinical Decision Support System (CDSS)** tailored exclusively for certified mental health professionals (psychologists, psychiatrists, and neurologists).

**Core Objective:**
To leverage *Machine Learning* algorithms, applied statistics, and probabilistic modeling to calculate the statistical likelihood of specific diagnoses based on the unified criteria of the **ICD-11 (International Classification of Diseases)** and the **DSM-5-TR (Diagnostic and Statistical Manual of Mental Disorders)**, serving as a complementary tool to the clinician's sovereign judgment.

---

## 3. Core System Features

### Phase 1: Minimum Viable Product (MVP)
* **Unified Probabilistic Calculation (ICD-11 & DSM-5-TR):** Cross-referencing structured clinical intake data against a verified knowledge base to output the statistical probability of differential diagnoses and comorbidity clusters.
* **Clinical Constraint Mapping (Logical Trees):** Automated execution of operational, duration, and exclusion criteria stipulated by the DSM-5-TR (e.g., minimum duration of symptoms, ruling out substance-induced states).
* **Structured Clinical Data Ingestion:** Digitized standardized intake forms based on validated cross-cutting symptom measures (such as the DSM-5-TR Level 1 and Level 2 measures) and binary/Likert-scale checklists filled out by the professional.
* **Longitudinal Patient Tracker:** Interactive dashboards allowing clinicians to graphically monitor symptom trajectory, severity fluctuations, and patient treatment response over time.

### Phase 2: Post-Validation Expansion
* **Multimodal Clinical Data Ingestion:** Deploying Natural Language Processing (NLP) pipelines for Clinical Entity Recognition (NER) to extract psychiatric features from unstructured clinical notes, referral letters, and previous medical history.
* **Advanced Phenotypic Profiling:** Screening deep epidemiological data to identify patterns of chronicity or remission. *(Active pharmacological prescription or intervention support has been decommissioned from the initial scope due to high-risk SaMD regulatory barriers).*

---

## 4. Technological Architecture & Data Engineering (Stack)

### 1. Storage & Relational Data Architecture (SQL)
A robust relational database schema engineered to map clinical entities, ensuring strict referential integrity across taxonomies and symptoms:
* **Symptom & Diagnosis Registry:** Standardized cataloging of ICD-11 alphanumeric codes and DSM-5-TR diagnostic criteria.
* **Operational Criteria Controls:** Database parameters tracking time constraints (months/weeks) and deterministic logical elimination rules.
* **Crosswalk Mapping Tables:** Equivalence matrices and correlation coefficients mapping ICD-11 criteria to DSM-5-TR constructs using concept unique identifiers (CUIs) derived from the **UMLS (Unified Medical Language System)**.

### 2. Statistical Modeling & Artificial Intelligence (Python / R)
* **R (Statistical Validation):** In-depth Exploratory Data Analysis (EDA), hypothesis testing, psychometric internal consistency validation (Cronbach's Alpha), and Latent Class Analysis (LCA) leveraging clinical microdata.
* **Python (Probabilistic Engine & ML):** Execution of data processing pipelines and implementation of **Bayesian Networks** or logical inference engines to calculate conditional probabilities ($P(\text{Diagnosis} \mid \text{Symptoms})$) based on active clinical features.

### 3. Metrics & Dashboards (DAX / Power BI)
* Creation of interactive clinical performance indicators. Utilizing advanced DAX expressions to compute percentage variances in symptom severity across clinical sessions and therapy adherence metrics.

---

## 5. Data Sources & Scientific References

### Official Diagnostic Taxonomies
* **ICD-11:** *Chapter 06 - Mental, behavioural or neurodevelopmental disorders*. World Health Organization (WHO). [Official Browser](https://icd.who.int/en).
* **DSM-5-TR:** *Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision*. American Psychiatric Association (APA). [Official Library](https://dsm.psychiatryonline.org).
* **DSM-5-TR Online Assessment Measures:** Level 1 and Level 2 Cross-Cutting Symptom Measures utilized as the gold standard for structured user input data. [Official Resource](https://www.psychiatry.org/psychiatrists/practice/dsm/educational-resources/assessment-measures).

### De-identified Microdata Repositories for Model Training
* **MIMIC-IV (Medical Information Mart for Intensive Care):** De-identified Electronic Health Records (EHR) containing real clinical histories, ICU stays, and ICD-coded diagnoses. PhysioNet / MIT Laboratory for Computational Physiology. [Official Repository](https://physionet.org/content/mimiciv/).
* **UCI Machine Learning Repository:** Tabular datasets and consolidated clinical surveys mapping mental health metrics, psychological stressors, and behavioral variables. [Official Portal](https://archive.ics.uci.edu/).
* **UMLS Metathesaurus:** The U.S. National Library of Medicine (NLM) integration engine, utilized for deterministic crosswalks and biomedical concept alignment. [Official Engine](https://www.nlm.nih.gov/research/umls/index.html).

### Epidemiological Benchmarks (Prior Probability Calibration)
* **Global Burden of Disease Study (GBD):** Global and regional incidence, prevalence, and Years Lived with Disability (YLDs) metrics for Mood, Anxiety, and Psychotic disorders. Institute for Health Metrics and Evaluation (IHME), University of Washington. [Official Data](https://www.healthdata.org/gbd).
* **National Survey on Drug Use and Health (NSDUH) / CDC Data:** Populates foundational baseline statistics (*a priori* probabilities) for behavioral health models.

---

## 6. Ethics, Security, and Compliance
* **Human-in-the-Loop (Clinician Sovereignty):** The system operates strictly as a statistical validation assistant. Final clinical methodology and diagnostic determination remain 100% under the legal and professional responsibility of the licensed healthcare practitioner.
* **HIPAA & GDPR Compliance:** Absolute and irreversible pseudonymization and anonymization of Protected Health Information (PHI) under HIPAA Safe Harbor methods and GDPR Article 9 requirements. Personally Identifiable Information (PII) is completely decoupled from the analytical processing layer.
* **Information Security & Cryptography:** End-to-end encryption (AES-256 for data at rest, TLS 1.3 for data in transit) aligning with medical record security standards and professional confidentiality boards.

---

## 7. Next Steps (Practical Action Plan)
1. **Initial Data Schema Implementation (SQL):** Build the relational schema mapping dependencies between ICD-11 and DSM-5-TR, scoped specifically for the Mood Disorders module (Depression & Bipolarity) for the MVP.
2. **Data Ingestion & Synthesis (Data Sourcing):** Ingest clinical microdata from validated open-source registries (UCI/UMLS) or engineer a rigorous synthetic population dataset modeled after the manuals' exact cutting scores.
3. **Probabilistic Engine Core Development (Python):** Program the deterministic DSM-5-TR exclusion criteria trees and the underlying conditional probability calculations.
4. **Clinical Calibration:** Run validation pilots comparing the model's probabilistic outputs against blind historical case reviews by senior clinicians to tune variable weights.