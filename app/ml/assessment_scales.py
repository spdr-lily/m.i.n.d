from typing import Dict, List, Tuple, Optional, Protocol

SCORE_OPTIONS = [0, 1, 2, 3]


def _clamp(value: float, max_value: float = 3.0) -> float:
    return max(0.0, min(float(value), max_value))


class ScaleDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        questions: List[str],
        severity_thresholds: List[Tuple[float, str, str]],
        max_score_per_item: float = 3.0,
    ):
        self.name = name
        self.description = description
        self.questions = questions
        self.severity_thresholds = sorted(severity_thresholds, key=lambda t: t[0])
        self.max_score_per_item = max_score_per_item

    def score(self, responses: List[float]) -> float:
        if not responses:
            return 0.0
        total = sum(_clamp(r, self.max_score_per_item) for r in responses[: len(self.questions)])
        return total

    def interpret(self, total_score: float) -> Tuple[str, str]:
        for threshold, severity, interpretation in reversed(self.severity_thresholds):
            if total_score >= threshold:
                return severity, interpretation
        return self.severity_thresholds[0][1], self.severity_thresholds[0][2]


PHQ9 = ScaleDefinition(
    name="PHQ-9",
    description="Patient Health Questionnaire-9 — screening tool for depression",
    questions=[
        "Little interest or pleasure in doing things",
        "Feeling down, depressed, or hopeless",
        "Trouble falling/staying asleep or sleeping too much",
        "Feeling tired or having little energy",
        "Poor appetite or overeating",
        "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
        "Trouble concentrating on things, such as reading the newspaper or watching television",
        "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
        "Thoughts that you would be better off dead or of hurting yourself in some way",
    ],
    severity_thresholds=[
        (0, "None-minimal", "No significant depressive symptoms."),
        (5, "Mild", "Mild depressive symptoms. Consider watchful waiting and repeat PHQ-9 at follow-up."),
        (10, "Moderate", "Moderate depressive symptoms. Recommend further evaluation and possible treatment."),
        (15, "Moderately severe", "Moderately severe depression. Active treatment recommended (pharmacotherapy and/or psychotherapy)."),
        (20, "Severe", "Severe depression. Immediate initiation of pharmacotherapy and psychotherapy; consider specialist referral."),
    ],
)


GAD7 = ScaleDefinition(
    name="GAD-7",
    description="Generalized Anxiety Disorder-7 — screening tool for anxiety",
    questions=[
        "Feeling nervous, anxious, or on edge",
        "Not being able to stop or control worrying",
        "Worrying too much about different things",
        "Trouble relaxing",
        "Being so restless that it is hard to sit still",
        "Becoming easily annoyed or irritable",
        "Feeling afraid as if something awful might happen",
    ],
    severity_thresholds=[
        (0, "None-minimal", "No significant anxiety symptoms."),
        (5, "Mild", "Mild anxiety. Consider monitoring and psychosocial interventions."),
        (10, "Moderate", "Moderate anxiety. Further evaluation recommended; consider pharmacotherapy and/or psychotherapy."),
        (15, "Severe", "Severe anxiety. Active treatment strongly recommended; consider specialist referral."),
    ],
)


MADRS = ScaleDefinition(
    name="MADRS",
    description="Montgomery-Åsberg Depression Rating Scale — clinician-rated depression severity",
    max_score_per_item=6.0,
    questions=[
        "Apparent sadness — representing despondency, gloom and despair (less than occasional)",
        "Reported sadness — representing reports of depressed mood regardless of whether it is reflected in appearance",
        "Inner tension — representing feelings of ill-defined discomfort, edginess, inner turmoil",
        "Reduced sleep — representing reduced duration or depth of sleep compared with the patient's normal pattern",
        "Reduced appetite — representing feeling of loss of appetite compared with earlier habits",
        "Concentration difficulties — representing difficulties in collecting thoughts",
        "Lassitude — representing difficulty getting started or slowness initiating and performing everyday activities",
        "Inability to feel — representing reduced interest in surroundings or activities",
        "Pessimistic thoughts — representing guilt, inferiority, self-reproach, sinfulness, ruin",
        "Suicidal thoughts — representing feeling that life is not worth living, that death is welcome",
    ],
    severity_thresholds=[
        (0, "Absent", "No depressive symptoms detected."),
        (7, "Mild", "Mild depression. Clinical monitoring recommended."),
        (20, "Moderate", "Moderate depression. Pharmacotherapy and/or psychotherapy recommended."),
        (35, "Severe", "Severe depression. Urgent initiation of antidepressant therapy and specialist follow-up."),
    ],
)


SCALES_REGISTRY: Dict[str, ScaleDefinition] = {
    "PHQ-9": PHQ9,
    "GAD-7": GAD7,
    "MADRS": MADRS,
}


def get_scale(name: str) -> Optional[ScaleDefinition]:
    return SCALES_REGISTRY.get(name)


def list_scales() -> Dict[str, str]:
    return {name: scale.description for name, scale in SCALES_REGISTRY.items()}
