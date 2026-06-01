import apiClient from './client'
import type { MetricsOverview, ScaleTrend, CorrelationData } from '../types'

export const metricsApi = {
  overview: () =>
    apiClient.get<MetricsOverview>('/metrics/overview').then((r) => r.data),

  scaleTrends: (scaleName: string) =>
    apiClient.get<ScaleTrend[]>(`/metrics/scales/${scaleName}/trends`).then((r) => r.data),

  correlations: () =>
    apiClient.get<CorrelationData[]>('/metrics/correlations').then((r) => r.data),
}
