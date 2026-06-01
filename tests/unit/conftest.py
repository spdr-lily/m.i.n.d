from datetime import datetime, timedelta
from uuid import uuid4
from typing import List
from dataclasses import dataclass, field
import pytest


@dataclass
class MockSymptomObservation:
    observation_id: int
    consultation_uuid: str
    symptom_id: int
    intensity: float
    frequency: str
    duration_days: int
    clinical_notes: str


@dataclass
class MockDiagnosticCriteria:
    criteria_id: int
    disorder_id: int
    symptom_id: int
    required_presence: bool
    minimum_duration_days: int
    clinical_notes: str


@dataclass
class MockDisorder:
    disorder_id: int
    disorder_name: str
    cid_code: str
    dsm_code: str


@dataclass
class MockDiagnosisRelationship:
    relationship_id: int
    source_disorder_id: int
    target_disorder_id: int
    relationship_type: str
    relationship_weight: float
    clinical_description: str


@pytest.fixture
def mdd_criteria() -> List[MockDiagnosticCriteria]:
    return [
        MockDiagnosticCriteria(1, 1, 1, True, 14, "Depressed mood most of the day"),
        MockDiagnosticCriteria(2, 1, 2, True, 14, "Markedly diminished interest or pleasure"),
        MockDiagnosticCriteria(3, 1, 3, False, 14, "Weight loss or decreased appetite"),
        MockDiagnosticCriteria(4, 1, 4, False, 14, "Insomnia or hypersomnia"),
        MockDiagnosticCriteria(5, 1, 5, False, 14, "Psychomotor agitation or retardation"),
        MockDiagnosticCriteria(6, 1, 6, False, 14, "Fatigue or loss of energy"),
        MockDiagnosticCriteria(7, 1, 7, False, 14, "Feelings of worthlessness or guilt"),
        MockDiagnosticCriteria(8, 1, 8, False, 14, "Diminished concentration"),
        MockDiagnosticCriteria(9, 1, 9, False, 14, "Recurrent thoughts of death"),
    ]


@pytest.fixture
def bipolar_criteria() -> List[MockDiagnosticCriteria]:
    return [
        MockDiagnosticCriteria(10, 2, 10, True, 7, "Inflated self-esteem or grandiosity"),
        MockDiagnosticCriteria(11, 2, 11, True, 7, "Decreased need for sleep"),
        MockDiagnosticCriteria(12, 2, 12, False, 7, "Pressured speech"),
        MockDiagnosticCriteria(13, 2, 13, False, 7, "Flight of ideas"),
        MockDiagnosticCriteria(14, 2, 14, False, 7, "Distractibility"),
        MockDiagnosticCriteria(15, 2, 15, False, 7, "Increased goal-directed activity"),
        MockDiagnosticCriteria(16, 2, 16, False, 7, "Risky behavior"),
    ]


@pytest.fixture
def gad_criteria() -> List[MockDiagnosticCriteria]:
    return [
        MockDiagnosticCriteria(17, 3, 17, True, 180, "Excessive anxiety and worry"),
        MockDiagnosticCriteria(18, 3, 18, False, 180, "Restlessness or feeling keyed up"),
        MockDiagnosticCriteria(19, 3, 19, False, 180, "Being easily fatigued"),
        MockDiagnosticCriteria(20, 3, 20, False, 180, "Difficulty concentrating"),
        MockDiagnosticCriteria(21, 3, 21, False, 180, "Irritability"),
        MockDiagnosticCriteria(22, 3, 22, False, 180, "Muscle tension"),
        MockDiagnosticCriteria(23, 3, 23, False, 180, "Sleep disturbance"),
    ]


@pytest.fixture
def mdd_symptoms_positive() -> List[MockSymptomObservation]:
    return [
        MockSymptomObservation(1, str(uuid4()), 1, 8.0, "daily", 21, "Patient reports persistent sadness"),
        MockSymptomObservation(2, str(uuid4()), 2, 7.0, "daily", 21, "Lost interest in hobbies"),
        MockSymptomObservation(3, str(uuid4()), 4, 8.0, "daily", 21, "Sleeps 3-4 hours per night"),
        MockSymptomObservation(4, str(uuid4()), 5, 6.0, "daily", 18, "Noticeable slowing of movement"),
        MockSymptomObservation(5, str(uuid4()), 6, 9.0, "daily", 21, "Constant fatigue"),
        MockSymptomObservation(6, str(uuid4()), 8, 6.0, "daily", 18, "Cannot focus at work"),
    ]


@pytest.fixture
def mdd_symptoms_partial() -> List[MockSymptomObservation]:
    return [
        MockSymptomObservation(7, str(uuid4()), 1, 5.0, "daily", 10, "Mild depressed mood"),
        MockSymptomObservation(8, str(uuid4()), 6, 7.0, "daily", 10, "Feeling tired"),
    ]


@pytest.fixture
def bipolar_symptoms_positive() -> List[MockSymptomObservation]:
    return [
        MockSymptomObservation(9, str(uuid4()), 10, 9.0, "daily", 10, "Believes has special powers"),
        MockSymptomObservation(10, str(uuid4()), 11, 8.0, "daily", 10, "Sleeps 2 hours, feels rested"),
        MockSymptomObservation(11, str(uuid4()), 12, 7.0, "daily", 10, "Talks rapidly, cannot be interrupted"),
        MockSymptomObservation(12, str(uuid4()), 13, 8.0, "daily", 10, "Racing thoughts"),
        MockSymptomObservation(13, str(uuid4()), 15, 9.0, "daily", 10, "Started multiple projects simultaneously"),
    ]


@pytest.fixture
def mdd_exclusion_relationship() -> List[MockDiagnosisRelationship]:
    return [
        MockDiagnosisRelationship(
            1, 1, 2, "exclusion", 0.0,
            "MDD cannot be diagnosed during manic episode"
        ),
    ]


@pytest.fixture
def mdd_gad_comorbidity() -> List[MockDiagnosisRelationship]:
    return [
        MockDiagnosisRelationship(
            2, 1, 3, "comorbidity", 0.3,
            "MDD and GAD frequently co-occur"
        ),
    ]


@pytest.fixture
def disorders() -> List[MockDisorder]:
    return [
        MockDisorder(1, "Major Depressive Disorder", "F32.1", "296.22"),
        MockDisorder(2, "Bipolar I Disorder", "F31.2", "296.42"),
        MockDisorder(3, "Generalized Anxiety Disorder", "F41.1", "300.02"),
    ]
