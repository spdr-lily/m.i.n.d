"""Enrich ICD-11 clinical descriptions for reference disorders using DSM-5-TR criteria text."""
from app.core.database import SessionLocal
from app.models.base import ICD11Code, Disorder

# Core disorder names (inlined from scripts.dsm5tr_data)
CORE_DISORDER_NAMES = {
    "Transtorno Depressivo Maior", "Transtorno de Ansiedade Generalizada",
    "Transtorno do Pânico", "Transtorno de Estresse Pós-Traumático",
    "Transtorno Depressivo Persistente (Distimia)", "Transtorno de Ansiedade Social",
    "Transtorno Bipolar Tipo I", "Transtorno Bipolar Tipo II",
    "Transtorno Obsessivo-Compulsivo", "Agorafobia",
    "Transtorno por Uso de Substâncias", "Anorexia Nervosa",
    "Bulimia Nervosa", "Transtorno de Compulsão Alimentar",
    "Transtorno de Insônia", "Esquizofrenia / Transtorno Psicótico",
    "Transtorno de Sintomas Somáticos", "Transtorno do Espectro Autista",
    "Transtorno de Déficit de Atenção/Hiperatividade",
}


def enrich():
    db = SessionLocal()
    try:
        core_names = set(CORE_DISORDER_NAMES)
        ref_codes = (
            db.query(ICD11Code)
            .join(Disorder)
            .filter(
                Disorder.disorder_name.notin_(list(core_names)),
                Disorder.dsm_criteria.isnot(None),
                Disorder.dsm_criteria != "",
            )
            .all()
        )
        updated = 0
        for code in ref_codes:
            if code.clinical_description:
                continue
            dsm_text = code.disorder.dsm_criteria
            if not dsm_text:
                continue
            # Truncate to reasonable length for a description
            desc = dsm_text[:500].strip()
            if len(dsm_text) > 500:
                desc += "..."
            code.clinical_description = desc
            updated += 1
        db.commit()
        print(f"OK - {updated} reference ICD-11 descriptions enriched from DSM-5-TR criteria")
    finally:
        db.close()


if __name__ == "__main__":
    enrich()
