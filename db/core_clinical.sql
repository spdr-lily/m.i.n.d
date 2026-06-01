-- SCHEMA: clinical

-- DROP SCHEMA IF EXISTS clinical ;

CREATE SCHEMA IF NOT EXISTS clinical
    AUTHORIZATION postgres;

-- perfil clínico do paciente

CREATE TABLE IF NOT EXISTS clinical.patient_profile (
    profile_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    patient_uuid UUID NOT NULL UNIQUE,

    birth_date DATE,

    sex_type_id INTEGER,
    gender_identity_id INTEGER,
    education_level_id INTEGER,
    ethnicity_id INTEGER,

    marital_status VARCHAR(50),
    occupation VARCHAR(120),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_uuid)
        REFERENCES security.patient_identity(patient_uuid)
        ON DELETE CASCADE,

    FOREIGN KEY (sex_type_id)
        REFERENCES core.sex_types(sex_type_id),

    FOREIGN KEY (gender_identity_id)
        REFERENCES core.gender_identities(gender_identity_id),

    FOREIGN KEY (education_level_id)
        REFERENCES core.education_levels(education_level_id),

    FOREIGN KEY (ethnicity_id)
        REFERENCES core.ethnicities(ethnicity_id)
);

-- profissionais de saúde 

CREATE TABLE IF NOT EXISTS clinical.healthcare_professionals (
    professional_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    full_name VARCHAR(255) NOT NULL,
    professional_license VARCHAR(100),
    specialty VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CONSULTA CLÍNICA

CREATE TABLE IF NOT EXISTS clinical.clinical_consultation (
    consultation_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_uuid UUID NOT NULL,
    professional_uuid UUID,

    consultation_date TIMESTAMP NOT NULL,
    consultation_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (profile_uuid)
        REFERENCES clinical.patient_profile(profile_uuid)
        ON DELETE CASCADE,

    FOREIGN KEY (professional_uuid)
        REFERENCES clinical.healthcare_professionals(professional_uuid)
        ON DELETE SET NULL
);

-- EPISÓDIOS CLÍNICOS 

CREATE TABLE IF NOT EXISTS clinical.clinical_episode (
    episode_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_uuid UUID NOT NULL,

    episode_start TIMESTAMP,
    episode_end TIMESTAMP,

    episode_type VARCHAR(100),
    clinical_description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (profile_uuid)
        REFERENCES clinical.patient_profile(profile_uuid)
        ON DELETE CASCADE
);
