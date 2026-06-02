"""Seed script — inserts initial reference data, symptoms, disorders, professionals, and patients."""

from datetime import date
from app.core.database import SessionLocal
from app.models.base import (
    SexType, GenderIdentity, EducationLevel, Ethnicity,
    Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship,
    HealthcareProfessional,
)
from app.repositories.auth_repository import AuthRepository
from app.security.auth import get_password_hash


def seed(db):
    # --- Reference data ---
    sexes = [
        SexType(sex_type_id=1, code="M", description="Masculino"),
        SexType(sex_type_id=2, code="F", description="Feminino"),
    ]
    genders = [
        GenderIdentity(gender_identity_id=1, code="M", description="Masculino"),
        GenderIdentity(gender_identity_id=2, code="F", description="Feminino"),
        GenderIdentity(gender_identity_id=3, code="NB", description="Não-Binário"),
    ]
    educations = [
        EducationLevel(education_level_id=1, code="EF", description="Ensino Fundamental"),
        EducationLevel(education_level_id=2, code="EM", description="Ensino Médio"),
        EducationLevel(education_level_id=3, code="ES", description="Ensino Superior"),
        EducationLevel(education_level_id=4, code="PG", description="Pós-Graduação"),
    ]
    ethnicities = [
        Ethnicity(ethnicity_id=1, code="BRANCA", description="Branca"),
        Ethnicity(ethnicity_id=2, code="PRETA", description="Preta"),
        Ethnicity(ethnicity_id=3, code="PARDA", description="Parda"),
        Ethnicity(ethnicity_id=4, code="AMARELA", description="Amarela"),
        Ethnicity(ethnicity_id=5, code="INDIGENA", description="Indígena"),
    ]

    for s in sexes:
        db.merge(s)
    for g in genders:
        db.merge(g)
    for e in educations:
        db.merge(e)
    for et in ethnicities:
        db.merge(et)
    db.commit()
    print("OK - Dados de referencia inseridos")

    # --- Symptoms (DSM-5-TR) ---
    symptoms_data = [
        # Depressão (9 critérios)
        ("humor_deprimido", "Humor deprimido na maior parte do dia"),
        ("anhedonia", "Acentuada diminuição de interesse ou prazer"),
        ("alteracao_peso", "Significativa perda ou ganho de peso"),
        ("insonia_hipersonia", "Insônia ou hipersonia quase todos os dias"),
        ("agitacao_retardo", "Agitação ou retardo psicomotor"),
        ("fadiga", "Fadiga ou perda de energia"),
        ("sentimento_inutilidade", "Sentimento de inutilidade ou culpa excessiva"),
        ("concentracao", "Capacidade diminuída de concentração"),
        ("pensamento_morte", "Pensamentos recorrentes de morte ou ideação suicida"),
        # Depressão — variantes
        ("lentificacao", "Lentificação psicomotora observável"),
        ("hipersonia_atipica", "Hipersonia diurna com dificuldade de despertar"),
        ("choro_frequente", "Episódios frequentes de choro sem gatilho claro"),
        # Ansiedade generalizada (6 critérios)
        ("preocupacao_excessiva", "Preocupação excessiva e difícil de controlar"),
        ("inquietacao", "Inquietação ou sensação de estar no limite"),
        ("tensao_muscular", "Tensão muscular"),
        ("irritabilidade", "Irritabilidade"),
        ("sono_prejudicado", "Dificuldade em conciliar ou manter o sono"),
        ("fadiga_constante", "Fadiga constante e fácil"),
        # Pânico (13 sintomas DSM-5)
        ("palpitacoes", "Palpitações ou taquicardia"),
        ("sudorese", "Sudorese"),
        ("tremores", "Tremores ou abalos"),
        ("sensacao_sufocamento", "Sensação de sufocamento ou falta de ar"),
        ("medo_morrer", "Medo de morrer ou perder o controle"),
        ("dor_peito", "Dor no peito ou desconforto torácico"),
        ("nausea_abdominal", "Náusea ou desconforto abdominal"),
        ("tontura_vertigem", "Tontura, vertigem ou desmaio"),
        ("parestesias", "Dormência ou formigamento nas extremidades"),
        ("desrealizacao", "Sensação de irrealidade ou despersonalização"),
        ("medo_enlouquecer", "Medo de enlouquecer ou perder o controle"),
        ("calafrios_ondas_calor", "Calafrios ou ondas de calor"),
        ("medo_morrer_panico", "Medo intenso de morrer durante o ataque"),
        # Bipolar (mania)
        ("euforia", "Humor elevado ou eufórico"),
        ("grandiosidade", "Autoestima inflada ou grandiosidade"),
        ("logorreia", "Fala acelerada ou pressão para falar"),
        ("reducao_sono", "Redução da necessidade de sono"),
        ("fuga_ideias", "Fuga de ideias ou pensamento acelerado"),
        ("comportamento_risco", "Comportamento de risco (gastos, sexo, investimentos)"),
        ("hiperssexualidade", "Aumento marcante do interesse sexual"),
        ("gastos_excessivos", "Gastos excessivos e imprudentes"),
        ("planos_grandiosos", "Planos grandiosos irreais"),
        # TOC
        ("obsessoes", "Pensamentos obsessivos recorrentes"),
        ("compulsoes", "Comportamentos compulsivos repetitivos"),
        ("simetria_ordenacao", "Necessidade excessiva de simetria ou ordenação"),
        ("verificacao_repetitiva", "Verificação repetitiva de objetos ou ações"),
        ("lavagem_limpeza", "Lavagem ou limpeza excessiva e ritualizada"),
        ("contagem_ritualistica", "Contagem ritualística"),
        ("acumulo_objetos", "Dificuldade persistente em descartar objetos"),
        # PTSD (20 sintomas DSM-5)
        ("reexperiencia", "Revivência traumática recorrente"),
        ("esquiva", "Esquiva persistente de estímulos traumáticos"),
        ("hipervigilancia", "Estado de hipervigilância"),
        ("sonhos_angustia", "Sonhos angustiantes recorrentes relacionados ao trauma"),
        ("flashbacks_dissociativos", "Flashbacks dissociativos com sensação de reviver o evento"),
        ("sobresalto_acentuado", "Resposta de sobressalto acentuada"),
        ("culpa_merito", "Sentimentos persistentes de culpa ou vergonha"),
        ("desesperanca_futuro", "Sensação de futuro encurtado ou sem perspectivas"),
        ("amnésia_traumática", "Incapacidade de recordar aspectos importantes do evento"),
        ("crenças_negativas", "Crenças negativas persistentes sobre si ou o mundo"),
        # Transtornos por uso de substâncias
        ("desejo_intenso", "Desejo intenso ou compulsão pelo uso da substância"),
        ("abstinencia_substancia", "Síndrome de abstinência característica"),
        ("tolerancia_aumentada", "Tolerância aumentada à substância"),
        ("uso_prolongado", "Uso por período mais longo ou em quantidade maior que o pretendido"),
        ("reducao_atividades", "Redução de atividades sociais ou laborais por causa do uso"),
        ("dificuldade_controle", "Dificuldade persistente em controlar o uso"),
        ("uso_risco_fisico", "Uso recorrente em situações de risco físico"),
        # Transtornos alimentares
        ("restricao_alimentar", "Restrição alimentar intensa com baixo peso"),
        ("compulsao_alimentar", "Episódios de compulsão alimentar recorrentes"),
        ("vomito_autoinduzido", "Vômito autoinduzido ou uso de laxantes"),
        ("peso_baixo", "Peso corporal significativamente baixo"),
        ("medo_ganho_peso", "Medo intenso de ganhar peso ou engordar"),
        ("distorcao_imagem", "Distorção da autoimagem corporal"),
        ("comer_oculto", "Comer escondido ou em segredo"),
        # Transtornos do sono-vigília
        ("dificuldade_iniciar_sono", "Dificuldade para iniciar o sono"),
        ("despertar_precoce", "Despertar precoce sem conseguir retomar o sono"),
        ("sono_nao_restaurador", "Sono não restaurador"),
        ("sonolencia_diurna", "Sonolência diurna excessiva"),
        ("apneia_sono", "Ronco intenso ou paradas respiratórias durante o sono"),
        ("movimento_pernas", "Movimentos periódicos das pernas durante o sono"),
        # Transtornos psicóticos
        ("delirios_persecutorios", "Delírios persecutórios"),
        ("alucinacoes_auditivas", "Alucinações auditivas (vozes)"),
        ("alucinacoes_visuais", "Alucinações visuais"),
        ("discurso_desorganizado", "Discurso desorganizado ou incoerente"),
        ("comportamento_desorganizado", "Comportamento visivelmente desorganizado"),
        ("negativismo_catatonico", "Negativismo ou mutismo catatônico"),
        ("embotamento_afetivo", "Embotamento afetivo ou expressão emocional reduzida"),
        # Transtornos somáticos
        ("sintomas_somaticos", "Sintomas somáticos múltiplos e recorrentes"),
        ("preocupacao_saude", "Preocupação excessiva com ter uma doença grave"),
        ("conversao_sensorial", "Sintomas neurológicos funcionais (visão, audição, motricidade)"),
        # Agorafobia
        ("medo_transporte", "Medo de usar transporte público"),
        ("medo_multidoes", "Medo de multidões ou filas"),
        ("medo_lugares_abertos", "Medo de espaços abertos"),
        ("medo_lugares_fechados", "Medo de espaços fechados"),
        ("evitacao_fobica", "Esquiva fóbica de situações temidas"),
    ]

    symptom_objects = {}
    for name, desc in symptoms_data:
        existing = db.query(Symptom).filter_by(symptom_name=name).first()
        if not existing:
            s = Symptom(symptom_name=name, symptom_description=desc)
            db.add(s)
            db.flush()
            symptom_objects[name] = s
        else:
            symptom_objects[name] = existing

    db.commit()
    print(f"OK - {len(symptoms_data)} sintomas inseridos")

    # --- Disorders ---
    disorders_data = [
        ("MDD", "F32.1", "296.22", "Major Depressive Disorder — single episode, moderate"),
        ("GAD", "F41.1", "300.02", "Generalized Anxiety Disorder"),
        ("PANIC", "F41.0", "300.01", "Panic Disorder"),
        ("AGORAPHOBIA", "F40.0", "300.22", "Agoraphobia"),
        ("BIPOLAR", "F31.1", "296.4", "Bipolar I Disorder — current episode manic"),
        ("OCD", "F42", "300.3", "Obsessive-Compulsive Disorder"),
        ("PTSD", "F43.1", "309.81", "Post-Traumatic Stress Disorder"),
        ("SUD", "F19.20", "304.90", "Substance Use Disorder — moderate"),
        ("ANOREXIA", "F50.0", "307.1", "Anorexia Nervosa"),
        ("BULIMIA", "F50.2", "307.51", "Bulimia Nervosa"),
        ("BED", "F50.8", "307.59", "Binge-Eating Disorder"),
        ("INSOMNIA", "G47.0", "307.42", "Insomnia Disorder"),
        ("PSYCHOTIC", "F20.9", "295.9", "Schizophrenia / Psychotic Disorder"),
        ("SOMATIC", "F45.1", "300.82", "Somatic Symptom Disorder"),
    ]

    disorder_objects = {}
    for name, cid, dsm, desc in disorders_data:
        existing = db.query(Disorder).filter_by(disorder_name=name).first()
        if not existing:
            d = Disorder(disorder_name=name, cid_code=cid, dsm_code=dsm, disorder_description=desc)
            db.add(d)
            db.flush()
            disorder_objects[name] = d
        else:
            disorder_objects[name] = existing

    db.commit()
    print(f"OK - {len(disorders_data)} transtornos inseridos")

    # --- Criteria (symptom ↔ disorder mapping) ---
    criteria_map = {
        "MDD": ["humor_deprimido", "anhedonia", "alteracao_peso", "insonia_hipersonia",
                 "agitacao_retardo", "fadiga", "sentimento_inutilidade", "concentracao",
                 "pensamento_morte", "lentificacao", "hipersonia_atipica", "choro_frequente"],
        "GAD": ["preocupacao_excessiva", "inquietacao", "tensao_muscular", "irritabilidade",
                 "sono_prejudicado", "fadiga_constante"],
        "PANIC": ["palpitacoes", "sudorese", "tremores", "sensacao_sufocamento", "medo_morrer",
                   "dor_peito", "nausea_abdominal", "tontura_vertigem", "parestesias",
                   "desrealizacao", "medo_enlouquecer", "calafrios_ondas_calor", "medo_morrer_panico"],
        "AGORAPHOBIA": ["medo_transporte", "medo_multidoes", "medo_lugares_abertos",
                         "medo_lugares_fechados", "evitacao_fobica"],
        "BIPOLAR": ["euforia", "grandiosidade", "logorreia", "reducao_sono", "fuga_ideias",
                     "comportamento_risco", "hiperssexualidade", "gastos_excessivos", "planos_grandiosos"],
        "OCD": ["obsessoes", "compulsoes", "simetria_ordenacao", "verificacao_repetitiva",
                 "lavagem_limpeza", "contagem_ritualistica", "acumulo_objetos"],
        "PTSD": ["reexperiencia", "esquiva", "hipervigilancia", "sonhos_angustia",
                  "flashbacks_dissociativos", "sobresalto_acentuado", "culpa_merito",
                  "desesperanca_futuro", "amnésia_traumática", "crenças_negativas"],
        "SUD": ["desejo_intenso", "abstinencia_substancia", "tolerancia_aumentada",
                 "uso_prolongado", "reducao_atividades", "dificuldade_controle", "uso_risco_fisico"],
        "ANOREXIA": ["restricao_alimentar", "peso_baixo", "medo_ganho_peso", "distorcao_imagem"],
        "BULIMIA": ["compulsao_alimentar", "vomito_autoinduzido", "comer_oculto",
                     "medo_ganho_peso", "distorcao_imagem"],
        "BED": ["compulsao_alimentar", "comer_oculto", "distorcao_imagem"],
        "INSOMNIA": ["dificuldade_iniciar_sono", "despertar_precoce", "sono_nao_restaurador",
                      "sonolencia_diurna"],
        "PSYCHOTIC": ["delirios_persecutorios", "alucinacoes_auditivas", "alucinacoes_visuais",
                       "discurso_desorganizado", "comportamento_desorganizado",
                       "negativismo_catatonico", "embotamento_afetivo"],
        "SOMATIC": ["sintomas_somaticos", "preocupacao_saude", "conversao_sensorial"],
    }

    criteria_count = 0
    for disorder_name, symptom_names in criteria_map.items():
        disorder = disorder_objects[disorder_name]
        for sym_name in symptom_names:
            symptom = symptom_objects.get(sym_name)
            if not symptom:
                continue
            existing = db.query(DiagnosticCriteria).filter_by(
                disorder_id=disorder.disorder_id,
                symptom_id=symptom.symptom_id,
            ).first()
            if not existing:
                db.add(DiagnosticCriteria(
                    disorder_id=disorder.disorder_id,
                    symptom_id=symptom.symptom_id,
                    required_presence=True,
                    minimum_duration_days={
                        "MDD": 14, "GAD": 14, "PANIC": 7, "AGORAPHOBIA": 14,
                        "BIPOLAR": 7, "OCD": 7, "PTSD": 30,
                        "SUD": 12, "ANOREXIA": 12, "BULIMIA": 12, "BED": 12,
                        "INSOMNIA": 30, "PSYCHOTIC": 30, "SOMATIC": 14,
                    }.get(disorder_name, 7),
                ))
                criteria_count += 1

    db.commit()
    print(f"OK - {criteria_count} criterios diagnosticos inseridos")

    # --- Relationships (comorbidity / exclusion) ---
    relationships = [
        ("MDD", "GAD", "comorbidity", 0.6),
        ("GAD", "MDD", "comorbidity", 0.6),
        ("GAD", "PANIC", "comorbidity", 0.5),
        ("PANIC", "AGORAPHOBIA", "comorbidity", 0.7),
        ("AGORAPHOBIA", "PANIC", "comorbidity", 0.7),
        ("MDD", "BIPOLAR", "hierarchical", 0.0),
        ("BIPOLAR", "MDD", "exclusion", 0.0),
        ("PTSD", "MDD", "comorbidity", 0.5),
        ("MDD", "PTSD", "comorbidity", 0.5),
        ("PTSD", "SUD", "comorbidity", 0.4),
        ("SUD", "PTSD", "comorbidity", 0.4),
        ("SUD", "MDD", "comorbidity", 0.4),
        ("ANOREXIA", "MDD", "comorbidity", 0.5),
        ("BULIMIA", "MDD", "comorbidity", 0.5),
        ("BULIMIA", "ANOREXIA", "hierarchical", 0.0),
        ("INSOMNIA", "MDD", "comorbidity", 0.6),
        ("MDD", "INSOMNIA", "comorbidity", 0.6),
        ("INSOMNIA", "GAD", "comorbidity", 0.5),
        ("PSYCHOTIC", "BIPOLAR", "hierarchical", 0.0),
        ("BIPOLAR", "PSYCHOTIC", "exclusion", 0.0),
        ("PSYCHOTIC", "SUD", "comorbidity", 0.4),
        ("SOMATIC", "GAD", "comorbidity", 0.5),
        ("SOMATIC", "MDD", "comorbidity", 0.4),
    ]

    for src, tgt, rtype, weight in relationships:
        if src in disorder_objects and tgt in disorder_objects:
            existing = db.query(DiagnosisRelationship).filter_by(
                source_disorder_id=disorder_objects[src].disorder_id,
                target_disorder_id=disorder_objects[tgt].disorder_id,
            ).first()
            if not existing:
                db.add(DiagnosisRelationship(
                    source_disorder_id=disorder_objects[src].disorder_id,
                    target_disorder_id=disorder_objects[tgt].disorder_id,
                    relationship_type=rtype,
                    relationship_weight=weight,
                ))

    db.commit()
    print("OK - Relacoes diagnosticas inseridas")

    # --- Professional ---
    existing_prof = db.query(HealthcareProfessional).first()
    if not existing_prof:
        prof = HealthcareProfessional(
            full_name="Dr. Carlos Silva",
            professional_license="CRM-12345",
            specialty="Psychiatry",
        )
        db.add(prof)
        db.commit()
        prof_uuid = prof.professional_uuid
        print(f"OK - Profissional criado: {prof_uuid}")
    else:
        prof_uuid = existing_prof.professional_uuid
        print(f"OK - Profissional ja existente: {prof_uuid}")

    # --- Clinician user ---
    repo = AuthRepository(db)
    existing_clin = repo.get_by_username("clinician")
    if not existing_clin:
        repo.create_user(
            username="clinician",
            hashed_password=get_password_hash("Cmspelo_137"),
            full_name="Dr. Carlos Silva (Clínico)",
            role="clinician",
        )
        print("OK - Usuario clinician criado")
    else:
        print("OK - Usuario clinician ja existe")

    print("\nSeed concluido!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
