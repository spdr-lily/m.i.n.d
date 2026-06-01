-- SCHEMA: diagnostic

-- DROP SCHEMA IF EXISTS diagnostic ;

CREATE SCHEMA IF NOT EXISTS diagnostic
    AUTHORIZATION postgres;

-- SINTOMAS

CREATE TABLE IF NOT EXISTS diagnostic.symptoms (
    symptom_id SERIAL PRIMARY KEY,

    symptom_name VARCHAR(255) UNIQUE NOT NULL,
    symptom_description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRANSTORNOS

CREATE TABLE IF NOT EXISTS diagnostic.disorders (
    disorder_id SERIAL PRIMARY KEY,

    cid_code VARCHAR(20),
    dsm_code VARCHAR(20),

    disorder_name VARCHAR(255) UNIQUE NOT NULL,
    disorder_description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CRITÉRIOS DIAGNÓSTICOS 

CREATE TABLE IF NOT EXISTS diagnostic.diagnostic_criteria (
    criteria_id SERIAL PRIMARY KEY,

    disorder_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,

    required_presence BOOLEAN DEFAULT TRUE,
    minimum_duration_days INTEGER,

    clinical_notes TEXT,

    FOREIGN KEY (disorder_id)
        REFERENCES diagnostic.disorders(disorder_id)
        ON DELETE CASCADE,

    FOREIGN KEY (symptom_id)
        REFERENCES diagnostic.symptoms(symptom_id)
        ON DELETE CASCADE
);

-- RELAÇÕES DIAGNÓSTICAS

CREATE TABLE IF NOT EXISTS diagnostic.diagnosis_relationships (
    relationship_id SERIAL PRIMARY KEY,

    source_disorder_id INTEGER NOT NULL,
    target_disorder_id INTEGER NOT NULL,

    relationship_type VARCHAR(50),
    relationship_weight NUMERIC(6,4),

    clinical_description TEXT,

    FOREIGN KEY (source_disorder_id)
        REFERENCES diagnostic.disorders(disorder_id)
        ON DELETE CASCADE,

    FOREIGN KEY (target_disorder_id)
        REFERENCES diagnostic.disorders(disorder_id)
        ON DELETE CASCADE
);
