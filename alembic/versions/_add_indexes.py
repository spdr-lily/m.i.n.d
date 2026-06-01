from alembic import op

# Revisão e dependências
revision = '20260601_add_indexes'
down_revision = '20260601_create_tables'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index(
        'idx_patient_identity_national_id',
        'patient_identity',
        ['national_id'],
        schema='security'
    )
    op.create_index(
        'idx_symptom_category',
        'symptoms',
        ['category_id'],
        schema='diagnostic'
    )
    op.create_index(
        'idx_disorder_icd',
        'disorders',
        ['icd_code'],
        schema='diagnostic'
    )
    op.create_index(
        'idx_consultation_patient',
        'clinical_consultation',
        ['patient_id'],
        schema='clinical'
    )
    op.create_index(
        'idx_inference_patient',
        'diagnostic_inference',
        ['patient_id'],
        schema='diagnostic'
    )

def downgrade():
    op.drop_index('idx_patient_identity_national_id', table_name='patient_identity', schema='security')
    op.drop_index('idx_symptom_category', table_name='symptoms', schema='diagnostic')
    op.drop_index('idx_disorder_icd', table_name='disorders', schema='diagnostic')
    op.drop_index('idx_consultation_patient', table_name='clinical_consultation', schema='clinical')
    op.drop_index('idx_inference_patient', table_name='diagnostic_inference', schema='diagnostic')
