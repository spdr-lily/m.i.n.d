-- SCHEMA: clinical

-- DROP SCHEMA IF EXISTS clinical ;

CREATE SCHEMA IF NOT EXISTS clinical
    AUTHORIZATION postgres;

-- OBSERVAÇÕES CLÍNICAS

CREATE TABLE IF NOT EXISTS clinical.symptom_observation (
    observation_id SERIAL PRIMARY KEY,

    consultation_uuid UUID NOT NULL,
    symptom_id INTEGER NOT NULL,

    intensity NUMERIC(5,2),
    frequency VARCHAR(50),
    duration_days INTEGER,

    clinical_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (consultation_uuid)
        REFERENCES clinical.clinical_consultation(consultation_uuid)
        ON DELETE CASCADE,

    FOREIGN KEY (symptom_id)
        REFERENCES diagnostic.symptoms(symptom_id)
        ON DELETE CASCADE
);
