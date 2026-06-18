import pytest
from app.ml.models.assessment_scales import (
    PHQ9,
    GAD7,
    MADRS,
    get_scale,
    list_scales,
    SCALES_REGISTRY,
)
from app.services.assessment_service import score_assessment
from app.schemas.assessment import ScoreRequest


class TestPHQ9:
    def test_score_phq9_none_minimal(self):
        total = PHQ9.score([0, 0, 0, 0, 0, 0, 0, 0, 0])
        severity, interpretation = PHQ9.interpret(total)
        assert total == 0
        assert severity == "Mínimo"

    def test_score_phq9_mild(self):
        total = PHQ9.score([1, 1, 0, 1, 0, 1, 0, 1, 0])
        severity, interpretation = PHQ9.interpret(total)
        assert total == 5
        assert severity == "Leve"

    def test_score_phq9_moderate(self):
        total = PHQ9.score([2, 2, 1, 2, 1, 1, 0, 1, 0])
        severity, interpretation = PHQ9.interpret(total)
        assert total == 10
        assert severity == "Moderado"

    def test_score_phq9_severe(self):
        total = PHQ9.score([3, 3, 3, 3, 2, 3, 2, 3, 3])
        severity, interpretation = PHQ9.interpret(total)
        assert total == 25
        assert severity == "Grave"

    def test_score_phq9_empty(self):
        assert PHQ9.score([]) == 0

    def test_score_phq9_partial(self):
        total = PHQ9.score([2, 3, 1])
        severity, interpretation = PHQ9.interpret(total)
        assert total == 6
        assert severity == "Leve"

    def test_score_phq9_clamps_negative(self):
        total = PHQ9.score([-5, 5, 0, 0, 0, 0, 0, 0, 0])
        assert total == 3

    def test_score_phq9_excessive_responses(self):
        total = PHQ9.score([1] * 20)
        assert total == 9


class TestGAD7:
    def test_score_gad7_none(self):
        total = GAD7.score([0] * 7)
        severity, interpretation = GAD7.interpret(total)
        assert total == 0
        assert severity == "Mínimo"

    def test_score_gad7_moderate(self):
        total = GAD7.score([2, 2, 1, 2, 1, 1, 1])
        severity, interpretation = GAD7.interpret(total)
        assert total == 10
        assert severity == "Moderado"

    def test_score_gad7_severe(self):
        total = GAD7.score([3, 3, 2, 3, 2, 3, 2])
        severity, interpretation = GAD7.interpret(total)
        assert total == 18
        assert severity == "Grave"


class TestMADRS:
    def test_score_madrs_absent(self):
        total = MADRS.score([0] * 10)
        severity, interpretation = MADRS.interpret(total)
        assert total == 0
        assert severity == "Ausente"

    def test_score_madrs_moderate(self):
        total = MADRS.score([3, 2, 3, 3, 2, 3, 2, 1, 1, 0])
        severity, interpretation = MADRS.interpret(total)
        assert total == 20
        assert severity == "Moderado"

    def test_score_madrs_severe(self):
        total = MADRS.score([5, 4, 4, 5, 4, 4, 3, 3, 3, 4])
        severity, interpretation = MADRS.interpret(total)
        assert total == 39
        assert severity == "Grave"


class TestScaleRegistry:
    def test_get_scale_exists(self):
        assert get_scale("PHQ-9") is PHQ9
        assert get_scale("GAD-7") is GAD7
        assert get_scale("MADRS") is MADRS

    def test_get_scale_unknown(self):
        assert get_scale("Unknown") is None

    def test_list_scales(self):
        scales = list_scales()
        assert "PHQ-9" in scales
        assert "GAD-7" in scales
        assert "MADRS" in scales
        assert len(scales) == len(SCALES_REGISTRY)


class TestAssessmentService:
    def test_score_assessment_phq9_mild(self):
        request = ScoreRequest(
            scale_name="PHQ-9",
            responses=[1] * 9,
        )
        result = score_assessment(request)
        assert result.scale_name == "PHQ-9"
        assert result.total_score == 9
        assert result.severity == "Leve"
        assert result.interpretation != ""

    def test_score_assessment_gad7_severe(self):
        request = ScoreRequest(
            scale_name="GAD-7",
            responses=[3] * 7,
        )
        result = score_assessment(request)
        assert result.scale_name == "GAD-7"
        assert result.total_score == 21
        assert result.severity == "Grave"

    def test_score_assessment_unknown_scale(self):
        import pytest

        request = ScoreRequest(
            scale_name="FAKE",
            responses=[1],
        )
        with pytest.raises(ValueError, match="Unknown scale"):
            score_assessment(request)

    def test_score_assessment_empty_responses(self):
        request = ScoreRequest(
            scale_name="PHQ-9",
            responses=[],
        )
        result = score_assessment(request)
        assert result.total_score == 0
        assert result.severity == "Mínimo"
