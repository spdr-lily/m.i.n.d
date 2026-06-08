import apiClient from './client'
import type {
  AssessmentScale, ScaleScoreRequest, ScaleScoreResponse, ScaleHistoryItem,
  ScaleCreateRequest, ScaleUpdateRequest, ScaleQuestionCreateRequest,
  ScaleQuestionUpdateRequest, PaginatedScales, PaginatedQuestions, ScaleQuestion,
} from '../types'

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

  history: (patientUuid: string, scaleName: string) =>
    apiClient
      .get<ScaleHistoryItem[]>('/assessments/history', { params: { patient_uuid: patientUuid, scale_name: scaleName } })
      .then((r) => r.data),

  patientHistory: (patientUuid: string) =>
    apiClient
      .get<{ total: number; assessments: { scale_name: string; consultation_uuid: string; date: string; total_score: number }[] }>(`/assessments/patient/${patientUuid}/history`)
      .then((r) => r.data),
}
