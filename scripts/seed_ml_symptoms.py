"""Seed English symptom names used by ML pipeline and Bayesian network."""
from app.core.database import SessionLocal
from app.models.base import Symptom, Disorder, DiagnosticCriteria
from sqlalchemy import text

ML_SYMPTOMS = [
    ("depressed_mood", "Depressed mood most of the day"),
    ("loss_of_interest", "Loss of interest or pleasure"),
    ("sleep_disturbance", "Sleep disturbance"),
    ("fatigue", "Fatigue or loss of energy"),
    ("appetite_changes", "Appetite or weight changes"),
    ("guilt_feelings", "Feelings of worthlessness or guilt"),
    ("concentration_problems", "Diminished concentration"),
    ("psychomotor_changes", "Psychomotor changes"),
    ("suicidal_ideation", "Suicidal ideation"),
    ("excessive_worry", "Excessive anxiety and worry"),
    ("restlessness", "Restlessness"),
    ("fatigue_gad", "Fatigue easily"),
    ("muscle_tension", "Muscle tension"),
    ("sleep_disturbance_gad", "Sleep disturbance (GAD)"),
    ("irritability", "Irritability"),
    ("concentration_difficulty_gad", "Difficulty concentrating (GAD)"),
    ("panic_attacks", "Recurrent unexpected panic attacks"),
    ("palpitations", "Palpitations"),
    ("chest_pain", "Chest pain or discomfort"),
    ("shortness_of_breath", "Shortness of breath"),
    ("fear_of_dying", "Fear of dying"),
    ("derealization", "Derealization"),
    ("avoidance_behavior", "Avoidance of situations"),
    ("traumatic_exposure", "Exposure to traumatic event"),
    ("intrusive_memories", "Intrusive memories"),
    ("nightmares", "Nightmares"),
    ("hypervigilance", "Hypervigilance"),
    ("avoidance_ptsd", "Avoidance of reminders"),
    ("negative_cognitions", "Negative cognitions"),
    ("startle_response", "Exaggerated startle response"),
    ("chronic_low_mood", "Chronic low mood"),
    ("poor_appetite_dysthymia", "Poor appetite (dysthymia)"),
    ("low_self_esteem", "Low self-esteem"),
    ("hopelessness", "Hopelessness"),
    ("low_energy_dysthymia", "Low energy (dysthymia)"),
    ("social_fear", "Fear of social situations"),
    ("avoidance_social", "Avoidance of social situations"),
    ("performance_anxiety", "Performance anxiety"),
    ("blushing", "Blushing"),
    ("euphoric_mood", "Euphoric or elevated mood"),
    ("increased_energy", "Increased energy"),
    ("grandiosity", "Inflated self-esteem"),
    ("decreased_sleep", "Decreased need for sleep"),
    ("rapid_speech", "Rapid or pressured speech"),
    ("racing_thoughts", "Racing thoughts"),
    ("distractibility", "Distractibility"),
    ("risk_behavior", "Risk-taking behavior"),
    ("hypomanic_mood", "Hypomanic mood"),
    ("mildly_increased_energy", "Mildly increased energy"),
    ("reduced_sleep_hypomania", "Reduced sleep need"),
    ("obsessions", "Recurrent obsessions"),
    ("compulsions", "Repetitive compulsions"),
    ("repetitive_behavior", "Repetitive behaviors"),
    ("intrusive_thoughts", "Intrusive thoughts"),
]


def seed():
    db = SessionLocal()
    try:
        count = 0
        for name, desc in ML_SYMPTOMS:
            existing = db.query(Symptom).filter_by(symptom_name=name).first()
            if not existing:
                db.add(Symptom(symptom_name=name, symptom_description=desc))
                count += 1
        db.commit()
        print(f"OK - {count} ML symptoms seeded")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
