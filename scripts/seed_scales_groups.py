"""Seed assessment scales and DSM-5-TR criteria groups/rules/thresholds.

Each group maps to a contiguous slice of the disorder's criteria, in the
order the criteria were seeded (ascending ``criteria_id``).  ``total_count``
in a rule defines that slice size; the last group absorbs any remaining
criteria.  ``required_count`` is the number of *distinct symptoms* that must
be present for the group to be satisfied.
"""
from app.core.database import SessionLocal
from app.models.base import (
    Disorder, CriteriaGroup, CriteriaRule, CriteriaThreshold,
)
from app.services.assessment_service import get_seeded_scale_data

# Portuguese(DB) disorder name -> groups/rules/thresholds
GROUPS_CONFIG = {
    "Transtorno Depressivo Maior": {
        "groups": [
            ("A", "5+ de 9 sintomas no mesmo periodo de 2 semanas, incluindo humor deprimido ou anedonia"),
        ],
        "rules": [("A", 5, 9, 14)],
        "thresholds": [
            ("mild", 5, None, 14),
            ("moderate", 7, None, 14),
            ("severe", 9, None, 14),
        ],
    },
    "Transtorno de Ansiedade Generalizada": {
        "groups": [
            ("A", "Ansiedade e preocupacao excessivas na maioria dos dias por 6+ meses, com 3+ sintomas associados"),
        ],
        "rules": [("A", 3, 7, 180)],
        "thresholds": [],
    },
    "Transtorno do Pânico": {
        "groups": [
            ("A", "Ataque de panico recorrente e inesperado com 4+ sintomas fisicos/cognitivos"),
        ],
        "rules": [("A", 4, 13, 28)],
        "thresholds": [],
    },
    "Agorafobia": {
        "groups": [
            ("A", "Medo ou ansiedade intensos em 2+ situacoes, com esquiva e sofrimento clinicamente significativo"),
        ],
        "rules": [("A", 2, 5, 180)],
        "thresholds": [],
    },
    "Transtorno Bipolar Tipo I": {
        "groups": [
            ("A", "Periodo distinto de humor elevado, expansivo ou irritavel"),
            ("B", "3+ sintomas durante o periodo de humor alterado (grandiosidade, reducao de sono, logorreia, fuga de ideias, comportamento de risco)"),
        ],
        "rules": [("A", 1, 1, 7), ("B", 3, 5, 7)],
        "thresholds": [],
    },
    "Transtorno Obsessivo-Compulsivo": {
        "groups": [
            ("A", "Presenca de obsessoes e/ou compulsoes que consomem tempo e causam sofrimento"),
        ],
        "rules": [("A", 1, 7, 7)],
        "thresholds": [
            ("mild", 1, None, 7),
            ("moderate", 4, None, 7),
            ("severe", 6, None, 7),
        ],
    },
    "Transtorno de Estresse Pós-Traumático": {
        "groups": [
            ("B", "Sintomas de intrusao (1+ sintoma)"),
            ("C", "Esquiva persistente de estimulos associados ao trauma"),
            ("D", "Alteracoes negativas em cognicoes e humor (2+ sintomas)"),
            ("E", "Alteracoes na excitacao e reatividade (1+ sintoma)"),
        ],
        "rules": [("B", 1, 3, 30), ("C", 1, 1, 30), ("D", 2, 4, 30), ("E", 1, 2, 30)],
        "thresholds": [],
    },
    "Transtorno por Uso de Substâncias": {
        "groups": [
            ("A", "Padrao problematico de uso levando a prejuizo ou sofrimento clinicamente significativo (2+ criterios)"),
        ],
        "rules": [("A", 2, 7, 12)],
        "thresholds": [
            ("mild", 2, None, 12),
            ("moderate", 4, None, 12),
            ("severe", 6, None, 12),
        ],
    },
    "Anorexia Nervosa": {
        "groups": [
            ("A", "Restricao energetica, peso significativamente baixo, medo de ganhar peso e/ou distorcao da imagem corporal"),
        ],
        "rules": [("A", 3, 4, 12)],
        "thresholds": [],
    },
    "Bulimia Nervosa": {
        "groups": [
            ("A", "Episodios de compulsao alimentar recorrentes com comportamentos compensatorios e autoavaliacao influenciada pelo peso"),
        ],
        "rules": [("A", 3, 4, 12)],
        "thresholds": [],
    },
    "Transtorno de Compulsão Alimentar": {
        "groups": [
            ("A", "Episodios recorrentes de compulsao alimentar sem comportamentos compensatorios (2+ sintomas)"),
        ],
        "rules": [("A", 2, 3, 12)],
        "thresholds": [],
    },
    "Transtorno de Insônia": {
        "groups": [
            ("A", "Insatisfacao com quantidade/qualidade do sono por 3+ meses, com prejuizo diurno"),
        ],
        "rules": [("A", 2, 4, 30)],
        "thresholds": [],
    },
    "Esquizofrenia / Transtorno Psicótico": {
        "groups": [
            ("A", "2+ sintomas caracteristicos (delirios, alucinacoes, discurso/comportamento desorganizado, sintomas negativos)"),
        ],
        "rules": [("A", 2, 7, 30)],
        "thresholds": [],
    },
    "Transtorno de Sintomas Somáticos": {
        "groups": [
            ("A", "Sintomas somaticos com sofrimento/prejuizo e preocupacao excessiva com saude"),
        ],
        "rules": [("A", 2, 3, 14)],
        "thresholds": [],
    },
    "Transtorno do Espectro Autista": {
        "groups": [
            ("A", "Deficits persistentes na comunicacao e interacao social (3/3 necessarios)"),
            ("B", "Padroes restritos e repetitivos de comportamento (2+/4)"),
        ],
        "rules": [("A", 3, 3, 365), ("B", 2, 4, 365)],
        "thresholds": [],
    },
    "Transtorno de Déficit de Atenção/Hiperatividade": {
        "groups": [
            ("A", "6+ sintomas de desatencao e/ou hiperatividade-impulsividade por 6+ meses (5+ se 17+ anos)"),
        ],
        "rules": [("A", 6, 14, 180)],
        "thresholds": [],
    },
    "Transtorno Depressivo Persistente (Distimia)": {
        "groups": [
            ("A", "Humor deprimido na maior parte do dia, na maioria dos dias, por 2+ anos, com 2+ sintomas associados"),
        ],
        "rules": [("A", 3, 5, 730)],
        "thresholds": [],
    },
    "Transtorno de Ansiedade Social": {
        "groups": [
            ("A", "Medo/ansiedade intensos em situacoes sociais com 3+ sintomas e esquiva ou sofrimento significativo"),
        ],
        "rules": [("A", 3, 4, 180)],
        "thresholds": [],
    },
    "Transtorno Bipolar Tipo II": {
        "groups": [
            ("A", "Periodo de humor elevado/expansivo/irritavel com 3+ sintomas hipomaniacos por 4+ dias"),
            ("B", "Historia de episodio depressivo maior (humor deprimido/anedonia) — necessario para o Tipo II"),
        ],
        "rules": [("A", 3, 6, 4), ("B", 1, 1, 14)],
        "thresholds": [],
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
        skipped = []

        for disorder_name, config in GROUPS_CONFIG.items():
            disorder = disorders.get(disorder_name)
            if not disorder:
                skipped.append(disorder_name)
                continue

            desired_labels = [label for label, _desc in config.get("groups", [])]

            # Remove stale groups that are no longer configured.
            existing_groups = db.query(CriteriaGroup).filter_by(
                disorder_id=disorder.disorder_id
            ).all()
            for group in existing_groups:
                if group.group_label not in desired_labels:
                    db.delete(group)

            group_objects = {}
            for sort_order, (label, desc) in enumerate(config.get("groups", []), start=1):
                group = db.query(CriteriaGroup).filter_by(
                    disorder_id=disorder.disorder_id, group_label=label
                ).first()
                if group:
                    group.description = desc
                    group.sort_order = sort_order
                else:
                    group = CriteriaGroup(
                        disorder_id=disorder.disorder_id,
                        group_label=label,
                        description=desc,
                        sort_order=sort_order,
                    )
                    db.add(group)
                    group_count += 1
                group_objects[label] = group

            db.flush()

            for label, required, total, duration in config.get("rules", []):
                group = group_objects.get(label)
                if not group:
                    continue
                existing = db.query(CriteriaRule).filter_by(group_id=group.group_id).first()
                if existing:
                    existing.required_count = required
                    existing.total_count = total
                    existing.min_duration_days = duration
                else:
                    db.add(CriteriaRule(
                        group_id=group.group_id, required_count=required,
                        total_count=total, min_duration_days=duration,
                    ))
                    rule_count += 1

            for severity, min_criteria, min_intensity, min_dur in config.get("thresholds", []):
                existing = db.query(CriteriaThreshold).filter_by(
                    disorder_id=disorder.disorder_id, severity_level=severity
                ).first()
                if existing:
                    existing.min_criteria_met = min_criteria
                    existing.min_intensity = min_intensity
                    existing.min_duration_days = min_dur
                else:
                    db.add(CriteriaThreshold(
                        disorder_id=disorder.disorder_id, severity_level=severity,
                        min_criteria_met=min_criteria, min_intensity=min_intensity,
                        min_duration_days=min_dur,
                    ))
                    threshold_count += 1

        db.commit()
        print(f"OK - {group_count} new groups, {rule_count} new rules, {threshold_count} new thresholds")
        if skipped:
            print(f"WARN - {len(skipped)} disorders not found: {', '.join(skipped)}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
