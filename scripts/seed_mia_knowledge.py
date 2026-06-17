"""Seed MIA knowledge base with common question-answer patterns from clinical data.

Run after the main seeds: db/seed.py, scripts/seed_full_catalog.py.
Idempotent — skips existing knowledge entries.
"""
import json
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, ".")

from sqlalchemy import create_engine, text
from app.core.config import settings

# (trigger_terms list, response_template, disorder_name=None, scale_name=None, confidence=0.7)
KNOWLEDGE_ENTRIES: List[Tuple[List[str], str, str, str, float]] = [
    # --- Depression ---
    (["depressao", "deprimido", "triste"],
     "Transtorno Depressivo Maior é caracterizado por humor deprimido ou perda de interesse "
     "por pelo menos 2 semanas, com pelo menos 5 dos 9 sintomas do DSM-5-TR: humor deprimido, "
     "anedonia, alterações de peso/sono, fadiga, agitação/retardo, culpa, dificuldade de "
     "concentração e pensamentos suicidas. A escala PHQ-9 é recomendada para rastreio.",
     "Transtorno Depressivo Maior", None, 0.8),

    (["depressao", "distimia", "cronico", "persistente"],
     "Transtorno Depressivo Persistente (Distimia) é um humor deprimido crônico que dura "
     "pelo menos 2 anos (1 ano em crianças), com pelo menos 2 dos sintomas: baixo apetite, "
     "insônia/hipersonia, baixa energia, baixa autoestima, dificuldade de concentração e "
     "desesperança. Diferencia-se do TDM pela cronicidade.",
     "Transtorno Depressivo Persistente (Distimia)", None, 0.75),

    # --- Anxiety ---
    (["ansiedade", "ansioso", "preocupado", "nervoso"],
     "Transtorno de Ansiedade Generalizada (TAG) envolve ansiedade e preocupação excessivas "
     "na maioria dos dias por pelo menos 6 meses, com 3+ sintomas: inquietação, fadiga, "
     "dificuldade de concentração, irritabilidade, tensão muscular e alterações do sono. "
     "A escala GAD-7 é recomendada para rastreio.",
     "Transtorno de Ansiedade Generalizada", None, 0.8),

    (["panico", "ataque", "medo", "crise"],
     "Transtorno de Pânico é caracterizado por ataques de pânico recorrentes e inesperados, "
     "seguidos por pelo menos 1 mês de preocupação com novos ataques ou mudança significativa "
     "no comportamento. Sintomas incluem palpitações, sudorese, tremor, falta de ar, dor no "
     "peito, náusea, tontura e medo de morrer ou enlouquecer.",
     "Transtorno de Pânico", None, 0.8),

    (["social", "fobia", "timidez", "julgar", "avaliar"],
     "Transtorno de Ansiedade Social (Fobia Social) é caracterizado por medo ou ansiedade "
     "intensa em situações sociais onde a pessoa pode ser avaliada, durando 6+ meses. "
     "A pessoa teme agir de forma humilhante ou mostrar sintomas de ansiedade. "
     "Situações sociais são evitadas ou suportadas com intenso sofrimento.",
     "Transtorno de Ansiedade Social", None, 0.75),

    (["agorafobia", "sair", "multidao", "espaco fechado"],
     "Agorafobia envolve medo ou ansiedade intensa em 2+ situações: transporte público, "
     "espaços abertos, espaços fechados, multidões ou sair de casa sozinho. A pessoa teme "
     "que possa ser difícil escapar ou obter ajuda. Duração mínima de 6 meses.",
     "Agorafobia", None, 0.7),

    # --- Bipolar ---
    (["bipolar", "mania", "euforia", "humor", "alternancia"],
     "Transtorno Bipolar Tipo I requer pelo menos 1 episódio maníaco (humor elevado/irritável "
     "com energia aumentada por 1+ semanas, causando prejuízo significativo). Episódios "
     "depressivos são comuns mas não necessários para o diagnóstico. "
     "Tipo II requer episódios hipomaníacos (4+ dias, menos grave que mania) + episódios "
     "depressivos maiores. A escala MDQ é usada para rastreio.",
     "Transtorno Bipolar Tipo I", None, 0.8),

    # --- PTSD ---
    (["trauma", "estresse", "ptsd", "evento traumatico", "abuso"],
     "Transtorno de Estresse Pós-Traumático (TEPT) requer exposição a morte real/ameaça, "
     "lesão grave ou violência sexual, seguida por 4 clusters de sintomas por 1+ mês: "
     "reexperiência (flashbacks, pesadelos), esquiva, alterações negativas na cognição/humor "
     "e alterações na reatividade/arousal. A escala PCL-5 é recomendada.",
     "Transtorno de Estresse Pós-Traumático", None, 0.8),

    # --- OCD ---
    (["toc", "obsessivo", "compulsivo", "obsessao", "compulsao", "repeticoes"],
     "Transtorno Obsessivo-Compulsivo (TOC) é caracterizado por obsessões (pensamentos, "
     "impulsos ou imagens recorrentes e intrusivas) e/ou compulsões (comportamentos repetitivos "
     "ou atos mentais que a pessoa se sente compelida a executar). As obsessões causam "
     "ansiedade e as compulsões visam neutralizá-las. Duração: 1+ hora/dia. "
     "A escala Y-BOCS é a referência para gravidade.",
     "Transtorno Obsessivo-Compulsivo", None, 0.8),

    # --- ADHD ---
    (["tdah", "atencao", "hiperatividade", "impulsividade", "concentracao", "foco"],
     "TDAH (Transtorno do Déficit de Atenção com Hiperatividade) requer 6+ sintomas de "
     "desatenção e/ou hiperatividade-impulsividade por 6+ meses, com início antes dos 12 anos, "
     "presentes em 2+ contextos. Sintomas de desatenção: não prestar atenção, erros por "
     "descuido, dificuldade em organizar, distrair-se facilmente. Hiperatividade: inquietação, "
     "não conseguir permanecer sentado, agir como se estivesse 'ligado no motor'. "
     "Escala ASRS para rastreio em adultos.",
     "TDAH", None, 0.75),

    # --- Insomnia ---
    (["insonia", "sono", "dormir", "insonia"],
     "Transtorno de Insônia envolve dificuldade em iniciar ou manter o sono, ou despertar "
     "precoce, por pelo menos 3 noites por semana durante 3+ meses, com prejuízo diurno "
     "significativo (fadiga, irritabilidade, déficit cognitivo).",
     "Transtorno de Insônia", None, 0.7),

    # --- Substance ---
    (["alcool", "bebida", "dependencia", "substancia", "drogas"],
     "Transtorno por Uso de Substâncias é caracterizado por 2+ critérios em 12 meses: "
     "consumo em maiores quantidades, desejo persistente, tempo excessivo obtendo/usando, "
     "fissura (craving), prejuízo em papéis sociais, uso continuado apesar de problemas, "
     "redução de atividades, uso em situações de risco, tolerância e abstinência. "
     "A escala AUDIT é recomendada para rastreio de álcool.",
     "Transtorno por Uso de Substâncias", None, 0.75),

    # --- Eating disorders ---
    (["anorexia", "alimentar", "comer", "peso", "corpo", "magreza"],
     "Anorexia Nervosa envolve restrição energética levando a peso significativamente baixo, "
     "medo intenso de ganhar peso e perturbação na autoavaliação do peso/corporal. "
     "Subtipo: restritivo ou purgativo.",
     "Anorexia Nervosa", None, 0.7),

    (["bulimia", "compulsao", "purga", "vomito", "comer muito"],
     "Bulimia Nervosa envolve episódios recorrentes de compulsão alimentar (comer em 2h "
     "uma quantidade definitivamente maior que o normal) seguidos por comportamentos "
     "compensatórios inapropriados (vômito, laxantes, jejum, exercício excessivo), "
     "pelo menos 1x/semana por 3 meses.",
     "Bulimia Nervosa", None, 0.7),

    (["compulsao alimentar", "binge", "comer emocional"],
     "Transtorno de Compulsão Alimentar Periódica envolve episódios de compulsão alimentar "
     "sem comportamentos compensatórios regulares, com sensação de perda de controle, "
     "comer muito mais rápido que o normal, até sentir desconforto, e sentimento de culpa "
     "após. Pelo menos 1x/semana por 3 meses.",
     "Transtorno de Compulsão Alimentar Periódica", None, 0.7),

    # --- Schizophrenia ---
    (["esquizofrenia", "psicose", "alucinacao", "delirio", "paranoia", "ouvir vozes"],
     "Esquizofrenia requer 2+ sintomas por 1 mês (pelo menos 1 dos 3 primeiros): delírios, "
     "alucinações, discurso desorganizado, comportamento desorganizado/catatônico e sintomas "
     "negativos. Sinais contínuos por 6+ meses, com prejuízo funcional significativo. "
     "Diferencia-se de Transtorno Esquizoafetivo pela ausência de episódios de humor proeminentes.",
     "Esquizofrenia", None, 0.8),

    # --- Autism ---
    (["autismo", "tea", "autista", "espectro"],
     "Transtorno do Espectro Autista (TEA) requer déficits persistentes na comunicação social "
     "e interação social em múltiplos contextos, mais comportamentos restritos e repetitivos, "
     "interesses fixos e hipo/hipersensibilidade sensorial. Sintomas presentes desde o início "
     "da infância. A escala AQ-10 é usada para rastreio em adultos.",
     "Transtorno do Espectro Autista", None, 0.75),

    # --- Somatic ---
    (["somatico", "sintomas fisicos", "dor cronica", "medico", "exames"],
     "Transtorno de Sintomas Somáticos envolve 1+ sintomas somáticos que causam sofrimento "
     "ou prejuízo, com pensamentos desproporcionais sobre a gravidade dos sintomas, "
     "ansiedade elevada sobre a saúde e tempo excessivo dedicado aos sintomas. "
     "Duração mínima de 6 meses.",
     "Transtorno de Sintomas Somáticos", None, 0.7),

    # --- General crisis ---
    (["crise", "ajuda", "urgente", "emergencia"],
     "Se você está em crise, entre em contato imediatamente com:\n"
     "📞 CVV (Centro de Valorização da Vida) — **188**\n"
     "🚑 SAMU — **192**\n"
     "🏥 Procure a emergência psiquiátrica mais próxima.\n\n"
     "Este sistema é uma ferramenta de apoio ao diagnóstico e não substitui "
     "atendimento profissional de urgência.",
     None, None, 0.9),

    # --- Medications ---
    (["medicamento", "medicacao", "remedio", "antidepressivo"],
     "Os principais antidepressivos incluem:\n"
     "• ISRS (Fluoxetina, Sertralina, Escitalopram, Paroxetina) — primeira linha para depressão e ansiedade\n"
     "• IRSN (Venlafaxina, Duloxetina) — depressão + dor crônica\n"
     "• Tricíclicos (Amitriptilina, Nortriptilina) — segunda/terceira linha\n"
     "• Atípicos (Bupropiona, Mirtazapina) — perfil diferencial\n\n"
     "A escolha depende do quadro clínico, comorbidades e perfil de efeitos colaterais. "
     "Consulte um psiquiatra para prescrição.",
     None, None, 0.75),
]


def seed_knowledge(session):
    from app.models.base import Disorder, MIAKnowledge

    count_new = 0
    count_existing = 0

    for terms, template, disorder_name, scale_name, confidence in KNOWLEDGE_ENTRIES:
        trigger_json = json.dumps(terms, ensure_ascii=False)

        existing = session.query(MIAKnowledge).filter(
            MIAKnowledge.trigger_terms == trigger_json
        ).first()
        if existing:
            count_existing += 1
            continue

        disorder_id = None
        if disorder_name:
            disorder = session.query(Disorder).filter(
                Disorder.disorder_name.ilike(f"%{disorder_name}%")
            ).first()
            if disorder:
                disorder_id = disorder.disorder_id

        knowledge = MIAKnowledge(
            trigger_terms=trigger_json,
            response_template=template,
            disorder_id=disorder_id,
            scale_name=scale_name,
            confidence=confidence,
            source="seed",
            times_used=0,
            positive_feedback=0,
            negative_feedback=0,
        )
        session.add(knowledge)
        count_new += 1

    print(f"MIA Knowledge: {count_new} new, {count_existing} existing")
    return count_new


def seed():
    """Main entry point — run from Docker or CLI."""
    from app.core.database import SessionLocal
    from app.models.base import MIAKnowledge
    db = SessionLocal()
    try:
        n = seed_knowledge(db)
        db.commit()
        total = db.query(MIAKnowledge).count()
        print(f"Total MIA Knowledge entries: {total}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
