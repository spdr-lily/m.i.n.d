import apiClient from './client'
import type { Medication, Prescription } from '../types'

export const medicationsApi = {
  list: () =>
    apiClient.get<{ total: number; medications: Medication[] }>('/medications').then((r) => r.data.medications),

  create: (data: { name: string; active_ingredient?: string; classification?: string; description?: string }) =>
    apiClient.post<Medication>('/medications', data).then((r) => r.data),

  update: (id: number, data: { name?: string; active_ingredient?: string; classification?: string; description?: string }) =>
    apiClient.patch<Medication>(`/medications/${id}`, data).then((r) => r.data),

  delete: (id: number) =>
    apiClient.delete(`/medications/${id}`),

  listPrescriptions: (consultationUuid: string) =>
    apiClient.get<{ total: number; prescriptions: Prescription[] }>(`/consultations/${consultationUuid}/prescriptions`).then((r) => r.data.prescriptions),

  createPrescription: (consultationUuid: string, data: { notes?: string; items: { medication_id: number; dosage: string; frequency: string; route?: string; duration_days?: number; notes?: string }[] }) =>
    apiClient.post<Prescription>(`/consultations/${consultationUuid}/prescriptions`, data).then((r) => r.data),

  deletePrescription: (prescriptionUuid: string) =>
    apiClient.delete(`/prescriptions/${prescriptionUuid}`),
}
