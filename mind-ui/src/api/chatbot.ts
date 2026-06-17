import apiClient from './client'

export interface SentimentoResult {
  rotulo: string
  score: number
}

export interface CriterioDetalhado {
  criteria_id: number
  symptom_name: string | null
  required_presence: boolean
  minimum_duration_days: number | null
  clinical_notes: string | null
}

export interface TranstornoResultado {
  disorder_id: number
  disorder_name: string
  cid_code: string | null
  dsm_code: string | null
  disorder_description: string | null
  dsm_criteria: string | null
  dsm_exclusions: string | null
  dsm_differentials: string | null
  icd11_exclusions: string | null
  icd11_differentials: string | null
  criterios_detalhados: CriterioDetalhado[]
  inference_probability?: number | null
}

export interface ChatResponse {
  sentimento: SentimentoResult
  resultados: TranstornoResultado[]
  sintomas: Array<{ symptom_id: number; symptom_name: string }>
  medicamentos: Array<{ medication_id: number; name: string; active_ingredient: string | null; classification: string | null }>
  escalas: Array<{ scale_id: number; scale_name: string; description: string | null }>
  resposta: string
  session_id: string
}

export interface FeedbackResponse {
  feedback_id: number
  message_id: number
  rating: string
}

export interface HistoryMessage {
  message_id: number
  role: string
  content: string
  metadata_json: string | null
  created_at: string
}

export interface HistoryResponse {
  messages: HistoryMessage[]
}

let currentSessionId: string | null = null

export function getSessionId(): string {
  if (!currentSessionId) {
    currentSessionId = localStorage.getItem('mia_session_id')
  }
  return currentSessionId || ''
}

export function setSessionId(id: string) {
  currentSessionId = id
  localStorage.setItem('mia_session_id', id)
}

export const chatbotApi = {
  ask: (mensagem: string) => {
    const session_id = getSessionId()
    return apiClient
      .post<ChatResponse>('/chatbot/ask', { mensagem, session_id: session_id || undefined })
      .then((r) => {
        if (r.data.session_id) {
          setSessionId(r.data.session_id)
        }
        return r.data
      })
  },

  sendFeedback: (message_id: number, rating: string, corrected_text?: string) =>
    apiClient
      .post<FeedbackResponse>('/chatbot/feedback', { message_id, rating, corrected_text })
      .then((r) => r.data),

  getHistory: (session_id: string) =>
    apiClient
      .get<HistoryResponse>('/chatbot/history', { params: { session_id } })
      .then((r) => r.data),
}
