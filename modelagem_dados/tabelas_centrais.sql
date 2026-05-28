-- 1. CAMADA DE ACESSO E LGPD (Anonimização de Dados do Paciente)
--

CREATE TABLE ID_PACIENTE(
	ID_PACIENTE_CRYPTO VARCHAR(255) PRIMARY KEY,
	NOME_COMPLETO VARCHAR(255) NOT NULL,
	CPF VARCHAR(14) UNIQUE NOT NULL
);

CREATE TABLE PACIENTE_ANALISE(
	ID_PACIENTE_ANALISE VARCHAR(255),
	ID_PACIENTE_CRYPTO VARCHAR(255) NOT NULL,
	NASCIMENTO TIMESTAMP NOT NULL,
	GENERO_BIO VARCHAR(50) NOT NULL,
	DADOS_EPIDEMIOLOGICOS_AGREGADOS TEXT,
	CONSTRAINT fk_paciente_lgpd FOREIGN KEY (id_paciente_crypto) 
        REFERENCES id_paciente(id_paciente_crypto) ON DELETE RESTRICT
);

-- 
-- 2. CAMADA PROFISSIONAL E CLÍNICA

CREATE TABLE PROFISSIONAL(
	ID_PROFISSIONAL SERIAL PRIMARY KEY,
	REGISTRO_CONSELHO VARCHAR(50) UNIQUE NOT NULL,
	ESPECIALIDADE VARCHAR(100) NOT NULL,
	NOME_PROFISSIONAL VARCHAR(255) NOT NULL
);

CREATE TABLE CONSULTA_SESSAO(
	ID_CONSULTA SERIAL PRIMARY KEY,
	ID_PACIENTE_ANALISE VARCHAR(255) NOT NULL,
	ID_PROFISSIONAL INTEGER NOT NULL,
	DATA_CONSULTA TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	NOTAS_CLINICAS_LIVRES TEXT,
	CONSTRAINT FK_CONSULTA_PACIENTE FOREIGN KEY(ID_PACIENTE_ANALISE)
		REFERENCES PACIENTE_ANALISE(ID_PACIENTE_ANALISE) ON DELETE CASCADE,
	CONSTRAINT FK_CONSULTA_PROFISSIONAL FOREIGN KEY(ID_PROFISSIONAL)
		REFERENCES PROFISSIONAL(ID_PROFISSIONAL) ON DELETE RESTRICT
);


CREATE TABLE TRATAMENTO_MEDICAMENTOSO (
    ID_PRESCRICAO TEXT PRIMARY KEY,
    ID_CONSULTA INTEGER NOT NULL,
    SUBSTANCIA_ATIVA VARCHAR(255) NOT NULL,
    STATUS_EFICACIA VARCHAR(100),
    DATA_INICIO TIMESTAMP NOT NULL,
    DATA_FIM TIMESTAMP,
    CONSTRAINT FK_TRATAMENTO_CONSULTA FOREIGN KEY (ID_CONSULTA) 
        REFERENCES CONSULTA_SESSAO(ID_CONSULTA) ON DELETE CASCADE
);

-- 3. CAMADA DE TAXONOMIA E BASE DE CONHECIMENTO (CID / DSM / UMLS)
-- 

CREATE TABLE CATALOGO_DIAGNOSTICO (
    ID_DIAGNOSTICO SERIAL PRIMARY KEY,
    CODIGO_CLASSIFICACAO VARCHAR(50) NOT NULL, -- Ex: F32.9 (CID-10) ou 296.20 (DSM)
    TIPO_SISTEMA VARCHAR(20) NOT NULL,        -- CID-11, DSM-V-TR, etc.
    DESCRICAO TEXT NOT NULL,
    GRUPO_TRANSTORNO VARCHAR(150),
    CONSTRAINT UP_SISTEMA_CODIGO UNIQUE (TIPO_SISTEMA, CODIGO_CLASSIFICACAO)
);

CREATE TABLE SINTOMA_REFERENCIA (
    ID_SINTOMA VARCHAR(50) PRIMARY KEY,       -- Permite códigos alfanuméricos estruturados
    CODIGO_UMLS INTEGER,
    NOME_SINTOMA VARCHAR(255) NOT NULL,
    CDATEGORIA VARCHAR(100)
);

-- 4. TABELAS INTERMEDIÁRIAS (Camada de Taxonomia N:M)
--

CREATE TABLE DIAGNOSTICO_SINTOMA (
    ID_DIAGNOSTICO INTEGER NOT NULL,
    ID_SINTOMA VARCHAR(50) NOT NULL,           -- CORREÇÃO: Alinhado com o tipo da tabela sintoma_referencia
    PESO_PROBABILISTICO_INICIAL NUMERIC(5,4) NOT NULL, -- Valores decimais entre 0 e 1
    data_vigencia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID_DIAGNOSTICO, ID_SINTOMA),
    CONSTRAINT fk_link_diagnostico FOREIGN KEY (ID_DIAGNOSTICO) 
        REFERENCES catalogo_diagnostico(ID_DIAGNOSTICO) ON DELETE CASCADE,
    CONSTRAINT fk_link_sintoma FOREIGN KEY (ID_SINTOMA) 
        REFERENCES sintoma_referencia(ID_SINTOMA) ON DELETE CASCADE,
    CONSTRAINT chk_peso CHECK (PESO_PROBABILISTICO_INICIAL >= 0 AND PESO_PROBABILISTICO_INICIAL <= 1)
);

CREATE TABLE criterio_operacional (
    id_criterio SERIAL PRIMARY KEY,
    tipo_regra VARCHAR(100) NOT NULL,
    tempo_minimo_semanas INTEGER,
    descricao_regra TEXT NOT NULL
);

CREATE TABLE diagnostico_criterio (
    id_diagnostico INTEGER NOT NULL,
    id_criterio INTEGER NOT NULL,              -- CORREÇÃO: Padronizado para INTEGER
    PRIMARY KEY (id_diagnostico, id_criterio),
    CONSTRAINT fk_crit_diagnostico FOREIGN KEY (id_diagnostico) 
        REFERENCES catalogo_diagnostico(id_diagnostico) ON DELETE CASCADE,
    CONSTRAINT fk_crit_operacional FOREIGN KEY (id_criterio) 
        REFERENCES criterio_operacional(id_criterio) ON DELETE CASCADE
);

CREATE TABLE crosswalk_sintomas (
    id_sintoma_origem VARCHAR(50) NOT NULL,
    id_sintoma_destino VARCHAR(50) NOT NULL,
    coeficiente_equivalencia NUMERIC(3,2) NOT NULL,
    PRIMARY KEY (id_sintoma_origem, id_sintoma_destino),
    CONSTRAINT fk_cross_origem FOREIGN KEY (id_sintoma_origem) REFERENCES sintoma_referencia(id_sintoma),
    CONSTRAINT fk_cross_destino FOREIGN KEY (id_sintoma_destino) REFERENCES sintoma_referencia(id_sintoma)
);

-- 5. CAMADA DE INTELIGÊNCIA, EVIDÊNCIAS E EVOLUÇÃO (Tabelas Fato)
-- 

CREATE TABLE sintoma_evidenciado (
    id_consulta INTEGER NOT NULL,
    id_sintoma VARCHAR(50) NOT NULL,
    intensidade INTEGER NOT NULL,
    presenca_sintoma BOOLEAN NOT NULL DEFAULT TRUE,
    evidencia_temporal INTEGER,               -- Ex: Duração em dias ou semanas do sintoma ativo
    PRIMARY KEY (id_consulta, id_sintoma),
    CONSTRAINT fk_evidencia_consulta FOREIGN KEY (id_consulta) REFERENCES consulta_sessao(id_consulta) ON DELETE CASCADE,
    CONSTRAINT fk_evidencia_sintoma FOREIGN KEY (id_sintoma) REFERENCES sintoma_referencia(id_sintoma) ON DELETE RESTRICT
);

CREATE TABLE predicao_diagnostica (
    id_predicao SERIAL PRIMARY KEY,
    id_consulta INTEGER NOT NULL,
    id_diagnostico INTEGER NOT NULL,
    probabilidade_calculada NUMERIC(5,4) NOT NULL, -- Mapeia o DECIMAL do diagrama
    algoritmo_versao VARCHAR(50) NOT NULL,
    metadados_modelo JSONB,                    -- ADIÇÃO: Armazena o estado das features de ML no instante do cálculo
    CONSTRAINT fk_predicao_consulta FOREIGN KEY (id_consulta) REFERENCES consulta_sessao(id_consulta) ON DELETE CASCADE,
    CONSTRAINT fk_predicao_diagnostico FOREIGN KEY (id_diagnostico) REFERENCES catalogo_diagnostico(id_diagnostico) ON DELETE RESTRICT,
    CONSTRAINT chk_probabilidade CHECK (probabilidade_calculada >= 0 AND probabilidade_calculada <= 1)
);

-- 6. ÍNDICES DE DESEMPENHO (Otimização para consultas analíticas)
-- 

CREATE INDEX idx_consulta_paciente ON consulta_sessao(id_paciente_analise);
CREATE INDEX idx_predicao_probabilidade ON predicao_diagnostica(probabilidade_calculada DESC);
CREATE INDEX idx_sintoma_evidenciado_consulta ON sintoma_evidenciado(id_consulta);



