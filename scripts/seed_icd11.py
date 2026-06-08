"""Seed CID-11 (ICD-11) codes for all 16 disorders."""
from app.core.database import SessionLocal
from app.models.base import Disorder, ICD11Code


# Map ICD-11 short codes to Portuguese disorder names for DB lookup
SHORT_TO_PT = {
    "MDD": "Transtorno Depressivo Maior",
    "GAD": "Transtorno de Ansiedade Generalizada",
    "PANIC": "Transtorno do Pânico",
    "AGORAPHOBIA": "Agorafobia",
    "BIPOLAR": "Transtorno Bipolar Tipo I",
    "OCD": "Transtorno Obsessivo-Compulsivo",
    "PTSD": "Transtorno de Estresse Pós-Traumático",
    "SUD": "Transtorno por Uso de Substâncias",
    "ANOREXIA": "Anorexia Nervosa",
    "BULIMIA": "Bulimia Nervosa",
    "BED": "Transtorno de Compulsão Alimentar",
    "INSOMNIA": "Transtorno de Insônia",
    "PSYCHOTIC": "Esquizofrenia / Transtorno Psicótico",
    "SOMATIC": "Transtorno de Sintomas Somáticos",
    "ASD": "Transtorno do Espectro Autista",
    "ADHD": "Transtorno de Déficit de Atenção/Hiperatividade",
}

ICD11_DATA = {
    "MDD": {
        "code": "6A70.2",
        "title": "Major depressive disorder, single episode, moderate",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Major depressive disorder is characterized by at least two weeks of depressed mood "
            "or loss of interest or pleasure, accompanied by other symptoms such as changes in "
            "appetite or sleep, psychomotor changes, fatigue, feelings of worthlessness, and "
            "difficulty concentrating."
        ),
        "diagnostic_requirements": (
            "At least 5 of 9 symptoms including depressed mood or loss of interest. Symptoms "
            "present most of the day, nearly every day for at least 2 weeks. Symptoms cause "
            "clinically significant distress or impairment."
        ),
    },
    "GAD": {
        "code": "6B00",
        "title": "Generalized anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Generalized anxiety disorder is characterized by marked symptoms of anxiety that "
            "persist for at least several months, manifested by general apprehension or excessive "
            "worry about multiple everyday events or problems."
        ),
        "diagnostic_requirements": (
            "Symptoms of anxiety and worry occurring more days than not for at least several months. "
            "Associated symptoms include restlessness, fatigue, difficulty concentrating, irritability, "
            "muscle tension, or sleep disturbance."
        ),
    },
    "PANIC": {
        "code": "6B01",
        "title": "Panic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Panic disorder is characterized by recurrent unexpected panic attacks that are not "
            "restricted to particular stimuli or situations."
        ),
        "diagnostic_requirements": (
            "Recurrent unexpected panic attacks with persistent concern about additional attacks. "
            "Not better explained by another mental disorder."
        ),
    },
    "AGORAPHOBIA": {
        "code": "6B02",
        "title": "Agoraphobia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Agoraphobia is characterized by marked and excessive fear or anxiety about being in "
            "multiple situations where escape or help might not be available."
        ),
        "diagnostic_requirements": (
            "Fear or avoidance of 2+ situations (public transport, open spaces, enclosed spaces, "
            "crowds, being outside home alone). Symptoms persist for at least several months."
        ),
    },
    "BIPOLAR": {
        "code": "6A60",
        "title": "Bipolar type I disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Bipolar type I disorder is characterized by at least one manic episode, an extreme "
            "mood state lasting at least 1 week with elevated mood and increased activity or energy."
        ),
        "diagnostic_requirements": (
            "At least one manic episode lasting 1 week (or requiring hospitalization). Manic episode "
            "defined by elevated/expansive/irritable mood plus 3+ associated symptoms."
        ),
    },
    "OCD": {
        "code": "6B20",
        "title": "Obsessive-compulsive disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Obsessive-compulsive disorder is characterized by persistent obsessions or compulsions "
            "that are time-consuming or cause marked distress or functional impairment."
        ),
        "diagnostic_requirements": (
            "Presence of obsessions and/or compulsions that are time-consuming (1+ hour/day) or "
            "cause clinically significant distress or impairment."
        ),
    },
    "PTSD": {
        "code": "6B40",
        "title": "Post-traumatic stress disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Post-traumatic stress disorder is characterized by symptoms following exposure to an "
            "extreme threatening event, including re-experiencing, avoidance, negative alterations "
            "in cognition and mood, and hyperarousal."
        ),
        "diagnostic_requirements": (
            "Exposure to traumatic event plus symptoms from each of 4 clusters: intrusion, avoidance, "
            "negative alterations in cognition/mood, and hyperarousal. Duration 1+ month."
        ),
    },
    "SUD": {
        "code": "6C40",
        "title": "Substance use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Substance use disorder is characterized by a pattern of use of a psychoactive substance "
            "that causes significant impairment or distress."
        ),
        "diagnostic_requirements": (
            "2+ of 11 criteria within 12 months, including impaired control, social impairment, "
            "risky use, and pharmacological criteria (tolerance, withdrawal)."
        ),
    },
    "ANOREXIA": {
        "code": "6B80",
        "title": "Anorexia nervosa",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Anorexia nervosa is characterized by significantly low body weight, intense fear of "
            "weight gain, and disturbance in body weight or shape perception."
        ),
        "diagnostic_requirements": (
            "Restriction of energy intake leading to significantly low body weight, intense fear "
            "of gaining weight, and disturbance in self-perceived weight or shape."
        ),
    },
    "BULIMIA": {
        "code": "6B81",
        "title": "Bulimia nervosa",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Bulimia nervosa is characterized by recurrent binge eating followed by compensatory "
            "behaviors such as vomiting or laxative misuse."
        ),
        "diagnostic_requirements": (
            "Recurrent episodes of binge eating with compensatory behaviors at least once weekly "
            "for 3 months. Self-evaluation unduly influenced by weight and shape."
        ),
    },
    "BED": {
        "code": "6B82",
        "title": "Binge-eating disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Binge-eating disorder is characterized by recurrent binge eating without the regular "
            "compensatory behaviors of bulimia nervosa."
        ),
        "diagnostic_requirements": (
            "Recurrent episodes of binge eating at least once weekly for 3 months, associated with "
            "marked distress and characterized by rapid eating, eating until uncomfortably full."
        ),
    },
    "INSOMNIA": {
        "code": "7A00",
        "title": "Insomnia disorders",
        "chapter": "Sleep-wake disorders",
        "chapter_code": "07",
        "clinical_description": (
            "Insomnia disorder is characterized by persistent difficulty with sleep initiation, "
            "duration, or quality, despite adequate opportunity for sleep."
        ),
        "diagnostic_requirements": (
            "Difficulty initiating or maintaining sleep, or early morning awakening, present at "
            "least 3 nights per week for at least 3 months, despite adequate sleep opportunity."
        ),
    },
    "PSYCHOTIC": {
        "code": "6A20",
        "title": "Schizophrenia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Schizophrenia is characterized by disturbances in multiple mental modalities, including "
            "thought, perception, self-experience, cognition, volition, and affect."
        ),
        "diagnostic_requirements": (
            "At least 2 of the following present for most of 1 month: delusions, hallucinations, "
            "disorganized speech, grossly disorganized behavior, negative symptoms. Continuous signs "
            "persist for 6+ months."
        ),
    },
    "SOMATIC": {
        "code": "6C20",
        "title": "Somatic symptom disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Somatic symptom disorder is characterized by one or more somatic symptoms that are "
            "accompanied by excessive thoughts, feelings, or behaviors related to the symptoms."
        ),
        "diagnostic_requirements": (
            "1+ distressing somatic symptoms with excessive thoughts/feelings/behaviors. Symptoms "
            "persist for 6+ months (specify persistent)."
        ),
    },
    "ASD": {
        "code": "6A02",
        "title": "Autism spectrum disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "Autism spectrum disorder is characterized by persistent deficits in social communication "
            "and social interaction, and restricted, repetitive patterns of behavior and interests."
        ),
        "diagnostic_requirements": (
            "All 3 deficits in social communication and 2+ of 4 restricted/repetitive behavior "
            "patterns. Symptoms present from early developmental period and cause functional impairment."
        ),
    },
    "ADHD": {
        "code": "6A05",
        "title": "Attention deficit hyperactivity disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": (
            "ADHD is characterized by a persistent pattern of inattention and/or hyperactivity-"
            "impulsivity that interferes with functioning or development."
        ),
        "diagnostic_requirements": (
            "6+ symptoms of inattention and/or 6+ symptoms of hyperactivity-impulsivity (5+ if age 17+) "
            "persisting for 6+ months, present before age 12, in 2+ settings."
        ),
    },
}


def seed():
    db = SessionLocal()
    try:
        disorders = {d.disorder_name: d for d in db.query(Disorder).all()}
        count = 0
        for short_name, data in ICD11_DATA.items():
            pt_name = SHORT_TO_PT.get(short_name, short_name)
            disorder = disorders.get(pt_name)
            if not disorder:
                print(f"  WARNING: Disorder '{short_name}' not found")
                continue
            existing = db.query(ICD11Code).filter_by(
                disorder_id=disorder.disorder_id, icd11_code=data["code"]
            ).first()
            if existing:
                continue
            db.add(ICD11Code(
                disorder_id=disorder.disorder_id,
                icd11_code=data["code"],
                icd11_title=data["title"],
                chapter=data["chapter"],
                chapter_code=data["chapter_code"],
                who_url=f"https://icd.who.int/browse11/l-m/en#/http://id.who.int/icd/entity/{data['code']}",
                clinical_description=data["clinical_description"],
                diagnostic_requirements=data["diagnostic_requirements"],
            ))
            count += 1
        db.commit()
        print(f"OK - {count} CID-11 codes seeded")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
