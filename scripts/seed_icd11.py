"""Seed CID-11 (ICD-11) codes for all DSM-5-TR disorders."""
from app.core.database import SessionLocal
from app.models.base import Disorder, ICD11Code


SHORT_TO_PT = {
    "MDD": "Transtorno Depressivo Maior",
    "GAD": "Transtorno de Ansiedade Generalizada",
    "PANIC": "Transtorno do Pânico",
    "AGORAPHOBIA": "Agorafobia",
    "BIPOLAR": "Transtorno Bipolar Tipo I",
    "BIPOLAR_II": "Transtorno Bipolar Tipo II",
    "OCD": "Transtorno Obsessivo-Compulsivo",
    "PTSD": "Transtorno de Estresse Pós-Traumático",
    "SUD": "Transtorno por Uso de Substâncias",
    "ANOREXIA": "Anorexia Nervosa",
    "BULIMIA": "Bulimia Nervosa",
    "BED": "Transtorno de Compulsão Alimentar",
    "INSOMNIA": "Transtorno de Insônia",
    "PSYCHOTIC": "Esquizofrenia / Transtorno Psicótico",
    "SOMATIC": "Transtorno de Sintomas Somáticos",
    "DYSTHYMIA": "Transtorno Depressivo Persistente (Distimia)",
    "SOCIAL_ANXIETY": "Transtorno de Ansiedade Social",
    "ASD": "Transtorno do Espectro Autista",
    "ADHD": "Transtorno de Déficit de Atenção/Hiperatividade",
}

ICD11_DATA = {
    "MDD": {
        "code": "6A70.2",
        "title": "Major depressive disorder, single episode, moderate",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Major depressive disorder is characterized by at least two weeks of depressed mood or loss of interest or pleasure, accompanied by other symptoms such as changes in appetite or sleep, psychomotor changes, fatigue, feelings of worthlessness, and difficulty concentrating.",
        "diagnostic_requirements": "At least 5 of 9 symptoms including depressed mood or loss of interest. Symptoms present most of the day, nearly every day for at least 2 weeks. Symptoms cause clinically significant distress or impairment.",
    },
    "GAD": {
        "code": "6B00",
        "title": "Generalized anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Generalized anxiety disorder is characterized by marked symptoms of anxiety that persist for at least several months, manifested by general apprehension or excessive worry about multiple everyday events or problems.",
        "diagnostic_requirements": "Symptoms of anxiety and worry occurring more days than not for at least several months. Associated symptoms include restlessness, fatigue, difficulty concentrating, irritability, muscle tension, or sleep disturbance.",
    },
    "PANIC": {
        "code": "6B01",
        "title": "Panic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Panic disorder is characterized by recurrent unexpected panic attacks that are not restricted to particular stimuli or situations.",
        "diagnostic_requirements": "Recurrent unexpected panic attacks with persistent concern about additional attacks. Not better explained by another mental disorder.",
    },
    "AGORAPHOBIA": {
        "code": "6B02",
        "title": "Agoraphobia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Agoraphobia is characterized by marked and excessive fear or anxiety about being in multiple situations where escape or help might not be available.",
        "diagnostic_requirements": "Fear or avoidance of 2+ situations (public transport, open spaces, enclosed spaces, crowds, being outside home alone). Symptoms persist for at least several months.",
    },
    "BIPOLAR": {
        "code": "6A60",
        "title": "Bipolar type I disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Bipolar type I disorder is characterized by at least one manic episode, an extreme mood state lasting at least 1 week with elevated mood and increased activity or energy.",
        "diagnostic_requirements": "At least one manic episode lasting 1 week (or requiring hospitalization). Manic episode defined by elevated/expansive/irritable mood plus 3+ associated symptoms.",
    },
    "OCD": {
        "code": "6B20",
        "title": "Obsessive-compulsive disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Obsessive-compulsive disorder is characterized by persistent obsessions or compulsions that are time-consuming or cause marked distress or functional impairment.",
        "diagnostic_requirements": "Presence of obsessions and/or compulsions that are time-consuming (1+ hour/day) or cause clinically significant distress or impairment.",
    },
    "PTSD": {
        "code": "6B40",
        "title": "Post-traumatic stress disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Post-traumatic stress disorder is characterized by symptoms following exposure to an extreme threatening event, including re-experiencing, avoidance, negative alterations in cognition and mood, and hyperarousal.",
        "diagnostic_requirements": "Exposure to traumatic event plus symptoms from each of 4 clusters: intrusion, avoidance, negative alterations in cognition/mood, and hyperarousal. Duration 1+ month.",
    },
    "SUD": {
        "code": "6C40",
        "title": "Substance use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Substance use disorder is characterized by a pattern of use of a psychoactive substance that causes significant impairment or distress.",
        "diagnostic_requirements": "2+ of 11 criteria within 12 months, including impaired control, social impairment, risky use, and pharmacological criteria (tolerance, withdrawal).",
    },
    "ANOREXIA": {
        "code": "6B80",
        "title": "Anorexia nervosa",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Anorexia nervosa is characterized by significantly low body weight, intense fear of weight gain, and disturbance in body weight or shape perception.",
        "diagnostic_requirements": "Restriction of energy intake leading to significantly low body weight, intense fear of gaining weight, and disturbance in self-perceived weight or shape.",
    },
    "BULIMIA": {
        "code": "6B81",
        "title": "Bulimia nervosa",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Bulimia nervosa is characterized by recurrent binge eating followed by compensatory behaviors such as vomiting or laxative misuse.",
        "diagnostic_requirements": "Recurrent episodes of binge eating with compensatory behaviors at least once weekly for 3 months. Self-evaluation unduly influenced by weight and shape.",
    },
    "BED": {
        "code": "6B82",
        "title": "Binge-eating disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Binge-eating disorder is characterized by recurrent binge eating without the regular compensatory behaviors of bulimia nervosa.",
        "diagnostic_requirements": "Recurrent episodes of binge eating at least once weekly for 3 months, associated with marked distress and characterized by rapid eating, eating until uncomfortably full.",
    },
    "INSOMNIA": {
        "code": "7A00",
        "title": "Insomnia disorders",
        "chapter": "Sleep-wake disorders",
        "chapter_code": "07",
        "clinical_description": "Insomnia disorder is characterized by persistent difficulty with sleep initiation, duration, or quality, despite adequate opportunity for sleep.",
        "diagnostic_requirements": "Difficulty initiating or maintaining sleep, or early morning awakening, present at least 3 nights per week for at least 3 months, despite adequate sleep opportunity.",
    },
    "PSYCHOTIC": {
        "code": "6A20",
        "title": "Schizophrenia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Schizophrenia is characterized by disturbances in multiple mental modalities, including thought, perception, self-experience, cognition, volition, and affect.",
        "diagnostic_requirements": "At least 2 of the following present for most of 1 month: delusions, hallucinations, disorganized speech, grossly disorganized behavior, negative symptoms. Continuous signs persist for 6+ months.",
    },
    "SOMATIC": {
        "code": "6C20",
        "title": "Somatic symptom disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Somatic symptom disorder is characterized by one or more somatic symptoms that are accompanied by excessive thoughts, feelings, or behaviors related to the symptoms.",
        "diagnostic_requirements": "1+ distressing somatic symptoms with excessive thoughts/feelings/behaviors. Symptoms persist for 6+ months (specify persistent).",
    },
    "ASD": {
        "code": "6A02",
        "title": "Autism spectrum disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Autism spectrum disorder is characterized by persistent deficits in social communication and social interaction, and restricted, repetitive patterns of behavior and interests.",
        "diagnostic_requirements": "All 3 deficits in social communication and 2+ of 4 restricted/repetitive behavior patterns. Symptoms present from early developmental period and cause functional impairment.",
    },
    "ADHD": {
        "code": "6A05",
        "title": "Attention deficit hyperactivity disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "ADHD is characterized by a persistent pattern of inattention and/or hyperactivity-impulsivity that interferes with functioning or development.",
        "diagnostic_requirements": "6+ symptoms of inattention and/or 6+ symptoms of hyperactivity-impulsivity (5+ if age 17+) persisting for 6+ months, present before age 12, in 2+ settings.",
    },
    "BIPOLAR_II": {
        "code": "6A61",
        "title": "Bipolar type II disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Bipolar type II disorder is characterized by a pattern of hypomanic episodes and depressive episodes, without full manic episodes that meet the criteria for bipolar type I.",
        "diagnostic_requirements": "At least one hypomanic episode (4+ days, elevated mood plus 3+ symptoms) and at least one major depressive episode. No history of manic episodes. Symptoms cause clinically significant distress or impairment.",
    },
    "DYSTHYMIA": {
        "code": "6A72",
        "title": "Dysthymic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Dysthymic disorder (persistent depressive disorder) is characterized by a chronically depressed mood that persists for at least 2 years, accompanied by additional depressive symptoms that do not meet the severity or duration of a major depressive episode.",
        "diagnostic_requirements": "Depressed mood for most of the day, more days than not, for at least 2 years (1 year for children/adolescents). Presence of 2+ associated symptoms (poor appetite, insomnia, low energy, low self-esteem, poor concentration, hopelessness).",
    },
    "SOCIAL_ANXIETY": {
        "code": "6B04",
        "title": "Social anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders",
        "chapter_code": "06",
        "clinical_description": "Social anxiety disorder is characterized by marked and persistent fear or anxiety about one or more social situations where the individual may be scrutinized by others, such as social interactions, being observed, or performing in front of others.",
        "diagnostic_requirements": "Marked fear or anxiety about 1+ social situations, fear of negative evaluation, social situations consistently provoke fear or anxiety, avoided or endured with intense fear, symptoms persist for 6+ months, cause clinically significant distress or impairment.",
    },
}

# ============================================================================
# REFERENCE DISORDER ICD-11 CODES — all ~122 non-core disorders
# Mapped per ICD-11 linearization (WHO, 2024) by DSM-5 chapter
# ============================================================================
ICD11_REFERENCE_MAP = {
    # ── Chapter 1: Transtornos do Neurodesenvolvimento ──
    "Deficiência Intelectual": {
        "code": "6A00", "title": "Intellectual developmental disorders",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Deficiência Intelectual Leve": {
        "code": "6A00.0", "title": "Mild intellectual developmental disorders",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Deficiência Intelectual Moderada": {
        "code": "6A00.1", "title": "Moderate intellectual developmental disorders",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Deficiência Intelectual Grave": {
        "code": "6A00.2", "title": "Severe intellectual developmental disorders",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Deficiência Intelectual Profunda": {
        "code": "6A00.3", "title": "Profound intellectual developmental disorders",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Atraso Global do Desenvolvimento": {
        "code": "6A00.Z", "title": "Intellectual developmental disorders, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Deficiência Intelectual Não Especificada": {
        "code": "6A00.Z", "title": "Intellectual developmental disorders, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Linguagem": {
        "code": "6A01.2", "title": "Developmental language disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Fonológico": {
        "code": "6A01.1", "title": "Developmental speech sound disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Fluência com Início na Infância (Gagueira)": {
        "code": "6A01.3", "title": "Developmental fluency disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Comunicação Social (Pragmática)": {
        "code": "6A01.0", "title": "Developmental speech or language disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Comunicação Não Especificado": {
        "code": "6A01.Z", "title": "Developmental speech or language disorders, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Déficit de Atenção/Hiperatividade — Apresentação Combinada": {
        "code": "6A05.0", "title": "ADHD, combined presentation",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Déficit de Atenção/Hiperatividade — Apresentação Predominante com Desatenção": {
        "code": "6A05.1", "title": "ADHD, predominantly inattentive presentation",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Déficit de Atenção/Hiperatividade — Apresentação Predominante com Hiperatividade": {
        "code": "6A05.2", "title": "ADHD, predominantly hyperactive-impulsive presentation",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Déficit de Atenção/Hiperatividade — Outra Apresentação Especificada": {
        "code": "6A05.Y", "title": "ADHD, other specified presentation",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Déficit de Atenção/Hiperatividade Não Especificado": {
        "code": "6A05.Z", "title": "ADHD, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Específico da Aprendizagem — com Prejuízo na Leitura": {
        "code": "6A03.0", "title": "Developmental learning disorder with impairment in reading",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Específico da Aprendizagem — com Prejuízo na Expressão Escrita": {
        "code": "6A03.1", "title": "Developmental learning disorder with impairment in written expression",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Específico da Aprendizagem — com Prejuízo na Matemática": {
        "code": "6A03.2", "title": "Developmental learning disorder with impairment in mathematics",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Específico da Aprendizagem Não Especificado": {
        "code": "6A03.Z", "title": "Developmental learning disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Desenvolvimento da Coordenação": {
        "code": "6A04", "title": "Developmental motor coordination disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Movimento Estereotipado": {
        "code": "6A06", "title": "Stereotyped movement disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Tourette": {
        "code": "8A05.00", "title": "Tourette disorder",
        "chapter": "Diseases of the nervous system", "chapter_code": "08",
    },
    "Transtorno de Tique Motor ou Vocal Crônico": {
        "code": "8A05.0", "title": "Chronic motor or vocal tic disorder",
        "chapter": "Diseases of the nervous system", "chapter_code": "08",
    },
    "Transtorno de Tique Transitório": {
        "code": "8A05.1", "title": "Transient tic disorder",
        "chapter": "Diseases of the nervous system", "chapter_code": "08",
    },
    "Transtorno de Tique Especificado": {
        "code": "8A05.Y", "title": "Other specified tic disorder",
        "chapter": "Diseases of the nervous system", "chapter_code": "08",
    },
    "Transtorno de Tique Não Especificado": {
        "code": "8A05.Z", "title": "Tic disorder, unspecified",
        "chapter": "Diseases of the nervous system", "chapter_code": "08",
    },
    "Outro Transtorno do Neurodesenvolvimento Especificado": {
        "code": "6A0Y", "title": "Other specified neurodevelopmental disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Neurodesenvolvimento Não Especificado": {
        "code": "6A0Z", "title": "Neurodevelopmental disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 2: Espectro da Esquizofrenia e Outros Transtornos Psicóticos ──
    "Transtorno Delirante": {
        "code": "6A24", "title": "Delusional disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Psicótico Breve": {
        "code": "6A23", "title": "Acute and transient psychotic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Esquizofreniforme": {
        "code": "6A22", "title": "Schizophreniform disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Esquizoafetivo": {
        "code": "6A21", "title": "Schizoaffective disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Psicótico Induzido por Substância": {
        "code": "6C4Y.6", "title": "Substance-induced psychotic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Psicótico Devido a Outra Condição Médica": {
        "code": "6E61", "title": "Secondary psychotic syndrome",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Catatonia Associada a Transtorno Mental": {
        "code": "6A40", "title": "Catatonia associated with another mental disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Catatonia Devido a Outra Condição Médica": {
        "code": "6E62", "title": "Secondary catatonia syndrome",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Catatonia Não Especificada": {
        "code": "6A4Z", "title": "Catatonia, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno do Espectro da Esquizofrenia Especificado": {
        "code": "6A2Y", "title": "Other specified schizophrenia or other primary psychotic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Espectro da Esquizofrenia Não Especificado": {
        "code": "6A2Z", "title": "Schizophrenia or other primary psychotic disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 3: Transtornos Bipolares e Relacionados ──
    "Transtorno Bipolar Tipo II": {
        "code": "6A61", "title": "Bipolar type II disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Ciclotímico": {
        "code": "6A62", "title": "Cyclothymic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Bipolar Induzido por Substância": {
        "code": "6C4Y.5", "title": "Substance-induced bipolar disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Bipolar Devido a Outra Condição Médica": {
        "code": "6E63", "title": "Secondary bipolar or related syndrome",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Bipolar Especificado": {
        "code": "6A6Y", "title": "Other specified bipolar or related disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Bipolar Não Especificado": {
        "code": "6A6Z", "title": "Bipolar or related disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 4: Transtornos Depressivos ──
    "Transtorno Disruptivo da Desregulação do Humor": {
        "code": "6A73", "title": "Disruptive mood dysregulation disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Depressivo Persistente (Distimia)": {
        "code": "6A72", "title": "Dysthymic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Disfórico Pré-Menstrual": {
        "code": "GA34.41", "title": "Premenstrual dysphoric disorder",
        "chapter": "Diseases of the genitourinary system", "chapter_code": "GA",
    },
    "Transtorno Depressivo Induzido por Substância": {
        "code": "6C4Y.4", "title": "Substance-induced depressive disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Depressivo Devido a Outra Condição Médica": {
        "code": "6E64", "title": "Secondary depressive syndrome",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Depressivo Especificado": {
        "code": "6A7Y", "title": "Other specified depressive disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Depressivo Não Especificado": {
        "code": "6A7Z", "title": "Depressive disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 5: Transtornos de Ansiedade ──
    "Transtorno de Ansiedade de Separação": {
        "code": "6B05", "title": "Separation anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Mutismo Seletivo": {
        "code": "6B06", "title": "Selective mutism",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Fobia Específica": {
        "code": "6B03", "title": "Specific phobia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Ansiedade Social": {
        "code": "6B04", "title": "Social anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Ansiedade Induzido por Substância": {
        "code": "6C4Y.1", "title": "Substance-induced anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Ansiedade Devido a Outra Condição Médica": {
        "code": "6E65", "title": "Secondary anxiety syndrome",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno de Ansiedade Especificado": {
        "code": "6B0Y", "title": "Other specified anxiety or fear-related disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Ansiedade Não Especificado": {
        "code": "6B0Z", "title": "Anxiety or fear-related disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 6: Transtornos Obsessivo-Compulsivos e Relacionados ──
    "Transtorno Dismórfico Corporal": {
        "code": "6B21", "title": "Body dysmorphic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Acumulação": {
        "code": "6B23", "title": "Hoarding disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Tricotilomania (Transtorno de Arrancar Cabelo)": {
        "code": "6B24.0", "title": "Trichotillomania",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Escoriação (Skin Picking)": {
        "code": "6B24.1", "title": "Excoriation disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "TOC Induzido por Substância": {
        "code": "6C4Y.2", "title": "Substance-induced obsessive-compulsive or related disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "TOC Devido a Outra Condição Médica": {
        "code": "6E66", "title": "Secondary obsessive-compulsive or related syndrome",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Obsessivo-Compulsivo Especificado": {
        "code": "6B2Y", "title": "Other specified obsessive-compulsive or related disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Obsessivo-Compulsivo Não Especificado": {
        "code": "6B2Z", "title": "Obsessive-compulsive or related disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 7: Transtornos Relacionados a Trauma e Estressores ──
    "Transtorno de Apego Reativo": {
        "code": "6B44", "title": "Reactive attachment disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Engajamento Social Desinibido": {
        "code": "6B45", "title": "Disinhibited social engagement disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Estresse Agudo": {
        "code": "6B43", "title": "Acute stress disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtornos de Adaptação": {
        "code": "6B43", "title": "Adjustment disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Luto Prolongado": {
        "code": "6B42", "title": "Prolonged grief disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Relacionado a Trauma Especificado": {
        "code": "6B4Y", "title": "Other specified disorder specifically associated with stress",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Relacionado a Trauma Não Especificado": {
        "code": "6B4Z", "title": "Disorder specifically associated with stress, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 8: Transtornos Dissociativos ──
    "Transtorno Dissociativo de Identidade": {
        "code": "6B60", "title": "Dissociative identity disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Amnésia Dissociativa": {
        "code": "6B63", "title": "Dissociative amnesia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Despersonalização/Desrealização": {
        "code": "6B62", "title": "Depersonalization-derealization disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Dissociativo Especificado": {
        "code": "6B6Y", "title": "Other specified dissociative disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Dissociativo Não Especificado": {
        "code": "6B6Z", "title": "Dissociative disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 9: Transtornos de Sintomas Somáticos e Relacionados ──
    "Transtorno de Ansiedade de Doença": {
        "code": "6C21", "title": "Illness anxiety disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Conversivo (Transtorno de Sintomas Neurológicos Funcionais)": {
        "code": "6C22", "title": "Functional neurological symptom disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Factício": {
        "code": "6C23", "title": "Factitious disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Fatores Psicológicos que Afetam Outras Condições Médicas": {
        "code": "6C2Y", "title": "Other specified bodily distress disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno de Sintomas Somáticos Especificado": {
        "code": "6C2Y", "title": "Other specified bodily distress disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Sintomas Somáticos Não Especificado": {
        "code": "6C2Z", "title": "Bodily distress disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 10: Transtornos Alimentares e da Alimentação ──
    "Pica": {
        "code": "6B84", "title": "Pica",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Ruminação": {
        "code": "6B85", "title": "Rumination disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Alimentar Restritivo-Evitante": {
        "code": "6B83", "title": "Avoidant-restrictive food intake disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Alimentar Especificado": {
        "code": "6B8Y", "title": "Other specified feeding or eating disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Alimentar Não Especificado": {
        "code": "6B8Z", "title": "Feeding or eating disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 11: Transtornos da Eliminação ──
    "Enurese": {
        "code": "6C00", "title": "Enuresis",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Encoprese": {
        "code": "6C01", "title": "Encopresis",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno da Eliminação Especificado": {
        "code": "6C0Y", "title": "Other specified elimination disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Eliminação Não Especificado": {
        "code": "6C0Z", "title": "Elimination disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 12: Transtornos do Sono-Vigília ──
    "Transtorno de Hipersonolência": {
        "code": "7A01", "title": "Hypersomnolence disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Narcolepsia": {
        "code": "7A02", "title": "Narcolepsy",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Apneia Obstrutiva do Sono": {
        "code": "7A11", "title": "Obstructive sleep apnoea",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Apneia Central do Sono": {
        "code": "7A12", "title": "Central sleep apnoea",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Transtorno do Ritmo Circadiano do Sono-Vigília": {
        "code": "7A60", "title": "Circadian rhythm sleep-wake disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Transtorno do Despertar do Sono Não REM (Sonambulismo)": {
        "code": "7B00.0", "title": "Sleepwalking disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Terror Noturno": {
        "code": "7B00.1", "title": "Sleep terrors",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Transtorno do Pesadelo": {
        "code": "7B00.2", "title": "Nightmare disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Transtorno Comportamental do Sono REM": {
        "code": "7B01", "title": "REM sleep behaviour disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Síndrome das Pernas Inquietas": {
        "code": "7A80", "title": "Restless legs syndrome",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Transtorno do Sono Induzido por Substância": {
        "code": "7A0Y", "title": "Other specified insomnia disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Outro Transtorno do Sono-Vigília Especificado": {
        "code": "7Z0Y", "title": "Other specified sleep-wake disorder",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },
    "Transtorno do Sono-Vigília Não Especificado": {
        "code": "7Z0Z", "title": "Sleep-wake disorder, unspecified",
        "chapter": "Sleep-wake disorders", "chapter_code": "07",
    },

    # ── Chapter 13: Disfunções Sexuais ──
    "Ejaculação Retardada": {
        "code": "6C91", "title": "Delayed ejaculation",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Erétil": {
        "code": "6C92", "title": "Erectile dysfunction",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Orgasmo Feminino": {
        "code": "6C93", "title": "Female orgasmic dysfunction",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Interesse/Excitação Sexual Feminino": {
        "code": "6C95", "title": "Female sexual interest/arousal dysfunction",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Dor Gênito-Pélvica/Penetração": {
        "code": "6C97", "title": "Genito-pelvic pain/penetration disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Desejo Sexual Hipoativo Masculino": {
        "code": "6C94", "title": "Male hypoactive sexual desire dysfunction",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Ejaculação Prematura": {
        "code": "6C90", "title": "Premature ejaculation",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Disfunção Sexual Induzida por Substância": {
        "code": "6C4Y.7", "title": "Substance-induced sexual dysfunction",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outra Disfunção Sexual Especificada": {
        "code": "6C9Y", "title": "Other specified sexual dysfunction",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Disfunção Sexual Não Especificada": {
        "code": "6C9Z", "title": "Sexual dysfunction, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 14: Disforia de Gênero ──
    "Disforia de Gênero em Crianças": {
        "code": "HA60", "title": "Gender incongruence of childhood",
        "chapter": "Conditions related to sexual health", "chapter_code": "HA",
    },
    "Disforia de Gênero em Adolescentes e Adultos": {
        "code": "HA61", "title": "Gender incongruence of adolescence or adulthood",
        "chapter": "Conditions related to sexual health", "chapter_code": "HA",
    },
    "Outra Disforia de Gênero Especificada": {
        "code": "HA6Y", "title": "Other specified gender incongruence",
        "chapter": "Conditions related to sexual health", "chapter_code": "HA",
    },
    "Disforia de Gênero Não Especificada": {
        "code": "HA6Z", "title": "Gender incongruence, unspecified",
        "chapter": "Conditions related to sexual health", "chapter_code": "HA",
    },

    # ── Chapter 15: Transtornos Disruptivos, do Controle de Impulsos e da Conduta ──
    "Transtorno Opositivo-Desafiador": {
        "code": "6C70", "title": "Oppositional defiant disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Explosivo Intermitente": {
        "code": "6C72", "title": "Intermittent explosive disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Conduta": {
        "code": "6C71", "title": "Conduct disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Antissocial": {
        "code": "6D11", "title": "Antisocial personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Piromania": {
        "code": "6C50", "title": "Pyromania",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Cleptomania": {
        "code": "6C51", "title": "Kleptomania",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Disruptivo Especificado": {
        "code": "6C7Y", "title": "Other specified disruptive behaviour or dissocial disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Disruptivo Não Especificado": {
        "code": "6C7Z", "title": "Disruptive behaviour or dissocial disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 16: Transtornos Relacionados a Substâncias e Aditivos ──
    "Transtorno por Uso de Álcool": {
        "code": "6C41", "title": "Alcohol use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Intoxicação Alcoólica": {
        "code": "6C41.3", "title": "Alcohol intoxication",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Abstinência Alcoólica": {
        "code": "6C41.4", "title": "Alcohol withdrawal",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Cannabis": {
        "code": "6C42", "title": "Cannabis use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Alucinógenos": {
        "code": "6C49", "title": "Hallucinogen use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Inalantes": {
        "code": "6C4B", "title": "Volatile inhalant use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Opioides": {
        "code": "6C44", "title": "Opioid use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Sedativos/Hipnóticos/Ansiolíticos": {
        "code": "6C44", "title": "Sedative use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Estimulantes": {
        "code": "6C46", "title": "Stimulant use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno por Uso de Tabaco": {
        "code": "6C4A", "title": "Nicotine use disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno do Jogo (Jogo Patológico)": {
        "code": "6C50", "title": "Gambling disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 17: Transtornos Neurocognitivos ──
    "Delirium": {
        "code": "6D70", "title": "Delirium",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Maior — Doença de Alzheimer": {
        "code": "6D80", "title": "Dementia due to Alzheimer disease",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Maior — Degeneração Lobar Frontotemporal": {
        "code": "6D81", "title": "Dementia due to frontotemporal lobar degeneration",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Maior — Corpos de Lewy": {
        "code": "6D82", "title": "Dementia with Lewy bodies",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Maior — Vascular": {
        "code": "6D83", "title": "Vascular dementia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Maior — Traumatismo Cranioencefálico": {
        "code": "6D84", "title": "Dementia due to traumatic brain injury",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Leve": {
        "code": "6D71", "title": "Mild neurocognitive disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Neurocognitivo Especificado": {
        "code": "6D8Y", "title": "Other specified dementia",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Neurocognitivo Não Especificado": {
        "code": "6D8Z", "title": "Dementia, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 18: Transtornos da Personalidade ──
    "Transtorno da Personalidade Paranoide": {
        "code": "6D10", "title": "Paranoid personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Esquizoide": {
        "code": "6D10", "title": "Schizoid personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Esquizotípica": {
        "code": "6A25.0", "title": "Schizotypal disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Borderline": {
        "code": "6D11", "title": "Borderline personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Histriônica": {
        "code": "6D11", "title": "Histrionic personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Narcisista": {
        "code": "6D11", "title": "Narcissistic personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Esquiva": {
        "code": "6D12", "title": "Avoidant personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Dependente": {
        "code": "6D12", "title": "Dependent personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Obsessivo-Compulsiva": {
        "code": "6D12", "title": "Obsessive-compulsive personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno da Personalidade Especificado": {
        "code": "6D1Y", "title": "Other specified personality disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno da Personalidade Não Especificado": {
        "code": "6D1Z", "title": "Personality disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 19: Transtornos Parafílicos ──
    "Transtorno Voyeurista": {
        "code": "6D30", "title": "Voyeuristic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Exhibitionista": {
        "code": "6D31", "title": "Exhibitionistic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Frotteurista": {
        "code": "6D32", "title": "Frotteuristic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Masoquismo Sexual": {
        "code": "6D33", "title": "Sexual masochism disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno de Sadismo Sexual": {
        "code": "6D34", "title": "Sexual sadism disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Pedofílico": {
        "code": "6D35", "title": "Paedophilic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Fetichista": {
        "code": "6D36", "title": "Fetishistic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Transvéstico": {
        "code": "6D37", "title": "Transvestic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Outro Transtorno Parafílico Especificado": {
        "code": "6D3Y", "title": "Other specified paraphilic disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Parafílico Não Especificado": {
        "code": "6D3Z", "title": "Paraphilic disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

    # ── Chapter 20: Outros Transtornos Mentais ──
    "Outro Transtorno Mental Especificado": {
        "code": "6E6Y", "title": "Other specified mental disorder",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },
    "Transtorno Mental Não Especificado": {
        "code": "6E6Z", "title": "Mental disorder, unspecified",
        "chapter": "Mental, behavioural or neurodevelopmental disorders", "chapter_code": "06",
    },

}


def seed():
    db = SessionLocal()
    try:
        disorders = {d.disorder_name: d for d in db.query(Disorder).all()}
        count_new = 0
        count_upd = 0

        # Build core set for update detection
        core_pt_names = set()
        for short_name in ICD11_DATA:
            core_pt_names.add(SHORT_TO_PT[short_name])

        # Merge core + reference data
        all_data = {}
        for short_name, data in ICD11_DATA.items():
            pt_name = SHORT_TO_PT[short_name]
            all_data[pt_name] = data
        for pt_name, data in ICD11_REFERENCE_MAP.items():
            if pt_name not in all_data:
                all_data[pt_name] = data

        for pt_name, data in all_data.items():
            disorder = disorders.get(pt_name)
            if not disorder:
                print(f"  WARNING: '{pt_name}' not found in DB")
                continue
            existing = db.query(ICD11Code).filter_by(
                disorder_id=disorder.disorder_id, icd11_code=data["code"]
            ).first()
            if existing:
                # Update existing core records with rich data
                if pt_name in core_pt_names:
                    needs_update = False
                    if data.get("clinical_description") and (
                        not existing.clinical_description or existing.clinical_description != data["clinical_description"]
                    ):
                        existing.clinical_description = data["clinical_description"]
                        needs_update = True
                    if data.get("diagnostic_requirements") and (
                        not existing.diagnostic_requirements or existing.diagnostic_requirements != data["diagnostic_requirements"]
                    ):
                        existing.diagnostic_requirements = data["diagnostic_requirements"]
                        needs_update = True
                    if needs_update:
                        count_upd += 1
                continue
            db.add(ICD11Code(
                disorder_id=disorder.disorder_id,
                icd11_code=data["code"],
                icd11_title=data.get("title", ""),
                chapter=data.get("chapter", "Mental, behavioural or neurodevelopmental disorders"),
                chapter_code=data.get("chapter_code", "06"),
                who_url=f"https://icd.who.int/browse11/l-m/en#/http://id.who.int/icd/entity/{data['code']}",
                clinical_description=data.get("clinical_description", ""),
                diagnostic_requirements=data.get("diagnostic_requirements", ""),
            ))
            count_new += 1
        db.commit()
        print(f"OK - {count_new} new, {count_upd} updated ({len(all_data)} total disorders mapped)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
