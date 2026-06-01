-- M.I.N.D - Initial Database Schema
-- This is a reference SQL script showing the basic structure
-- Actual migrations are managed by Alembic in alembic/versions/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Patient Profile Table
-- LGPD Compliance: Contains demographics only, no PII
CREATE TABLE IF NOT EXISTS patient_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    biological_sex VARCHAR(10) NOT NULL,
    gender_identity VARCHAR(50),
    birth_date DATE NOT NULL,
    education_level VARCHAR(50),
    marital_status VARCHAR(50),
    occupation VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_sex CHECK (biological_sex IN ('Male', 'Female', 'Other'))
);

-- Healthcare Professionals Registry
-- LGPD Compliance: Clinician credentials and licensing info
CREATE TABLE IF NOT EXISTS healthcare_professionals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) NOT NULL UNIQUE,
    professional_type VARCHAR(50) NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Disorders Registry
-- DSM-5-TR and ICD-11 codes mapping
CREATE TABLE IF NOT EXISTS disorders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    dsm_code VARCHAR(20) UNIQUE,
    icd_code VARCHAR(20) UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Symptoms Catalog
-- DSM-5-TR symptom definitions
CREATE TABLE IF NOT EXISTS symptoms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    dsm_reference VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Diagnostic Criteria
-- Rules for combining symptoms into diagnoses
CREATE TABLE IF NOT EXISTS diagnostic_criteria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disorder_id UUID NOT NULL REFERENCES disorders(id),
    description TEXT,
    minimum_symptom_count INT,
    duration_days INT,
    is_required BOOLEAN DEFAULT false,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Consultations
-- Patient-clinician consultations
CREATE TABLE IF NOT EXISTS clinical_consultation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient_profile(id),
    professional_id UUID NOT NULL REFERENCES healthcare_professionals(id),
    consultation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    consultation_type VARCHAR(50),
    clinical_notes TEXT,
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Episodes
-- Longitudinal tracking of patient episodes
CREATE TABLE IF NOT EXISTS clinical_episode (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient_profile(id),
    episode_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    severity_score INT CHECK (severity_score BETWEEN 0 AND 10),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Symptom Assessments
-- Patient symptom assessments in consultations
CREATE TABLE IF NOT EXISTS symptom_assessment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_id UUID NOT NULL REFERENCES clinical_consultation(id),
    symptom_id UUID NOT NULL REFERENCES symptoms(id),
    severity_score INT CHECK (severity_score BETWEEN 0 AND 10),
    duration_days INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Diagnosis Results
-- Probabilistic diagnosis calculations
CREATE TABLE IF NOT EXISTS diagnosis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_id UUID NOT NULL REFERENCES clinical_consultation(id),
    disorder_id UUID NOT NULL REFERENCES disorders(id),
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    is_differential BOOLEAN DEFAULT false,
    clinician_validated BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessment Scales
-- Psychometric instruments (PHQ-9, GAD-7, etc.)
CREATE TABLE IF NOT EXISTS assessment_scales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    total_items INT,
    score_range_min INT,
    score_range_max INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scale Assessments
-- Patient scale assessments and scores
CREATE TABLE IF NOT EXISTS scale_assessment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consultation_id UUID NOT NULL REFERENCES clinical_consultation(id),
    scale_id UUID NOT NULL REFERENCES assessment_scales(id),
    raw_score INT,
    interpretation VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Diagnosis Relationships
-- Comorbidity and differential diagnosis rules
CREATE TABLE IF NOT EXISTS diagnosis_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disorder_a_id UUID NOT NULL REFERENCES disorders(id),
    disorder_b_id UUID NOT NULL REFERENCES disorders(id),
    relationship_type VARCHAR(50) NOT NULL,  -- 'comorbidity', 'differential', 'exclusion'
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_relationship CHECK (disorder_a_id != disorder_b_id)
);

-- Create indexes for common queries
CREATE INDEX idx_patient_profile_created ON patient_profile(created_at);
CREATE INDEX idx_clinical_consultation_patient ON clinical_consultation(patient_id);
CREATE INDEX idx_clinical_consultation_professional ON clinical_consultation(professional_id);
CREATE INDEX idx_clinical_episode_patient ON clinical_episode(patient_id);
CREATE INDEX idx_diagnosis_consultation ON diagnosis(consultation_id);
CREATE INDEX idx_disorder_codes ON disorders(dsm_code, icd_code);
CREATE INDEX idx_symptom_assessment_consultation ON symptom_assessment(consultation_id);
CREATE INDEX idx_scale_assessment_consultation ON scale_assessment(consultation_id);

-- Add audit trigger for tracking changes
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply audit trigger to all tables
CREATE TRIGGER update_patient_profile_timestamp BEFORE UPDATE ON patient_profile
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_disorders_timestamp BEFORE UPDATE ON disorders
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_symptoms_timestamp BEFORE UPDATE ON symptoms
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_clinical_consultation_timestamp BEFORE UPDATE ON clinical_consultation
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_clinical_episode_timestamp BEFORE UPDATE ON clinical_episode
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_diagnosis_timestamp BEFORE UPDATE ON diagnosis
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Initial seed data (example)
INSERT INTO disorders (name, dsm_code, icd_code, description)
VALUES
    ('Major Depressive Disorder', 'F32.x', '6A70.y', 'Persistent depressed mood'),
    ('Bipolar I Disorder', 'F31.x', '6A60.x', 'Alternating manic and depressive episodes'),
    ('Generalized Anxiety Disorder', 'F41.1', '6D02', 'Excessive worry')
ON CONFLICT (dsm_code) DO NOTHING;
