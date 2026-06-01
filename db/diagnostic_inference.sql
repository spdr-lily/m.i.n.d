-- SCHEMA: diagnostic

-- DROP SCHEMA IF EXISTS diagnostic ;

CREATE SCHEMA IF NOT EXISTS diagnostic
    AUTHORIZATION postgres;

-- inferência diagnóstica

CREATE TABLE IF NOT EXISTS diagnostic.diagnostic_inference (
    inference_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    consultation_uuid UUID NOT NULL,
    disorder_id INTEGER NOT NULL,

    inference_probability NUMERIC(8,6),
    confidence_level NUMERIC(6,4),

    generated_by_model VARCHAR(120),
    model_version VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (consultation_uuid)
        REFERENCES clinical.clinical_consultation(consultation_uuid)
        ON DELETE CASCADE,

    FOREIGN KEY (disorder_id)
        REFERENCES diagnostic.disorders(disorder_id)
        ON DELETE CASCADE
);
