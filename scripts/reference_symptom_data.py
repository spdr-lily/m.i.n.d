# -*- coding: utf-8 -*-
"""Reference symptom mapping data for disorders beyond the 19 core.
Generated from DSM-5-TR criteria. Used by seed_full_catalog.py."""

# ═══ REFERENCE SYMPTOM MAP ═══
# Maps each reference disorder (by Portuguese DSM-5-TR name) to its key symptoms.
# Format: disorder_name -> [(symptom_key, description_pt, required, min_duration_days)]
REFERENCE_SYMPTOM_MAP = {
    # ═══ CHAPTER 1: Transtornos do Neurodesenvolvimento ═══
    "Deficiência Intelectual": [
        ("intellectual_function_deficit", "Déficits em funções intelectuais (raciocínio, solução de problemas, planejamento, pensamento abstrato, julgamento)", True, 0),
        ("adaptive_functioning_deficit", "Déficits no funcionamento adaptativo resultando em falha em atingir padrões de independência pessoal e responsabilidade social", True, 0),
        ("developmental_onset", "Início no período do desenvolvimento", True, 0),
        ("social_adaptive_deficit", "Déficit em habilidades sociais e responsabilidade social para a idade", False, 0),
    ],
    "Atraso Global do Desenvolvimento": [
        ("global_developmental_delay", "Atraso significativo em múltiplas áreas do desenvolvimento (motora grossa/fina, linguagem, cognição, habilidades sociais)", True, 0),
        ("motor_skill_delay", "Atraso no desenvolvimento motor grosso ou fino", False, 0),
        ("speech_language_delay", "Atraso na aquisição da fala e linguagem", False, 0),
        ("cognitive_delay", "Atraso no desenvolvimento cognitivo para a idade", False, 0),
        ("social_skill_delay", "Atraso em habilidades sociais e atividades da vida diária", False, 0),
    ],
    "Transtorno da Linguagem": [
        ("language_acquisition_deficit", "Dificuldades persistentes na aquisição e uso da linguagem em todas as modalidades (falada, escrita, sinais)", True, 0),
        ("language_comprehension_deficit", "Déficit na compreensão da linguagem (vocabulário reduzido, dificuldade com sentenças complexas)", False, 0),
        ("language_expression_deficit", "Déficit na produção da linguagem (vocabulário limitado, erros gramaticais, discurso desorganizado)", False, 0),
        ("language_below_age", "Capacidades linguísticas substancialmente abaixo do esperado para a idade", False, 0),
    ],
    "Transtorno Fonológico": [
        ("speech_sound_production_deficit", "Dificuldade persistente na produção de sons da fala que interfere na inteligibilidade", True, 0),
        ("speech_intelligibility_deficit", "Inteligibilidade da fala reduzida impedindo a comunicação verbal", False, 0),
        ("social_communication_impairment", "Prejuízo na comunicação social devido aos erros na produção de sons da fala", False, 0),
    ],
    "Transtorno da Fluência com Início na Infância (Gagueira)": [
        ("stuttering", "Repetições de sons, sílabas ou palavras na fala", True, 0),
        ("speech_block", "Prolongamentos de sons ou bloqueios audíveis/visíveis da fala", False, 0),
        ("speech_avoidance", "Substituição de palavras ou circunlóquios para evitar momentos de gagueira", False, 0),
        ("stuttering_anxiety", "Ansiedade ou prejuízo na comunicação social devido à gagueira", False, 0),
    ],
    "Transtorno da Comunicação Social (Pragmática)": [
        ("pragmatic_language_deficit", "Dificuldades persistentes no uso social da comunicação verbal e não verbal", True, 0),
        ("conversational_turn_taking_deficit", "Déficit na alternância de turnos conversacionais e saudações", False, 0),
        ("non_literal_language_deficit", "Dificuldade com linguagem não literal (ironia, metáforas, inferências, humor)", False, 0),
        ("social_context_communication", "Dificuldade em adequar a comunicação ao contexto social e à audiência", False, 0),
    ],
    "Transtorno Específico da Aprendizagem": [
        ("reading_accuracy_deficit", "Precisão de leitura de palavras abaixo do esperado para a idade", False, 180),
        ("reading_comprehension_deficit", "Dificuldade de compreensão do material lido (inferências, sentido)", False, 180),
        ("spelling_deficit", "Dificuldade de ortografia e soletração (erros múltiplos, inconsistências)", False, 180),
        ("written_expression_deficit", "Dificuldade na expressão escrita (organização, clareza, gramática, construção de parágrafos)", False, 180),
        ("math_computation_deficit", "Dificuldade no cálculo e raciocínio matemático (sentido numérico, memorização de fatos)", False, 180),
        ("math_reasoning_deficit", "Dificuldade na solução de problemas matemáticos e raciocínio quantitativo", False, 180),
    ],
    "Transtorno do Desenvolvimento da Coordenação": [
        ("gross_motor_coordination_deficit", "Aquisição e execução de habilidades motoras coordenadas substancialmente abaixo do esperado para a idade", True, 0),
        ("fine_motor_coordination_deficit", "Déficit na coordenação motora fina (escrita manual, uso de tesoura, amarrar sapatos)", False, 0),
        ("motor_milestone_delay", "Atraso na aquisição de marcos motores (engatinhar, andar, correr)", False, 0),
        ("manual_dexterity_impairment", "Prejuízo no desempenho de atividades diárias que exigem destreza manual", False, 0),
    ],
    "Transtorno do Movimento Estereotipado": [
        ("repetitive_sterotyped_movements", "Comportamento motor repetitivo, aparentemente impulsivo e não funcional", True, 0),
        ("stereotype_activity_interference", "O comportamento repetitivo interfere nas atividades normais ou sociais", False, 0),
        ("self_injurious_stereotypy", "Comportamento estereotipado que causa ou pode causar lesão corporal", False, 0),
        ("difficulty_suppressing_movements", "Dificuldade em suprimir ou interromper os movimentos repetitivos", False, 0),
    ],
    "Transtorno de Tourette": [
        ("multiple_motor_tics", "Múltiplos tiques motores (piscar, sacudir, caretas, movimentos de ombros)", True, 365),
        ("vocal_tics", "Um ou mais tiques vocais (grunhidos, pigarrear, palavras, ecolalia)", True, 365),
        ("tic_onset_before_18", "Início dos tiques antes dos 18 anos", True, 0),
        ("tic_duration_one_year", "Presença de tiques por mais de um ano desde o primeiro tique", False, 365),
    ],
    "Transtorno de Tique Motor ou Vocal Crônico": [
        ("chronic_motor_tics", "Tiques motores únicos ou múltiplos presentes por mais de um ano (sem tiques vocais)", True, 365),
        ("chronic_vocal_tics", "Tiques vocais únicos ou múltiplos presentes por mais de um ano (sem tiques motores)", True, 365),
        ("tic_onset_before_18", "Início antes dos 18 anos", True, 0),
        ("tic_duration_one_year", "Tiques presentes por mais de um ano desde o início", False, 365),
    ],
    "Transtorno de Tique Transitório": [
        ("transient_motor_tics", "Tiques motores e/ou vocais presentes há menos de um ano", True, 0),
        ("tic_onset_before_18", "Início antes dos 18 anos", True, 0),
        ("tic_duration_one_year", "Duração inferior a 1 ano desde o início dos tiques", False, 0),
    ],

    # ═══ CHAPTER 2: Espectro da Esquizofrenia e Outros Transtornos Psicóticos ═══
    "Transtorno Delirante": [
        ("delusions", "Presença de um ou mais delírios com duração de um mês ou mais", True, 30),
        ("non_bizarre_delusions", "Delírios não bizarros envolvendo situações da vida real (perseguição, ciúmes, grandiosidade, somáticos)", False, 0),
        ("preserved_functioning", "Funcionamento psicossocial não está acentuadamente prejudicado", False, 0),
        ("social_dysfunction", "Ausência de alucinações proeminentes, discurso desorganizado ou sintomas negativos", False, 0),
    ],
    "Transtorno Psicótico Breve": [
        ("acute_psychotic_symptoms", "Presença de delírios, alucinações, discurso desorganizado ou comportamento catatônico", True, 0),
        ("symptom_duration_1_to_30_days", "Duração dos sintomas de 1 a 30 dias com retorno ao funcionamento pré-mórbido", True, 0),
        ("psychotic_sudden_onset", "Início súbito de sintomas psicóticos", False, 0),
        ("full_functional_recovery", "Recuperação completa do funcionamento pré-mórbido após o episódio", False, 0),
    ],
    "Transtorno Esquizofreniforme": [
        ("hallucinations", "Alucinações, delírios ou discurso desorganizado equivalentes ao Critério A da esquizofrenia", True, 30),
        ("psychotic_symptoms_1_to_6_months", "Sintomas psicóticos presentes de 1 a 6 meses", True, 0),
        ("social_dysfunction", "Prejuízo funcional não é necessário para o diagnóstico, mas pode estar presente", False, 0),
    ],
    "Transtorno Esquizoafetivo": [
        ("delusions", "Delírios ou alucinações por 2+ semanas na ausência de episódio de humor maior", True, 14),
        ("euphoric_mood", "Episódio de humor maior (depressivo ou maníaco) concomitante com sintomas do Critério A de esquizofrenia", True, 0),
        ("psychosis_without_mood", "Sintomas psicóticos presentes na maior parte do curso da doença, mesmo sem sintomas de humor", False, 0),
        ("negative_symptoms", "Sintomas negativos ou desorganização durante períodos psicóticos", False, 0),
    ],
    "Transtorno Psicótico Induzido por Substância": [
        ("substance_induced_psychosis", "Delírios ou alucinações proeminentes decorrentes do uso de substância", True, 0),
        ("substance_psychosis_temporal", "Evidência de desenvolvimento dos sintomas durante ou logo após intoxicação ou abstinência", True, 0),
        ("psychosis_not_primary", "Não é melhor explicado por transtorno psicótico primário", False, 0),
    ],
    "Transtorno Psicótico Devido a Outra Condição Médica": [
        ("medical_condition_psychosis", "Delírios ou alucinações proeminentes consequência direta de condição médica", True, 0),
        ("psychosis_not_primary", "Evidência temporal e fisiológica entre condição médica e desenvolvimento dos sintomas psicóticos", True, 0),
        ("no_substance_etiology", "Não é melhor explicado por transtorno mental, substância ou efeito de medicação", False, 0),
    ],
    "Catatonia": [
        ("catatonic_stupor", "Estupor cataléptico com redução marcante da reatividade e movimentos espontâneos", True, 0),
        ("catatonic_excitement", "Agitação catatônica desproporcional sem influência externa aparente", False, 0),
        ("catatonic_posturing", "Posturação ou flexibilidade cérea (manutenção de posições impostas por outros)", False, 0),
        ("catatonic_mutism", "Mutismo ou negativismo catatônico (resistência a instruções ou estímulos)", False, 0),
        ("echolalia_ecopraxia", "Ecolalia (imitação da fala) ou ecopraxia (imitação de movimentos)", False, 0),
        ("repetitive_sterotyped_movements", "Maneirismos, estereotipias ou caretas", False, 0),
    ],

    # ═══ CHAPTER 3: Transtornos Bipolares e Relacionados ═══
    "Transtorno Ciclotímico": [
        ("hypomanic_subclinical", "Numerosos períodos de sintomas hipomaníacos subclínicos por 2+ anos", True, 720),
        ("depressive_subclinical", "Numerosos períodos de sintomas depressivos subclínicos por 2+ anos", True, 720),
        ("cyclothymic_two_years", "Sintomas presentes por 2+ anos (1 ano em adolescentes) sem período assintomático > 2 meses", False, 720),
        ("no_major_mood_episode", "Sintomas não preenchem critérios para episódio hipomaníaco, maníaco ou depressivo maior", False, 0),
    ],
    "Transtorno Bipolar Induzido por Substância": [
        ("substance_induced_elevated_mood", "Elevação ou irritabilidade proeminente e persistente do humor devido ao uso de substância", True, 0),
        ("euphoric_mood", "Humor elevado, expansivo ou irritável persistente durante intoxicação ou abstinência", False, 0),
        ("not_primary_bipolar", "Não é melhor explicado por transtorno bipolar primário", False, 0),
    ],
    "Transtorno Bipolar Devido a Outra Condição Médica": [
        ("medical_condition_mania", "Elevação ou irritabilidade proeminente e persistente do humor consequência direta de condição médica", True, 0),
        ("euphoric_mood", "Humor elevado, expansivo ou irritável persistente devido a condição médica", False, 0),
        ("increased_energy", "Aumento de energia ou atividade dirigida a objetivos devido a condição médica", False, 0),
    ],

    # ═══ CHAPTER 4: Transtornos Depressivos ═══
    "Transtorno Disruptivo da Desregulação do Humor": [
        ("temper_outbursts_severe", "Explosões de raiva severas e recorrentes (verbais ou físicas) desproporcionais em intensidade e duração", True, 365),
        ("irritable_mood_persistent", "Humor persistentemente irritável ou raivoso na maior parte do dia entre as explosões", True, 365),
        ("outburst_frequency_3x_week", "Explosões de raiva ocorrem 3+ vezes por semana em média", False, 365),
        ("outbursts_multiple_settings", "Explosões presentes em 2+ ambientes (casa, escola, comunidade)", False, 0),
        ("dmd_onset_before_10", "Início dos sintomas antes dos 10 anos de idade", False, 0),
    ],
    "Transtorno Disfórico Pré-Menstrual": [
        ("premenstrual_affective_lability", "Labilidade afetiva, irritabilidade, humor deprimido ou ansiedade na semana pré-menstrual", True, 0),
        ("premenstrual_physical_symptoms", "Sintomas físicos (mastalgia, distensão abdominal, fadiga, cefaleia) na fase lútea", False, 0),
        ("post_menses_remission", "Melhora significativa dos sintomas na semana pós-menstrual", False, 0),
        ("premenstrual_functional_impairment", "Prejuízo no funcionamento social, ocupacional ou acadêmico na fase pré-menstrual", False, 0),
    ],
    "Transtorno Depressivo Induzido por Substância": [
        ("substance_induced_depressed_mood", "Humor deprimido ou anedonia proeminente devido ao uso de substância", True, 0),
        ("depressive_temporal_substance", "Desenvolvimento dos sintomas durante ou logo após intoxicação ou abstinência", True, 0),
        ("not_primary_depression", "Não é melhor explicado por transtorno depressivo primário", False, 0),
    ],
    "Transtorno Depressivo Devido a Outra Condição Médica": [
        ("medical_condition_depression", "Humor deprimido ou anedonia proeminente consequência direta de condição médica", True, 0),
        ("depressed_mood", "Humor deprimido persistente devido a condição médica que não ocorre exclusivamente durante delirium", False, 0),
        ("loss_of_interest", "Redução acentuada de interesse ou prazer devido a condição médica", False, 0),
    ],

    # ═══ CHAPTER 5: Transtornos de Ansiedade ═══
    "Transtorno de Ansiedade de Separação": [
        ("separation_fear", "Medo ou ansiedade excessiva e persistente quanto à separação de figuras de apego", True, 30),
        ("separation_worry_loss", "Preocupação persistente sobre perda, dano ou acidente com figuras de apego", False, 30),
        ("separation_refusal", "Recusa persistente a sair de perto de casa ou figuras de apego (inclusive escola)", False, 30),
        ("separation_physical_symptoms", "Sintomas físicos (náusea, cefaleia, dor abdominal) antecipando a separação", False, 0),
    ],
    "Mutismo Seletivo": [
        ("selective_mutism", "Fala consistentemente ausente em situações sociais específicas onde se espera que fale", True, 30),
        ("speaks_other_settings", "Fala normalmente em outras situações onde a fala é esperada e confortável", True, 0),
        ("mutism_impairment", "O mutismo interfere no funcionamento educacional, ocupacional ou social", False, 0),
        ("selective_mutism_duration", "Duração de 1+ meses (não limitado ao primeiro mês em ambiente novo)", False, 30),
    ],
    "Fobia Específica": [
        ("specific_phobic_fear", "Medo ou ansiedade intensa e persistente em relação a objeto ou situação específica", True, 180),
        ("active_phobic_avoidance", "A situação fóbica é ativamente evitada ou suportada com intensa ansiedade ou sofrimento", False, 180),
        ("fear_disproportional", "Medo desproporcional ao perigo real representado pela situação ou contexto cultural", False, 0),
        ("phobia_6_months", "Medo ou esquiva persistente por 6+ meses", False, 180),
    ],
    "Transtorno de Ansiedade Induzido por Substância": [
        ("substance_induced_anxiety", "Ansiedade ou ataques de pânico proeminentes devido ao uso de substância", True, 0),
        ("anxiety_temporal_substance", "Desenvolvimento dos sintomas durante ou logo após intoxicação ou abstinência", True, 0),
        ("not_primary_anxiety", "Não é melhor explicado por transtorno de ansiedade primário", False, 0),
    ],
    "Transtorno de Ansiedade Devido a Outra Condição Médica": [
        ("medical_condition_anxiety", "Ansiedade ou ataques de pânico consequência direta de condição médica", True, 0),
        ("excessive_worry", "Ansiedade proeminente devido a condição médica (hipertireoidismo, feocromocitoma, arritmia)", False, 0),
        ("not_during_delirium_anxiety", "Sintomas não ocorrem exclusivamente durante delirium", False, 0),
    ],

    # ═══ CHAPTER 6: Transtornos Obsessivo-Compulsivos e Relacionados ═══
    "Transtorno Dismórfico Corporal": [
        ("body_defect_preoccupation", "Preocupação com um ou mais defeitos na aparência que não são observáveis ou parecem menores para outros", True, 0),
        ("appearance_checking", "Comportamentos repetitivos (verificar-se no espelho, comparar-se, camuflar) em resposta à preocupação", False, 0),
        ("appearance_avoidance", "Esquiva de situações sociais que expõem a aparência física", False, 0),
        ("appearance_repetitive_behaviors", "Atos mentais repetitivos em resposta à preocupação com a aparência", False, 0),
    ],
    "Transtorno de Acumulação": [
        ("difficulty_discarding", "Dificuldade persistente em descartar posses independentemente do valor real", True, 0),
        ("need_save_items", "Necessidade percebida de guardar itens e sofrimento intenso ao descartá-los", False, 0),
        ("clutter_impairment", "Acúmulo que compromete o uso funcional de áreas da vida (cozinha, quarto, circulação)", False, 0),
        ("acquiring_excess_items", "Aquisição excessiva de itens não necessários ou sem espaço disponível", False, 0),
    ],
    "Tricotilomania": [
        ("hair_pulling", "Arrancar cabelos recorrentemente, resultando em perda capilar perceptível", True, 0),
        ("attempts_stop_pulling", "Tentativas repetidas de parar ou reduzir o comportamento de arrancar cabelos", True, 0),
        ("hair_loss_result", "Perda capilar (alopecia por tração) visível resultante do ato", False, 0),
        ("hair_pulling_tension", "Sensação crescente de tensão antes de arrancar os cabelos ou ao resistir ao impulso", False, 0),
    ],
    "Transtorno de Escoriação (Skin Picking)": [
        ("skin_picking", "Beliscar a pele recorrentemente, resultando em lesões cutâneas", True, 0),
        ("attempts_stop_picking", "Tentativas repetidas de parar ou reduzir o comportamento de beliscar a pele", True, 0),
        ("skin_lesions", "Lesões cutâneas, cicatrizes ou marcas resultantes do beliscar", False, 0),
        ("skin_picking_tension", "Sensação crescente de tensão antes de beliscar a pele ou ao resistir ao impulso", False, 0),
    ],
    "TOC Induzido por Substância": [
        ("substance_induced_obsessions", "Sintomas obsessivo-compulsivos proeminentes decorrentes do uso de substância", True, 0),
        ("obsessions", "Obsessões ou compulsões que se desenvolveram durante intoxicação ou abstinência", False, 0),
        ("not_primary_ocd", "Não é melhor explicado por TOC primário", False, 0),
    ],

    # ═══ CHAPTER 7: Transtornos Relacionados a Trauma e Estressores ═══
    "Transtorno de Apego Reativo": [
        ("inhibited_withdrawal", "Padrão inibido emocionalmente e retraído em relação a cuidadores", True, 0),
        ("reduced_social_reciprocity", "Reciprocidade social e emocional acentuadamente reduzida com os outros", False, 0),
        ("emotional_regulation_impairment", "Regulação emocional prejudicada com sofrimento mínimo mesmo quando confortado", False, 0),
        ("extreme_insufficient_care", "Cuidados extremamente insuficientes (privação, negligência, mudanças repetidas de cuidador)", True, 0),
    ],
    "Transtorno de Engajamento Social Desinibido": [
        ("indiscriminate_sociability", "Comportamento excessivamente familiar com estranhos, com aproximação ativa", True, 0),
        ("lack_caregiver_checking", "Falta de verificação com o cuidador ao se aproximar ou sair com estranhos", True, 0),
        ("willingness_leave_stranger", "Disposição em sair com estranhos sem hesitação ou permissão", False, 0),
        ("extreme_insufficient_care", "Cuidados extremamente insuficientes (privação social grave, institucionalização)", True, 0),
    ],
    "Transtorno de Estresse Agudo": [
        ("traumatic_exposure_acute", "Exposição a morte real ou ameaçadora, lesão grave ou violência sexual", True, 0),
        ("acute_intrusion", "Sintomas de intrusão (memórias recorrentes, sonhos angustiantes, flashbacks)", False, 0),
        ("acute_dissociation", "Sintomas dissociativos (desrealização, despersonalização, amnésia dissociativa)", False, 0),
        ("acute_avoidance", "Esquiva persistente de estímulos traumáticos (pensamentos, lugares, pessoas)", False, 0),
        ("acute_arousal", "Sintomas de excitação aumentada (hipervigilância, sobressalto, irritabilidade, insônia)", False, 0),
        ("acute_stress_duration", "Duração dos sintomas de 3 dias a 1 mês após exposição ao trauma", True, 0),
    ],
    "Transtornos de Adaptação": [
        ("stressor_response", "Sintomas emocionais ou comportamentais em resposta a estressor identificável", True, 0),
        ("distress_disproportional", "Sofrimento acentuado desproporcional à intensidade do estressor ou prejuízo no funcionamento", False, 0),
        ("adjustment_onset_3_months", "Início dos sintomas dentro de 3 meses após a ocorrência do estressor", False, 0),
        ("adjustment_duration_6_months", "Duração dos sintomas de até 6 meses após o término do estressor ou suas consequências", False, 0),
    ],
    "Transtorno de Luto Prolongado": [
        ("persistent_grief", "Dor intensa e persistente pela morte de alguém próximo há 12+ meses", True, 365),
        ("yearning_for_deceased", "Anseio intenso, saudade profunda e preocupação com o falecido", False, 365),
        ("preoccupation_with_death", "Preocupação com pensamentos, memórias ou circunstâncias da morte", False, 365),
        ("grief_identity_disruption", "Perturbação da identidade com sentimento de descrença e dificuldade em reconectar-se socialmente", False, 0),
        ("emotional_numbness_grief", "Dificuldade em sentir emoções positivas, entorpecimento emocional e solidão intensa", False, 0),
    ],

    # ═══ CHAPTER 8: Transtornos Dissociativos ═══
    "Transtorno Dissociativo de Identidade": [
        ("identity_disruption", "Perturbação da identidade caracterizada por dois ou mais estados de personalidade distintos", True, 0),
        ("memory_gaps_daily", "Lacunas recorrentes na recordação de eventos cotidianos, informações pessoais ou eventos traumáticos", True, 0),
        ("autobiographical_amnesia", "Amnésia para eventos traumáticos ou estressantes incompatível com esquecimento normal", False, 0),
        ("depersonalization", "Sintomas de despersonalização ou desrealização durante estresse", False, 0),
        ("dissociative_flashbacks", "Flashbacks dissociativos ou intrusões de outros estados de personalidade", False, 0),
    ],
    "Amnésia Dissociativa": [
        ("autobiographical_amnesia", "Incapacidade de recordar informações autobiográficas, geralmente traumáticas ou estressantes", True, 0),
        ("memory_gaps_daily", "Lacunas na memória inconsistentes com esquecimento normal", False, 0),
        ("not_neurological_amnesia", "Os sintomas não são atribuíveis a substância, condição neurológica, TEPT ou TDI", False, 0),
    ],
    "Transtorno de Despersonalização/Desrealização": [
        ("depersonalization", "Experiências persistentes de despersonalização (sentir-se fora do corpo, como observador dos próprios processos)", True, 0),
        ("derealization", "Experiências de desrealização (o mundo parece irreal, distante, distorcido ou sonhado)", False, 0),
        ("reality_testing_preserved", "Preservação do senso de realidade durante os episódios (insight preservado)", False, 0),
        ("depersonalization_impairment", "Prejuízo clinicamente significativo no funcionamento social ou ocupacional devido aos sintomas", False, 0),
    ],

    # ═══ CHAPTER 9: Transtornos de Sintomas Somáticos e Relacionados ═══
    "Transtorno de Ansiedade de Doença": [
        ("illness_preoccupation", "Preocupação com ter ou adquirir doença grave, com sintomas somáticos ausentes ou leves", True, 180),
        ("health_anxiety_elevated", "Ansiedade elevada acerca da saúde e do risco de desenvolver doenças", False, 180),
        ("health_checking_behaviors", "Comportamentos excessivos relacionados à saúde (verificação corporal, pesquisas médicas, consultas frequentes)", False, 180),
        ("health_anxiety_6_months", "Preocupação com doença presente por 6+ meses", False, 180),
    ],
    "Transtorno Conversivo (Transtorno de Sintomas Neurológicos Funcionais)": [
        ("functional_neurological_symptoms", "Sintomas neurológicos motores ou sensoriais que alteram a função voluntária ou sensorial", True, 0),
        ("neurological_incompatibility", "Achados clínicos incompatíveis com condições neurológicas conhecidas", True, 0),
        ("functional_motor_symptoms", "Sintomas motores funcionais (fraqueza, tremores, alterações de marcha, quedas, distonia)", False, 0),
        ("functional_sensory_symptoms", "Sintomas sensoriais funcionais (anestesia, alterações visuais, auditivas, dormência)", False, 0),
        ("conversive_seizures", "Crises não-epilépticas psicogênicas ou eventos semelhantes a convulsões", False, 0),
    ],
    "Transtorno Factício": [
        ("symptom_falsification", "Falsificação de sinais ou sintomas físicos ou psicológicos (produção, simulação, exagero)", True, 0),
        ("presenting_as_ill", "Apresenta-se consistentemente como doente, debilitado ou prejudicado", False, 0),
        ("deceptive_behavior", "Comportamento enganoso evidente mesmo sem incentivos externos óbvios (ganhos secundários)", False, 0),
        ("factitious_medical_visits", "História de consultas médicas frequentes, hospitalizações e procedimentos com apresentação inconsistente", False, 0),
    ],
    "Fatores Psicológicos que Afetam Outras Condições Médicas": [
        ("psychological_factors_medical", "Presença de condição médica ou sintoma que é adversamente afetado por fatores psicológicos ou comportamentais", True, 0),
        ("behavior_treatment_impact", "Fatores psicológicos influenciam negativamente o curso, adesão, tratamento ou qualidade de vida", False, 0),
        ("stress_influences_medical", "Estresse emocional, traços de personalidade ou comportamentos de saúde afetam a condição médica", False, 0),
    ],

    # ═══ CHAPTER 10: Transtornos Alimentares ═══
    "Pica": [
        ("non_nutritive_ingestion", "Ingestão persistente de substâncias não nutritivas e não alimentares (terra, papel, gelo, cabelo) por 1+ mês", True, 30),
        ("pica_one_month", "Comportamento alimentar de ingerir substâncias não nutritivas presente por 1+ mês", False, 30),
        ("not_cultural_practice", "A ingestão não é parte de prática cultural ou socialmente normativa", False, 0),
    ],
    "Transtorno de Ruminação": [
        ("food_regurgitation", "Regurgitação repetida de alimentos após a alimentação por 1+ mês", True, 30),
        ("re_chewing_food", "Remastigação, reengolida ou cuspida do alimento regurgitado", False, 30),
        ("not_gastrointestinal", "A regurgitação não é atribuível a condição gastrointestinal (refluxo, estenose)", False, 0),
        ("not_other_eating_disorder", "Não ocorre exclusivamente durante anorexia nervosa, bulimia nervosa ou TAREA", False, 0),
    ],
    "Transtorno Alimentar Restritivo-Evitante": [
        ("restrictive_food_intake", "Perturbação alimentar com restrição significativa (desinteresse por comida, evitação sensorial)", True, 0),
        ("food_sensory_avoidance", "Evitação de alimentos com base em características sensoriais (textura, cheiro, cor, temperatura)", False, 0),
        ("weight_loss_nutritional_deficit", "Perda de peso significativa, déficit nutricional ou dependência de suplementos alimentares", False, 0),
        ("no_weight_shape_concern", "Ausência de preocupação com peso ou forma corporal, diferenciando de anorexia/bulimia", False, 0),
    ],

    # ═══ CHAPTER 11: Transtornos da Eliminação ═══
    "Enurese": [
        ("enuresis_repeated", "Eliminação repetida de urina na cama ou na roupa (involuntária ou intencional)", True, 90),
        ("enuresis_frequency", "Ocorre 2+ vezes por semana por 3+ meses consecutivos", False, 90),
        ("enurese_age_5", "Idade cronológica de 5+ anos (ou nível de desenvolvimento equivalente)", False, 0),
        ("not_medical_enurese", "Não atribuível a condição médica (infecção urinária, diabetes, epilepsia, bexiga neurogênica)", False, 0),
    ],
    "Encoprese": [
        ("encopresis_repeated", "Eliminação repetida de fezes em locais inadequados (involuntária ou intencional)", True, 90),
        ("encopresis_frequency", "1+ episódio por mês por 3+ meses consecutivos", False, 90),
        ("encoprese_age_4", "Idade cronológica de 4+ anos (ou nível de desenvolvimento equivalente)", False, 0),
        ("not_medical_encoprese", "Não atribuível a condição médica (doença de Hirschsprung, constipação crônica, lesão medular)", False, 0),
    ],

    # ═══ CHAPTER 12: Transtornos do Sono-Vigília ═══
    "Transtorno de Hipersonolência": [
        ("excessive_sleepiness_7h", "Sonolência excessiva apesar de sono principal de 7+ horas", True, 90),
        ("irresistible_sleep_episodes", "Períodos recorrentes de sono irresistível ou lapsos de sono durante o dia", False, 90),
        ("hypersomnia_3x_week", "Ocorre 3+ vezes por semana por 3+ meses", False, 90),
        ("non_restorative_sleep", "Sono não restaurador apesar de duração adequada", False, 0),
    ],
    "Narcolepsia": [
        ("irresistible_sleep_attacks", "Ataques recorrentes de sono irresistível 3+ vezes/semana por 3+ meses", True, 90),
        ("cataplexy", "Cataplexia (episódios súbitos de perda bilateral de tônus muscular desencadeados por emoções)", False, 0),
        ("sleep_paralysis", "Paralisia do sono (incapacidade de mover-se ao adormecer ou despertar)", False, 0),
        ("hypnagogic_hallucinations", "Alucinações hipnagógicas ou hipnopômpicas vívidas e frequentemente assustadoras", False, 0),
    ],
    "Apneia Obstrutiva do Sono": [
        ("sleep_apnea_events", "Pausas respiratórias recorrentes durante o sono com esforço respiratório preservado", True, 0),
        ("loud_snoring", "Ronco intenso e alto com pausas respiratórias observadas por terceiros", False, 0),
        ("excessive_daytime_sleepiness_apnea", "Sonolência diurna excessiva, sono não restaurador ou cefaleia matinal", False, 0),
        ("apneia_sono", "Ronco forte com paradas respiratórias durante o sono observadas por terceiros", False, 0),
    ],
    "Apneia Central do Sono": [
        ("central_sleep_apnea", "Pausas respiratórias recorrentes sem esforço respiratório durante o sono", True, 0),
        ("central_apnea_fragmented_sono", "Sono fragmentado devido a despertares recorrentes por apneia central", False, 0),
        ("shortness_of_breath_lying", "Falta de ar ou desconforto respiratório ao deitar", False, 0),
    ],
    "Transtorno do Ritmo Circadiano do Sono-Vigília": [
        ("circadian_rhythm_disruption", "Padrão persistente de perturbação do sono devido a alteração do sistema circadiano", True, 90),
        ("circadian_insomnia_hypersomnia", "Insônia ou sonolência excessiva devido ao desalinhamento circadiano", False, 90),
        ("sleep_wake_misalignment", "Desalinhamento entre o ciclo sono-vigília do indivíduo e o desejado ou socialmente aceito", False, 0),
        ("circadian_duration_3_months", "Duração de 3+ meses", False, 90),
    ],
    "Transtorno do Despertar do Sono Não REM (Sonambulismo)": [
        ("sleepwalking", "Episódios repetidos de levantar e andar durante o sono NREM", True, 0),
        ("sleepwalking_confusion", "Dificuldade em despertar, confusão ou expressão fixa durante o episódio", False, 0),
        ("sleepwalking_amnesia", "Amnésia do evento ao despertar pela manhã", False, 0),
        ("sleepwalking_risk", "Comportamento que causa prejuízo, risco de lesão ou sofrimento significativo", False, 0),
    ],
    "Terror Noturno": [
        ("night_terror_screaming", "Episódios de gritos de medo intenso com despertar parcial do sono NREM", True, 0),
        ("night_terror_inconsolable", "Difícil consolar durante o episódio, com confusão e desorientação significativas", False, 0),
        ("night_terror_amnesia", "Amnésia do episódio ao despertar pela manhã", False, 0),
        ("night_terror_autonomic", "Sinais autonômicos (taquicardia, taquipneia, sudorese) durante o episódio", False, 0),
    ],
    "Transtorno do Pesadelo": [
        ("dysphoric_dreams", "Sonhos extensos, bem lembrados e extremamente disféricos envolvendo ameaça à sobrevivência", True, 0),
        ("nightmare_rapid_orientation", "Rápido despertar do sono com orientação preservada, alerta e sem confusão", False, 0),
        ("nightmare_distress", "Sofrimento clinicamente significativo ou prejuízo no funcionamento diurno (humor, cognição, fadiga)", False, 0),
        ("nightmare_frequency", "Frequência recorrente de pesadelos causando prejuízo na qualidade do sono", False, 0),
    ],
    "Transtorno Comportamental do Sono REM": [
        ("rem_sleep_vocalization", "Vocalização (fala, gritos, risos) durante o sono REM", True, 0),
        ("rem_sleep_movement", "Movimentos complexos durante o sono REM (socos, chutes, saltos, gestos)", False, 0),
        ("dream_enactment", "Comportamentos que representam o conteúdo dos sonhos (geralmente agressivos ou defensivos)", False, 0),
        ("rem_without_tonia", "Polissonografia mostra REM sem atonia muscular (aumento do tônus ou movimentos fásicos)", False, 0),
    ],
    "Síndrome das Pernas Inquietas": [
        ("restless_legs_urge", "Necessidade urgente de mover as pernas acompanhada de sensações desconfortáveis (formigamento, ardor)", True, 0),
        ("rest_leg_worsening", "Piora ou início dos sintomas durante o repouso ou inatividade", False, 0),
        ("movement_leg_improvement", "Melhora parcial ou total das sensações com o movimento (esticar, andar)", False, 0),
        ("leg_symptoms_evening", "Piora dos sintomas no final da tarde ou à noite", False, 0),
        ("restless_legs_3x_week", "Ocorre 3+ vezes por semana", False, 0),
    ],

    # ═══ CHAPTER 13: Disfunções Sexuais ═══
    "Ejaculação Retardada": [
        ("delayed_ejaculation", "Atraso acentuado, infrequência ou ausência de ejaculação em todas as situações", True, 180),
        ("delayed_ejaculation_frequency", "Presente em 75-100% das atividades sexuais com parceiro", False, 180),
        ("delayed_ejaculation_duration", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
    ],
    "Transtorno Erétil": [
        ("erectile_difficulty", "Dificuldade marcante em obter ou manter a ereção até a conclusão da atividade sexual", True, 180),
        ("erectile_frequency", "Presente em 75-100% das oportunidades sexuais", False, 180),
        ("erectile_duration", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
    ],
    "Transtorno do Orgasmo Feminino": [
        ("female_orgasm_delay", "Ausência, atraso acentuado ou redução significativa da intensidade do orgasmo", True, 180),
        ("female_orgasm_frequency", "Presente em 75-100% das oportunidades sexuais", False, 180),
        ("female_orgasm_duration", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
    ],
    "Transtorno do Interesse/Excitação Sexual Feminino": [
        ("reduced_sexual_interest", "Falta ou redução significativa do interesse ou desejo sexual", True, 180),
        ("reduced_sexual_excitation", "Redução da excitação sexual (resposta genital ou não genital)", True, 180),
        ("sexual_interest_duration", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
        ("no_sexual_initiative", "Ausência de iniciação de atividade sexual e receptividade reduzida", False, 0),
    ],
    "Transtorno da Dor Gênito-Pélvica/Penetração": [
        ("pelvic_penetration_pain", "Dor vulvovaginal ou pélvica durante a penetração vaginal ou tentativa de penetração", True, 180),
        ("pelvic_floor_tension", "Tensão ou contração dos músculos do assoalho pélvico durante tentativa de penetração", False, 180),
        ("fear_pelvic_pain", "Medo de dor durante a penetração vaginal ou antecipação", False, 0),
        ("pelvic_pain_duration", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
    ],
    "Transtorno do Desejo Sexual Hipoativo Masculino": [
        ("reduced_male_sexual_desire", "Déficit persistente ou recorrente de desejo ou ideação sexual", True, 180),
        ("male_desire_duration", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
        ("no_sexual_interest_male", "Ausência de iniciativa sexual e receptividade reduzida", False, 0),
    ],
    "Ejaculação Prematura": [
        ("premature_ejaculation", "Ejaculação que ocorre antes ou logo após a penetração (~1 minuto) e antes do desejado", True, 180),
        ("premature_ejaculation_frequency", "Presente em 75-100% das atividades sexuais com parceiro", False, 180),
        ("premature_duration_6_months", "Duração de 6+ meses causando sofrimento clinicamente significativo", False, 180),
    ],

    # ═══ CHAPTER 14: Disforia de Gênero ═══
    "Disforia de Gênero em Crianças": [
        ("gender_incongruence", "Incongruência marcante entre gênero experienciado e gênero designado por 6+ meses", True, 180),
        ("cross_gender_preferences", "Forte preferência por roupas, brinquedos, atividades e papéis do outro gênero", False, 0),
        ("aversion_sex_characteristics", "Aversão às próprias características sexuais ou desejo de tê-las diferentes", False, 0),
        ("desire_be_other_gender", "Forte desejo de ser do outro gênero ou crença de que já é do outro gênero", False, 0),
        ("preference_other_gender_peers", "Forte preferência por brincar com crianças do outro gênero", False, 0),
    ],
    "Disforia de Gênero em Adolescentes e Adultos": [
        ("gender_identity_incongruence_adult", "Incongruência marcante entre gênero experienciado e gênero designado por 6+ meses", True, 180),
        ("desire_remove_sex_characteristics", "Forte desejo de livrar-se das características sexuais primárias ou secundárias", False, 0),
        ("desire_other_gender_treatment", "Forte desejo de ser tratado como o outro gênero ou de pertencer ao outro gênero", False, 0),
        ("conviction_belongs_other_gender", "Convicção de que tem sentimentos e reações típicas do outro gênero", False, 0),
    ],

    # ═══ CHAPTER 15: Transtornos Disruptivos, do Controle de Impulsos e da Conduta ═══
    "Transtorno Opositivo-Desafiador": [
        ("angry_irritable_mood", "Humor raivoso ou irritável na maior parte do tempo", True, 180),
        ("argumentative_defiant", "Comportamento questionador, desafiador ou recusante em relação a figuras de autoridade", False, 180),
        ("vindictiveness", "Comportamento vingativo ou rancoroso (pelo menos 2x nos últimos 6 meses)", False, 180),
        ("odd_behavior_6_months", "Padrão de comportamento presente por 6+ meses com 4+ sintomas", False, 180),
    ],
    "Transtorno Explosivo Intermitente": [
        ("impulsive_aggressive_outbursts", "Explosões comportamentais impulsivas e agressivas (verbais ou físicas) desproporcionais ao estressor", True, 90),
        ("outburst_frequency_3x_week", "Média de 2+ explosões agressivas por semana por 3 meses", False, 90),
        ("outburst_damage", "3+ explosões agressivas que causam dano físico ou destruição de propriedade em 12 meses", False, 365),
        ("outburst_disproportional", "Explosões de raiva desproporcionais em intensidade e duração ao estressor ou provocação", False, 0),
    ],
    "Transtorno da Conduta": [
        ("rights_violation_pattern", "Padrão repetitivo de violação de direitos básicos dos outros, normas ou regras sociais", True, 365),
        ("aggression_people_animals", "Agressão a pessoas ou animais (intimidação, briga física, uso de arma, crueldade)", False, 0),
        ("property_destruction", "Destruição deliberada de propriedade alheia (incêndio, vandalismo)", False, 0),
        ("deceitfulness_theft", "Engano, mentira sistemática ou furto de objetos de valor", False, 0),
        ("serious_rule_violation", "Violação grave de regras (sair de casa à noite sem permissão, fugir, matar aula)", False, 0),
    ],
    "Piromania": [
        ("deliberate_fire_setting", "Incêndio deliberado e intencional em múltiplas ocasiões", True, 0),
        ("tension_before_fire", "Tensão ou excitação afetiva antes do ato de atear fogo", False, 0),
        ("fascination_fire", "Fascínio persistente por fogo, seus contextos, equipamentos e consequências", False, 0),
        ("pleasure_from_fire", "Prazer, satisfação, gratificação ou alívio ao causar incêndios", False, 0),
    ],
    "Cleptomania": [
        ("stealing_impulse", "Falha recorrente em resistir a impulsos de furtar objetos não necessários para uso ou valor", True, 0),
        ("tension_before_theft", "Sensação crescente de tensão afetiva antes do furto", False, 0),
        ("pleasure_during_theft", "Prazer, gratificação ou alívio durante o ato de furtar", False, 0),
        ("stealing_not_anger_revenge", "O furto não é motivado por vingança, raiva, delírio ou alucinação", False, 0),
    ],

    # ═══ CHAPTER 16: Transtornos por Uso de Substâncias e Aditivos ═══
    "Transtorno por Uso de Álcool": [
        ("alcohol_craving", "Fissura ou desejo intenso por álcool", True, 365),
        ("loss_control", "Dificuldade persistente em controlar o consumo de álcool (quantidade, duração)", False, 365),
        ("alcohol_withdrawal", "Síndrome de abstinência alcoólica (hiperatividade autonômica, tremor, insônia, ansiedade, convulsões)", False, 0),
        ("alcohol_tolerance", "Tolerância aumentada (necessidade de quantidades maiores para atingir intoxicação ou efeito desejado)", False, 365),
        ("neglect_activities", "Negligência de atividades sociais, ocupacionais ou recreativas devido ao uso de álcool", False, 365),
        ("use_risco_fisico", "Uso recorrente de álcool em situações de risco físico (dirigir, operar máquinas)", False, 0),
    ],
    "Intoxicação Alcoólica": [
        ("alcohol_intoxication_symptoms", "Sintomas reversíveis após ingestão recente de álcool (fala arrastada, incoordenação, nistagmo)", True, 0),
        ("slurred_speech", "Fala arrastada ou pastosa", False, 0),
        ("motor_incoordination", "Incoordenação motora e prejuízo da marcha", False, 0),
        ("unstable_gait", "Marcha instável ou nistagmo", False, 0),
        ("alcohol_stupor_coma", "Estupor ou coma em casos graves de intoxicação aguda", False, 0),
    ],
    "Abstinência Alcoólica": [
        ("alcohol_withdrawal", "Síndrome de abstinência após cessação ou redução do uso prolongado de álcool", True, 0),
        ("alcohol_withdrawal_tremor", "Tremor de mãos, língua ou pálpebras na abstinência", False, 0),
        ("alcohol_withdrawal_seizures", "Convulsões tônico-clônicas generalizadas na abstinência alcoólica", False, 0),
        ("irritability", "Irritabilidade, ansiedade ou agitação psicomotora na abstinência", False, 0),
        ("alcohol_withdrawal_hallucinations", "Alucinações ou ilusões transitórias (auditivas, visuais, táteis) na abstinência", False, 0),
    ],
    "Transtorno por Uso de Cannabis": [
        ("cannabis_craving", "Fissura ou desejo intenso por cannabis", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de cannabis (quantidade, frequência)", False, 365),
        ("cannabis_withdrawal", "Abstinência (irritabilidade, ansiedade, insônia, diminuição apetite, humor deprimido)", False, 0),
        ("cannabis_tolerance", "Tolerância aumentada à cannabis", False, 365),
        ("neglect_activities", "Negligência de atividades sociais ou ocupacionais devido ao uso de cannabis", False, 365),
        ("use_risco_fisico", "Uso de cannabis em situações de risco físico", False, 0),
    ],
    "Transtorno por Uso de Alucinógenos": [
        ("hallucinogen_craving", "Fissura ou desejo intenso por alucinógenos (LSD, dissociativos, fenciclidina)", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de alucinógenos", False, 365),
        ("tolerance", "Tolerância aumentada (cruzada com outros alucinógenos/dissociativos)", False, 0),
        ("use_continued_despite_problems", "Uso continuado apesar de problemas físicos ou psicológicos recorrentes", False, 365),
    ],
    "Transtorno por Uso de Inalantes": [
        ("inhalant_craving", "Fissura ou desejo intenso por inalantes (hidrocarbonetos voláteis)", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de inalantes", False, 365),
        ("tolerance", "Tolerância aumentada a inalantes", False, 0),
        ("use_continued_despite_problems", "Uso continuado apesar de problemas físicos/psicológicos", False, 365),
    ],
    "Transtorno por Uso de Opioides": [
        ("opioid_craving", "Fissura ou desejo intenso por opioides", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de opioides", False, 365),
        ("opioid_withdrawal", "Abstinência opioide (humor disfórico, náusea, sudorese, midríase, diarreia, insônia)", False, 0),
        ("opioid_tolerance", "Tolerância aumentada a opioides", False, 365),
        ("neglect_activities", "Negligência de atividades sociais ou ocupacionais devido ao uso de opioides", False, 365),
        ("use_risco_fisico", "Uso em situações de risco físico", False, 0),
    ],
    "Transtorno por Uso de Sedativos/Hipnóticos/Ansiolíticos": [
        ("sedative_craving", "Fissura ou desejo intenso por sedativos/benzodiazepínicos", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de sedativos", False, 365),
        ("sedative_withdrawal", "Abstinência (hiperatividade autonômica, tremor, insônia, ansiedade, convulsões, delirium)", False, 0),
        ("sedative_tolerance", "Tolerância aumentada a sedativos", False, 365),
        ("use_risco_fisico", "Uso em situações de risco físico (dirigir, operar máquinas sob efeito)", False, 0),
    ],
    "Transtorno por Uso de Estimulantes": [
        ("stimulant_craving", "Fissura ou desejo intenso por estimulantes (cocaína, anfetaminas, metilfenidato)", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de estimulantes", False, 365),
        ("stimulant_withdrawal", "Abstinência (humor disfórico, fadiga, sonhos vívidos, insônia/hipersonia, aumento apetite)", False, 0),
        ("stimulant_tolerance", "Tolerância aumentada a estimulantes", False, 365),
        ("neglect_activities", "Negligência de atividades sociais ou ocupacionais devido ao uso de estimulantes", False, 365),
    ],
    "Transtorno por Uso de Tabaco": [
        ("tobacco_craving", "Fissura ou desejo intenso por tabaco ou nicotina", True, 365),
        ("loss_control", "Dificuldade em controlar o uso de tabaco", False, 365),
        ("tobacco_withdrawal", "Abstinência (irritabilidade, ansiedade, dificuldade de concentração, aumento do apetite, humor deprimido)", False, 0),
        ("tobacco_tolerance", "Tolerância (perda do efeito estimulante, necessidade de mais cigarros para mesmo efeito)", False, 365),
        ("use_continued_despite_problems", "Uso continuado apesar de problemas físicos (DPOC, doenças cardiovasculares)", False, 0),
    ],
    "Transtorno do Jogo (Jogo Patológico)": [
        ("gambling_preoccupation", "Preocupação com jogo (reviver experiências passadas, planejar apostas futuras, pensar em maneiras de obter dinheiro)", True, 365),
        ("gambling_tolerance", "Necessidade de apostar quantias crescentes de dinheiro para atingir a excitação desejada", False, 365),
        ("gambling_withdrawal", "Inquietação ou irritabilidade ao tentar reduzir ou parar o jogo", False, 0),
        ("gambling_loss_chasing", "Volta no outro dia para recuperar perdas (perseguir perdas) aumentando o prejuízo", False, 0),
        ("gambling_lying", "Mente para esconder o envolvimento com o jogo de familiares, terapeutas ou outros", False, 0),
        ("gambling_financial_dependence", "Depende de outros financeiramente devido ao jogo (empréstimos, venda de bens)", False, 0),
    ],

    # ═══ CHAPTER 17: Transtornos Neurocognitivos ═══
    "Delirium": [
        ("attention_disturbance", "Perturbação na atenção com capacidade reduzida de dirigir, focar, sustentar e desviar a atenção", True, 0),
        ("consciousness_disturbance", "Perturbação na consciência com orientação reduzida ao ambiente", True, 0),
        ("cognitive_deficit_acute", "Déficit cognitivo adicional agudo (memória, orientação, linguagem, percepção, visuoespacial)", False, 0),
        ("delirium_fluctuation", "Início agudo (horas a dias) e flutuação dos sintomas ao longo do dia com piora noturna", False, 0),
        ("delirium_causal_condition", "Evidência de causa fisiológica direta (condição médica, intoxicação, abstinência, toxina)", False, 0),
    ],
    "Transtorno Neurocognitivo Maior": [
        ("cognitive_decline_significant", "Declínio cognitivo significativo em 1+ domínios (atenção complexa, função executiva, memória, linguagem, percepto-motor, cognição social)", True, 0),
        ("daily_activity_dependence", "Os déficits cognitivos interferem na independência nas atividades da vida diária", True, 0),
        ("cognitive_concern", "Preocupação do paciente, informante ou clínico sobre declínio cognitivo", False, 0),
        ("not_during_delirium", "Os sintomas não ocorrem exclusivamente no contexto de delirium", False, 0),
    ],
    "Transtorno Neurocognitivo Leve": [
        ("cognitive_decline_modest", "Declínio cognitivo modesto em 1+ domínios cognitivos", True, 0),
        ("preserved_independence", "Os déficits NÃO interferem na independência nas atividades diárias, mas exigem maior esforço", True, 0),
        ("cognitive_test_decline", "Prejuízo modesto em testes cognitivos padronizados", False, 0),
        ("not_during_delirium", "Não ocorre exclusivamente no contexto de delirium", False, 0),
    ],

    # ═══ CHAPTER 18: Transtornos da Personalidade ═══
    "Transtorno da Personalidade Paranoide": [
        ("paranoid_suspicion", "Suspeita generalizada de que os outros estão explorando, enganando ou prejudicando", True, 0),
        ("distrust_loyalty", "Preocupação com dúvidas sobre lealdade e confiança de amigos e associados", False, 0),
        ("grudges", "Guarda rancor persistentemente e não perdoa insultos, lesões ou desprezos", False, 0),
        ("threat_overreaction", "Reage exageradamente a ameaças percebidas com raiva ou contra-ataque", False, 0),
        ("hidden_meanings", "Percebe significados ocultos e ameaçadores em comentários ou eventos benignos", False, 0),
        ("suspicious_fidelity", "Suspeita recorrente e infundada da fidelidade do parceiro conjugal ou sexual", False, 0),
    ],
    "Transtorno da Personalidade Esquizoide": [
        ("social_detachment", "Distanciamento social com preferência por atividades solitárias e falta de interesse em relacionamentos", True, 0),
        ("emotional_coldness", "Afeto embotado, frieza emocional ou distanciamento afetivo em situações sociais", False, 0),
        ("lack_interest_relationships", "Pouco ou nenhum interesse em relacionamentos próximos, incluindo experiências sexuais", False, 0),
        ("indifference_praise_criticism", "Indiferente a críticas ou elogios de outras pessoas", False, 0),
        ("lack_pleasure", "Prazer em poucas ou nenhuma atividade (anedonia social)", False, 0),
    ],
    "Transtorno da Personalidade Esquizotípica": [
        ("magical_thinking", "Crenças estranhas ou pensamento mágico que influenciam o comportamento (superstições, clarividência, telepatia)", True, 0),
        ("unusual_perceptual_experiences", "Experiências perceptivas incomuns, incluindo ilusões somáticas e corporais", False, 0),
        ("eccentric_behavior", "Comportamento ou aparência excêntrica, peculiar ou incomum", False, 0),
        ("ideas_of_reference", "Ideias de referência (interpretação de eventos casuais como significativos para si, sem delírios)", False, 0),
        ("odd_speech_thinking", "Pensamento e fala estranhos, vagos, circunstanciais, metafóricos ou estereotipados", False, 0),
        ("lack_close_friends", "Ausência de amigos próximos ou confidentes fora da família de primeiro grau", False, 0),
    ],
    "Transtorno da Personalidade Borderline": [
        ("abandonment_fear", "Esforços desesperados para evitar abandono real ou imaginado", True, 0),
        ("unstable_relationships", "Relacionamentos intensos e instáveis com alternância entre idealização e depreciação", False, 0),
        ("identity_disturbance", "Perturbação da identidade com autoimagem ou senso de si acentuadamente instável", False, 0),
        ("impulsivity_borderline", "Impulsividade em pelo menos duas áreas (gastos, sexo, substâncias, direção, alimentação) potencialmente autolesivas", False, 0),
        ("self_harm_behaviors", "Comportamento suicida, gestos suicidas, ameaças ou automutilação recorrentes", False, 0),
        ("emotional_dysregulation_borderline", "Instabilidade afetiva intensa com episódios de disforia, irritabilidade ou ansiedade", False, 0),
        ("chronic_emptiness", "Sensação crônica de vazio interior", False, 0),
    ],
    "Transtorno da Personalidade Histriônica": [
        ("attention_center_need", "Desconforto quando não é o centro das atenções", True, 0),
        ("seductive_behavior", "Comportamento sedutor ou provocativo inadequado ao contexto social", False, 0),
        ("shallow_emotions", "Emoções superficiais que mudam rapidamente e expressão emocional exagerada", False, 0),
        ("appearance_focus_attention", "Usa consistentemente a aparência física para chamar atenção", False, 0),
        ("theatrical_speech", "Fala impressionista e teatral, carente de detalhes", False, 0),
        ("suggestibility", "Sugestionável, facilmente influenciado por outras pessoas ou situações", False, 0),
    ],
    "Transtorno da Personalidade Narcisista": [
        ("grandiosity_narcissistic", "Senso grandioso de autoimportância (exagera realizações, espera ser reconhecido como superior)", True, 0),
        ("admiration_requirement", "Exige admiração excessiva e atenção constante", False, 0),
        ("entitlement", "Sentimento de merecimento especial com expectativas irracionais de tratamento favorável", False, 0),
        ("lack_empathy", "Falta de empatia ou relutância em reconhecer sentimentos e necessidades alheias", False, 0),
        ("exploitative_behavior", "Explora os outros para atingir seus próprios fins", False, 0),
        ("arrogant_attitude", "Atitude arrogante, insolente ou desdenhosa", False, 0),
    ],
    "Transtorno da Personalidade Esquiva": [
        ("social_inhibition", "Inibição social por medo de crítica, rejeição ou desaprovação", True, 0),
        ("inadequacy_feelings", "Sentimentos de inadequação, inferioridade e de ser socialmente inepto", False, 0),
        ("rejection_hypersensitivity", "Hipersensibilidade a avaliação negativa e preocupação com crítica ou rejeição", False, 0),
        ("avoidance_risk_activities", "Reluta em assumir riscos pessoais ou novas atividades para evitar possível vergonha", False, 0),
        ("social_avoidance_desire", "Evita atividades profissionais ou sociais que envolvam contato interpessoal por medo de crítica", False, 0),
    ],
    "Transtorno da Personalidade Dependente": [
        ("decision_difficulty_dependent", "Dificuldade em tomar decisões cotidianas sem conselho e reasseguramento excessivo de outros", True, 0),
        ("responsibility_delegation", "Necessidade excessiva de que outros assumam responsabilidade por áreas importantes da vida", False, 0),
        ("disagreement_fear_dependent", "Dificuldade em expressar discordância por medo de perder apoio ou aprovação", False, 0),
        ("helplessness_alone", "Sentimento de desconforto ou desamparo quando sozinho devido a medo de cuidar de si", False, 0),
        ("urgency_new_relationship", "Termina um relacionamento próximo e busca imediatamente outra relação como fonte de cuidado", False, 0),
    ],
    "Transtorno da Personalidade Obsessivo-Compulsiva": [
        ("order_preoccupation", "Preocupação com detalhes, regras, listas, ordem, organização e horários", True, 0),
        ("perfectionism_interference", "Perfeccionismo que interfere na conclusão de tarefas (falha em cumprir prazos)", False, 0),
        ("work_devotion_excessive", "Dedicação excessiva ao trabalho em detrimento de lazer e relacionamentos", False, 0),
        ("moral_inflexibility", "Inflexibilidade em questões de moral, ética ou valores (conscienciosidade rígida)", False, 0),
        ("delegation_reluctance", "Relutância em delegar tarefas a menos que outros se submetam exatamente ao seu modo de fazer", False, 0),
        ("miserliness", "Avareza em relação a si e aos outros (gastos contidos para si e para pessoas próximas)", False, 0),
    ],
    "Transtorno da Personalidade Antissocial": [
        ("social_norm_violation", "Incapacidade de adequar-se a normas sociais com comportamento repetido que constitui motivo de detenção", True, 0),
        ("deceitfulness_antisocial", "Mentira repetida, uso de pseudônimos ou trapaça para ganho ou prazer pessoal", False, 0),
        ("impulsivity_antisocial", "Impulsividade ou incapacidade de planejar o futuro", False, 0),
        ("aggressiveness_antisocial", "Irritabilidade e agressividade com brigas físicas ou agressões repetidas", False, 0),
        ("recklessness_antisocial", "Desrespeito pela segurança própria ou alheia", False, 0),
        ("irresponsibility_antisocial", "Irresponsabilidade consistente (falha em manter trabalho, obrigações financeiras)", False, 0),
        ("lack_remorse", "Ausência de remorso ou racionalização por ter magoado, maltratado ou furtado", False, 0),
    ],

    # ═══ CHAPTER 19: Transtornos Parafílicos ═══
    "Transtorno Voyeurista": [
        ("voyeuristic_arousal", "Excitação sexual recorrente e intensa ao observar pessoa sem suspeita nua, em atividade sexual ou em atos íntimos", True, 0),
        ("voyeuristic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("voyeuristic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
        ("voyeuristic_action", "O indivíduo agiu com pessoa não consentida OU o desejo causa sofrimento significativo", False, 0),
    ],
    "Transtorno Exhibitionista": [
        ("exhibitionistic_arousal", "Excitação sexual recorrente e intensa pela exposição dos próprios genitais a pessoa sem suspeita", True, 0),
        ("exhibitionistic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("exhibitionistic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
        ("exhibitionistic_action", "O indivíduo agiu com pessoa não consentida OU o desejo causa sofrimento", False, 0),
    ],
    "Transtorno Frotteurista": [
        ("frotteuristic_arousal", "Excitação sexual recorrente e intensa por tocar ou esfregar-se em pessoa não consentida", True, 0),
        ("frotteuristic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("frotteuristic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
        ("frotteuristic_action", "O indivíduo agiu com pessoa não consentida OU o desejo causa sofrimento", False, 0),
    ],
    "Transtorno de Masoquismo Sexual": [
        ("masochistic_arousal", "Excitação sexual recorrente e intensa ao ser humilhado, agredido ou fazer sofrer", True, 0),
        ("masochistic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("masochistic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
    ],
    "Transtorno de Sadismo Sexual": [
        ("sadistic_arousal", "Excitação sexual recorrente e intensa pelo sofrimento físico ou psicológico de outra pessoa", True, 0),
        ("sadistic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("sadistic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
        ("sadistic_action", "O indivíduo agiu com pessoa não consentida OU o desejo causa sofrimento", False, 0),
    ],
    "Transtorno Pedofílico": [
        ("pedophilic_arousal", "Excitação sexual recorrente e intensa por atividade sexual com criança(s) pré-púbere(s) (geralmente ≤ 13 anos)", True, 0),
        ("pedophilic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("pedophilic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
        ("pedophilic_age_16_5", "Idade do indivíduo ≥ 16 anos e ≥ 5 anos mais velho que a criança", True, 0),
    ],
    "Transtorno Fetichista": [
        ("fetishistic_arousal", "Excitação sexual recorrente e intensa por objetos não vivos ou partes do corpo específicas", True, 0),
        ("fetishistic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("fetishistic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
    ],
    "Transtorno Transvéstico": [
        ("transvestic_arousal", "Excitação sexual recorrente e intensa por trajar-se do sexo oposto", True, 0),
        ("transvestic_6_months", "Comportamento ou desejos presentes por 6+ meses", True, 180),
        ("transvestic_distress", "O desejo ou comportamento causa sofrimento ou comprometimento clinicamente significativo", False, 0),
    ],

    # ═══ CORE DISORDERS THAT WERE MISSING DC ═══
    "Transtorno Bipolar Tipo II": [
        ("hypomanic_mood", "Humor hipomaníaco por no mínimo 4 dias consecutivos", True, 4),
        ("mildly_increased_energy", "Energia levemente aumentada e direcionada a objetivos", False, 4),
        ("reduced_sleep_hypomania", "Necessidade reduzida de sono (sentir-se descansado com menos horas)", False, 4),
    ],
    "Transtorno Depressivo Persistente (Distimia)": [
        ("chronic_low_mood", "Humor deprimido crônico na maior parte do dia, na maioria dos dias", True, 730),
        ("poor_appetite_dysthymia", "Apetite reduzido ou hiperfagia", False, 730),
        ("low_self_esteem", "Baixa autoestima crônica", False, 730),
        ("hopelessness", "Sentimentos de desesperança", False, 730),
        ("low_energy_dysthymia", "Baixa energia ou fadiga crônica", False, 730),
    ],
    "Transtorno de Ansiedade Social": [
        ("social_fear", "Medo intenso de uma ou mais situações sociais onde pode ser avaliado", True, 180),
        ("avoidance_social", "Esquiva ativa de situações sociais temidas", False, 180),
        ("performance_anxiety", "Ansiedade intensa relacionada a desempenho em público", False, 180),
        ("blushing", "Reações fisiológicas como rubor, taquicardia ou sudorese em situações sociais", False, 180),
    ],
}

