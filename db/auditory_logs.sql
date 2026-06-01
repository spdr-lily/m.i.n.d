-- SCHEMA: audit

-- DROP SCHEMA IF EXISTS audit ;

CREATE SCHEMA IF NOT EXISTS audit
    AUTHORIZATION postgres;

-- AUDITORIA

CREATE TABLE IF NOT EXISTS audit.audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,

    entity_name VARCHAR(100),
    operation_type VARCHAR(20),

    performed_by VARCHAR(255),

    old_data JSONB,
    new_data JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
