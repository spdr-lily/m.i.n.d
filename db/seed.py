"""
⚠️  WARNING: CLINICAL DATA (PATIENTS, PROFESSIONALS, CONSULTATIONS) IS SYNTHETIC.
⚠️  Reference data (sex types, ethnicities, symptoms, disorders, medications) is
⚠️  based on real-world classifications. All patient/professional records are
⚠️  procedurally generated for development and testing only.
"""

import sys
from pathlib import Path
from datetime import date
from app.core.database import SessionLocal
from app.models.base import (
    SexType, GenderIdentity, EducationLevel, Ethnicity,
    Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship,
    HealthcareProfessional, Medication, ClassificationAuthority,
)
from app.repositories import AuthRepository
from app.security.hashing import get_password_hash
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.dsm5tr_data import DSM5TR_DISORDERS, CORE_DISORDER_NAMES


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
            EducationLevel(education_level_id=5, code="ESI", description="Ensino Superior Incompleto"),
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
        # ── Reference: Neurodesenvolvimento ──
        ("deficit_intelectual", "Déficits em funções intelectuais (raciocínio, solução de problemas, planejamento, pensamento abstrato)"),
        ("deficit_adaptativo", "Déficits no funcionamento adaptativo resultando em falha em atingir padrões de independência pessoal"),
        ("deficit_social_adaptativo", "Déficit em habilidades sociais e responsabilidade social para a idade"),
        ("inicio_desenvolvimento", "Início no período do desenvolvimento"),
        ("atraso_global_desenvolvimento", "Atraso significativo em múltiplas áreas do desenvolvimento (motora grossa/fina, linguagem, cognição)"),
        ("atraso_motor", "Atraso no desenvolvimento motor grosso ou fino"),
        ("atraso_fala_linguagem", "Atraso na aquisição da fala e linguagem"),
        ("atraso_cognitivo", "Atraso no desenvolvimento cognitivo para a idade"),
        ("atraso_social", "Atraso em habilidades sociais e atividades da vida diária"),
        ("deficit_aquisicao_linguagem", "Dificuldades persistentes na aquisição e uso da linguagem em todas as modalidades"),
        ("deficit_compreensao_linguagem", "Déficit na compreensão da linguagem (vocabulário reduzido)"),
        ("deficit_expressao_linguagem", "Déficit na produção da linguagem (vocabulário limitado, discurso desorganizado)"),
        ("deficit_producao_som_fala", "Dificuldade persistente na produção de sons da fala que interfere na inteligibilidade"),
        ("deficit_inteligibilidade_fala", "Inteligibilidade da fala reduzida impedindo a comunicação verbal"),
        ("gagueira", "Repetições de sons, sílabas ou palavras na fala"),
        ("bloqueio_fala", "Prolongamentos de sons ou bloqueios audíveis/visíveis da fala"),
        ("esquiva_fala", "Substituição de palavras ou circunlóquios para evitar momentos de gagueira"),
        ("deficit_linguagem_pragmatica", "Dificuldades persistentes no uso social da comunicação verbal e não verbal"),
        ("deficit_alternancia_turnos", "Déficit na alternância de turnos conversacionais e saudações"),
        ("deficit_linguagem_nao_literal", "Dificuldade com linguagem não literal (ironia, metáforas)"),
        ("comunicacao_contexto_social", "Dificuldade em adequar a comunicação ao contexto social e à audiência"),
        ("deficit_precisao_leitura", "Precisão de leitura de palavras abaixo do esperado para a idade"),
        ("deficit_compreensao_leitura", "Dificuldade de compreensão do material lido"),
        ("deficit_ortografia", "Dificuldade de ortografia e soletração (erros múltiplos)"),
        ("deficit_expressao_escrita", "Dificuldade na expressão escrita (organização, gramática)"),
        ("deficit_calculo_matematico", "Dificuldade no cálculo e raciocínio matemático"),
        ("deficit_raciocinio_matematico", "Dificuldade na solução de problemas matemáticos e raciocínio quantitativo"),
        ("deficit_coordenacao_motora_grossa", "Habilidades motoras coordenadas substancialmente abaixo do esperado para a idade"),
        ("deficit_coordenacao_motora_fina", "Déficit na coordenação motora fina (escrita manual, uso de tesoura)"),
        ("prejuizo_destrezas_manuais", "Prejuízo no desempenho de atividades diárias que exigem destreza manual"),
        ("atraso_marcos_motores", "Atraso na aquisição de marcos motores (engatinhar, andar, correr)"),
        ("movimentos_repetitivos_estereotipados", "Comportamento motor repetitivo, aparentemente impulsivo e não funcional"),
        ("comportamento_estereotipado_autolesivo", "Comportamento estereotipado que causa ou pode causar lesão corporal"),
        ("interferencia_atividade_estereotipada", "O comportamento repetitivo interfere nas atividades normais ou sociais"),
        ("tiques_motores_multiplos", "Múltiplos tiques motores (piscar, sacudir, caretas)"),
        ("tiques_vocais", "Um ou mais tiques vocais (grunhidos, pigarrear, ecolalia)"),
        ("tiques_duracao_um_ano", "Presença de tiques por mais de um ano desde o primeiro tique"),
        ("tiques_inicio_antes_18", "Início dos tiques antes dos 18 anos"),
        ("tiques_motores_cronicos", "Tiques motores únicos ou múltiplos presentes por mais de um ano (sem tiques vocais)"),
        ("tiques_vocais_cronicos", "Tiques vocais únicos ou múltiplos presentes por mais de um ano (sem tiques motores)"),
        ("tiques_motores_transitorios", "Tiques motores e/ou vocais presentes há menos de um ano"),
        # ── Reference: Psicótico ──
        ("funcionamento_preservado", "Funcionamento psicossocial não está acentuadamente prejudicado"),
        ("delirios_nao_bizarros", "Delírios não bizarros envolvendo situações da vida real"),
        ("sintomas_psicoticos_agudos", "Presença de delírios, alucinações, discurso desorganizado ou comportamento catatônico"),
        ("duracao_sintomas_1_a_30_dias", "Duração dos sintomas de 1 a 30 dias com retorno ao funcionamento pré-mórbido"),
        ("inicio_subito_sintomas_psicoticos", "Início súbito de sintomas psicóticos"),
        ("recuperacao_funcional_completa", "Recuperação completa do funcionamento pré-mórbido após o episódio"),
        ("sintomas_psicoticos_1_a_6_meses", "Sintomas psicóticos presentes de 1 a 6 meses"),
        ("psicose_sem_episodio_humor", "Sintomas psicóticos presentes mesmo sem sintomas de humor"),
        ("psicose_induzida_substancia", "Delírios ou alucinações decorrentes do uso de substância"),
        ("relacao_temporal_substancia_psicose", "Desenvolvimento dos sintomas durante ou logo após intoxicação ou abstinência"),
        ("psicose_nao_primaria", "Não é melhor explicado por transtorno psicótico primário"),
        ("psicose_devido_condicao_medica", "Delírios ou alucinações consequência direta de condição médica"),
        ("sem_etiologia_substancia", "Não é melhor explicado por transtorno mental, substância ou efeito de medicação"),
        ("estupor_catatonico", "Estupor cataléptico com redução marcante da reatividade"),
        ("agitacao_catatonica", "Agitação catatônica desproporcional sem influência externa aparente"),
        ("postura_catatonica", "Posturação ou flexibilidade cérea"),
        ("mutismo_catatonico", "Mutismo ou negativismo catatônico"),
        ("ecolalia_ecopraxia", "Ecolalia (imitação da fala) ou ecopraxia (imitação de movimentos)"),
        # ── Reference: Bipolar ──
        ("sintomas_hipomaniacos_subclinicos", "Numerosos períodos de sintomas hipomaníacos subclínicos por 2+ anos"),
        ("sintomas_depressivos_subclinicos", "Numerosos períodos de sintomas depressivos subclínicos por 2+ anos"),
        ("ciclotimia_dois_anos", "Sintomas presentes por 2+ anos sem período assintomático > 2 meses"),
        ("ausencia_episodio_humor_maior", "Sintomas não preenchem critérios para episódio de humor maior"),
        ("humor_elevado_induzido_substancia", "Elevação ou irritabilidade do humor devido ao uso de substância"),
        ("nao_bipolar_primario", "Não é melhor explicado por transtorno bipolar primário"),
        ("mania_devido_condicao_medica", "Elevação ou irritabilidade do humor consequência direta de condição médica"),
        # ── Reference: Depressivo ──
        ("explosoes_raiva_severas", "Explosões de raiva severas e recorrentes desproporcionais em intensidade"),
        ("frequencia_explosoes_3x_semana", "Explosões de raiva ocorrem 3+ vezes por semana em média"),
        ("humor_irritavel_persistente", "Humor persistentemente irritável entre as explosões"),
        ("explosoes_multiplos_ambientes", "Explosões presentes em 2+ ambientes (casa, escola, comunidade)"),
        ("inicio_tddh_antes_10_anos", "Início dos sintomas antes dos 10 anos de idade"),
        ("labilidade_afetiva_pre_menstrual", "Labilidade afetiva, irritabilidade, humor deprimido na semana pré-menstrual"),
        ("sintomas_fisicos_pre_menstruais", "Sintomas físicos (mastalgia, distensão, fadiga) na fase lútea"),
        ("remissao_pos_menstrual", "Melhora significativa dos sintomas na semana pós-menstrual"),
        ("prejuizo_funcional_pre_menstrual", "Prejuízo no funcionamento social/ocupacional na fase pré-menstrual"),
        ("humor_deprimido_induzido_substancia", "Humor deprimido ou anedonia devido ao uso de substância"),
        ("relacao_temporal_depressao_substancia", "Sintomas depressivos durante intoxicação ou abstinência"),
        ("nao_depressao_primaria", "Não é melhor explicado por transtorno depressivo primário"),
        ("depressao_devido_condicao_medica", "Humor deprimido ou anedonia consequência direta de condição médica"),
        # ── Reference: Ansiedade ──
        ("medo_separacao_figuras_apego", "Medo excessivo e persistente quanto à separação de figuras de apego"),
        ("preocupacao_perda_figuras_apego", "Preocupação com perda ou dano a figuras de apego"),
        ("recusa_separacao_casa", "Recusa a sair de perto de casa ou figuras de apego"),
        ("sintomas_fisicos_separacao", "Náusea, cefaleia, dor abdominal antecipando a separação"),
        ("mutismo_seletivo", "Fala ausente em situações sociais específicas onde se espera que fale"),
        ("fala_em_outros_contextos", "Fala normalmente em outros contextos"),
        ("prejuizo_mutismo_seletivo", "O mutismo interfere no funcionamento educacional, ocupacional ou social"),
        ("duracao_mutismo_seletivo", "Duração de 1+ meses do mutismo"),
        ("medo_fobico_especifico", "Medo intenso e persistente de objeto ou situação específica"),
        ("esquiva_fobica_ativa", "A situação fóbica é ativamente evitada com intensa ansiedade"),
        ("medo_desproporcional_perigo", "Medo desproporcional ao perigo real"),
        ("fobia_seis_meses", "Medo ou esquiva persistente por 6+ meses"),
        ("ansiedade_induzida_substancia", "Ansiedade ou pânico devido ao uso de substância"),
        ("relacao_temporal_ansiedade_substancia", "Ansiedade durante intoxicação ou abstinência"),
        ("nao_ansiedade_primaria", "Não é melhor explicado por transtorno de ansiedade primário"),
        ("ansiedade_devido_condicao_medica", "Ansiedade ou pânico consequência direta de condição médica"),
        ("nao_durante_delirium_ansiedade", "Sintomas não ocorrem exclusivamente durante delirium"),
        # ── Reference: TOC ──
        ("preocupacao_defeitos_aparencia", "Preocupação com defeitos na aparência não observáveis para outros"),
        ("verificacao_aparencia_repetitiva", "Comportamentos repetitivos em resposta à preocupação com a aparência"),
        ("esquiva_situacoes_exposicao", "Esquiva de situações sociais que expõem a aparência física"),
        ("comportamentos_repetitivos_aparencia", "Atos mentais repetitivos em resposta à preocupação com a aparência"),
        ("dificuldade_descartar_objetos", "Dificuldade persistente em descartar posses independentemente do valor"),
        ("necessidade_guardar_itens", "Necessidade de guardar itens e sofrimento ao descartá-los"),
        ("acumulo_compromete_areas_vida", "Acúmulo que compromete o uso funcional de áreas da vida"),
        ("aquisicao_excessiva_itens", "Aquisição excessiva de itens não necessários"),
        ("arrancar_cabelos_recorrente", "Arrancar cabelos recorrentemente resultando em perda capilar"),
        ("tentativas_parar_arrancar_cabelos", "Tentativas repetidas de parar de arrancar cabelos"),
        ("perda_capilar_resultante", "Perda capilar visível resultante"),
        ("tensao_antes_arrancar_cabelos", "Tensão antes de arrancar cabelos"),
        ("beliscar_pele_recorrente", "Beliscar a pele recorrentemente resultando em lesões cutâneas"),
        ("tentativas_parar_beliscar_pele", "Tentativas repetidas de parar de beliscar a pele"),
        ("lesoes_pele_resultantes", "Lesões cutâneas resultantes do beliscar"),
        ("tensao_antes_beliscar_pele", "Tensão antes de beliscar a pele"),
        ("obsessoes_induzidas_substancia", "Sintomas obsessivo-compulsivos decorrentes do uso de substância"),
        ("nao_toc_primario", "Não é melhor explicado por TOC primário"),
        # ── Reference: Trauma ──
        ("padrao_inibido_retraido", "Padrão inibido emocionalmente e retraído em relação a cuidadores"),
        ("reciprocidade_social_reduzida", "Reciprocidade social e emocional acentuadamente reduzida"),
        ("regulacao_emocional_prejudicada", "Regulação emocional prejudicada"),
        ("cuidados_insuficientes_extremos", "Cuidados extremamente insuficientes (privação, negligência)"),
        ("sociabilidade_indiscriminada", "Comportamento excessivamente familiar com estranhos"),
        ("falta_verificacao_cuidador", "Falta de verificação com o cuidador ao sair com estranhos"),
        ("disposicao_sair_estranhos", "Disposição em sair com estranhos sem hesitação"),
        ("exposicao_traumatica_aguda", "Exposição a morte real/ameaçadora, lesão grave ou violência sexual"),
        ("intrusao_aguda_trauma", "Sintomas de intrusão (memórias, sonhos, flashbacks)"),
        ("dissociacao_aguda", "Sintomas dissociativos (desrealização, despersonalização, amnésia)"),
        ("esquiva_aguda", "Esquiva persistente de estímulos traumáticos"),
        ("excitacao_aumentada_aguda", "Hipervigilância, sobressalto, irritabilidade, insônia"),
        ("duracao_3_dias_1_mes", "Duração dos sintomas de 3 dias a 1 mês após exposição ao trauma"),
        ("resposta_estressor_identificavel", "Sintomas emocionais ou comportamentais em resposta a estressor identificável"),
        ("sofrimento_desproporcional_estressor", "Sofrimento desproporcional à intensidade do estressor"),
        ("inicio_3_meses_estressor", "Início dos sintomas dentro de 3 meses após o estressor"),
        ("duracao_6_meses_fim_estressor", "Duração de até 6 meses após o término do estressor"),
        ("dor_intensa_persistente_luto", "Dor intensa e persistente pela morte de alguém próximo há 12+ meses"),
        ("anseio_intenso_falecido", "Anseio intenso e preocupação com o falecido"),
        ("preocupacao_pensamentos_falecido", "Preocupação com memórias ou circunstâncias da morte"),
        ("perturbacao_identidade_luto", "Perturbação da identidade com sentimento de descrença"),
        ("entorpecimento_emocional_luto", "Dificuldade em sentir emoções positivas, entorpecimento emocional"),
        # ── Reference: Dissociativos ──
        ("perturbacao_identidade_estados_personalidade", "Dois ou mais estados de personalidade distintos"),
        ("lacunas_memoria_cotidianas", "Lacunas recorrentes na recordação de eventos cotidianos"),
        ("amnesia_informacoes_autobiograficas", "Amnésia para eventos autobiográficos incompatível com esquecimento normal"),
        ("flashbacks_dissociativos_personalidade", "Flashbacks dissociativos ou intrusões de outros estados"),
        ("nao_amnesia_neurologica", "Não atribuível a condição neurológica"),
        ("teste_realidade_preservado", "Preservação do senso de realidade durante os episódios"),
        ("prejuizo_despersonalizacao", "Prejuízo no funcionamento devido à despersonalização"),
        # ── Reference: Somáticos ──
        ("preocupacao_doenca_grave", "Preocupação com ter doença grave com sintomas leves ou ausentes"),
        ("ansiedade_saude_elevada", "Ansiedade elevada sobre saúde e risco de doenças"),
        ("comportamentos_verificacao_saude", "Verificação corporal e consultas médicas frequentes"),
        ("ansiedade_saude_6_meses", "Preocupação com doença presente por 6+ meses"),
        ("sintomas_neurologicos_funcionais", "Sintomas neurológicos motores ou sensoriais funcionais"),
        ("incompatibilidade_neurologica", "Achados incompatíveis com condições neurológicas conhecidas"),
        ("sintomas_motores_funcionais", "Fraqueza, tremores, alterações de marcha, quedas, distonia"),
        ("sintomas_sensoriais_funcionais", "Anestesia, alterações visuais, auditivas, dormência"),
        ("crises_nao_epilepticas_psicogenicas", "Crises não-epilépticas psicogênicas"),
        ("falsificacao_sinais_sintomas", "Falsificação de sinais ou sintomas físicos ou psicológicos"),
        ("apresentacao_como_doente", "Apresenta-se consistentemente como doente ou debilitado"),
        ("comportamento_enganoso", "Comportamento enganoso sem incentivos externos óbvios"),
        ("consultas_medicas_frequentes_facticias", "Consultas frequentes com apresentação inconsistente"),
        ("fatores_psicologicos_afetam_condicao_medica", "Condição médica afetada adversamente por fatores psicológicos"),
        ("comportamentos_afetam_tratamento", "Fatores psicológicos influenciam negativamente o tratamento"),
        ("estresse_influencia_condicao_medica", "Estresse e comportamentos afetam a condição médica"),
        # ── Reference: Alimentares ──
        ("ingestao_substancias_nao_nutritivas", "Ingestão persistente de substâncias não nutritivas (terra, papel, gelo)"),
        ("pica_um_mes", "Comportamento de ingerir substâncias não nutritivas por 1+ mês"),
        ("nao_pratica_cultural", "A ingestão não é parte de prática cultural"),
        ("regurgitacao_repetida_alimentos", "Regurgitação repetida de alimentos após a alimentação"),
        ("remastigacao_alimentos", "Remastigação do alimento regurgitado"),
        ("nao_condicao_gastrointestinal", "Não atribuível a condição gastrointestinal"),
        ("nao_outro_transtorno_alimentar", "Não ocorre exclusivamente durante anorexia/bulimia/TAREA"),
        ("ingestao_alimentar_restritiva", "Restrição alimentar significativa (desinteresse, evitação sensorial)"),
        ("evitacao_sensorial_alimentos", "Evitação de alimentos por textura, cheiro, cor ou temperatura"),
        ("perda_peso_deficit_nutricional", "Perda de peso significativa ou déficit nutricional"),
        ("ausencia_preocupacao_peso_forma", "Ausência de preocupação com peso ou forma corporal"),
        # ── Reference: Eliminação ──
        ("eliminacao_urina_repetida", "Eliminação repetida de urina na cama ou roupa"),
        ("enurese_frequencia_2x_semana", "Ocorre 2+ vezes por semana por 3+ meses"),
        ("idade_enurese_5_anos", "Idade cronológica de 5+ anos"),
        ("nao_condicao_medica_enurese", "Não atribuível a condição médica"),
        ("eliminacao_fezes_repetida", "Eliminação repetida de fezes em locais inadequados"),
        ("encoprese_frequencia_1x_mes", "1+ episódio por mês por 3+ meses"),
        ("idade_encoprese_4_anos", "Idade cronológica de 4+ anos"),
        ("nao_condicao_medica_encoprese", "Não atribuível a condição médica"),
        # ── Reference: Sono ──
        ("sonolencia_excessiva_7h_sono", "Sonolência excessiva apesar de 7+ horas de sono"),
        ("episodios_sono_irresistiveis", "Períodos recorrentes de sono irresistível durante o dia"),
        ("hipersonia_3x_semana", "Ocorre 3+ vezes por semana"),
        ("sono_nao_restaurador_duracao_adequada", "Sono não restaurador apesar de duração adequada"),
        ("ataques_sono_irresistiveis", "Ataques recorrentes de sono irresistível 3+ vezes/semana"),
        ("cataplexia", "Perda súbita bilateral de tônus muscular desencadeada por emoções"),
        ("paralisia_sono", "Incapacidade de mover-se ao adormecer ou despertar"),
        ("alucinacoes_hipnagogicas", "Alucinações hipnagógicas ou hipnopômpicas"),
        ("pausas_respiratorias_sono", "Pausas respiratórias com esforço respiratório preservado"),
        ("ronco_intenso", "Ronco intenso com pausas observadas por terceiros"),
        ("sonolencia_diurna_excessiva_apneia", "Sonolência diurna por apneia do sono"),
        ("apneia_central_sono", "Pausas respiratórias sem esforço respiratório"),
        ("sono_fragmentado_apneia_central", "Sono fragmentado por apneia central"),
        ("falta_ar_ao_deitar", "Falta de ar ao deitar"),
        ("perturbacao_ritmo_circadiano", "Perturbação do sono por alteração do ritmo circadiano"),
        ("insonia_hipersonia_circadiana", "Insônia ou hipersonia por desalinhamento circadiano"),
        ("desalinhamento_sono_vigilia", "Desalinhamento do ciclo sono-vigília com o desejado"),
        ("duracao_circadiana_3_meses", "Duração de 3+ meses"),
        ("sonambulismo", "Episódios repetidos de andar durante o sono NREM"),
        ("confusao_despertar_sonambulismo", "Confusão durante episódio de sonambulismo"),
        ("amnesia_sonambulismo", "Amnésia do sonambulismo ao despertar"),
        ("risco_sonambulismo", "Comportamento que causa risco de lesão"),
        ("gritos_terror_noturno", "Episódios de gritos de medo intenso durante sono NREM"),
        ("inconsolavel_terror_noturno", "Difícil consolar durante terror noturno"),
        ("amnesia_terror_noturno", "Amnésia do terror noturno ao despertar"),
        ("sinais_autonomicos_terror_noturno", "Taquicardia, taquipneia, sudorese durante terror noturno"),
        ("despertar_rapido_orientado_pesadelo", "Rápido despertar do pesadelo com orientação preservada"),
        ("sofrimento_pesadelos", "Sofrimento ou prejuízo devido a pesadelos"),
        ("frequencia_pesadelos", "Frequência recorrente de pesadelos"),
        ("representacao_comportamental_sonhos", "Comportamentos que representam o conteúdo dos sonhos"),
        ("vocalizacao_sono_rem", "Vocalização (fala, gritos) durante sono REM"),
        ("movimentos_complexos_sono_rem", "Socos, chutes, saltos durante sono REM"),
        ("rem_sem_atonia", "REM sem atonia muscular na polissonografia"),
        ("necessidade_mover_pernas", "Necessidade urgente de mover as pernas com sensações desconfortáveis"),
        ("piora_repouso_pernas", "Piora dos sintomas das pernas durante o repouso"),
        ("melhora_movimento_pernas", "Melhora com o movimento"),
        ("sintomas_pernas_noturnos", "Piora dos sintomas à noite"),
        ("pernas_inquietas_3x_semana", "Ocorre 3+ vezes por semana"),
        # ── Reference: Disfunções Sexuais ──
        ("ejaculacao_retardada", "Atraso acentuado ou ausência de ejaculação"),
        ("frequencia_ejaculacao_retardada", "Presente em 75-100% das atividades sexuais"),
        ("duracao_ejaculacao_retardada", "Duração de 6+ meses"),
        ("dificuldade_erecao", "Dificuldade em obter ou manter a ereção"),
        ("frequencia_disfuncao_eretil", "Presente em 75-100% das oportunidades sexuais"),
        ("duracao_disfuncao_eretil", "Duração de 6+ meses"),
        ("ausencia_retardo_orgasmo_feminino", "Ausência ou atraso do orgasmo feminino"),
        ("frequencia_anorgasmia_feminina", "Presente em 75-100% das oportunidades sexuais"),
        ("duracao_anorgasmia_feminina", "Duração de 6+ meses"),
        ("reducao_interesse_sexual", "Falta ou redução do interesse ou desejo sexual"),
        ("reducao_excitacao_sexual", "Redução da excitação sexual"),
        ("duracao_reducao_interesse_sexual", "Duração de 6+ meses"),
        ("ausencia_iniciativa_sexual", "Ausência de iniciação de atividade sexual"),
        ("dor_penetracao_pelvica", "Dor pélvica durante a penetração vaginal"),
        ("tensao_musculos_pelvicos", "Tensão dos músculos pélvicos na penetração"),
        ("medo_dor_pelvica", "Medo de dor durante a penetração"),
        ("duracao_dor_pelvica", "Duração de 6+ meses"),
        ("reducao_desejo_sexual_masculino", "Déficit persistente de desejo sexual masculino"),
        ("duracao_desejo_hipoativo_masculino", "Duração de 6+ meses"),
        ("ausencia_interesse_sexual_masculino", "Ausência de iniciativa sexual"),
        ("ejaculacao_prematura", "Ejaculação antes do desejado (~1 minuto após penetração)"),
        ("frequencia_ejaculacao_prematura", "Presente em 75-100% das atividades sexuais"),
        ("duracao_ejaculacao_prematura", "Duração de 6+ meses"),
        # ── Reference: Disforia de Gênero ──
        ("incongruencia_genero_experienciado_designado", "Incongruência entre gênero experienciado e designado"),
        ("preferencias_outro_genero", "Preferência por roupas e atividades do outro gênero"),
        ("aversao_caracteristicas_sexuais", "Aversão às próprias características sexuais"),
        ("desejo_ser_outro_genero", "Forte desejo de ser do outro gênero"),
        ("preferencia_pares_outro_genero", "Preferência por brincar com crianças do outro gênero"),
        ("incongruencia_identidade_genero_adulto", "Incongruência entre identidade de gênero e sexo designado"),
        ("desejo_eliminar_caracteristicas_sexuais", "Desejo de livrar-se das características sexuais"),
        ("desejo_tratado_como_outro_genero", "Desejo de ser tratado como o outro gênero"),
        ("conviccao_pertencer_outro_genero", "Convicção de ter reações típicas do outro gênero"),
        # ── Reference: Disruptivos ──
        ("humor_raivoso_irritavel", "Humor raivoso ou irritável na maior parte do tempo"),
        ("comportamento_desafiador_questionador", "Comportamento desafiador em relação a figuras de autoridade"),
        ("comportamento_vingativo", "Comportamento vingativo (pelo menos 2x nos últimos 6 meses)"),
        ("comportamento_6_meses", "Padrão de comportamento presente por 6+ meses"),
        ("explosoes_agressivas_impulsivas", "Explosões agressivas impulsivas desproporcionais"),
        ("explosoes_causam_dano", "3+ explosões com dano físico ou destruição em 12 meses"),
        ("explosoes_desproporcionais", "Explosões desproporcionais em intensidade e duração"),
        ("padrao_violacao_direitos", "Violação repetitiva de direitos básicos e normas sociais"),
        ("agressao_pessoas_animais", "Agressão a pessoas ou animais"),
        ("destruicao_propriedade", "Destruição deliberada de propriedade"),
        ("engano_furto", "Engano, mentira sistemática ou furto"),
        ("violacao_grave_regras", "Violação grave de regras (fugir, matar aula)"),
        ("incendio_deliberado", "Incêndio deliberado em múltiplas ocasiões"),
        ("tensao_antes_fogo", "Tensão antes de atear fogo"),
        ("fascinio_fogo", "Fascínio persistente por fogo"),
        ("prazer_alivio_fogo", "Prazer ou alívio ao causar incêndios"),
        ("impulso_furtar_objetos", "Falha em resistir a impulsos de furtar"),
        ("tensao_antes_furto", "Tensão antes do furto"),
        ("prazer_alivio_durante_furto", "Prazer ou alívio durante o furto"),
        ("furto_nao_vinganca", "Furto não motivado por vingança ou delírio"),
        # ── Reference: Substâncias ──
        ("fissura_alcool", "Fissura ou desejo intenso por álcool"),
        ("fala_arrastada", "Fala arrastada ou pastosa"),
        ("incoordenacao_motora", "Incoordenação motora e prejuízo da marcha"),
        ("marcha_instavel", "Marcha instável ou nistagmo"),
        ("estupor_coma_alcoolico", "Estupor ou coma por intoxicação alcoólica"),
        ("tremor_abstinencia_alcool", "Tremor de mãos na abstinência alcoólica"),
        ("convulsoes_abstinencia_alcool", "Convulsões na abstinência alcoólica"),
        ("alucinacoes_abstinencia_alcool", "Alucinações na abstinência alcoólica"),
        ("fissura_cannabis", "Fissura ou desejo intenso por cannabis"),
        ("abstinencia_cannabis", "Irritabilidade, ansiedade, insônia na abstinência de cannabis"),
        ("tolerancia_cannabis", "Tolerância aumentada à cannabis"),
        ("fissura_alucinogenos", "Fissura por alucinógenos (LSD, dissociativos)"),
        ("uso_continuado_apesar_problemas", "Uso continuado apesar de problemas físicos/psicológicos"),
        ("fissura_inalantes", "Fissura por inalantes (hidrocarbonetos voláteis)"),
        ("fissura_opioides", "Fissura ou desejo intenso por opioides"),
        ("abstinencia_opioides", "Humor disfórico, náusea, sudorese, diarreia na abstinência opioide"),
        ("tolerancia_opioides", "Tolerância aumentada a opioides"),
        ("fissura_benzodiazepinicos", "Fissura por sedativos/benzodiazepínicos"),
        ("abstinencia_benzodiazepinicos", "Insônia, ansiedade, convulsões na abstinência de benzodiazepínicos"),
        ("tolerancia_benzodiazepinicos", "Tolerância aumentada a sedativos"),
        ("fissura_estimulantes", "Fissura por estimulantes (cocaína, anfetaminas)"),
        ("abstinencia_estimulantes", "Humor disfórico, fadiga, insônia na abstinência de estimulantes"),
        ("tolerancia_estimulantes", "Tolerância aumentada a estimulantes"),
        ("fissura_tabaco", "Fissura por tabaco ou nicotina"),
        ("abstinencia_nicotina", "Irritabilidade, ansiedade, aumento do apetite na abstinência de nicotina"),
        ("tolerancia_nicotina", "Tolerância à nicotina"),
        ("preocupacao_jogo", "Preocupação com jogo (reviver, planejar, obter dinheiro)"),
        ("tolerancia_jogo", "Necessidade de apostar mais para a excitação desejada"),
        ("abstinencia_jogo", "Inquietação ou irritabilidade ao reduzir o jogo"),
        ("perseguir_perdas_jogo", "Volta para recuperar perdas, aumentando o prejuízo"),
        ("mentir_jogo", "Mente para esconder o envolvimento com o jogo"),
        ("dependencia_financeira_jogo", "Depende de outros financeiramente devido ao jogo"),
        # ── Reference: Neurocognitivos ──
        ("perturbacao_atencao", "Capacidade reduzida de dirigir e sustentar a atenção"),
        ("perturbacao_consciencia", "Perturbação na consciência e orientação ao ambiente"),
        ("deficit_cognitivo_agudo", "Déficit cognitivo agudo (memória, orientação, linguagem)"),
        ("flutuacao_delirium", "Início agudo e flutuação dos sintomas ao longo do dia"),
        ("causa_fisiologica_delirium", "Evidência de causa fisiológica direta"),
        ("declinio_cognitivo_significativo", "Declínio cognitivo significativo em 1+ domínios"),
        ("dependencia_atividades_diarias", "Déficits interferem na independência diária"),
        ("preocupacao_declinio_cognitivo", "Preocupação do paciente ou clínico sobre declínio cognitivo"),
        ("nao_durante_delirium", "Sintomas não ocorrem exclusivamente durante delirium"),
        ("declinio_cognitivo_modesto", "Declínio cognitivo modesto em 1+ domínios"),
        ("independencia_preservada", "Déficits não interferem na independência, mas exigem esforço"),
        ("prejuizo_testes_cognitivos", "Prejuízo modesto em testes cognitivos padronizados"),
        # ── Reference: Personalidade ──
        ("suspeita_generalizada_exploracao", "Suspeita de que os outros exploram, enganam ou prejudicam"),
        ("duvidas_lealdade_confianca", "Dúvidas sobre lealdade de amigos e associados"),
        ("rancor_persistente", "Guarda rancor sem perdoar insultos ou desprezos"),
        ("reacao_exagerada_ameacas", "Reage exageradamente a ameaças percebidas"),
        ("significados_ocultos", "Percebe significados ameaçadores em eventos benignos"),
        ("suspeita_fidelidade_conjugal", "Suspeita infundada de fidelidade do parceiro"),
        ("distanciamento_social", "Preferência por atividades solitárias"),
        ("falta_interesse_relacionamentos", "Pouco interesse em relacionamentos próximos"),
        ("frieza_emocional_distanciamento", "Afeto embotado e distanciamento afetivo"),
        ("indiferenca_criticas_elogios", "Indiferente a críticas ou elogios"),
        ("prazer_poucas_atividades", "Prazer em poucas atividades (anedonia social)"),
        ("pensamento_magico_crencas_estranhas", "Crenças estranhas ou pensamento mágico"),
        ("experiencias_perceptivas_incomuns", "Experiências perceptivas incomuns"),
        ("comportamento_aparencia_excentrica", "Comportamento ou aparência excêntrica"),
        ("ideias_referencia", "Interpretação de eventos casuais como significativos"),
        ("pensamento_fala_estranhos", "Pensamento e fala vagos, circunstanciais"),
        ("ausencia_amigos_proximos", "Ausência de amigos próximos"),
        ("medo_abandono_esforcos_desesperados", "Esforços para evitar abandono real ou imaginado"),
        ("relacionamentos_instaveis_intensos", "Relacionamentos instáveis com idealização e depreciação"),
        ("perturbacao_identidade_autoimagem", "Autoimagem acentuadamente instável"),
        ("impulsividade_multiplas_areas", "Impulsividade em gastos, sexo, substâncias"),
        ("comportamento_suicida_automutilacao", "Automutilação ou comportamento suicida recorrente"),
        ("instabilidade_afetiva_intensa", "Instabilidade afetiva com episódios de disforia"),
        ("vazio_cronico", "Sensação crônica de vazio interior"),
        ("necessidade_centro_atencao", "Desconforto quando não é o centro das atenções"),
        ("comportamento_sedutor_inadequado", "Comportamento sedutor inadequado ao contexto"),
        ("emocoes_superficiais_mudancas_rapidas", "Emoções superficiais que mudam rapidamente"),
        ("aparencia_fisica_chamar_atencao", "Usa a aparência para chamar atenção"),
        ("fala_teatral_impressionista", "Fala teatral carente de detalhes"),
        ("sugestionabilidade", "Facilmente influenciado por outros"),
        ("grandiosidade_senso_importancia", "Senso grandioso de autoimportância"),
        ("exige_admiracao_excessiva", "Exige admiração excessiva"),
        ("sentimento_merecimento_especial", "Sentimento de merecimento especial"),
        ("falta_empatia", "Falta de empatia ou relutância em reconhecer sentimentos alheios"),
        ("exploracao_outros_fins_proprios", "Explora outros para fins próprios"),
        ("atitude_arrogante_insolente", "Atitude arrogante e insolente"),
        ("inibicao_social_medo_critica", "Inibição social por medo de crítica ou rejeição"),
        ("sentimentos_inadequacao_inferioridade", "Sentimentos de inadequação e inferioridade"),
        ("hipersensibilidade_avaliacao_negativa", "Hipersensibilidade a avaliação negativa"),
        ("esquiva_riscos_pessoais_vergonha", "Reluta em assumir riscos pessoais"),
        ("dificuldade_decisoes_sem_conselho", "Dificuldade em tomar decisões sem conselho"),
        ("delegacao_responsabilidades_outros", "Delega responsabilidades a outros"),
        ("medo_discordar_perda_apoio", "Medo de discordar por perda de apoio"),
        ("desamparo_sozinho", "Desamparo quando sozinho"),
        ("urgencia_novo_relacionamento", "Busca imediata de nova relação ao terminar uma"),
        ("preocupacao_detalhes_regras_ordem", "Preocupação com detalhes, regras e ordem"),
        ("perfeccionismo_interfere_tarefas", "Perfeccionismo que interfere na conclusão de tarefas"),
        ("dedicacao_excessiva_trabalho", "Dedicação excessiva ao trabalho em detrimento do lazer"),
        ("inflexibilidade_moral_etica", "Inflexibilidade em questões morais"),
        ("relutancia_delegar_tarefas", "Relutância em delegar tarefas"),
        ("avareza", "Avareza em relação a si e aos outros"),
        ("incapacidade_adequar_normas_sociais", "Incapacidade de adequar-se a normas sociais"),
        ("mentira_repetida_trapaca", "Mentira repetida e trapaça"),
        ("impulsividade_incapacidade_planejar", "Impulsividade sem planejamento"),
        ("irritabilidade_agressividade", "Irritabilidade e agressividade com brigas"),
        ("desrespeito_seguranca_propria_alheia", "Desrespeito pela segurança própria ou alheia"),
        ("irresponsabilidade_consistente", "Irresponsabilidade no trabalho e obrigações"),
        ("ausencia_remorso", "Ausência de remorso por ter magoado ou furtado"),
        # ── Reference: Parafílicos ──
        ("excitacao_sexual_observar_pessoa_suspeita", "Excitação ao observar pessoa sem suspeita"),
        ("sofrimento_comportamento_voyeurista", "Sofrimento pelo comportamento voyeurista"),
        ("voyeurismo_seis_meses", "Comportamento voyeurista por 6+ meses"),
        ("excitacao_exposicao_genitais", "Excitação pela exposição dos genitais"),
        ("sofrimento_comportamento_exhibitionista", "Sofrimento pelo exibicionismo"),
        ("exibicionismo_seis_meses", "Comportamento exibicionista por 6+ meses"),
        ("excitacao_tocar_esfregar_pessoa", "Excitação por tocar/esfregar-se em pessoa"),
        ("sofrimento_comportamento_frotteurista", "Sofrimento pelo frotteurismo"),
        ("frotteurismo_seis_meses", "Comportamento frotteurista por 6+ meses"),
        ("excitacao_ser_humilhado_agredido", "Excitação por ser humilhado ou agredido"),
        ("sofrimento_masoquismo_sexual", "Sofrimento pelo masoquismo sexual"),
        ("masoquismo_sexual_seis_meses", "Masoquismo sexual por 6+ meses"),
        ("excitacao_sofrimento_outra_pessoa", "Excitação pelo sofrimento de outra pessoa"),
        ("sofrimento_sadismo_sexual", "Sofrimento pelo sadismo sexual"),
        ("sadismo_sexual_seis_meses", "Sadismo sexual por 6+ meses"),
        ("excitacao_atividade_sexual_crianca", "Excitação por atividade sexual com criança pré-púbere"),
        ("sofrimento_pedofilia", "Sofrimento pela pedofilia"),
        ("pedofilia_seis_meses", "Pedofilia por 6+ meses"),
        ("idade_pedofilia_16_5_anos", "Idade >= 16 anos e >= 5 anos mais velho que a criança"),
        ("excitacao_objetos_nao_vivos", "Excitação por objetos não vivos"),
        ("sofrimento_fetichismo", "Sofrimento pelo fetichismo"),
        ("fetichismo_seis_meses", "Fetichismo por 6+ meses"),
        ("excitacao_trajar_sexo_oposto", "Excitação por trajar-se do sexo oposto"),
        ("sofrimento_transvestismo", "Sofrimento pelo transvestismo"),
        ("transvestismo_seis_meses", "Transvestismo por 6+ meses"),
    # ── Missing keys from verification ──
    ("sintomas_intoxicacao_alcool", "Sintomas reversíveis após ingestão recente de álcool"),
    ("tolerancia_alcool", "Necessidade de quantidades maiores de álcool para efeito desejado"),
    ("despersonalizacao_fora_corpo", "Experiências de despersonalização (sentir-se fora do corpo)"),
    ("dificuldade_suprimir_movimentos", "Dificuldade em suprimir movimentos repetitivos"),
    ("exibicionismo_acao", "Agir com pessoa não consentida para excitação exibicionista"),
    ("frotteurismo_acao", "Agir com pessoa não consentida para excitação frotteurista"),
    ("linguagem_abaixo_idade", "Capacidades linguísticas abaixo do esperado para a idade"),
    ("sadismo_acao", "Agir com pessoa não consentida para excitação sádica"),
    ("esquiva_social_desejo", "Evita atividades profissionais ou sociais por medo de crítica"),
    ("prejuizo_comunicacao_social", "Prejuízo na comunicação social devido a erros na fala"),
    ("ansiedade_gagueira", "Ansiedade ou prejuízo na comunicação social devido à gagueira"),
    ("voyeurismo_acao", "Agir observando pessoa não consentida para excitação voyeurista"),
    # ── Missed by verification (Phase 4 detected) ──
    ("abstinencia_alcool", "Síndrome fisiológica de abstinência após cessação do álcool"),
    ("sonhos_disfóricos_extensos", "Sonhos prolongados, angustiantes e bem lembrados"),
    # ── Residual / unspecified disorder symptom keys ──
    ("distress_impairment_symptoms", "Sintomas característicos de transtorno mental que causam sofrimento ou prejuízo clinicamente significativo"),
    ("clinician_specifies_reason", "O clínico opta por especificar a razão pela qual os critérios não são totalmente preenchidos"),
    ("exclude_primary_disorder", "Os sintomas não são mais bem explicados por outro transtorno mental"),
    ("insufficient_information", "Não há informação suficiente para fazer um diagnóstico mais específico"),
    ("emergency_context", "Em contextos de emergência onde não é possível determinar se os sintomas são primários ou induzidos"),
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

    # --- All DSM-5-TR disorders (~157) ---
    disorders_data = DSM5TR_DISORDERS

    disorder_objects = {}
    for name, cid, dsm, chapter, desc, _ in disorders_data:
        existing = db.query(Disorder).filter_by(disorder_name=name).first()
        if not existing:
            d = Disorder(
                disorder_name=name, cid_code=cid, dsm_code=dsm,
                dsm_chapter=chapter, disorder_description=desc,
            )
            db.add(d)
            db.flush()
            disorder_objects[name] = d
        else:
            existing.dsm_chapter = chapter
            disorder_objects[name] = existing

    db.commit()
    print(f"OK - {len(disorders_data)} transtornos DSM-5-TR inseridos")

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

    # --- Additional role-based users ---
    role_users = [
        ("clinician", "clinician", "Dr. Carlos Silva (Clínico)", "clinician"),
        ("psychiatrist", "psychiatrist", "Dra. Mariana Costa (Psiquiatra)", "psychiatrist"),
        ("psychologist", "psychologist", "Dr. Fernando Oliveira (Psicólogo)", "psychologist"),
        ("researcher", "researcher", "Dra. Patrícia Santos (Pesquisadora)", "researcher"),
        ("clinical_supervisor", "supervisor", "Dr. Eduardo Martins (Supervisor)", "clinical_supervisor"),
        ("viewer", "viewer", "Maria Oliveira (Visualizadora)", "viewer"),
    ]
    for username, password, full_name, role in role_users:
        existing = repo.get_by_username(username)
        if not existing:
            repo.create_user(
                username=username,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                role=role,
            )
            print(f"OK - Usuario {username} criado")
        else:
            print(f"OK - Usuario {username} ja existe")

    # --- Medications ---
    common_medications = [
        # Antidepressivos
        ("Fluoxetina", "Fluoxetina", "Antidepressivo (ISRS)"),
        ("Sertralina", "Sertralina", "Antidepressivo (ISRS)"),
        ("Escitalopram", "Escitalopram", "Antidepressivo (ISRS)"),
        ("Paroxetina", "Paroxetina", "Antidepressivo (ISRS)"),
        ("Citalopram", "Citalopram", "Antidepressivo (ISRS)"),
        ("Venlafaxina", "Venlafaxina", "Antidepressivo (ISRSN)"),
        ("Desvenlafaxina", "Desvenlafaxina", "Antidepressivo (ISRSN)"),
        ("Duloxetina", "Duloxetina", "Antidepressivo (ISRSN)"),
        ("Bupropiona", "Bupropiona", "Antidepressivo (NDRI)"),
        ("Mirtazapina", "Mirtazapina", "Antidepressivo (NaSSA)"),
        ("Trazodona", "Trazodona", "Antidepressivo (SARI)"),
        ("Agomelatina", "Agomelatina", "Antidepressivo (Melatonérgico)"),
        ("Amitriptilina", "Amitriptilina", "Antidepressivo (Tricíclico)"),
        ("Nortriptilina", "Nortriptilina", "Antidepressivo (Tricíclico)"),
        ("Clomipramina", "Clomipramina", "Antidepressivo (Tricíclico)"),
        ("Imipramina", "Imipramina", "Antidepressivo (Tricíclico)"),
        # Antipsicóticos
        ("Risperidona", "Risperidona", "Antipsicótico (Atípico)"),
        ("Olanzapina", "Olanzapina", "Antipsicótico (Atípico)"),
        ("Quetiapina", "Quetiapina", "Antipsicótico (Atípico)"),
        ("Aripiprazol", "Aripiprazol", "Antipsicótico (Atípico)"),
        ("Clozapina", "Clozapina", "Antipsicótico (Atípico)"),
        ("Paliperidona", "Paliperidona", "Antipsicótico (Atípico)"),
        ("Ziprasidona", "Ziprasidona", "Antipsicótico (Atípico)"),
        ("Haloperidol", "Haloperidol", "Antipsicótico (Típico)"),
        ("Clorpromazina", "Clorpromazina", "Antipsicótico (Típico)"),
        # Estabilizadores de Humor
        ("Carbonato de Lítio", "Lítio", "Estabilizador de Humor"),
        ("Valproato de Sódio", "Valproato", "Estabilizador de Humor"),
        ("Lamotrigina", "Lamotrigina", "Estabilizador de Humor"),
        ("Carbamazepina", "Carbamazepina", "Estabilizador de Humor"),
        ("Oxcarbazepina", "Oxcarbazepina", "Estabilizador de Humor"),
        ("Topiramato", "Topiramato", "Estabilizador de Humor"),
        # Ansiolíticos
        ("Clonazepam", "Clonazepam", "Ansiolítico (Benzodiazepínico)"),
        ("Alprazolam", "Alprazolam", "Ansiolítico (Benzodiazepínico)"),
        ("Diazepam", "Diazepam", "Ansiolítico (Benzodiazepínico)"),
        ("Lorazepam", "Lorazepam", "Ansiolítico (Benzodiazepínico)"),
        ("Buspirona", "Buspirona", "Ansiolítico (Não Benzodiazepínico)"),
        # Psicoestimulantes
        ("Metilfenidato", "Metilfenidato", "Psicoestimulante"),
        ("Lisdexanfetamina", "Lisdexanfetamina", "Psicoestimulante"),
        ("Atomoxetina", "Atomoxetina", "Psicoestimulante (Não Estimulante)"),
        ("Guanfacina", "Guanfacina", "Psicoestimulante (Não Estimulante)"),
        # Hipnóticos
        ("Zolpidem", "Zolpidem", "Hipnótico"),
        ("Melatonina", "Melatonina", "Hipnótico"),
        ("Doxepina", "Doxepina", "Hipnótico (Antidepressivo em baixa dose)"),
        # Antidemência
        ("Donepezila", "Donepezila", "Anticolinesterásico (Demência)"),
        ("Rivastigmina", "Rivastigmina", "Anticolinesterásico (Demência)"),
        ("Memantina", "Memantina", "Antagonista NMDA (Demência)"),
        ("Galantamina", "Galantamina", "Anticolinesterásico (Demência)"),
        # Tratamento para Dependência Química
        ("Naltrexona", "Naltrexona", "Tratamento Dependência Química"),
        ("Acamprosato", "Acamprosato", "Tratamento Dependência Química"),
        ("Dissulfiram", "Dissulfiram", "Tratamento Dependência Química"),
        ("Buprenorfina", "Buprenorfina", "Tratamento Dependência Química"),
        ("Vareniclina", "Vareniclina", "Tratamento Dependência Química"),
        # Anticolinérgicos
        ("Biperideno", "Biperideno", "Anticolinérgico"),
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
