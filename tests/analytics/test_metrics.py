import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from app.analytics.service import ConsultationMetricsService, BIService, DashboardService, StatisticsService
from app.services.alerts_service import AlertsService


class TestConsultationMetricsService:
    def test_general_stats_empty_db(self, db_session):
        service = ConsultationMetricsService(db_session)
        stats = service.get_general_stats()
        assert stats["total_patients"] == 0
        assert stats["total_consultations"] == 0
        assert stats["total_inferences"] == 0

    def test_consultation_metrics_empty(self, db_session):
        service = ConsultationMetricsService(db_session)
        metrics = service.get_consultation_metrics(days=30)
        assert metrics["total_consultations"] == 0
        assert metrics["period_days"] == 30


class TestStatisticsService:
    def test_patient_demographics_empty(self, db_session):
        service = StatisticsService(db_session)
        demo = service.get_patient_demographics()
        assert demo["total_patients"] == 0

    def test_scale_distribution_unknown(self, db_session):
        service = StatisticsService(db_session)
        dist = service.get_scale_score_distribution("UNKNOWN_SCALE")
        assert dist.get("total_assessments", 0) == 0


class TestBIService:
    def test_disorder_prevalence_empty(self, db_session):
        service = BIService(db_session)
        prevalence = service.get_disorder_prevalence()
        assert prevalence == []


class TestDashboardService:
    def test_patient_longitudinal_not_found(self, db_session):
        service = DashboardService(db_session)
        result = service.get_patient_longitudinal(uuid4())
        assert "error" in result


class TestAlertsService:
    def test_check_scale_thresholds_unknown_scale(self, db_session):
        service = AlertsService(db_session)
        alerts = service.check_scale_thresholds("UNKNOWN", 10)
        assert alerts == []

    def test_check_suicidal_ideation_empty(self, db_session):
        service = AlertsService(db_session)
        alerts = service.check_suicidal_ideation()
        assert alerts == []

    def test_check_missed_follow_up_empty(self, db_session):
        service = AlertsService(db_session)
        alerts = service.check_missed_follow_up()
        assert alerts == []

    def test_check_high_confidence_empty(self, db_session):
        service = AlertsService(db_session)
        alerts = service.check_high_confidence_deterioration()
        assert alerts == []

    def test_run_all_checks_empty(self, db_session):
        service = AlertsService(db_session)
        result = service.run_all_checks()
        assert result["total_alerts"] == 0
        for sev in ["critical", "high", "medium", "low"]:
            assert sev in result["by_severity"]
