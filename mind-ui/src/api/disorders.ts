import apiClient from './client'
import type { Disorder, Symptom, DiagnosticCriteria } from '../types'

export const disordersApi = {
  listSymptoms: () =>
    apiClient.get<{ total: number; symptoms: Symptom[] }>('/symptoms').then((r) => r.data.symptoms),

  createSymptom: (data: { symptom_name: string; symptom_description?: string }) =>
    apiClient.post<Symptom>('/symptoms', data).then((r) => r.data),

  updateSymptom: (id: number, data: { symptom_name?: string; symptom_description?: string }) =>
    apiClient.patch<Symptom>(`/symptoms/${id}`, data).then((r) => r.data),

  deleteSymptom: (id: number) =>
    apiClient.delete(`/symptoms/${id}`),

  listDisorders: () =>
    apiClient.get<{ total: number; disorders: Disorder[] }>('/disorders').then((r) => r.data.disorders),

  getCriteria: (disorderId: number) =>
    apiClient.get<{ total: number; criteria: DiagnosticCriteria[] }>(`/disorders/${disorderId}/criteria`).then((r) => r.data),
}
