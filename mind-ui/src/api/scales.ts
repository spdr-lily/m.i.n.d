import apiClient from './client'
import type { AssessmentScale, ScaleScoreRequest, ScaleScoreResponse, ScaleHistoryItem } from '../types'

export const scalesApi = {
  list: () =>
    apiClient.get<AssessmentScale[]>('/scales').then((r) => r.data),

  get: (name: string) =>
    apiClient.get<AssessmentScale>(`/scales/${name}`).then((r) => r.data),

  score: (data: ScaleScoreRequest) =>
    apiClient.post<ScaleScoreResponse>('/assessments/score', data).then((r) => r.data),

  history: (patientUuid: string, scaleName: string) =>
    apiClient
      .get<ScaleHistoryItem[]>('/assessments/history', { params: { patient_uuid: patientUuid, scale_name: scaleName } })
      .then((r) => r.data),
}
