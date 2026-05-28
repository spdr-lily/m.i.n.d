-- EXTENSÃO
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- CAMADA DE IDENTIDADE (LGPD)
--

CREATE TABLE patient_identity(
	patient_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	full_name TEXT NOT NULL,
	cpf_hash TEXT UNIQUE NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PERFIL ANALÍTICO DO PACIENTE
--

CREATE TABLE patient_profile (
    patient_uuid UUID PRIMARY KEY,
    birth_date DATE,
    biological_sex VARCHAR(20),
    gender_identity VARCHAR(50),
    ethnicity VARCHAR(50),
    education_level VARCHAR(50),
    marital_status VARCHAR(50),
    occupation VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_uuid)
        REFERENCES patient_identity(patient_uuid)
        ON DELETE CASCADE
);

--PROFISSIONAIS DE SAÚDE
--

CREATE TABLE healthcare_professionals (
    professional_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255),
    professional_type VARCHAR(100),
    license_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CONSULTAS CLÍNICAS
--

CREATE TABLE clinical_consultation (
    consultation_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_uuid UUID NOT NULL,
    professional_uuid UUID,
    consultation_date TIMESTAMP NOT NULL,
    consultation_type VARCHAR(50),
    clinical_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_uuid)
        REFERENCES patient_identity(patient_uuid)
        ON DELETE CASCADE,
    FOREIGN KEY (professional_uuid)
        REFERENCES healthcare_professionals(professional_uuid)
);

-- EPISÓDIOS CLÍNICOS 
--

CREATE TABLE clinical_episode(
	episode_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	patient_uuid UUID NOT NULL,
	episode_type VARCHAR(100),
	start_date DATE,
	end_date DATE,
	severity_score NUMERIC(5,2),
	status VARCHAR(50),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (patient_uuid)
		REFERENCES patient_identity(patient_uuid)
		ON DELETE CASCADE
);

-- CATÁLOGO DE SINTOMAS
--

CREATE TABLE symptoms(
	symptom_id VARCHAR(50) PRIMARY KEY,
	symptom_name VARCHAR(255) NOT NULL,
	category VARCHAR(100),
	description TEXT,
	dsm_reference TEXT,
	cid_reference TEXT,
	active BOOLEAN DEFAULT TRUE,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRANSTORNOS / DIAGNÓSTICOS
--

CREATE TABLE disorders (
    disorder_id SERIAL PRIMARY KEY,
    disorder_name VARCHAR(255) NOT NULL,
    dsm_code VARCHAR(50),
    cid11_code VARCHAR(50),
    disorder_category VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    version_tag VARCHAR(50),
    valid_from DATE,
    valid_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CRITÉRIOS DIAGNÓSTICOS DSM/CID
--

CREATE TABLE diagnostic_criteria(
	criteria_id SERIAL PRIMARY KEY,
	disorder_id INTEGER NOT NULL,
	symptom_id VARCHAR(50),
	is_required BOOLEAN DEFAULT FALSE,
	minimum_symptom_count INTEGER,
	minimum_duration_days INTEGER,
	exclusionary BOOLEAN DEFAULT FALSE,
	logical_operator VARCHAR(10),
	weight NUMERIC(6,4),
	criteria_group VARCHAR(50),
	valid_from DATE,
	valid_to DATE,
	FOREIGN KEY (disorder_id)
		REFERENCES disorders(disorder_id)
		ON DELETE CASCADE,
	FOREIGN KEY (symptom_id)
		REFERENCES symptoms(symptom_id)
		ON DELETE CASCADE
);

-- RELAÇÕES ENTRE DIAGNÓSTICOS
--

CREATE TABLE diagnosis_relationships(
	relationship_id SERIAL PRIMARY KEY,
	source_disorder_id INTEGER NOT NULL,
	target_disorder_id INTEGER NOT NULL,
	relationship_type VARCHAR(50),
	relationship_weight NUMERIC(6,4),
	clinical_description TEXT,
	FOREIGN KEY (source_disorder_id)
		REFERENCES disorders(disorder_id)
		ON DELETE CASCADE,
	FOREIGN KEY (target_disorder_id)
		REFERENCES disorders(disorder_id)
		ON DELETE CASCADE
);

-- ESCALAS PSICOMÉTRICAS
--

CREATE TABLE assessment_scales(
	scale_id SERIAL PRIMARY KEY,
	scale_name VARCHAR(255),
	version VARCHAR(50),
	description TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scale_questions (
    question_id SERIAL PRIMARY KEY,
    scale_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_code VARCHAR(100),
    question_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scale_id)
        REFERENCES assessment_scales(scale_id)
        ON DELETE CASCADE
);

-- RESPOSTAS DAS ESCALAS
--

CREATE TABLE scale_responses(
	response_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	consultation_uuid UUID NOT NULL,
	question_id INTEGER NOT NULL,
	response_value INTEGER,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (consultation_uuid)
		REFERENCES clinical_consultation(consultation_uuid)
		ON DELETE CASCADE,
	FOREIGN KEY (question_id)
		REFERENCES scale_questions(question_id)
		ON DELETE CASCADE
);

-- OBSERVAÇÃO DE SINTOMAS 
--

CREATE TABLE symptom_observation(
	observation_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	consultation_uuid UUID NOT NULL,
	symptom_id VARCHAR(50) NOT NULL,
	severity_score INTEGER,
	frequency_score INTEGER,
	functional_impact_score INTEGER,
	duration_days INTEGER,
	observed_by_professional BOOLEAN DEFAULT FALSE,
	self_reported BOOLEAN DEFAULT TRUE,
	confidence_level NUMERIC(5,2),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (consultation_uuid)
		REFERENCES clinical_consultation(consultation_uuid)
		ON DELETE CASCADE,
	FOREIGN KEY (symptom_id)
		REFERENCES symptoms(symptom_id)
		ON DELETE CASCADE
);

-- PESOS PROBABILÍSTICOS
--

CREATE TABLE probabilistic_feature_weights (
    weight_id SERIAL PRIMARY KEY,
    disorder_id INTEGER NOT NULL,
    symptom_id VARCHAR(50) NOT NULL,
    prior_weight NUMERIC(8,6),
    conditional_weight NUMERIC(8,6),
    evidence_strength VARCHAR(100),
    source_reference TEXT,
    version_tag VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (disorder_id)
        REFERENCES disorders(disorder_id)
        ON DELETE CASCADE,
    FOREIGN KEY (symptom_id)
        REFERENCES symptoms(symptom_id)
        ON DELETE CASCADE
);

-- INFERÊNCIA DIAGNÓSTICA
--

CREATE TABLE diagnostic_inference (
    inference_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_uuid UUID NOT NULL,
    disorder_id INTEGER NOT NULL,
    raw_score NUMERIC(10,4),
    normalized_probability NUMERIC(10,4),
    activated_rules JSONB,
    excluded_rules JSONB,
    inference_trace JSONB,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_uuid)
        REFERENCES clinical_consultation(consultation_uuid)
        ON DELETE CASCADE,
    FOREIGN KEY (disorder_id)
        REFERENCES disorders(disorder_id)
        ON DELETE CASCADE
);

-- RELAÇÕES BAYESIANAS
--

CREATE TABLE bayesian_relationships (
    relationship_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_node VARCHAR(100),
    target_node VARCHAR(100),
    conditional_probability NUMERIC(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AUDITORIA E RASTREABILIDADE
--

CREATE TABLE audit_logs (
    audit_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_name VARCHAR(255),
    entity_id VARCHAR(255),
    operation_type VARCHAR(50),
    changed_by VARCHAR(255),
    change_payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ÍNDICES IMPORTANTES
--

CREATE INDEX idx_symptom_observation_consultation
ON symptom_observation(consultation_uuid);
CREATE INDEX idx_diagnostic_inference_consultation
ON diagnostic_inference(consultation_uuid);
CREATE INDEX idx_probabilistic_weights_disorder
ON probabilistic_feature_weights(disorder_id);
CREATE INDEX idx_probabilistic_weights_symptom
ON probabilistic_feature_weights(symptom_id);
CREATE INDEX idx_scale_responses_consultation
ON scale_responses(consultation_uuid);
CREATE INDEX idx_scale_responses_question
ON scale_responses(question_id);	


