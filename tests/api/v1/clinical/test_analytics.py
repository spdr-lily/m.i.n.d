import pytest
from unittest.mock import patch
from uuid import uuid4


class TestAnalyticsAPI:
    BASE = "/api/v1/analytics"

    def _mock_service(self, return_value):
        return patch("app.api.v1.clinical.analytics.DWAnalyticsService")

    def test_prevalence_trends_invalid_months(self, client):
        resp = client.get(f"{self.BASE}/prevalence-trends?months=0")
        assert resp.status_code == 422

    def test_prevalence_trends_invalid_top_n(self, client):
        resp = client.get(f"{self.BASE}/prevalence-trends?top_n=2")
        assert resp.status_code == 422

    def test_comorbidity_invalid_top_n(self, client):
        resp = client.get(f"{self.BASE}/comorbidity?top_n=1")
        assert resp.status_code == 422

    def test_patient_summary_invalid_limit(self, client):
        resp = client.get(f"{self.BASE}/patient-summary?limit=0")
        assert resp.status_code == 422

    def test_patient_summary_limit_too_high(self, client):
        resp = client.get(f"{self.BASE}/patient-summary?limit=201")
        assert resp.status_code == 422

    def test_monthly_consultations_invalid_months(self, client):
        resp = client.get(f"{self.BASE}/monthly-consultations?months=0")
        assert resp.status_code == 422

    def test_mocked_prevalence_trends_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_prevalence_trends.return_value = {
                "disorders": [
                    {
                        "disorder_name": "TAG",
                        "data": [{"month": "2026-01", "count": 5, "avg_probability": 0.85}],
                        "total": 5,
                    }
                ],
                "total": 1,
            }
            resp = client.get(f"{self.BASE}/prevalence-trends")
            assert resp.status_code == 200
            data = resp.json()
            assert "disorders" in data
            assert data["total"] == 1
            assert data["disorders"][0]["disorder_name"] == "TAG"

    def test_mocked_comorbidity_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_comorbidity_pairs.return_value = {
                "pairs": [{"disorder_a": "TAG", "disorder_b": "TDM", "co_occurrence_count": 3, "prevalence_pct": 15.0}],
                "total_pairs": 1,
            }
            resp = client.get(f"{self.BASE}/comorbidity")
            assert resp.status_code == 200
            data = resp.json()
            assert "pairs" in data
            assert data["total_pairs"] == 1

    def test_mocked_score_distributions_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_score_distributions.return_value = {
                "scales": [{"scale_name": "PHQ-9", "total_responses": 50, "mean_score": 12.5}],
            }
            resp = client.get(f"{self.BASE}/score-distributions")
            assert resp.status_code == 200
            data = resp.json()
            assert "scales" in data

    def test_mocked_scale_severity_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_scale_severity_distribution.return_value = {
                "scales": [{"scale_name": "PHQ-9", "severity_levels": [{"severity": "moderate", "count": 10, "avg_score": 15.0}]}],
            }
            resp = client.get(f"{self.BASE}/scale-severity")
            assert resp.status_code == 200
            data = resp.json()
            assert "scales" in data

    def test_mocked_patient_summary_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_patient_summary.return_value = {"patients": [{"patient_uuid": str(uuid4())}], "total": 1}
            resp = client.get(f"{self.BASE}/patient-summary")
            assert resp.status_code == 200
            data = resp.json()
            assert "patients" in data

    def test_mocked_professional_workload_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_professional_workload.return_value = {"professionals": [{"full_name": "Dr. Silva"}], "total": 1}
            resp = client.get(f"{self.BASE}/professional-workload")
            assert resp.status_code == 200
            data = resp.json()
            assert "professionals" in data

    def test_mocked_demographic_summary_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_demographic_summary.return_value = {"demographics": [{"age_group": "30-39"}], "total": 1}
            resp = client.get(f"{self.BASE}/demographic-summary")
            assert resp.status_code == 200
            data = resp.json()
            assert "demographics" in data

    def test_mocked_monthly_consultations_returns_structure(self, client):
        with patch("app.api.v1.clinical.analytics.DWAnalyticsService") as MockService:
            instance = MockService.return_value
            instance.get_monthly_consultation_stats.return_value = {
                "months": [{"year_month": "2026-01", "total_consultations": 10}],
                "total_months": 1,
            }
            resp = client.get(f"{self.BASE}/monthly-consultations")
            assert resp.status_code == 200
            data = resp.json()
            assert "months" in data
