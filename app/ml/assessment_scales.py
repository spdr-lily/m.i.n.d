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


MDQ = ScaleDefinition(
    name="MDQ",
    description="Mood Disorder Questionnaire — screening for bipolar spectrum disorder",
    max_score_per_item=1.0,
    questions=[
        "Felt so good or so hyper that other people thought you were not normal?",
        "Felt so irritable that you shouted at people or started fights?",
        "Felt much more self-confident than usual?",
        "Got much less sleep than usual and did not feel tired?",
        "Was much more talkative or spoke faster than usual?",
        "Thoughts raced through your head?",
        "Were easily distracted by unimportant things?",
        "Had much more energy than usual?",
        "Was much more active or did many things at once?",
        "Was much more social or outgoing than usual?",
        "Was much more interested in sex than usual?",
        "Did things that could have caused trouble (spending, sex, investments)?",
        "Spent money that caused financial problems?",
    ],
    severity_thresholds=[
        (0, "Negative", "No indication of bipolar spectrum disorder."),
        (7, "Positive", "Positive screen for bipolar spectrum disorder. Comprehensive diagnostic evaluation recommended."),
    ],
)


PCL5 = ScaleDefinition(
    name="PCL-5",
    description="PTSD Checklist for DSM-5 — trauma exposure symptoms",
    max_score_per_item=4.0,
    questions=[
        "Repeated upsetting memories of the stressful event?",
        "Repeated distressing dreams about the event?",
        "Suddenly feeling or acting as if the event were happening again?",
        "Feeling very upset when something reminded you of the event?",
        "Having strong physical reactions when reminded of the event?",
        "Avoiding memories, thoughts, or feelings about the event?",
        "Avoiding external reminders of the event?",
        "Trouble remembering important parts of the event?",
        "Having strong negative beliefs about yourself or the world?",
        "Blaming yourself or others for the event?",
        "Having strong negative feelings (fear, guilt, shame)?",
        "Loss of interest in activities you used to enjoy?",
        "Feeling distant or cut off from others?",
        "Trouble experiencing positive feelings?",
        "Irritable or aggressive behavior?",
        "Reckless or self-destructive behavior?",
        "Being overly alert or watchful?",
        "Being jumpy or easily startled?",
        "Trouble concentrating?",
        "Trouble falling or staying asleep?",
    ],
    severity_thresholds=[
        (0, "None", "No clinically significant PTSD symptoms."),
        (31, "Mild", "Mild PTSD symptoms. Monitor and consider psychotherapy."),
        (45, "Moderate", "Moderate PTSD symptoms. Evidence-based psychotherapy (CBT, EMDR) recommended."),
        (56, "Severe", "Severe PTSD symptoms. Intensive treatment and specialist referral recommended."),
    ],
)


YBOCS = ScaleDefinition(
    name="Y-BOCS",
    description="Yale-Brown Obsessive Compulsive Scale — OCD severity",
    max_score_per_item=4.0,
    questions=[
        "Time spent on obsessive thoughts?",
        "Interference from obsessive thoughts?",
        "Distress from obsessive thoughts?",
        "Resistance against obsessive thoughts?",
        "Control over obsessive thoughts?",
        "Time spent on compulsive behaviors?",
        "Interference from compulsive behaviors?",
        "Distress when prevented from performing compulsions?",
        "Resistance against compulsions?",
        "Control over compulsions?",
    ],
    severity_thresholds=[
        (0, "None", "No clinically significant OCD symptoms."),
        (8, "Mild", "Mild OCD symptoms. Consider monitoring and CBT."),
        (16, "Moderate", "Moderate OCD severity. CBT/ERP and pharmacotherapy recommended."),
        (24, "Severe", "Severe OCD symptoms. Intensive treatment and specialist referral."),
        (32, "Extreme", "Extreme OCD symptoms. Urgent intensive treatment required."),
    ],
)


AUDIT = ScaleDefinition(
    name="AUDIT",
    description="Alcohol Use Disorders Identification Test — alcohol consumption screening",
    max_score_per_item=4.0,
    questions=[
        "How often do you have a drink containing alcohol?",
        "How many drinks do you have on a typical day?",
        "How often do you have six or more drinks on one occasion?",
        "How often have you found you could not stop drinking once started?",
        "How often have you failed to do what was expected because of drinking?",
        "How often have you needed a drink in the morning to get going?",
        "How often have you felt guilt or remorse after drinking?",
        "How often have you been unable to remember the night before?",
        "Has someone been injured because of your drinking?",
        "Has a relative, friend, or doctor suggested you cut down?",
    ],
    severity_thresholds=[
        (0, "Low risk", "Low-risk alcohol use. Maintain current pattern."),
        (8, "Hazardous", "Hazardous alcohol use. Brief intervention and advice recommended."),
        (16, "Harmful", "Harmful alcohol use. Diagnostic evaluation and intervention required."),
        (20, "Dependence", "Possible alcohol dependence. Specialist assessment and treatment recommended."),
    ],
)


ASRM = ScaleDefinition(
    name="ASRM",
    description="Altman Self-Rating Mania Scale — manic symptom screening",
    max_score_per_item=4.0,
    questions=[
        "Happier or more cheerful than usual?",
        "More self-confident than usual?",
        "Slept less than usual without feeling tired?",
        "Talked more than usual?",
        "Was so active that others found it unusual?",
    ],
    severity_thresholds=[
        (0, "None", "No manic symptoms detected."),
        (6, "Possible hypomania/mania", "Elevated score suggesting possible manic or hypomanic episode. Further evaluation recommended."),
        (10, "Probable mania", "Highly suggestive of current manic episode. Immediate psychiatric evaluation recommended."),
    ],
)


SCALES_REGISTRY: Dict[str, ScaleDefinition] = {
    "PHQ-9": PHQ9,
    "GAD-7": GAD7,
    "MADRS": MADRS,
    "MDQ": MDQ,
    "PCL-5": PCL5,
    "Y-BOCS": YBOCS,
    "AUDIT": AUDIT,
    "ASRM": ASRM,
}


def get_scale(name: str) -> Optional[ScaleDefinition]:
    return SCALES_REGISTRY.get(name)


def list_scales() -> Dict[str, str]:
    return {name: scale.description for name, scale in SCALES_REGISTRY.items()}
