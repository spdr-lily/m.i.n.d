import apiClient from './client'
import type { PatientCreateRequest, PatientResponse, PaginatedPatients } from '../types'

export const patientsApi = {
  list: (page = 1, size = 20) =>
    apiClient.get<PaginatedPatients>('/patients', { params: { page, size } }).then((r) => r.data),

  get: (uuid: string) =>
    apiClient.get<PatientResponse>(`/patients/${uuid}`).then((r) => r.data),

  create: (data: PatientCreateRequest) =>
    apiClient.post<PatientResponse>('/patients', data).then((r) => r.data),

  update: (uuid: string, data: Partial<PatientCreateRequest>) =>
    apiClient.patch<PatientResponse>(`/patients/${uuid}`, data).then((r) => r.data),

  delete: (uuid: string) =>
    apiClient.delete(`/patients/${uuid}`),
}
