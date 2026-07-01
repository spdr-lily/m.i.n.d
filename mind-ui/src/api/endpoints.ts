import apiClient from './client';

type ApiResponse<T = any> = { data: T };

export const patientsApi = {
  list: (arg1?: any, arg2?: any) => {
    const params = typeof arg1 === 'number' ? { page: arg1, size: arg2 } : arg1;
    return apiClient.get('/patients', { params }).then((r: ApiResponse) => r.data);
  },
  get: (uuid: string) => apiClient.get(`/patients/${uuid}`).then((r: ApiResponse) => r.data),
  create: (data: any) => apiClient.post('/patients', data).then((r: ApiResponse) => r.data),
  update: (uuid: string, data: any) => apiClient.patch(`/patients/${uuid}`, data).then((r: ApiResponse) => r.data),
  delete: (uuid: string) => apiClient.delete(`/patients/${uuid}`).then((r: ApiResponse) => r.data),
  search: (query: string) => apiClient.get('/patients/search', { params: { q: query } }).then((r: ApiResponse) => r.data),
  listByProfile: (params?: any) => apiClient.get('/patients', { params }).then((r: ApiResponse) => r.data),
};

export const consultationsApi = {
  list: (params?: any, _signal?: any) => apiClient.get('/consultations', { params }).then((r: ApiResponse) => r.data),
  get: (uuid: string) => apiClient.get(`/consultations/${uuid}`).then((r: ApiResponse) => r.data),
  create: (data: any) => apiClient.post('/consultations', data).then((r: ApiResponse) => r.data),
  update: (uuid: string, data: any) => apiClient.patch(`/consultations/${uuid}`, data).then((r: ApiResponse) => r.data),
  delete: (uuid: string) => apiClient.delete(`/consultations/${uuid}`).then((r: ApiResponse) => r.data),
  createWithData: (data: any) => apiClient.post('/consultations/with-data', data).then((r: ApiResponse) => r.data),
  getCompleteness: (uuid: string) => apiClient.get(`/consultations/${uuid}/completeness`).then((r: ApiResponse) => r.data),
  listByProfile: (params?: any) => apiClient.get('/consultations', { params }).then((r: ApiResponse) => r.data),
};

export const scalesApi = {
  list: (skip?: number, limit?: any) => {
    if (typeof skip === 'object') return apiClient.get('/scales', { params: skip }).then((r: ApiResponse) => r.data);
    return apiClient.get('/scales', { params: { skip, limit } }).then((r: ApiResponse) => r.data);
  },
  get: (id: any) => apiClient.get(`/scales/${id}`).then((r: ApiResponse) => r.data),
  getDetail: (id: any) => apiClient.get(`/scales/${id}`).then((r: ApiResponse) => r.data),
  create: (data: any) => apiClient.post('/scales', data).then((r: ApiResponse) => r.data),
  update: (id: number, data: any) => apiClient.patch(`/scales/${id}`, data).then((r: ApiResponse) => r.data),
  delete: (id: number) => apiClient.delete(`/scales/${id}`).then((r: ApiResponse) => r.data),
  getQuestions: (scaleId: number) => apiClient.get(`/scales/${scaleId}/questions`).then((r: ApiResponse) => r.data),
  submitResponses: (data: any) => apiClient.post('/scales/responses', data).then((r: ApiResponse) => r.data),
  score: (data: any) => apiClient.post('/scales/score', data).then((r: ApiResponse) => r.data),
  apply: (patientUuid: string, scaleName: string, responses: any) => apiClient.post(`/scales/apply/${patientUuid}`, { scale_name: scaleName, responses }).then((r: ApiResponse) => r.data),
  personalityTimeline: (patientUuid: string) => apiClient.get(`/assessments/patient/${patientUuid}/personality-timeline`).then((r: ApiResponse) => r.data),
  patientHistory: (patientUuid: string) => apiClient.get(`/assessments/patient/${patientUuid}`).then((r: ApiResponse) => r.data),
  history: (patientUuid: string, _signal?: any) => apiClient.get(`/assessments/patient/${patientUuid}`).then((r: ApiResponse) => r.data),
  updateQuestion: (id: number, data: any) => apiClient.patch(`/scales/questions/${id}`, data).then((r: ApiResponse) => r.data),
  createQuestion: (scaleId: number, data: any) => apiClient.post(`/scales/${scaleId}/questions`, data).then((r: ApiResponse) => r.data),
  deleteQuestion: (id: number) => apiClient.delete(`/scales/questions/${id}`).then((r: ApiResponse) => r.data),
};

export const mlApi = {
  predictPersonality: (data: any) => apiClient.post('/ml/scales/predict-personality', data).then((r: ApiResponse) => r.data),
  predictDisorderRisk: (data: any) => apiClient.post('/ml/scales/predict-disorder-risk', data).then((r: ApiResponse) => r.data),
  predictPersonalityFromPatient: (uuid: string) => apiClient.post(`/ml/scales/predict-personality-from-patient/${uuid}`).then((r: ApiResponse) => r.data),
  personalityFactors: (patientUuid: string) => apiClient.get(`/assessments/patient/${patientUuid}/personality-factors`).then((r: ApiResponse) => r.data),
  personalityTimeline: (patientUuid: string) => apiClient.get(`/assessments/patient/${patientUuid}/personality-timeline`).then((r: ApiResponse) => r.data),
};

export const inferencesApi = {
  listByConsultation: (uuid: string) => apiClient.get(`/inferences/consultation/${typeof uuid === 'string' ? uuid : uuid}`).then((r: ApiResponse) => r.data),
  explanation: (uuid: string) => apiClient.get(`/inferences/${uuid}/explanation`).then((r: ApiResponse) => r.data),
  listByPatient: (uuid: string) => apiClient.get(`/inferences/patient/${uuid}`).then((r: ApiResponse) => r.data),
  runCriteria: (arg: any) => {
    const uuid = typeof arg === 'string' ? arg : arg?.consultation_uuid;
    return apiClient.post(`/inferences/criteria/${uuid}`).then((r: ApiResponse) => r.data);
  },
  runBayesian: (arg: any) => {
    const uuid = typeof arg === 'string' ? arg : arg?.consultation_uuid;
    return apiClient.post(`/inferences/bayesian/${uuid}`).then((r: ApiResponse) => r.data);
  },
};

export const metricsApi = {
  overview: () => apiClient.get('/metrics/overview').then((r: ApiResponse) => r.data),
  general: () => apiClient.get('/metrics/general').then((r: ApiResponse) => r.data),
  demographics: () => apiClient.get('/metrics/demographics').then((r: ApiResponse) => r.data),
  consultations: (days?: number) => apiClient.get('/metrics/consultations', { params: { days } }).then((r: ApiResponse) => r.data),
  disorderPrevalence: (topN?: number) => apiClient.get('/metrics/disorders', { params: { top_n: topN } }).then((r: ApiResponse) => r.data),
  scaleDistribution: (name: string) => apiClient.get(`/metrics/scales/${name}`).then((r: ApiResponse) => r.data),
  scaleTrends: (name: string, days?: number) => apiClient.get(`/metrics/scales/${name}/trends`, { params: { days } }).then((r: ApiResponse) => r.data),
  correlations: () => apiClient.get('/metrics/correlations').then((r: ApiResponse) => r.data),
  patientLongitudinal: (uuid: string, days?: number) => apiClient.get(`/metrics/patients/${uuid}/longitudinal`, { params: { days } }).then((r: ApiResponse) => r.data),
  prevalenceTrends: (months?: number) => apiClient.get('/metrics/prevalence-trends', { params: { months } }).then((r: ApiResponse) => r.data),
  comorbidity: (topN?: number) => apiClient.get('/metrics/comorbidity', { params: { top_n: topN } }).then((r: ApiResponse) => r.data),
  mlDashboard: () => apiClient.get('/metrics/ml/dashboard').then((r: ApiResponse) => r.data),
  consultationMetrics: (days?: number) => apiClient.get('/metrics/consultations', { params: { days } }).then((r: ApiResponse) => r.data),
};

export const analyticsApi = {
  prevalenceTrends: (months?: number, top_n?: number) => apiClient.get('/analytics/prevalence-trends', { params: { months, top_n } }).then((r: ApiResponse) => r.data),
  comorbidity: (top_n?: number) => apiClient.get('/analytics/comorbidity', { params: { top_n } }).then((r: ApiResponse) => r.data),
  scoreDistributions: () => apiClient.get('/analytics/score-distributions').then((r: ApiResponse) => r.data),
  scaleSeverity: () => apiClient.get('/analytics/scale-severity').then((r: ApiResponse) => r.data),
  patientSummary: (limit?: number) => apiClient.get('/analytics/patient-summary', { params: { limit } }).then((r: ApiResponse) => r.data),
  professionalWorkload: () => apiClient.get('/analytics/professional-workload').then((r: ApiResponse) => r.data),
  demographicSummary: () => apiClient.get('/analytics/demographic-summary').then((r: ApiResponse) => r.data),
  monthlyConsultations: (months?: number) => apiClient.get('/analytics/monthly-consultations', { params: { months } }).then((r: ApiResponse) => r.data),
  symptomPrevalence: (params?: any) => apiClient.get('/analytics/symptom-prevalence', { params }).then((r: ApiResponse) => r.data),
  scaleTrendsMonthly: (params?: any) => apiClient.get('/analytics/scale-trends-monthly', { params }).then((r: ApiResponse) => r.data),
  disorderByDemographic: () => apiClient.get('/analytics/disorder-by-demographic').then((r: ApiResponse) => r.data),
};

export const adminApi = {
  listUsers: (params?: any, _signal?: any) => apiClient.get('/admin/users', { params }).then((r: ApiResponse) => r.data),
  getUser: (uuid: string) => apiClient.get(`/admin/users/${uuid}`).then((r: ApiResponse) => r.data),
  createUser: (data: any) => apiClient.post('/admin/users', data).then((r: ApiResponse) => r.data),
  updateUser: (uuid: string, data: any) => apiClient.patch(`/admin/users/${uuid}`, data).then((r: ApiResponse) => r.data),
  deleteUser: (uuid: string) => apiClient.delete(`/admin/users/${uuid}`).then((r: ApiResponse) => r.data),
  changePassword: (uuid: string, password: string) => apiClient.post(`/admin/users/${uuid}/change-password`, { new_password: password }).then((r: ApiResponse) => r.data),
  listPermissions: () => apiClient.get('/admin/permissions').then((r: ApiResponse) => r.data),
  addPermission: (data: any) => apiClient.post('/admin/permissions', data).then((r: ApiResponse) => r.data),
  removePermission: (id: number) => apiClient.delete(`/admin/permissions/${id}`).then((r: ApiResponse) => r.data),
  updatePermission: (id: number, data: any) => apiClient.patch(`/admin/permissions/${id}`, data).then((r: ApiResponse) => r.data),
  listRoles: () => apiClient.get('/admin/roles').then((r: ApiResponse) => r.data),
  listRoutePermissions: () => apiClient.get('/admin/route-permissions').then((r: ApiResponse) => r.data),
  addRoutePermission: (data: any) => apiClient.post('/admin/route-permissions', data).then((r: ApiResponse) => r.data),
  deleteRoutePermission: (id: number) => apiClient.delete(`/admin/route-permissions/${id}`).then((r: ApiResponse) => r.data),
  monitoring: () => apiClient.get('/admin/monitoring').then((r: ApiResponse) => r.data),
  stats: () => apiClient.get('/admin/monitoring/stats').then((r: ApiResponse) => r.data),
  health: () => apiClient.get('/admin/monitoring/health').then((r: ApiResponse) => r.data),
  requests: () => apiClient.get('/admin/monitoring/requests').then((r: ApiResponse) => r.data),
};

export const providersApi = {
  list: (params?: any) => apiClient.get('/professionals', { params }).then((r: ApiResponse) => r.data),
  get: (uuid: string) => apiClient.get(`/professionals/${uuid}`).then((r: ApiResponse) => r.data),
  create: (data: any) => apiClient.post('/professionals', data).then((r: ApiResponse) => r.data),
  update: (uuid: string, data: any) => apiClient.patch(`/professionals/${uuid}`, data).then((r: ApiResponse) => r.data),
  delete: (uuid: string) => apiClient.delete(`/professionals/${uuid}`).then((r: ApiResponse) => r.data),
};

export const disordersApi = {
  list: (params?: any) => apiClient.get('/disorders', { params }).then((r: ApiResponse) => r.data),
  listDisorders: (params?: any) => apiClient.get('/disorders', { params }).then((r: ApiResponse) => r.data),
  get: (id: number) => apiClient.get(`/disorders/${id}`).then((r: ApiResponse) => r.data),
  getCriteria: (disorderId: number) => apiClient.get(`/disorders/${disorderId}/criteria`).then((r: ApiResponse) => r.data),
  listSymptoms: (params?: any) => apiClient.get('/disorders/symptoms', { params }).then((r: ApiResponse) => r.data),
  createSymptom: (data: any) => apiClient.post('/disorders/symptoms', data).then((r: ApiResponse) => r.data),
  updateSymptom: (id: number, data: any) => apiClient.patch(`/disorders/symptoms/${id}`, data).then((r: ApiResponse) => r.data),
  deleteSymptom: (id: number) => apiClient.delete(`/disorders/symptoms/${id}`).then((r: ApiResponse) => r.data),
};

export const medicationsApi = {
  list: (params?: any) => apiClient.get('/medications', { params }).then((r: ApiResponse) => r.data),
  create: (data: any) => apiClient.post('/medications', data).then((r: ApiResponse) => r.data),
  update: (id: number, data: any) => apiClient.patch(`/medications/${id}`, data).then((r: ApiResponse) => r.data),
  delete: (id: number) => apiClient.delete(`/medications/${id}`).then((r: ApiResponse) => r.data),
  createPrescription: (data: any) => apiClient.post('/medications/prescriptions', data).then((r: ApiResponse) => r.data),
  listPrescriptions: (consultationUuid: string) => apiClient.get(`/medications/prescriptions/${consultationUuid}`).then((r: ApiResponse) => r.data),
  deletePrescription: (id: any) => apiClient.delete(`/medications/prescriptions/${id}`).then((r: ApiResponse) => r.data),
};

export const treatmentsApi = {
  listAssociations: (params?: any) => apiClient.get('/treatments/associations', { params }).then((r: ApiResponse) => r.data),
  createAssociation: (data: any) => apiClient.post('/treatments/associations', data).then((r: ApiResponse) => r.data),
  updateAssociation: (id: number, data: any) => apiClient.patch(`/treatments/associations/${id}`, data).then((r: ApiResponse) => r.data),
  deleteAssociation: (id: number) => apiClient.delete(`/treatments/associations/${id}`).then((r: ApiResponse) => r.data),
  predictEfficacy: (data: any) => apiClient.post('/treatments/predict', data).then((r: ApiResponse) => r.data),
  getStats: (disorderId: number) => apiClient.get(`/treatments/stats/${disorderId}`).then((r: ApiResponse) => r.data),
  predict: (...args: any[]) => {
    const data = args.length === 1 ? args[0] : { medication_id: args[0], patient_id: args[1], diagnosis_id: args[2] };
    return apiClient.post('/treatments/predict', data).then((r: ApiResponse) => r.data);
  },
  listOutcomes: (params?: any) => apiClient.get('/treatments/outcomes', { params }).then((r: ApiResponse) => r.data),
};

export const reportsApi = {
  list: (patientUuid: string, _signal?: any) => apiClient.get(`/reports/${patientUuid}`).then((r: ApiResponse) => r.data),
  create: (arg1: any, arg2?: any) => {
    if (arg2 !== undefined) return apiClient.post(`/reports/${arg1}`, arg2).then((r: ApiResponse) => r.data);
    return apiClient.post('/reports', arg1).then((r: ApiResponse) => r.data);
  },
  get: (uuid: string) => apiClient.get(`/reports/detail/${uuid}`).then((r: ApiResponse) => r.data),
  update: (uuid: string, data: any) => apiClient.patch(`/reports/${uuid}`, data).then((r: ApiResponse) => r.data),
  delete: (uuid: string) => apiClient.delete(`/reports/${uuid}`).then((r: ApiResponse) => r.data),
  togglePin: (uuid: string) => apiClient.post(`/reports/${uuid}/toggle-pin`).then((r: ApiResponse) => r.data),
};

export const timelineApi = {
  get: (patientUuid: string) => apiClient.get(`/timeline/${patientUuid}`).then((r: ApiResponse) => r.data),
};

export const alertsApi = {
  list: (params?: any) => apiClient.get('/alerts', { params }).then((r: ApiResponse) => r.data),
  resolve: (id: number) => apiClient.post(`/alerts/${id}/resolve`).then((r: ApiResponse) => r.data),
};

export const auditApi = {
  list: (...args: any[]) => {
    const params = args[0] || {};
    return apiClient.get('/audit', { params }).then((r: ApiResponse) => r.data);
  },
};

export const referenceApi = {
  sexTypes: () => apiClient.get('/reference/sex-types').then((r: ApiResponse) => r.data),
  genderIdentities: () => apiClient.get('/reference/gender-identities').then((r: ApiResponse) => r.data),
  educationLevels: () => apiClient.get('/reference/education-levels').then((r: ApiResponse) => r.data),
  ethnicities: () => apiClient.get('/reference/ethnicities').then((r: ApiResponse) => r.data),
};
