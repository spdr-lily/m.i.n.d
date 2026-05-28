-- EXTENÇÃO
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

CREATE TABLE patient_profile(
	patient_uuid UUID PRIMARY KEY,

	birth_date DATE,

	biological_sex VARCHAR(30),

	gender_identity VARCHAR(50),

	ethnicity VARCHAR(50),

	education_level VARCHAR(100),

	matital_status VARCHAR(50),

	occupation TEXT,

	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (patient_uuid)
		REFERENCES patient_identity(patient_uuid)
		ON DELETE CASCADE
);


