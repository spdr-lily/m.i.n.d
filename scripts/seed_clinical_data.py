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
    SymptomObservation, ScaleResponse, DiagnosticInference, MedicalReport,
    CriteriaGroup, CriteriaRule, ICD11Code, User, ProfessionalPatientAssignment,
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

# Map English symptom keys (DISORDER_DEFS internal names) to Portuguese symptom names (db/seed.py)
EN_TO_PT_SYMPTOM = {
    # Depressão
    "depressed_mood": "humor_deprimido",
    "loss_of_interest": "anhedonia",
    "sleep_disturbance": "insonia_hipersonia",
    "fatigue": "fadiga",
    "appetite_changes": "alteracao_peso",
    "guilt_feelings": "sentimento_inutilidade",
    "concentration_problems": "concentracao",
    "psychomotor_changes": "agitacao_retardo",
    "suicidal_ideation": "pensamento_morte",
    # GAD
    "excessive_worry": "preocupacao_excessiva",
    "restlessness": "inquietacao",
    "fatigue_gad": "fadiga_constante",
    "muscle_tension": "tensao_muscular",
    "sleep_disturbance_gad": "sono_prejudicado",
    "irritability": "irritabilidade",
    "concentration_difficulty_gad": "concentracao",
    # Pânico
    "panic_attacks": "palpitacoes",
    "palpitations": "palpitacoes",
    "chest_pain": "dor_peito",
    "shortness_of_breath": "sensacao_sufocamento",
    "fear_of_dying": "medo_morrer",
    "derealization": "desrealizacao",
    "avoidance_behavior": "esquiva",
    # PTSD
    "traumatic_exposure": "reexperiencia",
    "intrusive_memories": "flashbacks_dissociativos",
    "nightmares": "sonhos_angustia",
    "hypervigilance": "hipervigilancia",
    "avoidance_ptsd": "esquiva",
    "negative_cognitions": "crencas_negativas",
    "startle_response": "sobresalto_acentuado",
    # Distimia
    "chronic_low_mood": "humor_deprimido",
    "poor_appetite_dysthymia": "alteracao_peso",
    "low_self_esteem": "sentimento_inutilidade",
    "hopelessness": "desesperanca_futuro",
    "low_energy_dysthymia": "fadiga",
    # Ansiedade Social
    "social_fear": "preocupacao_excessiva",
    "avoidance_social": "esquiva",
    "performance_anxiety": "inquietacao",
    "blushing": "sudorese",
    # Bipolar I
    "euphoric_mood": "euforia",
    "increased_energy": "euforia",
    "grandiosity": "grandiosidade",
    "decreased_sleep": "reducao_sono",
    "rapid_speech": "logorreia",
    "racing_thoughts": "fuga_ideias",
    "distractibility": "concentracao",
    "risk_behavior": "comportamento_risco",
    # Bipolar II
    "hypomanic_mood": "euforia",
    "mildly_increased_energy": "euforia",
    "reduced_sleep_hypomania": "reducao_sono",
    # TOC
    "obsessions": "obsessoes",
    "compulsions": "compulsoes",
    "repetitive_behavior": "verificacao_repetitiva",
    "intrusive_thoughts": "obsessoes",
    # Agorafobia
    "fear_open_spaces": "medo_lugares_abertos",
    "avoidance_public": "evitacao_fobica",
    "need_escort": "medo_lugares_abertos",
    "panic_agora": "medo_morrer",
    # Substâncias
    "substance_craving": "desejo_intenso",
    "loss_control": "dificuldade_controle",
    "withdrawal": "abstinencia_substancia",
    "tolerance": "tolerancia_aumentada",
    "neglect_activities": "reducao_atividades",
    # Anorexia
    "restrictive_eating": "restricao_alimentar",
    "weight_fear": "medo_ganho_peso",
    "body_image_distortion": "distorcao_imagem",
    "low_weight": "peso_baixo",
    # Bulimia
    "binge_eating": "compulsao_alimentar",
    "purging": "vomito_autoinduzido",
    "binge_control_loss": "compulsao_alimentar",
    "self_evaluation_weight": "medo_ganho_peso",
    # Compulsão Alimentar
    "binge_episodes": "compulsao_alimentar",
    "binge_distress": "compulsao_alimentar",
    "binge_alone": "comer_oculto",
    "binge_depressed": "compulsao_alimentar",
    # Insônia
    "sleep_onset": "dificuldade_iniciar_sono",
    "sleep_maintenance": "sono_nao_restaurador",
    "early_waking": "despertar_precoce",
    "daytime_impairment": "sonolencia_diurna",
    # Psicótico
    "delusions": "delirios_persecutorios",
    "hallucinations": "alucinacoes_auditivas",
    "disorganized_speech": "discurso_desorganizado",
    "negative_symptoms": "embotamento_afetivo",
    "social_dysfunction": "comportamento_desorganizado",
    # Somático
    "somatic_symptoms": "sintomas_somaticos",
    "excessive_health_concern": "preocupacao_saude",
    "medical_consultation": "preocupacao_saude",
    "symptom_persistence": "sintomas_somaticos",
    # TEA
    "social_communication": "deficit_reciprocidade",
    "restricted_interests": "interesses_fixos",
    "repetitive_movements": "movimentos_estereotipados",
    "sensory_sensitivity": "reatividade_sensorial_atipica",
    "routine_insistence": "insistencia_rotina",
    # TDAH
    "inattention": "desatencao_detalhes",
    "hyperactivity": "inquietacao_motora",
    "impulsivity": "dificuldade_esperar_vez",
    "organizational_difficulty": "dificuldade_organizacao",
    "forgetfulness": "esquecimento_atividades",
    # ── Reference: Neurodesenvolvimento ──
    "intellectual_function_deficit": "deficit_intelectual",
    "adaptive_functioning_deficit": "deficit_adaptativo",
    "social_adaptive_deficit": "deficit_social_adaptativo",
    "developmental_onset": "inicio_desenvolvimento",
    "global_developmental_delay": "atraso_global_desenvolvimento",
    "motor_skill_delay": "atraso_motor",
    "speech_language_delay": "atraso_fala_linguagem",
    "cognitive_delay": "atraso_cognitivo",
    "social_skill_delay": "atraso_social",
    "language_acquisition_deficit": "deficit_aquisicao_linguagem",
    "language_comprehension_deficit": "deficit_compreensao_linguagem",
    "language_expression_deficit": "deficit_expressao_linguagem",
    "speech_sound_production_deficit": "deficit_producao_som_fala",
    "speech_intelligibility_deficit": "deficit_inteligibilidade_fala",
    "stuttering": "gagueira",
    "speech_block": "bloqueio_fala",
    "speech_avoidance": "esquiva_fala",
    "pragmatic_language_deficit": "deficit_linguagem_pragmatica",
    "conversational_turn_taking_deficit": "deficit_alternancia_turnos",
    "non_literal_language_deficit": "deficit_linguagem_nao_literal",
    "social_context_communication": "comunicacao_contexto_social",
    "reading_accuracy_deficit": "deficit_precisao_leitura",
    "reading_comprehension_deficit": "deficit_compreensao_leitura",
    "spelling_deficit": "deficit_ortografia",
    "written_expression_deficit": "deficit_expressao_escrita",
    "math_computation_deficit": "deficit_calculo_matematico",
    "math_reasoning_deficit": "deficit_raciocinio_matematico",
    "gross_motor_coordination_deficit": "deficit_coordenacao_motora_grossa",
    "fine_motor_coordination_deficit": "deficit_coordenacao_motora_fina",
    "manual_dexterity_impairment": "prejuizo_destrezas_manuais",
    "motor_milestone_delay": "atraso_marcos_motores",
    "repetitive_sterotyped_movements": "movimentos_repetitivos_estereotipados",
    "self_injurious_stereotypy": "comportamento_estereotipado_autolesivo",
    "stereotype_activity_interference": "interferencia_atividade_estereotipada",
    "multiple_motor_tics": "tiques_motores_multiplos",
    "vocal_tics": "tiques_vocais",
    "tic_duration_one_year": "tiques_duracao_um_ano",
    "tic_onset_before_18": "tiques_inicio_antes_18",
    "chronic_motor_tics": "tiques_motores_cronicos",
    "chronic_vocal_tics": "tiques_vocais_cronicos",
    "transient_motor_tics": "tiques_motores_transitorios",
    "transient_vocal_tics": "tiques_vocais_transitorios",
    # ── Reference: Psicótico ──
    "preserved_functioning": "funcionamento_preservado",
    "non_bizarre_delusions": "delirios_nao_bizarros",
    "acute_psychotic_symptoms": "sintomas_psicoticos_agudos",
    "symptom_duration_1_to_30_days": "duracao_sintomas_1_a_30_dias",
    "psychotic_sudden_onset": "inicio_subito_sintomas_psicoticos",
    "full_functional_recovery": "recuperacao_funcional_completa",
    "psychotic_symptoms_1_to_6_months": "sintomas_psicoticos_1_a_6_meses",
    "psychosis_without_mood": "psicose_sem_episodio_humor",
    "substance_induced_psychosis": "psicose_induzida_substancia",
    "substance_psychosis_temporal": "relacao_temporal_substancia_psicose",
    "psychosis_not_primary": "psicose_nao_primaria",
    "medical_condition_psychosis": "psicose_devido_condicao_medica",
    "no_substance_etiology": "sem_etiologia_substancia",
    "catatonic_stupor": "estupor_catatonico",
    "catatonic_excitement": "agitacao_catatonica",
    "catatonic_posturing": "postura_catatonica",
    "catatonic_mutism": "mutismo_catatonico",
    "echolalia_ecopraxia": "ecolalia_ecopraxia",
    # ── Reference: Bipolar ──
    "hypomanic_subclinical": "sintomas_hipomaniacos_subclinicos",
    "depressive_subclinical": "sintomas_depressivos_subclinicos",
    "cyclothymic_two_years": "ciclotimia_dois_anos",
    "no_major_mood_episode": "ausencia_episodio_humor_maior",
    "substance_induced_elevated_mood": "humor_elevado_induzido_substancia",
    "not_primary_bipolar": "nao_bipolar_primario",
    "medical_condition_mania": "mania_devido_condicao_medica",
    # ── Reference: Depressivo ──
    "temper_outbursts_severe": "explosoes_raiva_severas",
    "outburst_frequency_3x_week": "frequencia_explosoes_3x_semana",
    "irritable_mood_persistent": "humor_irritavel_persistente",
    "outbursts_multiple_settings": "explosoes_multiplos_ambientes",
    "dmd_onset_before_10": "inicio_tddh_antes_10_anos",
    "premenstrual_affective_lability": "labilidade_afetiva_pre_menstrual",
    "premenstrual_physical_symptoms": "sintomas_fisicos_pre_menstruais",
    "post_menses_remission": "remissao_pos_menstrual",
    "premenstrual_functional_impairment": "prejuizo_funcional_pre_menstrual",
    "substance_induced_depressed_mood": "humor_deprimido_induzido_substancia",
    "depressive_temporal_substance": "relacao_temporal_depressao_substancia",
    "not_primary_depression": "nao_depressao_primaria",
    "medical_condition_depression": "depressao_devido_condicao_medica",
    # ── Reference: Ansiedade ──
    "separation_fear": "medo_separacao_figuras_apego",
    "separation_worry_loss": "preocupacao_perda_figuras_apego",
    "separation_refusal": "recusa_separacao_casa",
    "separation_physical_symptoms": "sintomas_fisicos_separacao",
    "selective_mutism": "mutismo_seletivo",
    "speaks_other_settings": "fala_em_outros_contextos",
    "mutism_impairment": "prejuizo_mutismo_seletivo",
    "selective_mutism_duration": "duracao_mutismo_seletivo",
    "specific_phobic_fear": "medo_fobico_especifico",
    "active_phobic_avoidance": "esquiva_fobica_ativa",
    "fear_disproportional": "medo_desproporcional_perigo",
    "phobia_6_months": "fobia_seis_meses",
    "substance_induced_anxiety": "ansiedade_induzida_substancia",
    "anxiety_temporal_substance": "relacao_temporal_ansiedade_substancia",
    "not_primary_anxiety": "nao_ansiedade_primaria",
    "medical_condition_anxiety": "ansiedade_devido_condicao_medica",
    "not_during_delirium_anxiety": "nao_durante_delirium_ansiedade",
    # ── Reference: TOC ──
    "body_defect_preoccupation": "preocupacao_defeitos_aparencia",
    "appearance_checking": "verificacao_aparencia_repetitiva",
    "appearance_avoidance": "esquiva_situacoes_exposicao",
    "appearance_repetitive_behaviors": "comportamentos_repetitivos_aparencia",
    "difficulty_discarding": "dificuldade_descartar_objetos",
    "need_save_items": "necessidade_guardar_itens",
    "clutter_impairment": "acumulo_compromete_areas_vida",
    "acquiring_excess_items": "aquisicao_excessiva_itens",
    "hair_pulling": "arrancar_cabelos_recorrente",
    "attempts_stop_pulling": "tentativas_parar_arrancar_cabelos",
    "hair_loss_result": "perda_capilar_resultante",
    "hair_pulling_tension": "tensao_antes_arrancar_cabelos",
    "skin_picking": "beliscar_pele_recorrente",
    "attempts_stop_picking": "tentativas_parar_beliscar_pele",
    "skin_lesions": "lesoes_pele_resultantes",
    "skin_picking_tension": "tensao_antes_beliscar_pele",
    "substance_induced_obsessions": "obsessoes_induzidas_substancia",
    "not_primary_ocd": "nao_toc_primario",
    # ── Reference: Trauma ──
    "inhibited_withdrawal": "padrao_inibido_retraido",
    "reduced_social_reciprocity": "reciprocidade_social_reduzida",
    "emotional_regulation_impairment": "regulacao_emocional_prejudicada",
    "extreme_insufficient_care": "cuidados_insuficientes_extremos",
    "indiscriminate_sociability": "sociabilidade_indiscriminada",
    "lack_caregiver_checking": "falta_verificacao_cuidador",
    "willingness_leave_stranger": "disposicao_sair_estranhos",
    "traumatic_exposure_acute": "exposicao_traumatica_aguda",
    "acute_intrusion": "intrusao_aguda_trauma",
    "acute_dissociation": "dissociacao_aguda",
    "acute_avoidance": "esquiva_aguda",
    "acute_arousal": "excitacao_aumentada_aguda",
    "acute_stress_duration": "duracao_3_dias_1_mes",
    "stressor_response": "resposta_estressor_identificavel",
    "distress_disproportional": "sofrimento_desproporcional_estressor",
    "adjustment_onset_3_months": "inicio_3_meses_estressor",
    "adjustment_duration_6_months": "duracao_6_meses_fim_estressor",
    "persistent_grief": "dor_intensa_persistente_luto",
    "yearning_for_deceased": "anseio_intenso_falecido",
    "preoccupation_with_death": "preocupacao_pensamentos_falecido",
    "grief_identity_disruption": "perturbacao_identidade_luto",
    "emotional_numbness_grief": "entorpecimento_emocional_luto",
    # ── Reference: Dissociativos ──
    "identity_disruption": "perturbacao_identidade_estados_personalidade",
    "memory_gaps_daily": "lacunas_memoria_cotidianas",
    "autobiographical_amnesia": "amnesia_informacoes_autobiograficas",
    "dissociative_flashbacks": "flashbacks_dissociativos_personalidade",
    "not_neurological_amnesia": "nao_amnesia_neurologica",
    "depersonalization_dd": "despersonalizacao_fora_corpo",
    "reality_testing_preserved": "teste_realidade_preservado",
    "depersonalization_impairment": "prejuizo_despersonalizacao",
    # ── Reference: Somáticos ──
    "illness_preoccupation": "preocupacao_doenca_grave",
    "health_anxiety_elevated": "ansiedade_saude_elevada",
    "health_checking_behaviors": "comportamentos_verificacao_saude",
    "health_anxiety_6_months": "ansiedade_saude_6_meses",
    "functional_neurological_symptoms": "sintomas_neurologicos_funcionais",
    "neurological_incompatibility": "incompatibilidade_neurologica",
    "functional_motor_symptoms": "sintomas_motores_funcionais",
    "functional_sensory_symptoms": "sintomas_sensoriais_funcionais",
    "conversive_seizures": "crises_nao_epilepticas_psicogenicas",
    "symptom_falsification": "falsificacao_sinais_sintomas",
    "presenting_as_ill": "apresentacao_como_doente",
    "deceptive_behavior": "comportamento_enganoso",
    "factitious_medical_visits": "consultas_medicas_frequentes_facticias",
    "psychological_factors_medical": "fatores_psicologicos_afetam_condicao_medica",
    "behavior_treatment_impact": "comportamentos_afetam_tratamento",
    "stress_influences_medical": "estresse_influencia_condicao_medica",
    # ── Reference: Alimentares ──
    "non_nutritive_ingestion": "ingestao_substancias_nao_nutritivas",
    "pica_one_month": "pica_um_mes",
    "not_cultural_practice": "nao_pratica_cultural",
    "food_regurgitation": "regurgitacao_repetida_alimentos",
    "re_chewing_food": "remastigacao_alimentos",
    "not_gastrointestinal": "nao_condicao_gastrointestinal",
    "not_other_eating_disorder": "nao_outro_transtorno_alimentar",
    "restrictive_food_intake": "ingestao_alimentar_restritiva",
    "food_sensory_avoidance": "evitacao_sensorial_alimentos",
    "weight_loss_nutritional_deficit": "perda_peso_deficit_nutricional",
    "no_weight_shape_concern": "ausencia_preocupacao_peso_forma",
    # ── Reference: Eliminação ──
    "enuresis_repeated": "eliminacao_urina_repetida",
    "enuresis_frequency": "enurese_frequencia_2x_semana",
    "enurese_age_5": "idade_enurese_5_anos",
    "not_medical_enurese": "nao_condicao_medica_enurese",
    "encopresis_repeated": "eliminacao_fezes_repetida",
    "encopresis_frequency": "encoprese_frequencia_1x_mes",
    "encoprese_age_4": "idade_encoprese_4_anos",
    "not_medical_encoprese": "nao_condicao_medica_encoprese",
    # ── Reference: Sono ──
    "excessive_sleepiness_7h": "sonolencia_excessiva_7h_sono",
    "irresistible_sleep_episodes": "episodios_sono_irresistiveis",
    "hypersomnia_3x_week": "hipersonia_3x_semana",
    "non_restorative_sleep": "sono_nao_restaurador_duracao_adequada",
    "irresistible_sleep_attacks": "ataques_sono_irresistiveis",
    "cataplexy": "cataplexia",
    "sleep_paralysis": "paralisia_sono",
    "hypnagogic_hallucinations": "alucinacoes_hipnagogicas",
    "sleep_apnea_events": "pausas_respiratorias_sono",
    "loud_snoring": "ronco_intenso",
    "excessive_daytime_sleepiness_apnea": "sonolencia_diurna_excessiva_apneia",
    "central_sleep_apnea": "apneia_central_sono",
    "central_apnea_fragmented_sono": "sono_fragmentado_apneia_central",
    "shortness_of_breath_lying": "falta_ar_ao_deitar",
    "circadian_rhythm_disruption": "perturbacao_ritmo_circadiano",
    "circadian_insomnia_hypersomnia": "insonia_hipersonia_circadiana",
    "sleep_wake_misalignment": "desalinhamento_sono_vigilia",
    "circadian_duration_3_months": "duracao_circadiana_3_meses",
    "sleepwalking": "sonambulismo",
    "sleepwalking_confusion": "confusao_despertar_sonambulismo",
    "sleepwalking_amnesia": "amnesia_sonambulismo",
    "sleepwalking_risk": "risco_sonambulismo",
    "night_terror_screaming": "gritos_terror_noturno",
    "night_terror_inconsolable": "inconsolavel_terror_noturno",
    "night_terror_amnesia": "amnesia_terror_noturno",
    "night_terror_autonomic": "sinais_autonomicos_terror_noturno",
    "dysphoric_dreams": "sonhos_disfóricos_extensos",
    "nightmare_rapid_orientation": "despertar_rapido_orientado_pesadelo",
    "nightmare_distress": "sofrimento_pesadelos",
    "nightmare_frequency": "frequencia_pesadelos",
    "dream_enactment": "representacao_comportamental_sonhos",
    "rem_sleep_vocalization": "vocalizacao_sono_rem",
    "rem_sleep_movement": "movimentos_complexos_sono_rem",
    "rem_without_tonia": "rem_sem_atonia",
    "restless_legs_urge": "necessidade_mover_pernas",
    "rest_leg_worsening": "piora_repouso_pernas",
    "movement_leg_improvement": "melhora_movimento_pernas",
    "leg_symptoms_evening": "sintomas_pernas_noturnos",
    "restless_legs_3x_week": "pernas_inquietas_3x_semana",
    # ── Reference: Disfunções Sexuais ──
    "delayed_ejaculation": "ejaculacao_retardada",
    "delayed_ejaculation_frequency": "frequencia_ejaculacao_retardada",
    "delayed_ejaculation_duration": "duracao_ejaculacao_retardada",
    "erectile_difficulty": "dificuldade_erecao",
    "erectile_frequency": "frequencia_disfuncao_eretil",
    "erectile_duration": "duracao_disfuncao_eretil",
    "female_orgasm_delay": "ausencia_retardo_orgasmo_feminino",
    "female_orgasm_frequency": "frequencia_anorgasmia_feminina",
    "female_orgasm_duration": "duracao_anorgasmia_feminina",
    "reduced_sexual_interest": "reducao_interesse_sexual",
    "reduced_sexual_excitation": "reducao_excitacao_sexual",
    "sexual_interest_duration": "duracao_reducao_interesse_sexual",
    "no_sexual_initiative": "ausencia_iniciativa_sexual",
    "pelvic_penetration_pain": "dor_penetracao_pelvica",
    "pelvic_floor_tension": "tensao_musculos_pelvicos",
    "fear_pelvic_pain": "medo_dor_pelvica",
    "pelvic_pain_duration": "duracao_dor_pelvica",
    "reduced_male_sexual_desire": "reducao_desejo_sexual_masculino",
    "male_desire_duration": "duracao_desejo_hipoativo_masculino",
    "no_sexual_interest_male": "ausencia_interesse_sexual_masculino",
    "premature_ejaculation": "ejaculacao_prematura",
    "premature_ejaculation_frequency": "frequencia_ejaculacao_prematura",
    "premature_duration_6_months": "duracao_ejaculacao_prematura",
    # ── Reference: Disforia de Gênero ──
    "gender_incongruence": "incongruencia_genero_experienciado_designado",
    "cross_gender_preferences": "preferencias_outro_genero",
    "aversion_sex_characteristics": "aversao_caracteristicas_sexuais",
    "desire_be_other_gender": "desejo_ser_outro_genero",
    "preference_other_gender_peers": "preferencia_pares_outro_genero",
    "gender_identity_incongruence_adult": "incongruencia_identidade_genero_adulto",
    "desire_remove_sex_characteristics": "desejo_eliminar_caracteristicas_sexuais",
    "desire_other_gender_treatment": "desejo_tratado_como_outro_genero",
    "conviction_belongs_other_gender": "conviccao_pertencer_outro_genero",
    # ── Reference: Disruptivos ──
    "angry_irritable_mood": "humor_raivoso_irritavel",
    "argumentative_defiant": "comportamento_desafiador_questionador",
    "vindictiveness": "comportamento_vingativo",
    "odd_behavior_6_months": "comportamento_6_meses",
    "impulsive_aggressive_outbursts": "explosoes_agressivas_impulsivas",
    "outburst_damage": "explosoes_causam_dano",
    "outburst_disproportional": "explosoes_desproporcionais",
    "rights_violation_pattern": "padrao_violacao_direitos",
    "aggression_people_animals": "agressao_pessoas_animais",
    "property_destruction": "destruicao_propriedade",
    "deceitfulness_theft": "engano_furto",
    "serious_rule_violation": "violacao_grave_regras",
    "deliberate_fire_setting": "incendio_deliberado",
    "tension_before_fire": "tensao_antes_fogo",
    "fascination_fire": "fascinio_fogo",
    "pleasure_from_fire": "prazer_alivio_fogo",
    "stealing_impulse": "impulso_furtar_objetos",
    "tension_before_theft": "tensao_antes_furto",
    "pleasure_during_theft": "prazer_alivio_durante_furto",
    "stealing_not_anger_revenge": "furto_nao_vinganca",
    # ── Reference: Substâncias ──
    "alcohol_craving": "fissura_alcool",
    "slurred_speech": "fala_arrastada",
    "motor_incoordination": "incoordenacao_motora",
    "unstable_gait": "marcha_instavel",
    "alcohol_stupor_coma": "estupor_coma_alcoolico",
    "alcohol_withdrawal_tremor": "tremor_abstinencia_alcool",
    "alcohol_withdrawal_seizures": "convulsoes_abstinencia_alcool",
    "alcohol_withdrawal_hallucinations": "alucinacoes_abstinencia_alcool",
    "cannabis_craving": "fissura_cannabis",
    "cannabis_withdrawal": "abstinencia_cannabis",
    "cannabis_tolerance": "tolerancia_cannabis",
    "hallucinogen_craving": "fissura_alucinogenos",
    "use_continued_despite_problems": "uso_continuado_apesar_problemas",
    "inhalant_craving": "fissura_inalantes",
    "opioid_craving": "fissura_opioides",
    "opioid_withdrawal": "abstinencia_opioides",
    "opioid_tolerance": "tolerancia_opioides",
    "sedative_craving": "fissura_benzodiazepinicos",
    "sedative_withdrawal": "abstinencia_benzodiazepinicos",
    "sedative_tolerance": "tolerancia_benzodiazepinicos",
    "stimulant_craving": "fissura_estimulantes",
    "stimulant_withdrawal": "abstinencia_estimulantes",
    "stimulant_tolerance": "tolerancia_estimulantes",
    "tobacco_craving": "fissura_tabaco",
    "tobacco_withdrawal": "abstinencia_nicotina",
    "tobacco_tolerance": "tolerancia_nicotina",
    "gambling_preoccupation": "preocupacao_jogo",
    "gambling_tolerance": "tolerancia_jogo",
    "gambling_withdrawal": "abstinencia_jogo",
    "gambling_loss_chasing": "perseguir_perdas_jogo",
    "gambling_lying": "mentir_jogo",
    "gambling_financial_dependence": "dependencia_financeira_jogo",
    # ── Reference: Neurocognitivos ──
    "attention_disturbance": "perturbacao_atencao",
    "consciousness_disturbance": "perturbacao_consciencia",
    "cognitive_deficit_acute": "deficit_cognitivo_agudo",
    "delirium_fluctuation": "flutuacao_delirium",
    "delirium_causal_condition": "causa_fisiologica_delirium",
    "cognitive_decline_significant": "declinio_cognitivo_significativo",
    "daily_activity_dependence": "dependencia_atividades_diarias",
    "cognitive_concern": "preocupacao_declinio_cognitivo",
    "not_during_delirium": "nao_durante_delirium",
    "cognitive_decline_modest": "declinio_cognitivo_modesto",
    "preserved_independence": "independencia_preservada",
    "cognitive_test_decline": "prejuizo_testes_cognitivos",
    # ── Reference: Personalidade ──
    "paranoid_suspicion": "suspeita_generalizada_exploracao",
    "distrust_loyalty": "duvidas_lealdade_confianca",
    "grudges": "rancor_persistente",
    "threat_overreaction": "reacao_exagerada_ameacas",
    "hidden_meanings": "significados_ocultos",
    "suspicious_fidelity": "suspeita_fidelidade_conjugal",
    "social_detachment": "distanciamento_social",
    "lack_interest_relationships": "falta_interesse_relacionamentos",
    "emotional_coldness": "frieza_emocional_distanciamento",
    "indifference_praise_criticism": "indiferenca_criticas_elogios",
    "lack_pleasure": "prazer_poucas_atividades",
    "magical_thinking": "pensamento_magico_crencas_estranhas",
    "unusual_perceptual_experiences": "experiencias_perceptivas_incomuns",
    "eccentric_behavior": "comportamento_aparencia_excentrica",
    "ideas_of_reference": "ideias_referencia",
    "odd_speech_thinking": "pensamento_fala_estranhos",
    "lack_close_friends": "ausencia_amigos_proximos",
    "abandonment_fear": "medo_abandono_esforcos_desesperados",
    "unstable_relationships": "relacionamentos_instaveis_intensos",
    "identity_disturbance": "perturbacao_identidade_autoimagem",
    "impulsivity_borderline": "impulsividade_multiplas_areas",
    "self_harm_behaviors": "comportamento_suicida_automutilacao",
    "emotional_dysregulation_borderline": "instabilidade_afetiva_intensa",
    "chronic_emptiness": "vazio_cronico",
    "anger_dyscontrol_borderline": "raiva_intensa_dificuldade_controle",
    "transient_paranoid_stress": "ideacao_paranoide_transitoria_stress",
    "attention_center_need": "necessidade_centro_atencao",
    "seductive_behavior": "comportamento_sedutor_inadequado",
    "shallow_emotions": "emocoes_superficiais_mudancas_rapidas",
    "appearance_focus_attention": "aparencia_fisica_chamar_atencao",
    "theatrical_speech": "fala_teatral_impressionista",
    "suggestibility": "sugestionabilidade",
    "relationship_overestimation": "superestimacao_intimidade_relacoes",
    "grandiosity_narcissistic": "grandiosidade_senso_importancia",
    "admiration_requirement": "exige_admiracao_excessiva",
    "entitlement": "sentimento_merecimento_especial",
    "lack_empathy": "falta_empatia",
    "exploitative_behavior": "exploracao_outros_fins_proprios",
    "arrogant_attitude": "atitude_arrogante_insolente",
    "envy_others": "inveja_outros_crenca_invejado",
    "fantasies_success_power": "fantasias_sucesso_poder_beleza",
    "social_inhibition": "inibicao_social_medo_critica",
    "inadequacy_feelings": "sentimentos_inadequacao_inferioridade",
    "rejection_hypersensitivity": "hipersensibilidade_avaliacao_negativa",
    "avoidance_risk_activities": "esquiva_riscos_pessoais_vergonha",
    "decision_difficulty_dependent": "dificuldade_decisoes_sem_conselho",
    "responsibility_delegation": "delegacao_responsabilidades_outros",
    "disagreement_fear_dependent": "medo_discordar_perda_apoio",
    "helplessness_alone": "desamparo_sozinho",
    "urgency_new_relationship": "urgencia_novo_relacionamento",
    "self_care_worry": "preocupacao_cuidar_si_mesmo",
    "order_preoccupation": "preocupacao_detalhes_regras_ordem",
    "perfectionism_interference": "perfeccionismo_interfere_tarefas",
    "work_devotion_excessive": "dedicacao_excessiva_trabalho",
    "moral_inflexibility": "inflexibilidade_moral_etica",
    "delegation_reluctance": "relutancia_delegar_tarefas",
    "miserliness": "avareza",
    "hoarding_inability_discard": "incapacidade_descartar_objetos",
    "social_norm_violation": "incapacidade_adequar_normas_sociais",
    "deceitfulness_antisocial": "mentira_repetida_trapaca",
    "impulsivity_antisocial": "impulsividade_incapacidade_planejar",
    "aggressiveness_antisocial": "irritabilidade_agressividade",
    "recklessness_antisocial": "desrespeito_seguranca_propria_alheia",
    "irresponsibility_antisocial": "irresponsabilidade_consistente",
    "lack_remorse": "ausencia_remorso",
    "conduct_disorder_evidence": "evidencia_transtorno_conduta_15_anos",
    # ── Reference: Parafílicos ──
    "voyeuristic_arousal": "excitacao_sexual_observar_pessoa_suspeita",
    "voyeuristic_distress": "sofrimento_comportamento_voyeurista",
    "voyeuristic_6_months": "voyeurismo_seis_meses",
    "exhibitionistic_arousal": "excitacao_exposicao_genitais",
    "exhibitionistic_distress": "sofrimento_comportamento_exhibitionista",
    "exhibitionistic_6_months": "exibicionismo_seis_meses",
    "frotteuristic_arousal": "excitacao_tocar_esfregar_pessoa",
    "frotteuristic_distress": "sofrimento_comportamento_frotteurista",
    "frotteuristic_6_months": "frotteurismo_seis_meses",
    "masochistic_arousal": "excitacao_ser_humilhado_agredido",
    "masochistic_distress": "sofrimento_masoquismo_sexual",
    "masochistic_6_months": "masoquismo_sexual_seis_meses",
    "sadistic_arousal": "excitacao_sofrimento_outra_pessoa",
    "sadistic_distress": "sofrimento_sadismo_sexual",
    "sadistic_6_months": "sadismo_sexual_seis_meses",
    "pedophilic_arousal": "excitacao_atividade_sexual_crianca",
    "pedophilic_distress": "sofrimento_pedofilia",
    "pedophilic_6_months": "pedofilia_seis_meses",
    "pedophilic_age_16_5": "idade_pedofilia_16_5_anos",
    "fetishistic_arousal": "excitacao_objetos_nao_vivos",
    "fetishistic_distress": "sofrimento_fetichismo",
    "fetishistic_6_months": "fetichismo_seis_meses",
    "transvestic_arousal": "excitacao_trajar_sexo_oposto",
    "transvestic_distress": "sofrimento_transvestismo",
    "transvestic_6_months": "transvestismo_seis_meses",
    # ── Missing keys found during verification ──
    "alcohol_intoxication_symptoms": "sintomas_intoxicacao_alcool",
    "alcohol_tolerance": "tolerancia_alcool",
    "alcohol_withdrawal": "abstinencia_alcool",
    "apneia_sono": "apneia_sono",
    "depersonalization": "despersonalizacao_fora_corpo",
    "difficulty_suppressing_movements": "dificuldade_suprimir_movimentos",
    "exhibitionistic_action": "exibicionismo_acao",
    "frotteuristic_action": "frotteurismo_acao",
    "language_below_age": "linguagem_abaixo_idade",
    "sadistic_action": "sadismo_acao",
    "social_avoidance_desire": "esquiva_social_desejo",
    "social_communication_impairment": "prejuizo_comunicacao_social",
    "stuttering_anxiety": "ansiedade_gagueira",
    "use_risco_fisico": "uso_risco_fisico",
    "voyeuristic_action": "voyeurismo_acao",
    # ── Residual / unspecified disorder symptom keys ──
    "distress_impairment_symptoms": "distress_impairment_symptoms",
    "clinician_specifies_reason": "clinician_specifies_reason",
    "exclude_primary_disorder": "exclude_primary_disorder",
    "insufficient_information": "insufficient_information",
    "emergency_context": "emergency_context",
}

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
    "BFP": {
        "description": "Bateria Fatorial da Personalidade — avaliação dos 5 grandes fatores (Big Five): Abertura, Conscienciosidade, Extroversão, Amabilidade, Neuroticismo. 25 itens (5 por fator).",
        "max_score": 100.0,
        "severity": [(0, "Baixo"), (40, "Médio"), (70, "Alto"), (90, "Muito alto")],
        "questions": [
            "Abertura - Gosto de explorar ideias novas e diferentes culturas",
            "Abertura - Tenho interesses artísticos e aprecio a beleza nas artes e na natureza",
            "Abertura - Sou curioso(a) sobre como as coisas funcionam",
            "Abertura - Valorizo experiências incomuns e viagens a lugares novos",
            "Abertura - Gosto de refletir sobre conceitos abstratos e filosóficos",
            "Conscienciosidade - Sou organizado(a) e mantenho minhas coisas em ordem",
            "Conscienciosidade - Cumpro prazos e responsabilidades com disciplina",
            "Conscienciosidade - Planejo com antecedência antes de agir",
            "Conscienciosidade - Sou meticuloso(a) e atento(a) aos detalhes",
            "Conscienciosidade - Persisto nas tarefas até concluí-las",
            "Extroversão - Sou comunicativo(a) e gosto de conversar com pessoas",
            "Extroversão - Sinto-me energizado(a) em ambientes sociais e festas",
            "Extroversão - Faço amizades com facilidade",
            "Extroversão - Gosto de ser o centro das atenções em situações sociais",
            "Extroversão - Prefiro trabalhar em grupo do que sozinho(a)",
            "Amabilidade - Procuro manter boas relações e evitar conflitos",
            "Amabilidade - Sou empático(a) e me importo com os sentimentos alheios",
            "Amabilidade - Confio nas pessoas até que provem o contrário",
            "Amabilidade - Colaboro e coopero com os outros voluntariamente",
            "Amabilidade - Trato a todos com respeito e cordialidade",
            "Neuroticismo - Costumo me preocupar facilmente com situações cotidianas",
            "Neuroticismo - Fico tenso(a) e nervoso(a) com frequência",
            "Neuroticismo - Tenho oscilações frequentes de humor",
            "Neuroticismo - Sinto-me inseguro(a) sobre minhas decisões",
            "Neuroticismo - Fico facilmente irritado(a) ou frustrado(a)",
        ],
    },
    "DT-12 (Tríade Sombria)": {
        "description": "Dirty Dozen (Jonason & Webster, 2010) — 12 itens para avaliação da Tríade Sombria: Maquiavelismo, Narcisismo e Psicopatia. Escala Likert de 7 pontos (0=Discordo totalmente a 6=Concordo totalmente).",
        "max_score": 72.0,
        "severity": [(0, "Baixo"), (30, "Moderado"), (50, "Elevado"), (65, "Muito elevado")],
        "questions": [
            "Maquiavelismo - Costumo usar manipulação para conseguir o que quero",
            "Maquiavelismo - Tendo a bajular pessoas para obter vantagens",
            "Maquiavelismo - Utilizo outras pessoas para alcançar meus objetivos",
            "Maquiavelismo - Costumo explorar os outros em benefício próprio",
            "Narcisismo - Acredito que sou mais especial do que as outras pessoas",
            "Narcisismo - Gosto de ser o centro das atenções e receber admiração",
            "Narcisismo - Sinto que mereço tratamento diferenciado",
            "Narcisismo - Busco reconhecimento e status social",
            "Psicopatia - Tenho dificuldade em sentir culpa ou remorso",
            "Psicopatia - Sou insensível aos sentimentos dos outros",
            "Psicopatia - Tendo a ser impulsivo(a) e agir sem pensar nas consequências",
            "Psicopatia - Sinto tédio com facilidade e busco emoções fortes",
        ],
    },
    "MEMÓRIA": {
        "description": "Teste de Rastreio de Funções Mnêmicas — avaliação breve de memória de trabalho, curto prazo, longo prazo, episódica e semântica",
        "max_score": 16.0,
        "severity": [(0, "Déficit grave"), (5, "Déficit moderado"), (9, "Déficit leve"), (13, "Normal"), (16, "Normal superior")],
        "questions": [
            "Registro: capacidade de repetir imediatamente uma sequência de 5 palavras (0=0 palavras, 1=2-3 palavras, 2=4-5 palavras)",
            "Memória de trabalho: consegue repetir 4 dígitos em ordem inversa (0=não, 1=parcial, 2=sim)",
            "Aprendizagem verbal: após 3 tentativas, quantas das 5 palavras recorda (0=0-1, 1=2-3, 2=4-5)",
            "Memória episódica recente - recordação tardia: quantas palavras recorda após 5 minutos (0=0-1, 1=2-3, 2=4-5)",
            "Memória episódica - reconhecimento: reconhece as palavras-alvo entre distratores (0=não, 1=parcial, 2=sim)",
            "Memória semântica: nomeia corretamente 3 figuras de categorias distintas (0=0, 1=1-2, 2=3)",
            "Memória prospectiva: lembra-se de pedir um objeto após intervalo (0=não, 1=com pista, 2=sim)",
            "Orientação témporo-espacial: sabe dia, mês, ano e local (0=0-2, 1=3, 2=4 corretos)",
        ],
    },
    "QI - RASTREIO": {
        "description": "Teste de Rastreio Cognitivo — estimativa breve de funcionamento intelectual com domínios verbal, raciocínio perceptual, memória de trabalho e velocidade de processamento",
        "max_score": 30.0,
        "severity": [(0, "Muito abaixo da média"), (8, "Abaixo da média"), (15, "Médio inferior"), (20, "Média"), (25, "Médio superior"), (28, "Superior")],
        "questions": [
            "Vocabulário: define corretamente palavras de complexidade crescente (0=não, 1=parcial, 2=definição adequada, 3=elaboração precisa)",
            "Analogias verbais: identifica relação entre pares de palavras (0=não, 1=parcial, 2=adequado, 3=superior)",
            "Raciocínio matricial: completa padrões visuais abstratos (0=não, 1=1 padrão, 2=2 padrões, 3=todos)",
            "Cubos: constrói padrões geométricos com blocos coloridos (0=não, 1=com ajuda, 2=sem ajuda, 3=rápido e preciso)",
            "Memória de trabalho — dígitos ordem direta: repete até 7 dígitos (0=<4, 1=4-5, 2=6, 3=7)",
            "Memória de trabalho — dígitos ordem inversa: repete até 5 dígitos ao contrário (0=<3, 1=3, 2=4, 3=5)",
            "Velocidade de processamento: completa código símbolo-número em 120s (0=<20, 1=20-35, 2=36-50, 3=>50 corretos)",
            "Conhecimento geral: responde a perguntas de cultura geral (0=0-1, 1=2-3, 2=4-5, 3=6 corretas)",
            "Raciocínio aritmético: resolve problemas numéricos simples (0=não, 1=com ajuda, 2=sem ajuda, 3=rápido)",
            "Compreensão: explica situações sociais e normas (0=não, 1=parcial, 2=adequado, 3=elaborado)",
        ],
    },
    "RECONHECIMENTO DE ROSTOS": {
        "description": "Teste de Reconhecimento de Rostos — avaliação da percepção facial e memória para faces, adaptado do Benton Facial Recognition Test e Warrington Recognition Memory Test",
        "max_score": 12.0,
        "severity": [(0, "Déficit grave"), (4, "Déficit moderado"), (7, "Déficit leve"), (10, "Normal")],
        "questions": [
            "Identificação imediata: de 3 fotos, aponta a que corresponde à foto-alvo (0=não, 1=com pista, 2=sim)",
            "Identificação diferida: após 5 minutos, reconhece o rosto-alvo entre 6 distratores (0=não, 1=parcial, 2=sim)",
            "Discriminação de identidade: duas fotos da mesma pessoa em ângulos diferentes (0=não, 1=parcial, 2=sim)",
            "Discriminação de emoção: identifica expressão facial (alegria, tristeza, raiva, medo) (0=0-1, 1=2-3, 2=4 corretas)",
            "Reconhecimento de faces familiares: identifica rostos de figuras públicas conhecidas (0=0, 1=1-2, 2=3+)",
            "Matching de faces sob ruído: reconhece o mesmo rosto em condições de iluminação/ângulo alterados (0=não, 1=parcial, 2=sim)",
        ],
    },
    "FLUÊNCIA VERBAL": {
        "description": "Teste de Fluência Verbal — avaliação das funções executivas e linguagem através de fluência fonológica (FAS) e semântica (animais)",
        "max_score": 16.0,
        "severity": [(0, "Déficit grave"), (5, "Déficit moderado"), (9, "Déficit leve"), (13, "Normal")],
        "questions": [
            "Fluência fonológica - letra F: número de palavras iniciadas com F em 1 minuto (0=<5, 1=5-9, 2=10+)",
            "Fluência fonológica - letra A: número de palavras iniciadas com A em 1 minuto (0=<5, 1=5-9, 2=10+)",
            "Fluência fonológica - letra S: número de palavras iniciadas com S em 1 minuto (0=<5, 1=5-9, 2=10+)",
            "Fluência semântica - animais: número de animais nomeados em 1 minuto (0=<10, 1=10-15, 2=16+)",
            "Fluência semântica - frutas: número de frutas nomeadas em 1 minuto (0=<6, 1=6-10, 2=11+)",
            "Erros de perseveração: repetiu palavras já ditas durante o teste (0=3+, 1=1-2, 2=0)",
            "Erros de intrusão: palavras fora da categoria solicitada (0=3+, 1=1-2, 2=0)",
            "Estratégia de clusterização: agrupa palavras por subcategorias (0=ausente, 1=parcial, 2=presente)",
        ],
    },
    "TESTE DO RELÓGIO": {
        "description": "Teste do Desenho do Relógio — rastreio cognitivo para funções visuoespaciais, planejamento motor e memória semântica (pontuação de Shulman adaptada)",
        "max_score": 18.0,
        "severity": [(0, "Déficit grave"), (6, "Déficit moderado"), (10, "Déficit leve"), (14, "Normal")],
        "questions": [
            "Desenho do relógio (cópia): copia o desenho de um relógio com todos os números e ponteiros (0=ausente, 1=reconhecível, 2=bom, 3=perfeito)",
            "Desenho do relógio (comando): desenha um relógio marcando 11h10 de memória (0=ausente, 1=reconhecível, 2=bom, 3=perfeito)",
            "Disposição dos números: números distribuídos corretamente ao redor do círculo (0=não, 1=parcial, 2=sim, 3=preciso)",
            "Ponteiros: posição correta dos ponteiros de hora e minuto (0=não, 1=um correto, 2=ambos aproximados, 3=ambos precisos)",
            "Planejamento: organização espacial demonstra planejamento prévio (0=desorganizado, 1=regular, 2=bom, 3=excelente)",
            "Integridade do círculo: o contorno do relógio é preservado (0=não, 1=irregular, 2=bom, 3=perfeito)",
        ],
    },
    "TRILHAS": {
        "description": "Teste de Trilhas A e B (Trail Making Test) — avaliação da atenção sustentada, velocidade de processamento e flexibilidade cognitiva",
        "max_score": 18.0,
        "severity": [(0, "Déficit grave"), (6, "Déficit moderado"), (10, "Déficit leve"), (14, "Normal")],
        "questions": [
            "Trilhas A - tempo: segundos para conectar números 1-25 em ordem crescente (0=>120s, 1=60-120s, 2=30-59s, 3=<30s)",
            "Trilhas A - erros: quantidade de erros cometidos na parte A (0=5+, 1=3-4, 2=1-2, 3=0)",
            "Trilhas B - tempo: segundos para alternar entre números e letras (1-A-2-B...) (0=>180s, 1=120-180s, 2=60-119s, 3=<60s)",
            "Trilhas B - erros: quantidade de erros na parte B (0=5+, 1=3-4, 2=1-2, 3=0)",
            "Índice B-A: diferença de tempo entre parte B e parte A (0=>90s, 1=60-90s, 2=30-59s, 3=<30s)",
            "Perseveração: repetiu o mesmo tipo de estímulo sem alternar (0=4+, 1=2-3, 2=1, 3=0)",
        ],
    },
    "STROOP": {
        "description": "Teste de Stroop (Victoria Version) — avaliação do controle inibitório, atenção seletiva e velocidade de processamento",
        "max_score": 16.0,
        "severity": [(0, "Déficit grave"), (5, "Déficit moderado"), (9, "Déficit leve"), (13, "Normal")],
        "questions": [
            "Cartão 1 - pontos: tempo para nomear cores de pontos (0=>20s, 1=10-20s, 2=<10s)",
            "Cartão 1 - erros: erros na nomeação de cores dos pontos (0=3+, 1=1-2, 2=0)",
            "Cartão 2 - palavras neutras: tempo para nomear cores de palavras neutras (0=>25s, 1=12-25s, 2=<12s)",
            "Cartão 2 - erros: erros na nomeação de palavras neutras (0=3+, 1=1-2, 2=0)",
            "Cartão 3 - Stroop: tempo para nomear cor da tinta de palavras incongruentes (ex: VERDE escrito em vermelho) (0=>40s, 1=20-40s, 2=<20s)",
            "Cartão 3 - erros: erros na condição incongruente (interferência) (0=3+, 1=1-2, 2=0)",
            "Índice de interferência: aumento de tempo entre cartão 2 e cartão 3 (0=>20s, 1=10-20s, 2=<10s)",
            "Correções espontâneas: autocorrigiu erros sem intervenção (0=nenhuma, 1=algumas, 2=sim)",
        ],
    },
    "CANCELAMENTO": {
        "description": "Teste de Cancelamento — avaliação da atenção seletiva, sustentada e velocidade perceptomotora",
        "max_score": 12.0,
        "severity": [(0, "Déficit grave"), (3, "Déficit moderado"), (6, "Déficit leve"), (9, "Normal")],
        "questions": [
            "Cancelamento de símbolos: número de alvos cancelados em 60s (0=<30%, 1=30-70%, 2=>70%)",
            "Erros de omissão: alvos não identificados (0=10+, 1=4-9, 2=<4)",
            "Erros de comissão: não-alvos marcados como alvos (0=5+, 1=2-4, 2=<2)",
            "Tempo total: segundos para concluir o cancelamento (0=>180s, 1=90-180s, 2=<90s)",
            "Estratégia de busca: padrão organizado vs aleatório (0=aleatório, 1=parcialmente organizado, 2=sistemático)",
            "Fadigabilidade: desempenho piora na segunda metade do teste (0=queda >50%, 1=queda 20-50%, 2=queda <20%)",
        ],
    },
    "FIGURA COMPLEXA DE REY": {
        "description": "Figura Complexa de Rey-Osterrieth — avaliação da praxia construtiva, memória visuoespacial, planejamento e organização",
        "max_score": 24.0,
        "severity": [(0, "Déficit grave"), (8, "Déficit moderado"), (14, "Déficit leve"), (19, "Normal")],
        "questions": [
            "Cópia - precisão: fidelidade da reprodução dos elementos da figura (0=irreconhecível, 1=parcial, 2=bom, 3=excelente)",
            "Cópia - organização: sequência lógica de construção (0=desorganizado, 1=parcial, 2=organizado, 3=sistemático)",
            "Cópia - tempo: minutos para completar a cópia (0=>10min, 1=6-10min, 2=3-5min, 3=<3min)",
            "Memória imediata (3min): elementos recordados após 3 minutos (0=<3, 1=3-8, 2=9-14, 3=15+)",
            "Memória tardia (30min): elementos recordados após 30 minutos (0=<3, 1=3-8, 2=9-14, 3=15+)",
            "Reconhecimento: identifica elementos da figura entre distratores (0=<50%, 1=50-69%, 2=70-89%, 3=90%+)",
            "Escore de retenção: % preservado entre cópia e memória tardia (0=<30%, 1=30-49%, 2=50-69%, 3=70%+)",
            "Detalhes vs global: foco excessivo em detalhes sem integrar o todo (0=apenas detalhes, 1=detalhes > global, 2=equilíbrio, 3=integração perfeita)",
        ],
    },
    "HEXACO-60": {
        "description": "HEXACO-60 — Inventário HEXACO de Personalidade (Lee & Ashton, 2009), 60 itens medindo 6 dimensões da personalidade com escala Likert de 5 pontos.",
        "max_score": 300.0,
        "severity": [(0, "Baixo"), (120, "Médio"), (200, "Alto"), (250, "Muito alto")],
        "questions": [
            "Honestidade-Humildade - Sinto que sou uma pessoa comum e não melhor que os outros",
            "Honestidade-Humildade - Não me interessaria por pertences caros mesmo que pudesse pagar",
            "Honestidade-Humildade - Acho errado tirar vantagem de alguém mesmo que a oportunidade apareça",
            "Honestidade-Humildade - Nunca usaria bajulação para conseguir algo que quero",
            "Honestidade-Humildade - Sei que sou superior ao que as pessoas pensam (R)",
            "Honestidade-Humildade - Sou atraído(a) por riqueza e luxo (R)",
            "Honestidade-Humildade - Seria tentado(a) a falsificar documentos se não houvesse risco (R)",
            "Honestidade-Humildade - Gosto de exibir minhas posses e conquistas (R)",
            "Honestidade-Humildade - Acho que mereço tratamento especial (R)",
            "Honestidade-Humildade - Prefiro manter os pés no chão a sonhar com grande riqueza",
            "Emotionalidade - Fico ansioso(a) quando algo ameaçador acontece",
            "Emotionalidade - Preciso de apoio emocional em momentos difíceis",
            "Emotionalidade - Sinto meus sentimentos intensamente",
            "Emotionalidade - Choro facilmente ao ver filmes ou situações tristes",
            "Emotionalidade - Tenho medo de situações perigosas",
            "Emotionalidade - Mesmo pequenas críticas me afetam profundamente",
            "Emotionalidade - Sou capaz de lidar com emergências sem me desesperar (R)",
            "Emotionalidade - Fico tenso(a) quando percebo que alguém está irritado(a) comigo",
            "Emotionalidade - Preocupo-me com coisas que podem dar errado",
            "Emotionalidade - Sou emocionalmente estável e difícil de abalar (R)",
            "Extroversão - Gosto de conversar com pessoas que não conheço",
            "Extroversão - Sinto-me energizado(a) ao estar em grupos sociais",
            "Extroversão - Sou animado(a) e otimista na maioria das situações",
            "Extroversão - Prefiro trabalhar em equipe do que sozinho(a)",
            "Extroversão - Falo pouco quando conheço pessoas novas (R)",
            "Extroversão - Evito ser o centro das atenções (R)",
            "Extroversão - Sinto-me desconfortável em festas cheias de estranhos (R)",
            "Extroversão - Considero-me uma pessoa tímida e reservada (R)",
            "Extroversão - Tenho facilidade para iniciar conversas",
            "Extroversão - Prefiro passar tempo sozinho(a) a estar com muitas pessoas (R)",
            "Amabilidade - Trato todos com respeito independentemente de quem são",
            "Amabilidade - Nunca guardo rancor de quem me magoou",
            "Amabilidade - Sou tolerante com os erros e defeitos dos outros",
            "Amabilidade - Consigo ver o lado bom mesmo de pessoas difíceis",
            "Amabilidade - Costumo criticar os outros com facilidade (R)",
            "Amabilidade - Fico irritado(a) com pessoas que não concordam comigo (R)",
            "Amabilidade - Acredito que as pessoas geralmente têm boas intenções",
            "Amabilidade - Perdoo com facilidade quando alguém me pede desculpas",
            "Amabilidade - Sou teimoso(a) e mantenho minha posição (R)",
            "Amabilidade - Julgo as pessoas com severidade quando erram (R)",
            "Conscienciosidade - Planejo com antecedência para evitar imprevistos",
            "Conscienciosidade - Cumpro prazos e compromissos rigorosamente",
            "Conscienciosidade - Mantenho minhas coisas organizadas e no lugar certo",
            "Conscienciosidade - Trabalho de forma disciplinada mesmo sem supervisão",
            "Conscienciosidade - Tomo decisões com cuidado e ponderação",
            "Conscienciosidade - Deixo tarefas importantes para a última hora (R)",
            "Conscienciosidade - Sou desleixado(a) com minha aparência e ambiente (R)",
            "Conscienciosidade - Tenho dificuldade em seguir rotinas e horários (R)",
            "Conscienciosidade - Evito responsabilidades sempre que possível (R)",
            "Conscienciosidade - Ajo por impulso sem pensar nas consequências (R)",
            "Abertura à Experiência - Gosto de explorar ideias novas e diferentes",
            "Abertura à Experiência - Tenho interesse por arte, música e literatura",
            "Abertura à Experiência - Sinto curiosidade sobre como as coisas funcionam",
            "Abertura à Experiência - Gosto de viajar e conhecer culturas diferentes",
            "Abertura à Experiência - Prefiro a rotina e o previsível ao novo (R)",
            "Abertura à Experiência - Acho difícil me interessar por temas abstratos (R)",
            "Abertura à Experiência - Tenho imaginação fértil e criativa",
            "Abertura à Experiência - Gosto de discutir questões filosóficas e existenciais",
            "Abertura à Experiência - Prefiro atividades práticas a teóricas (R)",
            "Abertura à Experiência - Fico entediado(a) com conversas sobre ideias complexas (R)",
        ],
    },
    "BIS-11": {
        "description": "Barratt Impulsiveness Scale (Patton, Stanford & Barratt, 1995) — 30 itens para avaliação da impulsividade em 3 subescalas: Atenção, Motora, Não-planejamento. Validação brasileira: Malloy-Diniz et al., 2010.",
        "max_score": 120.0,
        "severity": [(0, "Baixa"), (30, "Moderada"), (45, "Elevada"), (60, "Muito elevada")],
        "questions": [
            "Atenção - Planejo tarefas com cuidado e antecedência (R)",
            "Atenção - Tomo decisões rapidamente e sem pensar muito",
            "Atenção - Distraio-me com facilidade durante conversas",
            "Atenção - Sou uma pessoa concentrada e focada (R)",
            "Atenção - Tenho pensamentos rápidos que se atropelam",
            "Atenção - Mudo de hobbies e interesses com frequência",
            "Atenção - Gasto mais do que ganho ou deveria",
            "Atenção - Fico entediado(a) facilmente com tarefas repetitivas",
            "Motor - Ajo por impulso sem planejar",
            "Motor - Faço coisas no calor do momento que depois lamento",
            "Motor - Compro coisas por impulso sem necessidade real",
            "Motor - Como mesmo quando não estou com fome",
            "Motor - Tenho relações sexuais sem proteção adequada",
            "Motor - Falo o que penso sem filtrar na hora errada",
            "Motor - Tenho dificuldade em controlar impulsos agressivos",
            "Motor - Começo novos projetos sem terminar os anteriores",
            "Motor - Mudo de emprego ou curso por decisões impulsivas",
            "Motor - Arrisco-me em atividades perigosas sem pensar nos riscos",
            "Motor - Sinto urgência em satisfazer desejos imediatamente",
            "Não-planejamento - Penso nas consequências antes de agir (R)",
            "Não-planejamento - Planejo meu orçamento e finanças com cuidado (R)",
            "Não-planejamento - Preparo-me com antecedência para compromissos (R)",
            "Não-planejamento - Considero todas as opções antes de decidir (R)",
            "Não-planejamento - Invisto tempo para tomar decisões importantes (R)",
            "Não-planejamento - Organizo meu tempo de forma eficiente (R)",
            "Não-planejamento - Mantenho uma rotina estável de atividades (R)",
            "Não-planejamento - Penso a longo prazo antes de fazer mudanças (R)",
            "Não-planejamento - Uso listas e lembretes para não esquecer tarefas (R)",
            "Não-planejamento - Avalio prós e contras antes de agir (R)",
            "Não-planejamento - Estabeleço metas e planejo etapas para alcançá-las (R)",
        ],
    },
    "TAS-20": {
        "description": "Toronto Alexithymia Scale (Bagby, Parker & Taylor, 1994) — 20 itens para avaliação da alexitimia: Dificuldade em Identificar Sentimentos (DIF), Dificuldade em Descrever Sentimentos (DDF), Pensamento Externamente Orientado (EOT). Versão brasileira validada.",
        "max_score": 100.0,
        "severity": [(0, "Ausente"), (30, "Moderada"), (40, "Elevada"), (50, "Muito elevada")],
        "questions": [
            "DIF - Frequentemente não sei exatamente qual emoção estou sentindo",
            "DIF - Tenho dificuldade em encontrar palavras para expressar meus sentimentos",
            "DIF - Sinto sensações físicas estranhas que nem os médicos entendem",
            "DIF - Consigo descrever meus sentimentos com facilidade (R)",
            "DIF - Prefiro deixar os problemas se resolverem sozinhos a analisar minhas emoções",
            "DIF - Quando estou chateado(a), não sei se estou triste, com medo ou com raiva",
            "DIF - Frequentemente fico confuso(a) sobre o que estou sentindo em meu corpo",
            "DDF - Acho difícil dizer aos outros como me sinto por dentro",
            "DDF - As pessoas me dizem que falo pouco sobre meus sentimentos",
            "DDF - Tenho palavras suficientes para descrever minhas emoções (R)",
            "DDF - Consigo falar facilmente sobre meus sentimentos íntimos (R)",
            "DDF - Prefiro falar sobre atividades cotidianas do que sobre emoções",
            "EOT - As pessoas me pedem que fale mais sobre meus sentimentos",
            "EOT - Olhar para o céu ou contemplar a natureza me traz paz interior (R)",
            "EOT - Acho que é perda de tempo tentar entender o que sinto",
            "EOT - Sonhar acordado(a) é perda de tempo (R)",
            "EOT - Prefiro conversas sobre fatos do dia a dia a conversas sobre sentimentos",
            "EOT - Mesmo quando estou angustiado(a), raramente analiso o que estou sentindo",
            "EOT - Buscar significados ocultos nas emoções é uma perda de tempo",
            "EOT - Ter pensamentos íntimos sobre os sentimentos é desnecessário",
        ],
    },
    "RSES": {
        "description": "Rosenberg Self-Esteem Scale (Rosenberg, 1965) — 10 itens para avaliação global da autoestima. Validação brasileira: Hutz & Zanon, 2011. Escala unifatorial com 5 itens positivos e 5 reversos.",
        "max_score": 40.0,
        "severity": [(0, "Muito baixa"), (15, "Baixa"), (25, "Média"), (35, "Elevada")],
        "questions": [
            "Autoestima - Sinto que sou uma pessoa de valor, pelo menos num plano igual aos outros",
            "Autoestima - Sinto que tenho várias boas qualidades",
            "Autoestima - No geral, tenho tendência a me sentir um fracasso (R)",
            "Autoestima - Sou capaz de fazer as coisas tão bem quanto a maioria das pessoas",
            "Autoestima - Sinto que não tenho muito do que me orgulhar (R)",
            "Autoestima - Tenho uma atitude positiva em relação a mim mesmo(a)",
            "Autoestima - No conjunto, estou satisfeito(a) comigo mesmo(a)",
            "Autoestima - Gostaria de ter mais respeito por mim mesmo(a) (R)",
            "Autoestima - Às vezes me sinto realmente inútil (R)",
            "Autoestima - Às vezes acho que não sou bom(a) em nada (R)",
        ],
    },
}


def create_date_key(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day


def get_severity(score: float, thresholds: list) -> str:
    for threshold, label in reversed(thresholds):
        if score >= threshold:
            return label
    return thresholds[0][1]


def _generate_scale_responses(session, consultation, disorders, scale_map, symptom_map, disorder_map=None):
    """Generate scale responses and inferences for a single consultation."""
    MAX_Q_SCORE = {
        "PHQ-9": 3, "GAD-7": 3, "MADRS": 6, "MDQ": 1,
        "PCL-5": 4, "Y-BOCS": 4, "AUDIT": 4, "ASRM": 4, "ASRS": 4, "AQ-10": 1,
        "BFP": 4, "DT-12 (Tríade Sombria)": 6,
        "HEXACO-60": 5, "BIS-11": 4, "TAS-20": 5, "RSES": 4,
        "MEMÓRIA": 2, "QI - RASTREIO": 3,
        "RECONHECIMENTO DE ROSTOS": 2, "FLUÊNCIA VERBAL": 2,
        "TESTE DO RELÓGIO": 3, "TRILHAS": 3, "STROOP": 2,
        "CANCELAMENTO": 2, "FIGURA COMPLEXA DE REY": 3,
    }
    SCALE_DISORDER_MAP = {
        "PHQ-9": ["Depressiv", "Disfórico", "Adaptação", "Luto", "Alimentar", "Sono", "Pica", "Ruminação", "Transtorno Mental"],
        "GAD-7": ["Ansiedade", "Pânico", "Agorafobia", "Fobia", "Catatonia", "Sexual", "Sono", "Eliminação", "Transtorno Mental", "Disfunção Sexual", "Apneia", "Hipersonolência", "Narcolepsia", "Pesadelo", "Sonambulismo", "Neurodesenvolvimento", "Disruptivo", "Fatores Psicológicos", "Terror Noturno", "Pernas Inquietas", "Ejaculação", "Erétil", "Orgasmo Feminino", "Gênito-Pélvica", "Penetração"],
        "MADRS": ["Depressiv", "Disfórico"],
        "MDQ": ["Bipolar", "Ciclotímico"],
        "PCL-5": ["Estresse Pós-Traumático", "Estresse Agudo", "Luto", "Adaptação", "Dissociativo", "Apego", "Amnésia Dissociativa", "Despersonalização", "Dissociativo de Identidade", "Transtorno Relacionado a Trauma"],
        "Y-BOCS": ["Obsessivo-Compulsivo", "TOC", "Dismórfico", "Acumulação", "Tricotilomania", "Escoriação", "Ansiedade de Doença", "Eliminação", "Enurese", "Encoprese", "Pica", "Ruminação", "Tourette", "Tique"],
        "AUDIT": ["Substâncias", "Álcool", "Jogo", "Tabaco"],
        "ASRM": ["Bipolar", "Ciclotímico"],
        "ASRS": ["Déficit de Atenção/Hiperatividade", "TDAH", "Aprendizagem", "Coordenação"],
        "AQ-10": ["Espectro Autista", "Autista", "Comunicação Social", "Comunicação Não Especificado", "Linguagem", "Fonológico", "Fluência com Início na Infância", "Gagueira", "Atraso Global do Desenvolvimento", "Coordenação", "Movimento Estereotipado"],
        "BFP": ["Depressiv", "Sintomas Somáticos", "Personalidade", "Ansiedade", "Insônia", "Factício", "Disforia de Gênero", "Catatonia", "Transtorno do Desenvolvimento", "Transtorno da Comunicação", "Transtorno de Tique", "Transtorno do Movimento"],
        "DT-12 (Tríade Sombria)": ["Substâncias", "Obsessivo-Compulsivo", "Personalidade", "Conduta", "Opositivo", "Explosivo", "Voyeurista", "Exhibitionista", "Frotteurista", "Pedofílico", "Sadismo", "Masoquismo", "Fetichista", "Transvéstico", "Parafílico"],
        "INSÔNIA": ["Insônia", "Sono"],
        "MEMÓRIA": ["Neurocognitivo", "Delirium", "Depressiv", "Esquizofrenif", "Psicótico", "Dissociativo", "Transtorno Dissociativo"],
        "QI-RASTREIO": ["Deficiência Intelectual", "Neurocognitivo", "Atraso Global", "Aprendizagem"],
        "FLUÊNCIA VERBAL": ["Déficit de Atenção/Hiperatividade", "Depressiv", "Esquizofrenia", "Delirante", "Esquizoafetivo", "Psicótico", "Esquizofreniforme"],
        "TESTE DO RELÓGIO": ["Esquizofrenia", "Depressiv", "Neurocognitivo", "Delirante", "Esquizofreniforme", "Psicótico"],
        "TRILHAS": ["Déficit de Atenção/Hiperatividade", "Ansiedade", "Depressiv", "Neurocognitivo", "Obsessivo-Compulsivo", "Psicótico", "Tique", "Tourette"],
        "STROOP": ["Déficit de Atenção/Hiperatividade", "Obsessivo-Compulsivo", "Ansiedade", "Neurocognitivo", "Esquizofrenia", "Psicótico", "Tique", "Tourette"],
        "CANCELAMENTO": ["Déficit de Atenção/Hiperatividade", "Ansiedade", "Neurocognitivo", "Esquizofrenia", "Psicótico", "Tique"],
        "RECONHECIMENTO DE ROSTOS": ["Espectro Autista", "Esquizofrenia", "Neurocognitivo", "Delirante", "Psicótico"],
        "FIGURA COMPLEXA DE REY": ["Estresse Pós-Traumático", "Depressiv", "Neurocognitivo", "Esquizofrenia", "Psicótico", "Dissociativo"],
        "HEXACO-60": ["Personalidade", "Ansiedade", "Depressiv", "Bipolar", "Obsessivo", "Alimentar"],
        "BIS-11": ["TDAH", "Bipolar", "Borderline", "Antissocial", "Substâncias", "Explosivo"],
        "TAS-20": ["Autista", "Somático", "Depressiv", "Pós-Traumático", "Ansiedade", "Dissociativo"],
        "RSES": ["Depressiv", "Ansiedade Social", "Esquiva", "Anorexia", "Personalidade Dependente"],
    }
    # BFP factor indices (5 questions per factor, 25 total)
    BFP_FACTOR_RANGES = {
        "Abertura": (0, 5), "Conscienciosidade": (5, 10),
        "Extroversão": (10, 15), "Amabilidade": (15, 20),
        "Neuroticismo": (20, 25),
    }
    # DT-12 subscale indices (4 questions per subscale, 12 total)
    DT12_SUBSCALE_RANGES = {
        "Maquiavelismo": (0, 4), "Narcisismo": (4, 8), "Psicopatia": (8, 12),
    }
    # HEXACO-60 factor indices (10 questions per factor, 60 total, mixed polarity)
    HEXACO_FACTOR_RANGES = {
        "Honestidade-Humildade": (0, 10),
        "Emotionalidade": (10, 20),
        "Extroversão": (20, 30),
        "Amabilidade": (30, 40),
        "Conscienciosidade": (40, 50),
        "Abertura à Experiência": (50, 60),
    }
    # BIS-11 subscale indices (Atenção=8, Motor=11, Não-planejamento=11, 30 total)
    BIS11_SUBSCALE_RANGES = {
        "Atenção": (0, 8),
        "Motor": (8, 19),
        "Não-planejamento": (19, 30),
    }
    # TAS-20 subscale indices (DIF=7, DDF=5, EOT=8, 20 total)
    TAS20_SUBSCALE_RANGES = {
        "DIF": (0, 7),
        "DDF": (7, 12),
        "EOT": (12, 20),
    }
    # RSES is unidimensional (10 questions)
    RSES_QUESTION_RANGE = (0, 10)

    def _bfp_factor_scores(disorder_list, max_q=4):
        """Generate realistic per-factor BFP scores based on patient disorders."""
        # Default moderate profile: all factors ~2.5/4 per question = ~12.5/20 per factor
        factors = {
            "Neuroticismo": random.uniform(1.5, 2.5),
            "Abertura": random.uniform(1.5, 2.5),
            "Conscienciosidade": random.uniform(1.5, 2.5),
            "Extroversão": random.uniform(1.5, 2.5),
            "Amabilidade": random.uniform(1.5, 2.5),
        }
        for d in disorder_list:
            dl = d.lower()
            if any(k in dl for k in ["depressiv", "distimia", "ansiedade", "estresse", "insônia", "somático"]):
                factors["Neuroticismo"] = random.uniform(3.0, 4.0)
                factors["Extroversão"] = random.uniform(0.5, 1.5)
            if any(k in dl for k in ["bipolar", "mania"]):
                factors["Abertura"] = random.uniform(3.0, 4.0)
                factors["Extroversão"] = random.uniform(3.0, 4.0)
            if any(k in dl for k in ["déficit de atenção", "tdah", "hiperatividade"]):
                factors["Conscienciosidade"] = random.uniform(0.5, 1.5)
            if any(k in dl for k in ["substâncias", "álcool", "uso de"]):
                factors["Amabilidade"] = random.uniform(0.5, 1.5)
                factors["Conscienciosidade"] = random.uniform(0.5, 1.5)
            if any(k in dl for k in ["obsessivo", "toc", "ansiedade social", "fobia"]):
                factors["Neuroticismo"] = max(factors["Neuroticismo"], random.uniform(2.5, 3.5))
            if any(k in dl for k in ["autista", "tea", "espectro autista"]):
                factors["Extroversão"] = random.uniform(0.5, 1.5)
                factors["Abertura"] = random.uniform(1.0, 2.0)
            if any(k in dl for k in ["anorexia", "bulimia", "compulsão"]):
                factors["Neuroticismo"] = max(factors["Neuroticismo"], random.uniform(2.5, 3.5))
                factors["Conscienciosidade"] = random.uniform(2.0, 3.5)
        return {k: min(max_q, max(0, v)) for k, v in factors.items()}

    def _dt12_subscale_scores(disorder_list, max_q=6):
        """Generate realistic per-subscale DT-12 scores based on patient disorders."""
        subscales = {
            "Maquiavelismo": random.uniform(0.5, 1.5),
            "Narcisismo": random.uniform(0.5, 1.5),
            "Psicopatia": random.uniform(0.5, 1.5),
        }
        for d in disorder_list:
            dl = d.lower()
            if any(k in dl for k in ["substâncias", "álcool", "uso de"]):
                subscales["Maquiavelismo"] = random.uniform(2.0, 4.0)
                subscales["Psicopatia"] = random.uniform(2.0, 4.0)
            if any(k in dl for k in ["bipolar", "mania"]):
                subscales["Narcisismo"] = random.uniform(2.0, 4.0)
            if any(k in dl for k in ["obsessivo", "toc"]):
                subscales["Maquiavelismo"] = random.uniform(1.5, 3.0)
            if any(k in dl for k in ["depressiv", "distimia"]):
                subscales["Narcisismo"] = max(0.5, subscales["Narcisismo"] - 0.5)
        return {k: min(max_q, max(0, v)) for k, v in subscales.items()}

    def _hexaco_factor_scores(disorder_list, max_q=5):
        """Generate realistic per-factor HEXACO-60 scores based on patient disorders."""
        factors = {
            "Honestidade-Humildade": random.uniform(2.0, 4.0),
            "Emotionalidade": random.uniform(2.0, 4.0),
            "Extroversão": random.uniform(2.0, 4.0),
            "Amabilidade": random.uniform(2.0, 4.0),
            "Conscienciosidade": random.uniform(2.0, 4.0),
            "Abertura à Experiência": random.uniform(2.0, 4.0),
        }
        for d in disorder_list:
            dl = d.lower()
            if any(k in dl for k in ["depressiv", "distimia", "ansiedade", "estresse", "insônia"]):
                factors["Emotionalidade"] = random.uniform(3.5, 5.0)
                factors["Extroversão"] = random.uniform(0.5, 2.0)
            if any(k in dl for k in ["bipolar", "mania"]):
                factors["Extroversão"] = random.uniform(3.5, 5.0)
                factors["Abertura à Experiência"] = random.uniform(3.5, 5.0)
            if any(k in dl for k in ["personalidade antissocial", "personalidade narcisista", "personalidade histriônica"]):
                factors["Honestidade-Humildade"] = random.uniform(0.5, 2.0)
            if any(k in dl for k in ["obsessivo", "toc"]):
                factors["Conscienciosidade"] = random.uniform(3.5, 5.0)
            if any(k in dl for k in ["autista", "tea"]):
                factors["Extroversão"] = random.uniform(0.5, 2.0)
                factors["Amabilidade"] = random.uniform(1.0, 3.0)
            if any(k in dl for k in ["anorexia", "bulimia"]):
                factors["Emotionalidade"] = max(factors["Emotionalidade"], random.uniform(3.5, 5.0))
                factors["Conscienciosidade"] = random.uniform(3.0, 5.0)
            if any(k in dl for k in ["personalidade paranoide", "personalidade borderline"]):
                factors["Amabilidade"] = random.uniform(0.5, 2.0)
                factors["Honestidade-Humildade"] = random.uniform(0.5, 2.0)
        return {k: min(max_q, max(0, v)) for k, v in factors.items()}

    def _bis11_subscale_scores(disorder_list, max_q=4):
        """Generate realistic per-subscale BIS-11 scores based on patient disorders."""
        subscales = {
            "Atenção": random.uniform(1.0, 2.0),
            "Motor": random.uniform(0.5, 1.5),
            "Não-planejamento": random.uniform(1.0, 2.0),
        }
        for d in disorder_list:
            dl = d.lower()
            if any(k in dl for k in ["déficit de atenção", "tdah", "hiperatividade"]):
                subscales["Atenção"] = random.uniform(3.0, 4.0)
                subscales["Motor"] = random.uniform(2.5, 4.0)
            if any(k in dl for k in ["bipolar", "mania"]):
                subscales["Motor"] = random.uniform(3.0, 4.0)
                subscales["Não-planejamento"] = random.uniform(2.5, 4.0)
            if any(k in dl for k in ["personalidade borderline"]):
                subscales["Motor"] = random.uniform(3.0, 4.0)
                subscales["Não-planejamento"] = random.uniform(2.5, 4.0)
            if any(k in dl for k in ["substâncias", "álcool"]):
                subscales["Motor"] = random.uniform(3.0, 4.0)
                subscales["Não-planejamento"] = random.uniform(2.5, 4.0)
            if any(k in dl for k in ["personalidade antissocial", "explosivo"]):
                subscales["Motor"] = random.uniform(3.5, 4.0)
            if any(k in dl for k in ["depressiv", "distimia"]):
                subscales["Atenção"] = max(subscales["Atenção"], random.uniform(2.0, 3.5))
        return {k: min(max_q, max(0, v)) for k, v in subscales.items()}

    def _tas20_subscale_scores(disorder_list, max_q=5):
        """Generate realistic per-subscale TAS-20 scores based on patient disorders."""
        subscales = {
            "DIF": random.uniform(1.0, 2.5),
            "DDF": random.uniform(1.0, 2.5),
            "EOT": random.uniform(1.0, 2.5),
        }
        for d in disorder_list:
            dl = d.lower()
            if any(k in dl for k in ["autista", "tea", "espectro autista"]):
                subscales["DIF"] = random.uniform(3.0, 5.0)
                subscales["DDF"] = random.uniform(3.0, 5.0)
                subscales["EOT"] = random.uniform(3.0, 5.0)
            if any(k in dl for k in ["somático", "conversão", "dissociativo"]):
                subscales["DIF"] = random.uniform(3.5, 5.0)
                subscales["DDF"] = random.uniform(2.5, 4.0)
            if any(k in dl for k in ["depressiv", "distimia"]):
                subscales["DIF"] = max(subscales["DIF"], random.uniform(2.5, 4.0))
            if any(k in dl for k in ["pós-traumático", "estresse agudo"]):
                subscales["DIF"] = max(subscales["DIF"], random.uniform(3.0, 5.0))
                subscales["EOT"] = max(subscales["EOT"], random.uniform(2.5, 4.0))
            if any(k in dl for k in ["anorexia", "bulimia"]):
                subscales["DIF"] = max(subscales["DIF"], random.uniform(2.5, 4.0))
                subscales["DDF"] = max(subscales["DDF"], random.uniform(2.5, 4.0))
        return {k: min(max_q, max(0, v)) for k, v in subscales.items()}

    def _rses_dimension_score(disorder_list, max_q=4):
        """Generate realistic RSES (self-esteem) score based on patient disorders."""
        base = random.uniform(1.5, 3.0)
        for d in disorder_list:
            dl = d.lower()
            if any(k in dl for k in ["depressiv", "distimia"]):
                base = random.uniform(0.5, 1.5)
            if any(k in dl for k in ["ansiedade social", "fobia social", "esquiva"]):
                base = min(base, random.uniform(0.5, 1.5))
            if any(k in dl for k in ["anorexia"]):
                base = min(base, random.uniform(0.5, 1.5))
            if any(k in dl for k in ["personalidade dependente"]):
                base = min(base, random.uniform(0.5, 2.0))
        return min(max_q, max(0, base))

    for sname, sinfo in scale_map.items():
        scale_def = sinfo["def"]
        max_q_score = MAX_Q_SCORE.get(sname, 3)
        matched = [d for d in disorders if any(k in d for k in SCALE_DISORDER_MAP.get(sname, []))]

        # Per-factor generation for BFP and DT-12
        if sname == "BFP":
            bfp_factors = _bfp_factor_scores(disorders)
            for q in sinfo["questions"]:
                q_idx = q.question_order - 1
                factor = next((f for f, (s, e) in BFP_FACTOR_RANGES.items() if s <= q_idx < e), None)
                mean_score = bfp_factors.get(factor, max_q_score / 2)
                score = min(max_q_score, max(0, int(mean_score + random.gauss(0, 0.6))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))
            session.flush()
            sname_continue = True
        elif sname == "DT-12 (Tríade Sombria)":
            dt12_sub = _dt12_subscale_scores(disorders)
            for q in sinfo["questions"]:
                q_idx = q.question_order - 1
                sub = next((s for s, (st, en) in DT12_SUBSCALE_RANGES.items() if st <= q_idx < en), None)
                mean_score = dt12_sub.get(sub, max_q_score / 2)
                score = min(max_q_score, max(0, int(mean_score + random.gauss(0, 0.8))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))
            session.flush()
            continue
        elif sname == "HEXACO-60":
            hexaco_factors = _hexaco_factor_scores(disorders)
            for q in sinfo["questions"]:
                q_idx = q.question_order - 1
                factor = next((f for f, (s, e) in HEXACO_FACTOR_RANGES.items() if s <= q_idx < e), None)
                mean_score = hexaco_factors.get(factor, max_q_score / 2)
                score = min(max_q_score, max(0, int(mean_score + random.gauss(0, 0.7))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))
            session.flush()
            continue
        elif sname == "BIS-11":
            bis11_sub = _bis11_subscale_scores(disorders)
            for q in sinfo["questions"]:
                q_idx = q.question_order - 1
                sub = next((s for s, (st, en) in BIS11_SUBSCALE_RANGES.items() if st <= q_idx < en), None)
                mean_score = bis11_sub.get(sub, max_q_score / 2)
                score = min(max_q_score, max(0, int(mean_score + random.gauss(0, 0.6))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))
            session.flush()
            continue
        elif sname == "TAS-20":
            tas20_sub = _tas20_subscale_scores(disorders)
            for q in sinfo["questions"]:
                q_idx = q.question_order - 1
                sub = next((s for s, (st, en) in TAS20_SUBSCALE_RANGES.items() if st <= q_idx < en), None)
                mean_score = tas20_sub.get(sub, max_q_score / 2)
                score = min(max_q_score, max(0, int(mean_score + random.gauss(0, 0.6))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))
            session.flush()
            continue
        elif sname == "RSES":
            rses_mean = _rses_dimension_score(disorders)
            for q in sinfo["questions"]:
                score = min(max_q_score, max(0, int(rses_mean + random.gauss(0, 0.6))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))
            session.flush()
            continue
        else:
            if matched:
                base_severity = random.randint(
                    int(len(scale_def["questions"]) * max_q_score * 0.4),
                    int(len(scale_def["questions"]) * max_q_score * 0.8),
                )
            else:
                base_severity = random.randint(0, int(len(scale_def["questions"]) * max_q_score * 0.25))
            num_q = len(sinfo["questions"])
            for q in sinfo["questions"]:
                score = min(max_q_score, max(0, int(base_severity / num_q + random.gauss(0, 0.5))))
                session.add(ScaleResponse(
                    consultation_uuid=consultation.consultation_uuid,
                    question_id=q.question_id,
                    response_value=score,
                    response_text=str(score),
                ))

    # Run inference
    from app.ml.inference.bayesian_network import BayesianNetwork, InferenceEvidence
    from app.ml.models.network_definition import build_mood_disorder_network
    try:
        bn = build_mood_disorder_network()
        evidence = []
        for dd in DISORDER_DEFS:
            for sname, *_ in dd["symptoms"]:
                has_symptom = session.query(SymptomObservation).filter(
                    SymptomObservation.consultation_uuid == consultation.consultation_uuid,
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
                dis_id = disorder_map.get(pt_name) if disorder_map else None
                if dis_id:
                    inf = DiagnosticInference(
                        consultation_uuid=consultation.consultation_uuid,
                        disorder_id=dis_id,
                        inference_probability=result.posterior_probability,
                        confidence_level=result.confidence_interval_upper,
                        generated_by_model="bayesian-network",
                        model_version="bayesian-net-v2",
                    )
                    session.add(inf)
    except Exception as e:
        print(f"  [WARN] Inference failed for consultation: {e}")


def _seed_reports(session, patient_data, consultation_records, profs):
    """Seed example medical reports for a subset of patients."""
    report_templates = [
        {
            "title": "Resumo Clínico — Evolução do Tratamento",
            "content": (
                "Paciente em acompanhamento regular com frequência {freq}. "
                "Apresentou melhora parcial dos sintomas desde o início do tratamento. "
                "Na última consulta, a pontuação no {scale} foi de {score} pontos, "
                "indicando {severity}. Mantém adesão à psicoterapia e uso regular da medicação prescrita. "
                "Observa-se progresso na redução dos episódios de {symptom1}, embora {symptom2} "
                "ainda ocorra com frequência semanal. Plano terapêutico: continuar com a abordagem atual "
                "e reavaliar em 30 dias."
            ),
            "type": "resumo_clinico",
        },
        {
            "title": "Avaliação Diagnóstica",
            "content": (
                "Avaliação realizada em {date} com base em entrevista clínica estruturada, "
                "aplicação de escalas padronizadas e revisão de prontuário. "
                "Os achados são consistentes com o diagnóstico de {disorder}. "
                "A escala {scale} apresentou escore {score} ({severity}), corroborando o quadro. "
                "Fatores estressores identificados: {stressors}. "
                "Avaliação funcional sugere comprometimento leve a moderado nas atividades laborais e sociais. "
                "Recomenda-se manutenção do tratamento farmacológico e psicoterápico, "
                "com monitoramento mensal da evolução dos sintomas."
            ),
            "type": "avaliacao",
        },
        {
            "title": "Encaminhamento — Avaliação Neuropsicológica",
            "content": (
                "Solicito avaliação neuropsicológica para paciente com queixas de {symptom1} e {symptom2}. "
                "Apresentou desempenho abaixo do esperado no teste de {neuro_test} "
                "(pontuação: {score}). Refere dificuldades persistentes em {difficulty}. "
                "Hipótese diagnóstica atual: {disorder}. "
                "Encaminho para avaliação complementar com neuropsicologia para melhor "
                "elucidação do perfil cognitivo e planejamento terapêutico."
            ),
            "type": "encaminhamento",
        },
    ]

    n_patients = len(patient_data)
    if n_patients == 0:
        return

    count = 0
    for i, pd_item in enumerate(patient_data):
        if i % 3 != 0:  # ~1/3 of patients get reports
            continue

        patient_uuid = pd_item["patient_uuid"]
        patient_consults = [c for c in consultation_records if c.profile_uuid == pd_item.get("profile_uuid")]
        # If consultation_records don't have profile_uuid matching, try direct query
        if not patient_consults:
            for c in consultation_records:
                pp = session.query(PatientProfile).filter_by(patient_uuid=patient_uuid).first()
                if pp and c.profile_uuid == pp.profile_uuid:
                    patient_consults.append(c)

        prof = random.choice(profs) if profs else None

        # Pick some disorder for this patient
        disorder_names = [dd["name"] for dd in DISORDER_DEFS]
        primary_disorder = random.choice(disorder_names)

        for template in report_templates:
            fill = {
                "freq": random.choice(["semanal", "quinzenal", "mensal"]),
                "scale": random.choice(["PHQ-9", "GAD-7", "BFP", "DT-12 (Tríade Sombria)"]),
                "score": str(random.randint(8, 27)),
                "severity": random.choice(["leve", "moderado", "moderadamente grave"]),
                "symptom1": random.choice(["humor deprimido", "ansiedade", "insônia", "irritabilidade"]),
                "symptom2": random.choice(["fadiga", "pensamentos ruminativos", "isolamento social", "dificuldade de concentração"]),
                "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%d/%m/%Y"),
                "disorder": primary_disorder,
                "stressors": random.choice([
                    "dificuldades financeiras e conflitos familiares",
                    "sobrecarga de trabalho e estresse laboral",
                    "problemas de relacionamento e luto recente",
                    "isolamento social e baixo suporte familiar"
                ]),
                "neuro_test": random.choice(["MEMÓRIA", "TRILHAS", "STROOP", "FLUÊNCIA VERBAL"]),
                "difficulty": random.choice([
                    "planejamento e organização",
                    "atenção sustentada e memória operacional",
                    "controle inibitório e flexibilidade cognitiva",
                    "fluência verbal e nomeação",
                ]),
            }

            try:
                content = template["content"].format(**fill)
            except KeyError:
                content = template["content"]

            existing = session.query(MedicalReport).filter_by(
                patient_uuid=patient_uuid,
                title=template["title"],
            ).first()
            if not existing:
                report = MedicalReport(
                    patient_uuid=patient_uuid,
                    title=template["title"],
                    content=content,
                    report_type=template["type"],
                    is_pinned=(i % 2 == 0),
                    created_by=prof.full_name if prof else "Sistema",
                )
                session.add(report)
                count += 1

    if count > 0:
        print(f"OK - {count} reports gerados para exemplos clinicos")


def seed():
    engine = create_engine(settings.database_url, echo=False)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    # Always clean dynamic data first
    session.execute(text("DELETE FROM diagnostic.diagnostic_inference CASCADE"))
    session.execute(text("DELETE FROM clinical.scale_responses CASCADE"))
    session.commit()

    existing_patients = session.query(PatientProfile).count()
    if existing_patients > 0:
        print(f"[RE-SEED] {existing_patients} patients found. Regenerating scale responses and inferences...")

        # Load existing data
        sex_types = session.query(SexType).all()
        genders = session.query(GenderIdentity).all()
        edu_levels = session.query(EducationLevel).all()
        ethnicities = session.query(Ethnicity).all()

        symptom_map = {}
        for dd in DISORDER_DEFS:
            for sname, sdesc, *_ in dd["symptoms"]:
                if sname in symptom_map:
                    continue
                pt_name = EN_TO_PT_SYMPTOM.get(sname, sname)
                existing = session.query(Symptom).filter_by(symptom_name=pt_name).first()
                if existing:
                    symptom_map[sname] = existing.symptom_id

        disorder_map = {}
        for dd in DISORDER_DEFS:
            existing = session.query(Disorder).filter_by(disorder_name=dd["name"]).first()
            if existing:
                disorder_map[dd["name"]] = existing.disorder_id

        scale_map = {}
        for sname, sdef in SCALE_DEFS.items():
            existing_scale = session.query(AssessmentScale).filter_by(scale_name=sname).first()
            if existing_scale:
                questions = session.query(ScaleQuestion).filter_by(scale_id=existing_scale.scale_id).order_by(ScaleQuestion.question_order).all()
                scale_map[sname] = {"scale": existing_scale, "questions": questions, "def": sdef}

        # Ensure professionals exist with user_uuid (in case of first re-seed after full seed was never run)
        prof_defs = [
            ("Dr. Ricardo Almeida", "CRM 12345-SP", "Psiquiatria", "Psiquiatria Clínica", "clinician"),
            ("Dra. Mariana Costa", "CRM 23456-SP", "Psiquiatria", "Psiquiatria da Infância", "psychiatrist"),
            ("Dr. Fernando Oliveira", "CRP 34567-SP", "Psicologia", "Psicologia Clínica", "psychologist"),
            ("Dra. Patrícia Santos", "CRP 45678-SP", "Psicologia", "Neuropsicologia", "researcher"),
            ("Dr. Eduardo Martins", "CRM 56789-SP", "Psiquiatria", "Psiquiatria Geral", "clinical_supervisor"),
        ]
        professionals_exist = session.query(HealthcareProfessional).first()
        if not professionals_exist:
            for name, license_no, profession, specialty, username in prof_defs:
                user = session.query(User).filter_by(username=username).first()
                p = HealthcareProfessional(
                    full_name=name, professional_license=license_no,
                    profession=profession, specialty=specialty,
                    start_date=date(2018, 1, 1),
                    user_uuid=user.user_uuid if user else None,
                )
                session.add(p)
            session.flush()
            print("OK - 5 profissionais criados no re-seed")
        else:
            # Link existing professionals to users if not yet linked
            for name, license_no, _, _, username in prof_defs:
                prof = session.query(HealthcareProfessional).filter_by(professional_license=license_no).first()
                if prof and prof.user_uuid is None:
                    user = session.query(User).filter_by(username=username).first()
                    if user:
                        prof.user_uuid = user.user_uuid
            session.flush()
            print("OK - Profissionais vinculados a usuarios no re-seed")

        # Ensure ProfessionalPatientAssignment records exist
        existing_assignments = session.query(ProfessionalPatientAssignment).first()
        if not existing_assignments:
            all_profs = session.query(HealthcareProfessional).all()
            all_patients = session.query(PatientIdentity).all()
            for i, pi in enumerate(all_patients):
                primary = all_profs[i % len(all_profs)]
                session.add(ProfessionalPatientAssignment(
                    professional_uuid=primary.professional_uuid,
                    patient_uuid=pi.patient_uuid, is_active=True,
                ))
                if random.random() < 0.20:
                    secondary = random.choice([p for p in all_profs if p.professional_uuid != primary.professional_uuid])
                    session.add(ProfessionalPatientAssignment(
                        professional_uuid=secondary.professional_uuid,
                        patient_uuid=pi.patient_uuid, is_active=True,
                    ))
            session.flush()
            print(f"OK - {len(all_patients)} pacientes distribuidos entre {len(all_profs)} profissionais no re-seed")

        consultation_records = session.query(ClinicalConsultation).all()
        patient_data = []
        for pp in session.query(PatientProfile).all():
            identity = session.query(PatientIdentity).filter_by(patient_uuid=pp.patient_uuid).first()
            patient_data.append({
                "patient_uuid": pp.patient_uuid,
                "profile_uuid": pp.profile_uuid,
            })

        patient_disorders = {}
        for pd_item in patient_data:
            disorder_names = [dd["name"] for dd in DISORDER_DEFS]
            primary = random.choice(disorder_names)
            assigned = [primary]
            others = [d for d in disorder_names if d != primary]
            if random.random() < 0.40:
                secondary = random.choice(others)
                assigned.append(secondary)
                others.remove(secondary)
            if random.random() < 0.15:
                tertiary = random.choice(others)
                assigned.append(tertiary)
            patient_disorders[pd_item["patient_uuid"]] = assigned

        for consult in consultation_records:
            prof = session.query(HealthcareProfessional).filter_by(professional_uuid=consult.professional_uuid).first()
            pp = session.query(PatientProfile).filter_by(profile_uuid=consult.profile_uuid).first()
            disorders = patient_disorders.get(pp.patient_uuid, [])
            _generate_scale_responses(session, consult, disorders, scale_map, symptom_map, disorder_map)

        all_profs = session.query(HealthcareProfessional).all()
        _seed_reports(session, patient_data, consultation_records, all_profs)
        session.commit()
        re_profs = session.query(HealthcareProfessional).count()
        re_assigns = session.query(ProfessionalPatientAssignment).count()
        _print_summary(session, re_profs, re_assigns)
        session.close()
        return

    # Full seed: clean all clinical data
    session.execute(text("DELETE FROM clinical.symptom_observation CASCADE"))
    session.execute(text("DELETE FROM clinical.clinical_consultation CASCADE"))
    session.execute(text("DELETE FROM clinical.clinical_episode CASCADE"))
    session.execute(text("DELETE FROM clinical.healthcare_professionals CASCADE"))
    session.execute(text("DELETE FROM clinical.patient_profile CASCADE"))
    session.execute(text("DELETE FROM security.patient_identity CASCADE"))
    session.execute(text("DELETE FROM clinical.professional_patient_assignments CASCADE"))
    session.commit()

    # ========================================================================
    # 1. Core reference data (use existing or create)
    # ========================================================================
    sex_types = session.query(SexType).all() or []
    if not sex_types:
        for code, desc in [("M", "Masculino"), ("F", "Feminino")]:
            st = SexType(code=code, description=desc)
            session.add(st)
            session.flush()
            sex_types.append(st)

    genders = session.query(GenderIdentity).all() or []
    if not genders:
        for code, desc in [("M", "Masculino"), ("F", "Feminino"), ("NB", "Não-binário"), ("O", "Outro")]:
            g = GenderIdentity(code=code, description=desc)
            session.add(g)
            session.flush()
            genders.append(g)

    edu_levels = session.query(EducationLevel).all() or []
    if not edu_levels:
        for code, desc in [
            ("EF", "Ensino Fundamental"), ("EM", "Ensino Médio"),
            ("ES", "Ensino Superior"), ("PG", "Pós-graduação"),
        ]:
            el = EducationLevel(code=code, description=desc)
            session.add(el)
            session.flush()
            edu_levels.append(el)

    ethnicities = session.query(Ethnicity).all() or []
    if not ethnicities:
        for code, desc in [
            ("BRANCA", "Branca"), ("PARDA", "Parda"), ("PRETA", "Preta"),
            ("AMARELA", "Amarela"), ("INDIGENA", "Indígena"),
        ]:
            et = Ethnicity(code=code, description=desc)
            session.add(et)
            session.flush()
            ethnicities.append(et)

    session.commit()

    # ========================================================================
    # 2. Symptoms — map English keys to existing Portuguese DB names
    # ========================================================================
    symptom_map = {}
    for dd in DISORDER_DEFS:
        for sname, sdesc, *_ in dd["symptoms"]:
            if sname in symptom_map:
                continue
            pt_name = EN_TO_PT_SYMPTOM.get(sname, sname)
            existing = session.query(Symptom).filter_by(symptom_name=pt_name).first()
            if existing:
                symptom_map[sname] = existing.symptom_id
            else:
                pt_key = sname.replace("_", "_")
                sym = Symptom(symptom_name=pt_name, symptom_description=sdesc)
                session.add(sym)
                session.flush()
                symptom_map[sname] = sym.symptom_id

    # ========================================================================
    # 3. Disorders — use existing (seeded by db/seed.py)
    # ========================================================================
    disorder_map = {}
    for dd in DISORDER_DEFS:
        existing = session.query(Disorder).filter_by(disorder_name=dd["name"]).first()
        if existing:
            disorder_map[dd["name"]] = existing.disorder_id
            continue
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

    session.commit()

    # ========================================================================
    # 4. Assessment scales — use existing (seeded by seed_scales_groups.py)
    # ========================================================================
    scale_map = {}
    for sname, sdef in SCALE_DEFS.items():
        existing_scale = session.query(AssessmentScale).filter_by(scale_name=sname).first()
        if existing_scale:
            questions = session.query(ScaleQuestion).filter_by(scale_id=existing_scale.scale_id).order_by(ScaleQuestion.question_order).all()
            scale_map[sname] = {"scale": existing_scale, "questions": questions, "def": sdef}
            continue
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
    # 5. Healthcare professionals (linked to role-based users)
    # ========================================================================
    professionals = []
    prof_defs = [
        ("Dr. Ricardo Almeida", "CRM 12345-SP", "Psiquiatria", "Psiquiatria Clínica", "clinician"),
        ("Dra. Mariana Costa", "CRM 23456-SP", "Psiquiatria", "Psiquiatria da Infância", "psychiatrist"),
        ("Dr. Fernando Oliveira", "CRP 34567-SP", "Psicologia", "Psicologia Clínica", "psychologist"),
        ("Dra. Patrícia Santos", "CRP 45678-SP", "Psicologia", "Neuropsicologia", "researcher"),
        ("Dr. Eduardo Martins", "CRM 56789-SP", "Psiquiatria", "Psiquiatria Geral", "clinical_supervisor"),
    ]
    for name, license_no, profession, specialty, username in prof_defs:
        user = session.query(User).filter_by(username=username).first()
        prof = HealthcareProfessional(
            full_name=name,
            professional_license=license_no,
            profession=profession,
            specialty=specialty,
            start_date=date(2018, 1, 1),
            user_uuid=user.user_uuid if user else None,
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
    # 8. Professional-patient assignments
    # ========================================================================
    # Distribute patients across professionals (each patient has 1 primary prof)
    for i, pd_item in enumerate(patient_data):
        primary_prof = professionals[i % len(professionals)]
        existing_assign = session.query(ProfessionalPatientAssignment).filter_by(
            patient_uuid=pd_item["patient_uuid"]
        ).first()
        if not existing_assign:
            session.add(ProfessionalPatientAssignment(
                professional_uuid=primary_prof.professional_uuid,
                patient_uuid=pd_item["patient_uuid"],
                is_active=True,
            ))
        # 20% chance of secondary assignment (shared patient)
        if random.random() < 0.20:
            secondary = random.choice([p for p in professionals if p.professional_uuid != primary_prof.professional_uuid])
            existing_sec = session.query(ProfessionalPatientAssignment).filter_by(
                patient_uuid=pd_item["patient_uuid"],
                professional_uuid=secondary.professional_uuid,
            ).first()
            if not existing_sec:
                session.add(ProfessionalPatientAssignment(
                    professional_uuid=secondary.professional_uuid,
                    patient_uuid=pd_item["patient_uuid"],
                    is_active=True,
                ))

    # ========================================================================
    # 9. Generate consultations with symptoms and scale responses
    # ========================================================================
    consultation_records = []

    for i, pd_item in enumerate(patient_data):
        disorders = patient_disorders[pd_item["patient_uuid"]]
        num_consultations = random.randint(2, 6)

        # Primary professional for this patient (same distribution as assignments)
        primary_prof = professionals[i % len(professionals)]

        for ci in range(num_consultations):
            days_ago = random.randint(1, 365)
            consult_date = datetime.now() - timedelta(days=days_ago)
            # Most consultations with primary prof, some with others
            if ci == 0 or random.random() < 0.7:
                prof = primary_prof
            else:
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

            # Add scale responses and run inference via shared helper
            _generate_scale_responses(session, consult, disorders, scale_map, symptom_map, disorder_map)

    # 10. Seed example medical reports for sample patients
    _seed_reports(session, patient_data, consultation_records, professionals)

    session.commit()

    total_assignments = session.query(ProfessionalPatientAssignment).count()
    _print_summary(session, len(professionals), total_assignments)
    session.close()


def _print_summary(session, num_professionals=0, num_assignments=0):
    total_patients = session.query(PatientIdentity).count()
    total_consults = session.query(ClinicalConsultation).count()
    total_symptoms = session.query(SymptomObservation).count()
    total_scales = session.query(ScaleResponse).count()
    total_inferences = session.query(DiagnosticInference).count()
    total_disorders = session.query(Disorder).count()
    total_users = session.query(User).count()
    total_prof_with_user = session.query(HealthcareProfessional).filter(HealthcareProfessional.user_uuid.isnot(None)).count()
    print(f"\n{'='*60}")
    print(f"Seed complete! Clinical dataset created:")
    print(f"  Users:         {total_users}")
    print(f"  Professionals: {num_professionals} ({total_prof_with_user} linked to users)")
    print(f"  Patient Assn:  {num_assignments}")
    total_reports = session.query(MedicalReport).count()
    print(f"  Patients:      {total_patients}")
    print(f"  Disorders:     {total_disorders}")
    print(f"  Consultations: {total_consults}")
    print(f"  Symptoms:      {total_symptoms}")
    print(f"  Scale Resp.:   {total_scales}")
    print(f"  Inferences:    {total_inferences}")
    print(f"  Reports:       {total_reports}")
    print(f"{'='*60}")


if __name__ == "__main__":
    seed()
