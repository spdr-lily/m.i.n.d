import sys
sys.path.insert(0, '.')
from scripts.seed_clinical_data import EN_TO_PT_SYMPTOM

keys = [
    'distracted', 'chronic_low_mood', 'poor_appetite_dysthymia',
    'low_self_esteem', 'hopelessness', 'low_energy_dysthymia',
    'social_fear', 'avoidance_social', 'performance_anxiety', 'blushing',
    'hypomanic_mood', 'mildly_increased_energy', 'reduced_sleep_hypomania',
]
for k in keys:
    val = EN_TO_PT_SYMPTOM.get(k)
    print(f'{k}: {val if val else "MISSING"}')
