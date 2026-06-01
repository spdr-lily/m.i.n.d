import apiClient from './client'
import type { InferenceRequest, InferenceResponse, BayesianInferenceRequest, BayesianResult } from '../types'

export const inferencesApi = {
  runCriteria: (data: InferenceRequest) =>
    apiClient.post<InferenceResponse>('/inferences/run', data).then((r) => r.data),

  runBayesian: (data: BayesianInferenceRequest) =>
    apiClient.post<BayesianResult[]>('/inferences/bayesian', data).then((r) => r.data),
}
