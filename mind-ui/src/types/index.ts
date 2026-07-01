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
  full_name_encrypted?: string
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
  gender_identity?: GenderIdentity
  education_level_id?: number
  education_level?: EducationLevel
  ethnicity_id?: number
  ethnicity?: Ethnicity
  marital_status?: string
  occupation?: string
  trans_status?: string
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

export interface PatientAssignment {
  assignment_id: number
  patient_uuid: string
  patient_name?: string
  assigned_at?: string
  is_active?: boolean
}

export interface HealthcareProfessionalResponse {
  professional_uuid: string
  full_name: string
  professional_license?: string
  profession?: string
  specialty?: string
  start_date?: string
  patient_assignments?: PatientAssignment[]
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
  dsm_criteria?: string
  dsm_exclusions?: string
  dsm_differentials?: string
  icd11_exclusions?: string
  icd11_differentials?: string
}

export interface DiagnosticInferenceResponse {
  inference_uuid: string
  consultation_uuid: string
  disorder_id: number
  disorder_name?: string
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
  patient_uuid?: string
  patient_name?: string
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
  patient_name?: string
  patient_uuid?: string
}

// --- Disorders / Symptoms ---
export interface Symptom {
  symptom_id: number
  symptom_name: string
  symptom_description?: string
}

export interface ICD11Code {
  code_id: number
  disorder_id: number
  icd11_code: string
  icd11_title?: string
  chapter?: string
  chapter_code?: string
  who_url?: string
  clinical_description?: string
  diagnostic_requirements?: string
}

export interface Disorder {
  disorder_id: number
  disorder_name: string
  cid_code: string
  dsm_code: string
  disorder_description?: string
  dsm_chapter?: string
  dsm_criteria?: string
  dsm_exclusions?: string
  dsm_differentials?: string
  icd11_exclusions?: string
  icd11_differentials?: string
  icd11_codes?: ICD11Code[]
  is_core?: boolean
}

export interface DiagnosticCriteria {
  criteria_id: number
  disorder_id: number
  symptom_id: number
  required_presence: boolean
  minimum_duration_days?: number
  clinical_notes?: string
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
  severity?: string
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

export interface ScaleTrendItem {
  scale_name: string
  total_records: number
  statistics?: Record<string, number>
  trend: {
    scores: Record<string, number>
    moving_avg_3: Record<string, number>
  }
}

export interface CorrelationData {
  scale_a: string
  scale_b: string
  pearson_r: number
  p_value: number
}

export interface SexDistribution {
  [key: string]: number
}

export interface AgeDistribution {
  '0-18': number
  '19-35': number
  '36-50': number
  '51-65': number
  '65+': number
}

export interface DemographicsResponse {
  total_patients: number
  sex_distribution: SexDistribution
  gender_identity_distribution: Record<string, number>
  age_distribution: AgeDistribution
  education_level_distribution: Record<string, number>
  ethnicity_distribution: Record<string, number>
}

export interface ConsultationMetricsResponse {
  period_days: number
  total_consultations: number
  unique_patients: number
  avg_per_day: number
  daily_breakdown: Record<string, number>
  trend: {
    daily_counts: Record<string, number>
    moving_avg_7d: Record<string, number>
  }
}

export interface PrevalenceTrendItem {
  disorder_name: string
  monthly_counts: { month: string; count: number; avg_probability: number }[]
  total_count: number
}

export interface DisorderPrevalenceItem {
  disorder_id: number
  disorder_name: string
  cid_code?: string
  inference_count: number
  avg_probability: number
}

export interface ScaleDistributionResponse {
  scale_name: string
  total_assessments: number
  statistics?: Record<string, number>
  distribution: {
    minimal: number
    mild: number
    moderate: number
    moderately_severe: number
    severe: number
  }
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

export interface Medication {
  medication_id: number
  name: string
  active_ingredient?: string
  classification?: string
  description?: string
  created_at?: string
}

export interface PrescriptionItem {
  item_uuid: string
  medication_id: number
  dosage: string
  frequency: string
  route?: string
  duration_days?: number
  notes?: string
  created_at?: string
  medication?: Medication
}

export interface Prescription {
  prescription_uuid: string
  consultation_uuid: string
  notes?: string
  created_at?: string
  items: PrescriptionItem[]
}

// --- Timeline ---
export interface SymptomObservationBrief {
  symptom_name: string
  intensity?: number
  frequency?: string
}

export interface DiagnosticInferenceBrief {
  disorder_name: string
  inference_probability: number
}

export interface PrescriptionBrief {
  medication_name: string
  dosage: string
  frequency: string
  route?: string
  duration_days?: number
}

export interface DisorderMedicationAssoc {
  dm_id: number
  medication_id: number
  disorder_id: number
  success_rate?: number
  failure_rate?: number
  avg_response_weeks?: number
  line_of_treatment?: number
  recommendation_strength?: string
  notes?: string
  created_at?: string
  medication?: Medication
  disorder_name?: string
}

export interface TreatmentOutcomeItem {
  outcome_uuid: string
  patient_uuid: string
  medication_id: number
  disorder_id: number
  start_date: string
  end_date?: string
  outcome: string
  response_weeks?: number
  side_effects?: string
  discontinued_reason?: string
  adherence?: string
  created_at?: string
  medication?: Medication
  disorder_name?: string
}

export interface MedicationStat {
  medication_id: number
  medication_name: string
  total_cases: number
  success_rate: number
  worsened_count: number
  discontinued_count: number
  avg_response_weeks?: number
}

export interface TreatmentPrediction {
  medication_id: number
  medication_name: string
  success_probability: number
  expected_response_weeks?: number
  recommendation_strength?: string
}

export interface ClinicalNoteBrief {
  chief_complaint?: string
  clinical_assessment?: string
  treatment_plan?: string
}

export interface ScaleScoreBrief {
  scale_name: string
  total_score: number
}

export interface ConsultationTimelineEvent {
  consultation_uuid: string
  consultation_date: string
  professional_name?: string
  consultation_notes?: string
  symptoms: SymptomObservationBrief[]
  scale_scores: ScaleScoreBrief[]
  inferences: DiagnosticInferenceBrief[]
  prescriptions: PrescriptionBrief[]
  clinical_note?: ClinicalNoteBrief
}

export interface EpisodeTimelineEvent {
  episode_uuid: string
  episode_start?: string
  episode_end?: string
  episode_type?: string
  clinical_description?: string
}

export interface TimelineEvent {
  date: string
  event_type: string
  consultation?: ConsultationTimelineEvent
  episode?: EpisodeTimelineEvent
}

// --- Medical Reports ---
export interface MedicalReport {
  report_uuid: string
  patient_uuid: string
  title: string
  content: string
  report_type: string
  is_pinned: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface TimelineResponse {
  patient_uuid: string
  patient_name: string
  events: TimelineEvent[]
}

// --- Analytics (DW Views) ---
export interface PrevalenceTrendItem {
  disorder_name: string
  data: { month: string; count: number; avg_probability: number }[]
  total: number
}

export interface PrevalenceTrendResponse {
  disorders: PrevalenceTrendItem[]
  total: number
}

export interface ComorbidityPair {
  disorder_a: string
  category_a: string
  disorder_b: string
  category_b: string
  co_occurrence_count: number
  prevalence_pct: number
}

export interface ComorbidityResponse {
  pairs: ComorbidityPair[]
  total_pairs: number
}

export interface ScaleDistributionRow {
  scale_name: string
  total_responses: number
  mean_score: number
  stddev_score: number
  min_score: number
  max_score: number
  median_score: number
  mean_pct: number
  unique_patients: number
}

export interface ScoreDistributionResponse {
  scales: ScaleDistributionRow[]
}

export interface ScaleSeverityLevel {
  severity: string
  count: number
  avg_score: number
}

export interface ScaleSeverityItem {
  scale_name: string
  severity_levels: ScaleSeverityLevel[]
}

export interface ScaleSeverityResponse {
  scales: ScaleSeverityItem[]
}

export interface ProfessionalWorkloadRow {
  full_name: string
  profession: string
  specialty: string
  total_consultations: number
  unique_patients: number
  total_diagnoses: number
  avg_symptoms_per_consult: number
  avg_symptom_intensity: number
  avg_max_probability: number
  scales_used: number
}

export interface ProfessionalWorkloadResponse {
  professionals: ProfessionalWorkloadRow[]
  total: number
}

export interface DemographicSummaryRow {
  age_group: string
  sex: string
  education_level: string
  ethnicity: string
  patient_count: number
  avg_consultations: number
}

export interface DemographicSummaryResponse {
  demographics: DemographicSummaryRow[]
  total: number
}

export interface MonthlyConsultationRow {
  year_month: string
  total_consultations: number
  unique_patients: number
  avg_symptoms: number
  avg_total_intensity: number
  consultations_with_inference: number
  avg_max_probability: number
}

export interface MonthlyConsultationResponse {
  months: MonthlyConsultationRow[]
  total_months: number
}

// --- ML Scale Predictions ---
export interface FactorScore {
  score: number
  max_possible: number
  percentage?: number
  description?: string
}

export interface PersonalityScaleSet {
  factors?: Record<string, FactorScore>
  subscales?: Record<string, FactorScore>
  dimensions?: Record<string, FactorScore>
  total_score: number
  total_max: number
}

export interface PersonalityTimelinePoint {
  consultation_uuid: string
  date: string
  total_score: number
  total_max: number
  factors?: Record<string, FactorScore>
  subscales?: Record<string, FactorScore>
  dimensions?: Record<string, FactorScore>
}

export interface PersonalityTimelineItem {
  timeline: PersonalityTimelinePoint[]
  total_max: number
}

export interface PersonalityTimelineResponse {
  bfp: PersonalityTimelineItem
  dt12: PersonalityTimelineItem
  hexaco: PersonalityTimelineItem
  bis11: PersonalityTimelineItem
  tas20: PersonalityTimelineItem
  rses: PersonalityTimelineItem
}

export interface PersonalityFactorsResponse {
  bfp: PersonalityScaleSet
  dt12: PersonalityScaleSet
  hexaco: PersonalityScaleSet
  bis11: PersonalityScaleSet
  tas20: PersonalityScaleSet
  rses: PersonalityScaleSet
  data_source?: string
  feature_scales?: Record<string, number>
}

export interface DisorderRiskRequest {
  scale_scores: Record<string, number>
}

export interface DisorderRiskResponse {
  risks: Record<string, number>
}

export interface MLDashboardResponse {
  personality: {
    bfp_averages: Record<string, number>
    dt12_averages: Record<string, number>
    hexaco_averages: Record<string, number>
    bis11_averages: Record<string, number>
    tas20_averages: Record<string, number>
    rses_averages: Record<string, number>
    total_assessments: number
  }
  efficacy: {
    total_outcomes: number
    total_associations: number
    outcome_distribution: Record<string, number>
    by_line_of_treatment: {
      line: string
      avg_success_rate: number
      count: number
    }[]
  }
  models: {
    name: string
    objective: string
    algorithm: string
    stage: string
    r2: number
    mae: number
    description: string
  }[]
}
