// --- Auth ---
export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface User {
  user_uuid: string
  username: string
  full_name: string
  email_hash?: string
  role: 'admin' | 'clinician' | 'viewer'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RegisterRequest {
  username: string
  password: string
  full_name: string
  role?: string
}

// --- Patients ---
export interface PatientIdentity {
  patient_uuid?: string
  full_name: string
  cpf_hash?: string
  email_hash?: string
}

export interface PatientProfile {
  profile_uuid?: string
  birth_date: string
  sex_type_id: number
  gender_identity_id: number
  education_level_id: number
  ethnicity_id: number
  marital_status?: string
  occupation?: string
}

export interface PatientCreateRequest {
  identity: PatientIdentity
  profile: PatientProfile
}

export interface PatientResponse {
  identity: PatientIdentity
  profile: PatientProfile
}

export interface PatientListItem {
  patient_uuid: string
  full_name: string
  birth_date: string
  sex_type: string
  age: number
}

export interface PaginatedPatients {
  total: number
  patients: PatientListItem[]
}

// --- Professionals ---
export interface Professional {
  professional_uuid?: string
  full_name: string
  license_number: string
  specialty: string
  email?: string
  phone?: string
}

// --- Consultations ---
export interface SymptomObservation {
  symptom_id: number
  intensity?: number
  frequency?: number
  duration_days?: number
}

export interface ConsultationCreate {
  patient_uuid: string
  professional_uuid: string
  consultation_notes?: string
  symptoms: SymptomObservation[]
}

export interface ConsultationResponse {
  consultation_uuid: string
  patient_uuid: string
  professional_uuid: string
  professional_name: string
  consultation_date: string
  consultation_notes?: string
}

// --- Disorders / Symptoms ---
export interface Symptom {
  symptom_id: number
  symptom_name: string
  symptom_description?: string
}

export interface Disorder {
  disorder_id: number
  disorder_name: string
  cid_code: string
  dsm_code: string
  disorder_description?: string
}

export interface DiagnosticCriteria {
  criteria_id: number
  symptom_id: number
  required_presence: boolean
  minimum_duration_days?: number
}

// --- Assessment Scales ---
export interface ScaleQuestion {
  question_id: number
  question_text: string
  question_order: number
}

export interface AssessmentScale {
  scale_id: number
  scale_name: string
  scale_description?: string
  questions: ScaleQuestion[]
}

export interface ScaleScoreRequest {
  scale_name: string
  responses: number[]
}

export interface ScaleScoreResponse {
  scale_name: string
  total_score: number
  severity: string
  interpretation: string
}

export interface ScaleHistoryItem {
  date: string
  score: number
  severity: string
}

// --- Inferences ---
export interface InferenceRequest {
  consultation_uuid: string
  observations?: Record<string, string>
}

export interface InferenceResult {
  inference_uuid: string
  disorder_name: string
  probability: number
  confidence_level: string
  criteria_met: boolean
  supporting_symptoms: string[]
  exclusion_applied?: boolean
}

export interface InferenceResponse {
  results: InferenceResult[]
  explanation?: string
}

export interface BayesianInferenceRequest {
  evidence: Record<string, boolean>
  top_k?: number
}

export interface BayesianResult {
  disorder_name: string
  prior_probability: number
  posterior_probability: number
  confidence: number
  supporting_symptoms: string[]
  excluding_symptoms: string[]
}

// --- Alerts ---
export interface Alert {
  alert_id: number
  alert_type: string
  severity: string
  message: string
  patient_uuid?: string
  created_at: string
  resolved: boolean
}

// --- Metrics ---
export interface MetricsOverview {
  total_patients: number
  total_consultations: number
  active_alerts: number
  total_inferences: number
  avg_confidence: number
}

export interface ScaleTrend {
  date: string
  avg_score: number
  patient_count: number
}

export interface CorrelationData {
  scale_a: string
  scale_b: string
  pearson_r: number
  p_value: number
}

// --- Admin ---
export interface RolePermission {
  id?: number
  role: string
  permission: string
}

export interface RoutePermission {
  id?: number
  http_method: string
  path_pattern: string
  permission_required: string
  description?: string
  is_active?: boolean
}

export interface MonitoringStats {
  total_requests: number
  avg_latency_ms: number
  p95_latency_ms: number
  requests_by_endpoint: Record<string, number>
  error_rate: number
}

export interface HealthStatus {
  status: string
  database: string
  uptime_seconds: number
}

export interface RequestLog {
  method: string
  path: string
  status_code: number
  latency_ms: number
  timestamp: string
}

// --- Audit ---
export interface AuditLog {
  audit_id: number
  entity_name: string
  entity_id: string
  operation_type: string
  performed_by: string
  old_data?: Record<string, unknown>
  new_data?: Record<string, unknown>
  ip_address?: string
  status_code?: number
  latency_ms?: number
  created_at: string
}

export interface PaginatedAuditLogs {
  total: number
  logs: AuditLog[]
}

// --- Pagination ---
export interface PaginatedResponse<T> {
  total: number
  items: T[]
}

// --- Reference Data ---
export interface SexType {
  sex_type_id: number
  code: string
  description: string
}

export interface GenderIdentity {
  gender_identity_id: number
  code: string
  description: string
}

export interface EducationLevel {
  education_level_id: number
  code: string
  description: string
}

export interface Ethnicity {
  ethnicity_id: number
  code: string
  description: string
}
