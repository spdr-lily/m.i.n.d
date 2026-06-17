import apiClient from './client'
import type {
  PrevalenceTrendResponse,
  ComorbidityResponse,
  ScoreDistributionResponse,
  ScaleSeverityResponse,
  ProfessionalWorkloadResponse,
  DemographicSummaryResponse,
  MonthlyConsultationResponse,
} from '../types'

export const analyticsApi = {
  prevalenceTrends: (months = 12, topN = 10) =>
    apiClient.get<PrevalenceTrendResponse>('/analytics/prevalence-trends', { params: { months, top_n: topN } }).then((r) => r.data),

  comorbidity: (topN = 15) =>
    apiClient.get<ComorbidityResponse>('/analytics/comorbidity', { params: { top_n: topN } }).then((r) => r.data),

  scoreDistributions: () =>
    apiClient.get<ScoreDistributionResponse>('/analytics/score-distributions').then((r) => r.data),

  scaleSeverity: () =>
    apiClient.get<ScaleSeverityResponse>('/analytics/scale-severity').then((r) => r.data),

  patientSummary: (limit = 50) =>
    apiClient.get<any>('/analytics/patient-summary', { params: { limit } }).then((r) => r.data),

  professionalWorkload: () =>
    apiClient.get<ProfessionalWorkloadResponse>('/analytics/professional-workload').then((r) => r.data),

  demographicSummary: () =>
    apiClient.get<DemographicSummaryResponse>('/analytics/demographic-summary').then((r) => r.data),

  monthlyConsultations: (months = 12) =>
    apiClient.get<MonthlyConsultationResponse>('/analytics/monthly-consultations', { params: { months } }).then((r) => r.data),
}
