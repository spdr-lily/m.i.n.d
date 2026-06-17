import apiClient from './client'
import type { DisorderMedicationAssoc, TreatmentOutcomeItem, MedicationStat, TreatmentPrediction } from '../types'

export const treatmentsApi = {
  listAssociations: async (params?: { disorder_id?: number; medication_id?: number }): Promise<DisorderMedicationAssoc[]> => {
    const res = await apiClient.get('/treatment/associations', { params })
    return res.data.associations
  },

  createAssociation: async (data: Partial<DisorderMedicationAssoc>) => {
    const res = await apiClient.post('/treatment/associations', data)
    return res.data
  },

  updateAssociation: async (dm_id: number, data: Partial<DisorderMedicationAssoc>) => {
    const res = await apiClient.patch(`/treatment/associations/${dm_id}`, data)
    return res.data
  },

  deleteAssociation: async (dm_id: number) => {
    await apiClient.delete(`/treatment/associations/${dm_id}`)
  },

  listOutcomes: async (params?: { patient_uuid?: string; medication_id?: number; disorder_id?: number }): Promise<TreatmentOutcomeItem[]> => {
    const res = await apiClient.get('/treatment/outcomes', { params })
    return res.data.outcomes
  },

  createOutcome: async (data: Partial<TreatmentOutcomeItem>) => {
    const res = await apiClient.post('/treatment/outcomes', data)
    return res.data
  },

  deleteOutcome: async (outcome_uuid: string) => {
    await apiClient.delete(`/treatment/outcomes/${outcome_uuid}`)
  },

  getStats: async (disorder_id: number, medication_id?: number): Promise<{ disorder_id: number; medication_stats: MedicationStat[] }> => {
    const res = await apiClient.get(`/treatment/stats/${disorder_id}`, { params: medication_id ? { medication_id } : {} })
    return res.data
  },

  predict: async (patient_uuid: string, disorder_id: number, medication_ids: number[]): Promise<{ disorder_id: number; disorder_name: string; predictions: TreatmentPrediction[] }> => {
    const res = await apiClient.post('/treatment/predict', { patient_uuid, disorder_id, medication_ids })
    return res.data
  },
}
