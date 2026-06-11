"""
Seed the clinical database with realistic Brazilian patient data for ML development.
Creates patients, consultations, symptoms, scale responses, and inferences.
"""

import random
import math
from datetime import datetime, timedelta, date
from uuid import uuid4
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.base import Base, SexType, GenderIdentity, EducationLevel, Ethnicity
from app.models.base import (
    Symptom, Disorder, DiagnosticCriteria, AssessmentScale, ScaleQuestion,
    ClinicalConsultation, PatientProfile, PatientIdentity, HealthcareProfessional,
    SymptomObservation, ScaleResponse, DiagnosticInference,
    CriteriaGroup, CriteriaRule, ICD11Code,
)
from app.security.lgpd import encrypt_field

random.seed(42)

# Brazilian names
FIRST_NAMES = [
    "Ana", "Beatriz", "Carlos", "Daniel", "Eduarda", "Felipe", "Gabriela",
    "Henrique", "Isabela", "João", "Kamila", "Lucas", "Mariana", "Nicolas",
    "Olivia", "Pedro", "Rafaela", "Samuel", "Tatiane", "Ubirajara",
    "Valentina", "William", "Ximena", "Yuri", "Amanda", "Bruno", "Camila",
    "Diego", "Elisa", "Fernando", "Giovanna", "Heitor", "Igor", "Julia",
    "Kevin", "Larissa", "Miguel", "Nathalia", "Otávio", "Patrícia",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Pereira",
    "Carvalho", "Almeida", "Rodrigues", "Nascimento", "Araújo", "Barbosa",
    "Ribeiro", "Gomes", "Martins", "Melo", "Teixeira", "Cavalcanti",
    "Dias", "Moreira", "Campos", "Cardoso", "Correia", "Castro",
]

# Disorder definitions with ICD-11 codes
DISORDER_DEFS = [
    {
        "name": "Transtorno Depressivo Maior",
        "english_name": "Major Depressive Disorder",
        "cid": "F32.9", "dsm": "296.2",
        "icd11": "6A70.2", "icd11_title": "Transtorno depressivo maior, episódio único, moderado",
        "category": "Transtornos Depressivos",
        "symptoms": [
            ("depressed_mood", "Humor deprimido na maior parte do dia", 0.90, 0.05, True, 14),
            ("loss_of_interest", "Perda de interesse ou prazer", 0.85, 0.04, True, 14),
            ("sleep_disturbance", "Distúrbio do sono", 0.75, 0.10, False, 14),
            ("fatigue", "Fadiga ou perda de energia", 0.80, 0.08, False, 14),
            ("appetite_changes", "Alterações de apetite ou peso", 0.65, 0.05, False, 14),
            ("guilt_feelings", "Sentimentos de inutilidade ou culpa", 0.70, 0.03, False, 14),
            ("concentration_problems", "Dificuldade de concentração", 0.70, 0.06, False, 14),
            ("psychomotor_changes", "Alterações psicomotoras", 0.50, 0.04, False, 14),
            ("suicidal_ideation", "Ideação suicida", 0.40, 0.01, False, 14),
        ],
        "groups": {"A": {"required": 5, "total": 9, "min_duration": 14}},
        "thresholds": [
            ("leve", 5, 14, 3.0), ("moderado", 6, 14, 5.0), ("grave", 8, 14, 7.0),
        ],
    },
    {
        "name": "Transtorno de Ansiedade Generalizada",
        "english_name": "Generalized Anxiety Disorder",
        "cid": "F41.1", "dsm": "300.02",
        "icd11": "6B00", "icd11_title": "Transtorno de ansiedade generalizada",
        "category": "Transtornos de Ansiedade",
        "symptoms": [
            ("excessive_worry", "Ansiedade e preocupação excessivas", 0.92, 0.08, True, 180),
            ("restlessness", "Inquietação", 0.75, 0.05, False, 180),
            ("fatigue_gad", "Fadiga fácil", 0.65, 0.06, False, 180),
            ("muscle_tension", "Tensão muscular", 0.60, 0.04, False, 180),
            ("sleep_disturbance_gad", "Distúrbio do sono", 0.70, 0.08, False, 180),
            ("irritability", "Irritabilidade", 0.65, 0.05, False, 180),
            ("concentration_difficulty_gad", "Dificuldade de concentração", 0.60, 0.05, False, 180),
        ],
        "groups": {"A": {"required": 3, "total": 7, "min_duration": 180}},
        "thresholds": [
            ("leve", 3, 180, 3.0), ("moderado", 4, 180, 5.0), ("grave", 6, 180, 7.0),
        ],
    },
    {
        "name": "Transtorno do Pânico",
        "english_name": "Panic Disorder",
        "cid": "F41.0", "dsm": "300.01",
        "icd11": "6B01", "icd11_title": "Transtorno do pânico",
        "category": "Transtornos de Ansiedade",
        "symptoms": [
            ("panic_attacks", "Ataques de pânico inesperados e recorrentes", 0.95, 0.03, True, 0),
            ("palpitations", "Palpitações", 0.85, 0.04, False, 0),
            ("chest_pain", "Dor ou desconforto no peito", 0.55, 0.02, False, 0),
            ("shortness_of_breath", "Falta de ar", 0.70, 0.03, False, 0),
            ("fear_of_dying", "Medo de morrer", 0.65, 0.01, False, 0),
            ("derealization", "Desrealização", 0.50, 0.02, False, 0),
            ("avoidance_behavior", "Esquiva de situações", 0.75, 0.04, False, 0),
        ],
        "groups": {"A": {"required": 4, "total": 7, "min_duration": 0}},
        "thresholds": [
            ("leve", 4, 0, 3.0), ("moderado", 5, 0, 5.0), ("grave", 7, 0, 7.0),
        ],
    },
    {
        "name": "Transtorno de Estresse Pós-Traumático",
        "english_name": "Post-Traumatic Stress Disorder",
        "cid": "F43.1", "dsm": "309.81",
        "icd11": "6B40", "icd11_title": "Transtorno de estresse pós-traumático",
        "category": "Transtornos Relacionados a Trauma",
        "symptoms": [
            ("traumatic_exposure", "Exposição a evento traumático", 1.00, 0.30, True, 0),
            ("intrusive_memories", "Memórias intrusivas", 0.85, 0.02, False, 30),
            ("nightmares", "Pesadelos", 0.65, 0.03, False, 30),
            ("hypervigilance", "Hipervigilância", 0.75, 0.04, False, 30),
            ("avoidance_ptsd", "Esquiva de lembranças", 0.80, 0.03, False, 30),
            ("negative_cognitions", "Cognições negativas", 0.65, 0.05, False, 30),
            ("startle_response", "Resposta de sobressalto exagerada", 0.70, 0.04, False, 30),
        ],
        "groups": {"A": {"required": 6, "total": 7, "min_duration": 30}},
        "thresholds": [
            ("leve", 4, 30, 3.0), ("moderado", 5, 30, 5.0), ("grave", 7, 30, 7.0),
        ],
    },
    {
        "name": "Transtorno Depressivo Persistente (Distimia)",
        "english_name": "Persistent Depressive Disorder",
        "cid": "F34.1", "dsm": "300.4",
        "icd11": "6A71", "icd11_title": "Transtorno depressivo persistente (distimia)",
        "category": "Transtornos Depressivos",
        "symptoms": [
            ("chronic_low_mood", "Humor deprimido crônico", 0.90, 0.04, True, 720),
            ("poor_appetite_dysthymia", "Apetite reduzido", 0.55, 0.04, False, 720),
            ("low_self_esteem", "Baixa autoestima", 0.70, 0.05, False, 720),
            ("hopelessness", "Desesperança", 0.75, 0.04, False, 720),
            ("low_energy_dysthymia", "Baixa energia", 0.70, 0.06, False, 720),
        ],
        "groups": {"A": {"required": 3, "total": 5, "min_duration": 720}},
        "thresholds": [
            ("leve", 3, 720, 3.0), ("moderado", 4, 720, 5.0), ("grave", 5, 720, 7.0),
        ],
    },
    {
        "name": "Transtorno de Ansiedade Social",
        "english_name": "Social Anxiety Disorder",
        "cid": "F40.1", "dsm": "300.23",
        "icd11": "6B04", "icd11_title": "Transtorno de ansiedade social",
        "category": "Transtornos de Ansiedade",
        "symptoms": [
            ("social_fear", "Medo de situações sociais", 0.92, 0.06, True, 180),
            ("avoidance_social", "Esquiva de situações sociais", 0.80, 0.04, False, 180),
            ("performance_anxiety", "Ansiedade de desempenho", 0.85, 0.05, False, 180),
            ("blushing", "Rubor facial", 0.60, 0.03, False, 180),
        ],
        "groups": {"A": {"required": 3, "total": 4, "min_duration": 180}},
        "thresholds": [
            ("leve", 3, 180, 3.0), ("moderado", 3, 180, 5.0), ("grave", 4, 180, 7.0),
        ],
    },
    {
        "name": "Transtorno Bipolar Tipo I",
        "english_name": "Bipolar I Disorder",
        "cid": "F31.9", "dsm": "296.7",
        "icd11": "6A60", "icd11_title": "Transtorno bipolar tipo I",
        "category": "Transtornos Bipolares",
        "symptoms": [
            ("euphoric_mood", "Humor eufórico ou elevado", 0.85, 0.02, True, 7),
            ("increased_energy", "Aumento de energia", 0.80, 0.03, False, 7),
            ("grandiosity", "Autoestima inflada", 0.60, 0.01, False, 7),
            ("decreased_sleep", "Necessidade reduzida de sono", 0.75, 0.05, False, 7),
            ("rapid_speech", "Fala rápida ou pressionada", 0.70, 0.02, False, 7),
            ("racing_thoughts", "Pensamentos acelerados", 0.65, 0.03, False, 7),
            ("distractibility", "Distratibilidade", 0.60, 0.04, False, 7),
            ("risk_behavior", "Comportamento de risco", 0.55, 0.02, False, 7),
        ],
        "groups": {"A": {"required": 3, "total": 8, "min_duration": 7}},
        "thresholds": [
            ("leve", 3, 7, 3.0), ("moderado", 5, 7, 5.0), ("grave", 7, 7, 7.0),
        ],
    },
    {
        "name": "Transtorno Bipolar Tipo II",
        "english_name": "Bipolar II Disorder",
        "cid": "F31.8", "dsm": "296.89",
        "icd11": "6A61", "icd11_title": "Transtorno bipolar tipo II",
        "category": "Transtornos Bipolares",
        "symptoms": [
            ("hypomanic_mood", "Humor hipomaníaco", 0.80, 0.04, True, 4),
            ("mildly_increased_energy", "Energia levemente aumentada", 0.75, 0.05, False, 4),
            ("reduced_sleep_hypomania", "Necessidade reduzida de sono", 0.65, 0.06, False, 4),
        ],
        "groups": {"A": {"required": 3, "total": 3, "min_duration": 4}},
        "thresholds": [
            ("leve", 2, 4, 3.0), ("moderado", 3, 4, 5.0), ("grave", 3, 4, 7.0),
        ],
    },
    {
        "name": "Transtorno Obsessivo-Compulsivo",
        "english_name": "Obsessive-Compulsive Disorder",
        "cid": "F42.9", "dsm": "300.3",
        "icd11": "6B20", "icd11_title": "Transtorno obsessivo-compulsivo",
        "category": "Transtornos Relacionados a TOC",
        "symptoms": [
            ("obsessions", "Obsessões recorrentes", 0.90, 0.02, True, 0),
            ("compulsions", "Compulsões repetitivas", 0.85, 0.02, False, 0),
            ("repetitive_behavior", "Comportamentos repetitivos", 0.80, 0.03, False, 0),
            ("intrusive_thoughts", "Pensamentos intrusivos", 0.75, 0.04, False, 0),
        ],
        "groups": {"A": {"required": 2, "total": 4, "min_duration": 0}},
        "thresholds": [
            ("leve", 2, 0, 3.0), ("moderado", 3, 0, 5.0), ("grave", 4, 0, 7.0),
        ],
    },
    {
        "name": "Agorafobia",
        "english_name": "Agoraphobia",
        "cid": "F40.0", "dsm": "300.22",
        "icd11": "6B02", "icd11_title": "Agorafobia",
        "category": "Transtornos de Ansiedade",
        "symptoms": [
            ("fear_open_spaces", "Medo de espaços abertos ou multidões", 0.90, 0.05, True, 180),
            ("avoidance_public", "Esquiva de locais públicos", 0.85, 0.04, False, 180),
            ("need_escort", "Necessidade de acompanhante", 0.70, 0.03, False, 180),
            ("panic_agora", "Ataques de pânico em situações temidas", 0.75, 0.04, False, 0),
        ],
        "groups": {"A": {"required": 2, "total": 4, "min_duration": 180}},
        "thresholds": [
            ("leve", 2, 180, 3.0), ("moderado", 3, 180, 5.0), ("grave", 4, 180, 7.0),
        ],
    },
    {
        "name": "Transtorno por Uso de Substâncias",
        "english_name": "Substance Use Disorder",
        "cid": "F19.20", "dsm": "304.90",
        "icd11": "6C40", "icd11_title": "Transtorno por uso de substâncias",
        "category": "Transtornos por Uso de Substâncias",
        "symptoms": [
            ("substance_craving", "Fissura ou desejo intenso pela substância", 0.90, 0.05, True, 365),
            ("loss_control", "Dificuldade em controlar o uso", 0.85, 0.04, False, 365),
            ("withdrawal", "Síndrome de abstinência", 0.75, 0.06, False, 0),
            ("tolerance", "Tolerância aumentada", 0.70, 0.05, False, 365),
            ("neglect_activities", "Negligência de atividades", 0.65, 0.04, False, 365),
        ],
        "groups": {"A": {"required": 2, "total": 5, "min_duration": 365}},
        "thresholds": [
            ("leve", 2, 365, 3.0), ("moderado", 3, 365, 5.0), ("grave", 4, 365, 7.0),
        ],
    },
    {
        "name": "Anorexia Nervosa",
        "english_name": "Anorexia Nervosa",
        "cid": "F50.0", "dsm": "307.1",
        "icd11": "6B80", "icd11_title": "Anorexia nervosa",
        "category": "Transtornos Alimentares",
        "symptoms": [
            ("restrictive_eating", "Restrição alimentar intensa", 0.95, 0.04, True, 90),
            ("weight_fear", "Medo intenso de ganhar peso", 0.90, 0.03, True, 90),
            ("body_image_distortion", "Distorção da imagem corporal", 0.85, 0.04, False, 90),
            ("low_weight", "Peso corporal significativamente baixo", 0.90, 0.05, True, 90),
        ],
        "groups": {"A": {"required": 3, "total": 4, "min_duration": 90}},
        "thresholds": [
            ("leve", 3, 90, 3.0), ("moderado", 4, 90, 5.0), ("grave", 4, 90, 7.0),
        ],
    },
    {
        "name": "Bulimia Nervosa",
        "english_name": "Bulimia Nervosa",
        "cid": "F50.2", "dsm": "307.51",
        "icd11": "6B81", "icd11_title": "Bulimia nervosa",
        "category": "Transtornos Alimentares",
        "symptoms": [
            ("binge_eating", "Episódios de compulsão alimentar", 0.95, 0.03, True, 90),
            ("purging", "Comportamentos compensatórios (vômito, laxantes)", 0.85, 0.04, True, 90),
            ("binge_control_loss", "Sensação de perda de controle durante compulsão", 0.90, 0.05, False, 90),
            ("self_evaluation_weight", "Autoavaliação indevidamente influenciada pelo peso", 0.80, 0.04, False, 90),
        ],
        "groups": {"A": {"required": 3, "total": 4, "min_duration": 90}},
        "thresholds": [
            ("leve", 3, 90, 3.0), ("moderado", 3, 90, 5.0), ("grave", 4, 90, 7.0),
        ],
    },
    {
        "name": "Transtorno de Compulsão Alimentar",
        "english_name": "Binge-Eating Disorder",
        "cid": "F50.8", "dsm": "307.59",
        "icd11": "6B82", "icd11_title": "Transtorno de compulsão alimentar periódica",
        "category": "Transtornos Alimentares",
        "symptoms": [
            ("binge_episodes", "Episódios recorrentes de compulsão alimentar", 0.95, 0.03, True, 90),
            ("binge_distress", "Sofrimento acentuado durante as compulsões", 0.85, 0.04, False, 90),
            ("binge_alone", "Comer sozinho por vergonha", 0.75, 0.03, False, 90),
            ("binge_depressed", "Sentimentos de depressão ou culpa após compulsão", 0.80, 0.04, False, 90),
        ],
        "groups": {"A": {"required": 3, "total": 4, "min_duration": 90}},
        "thresholds": [
            ("leve", 3, 90, 3.0), ("moderado", 3, 90, 5.0), ("grave", 4, 90, 7.0),
        ],
    },
    {
        "name": "Transtorno de Insônia",
        "english_name": "Insomnia Disorder",
        "cid": "G47.0", "dsm": "307.42",
        "icd11": "7A00", "icd11_title": "Transtorno de insônia",
        "category": "Transtornos do Sono-Vigília",
        "symptoms": [
            ("sleep_onset", "Dificuldade para iniciar o sono", 0.90, 0.04, True, 90),
            ("sleep_maintenance", "Dificuldade para manter o sono", 0.85, 0.05, False, 90),
            ("early_waking", "Despertar precoce", 0.70, 0.04, False, 90),
            ("daytime_impairment", "Prejuízo diurno devido ao sono", 0.80, 0.06, False, 90),
        ],
        "groups": {"A": {"required": 3, "total": 4, "min_duration": 90}},
        "thresholds": [
            ("leve", 3, 90, 3.0), ("moderado", 3, 90, 5.0), ("grave", 4, 90, 7.0),
        ],
    },
    {
        "name": "Esquizofrenia / Transtorno Psicótico",
        "english_name": "Schizophrenia / Psychotic Disorder",
        "cid": "F20.9", "dsm": "295.9",
        "icd11": "6A20", "icd11_title": "Esquizofrenia",
        "category": "Transtornos do Espectro da Esquizofrenia",
        "symptoms": [
            ("delusions", "Delírios", 0.85, 0.02, True, 30),
            ("hallucinations", "Alucinações", 0.80, 0.03, True, 30),
            ("disorganized_speech", "Discurso desorganizado", 0.65, 0.02, False, 30),
            ("negative_symptoms", "Sintomas negativos (embotamento afetivo, avolia)", 0.70, 0.04, False, 30),
            ("social_dysfunction", "Disfunção social/laboral", 0.75, 0.05, False, 180),
        ],
        "groups": {"A": {"required": 2, "total": 5, "min_duration": 30}},
        "thresholds": [
            ("leve", 2, 30, 3.0), ("moderado", 3, 30, 5.0), ("grave", 4, 30, 7.0),
        ],
    },
    {
        "name": "Transtorno de Sintomas Somáticos",
        "english_name": "Somatic Symptom Disorder",
        "cid": "F45.1", "dsm": "300.82",
        "icd11": "6C20", "icd11_title": "Transtorno de sintomas somáticos",
        "category": "Transtornos de Sintomas Somáticos",
        "symptoms": [
            ("somatic_symptoms", "Sintomas somáticos causando sofrimento", 0.90, 0.05, True, 14),
            ("excessive_health_concern", "Preocupação excessiva com a saúde", 0.80, 0.04, False, 14),
            ("medical_consultation", "Consultas médicas frequentes", 0.75, 0.06, False, 180),
            ("symptom_persistence", "Persistência dos sintomas apesar de avaliação adequada", 0.70, 0.05, False, 180),
        ],
        "groups": {"A": {"required": 2, "total": 4, "min_duration": 180}},
        "thresholds": [
            ("leve", 2, 180, 3.0), ("moderado", 3, 180, 5.0), ("grave", 4, 180, 7.0),
        ],
    },
    {
        "name": "Transtorno do Espectro Autista",
        "english_name": "Autism Spectrum Disorder",
        "cid": "F84.0", "dsm": "299.00",
        "icd11": "6A02", "icd11_title": "Transtorno do espectro autista",
        "category": "Transtornos do Neurodesenvolvimento",
        "symptoms": [
            ("social_communication", "Déficits na comunicação social", 0.95, 0.03, True, 365),
            ("restricted_interests", "Interesses restritos e fixos", 0.85, 0.04, False, 365),
            ("repetitive_movements", "Movimentos repetitivos ou estereotipados", 0.75, 0.05, False, 365),
            ("sensory_sensitivity", "Hipersensibilidade ou hipossensibilidade sensorial", 0.70, 0.06, False, 365),
            ("routine_insistence", "Insistência em rotinas e rituais", 0.80, 0.04, False, 365),
        ],
        "groups": {"A": {"required": 3, "total": 5, "min_duration": 365}},
        "thresholds": [
            ("nível_1", 3, 365, 3.0), ("nível_2", 4, 365, 5.0), ("nível_3", 5, 365, 7.0),
        ],
    },
    {
        "name": "Transtorno de Déficit de Atenção/Hiperatividade",
        "english_name": "ADHD",
        "cid": "F90.0", "dsm": "314.01",
        "icd11": "6A05", "icd11_title": "Transtorno de déficit de atenção/hiperatividade",
        "category": "Transtornos do Neurodesenvolvimento",
        "symptoms": [
            ("inattention", "Desatenção persistente", 0.90, 0.05, True, 180),
            ("hyperactivity", "Hiperatividade", 0.80, 0.04, False, 180),
            ("impulsivity", "Impulsividade", 0.75, 0.04, False, 180),
            ("organizational_difficulty", "Dificuldade organizacional", 0.70, 0.05, False, 180),
            ("forgetfulness", "Esquecimento frequente", 0.65, 0.04, False, 180),
        ],
        "groups": {"A": {"required": 3, "total": 5, "min_duration": 180}},
        "thresholds": [
            ("leve", 3, 180, 3.0), ("moderado", 4, 180, 5.0), ("grave", 5, 180, 7.0),
        ],
    },
]

# Map English BN disorder names to Portuguese names for inference lookup
BN_TO_PT = {d["english_name"]: d["name"] for d in DISORDER_DEFS}

# Scale definitions
SCALE_DEFS = {
    "PHQ-9": {
        "description": "Patient Health Questionnaire — 9 itens para rastreio de depressão",
        "questions": [
            "Pouco interesse ou prazer em fazer as coisas",
            "Se sentir para baixo, deprimido(a) ou sem esperança",
            "Dificuldade para pegar no sono ou permanecer dormindo",
            "Se sentir cansado(a) ou com pouca energia",
            "Falta de apetite ou comendo demais",
            "Se sentir mal consigo mesmo(a) — ou acha que é um fracasso",
            "Dificuldade para se concentrar nas coisas",
            "Falar ou se mover mais devagar que o normal",
            "Pensamentos de que seria melhor estar morto(a)",
        ],
        "max_score": 27.0,
        "severity": [(0, "none"), (5, "mild"), (10, "moderate"), (15, "moderately severe"), (20, "severe")],
    },
    "GAD-7": {
        "description": "Generalized Anxiety Disorder — 7 itens para rastreio de ansiedade",
        "questions": [
            "Se sentir nervoso(a), ansioso(a) ou muito tenso(a)",
            "Não conseguir parar de se preocupar",
            "Se preocupar demais com coisas diferentes",
            "Dificuldade para relaxar",
            "Ficar tão agitado(a) que é difícil ficar parado(a)",
            "Ficar facilmente irritado(a) ou chateado(a)",
            "Se sentir com medo como se algo terrível fosse acontecer",
        ],
        "max_score": 21.0,
        "severity": [(0, "none"), (5, "mild"), (10, "moderate"), (15, "severe")],
    },
    "MADRS": {
        "description": "Escala de Depressão de Montgomery-Åsberg — 10 itens para gravidade da depressão",
        "questions": [
            "Tristeza aparente — desânimo, melancolia e desespero",
            "Tristeza relatada — relatos de humor deprimido",
            "Tensão interna — sentimentos de desconforto vago, irritabilidade",
            "Sono reduzido — redução da duração ou profundidade do sono",
            "Apetite reduzido — sensação de perda de apetite",
            "Dificuldade de concentração — dificuldade em organizar os pensamentos",
            "Lassidão — dificuldade em iniciar atividades diárias",
            "Incapacidade de sentir — interesse reduzido pelo ambiente",
            "Pensamentos pessimistas — culpa, inferioridade, ruína",
            "Pensamentos suicidas — desejo de morrer",
        ],
        "max_score": 60.0,
        "severity": [(0, "absent"), (7, "mild"), (20, "moderate"), (35, "severe")],
    },
    "MDQ": {
        "description": "Questionário de Transtorno do Humor — 13 itens para triagem de espectro bipolar",
        "questions": [
            "Sentiu-se tão bem ou eufórico que outros acharam que você não estava normal?",
            "Sentiu-se tão irritado que gritou com pessoas ou começou brigas?",
            "Sentiu-se muito mais autoconfiante que o habitual?",
            "Dormiu muito menos que o habitual e não se sentiu cansado?",
            "Falou muito mais ou mais rápido que o habitual?",
            "Teve pensamentos acelerados na cabeça?",
            "Distraiu-se facilmente com coisas sem importância?",
            "Teve muito mais energia que o habitual?",
            "Esteve muito mais ativo ou fez muitas coisas ao mesmo tempo?",
            "Esteve muito mais sociável ou extrovertido que o habitual?",
            "Teve muito mais interesse por sexo que o habitual?",
            "Fez coisas que poderiam ter causado problemas (gastos, sexo, investimentos)?",
            "Gastou dinheiro que causou problemas financeiros?",
        ],
        "max_score": 13.0,
        "severity": [(0, "negative"), (7, "positive")],
    },
    "PCL-5": {
        "description": "Lista de Verificação de TEPT para DSM-5 — 20 itens",
        "questions": [
            "Memórias repetitivas e angustiantes do evento estressante?",
            "Sonhos repetitivos e angustiantes sobre o evento?",
            "Sentir ou agir como se o evento estivesse acontecendo novamente?",
            "Ficar muito perturbado quando algo lembrava o evento?",
            "Ter fortes reações físicas quando lembrado do evento?",
            "Evitar memórias, pensamentos ou sentimentos sobre o evento?",
            "Evitar lembranças externas do evento?",
            "Dificuldade em lembrar partes importantes do evento?",
            "Ter crenças negativas fortes sobre si mesmo ou o mundo?",
            "Culpar a si mesmo ou outros pelo evento?",
            "Ter sentimentos negativos fortes (medo, culpa, vergonha)?",
            "Perda de interesse em atividades que antes gostava?",
            "Sentir-se distante ou afastado dos outros?",
            "Dificuldade em experimentar sentimentos positivos?",
            "Comportamento irritado ou agressivo?",
            "Comportamento imprudente ou autodestrutivo?",
            "Estar excessivamente alerta ou vigilante?",
            "Assustar-se facilmente?",
            "Dificuldade de concentração?",
            "Dificuldade para pegar no sono ou permanecer dormindo?",
        ],
        "max_score": 80.0,
        "severity": [(0, "none"), (31, "mild"), (45, "moderate"), (56, "severe")],
    },
    "Y-BOCS": {
        "description": "Escala Obsessivo-Compulsiva de Yale-Brown — 10 itens para gravidade do TOC",
        "questions": [
            "Tempo gasto com pensamentos obsessivos?",
            "Interferência dos pensamentos obsessivos?",
            "Sofrimento causado pelos pensamentos obsessivos?",
            "Resistência aos pensamentos obsessivos?",
            "Controle sobre os pensamentos obsessivos?",
            "Tempo gasto com comportamentos compulsivos?",
            "Interferência dos comportamentos compulsivos?",
            "Sofrimento ao ser impedido de realizar compulsões?",
            "Resistência às compulsões?",
            "Controle sobre as compulsões?",
        ],
        "max_score": 40.0,
        "severity": [(0, "none"), (8, "mild"), (16, "moderate"), (24, "severe"), (32, "extreme")],
    },
    "AUDIT": {
        "description": "Teste de Identificação de Transtornos por Uso de Álcool — 10 itens",
        "questions": [
            "Com que frequência você consome bebidas alcoólicas?",
            "Quantas doses você consome em um dia típico?",
            "Com que frequência consome seis ou mais doses em uma ocasião?",
            "Com que frequência não conseguia parar de beber depois de começar?",
            "Com que frequência deixou de fazer o esperado por causa da bebida?",
            "Com que frequência precisou de uma bebida pela manhã?",
            "Com que frequência sentiu culpa ou remorso após beber?",
            "Com que frequência não conseguiu se lembrar da noite anterior?",
            "Alguém já se feriu por causa do seu consumo de álcool?",
            "Algum parente, amigo ou médico já sugeriu reduzir a bebida?",
        ],
        "max_score": 40.0,
        "severity": [(0, "low_risk"), (8, "hazardous"), (16, "harmful"), (20, "dependence")],
    },
    "ASRM": {
        "description": "Escala de Autoavaliação de Mania de Altman — 5 itens para triagem de mania",
        "questions": [
            "Mais feliz ou animado que o habitual?",
            "Mais autoconfiante que o habitual?",
            "Dormiu menos que o habitual sem se sentir cansado?",
            "Falou mais que o habitual?",
            "Esteve tão ativo que outras pessoas acharam incomum?",
        ],
        "max_score": 20.0,
        "severity": [(0, "none"), (6, "possible_hypomania"), (10, "probable_mania")],
    },
    "ASRS": {
        "description": "Escala de Autorrelato de TDAH em Adultos v1.1 — 18 itens",
        "questions": [
            "Dificuldade para finalizar os últimos detalhes de um projeto?",
            "Dificuldade para organizar tarefas?",
            "Problemas para lembrar compromissos ou obrigações?",
            "Evita ou adia iniciar tarefas que exigem concentração?",
            "Mexe as mãos ou os pés quando precisa ficar sentado?",
            "Sente-se excessivamente ativo e compelido a fazer coisas?",
            "Comete erros por descuido em projetos chatos ou difíceis?",
            "Dificuldade de manter a atenção em trabalhos repetitivos?",
            "Dificuldade de se concentrar no que as pessoas dizem?",
            "Perde ou tem dificuldade de encontrar objetos?",
            "Se distrai com atividades ou barulho ao redor?",
            "Se levanta em reuniões quando deveria ficar sentado?",
            "Se sente inquieto ou agitado?",
            "Dificuldade para relaxar quando tem tempo livre?",
            "Fala demais em situações sociais?",
            "Completa as frases das pessoas durante conversa?",
            "Dificuldade para esperar sua vez?",
            "Interrompe os outros quando estão ocupados?",
        ],
        "max_score": 72.0,
        "severity": [(0, "low"), (17, "moderate"), (24, "high")],
    },
    "AQ-10": {
        "description": "Quociente do Espectro Autista — 10 itens de triagem para autismo em adultos",
        "questions": [
            "Costumo notar sons pequenos quando outros não percebem",
            "Concentro-me mais no quadro geral do que nos pequenos detalhes",
            "Acho fácil fazer mais de uma coisa ao mesmo tempo",
            "Consigo voltar rapidamente ao que estava fazendo após interrupção",
            "Acho fácil 'ler nas entrelinhas' quando alguém fala comigo",
            "Sei identificar se alguém está entediado ao me ouvir",
            "Tenho dificuldade em entender as intenções dos personagens ao ler",
            "Gosto de colecionar informações sobre categorias de coisas",
            "Acho fácil perceber o que alguém está pensando pelo rosto",
            "Tenho dificuldade em entender as intenções das pessoas",
        ],
        "max_score": 10.0,
        "severity": [(0, "negative"), (6, "positive")],
    },
}


def create_date_key(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day


def get_severity(score: float, thresholds: list) -> str:
    for threshold, label in reversed(thresholds):
        if score >= threshold:
            return label
    return thresholds[0][1]


def seed():
    engine = create_engine(settings.database_url, echo=False)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    # Clean existing clinical data
    session.execute(text("DELETE FROM diagnostic.diagnostic_inference CASCADE"))
    session.execute(text("DELETE FROM clinical.scale_responses CASCADE"))
    session.execute(text("DELETE FROM clinical.symptom_observation CASCADE"))
    session.execute(text("DELETE FROM clinical.clinical_notes CASCADE"))
    session.execute(text("DELETE FROM clinical.medical_reports CASCADE"))
    session.execute(text("DELETE FROM clinical.prescription_items CASCADE"))
    session.execute(text("DELETE FROM clinical.prescriptions CASCADE"))
    session.execute(text("DELETE FROM clinical.medications CASCADE"))
    session.execute(text("DELETE FROM clinical.clinical_alerts CASCADE"))
    session.execute(text("DELETE FROM clinical.clinical_consultation CASCADE"))
    session.execute(text("DELETE FROM clinical.clinical_episode CASCADE"))
    session.execute(text("DELETE FROM clinical.healthcare_professionals CASCADE"))
    session.execute(text("DELETE FROM clinical.patient_profile CASCADE"))
    session.execute(text("DELETE FROM security.patient_identity CASCADE"))
    session.execute(text("DELETE FROM diagnostic.icd11_differentials CASCADE"))
    session.execute(text("DELETE FROM diagnostic.icd11_exclusions CASCADE"))
    session.execute(text("DELETE FROM diagnostic.icd11_codes CASCADE"))
    session.execute(text("DELETE FROM diagnostic.criteria_thresholds CASCADE"))
    session.execute(text("DELETE FROM diagnostic.criteria_rules CASCADE"))
    session.execute(text("DELETE FROM diagnostic.criteria_groups CASCADE"))
    session.execute(text("DELETE FROM diagnostic.diagnosis_relationships CASCADE"))
    session.execute(text("DELETE FROM diagnostic.diagnostic_criteria CASCADE"))
    session.execute(text("DELETE FROM diagnostic.scale_questions CASCADE"))
    session.execute(text("DELETE FROM diagnostic.assessment_scales CASCADE"))
    session.execute(text("DELETE FROM diagnostic.disorders CASCADE"))
    session.execute(text("DELETE FROM diagnostic.symptoms CASCADE"))
    session.execute(text("DELETE FROM core.ethnicities CASCADE"))
    session.execute(text("DELETE FROM core.education_levels CASCADE"))
    session.execute(text("DELETE FROM core.gender_identities CASCADE"))
    session.execute(text("DELETE FROM core.sex_types CASCADE"))
    session.commit()

    # ========================================================================
    # 1. Core reference data
    # ========================================================================
    sex_types = []
    for code, desc in [("M", "Masculino"), ("F", "Feminino")]:
        st = SexType(code=code, description=desc)
        session.add(st)
        session.flush()
        sex_types.append(st)

    genders = []
    for code, desc in [("M", "Masculino"), ("F", "Feminino"), ("NB", "Não-binário"), ("O", "Outro")]:
        g = GenderIdentity(code=code, description=desc)
        session.add(g)
        session.flush()
        genders.append(g)

    edu_levels = []
    for code, desc in [
        ("EF", "Ensino Fundamental"), ("EM", "Ensino Médio"),
        ("ES", "Ensino Superior"), ("PG", "Pós-graduação"),
    ]:
        el = EducationLevel(code=code, description=desc)
        session.add(el)
        session.flush()
        edu_levels.append(el)

    ethnicities = []
    for code, desc in [
        ("BRANCA", "Branca"), ("PARDA", "Parda"), ("PRETA", "Preta"),
        ("AMARELA", "Amarela"), ("INDIGENA", "Indígena"),
    ]:
        et = Ethnicity(code=code, description=desc)
        session.add(et)
        session.flush()
        ethnicities.append(et)

    # ========================================================================
    # 2. Symptoms
    # ========================================================================
    symptom_map = {}
    for dd in DISORDER_DEFS:
        for sname, sdesc, *_ in dd["symptoms"]:
            if sname not in symptom_map:
                sym = Symptom(symptom_name=sname, symptom_description=sdesc)
                session.add(sym)
                session.flush()
                symptom_map[sname] = sym.symptom_id

    # ========================================================================
    # 3. Disorders with criteria, groups, ICD-11 codes
    # ========================================================================
    disorder_map = {}
    for dd in DISORDER_DEFS:
        dis = Disorder(
            disorder_name=dd["name"],
            cid_code=dd["cid"],
            dsm_code=dd["dsm"],
            disorder_description=f"Transtorno conforme CID-11 ({dd['icd11']}) e DSM-5-TR",
        )
        session.add(dis)
        session.flush()
        disorder_map[dd["name"]] = dis.disorder_id

        # Criteria
        for sname, sdesc, p_given, p_not, required, min_dur in dd["symptoms"]:
            dc = DiagnosticCriteria(
                disorder_id=dis.disorder_id,
                symptom_id=symptom_map[sname],
                required_presence=required,
                minimum_duration_days=min_dur if min_dur > 0 else None,
                clinical_notes=sdesc,
            )
            session.add(dc)

        # Criteria Groups
        for label, group_def in dd["groups"].items():
            cg = CriteriaGroup(
                disorder_id=dis.disorder_id,
                group_label=label,
                description=f"Criterion {label} — requires {group_def['required']} of {group_def['total']} symptoms",
                sort_order=ord(label) - 64,
            )
            session.add(cg)
            session.flush()
            cr = CriteriaRule(
                group_id=cg.group_id,
                required_count=group_def["required"],
                total_count=group_def["total"],
                min_duration_days=group_def["min_duration"] if group_def["min_duration"] > 0 else None,
            )
            session.add(cr)

        # Criteria Thresholds
        for severity, min_crit, min_dur, min_int in dd["thresholds"]:
            from app.models.base import CriteriaThreshold
            ct = CriteriaThreshold(
                disorder_id=dis.disorder_id,
                severity_level=severity,
                min_criteria_met=min_crit,
                min_duration_days=min_dur if min_dur > 0 else None,
                min_intensity=min_int,
            )
            session.add(ct)

        # ICD-11 codes
        icd = ICD11Code(
            disorder_id=dis.disorder_id,
            icd11_code=dd["icd11"],
            icd11_title=dd["icd11_title"],
            chapter="Mental and behavioural disorders",
            chapter_code="06",
            clinical_description=dd["name"],
            diagnostic_requirements=(
                f"DSM-5-TR: {list(dd['groups'].values())[0]['required']} of "
                f"{list(dd['groups'].values())[0]['total']} symptoms required"
            ),
        )
        session.add(icd)

    # ========================================================================
    # 4. Assessment scales
    # ========================================================================
    scale_map = {}
    for sname, sdef in SCALE_DEFS.items():
        scale = AssessmentScale(scale_name=sname, scale_description=sdef["description"])
        session.add(scale)
        session.flush()
        questions = []
        for i, qtext in enumerate(sdef["questions"]):
            q = ScaleQuestion(scale_id=scale.scale_id, question_text=qtext, question_order=i + 1)
            session.add(q)
            session.flush()
            questions.append(q)
        scale_map[sname] = {"scale": scale, "questions": questions, "def": sdef}

    # ========================================================================
    # 5. Healthcare professionals
    # ========================================================================
    professionals = []
    prof_names = [
        ("Dr. Ricardo Almeida", "CRM 12345-SP", "Psiquiatria", "Psiquiatria Clínica"),
        ("Dra. Mariana Costa", "CRM 23456-SP", "Psiquiatria", "Psiquiatria da Infância"),
        ("Dr. Fernando Oliveira", "CRP 34567-SP", "Psicologia", "Psicologia Clínica"),
        ("Dra. Patrícia Santos", "CRP 45678-SP", "Psicologia", "Neuropsicologia"),
        ("Dr. Eduardo Martins", "CRM 56789-SP", "Psiquiatria", "Psiquiatria Geral"),
    ]
    for name, license_no, profession, specialty in prof_names:
        prof = HealthcareProfessional(
            full_name=name,
            professional_license=license_no,
            profession=profession,
            specialty=specialty,
            start_date=date(2018, 1, 1),
        )
        session.add(prof)
        session.flush()
        professionals.append(prof)

    # ========================================================================
    # 6. Patients with clinical profiles
    # ========================================================================
    patient_data = []
    num_patients = 50

    for i in range(num_patients):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        patient_uuid = uuid4()

        sex = random.choice(sex_types)
        gender = random.choice(genders)
        edu = random.choice(edu_levels)
        eth = random.choice(ethnicities)
        birth = date.today() - timedelta(days=random.randint(6570, 29200))

        marital_options = ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"]
        marital = random.choice(marital_options)
        occupations = [
            "Professor(a)", "Engenheiro(a)", "Advogado(a)", "Médico(a)",
            "Comerciante", "Estudante", "Aposentado(a)", "Autônomo(a)",
            "Desenvolvedor(a)", "Analista de Sistemas",
        ]
        occupation = random.choice(occupations)

        # Encrypt PII
        encrypted_name = encrypt_field(full_name)
        pi = PatientIdentity(
            patient_uuid=patient_uuid,
            full_name=encrypted_name,
        )
        session.add(pi)
        session.flush()

        pp = PatientProfile(
            patient_uuid=patient_uuid,
            birth_date=birth,
            sex_type_id=sex.sex_type_id,
            gender_identity_id=gender.gender_identity_id,
            education_level_id=edu.education_level_id,
            ethnicity_id=eth.ethnicity_id,
            marital_status=marital,
            occupation=occupation,
        )
        session.add(pp)
        session.flush()

        age = (date.today() - birth).days // 365
        patient_data.append({
            "patient_uuid": patient_uuid,
            "profile_uuid": pp.profile_uuid,
            "full_name": full_name,
            "age": age,
            "sex": sex.description,
            "education": edu.description,
            "ethnicity": eth.description,
            "marital": marital,
            "occupation": occupation,
        })

    # ========================================================================
    # 7. Assign disorders to patients (comorbidity patterns)
    # ========================================================================
    # Each patient gets 1-3 disorders with realistic comorbidity
    disorder_names = [dd["name"] for dd in DISORDER_DEFS]
    patient_disorders = {}
    for pd_item in patient_data:
        # Primary disorder
        primary = random.choice(disorder_names)
        assigned = [primary]
        # Comorbidity: 40% chance of secondary, 15% chance of tertiary
        others = [d for d in disorder_names if d != primary]
        if random.random() < 0.40:
            secondary = random.choice(others)
            assigned.append(secondary)
            others.remove(secondary)
        if random.random() < 0.15:
            tertiary = random.choice(others)
            assigned.append(tertiary)
        patient_disorders[pd_item["patient_uuid"]] = assigned

    # ========================================================================
    # 8. Generate consultations with symptoms and scale responses
    # ========================================================================
    consultation_records = []
    inference_records = []

    for pd_item in patient_data:
        disorders = patient_disorders[pd_item["patient_uuid"]]
        num_consultations = random.randint(2, 6)

        for ci in range(num_consultations):
            days_ago = random.randint(1, 365)
            consult_date = datetime.now() - timedelta(days=days_ago)
            prof = random.choice(professionals)

            consult = ClinicalConsultation(
                consultation_uuid=uuid4(),
                profile_uuid=pd_item["profile_uuid"],
                professional_uuid=prof.professional_uuid,
                consultation_date=consult_date,
                consultation_notes=f"Consulta de acompanhamento #{ci + 1}",
            )
            session.add(consult)
            session.flush()
            consultation_records.append(consult)

            # Add symptoms for assigned disorders
            for dd in DISORDER_DEFS:
                if dd["name"] in disorders:
                    # Each symptom has a probability of being present
                    for sname, sdesc, p_given, p_not, required, min_dur in dd["symptoms"]:
                        if random.random() < p_given * 0.85:
                            intensity = round(random.uniform(3.0, 9.0), 2)
                            freq_options = ["daily", "several_times_week", "weekly", "several_times_month"]
                            freq = random.choice(freq_options)
                            duration = random.randint(min_dur if min_dur > 0 else 1, max(min_dur + 60, 90))
                            obs = SymptomObservation(
                                consultation_uuid=consult.consultation_uuid,
                                symptom_id=symptom_map[sname],
                                intensity=intensity,
                                frequency=freq,
                                duration_days=duration,
                                clinical_notes=sdesc,
                            )
                            session.add(obs)

            # Add scale responses
            for sname, sinfo in scale_map.items():
                scale_def = sinfo["def"]
                max_q_score = 3
                if sname in ("MADRS",):
                    max_q_score = 6
                elif sname in ("MDQ", "AQ-10"):
                    max_q_score = 1
                elif sname in ("PCL-5", "Y-BOCS", "AUDIT", "ASRM", "ASRS"):
                    max_q_score = 4

                # Map scales to relevant disorder keywords for base severity
                scale_disorder_map = {
                    "PHQ-9": ["Depressiv"],
                    "GAD-7": ["Ansiedade"],
                    "MADRS": ["Depressiv"],
                    "MDQ": ["Bipolar"],
                    "PCL-5": ["Estresse Pós-Traumático"],
                    "Y-BOCS": ["Obsessivo-Compulsivo"],
                    "AUDIT": ["Substâncias"],
                    "ASRM": ["Bipolar"],
                    "ASRS": ["Déficit de Atenção/Hiperatividade", "TDAH"],
                    "AQ-10": ["Espectro Autista", "Autista"],
                }
                matched = [d for d in disorders if any(k in d for k in scale_disorder_map.get(sname, []))]
                if matched:
                    base_severity = random.randint(
                        int(len(scale_def["questions"]) * max_q_score * 0.4),
                        int(len(scale_def["questions"]) * max_q_score * 0.8),
                    )
                else:
                    base_severity = random.randint(0, int(len(scale_def["questions"]) * max_q_score * 0.25))

                # Generate per-question scores
                total = 0
                num_q = len(sinfo["questions"])
                for q in sinfo["questions"]:
                    score = min(max_q_score, max(0, int(base_severity / num_q + random.gauss(0, 0.5))))
                    sr = ScaleResponse(
                        consultation_uuid=consult.consultation_uuid,
                        question_id=q.question_id,
                        response_value=score,
                        response_text=str(score),
                    )
                    session.add(sr)
                    total += score

            # Run inference — determine which disorder has highest probability
            from app.ml.inference.bayesian_network import BayesianNetwork, InferenceEvidence
            from app.ml.models.network_definition import build_mood_disorder_network

            try:
                bn = build_mood_disorder_network()
                evidence = []
                for dd in DISORDER_DEFS:
                    for sname, *_ in dd["symptoms"]:
                        has_symptom = session.query(SymptomObservation).filter(
                            SymptomObservation.consultation_uuid == consult.consultation_uuid,
                            SymptomObservation.symptom_id == symptom_map[sname],
                        ).first()
                        if has_symptom:
                            evidence.append(InferenceEvidence(
                                sname, present=True,
                                intensity=float(has_symptom.intensity) if has_symptom.intensity else None,
                            ))

                if evidence:
                    results = bn.infer(evidence, top_k=5, apply_comorbidity=True)
                    for rank, result in enumerate(results):
                        pt_name = BN_TO_PT.get(result.disorder_name, result.disorder_name)
                        dis_id = disorder_map.get(pt_name)
                        if dis_id:
                            inf = DiagnosticInference(
                                consultation_uuid=consult.consultation_uuid,
                                disorder_id=dis_id,
                                inference_probability=result.posterior_probability,
                                confidence_level=result.confidence_interval_upper,
                                generated_by_model="bayesian-network",
                                model_version="bayesian-net-v2",
                            )
                            session.add(inf)
                            session.flush()
                            inference_records.append(inf)
            except Exception as e:
                print(f"  [WARN] Inference failed for consultation: {e}")

    session.commit()

    # ========================================================================
    # Summary
    # ========================================================================
    total_patients = session.query(PatientIdentity).count()
    total_consults = session.query(ClinicalConsultation).count()
    total_symptoms = session.query(SymptomObservation).count()
    total_scales = session.query(ScaleResponse).count()
    total_inferences = session.query(DiagnosticInference).count()
    total_disorders = session.query(Disorder).count()

    print(f"\n{'='*60}")
    print(f"Seed complete! Clinical dataset created:")
    print(f"  Patients:      {total_patients}")
    print(f"  Disorders:     {total_disorders}")
    print(f"  Professionals: {len(professionals)}")
    print(f"  Consultations: {total_consults}")
    print(f"  Symptoms:      {total_symptoms}")
    print(f"  Scale Resp.:   {total_scales}")
    print(f"  Inferences:    {total_inferences}")
    print(f"{'='*60}")

    session.close()


if __name__ == "__main__":
    seed()
