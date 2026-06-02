import apiClient from './client'
import type { Disorder, Symptom, DiagnosticCriteria } from '../types'

export const disordersApi = {
  listSymptoms: () =>
    apiClient.get<{ total: number; symptoms: Symptom[] }>('/symptoms').then((r) => r.data.symptoms),

  listDisorders: () =>
    apiClient.get<Disorder[]>('/disorders').then((r) => r.data),

  getCriteria: (disorderId: number) =>
    apiClient.get<DiagnosticCriteria[]>(`/disorders/${disorderId}/criteria`).then((r) => r.data),
}
