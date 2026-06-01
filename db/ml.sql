-- SCHEMA: ml

-- DROP SCHEMA IF EXISTS ml ;

CREATE SCHEMA IF NOT EXISTS ml
    AUTHORIZATION postgres;

-- CAMADA PROBABILÍSTICA E ML

CREATE TABLE IF NOT EXISTS ml.probabilistic_feature_weights (
    weight_id SERIAL PRIMARY KEY,

    disorder_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,

    feature_weight NUMERIC(8,6) NOT NULL,
    confidence_score NUMERIC(6,4),

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (disorder_id)
        REFERENCES diagnostic.disorders(disorder_id)
        ON DELETE CASCADE,

    FOREIGN KEY (symptom_id)
        REFERENCES diagnostic.symptoms(symptom_id)
        ON DELETE CASCADE
);

-- RELAÇÕES BAYESIANAS

CREATE TABLE IF NOT EXISTS ml.bayesian_relationships (
    bayesian_relationship_id SERIAL PRIMARY KEY,

    disorder_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,

    prior_probability NUMERIC(8,6),
    posterior_probability NUMERIC(8,6),
    likelihood_ratio NUMERIC(8,6),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (disorder_id)
        REFERENCES diagnostic.disorders(disorder_id)
        ON DELETE CASCADE,

    FOREIGN KEY (symptom_id)
        REFERENCES diagnostic.symptoms(symptom_id)
        ON DELETE CASCADE
);
