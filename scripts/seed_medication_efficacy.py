"""
Seed medication-disorder associations with literature-based efficacy data.
Maps medications to disorders with success/failure rates. Also seeds
any missing medications from the catalog.

Usage:
    docker exec mind-api python scripts/seed_medication_efficacy.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.base import Disorder, Medication, DisorderMedication

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mind:mind@localhost:5432/mind")

# Medications that may not be in the DB yet (from db/seed.py catalog)
MISSING_MEDS = [
    "Paroxetina", "Citalopram", "Desvenlafaxina", "Duloxetina",
    "Trazodona", "Agomelatina", "Amitriptilina", "Nortriptilina",
    "Clomipramina", "Imipramina", "Clozapina", "Paliperidona",
    "Ziprasidona", "Clorpromazina", "Carbamazepina", "Oxcarbazepina",
    "Topiramato", "Lorazepam", "Buspirona", "Atomoxetina",
    "Guanfacina", "Melatonina", "Doxepina", "Donepezila",
    "Rivastigmina", "Memantina", "Galantamina", "Naltrexona",
    "Acamprosato", "Dissulfiram", "Buprenorfina", "Vareniclina",
    "Biperideno",
]

# (medication_name, disorder_name, success_rate, failure_rate, avg_response_weeks, line, strength, notes)
ASSOCIATIONS = [
    # ================================================================
    # ANTIDEPRESSANTS - ISRS
    # ================================================================
    ("Fluoxetina", "Transtorno Depressivo Maior", 0.62, 0.18, 4.0, 1, "A", "ISRS de primeira linha para TDM. Dose inicial 20mg/dia."),
    ("Fluoxetina", "Transtorno Obsessivo-Compulsivo", 0.58, 0.20, 6.0, 1, "A", "Primeira linha para TOC. Doses mais altas (40-80mg)."),
    ("Fluoxetina", "Transtorno do Pânico", 0.55, 0.22, 5.0, 1, "A", "Pode aumentar ansiedade nas primeiras semanas."),
    ("Fluoxetina", "Bulimia Nervosa", 0.60, 0.18, 4.0, 1, "A", "Único ISRS aprovado especificamente para bulimia. Dose 60mg."),

    ("Sertralina", "Transtorno Depressivo Maior", 0.64, 0.17, 4.0, 1, "A", "ISRS de primeira linha. Perfil favorável. Dose 50-200mg."),
    ("Sertralina", "Transtorno de Ansiedade Generalizada", 0.60, 0.19, 4.0, 1, "A", "Primeira linha para TAG. Efeito ansiolítico após 2-4 semanas."),
    ("Sertralina", "Transtorno do Pânico", 0.58, 0.20, 4.0, 1, "A", "Aprovado para pânico. Iniciar 25mg."),
    ("Sertralina", "Transtorno Obsessivo-Compulsivo", 0.56, 0.21, 6.0, 1, "A", "Primeira linha para TOC. Resposta em 8-12 semanas."),
    ("Sertralina", "Transtorno de Estresse Pós-Traumático", 0.60, 0.18, 6.0, 1, "A", "Primeira linha para TEPT."),
    ("Sertralina", "Transtorno de Ansiedade Social", 0.58, 0.20, 6.0, 1, "A", "Primeira linha para fobia social. Dose 50-200mg."),

    ("Escitalopram", "Transtorno Depressivo Maior", 0.66, 0.16, 3.0, 1, "A", "ISRS com melhor tolerabilidade. Dose 10-20mg."),
    ("Escitalopram", "Transtorno de Ansiedade Generalizada", 0.63, 0.17, 3.0, 1, "A", "Primeira linha para TAG."),
    ("Escitalopram", "Transtorno do Pânico", 0.59, 0.19, 4.0, 1, "A", "Eficaz para pânico com ou sem agorafobia."),
    ("Escitalopram", "Transtorno Obsessivo-Compulsivo", 0.55, 0.22, 6.0, 1, "A", "Aprovado para TOC. Dose 10-40mg."),
    ("Escitalopram", "Transtorno de Ansiedade Social", 0.60, 0.18, 4.0, 1, "A", "Eficaz para fobia social. Dose 10-20mg."),

    ("Paroxetina", "Transtorno Depressivo Maior", 0.62, 0.19, 4.0, 1, "A", "ISRS potente. Síndrome de descontinuação. Dose 20-50mg."),
    ("Paroxetina", "Transtorno de Ansiedade Generalizada", 0.61, 0.18, 4.0, 1, "A", "Aprovado para TAG. Efeito sedativo benéfico."),
    ("Paroxetina", "Transtorno do Pânico", 0.60, 0.18, 4.0, 1, "A", "Aprovado para pânico. Iniciar 10mg."),
    ("Paroxetina", "Transtorno Obsessivo-Compulsivo", 0.57, 0.20, 6.0, 1, "A", "Aprovado para TOC. Dose 20-60mg."),
    ("Paroxetina", "Transtorno de Estresse Pós-Traumático", 0.59, 0.19, 6.0, 1, "A", "Aprovado para TEPT. Dose 20-50mg."),
    ("Paroxetina", "Transtorno de Ansiedade Social", 0.62, 0.17, 6.0, 1, "A", "Aprovado para fobia social."),

    ("Citalopram", "Transtorno Depressivo Maior", 0.60, 0.20, 4.0, 1, "A", "ISRS. Risco QT em doses >40mg. Dose 20-40mg."),
    ("Citalopram", "Transtorno do Pânico", 0.55, 0.22, 5.0, 2, "B", "Alternativa de segunda linha para pânico."),
    ("Citalopram", "Transtorno Obsessivo-Compulsivo", 0.50, 0.25, 6.0, 2, "B", "Segunda linha para TOC."),

    # ================================================================
    # ANTIDEPRESSANTS - ISRSN
    # ================================================================
    ("Venlafaxina", "Transtorno Depressivo Maior", 0.65, 0.16, 3.5, 1, "A", "ISRSN. Dose 75-225mg. Monitorar PA."),
    ("Venlafaxina", "Transtorno de Ansiedade Generalizada", 0.64, 0.16, 3.0, 1, "A", "Primeira linha para TAG. Início mais rápido."),
    ("Venlafaxina", "Transtorno do Pânico", 0.58, 0.20, 4.0, 1, "A", "Aprovado para pânico. Dose 75-225mg."),
    ("Venlafaxina", "Transtorno de Ansiedade Social", 0.60, 0.18, 4.0, 1, "A", "Aprovado para fobia social."),

    ("Desvenlafaxina", "Transtorno Depressivo Maior", 0.62, 0.18, 3.5, 1, "A", "Metabólito da venlafaxina. Dose 50mg."),
    ("Desvenlafaxina", "Transtorno de Ansiedade Generalizada", 0.60, 0.19, 3.5, 1, "A", "Aprovado para TAG. Dose 50mg."),

    ("Duloxetina", "Transtorno Depressivo Maior", 0.63, 0.17, 3.5, 1, "A", "ISRSN duplo. Dose 60-120mg."),
    ("Duloxetina", "Transtorno de Ansiedade Generalizada", 0.62, 0.17, 3.0, 1, "A", "Primeira linha para TAG. Eficaz para dor crônica associada."),

    # ================================================================
    # ANTIDEPRESSANTS - NDRI / NaSSA / SARI / Melatonérgico
    # ================================================================
    ("Bupropiona", "Transtorno Depressivo Maior", 0.61, 0.18, 4.0, 1, "A", "NDRI. Sem efeitos sexuais. Dose 150-300mg."),
    ("Bupropiona", "Transtorno por Uso de Substâncias", 0.50, 0.25, 8.0, 2, "B", "Auxiliar na cessação do tabagismo."),

    ("Mirtazapina", "Transtorno Depressivo Maior", 0.63, 0.17, 3.0, 1, "A", "NaSSA. Efeito sedativo. Dose 15-45mg."),
    ("Mirtazapina", "Transtorno de Insônia", 0.55, 0.20, 2.0, 2, "B", "Usado off-label para insônia. Dose 7.5-15mg."),

    ("Trazodona", "Transtorno Depressivo Maior", 0.55, 0.22, 4.0, 2, "B", "SARI. Dose 150-300mg."),
    ("Trazodona", "Transtorno de Insônia", 0.65, 0.15, 1.0, 1, "A", "Amplamente usado para insônia. Dose 25-100mg."),

    ("Agomelatina", "Transtorno Depressivo Maior", 0.58, 0.20, 3.0, 2, "B", "Melatonérgico. Sem efeitos sexuais."),

    # ================================================================
    # ANTIDEPRESSANTS - Tricíclicos
    # ================================================================
    ("Amitriptilina", "Transtorno Depressivo Maior", 0.55, 0.22, 4.5, 2, "B", "Tricíclico. Muitos efeitos anticolinérgicos. Dose 75-150mg."),
    ("Amitriptilina", "Transtorno de Insônia", 0.60, 0.18, 1.5, 2, "B", "Usado para insônia. Dose 12.5-50mg."),
    ("Amitriptilina", "Transtorno de Sintomas Somáticos", 0.55, 0.22, 4.0, 2, "B", "Usado para dor crônica e fibromialgia."),

    ("Nortriptilina", "Transtorno Depressivo Maior", 0.53, 0.24, 4.5, 2, "B", "Tricíclico. Menos efeitos anticolinérgicos. Dose 50-150mg."),

    ("Clomipramina", "Transtorno Obsessivo-Compulsivo", 0.65, 0.15, 5.0, 1, "A", "Primeira linha para TOC. Dose 100-250mg."),
    ("Clomipramina", "Transtorno Depressivo Maior", 0.55, 0.22, 4.0, 2, "B", "Tricíclico. Segunda linha para TDM."),

    ("Imipramina", "Transtorno Depressivo Maior", 0.52, 0.25, 5.0, 2, "B", "Tricíclico clássico. Dose 75-200mg."),
    ("Imipramina", "Transtorno do Pânico", 0.55, 0.22, 4.0, 2, "B", "Segunda linha para pânico."),

    # ================================================================
    # ANTIPSICÓTICOS - Atípicos
    # ================================================================
    ("Risperidona", "Esquizofrenia / Transtorno Psicótico", 0.70, 0.12, 3.0, 1, "A", "Antipsicótico atípico de primeira linha. Dose 2-8mg."),
    ("Risperidona", "Transtorno Bipolar Tipo I", 0.62, 0.18, 3.0, 1, "A", "Aprovado para mania aguda e manutenção."),
    ("Risperidona", "Transtorno Bipolar Tipo II", 0.55, 0.22, 4.0, 2, "B", "Estabilizador adjuvante. Dose 1-3mg."),
    ("Risperidona", "Transtorno Depressivo Maior", 0.50, 0.25, 4.0, 3, "C", "Aumento para TDM refratário. Dose 0.5-2mg."),
    ("Risperidona", "Transtorno do Espectro Autista", 0.55, 0.22, 6.0, 1, "A", "Aprovado para irritabilidade no TEA. Dose 0.5-3mg."),

    ("Olanzapina", "Esquizofrenia / Transtorno Psicótico", 0.72, 0.11, 2.5, 1, "A", "Antipsicótico potente. Risco metabólico. Dose 10-20mg."),
    ("Olanzapina", "Transtorno Bipolar Tipo I", 0.68, 0.14, 2.0, 1, "A", "Primeira linha para mania aguda."),
    ("Olanzapina", "Transtorno Depressivo Maior", 0.52, 0.24, 3.5, 3, "C", "Aumento para TDM refratário. Dose 5-10mg."),
    ("Olanzapina", "Anorexia Nervosa", 0.45, 0.30, 6.0, 2, "C", "Usado para ganho de peso na anorexia."),

    ("Quetiapina", "Esquizofrenia / Transtorno Psicótico", 0.68, 0.13, 3.0, 1, "A", "Antipsicótico atípico. Dose 300-800mg."),
    ("Quetiapina", "Transtorno Bipolar Tipo I", 0.66, 0.15, 2.5, 1, "A", "Aprovado para mania e depressão bipolar."),
    ("Quetiapina", "Transtorno Bipolar Tipo II", 0.60, 0.18, 3.0, 1, "A", "Aprovado para depressão bipolar II."),
    ("Quetiapina", "Transtorno Depressivo Maior", 0.57, 0.20, 3.0, 1, "A", "Aprovado como adjuvante para TDM."),
    ("Quetiapina", "Transtorno de Ansiedade Generalizada", 0.55, 0.22, 3.0, 2, "B", "Segunda linha para TAG. Liberação prolongada."),
    ("Quetiapina", "Transtorno de Insônia", 0.60, 0.18, 1.0, 2, "B", "Usado off-label para insônia. Dose 12.5-50mg."),

    ("Aripiprazol", "Esquizofrenia / Transtorno Psicótico", 0.67, 0.14, 3.0, 1, "A", "Antipsicótico. Perfil metabólico favorável. Dose 10-30mg."),
    ("Aripiprazol", "Transtorno Bipolar Tipo I", 0.63, 0.17, 3.0, 1, "A", "Aprovado para mania e manutenção."),
    ("Aripiprazol", "Transtorno Depressivo Maior", 0.58, 0.20, 3.5, 1, "A", "Aprovado como adjuvante para TDM. Dose 2-15mg."),
    ("Aripiprazol", "Transtorno Obsessivo-Compulsivo", 0.45, 0.30, 8.0, 3, "C", "Aumento para TOC refratário."),
    ("Aripiprazol", "Transtorno do Espectro Autista", 0.45, 0.30, 8.0, 2, "B", "Usado para irritabilidade no TEA."),

    ("Clozapina", "Esquizofrenia / Transtorno Psicótico", 0.78, 0.08, 4.0, 3, "A", "Gold standard para esquizofrenia refratária."),
    ("Clozapina", "Transtorno Bipolar Tipo I", 0.55, 0.22, 4.0, 4, "C", "Reservado para bipolar refratário."),

    ("Paliperidona", "Esquizofrenia / Transtorno Psicótico", 0.66, 0.15, 3.0, 1, "A", "Metabólito da risperidona. Dose 6-12mg."),
    ("Paliperidona", "Transtorno Bipolar Tipo I", 0.55, 0.22, 3.5, 2, "B", "Aprovado para mania aguda."),

    ("Ziprasidona", "Esquizofrenia / Transtorno Psicótico", 0.60, 0.20, 3.5, 1, "A", "Antipsicótico. Neutralidade metabólica. Dose 80-160mg."),
    ("Ziprasidona", "Transtorno Bipolar Tipo I", 0.55, 0.22, 3.5, 2, "B", "Aprovado para mania aguda."),

    # ================================================================
    # ANTIPSICÓTICOS - Típicos
    # ================================================================
    ("Haloperidol", "Esquizofrenia / Transtorno Psicótico", 0.70, 0.15, 2.0, 1, "A", "Antipsicótico típico potente. Dose 5-20mg."),
    ("Haloperidol", "Transtorno Bipolar Tipo I", 0.65, 0.18, 2.0, 1, "A", "Eficaz na mania aguda. Dose 5-15mg."),

    ("Clorpromazina", "Esquizofrenia / Transtorno Psicótico", 0.62, 0.20, 3.0, 1, "A", "Antipsicótico típico. Dose 300-800mg."),

    # ================================================================
    # ESTABILIZADORES DE HUMOR
    # ================================================================
    ("Carbonato de Lítio", "Transtorno Bipolar Tipo I", 0.72, 0.10, 3.0, 1, "A", "Gold standard. Litemia 0.6-1.2 mEq/L."),
    ("Carbonato de Lítio", "Transtorno Bipolar Tipo II", 0.68, 0.14, 3.0, 1, "A", "Primeira linha para depressão bipolar."),
    ("Carbonato de Lítio", "Transtorno Depressivo Maior", 0.48, 0.28, 5.0, 3, "C", "Aumento para TDM refratário."),

    ("Valproato de Sódio", "Transtorno Bipolar Tipo I", 0.68, 0.14, 2.0, 1, "A", "Primeira linha para mania aguda."),
    ("Valproato de Sódio", "Transtorno Bipolar Tipo II", 0.55, 0.22, 3.5, 2, "B", "Alternativa para ciclagem rápida."),

    ("Lamotrigina", "Transtorno Bipolar Tipo I", 0.60, 0.18, 6.0, 1, "A", "Excelente para depressão bipolar."),
    ("Lamotrigina", "Transtorno Bipolar Tipo II", 0.65, 0.16, 6.0, 1, "A", "Primeira linha para depressão bipolar II."),
    ("Lamotrigina", "Transtorno Depressivo Maior", 0.45, 0.30, 6.0, 4, "C", "Evidência limitada para TDM."),

    ("Carbamazepina", "Transtorno Bipolar Tipo I", 0.55, 0.22, 3.0, 2, "B", "Segunda linha para mania."),

    ("Oxcarbazepina", "Transtorno Bipolar Tipo I", 0.50, 0.25, 3.5, 3, "C", "Alternativa para bipolar."),

    ("Topiramato", "Transtorno Bipolar Tipo I", 0.35, 0.40, 8.0, 4, "C", "Evidência limitada."),
    ("Topiramato", "Transtorno de Compulsão Alimentar", 0.55, 0.25, 8.0, 2, "B", "Reduz compulsão alimentar. Dose 50-150mg."),

    # ================================================================
    # ANSIOLÍTICOS
    # ================================================================
    ("Clonazepam", "Transtorno de Ansiedade Generalizada", 0.60, 0.20, 1.0, 2, "B", "Benzodiazepínico. Risco de dependência."),
    ("Clonazepam", "Transtorno do Pânico", 0.65, 0.18, 1.0, 2, "B", "Eficaz para pânico. Uso curto prazo."),
    ("Clonazepam", "Transtorno de Insônia", 0.55, 0.22, 0.5, 3, "C", "Risco de tolerância e dependência."),

    ("Alprazolam", "Transtorno do Pânico", 0.68, 0.16, 0.5, 1, "A", "Aprovado para pânico. Dose 0.5-6mg."),
    ("Alprazolam", "Transtorno de Ansiedade Generalizada", 0.62, 0.19, 0.5, 2, "B", "Eficaz para TAG. Risco de dependência."),

    ("Diazepam", "Transtorno de Ansiedade Generalizada", 0.58, 0.22, 0.5, 2, "B", "Benzodiazepínico longa duração. Dose 5-40mg."),

    ("Lorazepam", "Transtorno de Ansiedade Generalizada", 0.55, 0.24, 0.5, 2, "B", "Benzodiazepínico. Dose 1-6mg."),

    ("Buspirona", "Transtorno de Ansiedade Generalizada", 0.55, 0.22, 4.0, 1, "A", "Não benzodiazepínico. Sem dependência. Dose 15-60mg."),

    # ================================================================
    # PSICOESTIMULANTES
    # ================================================================
    ("Metilfenidato", "Transtorno de Déficit de Atenção/Hiperatividade", 0.72, 0.10, 1.0, 1, "A", "Primeira linha para TDAH. Dose 10-60mg."),
    ("Lisdexanfetamina", "Transtorno de Déficit de Atenção/Hiperatividade", 0.75, 0.08, 1.0, 1, "A", "Pró-fármaco. Duração 12h. Dose 30-70mg."),
    ("Atomoxetina", "Transtorno de Déficit de Atenção/Hiperatividade", 0.58, 0.20, 4.0, 2, "A", "Inibidor de recaptação de NA. Dose 40-80mg."),
    ("Guanfacina", "Transtorno de Déficit de Atenção/Hiperatividade", 0.55, 0.22, 3.0, 2, "B", "Agonista alfa-2. Liberação prolongada."),

    # ================================================================
    # HIPNÓTICOS
    # ================================================================
    ("Zolpidem", "Transtorno de Insônia", 0.70, 0.12, 0.5, 1, "A", "Hipnótico não BZD. Dose 5-10mg."),
    ("Melatonina", "Transtorno de Insônia", 0.40, 0.30, 1.0, 1, "C", "Eficácia modesta. Dose 0.5-5mg. Seguro."),
    ("Doxepina", "Transtorno de Insônia", 0.60, 0.18, 1.0, 1, "A", "Tricíclico em baixa dose. 3-6mg. Aprovado para insônia."),

    # ================================================================
    # ANTIDEMÊNCIA
    # ================================================================
    ("Donepezila", "Transtorno Neurocognitivo Maior — Doença de Alzheimer", 0.45, 0.28, 12.0, 1, "A", "Inibidor de acetilcolinesterase. Dose 5-10mg."),
    ("Rivastigmina", "Transtorno Neurocognitivo Maior — Doença de Alzheimer", 0.48, 0.26, 12.0, 1, "A", "Inibidor de acetilcolinesterase. Dose 3-12mg."),
    ("Rivastigmina", "Transtorno Neurocognitivo Leve", 0.30, 0.40, 16.0, 2, "C", "Evidência limitada para NCD leve."),
    ("Memantina", "Transtorno Neurocognitivo Maior — Doença de Alzheimer", 0.42, 0.30, 8.0, 2, "A", "Antagonista NMDA. Dose 10-20mg."),
    ("Galantamina", "Transtorno Neurocognitivo Maior — Doença de Alzheimer", 0.44, 0.28, 12.0, 1, "A", "Inibidor de acetilcolinesterase. Dose 16-24mg."),

    # ================================================================
    # DEPENDÊNCIA QUÍMICA
    # ================================================================
    ("Naltrexona", "Transtorno por Uso de Substâncias", 0.50, 0.28, 4.0, 1, "A", "Antagonista opioide. Álcool e opioides."),
    ("Acamprosato", "Transtorno por Uso de Substâncias", 0.45, 0.30, 4.0, 1, "A", "Estabilizador glutamatérgico. Álcool."),
    ("Dissulfiram", "Transtorno por Uso de Substâncias", 0.42, 0.35, 2.0, 2, "B", "Aversivo para álcool. Dose 250-500mg."),
    ("Buprenorfina", "Transtorno por Uso de Substâncias", 0.65, 0.15, 2.0, 1, "A", "Agonista parcial opioide. Dose 8-24mg."),
    ("Vareniclina", "Transtorno por Uso de Substâncias", 0.55, 0.22, 4.0, 1, "A", "Agonista nicotínico. Cessação tabagismo."),

    # ================================================================
    # ANTICOLINÉRGICOS
    # ================================================================
    ("Biperideno", "Esquizofrenia / Transtorno Psicótico", 0.75, 0.10, 0.5, 2, "B", "Anticolinérgico para EPS. Dose 2-8mg. Não trata psicose."),
]


def seed():
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # 1. Add any missing medications
        for med_name in MISSING_MEDS:
            existing = session.query(Medication).filter(Medication.name == med_name).first()
            if not existing:
                session.add(Medication(name=med_name, active_ingredient=med_name, classification="Outro"))
                print(f"[ADD] Added medication '{med_name}'")
        session.commit()

        # 2. Seed associations
        count = 0
        for (med_name, disorder_name, sr, fr, arw, line, strength, notes) in ASSOCIATIONS:
            med = session.query(Medication).filter(Medication.name == med_name).first()
            disorder = session.query(Disorder).filter(Disorder.disorder_name == disorder_name).first()
            if not med:
                print(f"[SKIP] Medication '{med_name}' not found")
                continue
            if not disorder:
                print(f"[SKIP] Disorder '{disorder_name}' not found in DB")
                continue

            existing = session.query(DisorderMedication).filter(
                DisorderMedication.medication_id == med.medication_id,
                DisorderMedication.disorder_id == disorder.disorder_id,
            ).first()
            if existing:
                existing.success_rate = sr
                existing.failure_rate = fr
                existing.avg_response_weeks = arw
                existing.line_of_treatment = line
                existing.recommendation_strength = strength
                existing.notes = notes
            else:
                dm = DisorderMedication(
                    medication_id=med.medication_id,
                    disorder_id=disorder.disorder_id,
                    success_rate=sr,
                    failure_rate=fr,
                    avg_response_weeks=arw,
                    line_of_treatment=line,
                    recommendation_strength=strength,
                    notes=notes,
                )
                session.add(dm)
            count += 1

        session.commit()
        print(f"[OK] Seeded/updated {count} medication-disorder associations")


if __name__ == "__main__":
    seed()
