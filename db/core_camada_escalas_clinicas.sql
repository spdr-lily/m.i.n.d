-- SCHEMA: diagnostic

-- DROP SCHEMA IF EXISTS diagnostic ;

CREATE SCHEMA IF NOT EXISTS diagnostic
    AUTHORIZATION postgres;

-- CAMADA DE ESCALA CLÍNICAS

CREATE TABLE IF NOT EXISTS diagnostic.assessment_scales (
    scale_id SERIAL PRIMARY KEY,

    scale_name VARCHAR(255) UNIQUE NOT NULL,
    scale_description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- QUESTÕES DE ESCALAS

CREATE TABLE IF NOT EXISTS diagnostic.scale_questions (
    question_id SERIAL PRIMARY KEY,

    scale_id INTEGER NOT NULL,

    question_text TEXT NOT NULL,
    question_order INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scale_id)
        REFERENCES diagnostic.assessment_scales(scale_id)
        ON DELETE CASCADE
);

-- RESPOSTAS DE ESCALAS

CREATE TABLE IF NOT EXISTS clinical.scale_responses (
    response_id SERIAL PRIMARY KEY,

    consultation_uuid UUID NOT NULL,
    question_id INTEGER NOT NULL,

    response_value NUMERIC(10,2),
    response_text TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (consultation_uuid)
        REFERENCES clinical.clinical_consultation(consultation_uuid)
        ON DELETE CASCADE,

    FOREIGN KEY (question_id)
        REFERENCES diagnostic.scale_questions(question_id)
        ON DELETE CASCADE
);
