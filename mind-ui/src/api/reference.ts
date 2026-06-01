import apiClient from './client'
import type { SexType, GenderIdentity, EducationLevel, Ethnicity } from '../types'

export const referenceApi = {
  sexTypes: () => apiClient.get<SexType[]>('/reference/sex-types').then((r) => r.data),
  genderIdentities: () => apiClient.get<GenderIdentity[]>('/reference/gender-identities').then((r) => r.data),
  educationLevels: () => apiClient.get<EducationLevel[]>('/reference/education-levels').then((r) => r.data),
  ethnicities: () => apiClient.get<Ethnicity[]>('/reference/ethnicities').then((r) => r.data),
}
