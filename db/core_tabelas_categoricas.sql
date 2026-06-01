-- Table: core.tabelas_categoricas

-- DROP TABLE IF EXISTS core.tabelas_categoricas;

CREATE TABLE IF NOT EXISTS core.tabelas_categoricas
(
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS core.tabelas_categoricas
    OWNER to postgres;

-- sexo biológico

CREATE TABLE IF NOT EXISTS core.sex_types (
    sex_type_id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(100) NOT NULL
);

-- identidade de gênero 

CREATE TABLE IF NOT EXISTS core.gender_identities (
    gender_identity_id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    description VARCHAR(100) NOT NULL
);

-- escolaridade

CREATE TABLE IF NOT EXISTS core.education_levels (
    education_level_id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    description VARCHAR(100) NOT NULL
);

-- etnia

CREATE TABLE IF NOT EXISTS core.ethnicities (
    ethnicity_id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    description VARCHAR(100) NOT NULL
);

