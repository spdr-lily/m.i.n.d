from datetime import date
from app.core.database import SessionLocal
from app.models.base import (
    PatientIdentity, PatientProfile,
    Symptom, Disorder, AssessmentScale, ScaleQuestion,
    HealthcareProfessional, ClinicalConsultation,
    SymptomObservation, ScaleResponse,
)
from app.repositories import PatientRepository, ConsultationRepository, ScaleRepository, ProfessionalRepository

db = SessionLocal()

def get_or_create_scales():
    repo = ScaleRepository(db)
    phq9 = db.query(AssessmentScale).filter_by(scale_name="PHQ-9").first()
    if not phq9:
        phq9 = repo.create_scale("PHQ-9", "Patient Health Questionnaire — Depressao")
        for i, q in enumerate([
            "Pouco interesse ou prazer em fazer as coisas",
            "Se sentir para baixo, deprimido ou sem esperanca",
            "Dificuldade para pegar no sono ou permanecer dormindo",
            "Se sentir cansado ou com pouca energia",
            "Falta de apetite ou comendo demais",
            "Se sentir mal consigo mesmo — ou que e um falhou",
            "Dificuldade para se concentrar nas coisas",
            "Lentidao para se mover ou falar — ou o contrario",
            "Pensamentos de que seria melhor estar morto",
        ], 1):
            repo.create_question(phq9.scale_id, q, i)
        db.commit()

    gad7 = db.query(AssessmentScale).filter_by(scale_name="GAD-7").first()
    if not gad7:
        gad7 = repo.create_scale("GAD-7", "Generalized Anxiety Disorder — Ansiedade")
        for i, q in enumerate([
            "Se sentir nervoso, ansioso ou muito tenso",
            "Nao conseguir parar de se preocupar",
            "Se preocupar demais com coisas diferentes",
            "Dificuldade para relaxar",
            "Ficar tao agitado que e dificil ficar parado",
            "Ficar facilmente aborrecido ou irritado",
            "Sentir medo como se algo horrivel fosse acontecer",
        ], 1):
            repo.create_question(gad7.scale_id, q, i)
        db.commit()

    mdq = db.query(AssessmentScale).filter_by(scale_name="MDQ").first()
    if not mdq:
        mdq = repo.create_scale("MDQ", "Mood Disorder Questionnaire — Rastreio Bipolar")
        for i, q in enumerate([
            "Sentiu-se tao bem ou tao eufoico que outras pessoas acharam que nao era normal?",
            "Sentiu-se tao irritado que gritava com as pessoas ou comecou briguas?",
            "Sentiu-se muito mais autoconfiante que o normal?",
            "Precisou de muito menos horas de sono que o normal?",
            "Falou muito mais ou mais rapido que o normal?",
            "Os pensamentos aceleravam na sua cabeca?",
            "Distraiu-se facilmente — dificuldade em manter o foco?",
            "Teve muito mais energia que o normal?",
            "Ficou muito mais ativo ou fez muitas coisas ao mesmo tempo?",
            "Ficou muito mais social ou extrovertido que o normal?",
            "Ficou muito mais interessado em sexo que o normal?",
            "Fez coisas que poderiam ter causado problemas (gastos, investimentos, sexo)?",
            "Gastou dinheiro a ponto de causar problemas financeiros?",
        ], 1):
            repo.create_question(mdq.scale_id, q, i)
        db.commit()

    pcl5 = db.query(AssessmentScale).filter_by(scale_name="PCL-5").first()
    if not pcl5:
        pcl5 = repo.create_scale("PCL-5", "PTSD Checklist para DSM-5 — TEPT")
        for i, q in enumerate([
            "Lembrancas repetitivas do evento estressante?",
            "Sonhos angustiantes sobre o evento?",
            "Sentir ou agir como se o evento estivesse acontecendo de novo?",
            "Ficar muito chateado quando algo lembra o evento?",
            "Ter reacoes fisicas fortes quando algo lembra o evento?",
            "Evitar lembrancas ou pensamentos sobre o evento?",
            "Evitar situacoes externas que lembram o evento?",
            "Dificuldade em lembrar partes importantes do evento?",
            "Crencas negativas sobre si mesmo ou sobre o mundo?",
            "Culpar a si mesmo ou aos outros pelo evento?",
            "Sentimentos negativos persistentes (medo, culpa, vergonha)?",
            "Perda de interesse em atividades significativas?",
            "Sentir-se distante ou desconectado das outras pessoas?",
            "Dificuldade em sentir emocoes positivas?",
            "Comportamento irritado ou explosivo?",
            "Comportamento imprudente ou autodestrutivo?",
            "Hipervigilancia?",
            "Sobressalto exagerado?",
            "Dificuldade de concentracao?",
            "Dificuldade para dormir?",
        ], 1):
            repo.create_question(pcl5.scale_id, q, i)
        db.commit()

    ybocs = db.query(AssessmentScale).filter_by(scale_name="Y-BOCS").first()
    if not ybocs:
        ybocs = repo.create_scale("Y-BOCS", "Yale-Brown Obsessive Compulsive Scale — TOC")
        for i, q in enumerate([
            "Tempo gasto com pensamentos obsessivos?",
            "Prejuizo causado pelos pensamentos obsessivos?",
            "Angustia causada pelos pensamentos obsessivos?",
            "Resistencia aos pensamentos obsessivos?",
            "Controle sobre os pensamentos obsessivos?",
            "Tempo gasto com comportamentos compulsivos?",
            "Prejuizo causado pelos comportamentos compulsivos?",
            "Angustia se impedido de fazer as compulsões?",
            "Resistencia aos comportamentos compulsivos?",
            "Controle sobre os comportamentos compulsivos?",
        ], 1):
            repo.create_question(ybocs.scale_id, q, i)
        db.commit()

    audit = db.query(AssessmentScale).filter_by(scale_name="AUDIT").first()
    if not audit:
        audit = repo.create_scale("AUDIT", "Alcohol Use Disorders Identification Test")
        for i, q in enumerate([
            "Com que frequencia consome bebidas alcoolicas?",
            "Quantas doses consome num dia tipico?",
            "Com que frequencia consome 6+ doses numa so ocasiao?",
            "Com que frequencia nao conseguiu parar de beber depois de comecar?",
            "Com que frequencia nao conseguiu fazer o esperado por causa da bebida?",
            "Com que frequencia precisou de uma dose para comecar o dia?",
            "Com que frequencia sentiu culpa ou remorso depois de beber?",
            "Com que frequencia nao lembrou do que aconteceu enquanto bebia?",
            "Alguem ja se feriu ou foi ferido por causa da sua bebida?",
            "Alguem ja sugeriu que voce pare ou reduza a bebida?",
        ], 1):
            repo.create_question(audit.scale_id, q, i)
        db.commit()

    asrm = db.query(AssessmentScale).filter_by(scale_name="ASRM").first()
    if not asrm:
        asrm = repo.create_scale("ASRM", "Altman Self-Rating Mania Scale")
        for i, q in enumerate([
            "Mais alegre ou bem-humorado que o normal?",
            "Mais autoconfiante que o normal?",
            "Dormiu menos que o normal sem sentir cansaco?",
            "Falou mais que o normal?",
            "Esteve tao ativo que outras pessoas estranharam?",
        ], 1):
            repo.create_question(asrm.scale_id, q, i)
        db.commit()

    asrs = db.query(AssessmentScale).filter_by(scale_name="ASRS").first()
    if not asrs:
        asrs = repo.create_scale("ASRS", "Adult ADHD Self-Report Scale v1.1 — Rastreio TDAH adulto")
        for i, q in enumerate([
            "Com que frequencia tem dificuldade para finalizar os detalhes de um projeto?",
            "Com que frequencia tem dificuldade para organizar tarefas?",
            "Com que frequencia tem problemas para lembrar compromissos ou obrigacoes?",
            "Com que frequencia evita ou adia iniciar tarefas que exigem muita concentracao?",
            "Com que frequencia mexe as maos ou pes quando precisa ficar sentado muito tempo?",
            "Com que frequencia se sente excessivamente ativo ou compelido a fazer coisas?",
            "Com que frequencia comete erros por descuido em tarefas entediantes?",
            "Com que frequencia tem dificuldade em manter a atencao em trabalhos repetitivos?",
            "Com que frequencia tem dificuldade em se concentrar no que as pessoas dizem?",
            "Com que frequencia perde ou tem dificuldade em encontrar objetos em casa ou no trabalho?",
            "Com que frequencia se distrai com atividades ou ruidos ao redor?",
            "Com que frequencia se levanta do lugar em reunioes quando deveria ficar sentado?",
            "Com que frequencia se sente inquieto ou agitado?",
            "Com que frequencia tem dificuldade em relaxar quando tem tempo livre?",
            "Com que frequencia fala demais em situacoes sociais?",
            "Com que frequencia completa as frases das pessoas durante conversas?",
            "Com que frequencia tem dificuldade em esperar sua vez?",
            "Com que frequencia interrompe os outros quando estao ocupados?",
        ], 1):
            repo.create_question(asrs.scale_id, q, i)
        db.commit()

    aq10 = db.query(AssessmentScale).filter_by(scale_name="AQ-10").first()
    if not aq10:
        aq10 = repo.create_scale("AQ-10", "Autism Spectrum Quotient 10-item — Rastreio TEA adulto")
        for i, q in enumerate([
            "Frequentemente noto sons suaves que outros nao percebem",
            "Geralmente concentro-me mais no quadro geral do que nos pequenos detalhes",
            "Acho facil fazer mais de uma coisa ao mesmo tempo",
            "Se ha uma interrupcao, consigo voltar rapidamente ao que estava fazendo",
            "Acho facil 'ler entrelinhas' quando alguem esta falando comigo",
            "Sei identificar se alguem esta entediado ao me ouvir",
            "Ao ler uma historia, tenho dificuldade em entender as intencoes dos personagens",
            "Gosto de colecionar informacoes sobre categorias de coisas (carros, passaros etc)",
            "Acho facil saber o que alguem esta pensando ou sentindo so de olhar para seu rosto",
            "Tenho dificuldade em entender as intencoes das pessoas",
        ], 1):
            repo.create_question(aq10.scale_id, q, i)
        db.commit()

    return phq9, gad7, mdq, pcl5, ybocs, audit, asrm, asrs, aq10


def find_patient(name):
    p = db.query(PatientIdentity).filter_by(full_name=name).first()
    return p


def get_profile(patient_uuid):
    return db.query(PatientProfile).filter_by(patient_uuid=patient_uuid).first()


def make_consult(consult_repo, patient_uuid, prof_uuid, dt, symptoms_in, scale_in, notes=""):
    profile = get_profile(patient_uuid)
    if not profile:
        return None

    c = consult_repo.create_consultation(
        profile_uuid=profile.profile_uuid,
        consultation_date=dt,
        professional_uuid=prof_uuid,
        consultation_notes=notes,
    )
    for sid, intensity in symptoms_in:
        consult_repo.create_symptom_observation(
            consultation_uuid=c.consultation_uuid,
            symptom_id=sid,
            intensity=intensity,
            frequency="daily" if intensity >= 2 else "weekly",
            duration_days=30 if intensity >= 2 else 14,
        )
    for qid, val in scale_in:
        consult_repo.create_scale_response(
            consultation_uuid=c.consultation_uuid,
            question_id=qid,
            response_value=val,
            response_text=str(val),
        )
    return c


def main():
    repo = PatientRepository(db)
    consult_repo = ConsultationRepository(db)

    prof = db.query(HealthcareProfessional).first()
    if not prof:
        prof = ProfessionalRepository(db).create("Dra. Ana Oliveira", "CRM-67890", "Psiquiatria")
        db.commit()

    sym_map = {s.symptom_name: s for s in db.query(Symptom).all()}
    phq9, gad7, mdq, pcl5, ybocs, audit, asrm, asrs, aq10 = get_or_create_scales()
    phq9_qs = db.query(ScaleQuestion).filter_by(scale_id=phq9.scale_id).order_by(ScaleQuestion.question_order).all()
    gad7_qs = db.query(ScaleQuestion).filter_by(scale_id=gad7.scale_id).order_by(ScaleQuestion.question_order).all()

    def s(name):
        return sym_map[name].symptom_id

    patients = [
        {
            "name": "Maria Souza",
            "birth": date(1992, 8, 20),
            "sex": 2, "gender": 2, "edu": 3, "eth": 3,
            "marital": "casada", "occ": "Professora",
            "consults": [
                (date(2026, 1, 15), [
                    (s("humor_deprimido"), 3), (s("anhedonia"), 2),
                    (s("insonia_hipersonia"), 3), (s("fadiga"), 2),
                    (s("concentracao"), 2), (s("preocupacao_excessiva"), 2),
                    (s("inquietacao"), 2), (s("tensao_muscular"), 1),
                ], [(q.question_id, 2) for q in phq9_qs[:5]] + [(q.question_id, 1) for q in phq9_qs[5:]] +
                   [(q.question_id, 2) for q in gad7_qs],
                 "Humor deprimido ha 3 semanas. Preocupacoes constantes."),
            ]
        },
        {
            "name": "Joao Pereira",
            "birth": date(1978, 3, 10),
            "sex": 1, "gender": 1, "edu": 3, "eth": 1,
            "marital": "solteiro", "occ": "Analista de TI",
            "consults": [
                (date(2026, 3, 5), [
                    (s("euforia"), 3), (s("grandiosidade"), 3),
                    (s("logorreia"), 2), (s("reducao_sono"), 3),
                    (s("fuga_ideias"), 2), (s("comportamento_risco"), 2),
                    (s("irritabilidade"), 2),
                ], [(q.question_id, 0) for q in phq9_qs] +
                   [(q.question_id, 1) for q in gad7_qs[:3]],
                 "Episodio maniaco agudo ha 1 semana."),
            ]
        },
        {
            "name": "Ana Lucia",
            "birth": date(1995, 11, 28),
            "sex": 2, "gender": 2, "edu": 2, "eth": 3,
            "marital": "solteira", "occ": "Estudante",
            "consults": [
                (date(2026, 2, 10), [
                    (s("palpitacoes"), 3), (s("sudorese"), 2),
                    (s("tremores"), 2), (s("sensacao_sufocamento"), 3),
                    (s("medo_morrer"), 3), (s("preocupacao_excessiva"), 1),
                ], [(q.question_id, 1) for q in phq9_qs[:4]] +
                   [(q.question_id, 3) for q in gad7_qs[:5]],
                 "Crises de panico frequentes ha 2 meses."),
                (date(2026, 3, 1), [
                    (s("palpitacoes"), 2), (s("sensacao_sufocamento"), 2),
                    (s("medo_morrer"), 2), (s("esquiva"), 2),
                ], [(q.question_id, 1) for q in phq9_qs[:3]] +
                   [(q.question_id, 2) for q in gad7_qs[:4]],
                 "Melhora parcial. Ainda evita algumas situacoes."),
            ]
        },
        {
            "name": "Roberto Bueno",
            "birth": date(1988, 7, 5),
            "sex": 1, "gender": 1, "edu": 3, "eth": 1,
            "marital": "casado", "occ": "Policial Militar",
            "consults": [
                (date(2026, 4, 12), [
                    (s("reexperiencia"), 3), (s("esquiva"), 3),
                    (s("hipervigilancia"), 3), (s("insonia_hipersonia"), 2),
                    (s("irritabilidade"), 2), (s("concentracao"), 2),
                ], [(q.question_id, 2) for q in phq9_qs[:6]] +
                   [(q.question_id, 2) for q in gad7_qs[:4]],
                 "Flashbacks diarios apos emboscada ha 4 meses."),
            ]
        },
        {
            "name": "Carla Dias",
            "birth": date(2000, 1, 15),
            "sex": 2, "gender": 2, "edu": 1, "eth": 2,
            "marital": "solteira", "occ": "Estudante",
            "consults": [
                (date(2026, 5, 8), [
                    (s("obsessoes"), 3), (s("compulsoes"), 3),
                    (s("preocupacao_excessiva"), 2), (s("sono_prejudicado"), 1),
                ], [(q.question_id, 2) for q in phq9_qs[:3]] +
                   [(q.question_id, 3) for q in gad7_qs[:3]],
                 "Pensamentos intrusivos e rituais de limpeza ha 2 anos."),
            ]
        },
    ]

    for pdata in patients:
        print(f"\n--- {pdata['name']} ---")
        existing = find_patient(pdata["name"])
        if existing:
            print("  Paciente ja existe, pulando")
            continue

        ident = repo.create_patient_identity(pdata["name"])
        repo.create_patient_profile(
            patient_uuid=ident.patient_uuid,
            birth_date=pdata["birth"],
            sex_type_id=pdata["sex"],
            gender_identity_id=pdata["gender"],
            education_level_id=pdata["edu"],
            ethnicity_id=pdata["eth"],
            marital_status=pdata["marital"],
            occupation=pdata["occ"],
        )
        db.commit()

        for dt, syms, scales, notes in pdata["consults"]:
            c = make_consult(consult_repo, ident.patient_uuid, prof.professional_uuid, dt, syms, scales, notes)
            db.commit()
            print(f"  Consulta em {dt} criada")

    print("\nPopulacao concluida!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
