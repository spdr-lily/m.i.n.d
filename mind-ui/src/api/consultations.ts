import apiClient from './client'
import type { ConsultationCreate, ConsultationResponse, ConsultationListItem, ClinicalNote, ConsultationCompleteness } from '../types'

export const consultationsApi = {
  list: (patient_uuid?: string, page = 1, size = 20) =>
    apiClient
      .get<{ total: number; consultations: ConsultationListItem[] }>('/consultations', {
        params: { patient_uuid, page, size },
      })
      .then((r) => r.data),

  get: (uuid: string) =>
    apiClient.get<ConsultationResponse>(`/consultations/${uuid}`).then((r) => r.data),

  create: (data: ConsultationCreate) =>
    apiClient.post<ConsultationResponse>('/consultations', data).then((r) => r.data),

  createWithData: (data: ConsultationCreate) =>
    apiClient.post<ConsultationResponse>('/consultations/with-data', data).then((r) => r.data),

  getClinicalNote: (uuid: string) =>
    apiClient.get<ClinicalNote>(`/consultations/${uuid}/clinical-note`).then((r) => r.data),

  updateClinicalNote: (uuid: string, data: ClinicalNote) =>
    apiClient.put<ClinicalNote>(`/consultations/${uuid}/clinical-note`, data).then((r) => r.data),

  listByProfile: (profileUuid: string) =>
    apiClient.get<{ total: number; consultations: ConsultationResponse[] }>(`/consultations/patient/${profileUuid}`).then((r) => r.data),

  getCompleteness: (uuid: string) =>
    apiClient.get<ConsultationCompleteness>(`/consultations/${uuid}/completeness`).then((r) => r.data),
}
