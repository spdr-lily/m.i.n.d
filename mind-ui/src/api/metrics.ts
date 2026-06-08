import apiClient from './client'
import type {
  MetricsOverview,
  ScaleTrend,
  CorrelationData,
  DemographicsResponse,
  ConsultationMetricsResponse,
  DisorderPrevalenceItem,
  ScaleDistributionResponse,
} from '../types'

export const metricsApi = {
  overview: () =>
    apiClient.get<MetricsOverview>('/metrics/overview').then((r) => r.data),

  demographics: () =>
    apiClient.get<DemographicsResponse>('/metrics/demographics').then((r) => r.data),

  consultationMetrics: (days = 30) =>
    apiClient.get<ConsultationMetricsResponse>('/metrics/consultations', { params: { days } }).then((r) => r.data),

  disorderPrevalence: (topN = 10) =>
    apiClient.get<DisorderPrevalenceItem[]>('/metrics/disorders', { params: { top_n: topN } }).then((r) => r.data),

  scaleDistribution: (scaleName: string) =>
    apiClient.get<ScaleDistributionResponse>(`/metrics/scales/${scaleName}`).then((r) => r.data),

  scaleTrends: (scaleName: string, days = 90) =>
    apiClient.get<ScaleTrend[]>(`/metrics/scales/${scaleName}/trends`, { params: { days } }).then((r) => r.data),

  correlations: () =>
    apiClient.get<CorrelationData[]>('/metrics/correlations').then((r) => r.data),
}
