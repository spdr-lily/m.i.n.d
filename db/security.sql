-- SCHEMA: security

-- DROP SCHEMA IF EXISTS security ;

CREATE SCHEMA IF NOT EXISTS security
    AUTHORIZATION postgres;

-- identidade3 protegida do paciente

CREATE TABLE IF NOT EXISTS security.patient_identity (
    patient_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    full_name VARCHAR(255) NOT NULL,
    cpf_hash VARCHAR(255),
    email_hash VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
