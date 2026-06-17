import apiClient from './client'
import type {
  AssessmentScale, ScaleScoreRequest, ScaleScoreResponse, ScaleHistoryItem,
  ScaleCreateRequest, ScaleUpdateRequest, ScaleQuestionCreateRequest,
  ScaleQuestionUpdateRequest, PaginatedScales, PaginatedQuestions, ScaleQuestion,
  PersonalityFactorsResponse, DisorderRiskRequest, DisorderRiskResponse,
} from '../types'

export const mlApi = {
  predictPersonality: (scaleScores: Record<string, number>) =>
    apiClient.post<{ bfp: Record<string, { score: number; max_possible: number }>; bfp_total: number; dt12: Record<string, { score: number; max_possible: number }>; dt12_total: number; ml_source: string }>('/ml/scales/predict-personality', { scale_scores: scaleScores }).then((r) => r.data),

  predictDisorderRisk: (data: DisorderRiskRequest) =>
    apiClient.post<DisorderRiskResponse>('/ml/scales/predict-disorder-risk', data).then((r) => r.data),

  predictPersonalityFromPatient: (patientUuid: string) =>
    apiClient.get<PersonalityFactorsResponse>(`/ml/scales/predict-personality-from-patient/${patientUuid}`).then((r) => r.data),

  listAvailableScales: () =>
    apiClient.get<{ clinical_scales: string[]; neuro_scales: string[]; total: number }>('/ml/scales/available-scales').then((r) => r.data),

  personalityFactors: (patientUuid: string) =>
    apiClient.get<PersonalityFactorsResponse>(`/assessments/patient/${patientUuid}/personality-factors`).then((r) => r.data),
}

export const scalesApi = {
  list: (skip = 0, limit = 100) =>
    apiClient
      .get<PaginatedScales>('/scales', { params: { skip, limit } })
      .then((r) => r.data),

  get: (scaleId: number) =>
    apiClient.get<AssessmentScale>(`/scales/${scaleId}`).then((r) => r.data),

  create: (data: ScaleCreateRequest) =>
    apiClient.post<AssessmentScale>('/scales', data).then((r) => r.data),

  update: (scaleId: number, data: ScaleUpdateRequest) =>
    apiClient.patch<AssessmentScale>(`/scales/${scaleId}`, data).then((r) => r.data),

  delete: (scaleId: number) =>
    apiClient.delete(`/scales/${scaleId}`),

  listQuestions: (scaleId: number) =>
    apiClient
      .get<PaginatedQuestions>(`/scales/${scaleId}/questions`)
      .then((r) => r.data),

  createQuestion: (scaleId: number, data: ScaleQuestionCreateRequest) =>
    apiClient.post<ScaleQuestion>(`/scales/${scaleId}/questions`, data).then((r) => r.data),

  updateQuestion: (questionId: number, data: ScaleQuestionUpdateRequest) =>
    apiClient.patch<ScaleQuestion>(`/scales/questions/${questionId}`, data).then((r) => r.data),

  deleteQuestion: (questionId: number) =>
    apiClient.delete(`/scales/questions/${questionId}`),

  score: (data: ScaleScoreRequest) =>
    apiClient.post<ScaleScoreResponse>('/assessments/score', data).then((r) => r.data),

  apply: (patientUuid: string, scaleName: string, responses: number[]) =>
    apiClient.post<ScaleScoreResponse & { consultation_uuid: string }>('/assessments/apply', { patient_uuid: patientUuid, scale_name: scaleName, responses }).then((r) => r.data),

  getDetail: (scaleName: string) =>
    apiClient.get<{ question_id: number; question_text: string; response_value: number }[]>(`/assessments/detail/${scaleName}`).then((r) => r.data),

  history: (patientUuid: string, scaleName: string) =>
    apiClient
      .get<ScaleHistoryItem[]>(`/assessments/patient/${patientUuid}/scale/${scaleName}`)
      .then((r) => r.data),

  patientHistory: (patientUuid: string) =>
    apiClient
      .get<{ total: number; assessments: { scale_name: string; consultation_uuid: string; date: string; total_score: number }[] }>(`/assessments/patient/${patientUuid}/history`)
      .then((r) => r.data),
}
