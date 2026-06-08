"""Seed script — inserts initial reference data, symptoms, disorders, professionals, and patients."""

from datetime import date
from app.core.database import SessionLocal
from app.models.base import (
    SexType, GenderIdentity, EducationLevel, Ethnicity,
    Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship,
    HealthcareProfessional, Medication, ClassificationAuthority,
)
from app.repositories.auth_repository import AuthRepository
from app.security.hashing import get_password_hash


def seed(db):
    # --- Reference data (skip if already populated) ---
    reference_data_exists = db.query(SexType).count() > 0

    if not reference_data_exists:
        for s in [
            SexType(sex_type_id=1, code="M", description="Masculino"),
            SexType(sex_type_id=2, code="F", description="Feminino"),
        ]: db.merge(s)
        for g in [
            GenderIdentity(gender_identity_id=1, code="M", description="Masculino"),
            GenderIdentity(gender_identity_id=2, code="F", description="Feminino"),
            GenderIdentity(gender_identity_id=3, code="NB", description="Não-Binário"),
            GenderIdentity(gender_identity_id=4, code="GF", description="Gênero Fluido"),
            GenderIdentity(gender_identity_id=5, code="AG", description="Agênero"),
            GenderIdentity(gender_identity_id=6, code="OT", description="Outro"),
            GenderIdentity(gender_identity_id=7, code="PN", description="Prefiro não informar"),
        ]: db.merge(g)
        for e in [
            EducationLevel(education_level_id=1, code="EF", description="Ensino Fundamental"),
            EducationLevel(education_level_id=2, code="EM", description="Ensino Médio"),
            EducationLevel(education_level_id=3, code="ES", description="Ensino Superior"),
            EducationLevel(education_level_id=4, code="PG", description="Pós-Graduação"),
        ]: db.merge(e)
        for et in [
            Ethnicity(ethnicity_id=1, code="BRANCA", description="Branca"),
            Ethnicity(ethnicity_id=2, code="PRETA", description="Preta"),
            Ethnicity(ethnicity_id=3, code="PARDA", description="Parda"),
            Ethnicity(ethnicity_id=4, code="AMARELA", description="Amarela"),
            Ethnicity(ethnicity_id=5, code="INDIGENA", description="Indígena"),
        ]: db.merge(et)
        db.commit()
        print("OK - Dados de referencia inseridos")
    else:
        print("Dados de referencia ja existem — pulando")

    # --- Classification Authorities (skip if exist) ---
    if db.query(ClassificationAuthority).count() == 0:
        authorities = [
            ClassificationAuthority(
                authority_id=1, name="World Health Organization",
                short_name="WHO",
                description="Global authority for international health classification, including ICD-11.",
                website_url="https://www.who.int",
            ),
            ClassificationAuthority(
                authority_id=2, name="American Psychiatric Association",
                short_name="APA",
                description="Professional organization publishing the Diagnostic and Statistical Manual of Mental Disorders (DSM-5-TR).",
                website_url="https://www.psychiatry.org",
            ),
        ]
        for a in authorities:
            db.add(a)
        db.commit()
        print("OK - Classification authorities inseridas (WHO, APA)")
    else:
        print("Classification authorities ja existem — pulando")

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
        # TEA — Transtorno do Espectro Autista (DSM-5-TR: A1–A3, B1–B4)
        ("deficit_reciprocidade", "Deficit na reciprocidade socioemocional (DSM-5 A1)"),
        ("deficit_comunicacao_nao_verbal", "Deficit na comunicacao nao verbal (DSM-5 A2)"),
        ("deficit_relacionamento", "Deficit em desenvolver e manter relacionamentos (DSM-5 A3)"),
        ("movimentos_estereotipados", "Movimentos motores estereotipados ou fala repetitiva (DSM-5 B1)"),
        ("insistencia_rotina", "Insistencia em uniformidade e rotinas inflexiveis (DSM-5 B2)"),
        ("interesses_fixos", "Interesses altamente restritos e fixos (DSM-5 B3)"),
        ("reatividade_sensorial_atipica", "Hipo ou hiperreatividade a estimulos sensoriais (DSM-5 B4)"),
        # TDAH — Transtorno de Déficit de Atenção/Hiperatividade (DSM-5-TR: A1a–i, A2a–i)
        ("desatencao_detalhes", "Falha em prestar atencao a detalhes (DSM-5 A1a)"),
        ("dificuldade_sustentacao_atencao", "Dificuldade em sustentar a atencao (DSM-5 A1b)"),
        ("nao_escuta_direto", "Parece nao escutar quando abordado diretamente (DSM-5 A1c)"),
        ("dificuldade_seguir_instrucoes", "Nao segue instrucoes ate o fim (DSM-5 A1d)"),
        ("dificuldade_organizacao", "Dificuldade em organizar tarefas e atividades (DSM-5 A1e)"),
        ("evitacao_esforco_mental", "Evita tarefas que exigem esforco mental sustentado (DSM-5 A1f)"),
        ("perde_objetos", "Perde objetos necessarios para tarefas (DSM-5 A1g)"),
        ("distraibilidade_externa", "Facilmente distraido por estimulos externos (DSM-5 A1h)"),
        ("esquecimento_atividades", "Esquecimento em atividades cotidianas (DSM-5 A1i)"),
        ("inquietacao_motora", "Agitacao motora ou incapacidade de permanecer quieto (DSM-5 A2a/b)"),
        ("incapacidade_quieto", "Dificuldade em permanecer quieto em situacoes de espera (DSM-5 A2d)"),
        ("fala_excessiva", "Fala excessiva (DSM-5 A2g)"),
        ("dificuldade_esperar_vez", "Dificuldade em esperar sua vez (DSM-5 A2h)"),
        ("interrompe_outros", "Interrompe ou se intromete nas conversas dos outros (DSM-5 A2i)"),
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

    # --- Disorders (Portuguese, 19 diagnostic categories) ---
    disorders_data = [
        ("Transtorno Depressivo Maior", "F32.9", "296.22", "Episódios de humor deprimido ou perda de interesse por ≥2 semanas com 5+ sintomas."),
        ("Transtorno de Ansiedade Generalizada", "F41.1", "300.02", "Ansiedade e preocupação excessivas por ≥6 meses com sintomas físicos."),
        ("Transtorno do Pânico", "F41.0", "300.01", "Ataques de pânico inesperados e recorrentes com preocupação persistente."),
        ("Transtorno de Estresse Pós-Traumático", "F43.1", "309.81", "Sintomas de reexperiência, evitação e hiperativação após trauma."),
        ("Transtorno Depressivo Persistente (Distimia)", "F34.1", "300.4", "Humor deprimido crônico por ≥2 anos com sintomas subclínicos."),
        ("Transtorno de Ansiedade Social", "F40.1", "300.23", "Medo/ansiedade intensos em situações sociais com medo de avaliação negativa."),
        ("Transtorno Bipolar Tipo I", "F31.9", "296.7", "Pelo menos um episódio maníaco (≥1 semana ou hospitalização)."),
        ("Transtorno Bipolar Tipo II", "F31.8", "296.89", "Episódio hipomaníaco (≥4 dias) + pelo menos um episódio depressivo maior."),
        ("Transtorno Obsessivo-Compulsivo", "F42.9", "300.3", "Obsessões e/ou compulsões que consomem ≥1 hora/dia."),
        ("Agorafobia", "F40.0", "300.22", "Medo/ansiedade em 2+ situações (transporte, multidões, espaços abertos/fechados)."),
        ("Transtorno por Uso de Substâncias", "F19.20", "304.90", "Padrão problemático de uso com 2+ critérios em 12 meses."),
        ("Anorexia Nervosa", "F50.0", "307.1", "Restrição alimentar com peso baixo, medo de engordar e distorção de imagem."),
        ("Bulimia Nervosa", "F50.2", "307.51", "Compulsões + comportamentos compensatórios ≥1x/semana por 3 meses."),
        ("Transtorno de Compulsão Alimentar", "F50.8", "307.59", "Compulsões recorrentes sem comportamentos compensatórios regulares."),
        ("Transtorno de Insônia", "G47.0", "307.42", "Dificuldade de iniciar/manter o sono ≥3 noites/semana por ≥3 meses."),
        ("Esquizofrenia / Transtorno Psicótico", "F20.9", "295.9", "Delírios, alucinações, discurso desorganizado e/ou sintomas negativos por ≥6 meses."),
        ("Transtorno de Sintomas Somáticos", "F45.1", "300.82", "Sintomas somáticos com pensamentos/sentimentos/comportamentos excessivos."),
        ("Transtorno do Espectro Autista", "F84.0", "299.00", "Déficits persistentes na comunicação social + padrões restritos/repetitivos."),
        ("Transtorno de Déficit de Atenção/Hiperatividade", "F90.0", "314.01", "Padrão persistente de desatenção e/ou hiperatividade-impulsividade."),
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

    # --- Criteria (symptom ↔ disorder mapping) — DSM-5-TR ---
    # Each entry: (symptom_name, required_presence, notes)
    # required_presence=True means the symptom MUST be present for diagnosis
    # For MDD: at least 1 of humor_deprimido or anhedonia is required (handled in evaluator)
    criteria_map = {
        "Transtorno Depressivo Maior": [
            ("humor_deprimido", True, "Humor deprimido na maior parte do dia"),
            ("anhedonia", True, "Acentuada diminuição de interesse ou prazer"),
            ("alteracao_peso", False, "Perda ou ganho significativo de peso"),
            ("insonia_hipersonia", False, "Insônia ou hipersonia quase todos os dias"),
            ("agitacao_retardo", False, "Agitação ou retardo psicomotor"),
            ("fadiga", False, "Fadiga ou perda de energia"),
            ("sentimento_inutilidade", False, "Sentimento de inutilidade ou culpa excessiva"),
            ("concentracao", False, "Capacidade diminuída de concentração"),
            ("pensamento_morte", False, "Pensamentos recorrentes de morte ou ideação suicida"),
        ],
        "Transtorno de Ansiedade Generalizada": [
            ("preocupacao_excessiva", True, "Preocupação excessiva e difícil de controlar"),
            ("inquietacao", False, "Inquietação ou sensação de estar no limite"),
            ("fadiga_constante", False, "Fadiga constante e fácil"),
            ("concentracao", False, "Dificuldade de concentração"),
            ("irritabilidade", False, "Irritabilidade"),
            ("tensao_muscular", False, "Tensão muscular"),
            ("sono_prejudicado", False, "Dificuldade em conciliar ou manter o sono"),
        ],
        "Transtorno do Pânico": [
            ("palpitacoes", False, "Palpitações ou taquicardia"),
            ("sudorese", False, "Sudorese"),
            ("tremores", False, "Tremores ou abalos"),
            ("sensacao_sufocamento", False, "Sensação de sufocamento ou falta de ar"),
            ("dor_peito", False, "Dor no peito ou desconforto torácico"),
            ("nausea_abdominal", False, "Náusea ou desconforto abdominal"),
            ("tontura_vertigem", False, "Tontura, vertigem ou desmaio"),
            ("calafrios_ondas_calor", False, "Calafrios ou ondas de calor"),
            ("parestesias", False, "Dormência ou formigamento"),
            ("desrealizacao", False, "Sensação de irrealidade ou despersonalização"),
            ("medo_enlouquecer", False, "Medo de enlouquecer ou perder o controle"),
            ("medo_morrer", False, "Medo de morrer"),
            ("medo_morrer_panico", False, "Medo intenso de morrer durante o ataque"),
        ],
        "Agorafobia": [
            ("medo_transporte", False, "Medo de usar transporte público"),
            ("medo_multidoes", False, "Medo de multidões ou filas"),
            ("medo_lugares_abertos", False, "Medo de espaços abertos"),
            ("medo_lugares_fechados", False, "Medo de espaços fechados"),
            ("evitacao_fobica", False, "Esquiva fóbica de situações temidas"),
        ],
        "Transtorno Bipolar Tipo I": [
            ("euforia", True, "Humor elevado ou eufórico"),
            ("grandiosidade", False, "Autoestima inflada ou grandiosidade"),
            ("reducao_sono", False, "Redução da necessidade de sono"),
            ("logorreia", False, "Fala acelerada ou pressão para falar"),
            ("fuga_ideias", False, "Fuga de ideias ou pensamento acelerado"),
            ("comportamento_risco", False, "Comportamento de risco (gastos, sexo, investimentos)"),
        ],
        "Transtorno Obsessivo-Compulsivo": [
            ("obsessoes", False, "Pensamentos obsessivos recorrentes"),
            ("compulsoes", False, "Comportamentos compulsivos repetitivos"),
            ("verificacao_repetitiva", False, "Verificação repetitiva de objetos ou ações"),
            ("lavagem_limpeza", False, "Lavagem ou limpeza excessiva e ritualizada"),
            ("simetria_ordenacao", False, "Necessidade excessiva de simetria ou ordenação"),
            ("contagem_ritualistica", False, "Contagem ritualística"),
            ("acumulo_objetos", False, "Dificuldade persistente em descartar objetos"),
        ],
        "Transtorno de Estresse Pós-Traumático": [
            ("reexperiencia", False, "Revivência traumática recorrente (Critério B)"),
            ("sonhos_angustia", False, "Sonhos angustiantes recorrentes (Critério B)"),
            ("flashbacks_dissociativos", False, "Flashbacks dissociativos (Critério B)"),
            ("esquiva", False, "Esquiva persistente de estímulos traumáticos (Critério C)"),
            ("amnésia_traumática", False, "Incapacidade de recordar aspectos do trauma (Critério D)"),
            ("crenças_negativas", False, "Crenças negativas persistentes (Critério D)"),
            ("culpa_merito", False, "Sentimentos de culpa ou vergonha (Critério D)"),
            ("desesperanca_futuro", False, "Sensação de futuro encurtado (Critério D)"),
            ("hipervigilancia", False, "Estado de hipervigilância (Critério E)"),
            ("sobresalto_acentuado", False, "Resposta de sobressalto acentuada (Critério E)"),
        ],
        "Transtorno por Uso de Substâncias": [
            ("uso_prolongado", False, "Uso em maior quantidade ou por mais tempo"),
            ("dificuldade_controle", False, "Dificuldade persistente em controlar o uso"),
            ("desejo_intenso", False, "Desejo intenso ou compulsão pelo uso"),
            ("reducao_atividades", False, "Redução de atividades por causa do uso"),
            ("uso_risco_fisico", False, "Uso recorrente em situações de risco físico"),
            ("tolerancia_aumentada", False, "Tolerância aumentada"),
            ("abstinencia_substancia", False, "Síndrome de abstinência característica"),
        ],
        "Anorexia Nervosa": [
            ("restricao_alimentar", False, "Restrição alimentar intensa com baixo peso"),
            ("peso_baixo", False, "Peso corporal significativamente baixo"),
            ("medo_ganho_peso", False, "Medo intenso de ganhar peso ou engordar"),
            ("distorcao_imagem", False, "Distorção da autoimagem corporal"),
        ],
        "Bulimia Nervosa": [
            ("compulsao_alimentar", False, "Episódios de compulsão alimentar recorrentes"),
            ("vomito_autoinduzido", False, "Vômito autoinduzido ou uso de laxantes"),
            ("medo_ganho_peso", False, "Medo intenso de ganhar peso"),
            ("distorcao_imagem", False, "Distorção da autoimagem corporal"),
        ],
        "Transtorno de Compulsão Alimentar": [
            ("compulsao_alimentar", False, "Episódios de compulsão alimentar recorrentes"),
            ("comer_oculto", False, "Comer escondido ou em segredo"),
            ("distorcao_imagem", False, "Distorção da autoimagem corporal"),
        ],
        "Transtorno de Insônia": [
            ("dificuldade_iniciar_sono", False, "Dificuldade para iniciar o sono"),
            ("despertar_precoce", False, "Despertar precoce sem conseguir retomar"),
            ("sono_nao_restaurador", False, "Sono não restaurador"),
            ("sonolencia_diurna", False, "Sonolência diurna excessiva"),
        ],
        "Esquizofrenia / Transtorno Psicótico": [
            ("delirios_persecutorios", False, "Delírios persecutórios (Critério A)"),
            ("alucinacoes_auditivas", False, "Alucinações auditivas (Critério A)"),
            ("alucinacoes_visuais", False, "Alucinações visuais (Critério A)"),
            ("discurso_desorganizado", False, "Discurso desorganizado (Critério B)"),
            ("comportamento_desorganizado", False, "Comportamento desorganizado (Critério B)"),
            ("negativismo_catatonico", False, "Negativismo ou mutismo catatônico"),
            ("embotamento_afetivo", False, "Embotamento afetivo (Critério A - sintoma negativo)"),
        ],
        "Transtorno de Sintomas Somáticos": [
            ("sintomas_somaticos", False, "Sintomas somáticos múltiplos e recorrentes"),
            ("preocupacao_saude", False, "Preocupação excessiva com ter doença grave"),
            ("conversao_sensorial", False, "Sintomas neurológicos funcionais"),
        ],
        "Transtorno do Espectro Autista": [
            ("deficit_reciprocidade", True, "Deficit na reciprocidade socioemocional (DSM-5 A1)"),
            ("deficit_comunicacao_nao_verbal", True, "Deficit na comunicacao nao verbal (DSM-5 A2)"),
            ("deficit_relacionamento", True, "Deficit em desenvolver e manter relacionamentos (DSM-5 A3)"),
            ("movimentos_estereotipados", False, "Movimentos ou fala estereotipados (DSM-5 B1)"),
            ("insistencia_rotina", False, "Insistencia em rotinas inflexiveis (DSM-5 B2)"),
            ("interesses_fixos", False, "Interesses restritos e fixos (DSM-5 B3)"),
            ("reatividade_sensorial_atipica", False, "Reatividade sensorial atipica (DSM-5 B4)"),
        ],
        "Transtorno de Déficit de Atenção/Hiperatividade": [
            ("desatencao_detalhes", False, "Falha em prestar atencao a detalhes (DSM-5 A1a)"),
            ("dificuldade_sustentacao_atencao", False, "Dificuldade em sustentar atencao (DSM-5 A1b)"),
            ("nao_escuta_direto", False, "Parece nao escutar quando abordado (DSM-5 A1c)"),
            ("dificuldade_seguir_instrucoes", False, "Nao segue instrucoes ate o fim (DSM-5 A1d)"),
            ("dificuldade_organizacao", False, "Dificuldade em organizar tarefas (DSM-5 A1e)"),
            ("evitacao_esforco_mental", False, "Evita esforco mental prolongado (DSM-5 A1f)"),
            ("perde_objetos", False, "Perde objetos necessarios (DSM-5 A1g)"),
            ("distraibilidade_externa", False, "Facilmente distraido (DSM-5 A1h)"),
            ("esquecimento_atividades", False, "Esquecimento em atividades cotidianas (DSM-5 A1i)"),
            ("inquietacao_motora", False, "Agitacao motora ou incapacidade de parar (DSM-5 A2a/b)"),
            ("incapacidade_quieto", False, "Dificuldade em permanecer quieto (DSM-5 A2d)"),
            ("fala_excessiva", False, "Fala excessiva (DSM-5 A2g)"),
            ("dificuldade_esperar_vez", False, "Dificuldade em esperar sua vez (DSM-5 A2h)"),
            ("interrompe_outros", False, "Interrompe ou se intromete (DSM-5 A2i)"),
        ],
    }

    criteria_count = 0
    for disorder_name, symptom_entries in criteria_map.items():
        disorder = disorder_objects[disorder_name]
        for entry in symptom_entries:
            if len(entry) == 3:
                sym_name, required, notes = entry
            else:
                sym_name, required = entry
                notes = None
            symptom = symptom_objects.get(sym_name)
            if not symptom:
                print(f"  WARNING: symptom '{sym_name}' not found for {disorder_name}")
                continue
            existing = db.query(DiagnosticCriteria).filter_by(
                disorder_id=disorder.disorder_id,
                symptom_id=symptom.symptom_id,
            ).first()
            if not existing:
                db.add(DiagnosticCriteria(
                    disorder_id=disorder.disorder_id,
                    symptom_id=symptom.symptom_id,
                    required_presence=required,
                    minimum_duration_days={
                        "Transtorno Depressivo Maior": 14, "Transtorno de Ansiedade Generalizada": 180, "Transtorno do Pânico": 28, "Agorafobia": 180,
                        "Transtorno Bipolar Tipo I": 7, "Transtorno Obsessivo-Compulsivo": 7, "Transtorno de Estresse Pós-Traumático": 30,
                        "Transtorno por Uso de Substâncias": 12, "Anorexia Nervosa": 12, "Bulimia Nervosa": 12, "Transtorno de Compulsão Alimentar": 12,
                        "Transtorno de Insônia": 30, "Esquizofrenia / Transtorno Psicótico": 30, "Transtorno de Sintomas Somáticos": 14,
                        "Transtorno do Espectro Autista": 365, "Transtorno de Déficit de Atenção/Hiperatividade": 180,
                    }.get(disorder_name, 7),
                    clinical_notes=notes,
                ))
                criteria_count += 1

    db.commit()
    print(f"OK - {criteria_count} criterios diagnosticos inseridos")

    # --- Relationships (comorbidity / exclusion) ---
    relationships = [
        ("Transtorno Depressivo Maior", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.6),
        ("Transtorno de Ansiedade Generalizada", "Transtorno Depressivo Maior", "comorbidity", 0.6),
        ("Transtorno de Ansiedade Generalizada", "Transtorno do Pânico", "comorbidity", 0.5),
        ("Transtorno do Pânico", "Agorafobia", "comorbidity", 0.7),
        ("Agorafobia", "Transtorno do Pânico", "comorbidity", 0.7),
        ("Transtorno Depressivo Maior", "Transtorno Bipolar Tipo I", "hierarchical", 0.0),
        ("Transtorno Bipolar Tipo I", "Transtorno Depressivo Maior", "exclusion", 0.0),
        ("Transtorno de Estresse Pós-Traumático", "Transtorno Depressivo Maior", "comorbidity", 0.5),
        ("Transtorno Depressivo Maior", "Transtorno de Estresse Pós-Traumático", "comorbidity", 0.5),
        ("Transtorno de Estresse Pós-Traumático", "Transtorno por Uso de Substâncias", "comorbidity", 0.4),
        ("Transtorno por Uso de Substâncias", "Transtorno de Estresse Pós-Traumático", "comorbidity", 0.4),
        ("Transtorno por Uso de Substâncias", "Transtorno Depressivo Maior", "comorbidity", 0.4),
        ("Anorexia Nervosa", "Transtorno Depressivo Maior", "comorbidity", 0.5),
        ("Bulimia Nervosa", "Transtorno Depressivo Maior", "comorbidity", 0.5),
        ("Bulimia Nervosa", "Anorexia Nervosa", "hierarchical", 0.0),
        ("Transtorno de Insônia", "Transtorno Depressivo Maior", "comorbidity", 0.6),
        ("Transtorno Depressivo Maior", "Transtorno de Insônia", "comorbidity", 0.6),
        ("Transtorno de Insônia", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.5),
        ("Esquizofrenia / Transtorno Psicótico", "Transtorno Bipolar Tipo I", "hierarchical", 0.0),
        ("Transtorno Bipolar Tipo I", "Esquizofrenia / Transtorno Psicótico", "exclusion", 0.0),
        ("Esquizofrenia / Transtorno Psicótico", "Transtorno por Uso de Substâncias", "comorbidity", 0.4),
        ("Transtorno de Sintomas Somáticos", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.5),
        ("Transtorno de Sintomas Somáticos", "Transtorno Depressivo Maior", "comorbidity", 0.4),
        # TEA
        ("Transtorno do Espectro Autista", "Transtorno de Déficit de Atenção/Hiperatividade", "comorbidity", 0.6),
        ("Transtorno de Déficit de Atenção/Hiperatividade", "Transtorno do Espectro Autista", "comorbidity", 0.6),
        ("Transtorno do Espectro Autista", "Transtorno Depressivo Maior", "comorbidity", 0.4),
        ("Transtorno do Espectro Autista", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.4),
        # TDAH
        ("Transtorno de Déficit de Atenção/Hiperatividade", "Transtorno Depressivo Maior", "comorbidity", 0.5),
        ("Transtorno Depressivo Maior", "Transtorno de Déficit de Atenção/Hiperatividade", "comorbidity", 0.4),
        ("Transtorno de Déficit de Atenção/Hiperatividade", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.5),
        ("Transtorno de Ansiedade Generalizada", "Transtorno de Déficit de Atenção/Hiperatividade", "comorbidity", 0.4),
        ("Transtorno de Déficit de Atenção/Hiperatividade", "Transtorno por Uso de Substâncias", "comorbidity", 0.4),
        ("Transtorno por Uso de Substâncias", "Transtorno de Déficit de Atenção/Hiperatividade", "comorbidity", 0.4),
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

    # --- Admin user ---
    repo = AuthRepository(db)
    existing_admin = repo.get_by_username("admin")
    if not existing_admin:
        repo.create_user(
            username="admin",
            hashed_password=get_password_hash("admin"),
            full_name="Administrador",
            role="admin",
        )
        print("OK - Usuario admin criado")
    else:
        print("OK - Usuario admin ja existe")

    # --- Clinician user ---
    existing_clin = repo.get_by_username("clinician")
    if not existing_clin:
        repo.create_user(
            username="clinician",
            hashed_password=get_password_hash("clinician"),
            full_name="Dr. Carlos Silva (Clínico)",
            role="clinician",
        )
        print("OK - Usuario clinician criado")
    else:
        print("OK - Usuario clinician ja existe")

    # --- Medications ---
    common_medications = [
        ("Fluoxetina", "Fluoxetina", "Antidepressivo (ISRS)"),
        ("Sertralina", "Sertralina", "Antidepressivo (ISRS)"),
        ("Escitalopram", "Escitalopram", "Antidepressivo (ISRS)"),
        ("Venlafaxina", "Venlafaxina", "Antidepressivo (ISRSN)"),
        ("Bupropiona", "Bupropiona", "Antidepressivo (NDRI)"),
        ("Mirtazapina", "Mirtazapina", "Antidepressivo (NaSSA)"),
        ("Risperidona", "Risperidona", "Antipsicótico (Atípico)"),
        ("Olanzapina", "Olanzapina", "Antipsicótico (Atípico)"),
        ("Quetiapina", "Quetiapina", "Antipsicótico (Atípico)"),
        ("Aripiprazol", "Aripiprazol", "Antipsicótico (Atípico)"),
        ("Haloperidol", "Haloperidol", "Antipsicótico (Típico)"),
        ("Carbonato de Lítio", "Lítio", "Estabilizador de Humor"),
        ("Valproato de Sódio", "Valproato", "Estabilizador de Humor"),
        ("Lamotrigina", "Lamotrigina", "Estabilizador de Humor"),
        ("Clonazepam", "Clonazepam", "Ansiolítico (Benzodiazepínico)"),
        ("Alprazolam", "Alprazolam", "Ansiolítico (Benzodiazepínico)"),
        ("Diazepam", "Diazepam", "Ansiolítico (Benzodiazepínico)"),
        ("Metilfenidato", "Metilfenidato", "Psicoestimulante"),
        ("Lisdexanfetamina", "Lisdexanfetamina", "Psicoestimulante"),
        ("Zolpidem", "Zolpidem", "Hipnótico"),
    ]
    for name, ingredient, classification in common_medications:
        existing = db.query(Medication).filter_by(name=name).first()
        if not existing:
            db.add(Medication(name=name, active_ingredient=ingredient, classification=classification))
    db.commit()
    print(f"OK - {len(common_medications)} medicamentos inseridos")

    print("\nSeed concluido!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
