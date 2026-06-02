// --- Auth ---
export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user_uuid: string
  role: string
  username: string
}

export interface User {
  user_uuid: string
  username: string
  full_name?: string
  role: string
  is_active: boolean
  created_at?: string
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
  patient_uuid?: string
  birth_date: string
  sex_type_id?: number
  sex_type?: SexType
  gender_identity_id?: number
  education_level_id?: number
  ethnicity_id?: number
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
  birth_date: string | null
  sex_type: string | null
  age: number | null
  occupation?: string | null
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
  frequency?: string
  duration_days?: number
  clinical_notes?: string
}

export interface ConsultationCreate {
  profile_uuid: string
  consultation_date: string
  professional_uuid?: string
  consultation_notes?: string
  symptom_observations?: SymptomObservation[]
  scale_responses?: { question_id: number; response_value?: number; response_text?: string }[]
  clinical_note?: ClinicalNote
}

export interface HealthcareProfessionalResponse {
  professional_uuid: string
  full_name: string
  professional_license?: string
  specialty?: string
}

export interface SymptomObservationResponse {
  observation_id: number
  consultation_uuid: string
  symptom_id: number
  intensity?: number
  frequency?: string
  duration_days?: number
  clinical_notes?: string
  symptom?: Symptom
}

export interface ScaleResponseResponse {
  response_id: number
  consultation_uuid: string
  question_id: number
  response_value?: number
  response_text?: string
}

export interface DisorderResponse {
  disorder_id: number
  cid_code?: string
  dsm_code?: string
  disorder_name: string
  disorder_description?: string
}

export interface DiagnosticInferenceResponse {
  inference_uuid: string
  consultation_uuid: string
  disorder_id: number
  inference_probability: number
  confidence_level?: number
  generated_by_model?: string
  model_version?: string
  disorder?: DisorderResponse
}

export interface ClinicalNote {
  note_uuid?: string
  consultation_uuid?: string
  chief_complaint?: string
  history_present_illness?: string
  subjective_findings?: string
  objective_findings?: string
  clinical_assessment?: string
  treatment_plan?: string
  follow_up?: string
}

export interface ConsultationResponse {
  consultation_uuid: string
  consultation_date: string
  profile_uuid: string
  professional_uuid?: string
  consultation_notes?: string
  healthcare_professional?: HealthcareProfessionalResponse
  symptom_observations?: SymptomObservationResponse[]
  scale_responses?: ScaleResponseResponse[]
  diagnostic_inferences?: DiagnosticInferenceResponse[]
  clinical_note?: ClinicalNote | null
}

export interface ConsultationListItem {
  consultation_uuid: string
  consultation_date: string
  professional_name?: string
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

export interface ScaleCreateRequest {
  scale_name: string
  scale_description?: string
}

export interface ScaleUpdateRequest {
  scale_name?: string
  scale_description?: string
}

export interface ScaleQuestionCreateRequest {
  question_text: string
  question_order: number
}

export interface ScaleQuestionUpdateRequest {
  question_text?: string
  question_order?: number
}

export interface PaginatedScales {
  total: number
  scales: AssessmentScale[]
}

export interface PaginatedQuestions {
  total: number
  questions: ScaleQuestion[]
}

// --- Inferences ---
export interface InferenceRequest {
  consultation_uuid: string
  observations?: Record<string, string>
}

export interface InferenceResult {
  disorder_id: number
  disorder_name: string
  cid_code?: string
  dsm_code?: string
  inference_probability: number
  confidence_level?: number
}

export interface InferenceResponse {
  consultation_uuid: string
  inferences: InferenceResult[]
  generated_by_model: string
  model_version: string
  requires_human_review: boolean
}

export interface BayesianInferenceRequest {
  consultation_uuid: string
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

// --- Completeness ---
export interface ConsultationCompleteness {
  score: number
  max_score: number
  missing: string[]
  complete: boolean
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
