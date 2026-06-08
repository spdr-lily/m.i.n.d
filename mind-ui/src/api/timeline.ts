import apiClient from './client'
import type { TimelineResponse } from '../types'

export const timelineApi = {
  get: (patientUuid: string) =>
    apiClient.get<TimelineResponse>(`/patients/${patientUuid}/timeline`).then((r) => r.data),
}
