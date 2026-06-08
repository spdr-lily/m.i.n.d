"""Seed assessment scales and DSM-5-TR criteria groups/rules/thresholds."""
from app.core.database import SessionLocal
from app.models.base import (
    Disorder, CriteriaGroup, CriteriaRule, CriteriaThreshold,
)
from app.services.assessment_service import get_seeded_scale_data

GROUPS_CONFIG = {
    "MDD": {
        "groups": [("A", "5+ dos 9 sintomas no mesmo periodo de 2 semanas, pelo menos 1 sendo humor deprimido ou anedonia")],
        "rules": [("A", 5, 9, 14)],
        "thresholds": [("mild", 5, None, None), ("moderate", None, None, None), ("severe", 9, None, None)],
    },
    "GAD": {
        "groups": [("A", "Ansiedade e preocupacao excessivas na maioria dos dias por 6+ meses")],
        "rules": [("A", 3, 6, 180)],
        "thresholds": [("mild", None, None, None), ("moderate", None, None, None), ("severe", None, None, None)],
    },
    "PANIC": {
        "groups": [
            ("A", "Ataques de panico inesperados e recorrentes"),
            ("B", "Preocupacao persistente sobre ataques futuros ou suas consequencias"),
        ],
        "rules": [("A", 1, 1, 0), ("B", 1, 1, 28)],
        "thresholds": [],
    },
    "AGORAPHOBIA": {
        "groups": [("A", "Medo/ansiedade intensos sobre 2+ situacoes")],
        "rules": [("A", 2, 5, 180)],
        "thresholds": [],
    },
    "BIPOLAR": {
        "groups": [
            ("A", "Periodo distinto de humor elevado/expansivo/irritavel por 1+ semana"),
            ("B", "3+ dos sintomas presentes durante o periodo de humor alterado"),
        ],
        "rules": [("A", 1, 1, 7), ("B", 3, 5, 7)],
        "thresholds": [],
    },
    "OCD": {
        "groups": [("A", "Obsessoes e/ou compulsoes")],
        "rules": [("A", 1, 1, 0)],
        "thresholds": [("mild", 8, None, None), ("moderate", 16, None, None), ("severe", 24, None, None)],
    },
    "PTSD": {
        "groups": [
            ("A", "Exposicao a evento traumatico real ou ameacador"),
            ("B", "Sintomas de intrusao (1+)"),
            ("C", "Esquiva persistente (1+)"),
            ("D", "Alteracoes negativas em cognicoes e humor (2+)"),
            ("E", "Alteracoes na excitacao e reatividade (2+)"),
        ],
        "rules": [("A", 1, 1, 0), ("B", 1, 3, 30), ("C", 1, 2, 30), ("D", 2, 4, 30), ("E", 2, 4, 30)],
        "thresholds": [("mild", None, None, None), ("moderate", None, None, None), ("severe", None, None, None)],
    },
    "SUD": {
        "groups": [("A", "Padrao problematico de uso levando a prejuizo clinicamente significativo")],
        "rules": [("A", 2, 7, 12)],
        "thresholds": [("mild", 2, None, None), ("moderate", 4, None, None), ("severe", 6, None, None)],
    },
    "ANOREXIA": {
        "groups": [("A", "Restricao energetica levando a peso corporal significativamente baixo")],
        "rules": [("A", 1, 1, 0)],
        "thresholds": [("mild", None, None, None), ("moderate", None, None, None), ("severe", None, None, None)],
    },
    "BULIMIA": {
        "groups": [("A", "Episodios recorrentes de compulsao alimentar com comportamentos compensatorios")],
        "rules": [("A", 1, 1, 0)],
        "thresholds": [("mild", None, None, None), ("moderate", None, None, None), ("severe", None, None, None)],
    },
    "BED": {
        "groups": [("A", "Episodios recorrentes de compulsao alimentar sem compensacao")],
        "rules": [("A", 1, 1, 0)],
        "thresholds": [("mild", None, None, None), ("moderate", None, None, None), ("severe", None, None, None)],
    },
    "INSOMNIA": {
        "groups": [("A", "Insatisfacao com quantidade/qualidade do sono por 3+ meses")],
        "rules": [("A", 1, 1, 30)],
        "thresholds": [],
    },
    "PSYCHOTIC": {
        "groups": [
            ("A", "Sintomas caracteristicos (delirios, alucinacoes, discurso desorganizado, sintomas negativos)"),
            ("B", "Disfuncao social/laboral"),
        ],
        "rules": [("A", 2, 5, 30), ("B", 1, 1, 30)],
        "thresholds": [],
    },
    "SOMATIC": {
        "groups": [("A", "Sintomas somaticos causando sofrimento ou prejuizo significativo")],
        "rules": [("A", 1, 1, 14)],
        "thresholds": [],
    },
    "ASD": {
        "groups": [
            ("A", "Deficits persistentes na comunicacao social (3/3 necessarios)"),
            ("B", "Padroes restritos e repetitivos de comportamento (2+/4)"),
        ],
        "rules": [("A", 3, 3, 365), ("B", 2, 4, 365)],
        "thresholds": [("level_1", None, None, None), ("level_2", None, None, None), ("level_3", None, None, None)],
    },
    "ADHD": {
        "groups": [
            ("A1", "6+ sintomas de desatencao por 6+ meses (5+ se 17+ anos)"),
            ("A2", "6+ sintomas de hiperatividade-impulsividade por 6+ meses (5+ se 17+ anos)"),
        ],
        "rules": [("A1", 6, 9, 180), ("A2", 6, 9, 180)],
        "thresholds": [("mild", None, None, None), ("moderate", None, None, None), ("severe", None, None, None)],
    },
}


def seed():
    db = SessionLocal()
    try:
        # 1. Seed scales
        scales = get_seeded_scale_data(db)
        print(f"OK - {len(scales)} scales seeded: {', '.join(scales.keys())}")

        # 2. Seed criteria groups, rules, thresholds
        disorders = {d.disorder_name: d for d in db.query(Disorder).all()}
        group_count = rule_count = threshold_count = 0

        for disorder_name, config in GROUPS_CONFIG.items():
            disorder = disorders.get(disorder_name)
            if not disorder:
                continue

            for label, desc in config.get("groups", []):
                existing = db.query(CriteriaGroup).filter_by(
                    disorder_id=disorder.disorder_id, group_label=label
                ).first()
                if not existing:
                    db.add(CriteriaGroup(
                        disorder_id=disorder.disorder_id, group_label=label, description=desc
                    ))
                    group_count += 1

            db.flush()

            for label, required, total, duration in config.get("rules", []):
                group = db.query(CriteriaGroup).filter_by(
                    disorder_id=disorder.disorder_id, group_label=label
                ).first()
                if group:
                    existing = db.query(CriteriaRule).filter_by(group_id=group.group_id).first()
                    if not existing:
                        db.add(CriteriaRule(
                            group_id=group.group_id, required_count=required,
                            total_count=total, min_duration_days=duration,
                        ))
                        rule_count += 1

            for severity, min_criteria, min_intensity, min_dur in config.get("thresholds", []):
                existing = db.query(CriteriaThreshold).filter_by(
                    disorder_id=disorder.disorder_id, severity_level=severity
                ).first()
                if not existing:
                    db.add(CriteriaThreshold(
                        disorder_id=disorder.disorder_id, severity_level=severity,
                        min_criteria_met=min_criteria, min_intensity=min_intensity,
                        min_duration_days=min_dur,
                    ))
                    threshold_count += 1

        db.commit()
        print(f"OK - {group_count} groups, {rule_count} rules, {threshold_count} thresholds")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
