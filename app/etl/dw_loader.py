"""ETL: Extract from clinical schema, transform, load into DW star schema."""

from datetime import date, datetime
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.dw import DWBase, DimDate, DimPatient, DimDisorder, DimScale
from app.models.dw import DimProfessional, FactConsultation, FactSymptom, FactDiagnosis, FactScaleResponse


def create_date_key(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day


def ensure_dim_date(session: Session, start: date, end: date):
    existing = {r[0] for r in session.query(DimDate.date_key).all()}
    d = start
    while d <= end:
        dk = create_date_key(d)
        if dk not in existing:
            dd = DimDate(
                date_key=dk, full_date=d, year=d.year, quarter=(d.month - 1) // 3 + 1,
                month=d.month, month_name=d.strftime("%B"), week=d.isocalendar()[1],
                day_of_year=d.timetuple().tm_yday, day_of_month=d.day,
                day_of_week=d.weekday(), day_name=d.strftime("%A"),
                is_weekend=d.weekday() >= 5,
            )
            session.add(dd)
        d += __import__("datetime").timedelta(days=1)
    session.commit()


def load_dim_patient(session: Session):
    session.execute(text("DELETE FROM dw.dim_patient"))
    rows = session.execute(text("""
        SELECT pp.profile_uuid, pi.patient_uuid,
               extract(year from age(pp.birth_date))::int as age,
               st.description as sex,
               el.description as education,
               et.description as ethnicity,
               pp.marital_status, pp.occupation
        FROM clinical.patient_profile pp
        JOIN security.patient_identity pi ON pp.patient_uuid = pi.patient_uuid
        LEFT JOIN core.sex_types st ON pp.sex_type_id = st.sex_type_id
        LEFT JOIN core.education_levels el ON pp.education_level_id = el.education_level_id
        LEFT JOIN core.ethnicities et ON pp.ethnicity_id = et.ethnicity_id
    """)).fetchall()

    for i, row in enumerate(rows, 1):
        age = row.age or 0
        if age < 18: age_group = "0-17"
        elif age < 30: age_group = "18-29"
        elif age < 45: age_group = "30-44"
        elif age < 60: age_group = "45-59"
        else: age_group = "60+"

        dp = DimPatient(
            patient_key=i, patient_uuid=row.patient_uuid,
            age_group=age_group, sex=row.sex, education_level=row.education,
            ethnicity=row.ethnicity, marital_status=row.marital_status,
            occupation=row.occupation, is_current=True,
        )
        session.add(dp)
    session.commit()
    return len(rows)


def load_dim_disorder(session: Session):
    session.execute(text("DELETE FROM dw.dim_disorder"))
    rows = session.execute(text("""
        SELECT disorder_id, disorder_name, cid_code, dsm_code, dsm_chapter
        FROM diagnostic.disorders ORDER BY disorder_id
    """)).fetchall()

    def category_from_chapter(chapter: str | None) -> str:
        if not chapter:
            return "Other"
        m = {
            "Transtornos do Neurodesenvolvimento": "Neurodevelopmental Disorders",
            "Espectro da Esquizofrenia e Outros Transtornos Psicóticos": "Psychotic Disorders",
            "Transtornos Bipolares e Relacionados": "Bipolar Disorders",
            "Transtornos Depressivos": "Depressive Disorders",
            "Transtornos de Ansiedade": "Anxiety Disorders",
            "Transtornos Obsessivo-Compulsivos e Relacionados": "OCD-Related Disorders",
            "Transtornos Relacionados a Trauma e Estressores": "Trauma Disorders",
            "Transtornos Dissociativos": "Dissociative Disorders",
            "Transtornos de Sintomas Somáticos e Relacionados": "Somatic Disorders",
            "Transtornos Alimentares e da Alimentação": "Eating Disorders",
            "Transtornos da Eliminação": "Elimination Disorders",
            "Transtornos do Sono-Vigília": "Sleep-Wake Disorders",
            "Disfunções Sexuais": "Sexual Dysfunctions",
            "Disforia de Gênero": "Gender Dysphoria",
            "Transtornos Disruptivos, do Controle de Impulsos e da Conduta": "Disruptive Disorders",
            "Transtornos Relacionados a Substâncias e Aditivos": "Substance-Related Disorders",
            "Transtornos Neurocognitivos": "Neurocognitive Disorders",
            "Transtornos da Personalidade": "Personality Disorders",
            "Transtornos Parafílicos": "Paraphilic Disorders",
            "Outros Transtornos Mentais": "Other Mental Disorders",
        }
        return m.get(chapter, "Other")

    for i, row in enumerate(rows, 1):
        dd = DimDisorder(
            disorder_key=i, disorder_id=row.disorder_id,
            disorder_name=row.disorder_name, cid_code=row.cid_code,
            dsm_code=row.dsm_code,
            disorder_category=category_from_chapter(row.dsm_chapter),
        )
        session.add(dd)
    session.commit()


def load_dim_scale(session: Session):
    session.execute(text("DELETE FROM dw.dim_scale"))
    rows = session.execute(text("""
        SELECT s.scale_id, s.scale_name, s.scale_description,
               (SELECT count(*) FROM diagnostic.scale_questions q WHERE q.scale_id = s.scale_id) as qcount
        FROM diagnostic.assessment_scales s
    """)).fetchall()

    max_scores = {
        "PHQ-9": 27.0, "GAD-7": 21.0, "MADRS": 60.0, "MDQ": 13.0,
        "PCL-5": 80.0, "Y-BOCS": 40.0, "AUDIT": 40.0, "ASRM": 20.0,
        "ASRS": 72.0, "AQ-10": 10.0,
        "BFP": 100.0, "DT-12 (Tríade Sombria)": 72.0,
        "HEXACO-60": 300.0, "BIS-11": 120.0, "TAS-20": 100.0, "RSES": 40.0,
        "MEMÓRIA": 16.0, "QI - RASTREIO": 30.0,
        "RECONHECIMENTO DE ROSTOS": 12.0, "FLUÊNCIA VERBAL": 16.0,
        "TESTE DO RELÓGIO": 18.0, "TRILHAS": 18.0, "STROOP": 16.0,
        "CANCELAMENTO": 12.0, "FIGURA COMPLEXA DE REY": 24.0,
    }
    for i, row in enumerate(rows, 1):
        ds = DimScale(
            scale_key=i, scale_id=row.scale_id, scale_name=row.scale_name,
            scale_description=row.scale_description, question_count=row.qcount,
            max_score=max_scores.get(row.scale_name, 0),
        )
        session.add(ds)
    session.commit()


def load_dim_professional(session: Session):
    session.execute(text("DELETE FROM dw.dim_professional"))
    rows = session.execute(text("""
        SELECT professional_uuid, full_name, profession, specialty
        FROM clinical.healthcare_professionals
    """)).fetchall()

    for i, row in enumerate(rows, 1):
        dp = DimProfessional(
            professional_key=i, professional_uuid=row.professional_uuid,
            full_name=row.full_name, profession=row.profession, specialty=row.specialty,
        )
        session.add(dp)
    session.commit()


def load_fact_consultation(session: Session):
    session.execute(text("DELETE FROM dw.fact_consultation"))
    # Build lookup maps
    patient_map = {r.patient_uuid: r.patient_key for r in session.query(DimPatient).all()}
    prof_map = {r.professional_uuid: r.professional_key for r in session.query(DimProfessional).all()}

    rows = session.execute(text("""
        SELECT c.consultation_uuid, c.profile_uuid, c.professional_uuid, c.consultation_date,
               pi.patient_uuid
        FROM clinical.clinical_consultation c
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        JOIN security.patient_identity pi ON pp.patient_uuid = pi.patient_uuid
    """)).fetchall()

    for i, row in enumerate(rows, 1):
        dk = create_date_key(row.consultation_date.date())
        pk = patient_map.get(row.patient_uuid)
        prk = prof_map.get(row.professional_uuid)

        # Aggregate symptom stats for this consultation
        sym_stats = session.execute(text("""
            SELECT count(*) as cnt, coalesce(sum(intensity),0) as tot,
                   coalesce(avg(intensity),0) as avg
            FROM clinical.symptom_observation
            WHERE consultation_uuid = :cuuid
        """), {"cuuid": row.consultation_uuid}).fetchone()

        # Scale stats
        scale_count = session.execute(text("""
            SELECT count(DISTINCT sq.scale_id) FROM clinical.scale_responses sr
            JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
            WHERE sr.consultation_uuid = :cuuid
        """), {"cuuid": row.consultation_uuid}).scalar() or 0

        # Inference stats
        inf_stats = session.execute(text("""
            SELECT count(*) as cnt, max(inference_probability) as maxp
            FROM diagnostic.diagnostic_inference
            WHERE consultation_uuid = :cuuid
        """), {"cuuid": row.consultation_uuid}).fetchone()

        fc = FactConsultation(
            consultation_key=i,
            consultation_uuid=row.consultation_uuid,
            date_key=dk, patient_key=pk, professional_key=prk,
            symptom_count=sym_stats.cnt,
            total_intensity=round(float(sym_stats.tot), 2) if sym_stats.tot else 0,
            avg_intensity=round(float(sym_stats.avg), 2) if sym_stats.avg else 0,
            scale_count=scale_count,
            has_inference=inf_stats.cnt > 0,
            inference_count=inf_stats.cnt,
            max_probability=round(float(inf_stats.maxp), 6) if inf_stats.maxp else None,
            created_at=row.consultation_date,
        )
        session.add(fc)
    session.commit()
    return len(rows)


def load_fact_symptom(session: Session):
    session.execute(text("DELETE FROM dw.fact_symptom"))
    consult_map = {r.consultation_uuid: r.consultation_key for r in session.query(FactConsultation).all()}
    patient_map = {r.patient_uuid: r.patient_key for r in session.query(DimPatient).all()}
    disorder_map = {r.disorder_id: r.disorder_key for r in session.query(DimDisorder).all()}

    rows = session.execute(text("""
        SELECT so.observation_id, so.consultation_uuid, so.symptom_id, so.intensity,
               so.frequency, so.duration_days, sym.symptom_name,
               pp.patient_uuid, c.consultation_date,
               dc.disorder_id
        FROM clinical.symptom_observation so
        JOIN diagnostic.symptoms sym ON so.symptom_id = sym.symptom_id
        JOIN clinical.clinical_consultation c ON so.consultation_uuid = c.consultation_uuid
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        LEFT JOIN diagnostic.diagnostic_criteria dc ON dc.symptom_id = so.symptom_id
            AND dc.disorder_id = (
                SELECT di.disorder_id FROM diagnostic.diagnostic_inference di
                WHERE di.consultation_uuid = so.consultation_uuid
                ORDER BY di.inference_probability DESC LIMIT 1
            )
    """)).fetchall()

    for i, row in enumerate(rows, 1):
        ck = consult_map.get(row.consultation_uuid)
        pk = patient_map.get(row.patient_uuid)
        dk = create_date_key(row.consultation_date.date())
        dok = disorder_map.get(row.disorder_id) if row.disorder_id else None

        fs = FactSymptom(
            symptom_key=i, observation_id=row.observation_id,
            consultation_key=ck, patient_key=pk, date_key=dk,
            disorder_key=dok, symptom_name=row.symptom_name,
            intensity=row.intensity, frequency=row.frequency,
            duration_days=row.duration_days, is_present=True,
        )
        session.add(fs)
    session.commit()


def load_fact_diagnosis(session: Session):
    session.execute(text("DELETE FROM dw.fact_diagnosis"))
    consult_map = {r.consultation_uuid: r.consultation_key for r in session.query(FactConsultation).all()}
    patient_map = {r.patient_uuid: r.patient_key for r in session.query(DimPatient).all()}
    disorder_map = {r.disorder_id: r.disorder_key for r in session.query(DimDisorder).all()}

    rows = session.execute(text("""
        SELECT di.inference_uuid, di.consultation_uuid, di.disorder_id,
               di.inference_probability, di.confidence_level, di.model_version,
               c.consultation_date, pp.patient_uuid
        FROM diagnostic.diagnostic_inference di
        JOIN clinical.clinical_consultation c ON di.consultation_uuid = c.consultation_uuid
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        WHERE di.disorder_id IS NOT NULL
    """)).fetchall()

    for i, row in enumerate(rows, 1):
        ck = consult_map.get(row.consultation_uuid)
        pk = patient_map.get(row.patient_uuid)
        dk = create_date_key(row.consultation_date.date())
        dok = disorder_map.get(row.disorder_id)
        if not all([ck, pk, dok]):
            continue

        fd = FactDiagnosis(
            diagnosis_key=i, inference_uuid=row.inference_uuid,
            consultation_key=ck, patient_key=pk, disorder_key=dok,
            date_key=dk, probability=row.inference_probability,
            confidence_level=row.confidence_level,
            model_version=row.model_version,
            is_primary=(i == 1),
        )
        session.add(fd)
    session.commit()


def load_fact_scale_response(session: Session):
    session.execute(text("DELETE FROM dw.fact_scale_response"))
    consult_map = {r.consultation_uuid: r.consultation_key for r in session.query(FactConsultation).all()}
    patient_map = {r.patient_uuid: r.patient_key for r in session.query(DimPatient).all()}
    scale_map = {r.scale_id: r.scale_key for r in session.query(DimScale).all()}

    max_scores = {
        "PHQ-9": 27.0, "GAD-7": 21.0, "MADRS": 60.0, "MDQ": 13.0,
        "PCL-5": 80.0, "Y-BOCS": 40.0, "AUDIT": 40.0, "ASRM": 20.0,
        "ASRS": 72.0, "AQ-10": 10.0, "BFP": 100.0, "DT-12 (Tríade Sombria)": 72.0,
        "HEXACO-60": 300.0, "BIS-11": 120.0, "TAS-20": 100.0, "RSES": 40.0,
    }
    severity_map = {
        "PHQ-9": [(0, "none"), (5, "mild"), (10, "moderate"), (15, "moderately severe"), (20, "severe")],
        "GAD-7": [(0, "none"), (5, "mild"), (10, "moderate"), (15, "severe")],
        "MADRS": [(0, "absent"), (7, "mild"), (20, "moderate"), (35, "severe")],
        "MDQ": [(0, "negative"), (7, "positive")],
        "PCL-5": [(0, "none"), (31, "mild"), (45, "moderate"), (56, "severe")],
        "Y-BOCS": [(0, "none"), (8, "mild"), (16, "moderate"), (24, "severe"), (32, "extreme")],
        "AUDIT": [(0, "low risk"), (8, "hazardous"), (16, "harmful"), (20, "dependence")],
        "ASRM": [(0, "none"), (6, "possible hypomania"), (10, "probable mania")],
        "ASRS": [(0, "low"), (17, "moderate"), (24, "high")],
        "AQ-10": [(0, "negative"), (6, "positive")],
    }

    rows = session.execute(text("""
        SELECT sr.consultation_uuid, sq.scale_id, s.scale_name,
               sum(sr.response_value) as total_score,
               c.consultation_date, pp.patient_uuid
        FROM clinical.scale_responses sr
        JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
        JOIN diagnostic.assessment_scales s ON sq.scale_id = s.scale_id
        JOIN clinical.clinical_consultation c ON sr.consultation_uuid = c.consultation_uuid
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        GROUP BY sr.consultation_uuid, sq.scale_id, s.scale_name, c.consultation_date, pp.patient_uuid
    """)).fetchall()

    for i, row in enumerate(rows, 1):
        ck = consult_map.get(row.consultation_uuid)
        pk = patient_map.get(row.patient_uuid)
        sk = scale_map.get(row.scale_id)
        dk = create_date_key(row.consultation_date.date())
        if not all([ck, pk, sk]):
            continue

        max_possible = max_scores.get(row.scale_name, 0)
        total = float(row.total_score or 0)
        pct = round(total / max_possible * 100, 2) if max_possible > 0 else 0

        severity = "unknown"
        thresholds = severity_map.get(row.scale_name, [])
        for thresh, label in reversed(thresholds):
            if total >= thresh:
                severity = label
                break

        fsr = FactScaleResponse(
            scale_response_key=i, response_id=i,
            consultation_key=ck, patient_key=pk, scale_key=sk,
            date_key=dk, total_score=total, max_possible=max_possible,
            percentage_score=pct, severity_level=severity,
        )
        session.add(fsr)
    session.commit()


def run_full_etl():
    engine = create_engine(settings.database_url, echo=False)
    DWBase.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    try:
        # Truncate fact tables first to avoid FK violations
        for tbl in ["dw.fact_scale_response", "dw.fact_diagnosis", "dw.fact_symptom", "dw.fact_consultation",
                     "dw.dim_patient", "dw.dim_disorder", "dw.dim_scale", "dw.dim_professional"]:
            session.execute(text(f"DELETE FROM {tbl}"))  # nosec - controlled table names
        session.commit()

        # Date dimension
        ensure_dim_date(session, date(2024, 1, 1), date(2027, 12, 31))

        # Dimensions
        p_count = load_dim_patient(session)
        load_dim_disorder(session)
        load_dim_scale(session)
        load_dim_professional(session)

        # Facts
        c_count = load_fact_consultation(session)
        load_fact_symptom(session)
        load_fact_diagnosis(session)
        load_fact_scale_response(session)

        print(f"ETL complete: {p_count} patients, {c_count} consultations loaded to DW")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    run_full_etl()
