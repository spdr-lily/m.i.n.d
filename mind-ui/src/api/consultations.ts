import apiClient from './client'
import type { ConsultationCreate, ConsultationResponse } from '../types'

export const consultationsApi = {
  list: (patient_uuid?: string, page = 1, size = 20) =>
    apiClient
      .get<{ total: number; consultations: ConsultationResponse[] }>('/consultations', {
        params: { patient_uuid, page, size },
      })
      .then((r) => r.data),

  get: (uuid: string) =>
    apiClient.get<ConsultationResponse>(`/consultations/${uuid}`).then((r) => r.data),

  create: (data: ConsultationCreate) =>
    apiClient.post<ConsultationResponse>('/consultations', data).then((r) => r.data),
}
