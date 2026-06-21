import apiClient from './client'
import type { InferenceRequest, InferenceResponse, BayesianInferenceRequest, DiagnosticInferenceResponse } from '../types'

export const inferencesApi = {
  runCriteria: (data: InferenceRequest) =>
    apiClient.post<InferenceResponse>('/inferences/run', data).then((r) => r.data),

  runBayesian: (data: BayesianInferenceRequest) =>
    apiClient.post<InferenceResponse>('/inferences/bayesian', data).then((r) => r.data),

  listByConsultation: (consultationUuid: string) =>
    apiClient.post<{ total: number; inferences: DiagnosticInferenceResponse[] }>('/inferences/list', { consultation_uuid: consultationUuid }).then((r) => r.data),
}
