import apiClient from './client'
import type { MedicalReport } from '../types'

export const reportsApi = {
  list: (patientUuid: string) =>
    apiClient.get<MedicalReport[]>(`/patients/${patientUuid}/reports`).then(r => r.data),

  get: (reportUuid: string) =>
    apiClient.get<MedicalReport>(`/patients/reports/${reportUuid}`).then(r => r.data),

  create: (patientUuid: string, data: { title: string; content: string; report_type?: string; is_pinned?: boolean; created_by?: string }) =>
    apiClient.post<MedicalReport>(`/patients/${patientUuid}/reports`, data).then(r => r.data),

  update: (reportUuid: string, data: { title?: string; content?: string; report_type?: string; is_pinned?: boolean }) =>
    apiClient.patch<MedicalReport>(`/patients/reports/${reportUuid}`, data).then(r => r.data),

  togglePin: (reportUuid: string) =>
    apiClient.post<MedicalReport>(`/patients/reports/${reportUuid}/toggle-pin`).then(r => r.data),

  delete: (reportUuid: string) =>
    apiClient.delete(`/patients/reports/${reportUuid}`),
}
