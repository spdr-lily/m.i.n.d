import { useEffect, useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Row, Col, Table, Tag, Spin, Switch, Divider, Alert, Progress, Collapse, Tooltip, Empty, Space, Grid, theme, Drawer, Descriptions } from 'antd'
import {
  ExperimentOutlined, ThunderboltOutlined, SafetyOutlined, HistoryOutlined,
  InfoCircleOutlined, FileSearchOutlined, PrinterOutlined, DownloadOutlined,
  LinkOutlined, CheckCircleOutlined,
} from '@ant-design/icons'
import { inferencesApi, patientsApi, consultationsApi, disordersApi } from '../../api/endpoints'
import type { PatientListItem, Symptom, InferenceResult, Disorder, DiagnosticCriteria, ICD11Code } from '../../types'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { useBreakpoint } = Grid

const SYMPTOM_GROUPS: Record<string, string> = {
  'abstinencia_substancia': 'Substâncias',
  'acumulo_objetos': 'TOC',
  'agitacao_retardo': 'Depressão',
  'alteracao_peso': 'Depressão',
  'alucinacoes_auditivas': 'Psicótico',
  'alucinacoes_visuais': 'Psicótico',
  'amnésia_traumática': 'PTSD',
  'anhedonia': 'Depressão',
  'apneia_sono': 'Sono',
  'appetite_changes': 'Depressão',
  'avoidance_behavior': 'PTSD',
  'avoidance_ptsd': 'PTSD',
  'avoidance_public': 'Agorafobia',
  'avoidance_social': 'Ansiedade',
  'binge_alone': 'Alimentar',
  'binge_control_loss': 'Alimentar',
  'binge_depressed': 'Alimentar',
  'binge_distress': 'Alimentar',
  'binge_eating': 'Alimentar',
  'binge_episodes': 'Alimentar',
  'blushing': 'Ansiedade',
  'body_image_distortion': 'Alimentar',
  'calafrios_ondas_calor': 'Pânico',
  'chest_pain': 'Pânico',
  'choro_frequente': 'Depressão',
  'chronic_low_mood': 'Depressão',
  'comer_oculto': 'Alimentar',
  'comportamento_desorganizado': 'Psicótico',
  'comportamento_risco': 'Bipolar',
  'compulsao_alimentar': 'Alimentar',
  'compulsions': 'TOC',
  'compulsoes': 'TOC',
  'concentracao': 'Depressão',
  'concentration_difficulty_gad': 'Ansiedade',
  'concentration_problems': 'Depressão',
  'contagem_ritualistica': 'TOC',
  'conversao_sensorial': 'Somático',
  'crenças_negativas': 'PTSD',
  'culpa_merito': 'PTSD',
  'daytime_impairment': 'Sono',
  'decreased_sleep': 'Bipolar',
  'deficit_comunicacao_nao_verbal': 'TEA',
  'deficit_reciprocidade': 'TEA',
  'deficit_relacionamento': 'TEA',
  'delirios_persecutorios': 'Psicótico',
  'delusions': 'Psicótico',
  'depressed_mood': 'Depressão',
  'derealization': 'Pânico',
  'desatencao_detalhes': 'TDAH',
  'desejo_intenso': 'Substâncias',
  'desesperanca_futuro': 'PTSD',
  'despertar_precoce': 'Sono',
  'desrealizacao': 'Pânico',
  'dificuldade_controle': 'Substâncias',
  'dificuldade_esperar_vez': 'TDAH',
  'dificuldade_iniciar_sono': 'Sono',
  'dificuldade_organizacao': 'TDAH',
  'dificuldade_seguir_instrucoes': 'TDAH',
  'dificuldade_sustentacao_atencao': 'TDAH',
  'discurso_desorganizado': 'Psicótico',
  'disorganized_speech': 'Psicótico',
  'distorcao_imagem': 'Alimentar',
  'distractibility': 'Bipolar',
  'distraibilidade_externa': 'TDAH',
  'dor_peito': 'Pânico',
  'early_waking': 'Sono',
  'embotamento_afetivo': 'Psicótico',
  'esquecimento_atividades': 'TDAH',
  'esquiva': 'PTSD',
  'euforia': 'Bipolar',
  'euphoric_mood': 'Bipolar',
  'evitacao_esforco_mental': 'TDAH',
  'evitacao_fobica': 'Agorafobia',
  'excessive_health_concern': 'Somático',
  'excessive_worry': 'Ansiedade',
  'fadiga': 'Depressão',
  'fadiga_constante': 'Ansiedade',
  'fala_excessiva': 'TDAH',
  'fatigue': 'Depressão',
  'fatigue_gad': 'Ansiedade',
  'fear_of_dying': 'Pânico',
  'fear_open_spaces': 'Agorafobia',
  'flashbacks_dissociativos': 'PTSD',
  'forgetfulness': 'TDAH',
  'fuga_ideias': 'Bipolar',
  'gastos_excessivos': 'Bipolar',
  'grandiosidade': 'Bipolar',
  'grandiosity': 'Bipolar',
  'guilt_feelings': 'Depressão',
  'hallucinations': 'Psicótico',
  'hipersonia_atipica': 'Depressão',
  'hiperssexualidade': 'Bipolar',
  'hipervigilancia': 'PTSD',
  'hopelessness': 'Depressão',
  'humor_deprimido': 'Depressão',
  'hyperactivity': 'TDAH',
  'hypervigilance': 'PTSD',
  'hypomanic_mood': 'Bipolar',
  'impulsivity': 'TDAH',
  'inattention': 'TDAH',
  'incapacidade_quieto': 'TDAH',
  'increased_energy': 'Bipolar',
  'inquietacao': 'Ansiedade',
  'inquietacao_motora': 'TDAH',
  'insistencia_rotina': 'TEA',
  'insonia_hipersonia': 'Depressão',
  'interesses_fixos': 'TEA',
  'interrompe_outros': 'TDAH',
  'intrusive_memories': 'PTSD',
  'intrusive_thoughts': 'TOC',
  'irritabilidade': 'Ansiedade',
  'irritability': 'Ansiedade',
  'lavagem_limpeza': 'TOC',
  'lentificacao': 'Depressão',
  'logorreia': 'Bipolar',
  'loss_control': 'Substâncias',
  'loss_of_interest': 'Depressão',
  'low_energy_dysthymia': 'Depressão',
  'low_self_esteem': 'Depressão',
  'low_weight': 'Alimentar',
  'medical_consultation': 'Somático',
  'medo_enlouquecer': 'Pânico',
  'medo_ganho_peso': 'Alimentar',
  'medo_lugares_abertos': 'Agorafobia',
  'medo_lugares_fechados': 'Agorafobia',
  'medo_morrer': 'Pânico',
  'medo_morrer_panico': 'Pânico',
  'medo_multidoes': 'Agorafobia',
  'medo_transporte': 'Agorafobia',
  'mildly_increased_energy': 'Bipolar',
  'movimento_pernas': 'Sono',
  'movimentos_estereotipados': 'TEA',
  'muscle_tension': 'Ansiedade',
  'nao_escuta_direto': 'TDAH',
  'nausea_abdominal': 'Pânico',
  'need_escort': 'Agorafobia',
  'negative_cognitions': 'PTSD',
  'negative_symptoms': 'Psicótico',
  'negativismo_catatonico': 'Psicótico',
  'neglect_activities': 'Substâncias',
  'nightmares': 'PTSD',
  'obsessions': 'TOC',
  'obsessoes': 'TOC',
  'organizational_difficulty': 'TDAH',
  'palpitacoes': 'Pânico',
  'palpitations': 'Pânico',
  'panic_agora': 'Agorafobia',
  'panic_attacks': 'Pânico',
  'parestesias': 'Pânico',
  'pensamento_morte': 'Depressão',
  'perde_objetos': 'TDAH',
  'performance_anxiety': 'Ansiedade',
  'peso_baixo': 'Alimentar',
  'planos_grandiosos': 'Bipolar',
  'poor_appetite_dysthymia': 'Depressão',
  'preocupacao_excessiva': 'Ansiedade',
  'preocupacao_saude': 'Somático',
  'psychomotor_changes': 'Depressão',
  'purging': 'Alimentar',
  'racing_thoughts': 'Bipolar',
  'rapid_speech': 'Bipolar',
  'reatividade_sensorial_atipica': 'TEA',
  'reducao_atividades': 'Substâncias',
  'reducao_sono': 'Bipolar',
  'reduced_sleep_hypomania': 'Bipolar',
  'reexperiencia': 'PTSD',
  'repetitive_behavior': 'TOC',
  'repetitive_movements': 'TEA',
  'restlessness': 'Ansiedade',
  'restricao_alimentar': 'Alimentar',
  'restricted_interests': 'TEA',
  'restrictive_eating': 'Alimentar',
  'risk_behavior': 'Bipolar',
  'routine_insistence': 'TEA',
  'self_evaluation_weight': 'Alimentar',
  'sensacao_sufocamento': 'Pânico',
  'sensory_sensitivity': 'TEA',
  'sentimento_inutilidade': 'Depressão',
  'shortness_of_breath': 'Pânico',
  'simetria_ordenacao': 'TOC',
  'sintomas_somaticos': 'Somático',
  'sleep_disturbance': 'Depressão',
  'sleep_disturbance_gad': 'Ansiedade',
  'sleep_maintenance': 'Sono',
  'sleep_onset': 'Sono',
  'sobresalto_acentuado': 'PTSD',
  'social_communication': 'TEA',
  'social_dysfunction': 'Psicótico',
  'social_fear': 'Ansiedade',
  'somatic_symptoms': 'Somático',
  'sonhos_angustia': 'PTSD',
  'sono_nao_restaurador': 'Sono',
  'sono_prejudicado': 'Ansiedade',
  'sonolencia_diurna': 'Sono',
  'startle_response': 'PTSD',
  'substance_craving': 'Substâncias',
  'sudorese': 'Pânico',
  'suicidal_ideation': 'Depressão',
  'symptom_persistence': 'Somático',
  'tensao_muscular': 'Ansiedade',
  'tolerance': 'Substâncias',
  'tolerancia_aumentada': 'Substâncias',
  'tontura_vertigem': 'Pânico',
  'traumatic_exposure': 'PTSD',
  'tremores': 'Pânico',
  'uso_prolongado': 'Substâncias',
  'uso_risco_fisico': 'Substâncias',
  'verificacao_repetitiva': 'TOC',
  'vomito_autoinduzido': 'Alimentar',
  'weight_fear': 'Alimentar',
  'withdrawal': 'Substâncias',
}

const GROUP_COLORS: Record<string, string> = {
  Depressão: '#1677ff', Ansiedade: '#52c41a', Pânico: '#ff4d4f',
  Bipolar: '#722ed1', TOC: '#fa8c16', PTSD: '#eb2f96',
  Substâncias: '#13c2c2', Alimentar: '#faad14', Sono: '#2f54eb',
  Psicótico: '#a0d911', Somático: '#f5222d', Agorafobia: '#1890ff',
  TEA: '#f759ab', TDAH: '#fa541c',
}

interface InferenceHistoryItem {
  consultation_uuid: string
  consultation_date: string
  disorder_name: string
  inference_probability: number
  confidence_level: number | null
  generated_by_model: string
}

interface CriterionWithSymptom extends DiagnosticCriteria {
  symptom_name?: string
}

export default function InferencePage() {
  const screens = useBreakpoint()
  const isMobile = !screens.md
  const { token } = theme.useToken()
  const navigate = useNavigate()
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [selectedPatient, setSelectedPatient] = useState<string>('')
  const [evidence, setEvidence] = useState<Record<string, boolean>>({})
  const [results, setResults] = useState<InferenceResult[]>([])
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<'bayesian' | 'criteria'>('criteria')
  const [history, setHistory] = useState<InferenceHistoryItem[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({})
  const disorderNameById = useRef<Record<number, string>>({})
  const disorderById = useRef<Record<number, Disorder>>({})

  const [detailVisible, setDetailVisible] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [disorderDetail, setDisorderDetail] = useState<Disorder | null>(null)
  const [detailCriteria, setDetailCriteria] = useState<CriterionWithSymptom[]>([])

  useEffect(() => {
    patientsApi.list(1, 100).then((data) => setPatients(data.patients))
    disordersApi.listSymptoms().then(setSymptoms)
    disordersApi.listDisorders({ limit: 600 }).then((data: any) => {
      const list: Disorder[] = data?.disorders || data || []
      const map: Record<number, string> = {}
      const byId: Record<number, Disorder> = {}
      for (const d of list) {
        map[d.disorder_id] = d.disorder_name
        byId[d.disorder_id] = d
      }
      disorderNameById.current = map
      disorderById.current = byId
    })
  }, [])

  const loadHistory = useCallback(async (patientUuid: string) => {
    if (!patientUuid) return
    setHistoryLoading(true)
    try {
      const data = await patientsApi.get(patientUuid)
      const puid = data.profile.profile_uuid
      if (!puid) return
      const consults = await consultationsApi.listByProfile(puid)
      const items: InferenceHistoryItem[] = []
      for (const c of consults.consultations || []) {
        try {
          const inf = await inferencesApi.listByConsultation(c.consultation_uuid)
          if (inf.inferences?.length) {
            for (const i of inf.inferences) {
              items.push({
                consultation_uuid: c.consultation_uuid,
                consultation_date: c.consultation_date,
                disorder_name: disorderNameById.current[i.disorder_id] ?? i.disorder_name ?? i.disorder?.disorder_name ?? '',
                inference_probability: i.inference_probability,
                confidence_level: i.confidence_level ?? null,
                generated_by_model: i.generated_by_model || '-',
              })
            }
          }
        } catch { /* skip consultations without inferences */ }
      }
      setHistory(items)
    } catch {
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  const toggleSymptom = (symptomName: string) => {
    setEvidence((prev) => ({ ...prev, [symptomName]: !prev[symptomName] }))
  }

  const handleRun = async () => {
    if (!selectedPatient) {
      message.warning('Selecione um paciente')
      return
    }
    const presentSymptoms = symptoms
      .filter((s) => evidence[s.symptom_name])
      .map((s) => ({ symptom_id: s.symptom_id, intensity: 7, frequency: 'daily' }))
    if (presentSymptoms.length === 0) {
      message.warning('Selecione pelo menos um sintoma')
      return
    }
    setLoading(true)
    try {
      const patientDetail = await patientsApi.get(selectedPatient)
      const puid = patientDetail.profile.profile_uuid
      if (!puid) throw new Error('Perfil do paciente não encontrado')
      const created = await consultationsApi.createWithData({
        profile_uuid: puid,
        consultation_date: new Date().toISOString(),
        symptom_observations: presentSymptoms,
      })
      const cuuid = created.consultation_uuid
      const res = mode === 'bayesian'
        ? await inferencesApi.runBayesian({ consultation_uuid: cuuid })
        : await inferencesApi.runCriteria({ consultation_uuid: cuuid })
      setResults(res.inferences)
      loadHistory(selectedPatient)
    } catch {
      message.error('Erro ao executar inferencia')
    } finally {
      setLoading(false)
    }
  }

  const openDisorderDetail = async (result: InferenceResult) => {
    const cached = disorderById.current[result.disorder_id]
    setDetailVisible(true)
    setDetailLoading(true)
    setDisorderDetail(cached ?? null)
    setDetailCriteria([])
    try {
      const symptomMap = new Map(symptoms.map((s) => [s.symptom_id, s.symptom_name]))
      const [disorder, criteriaRes] = await Promise.all([
        cached ?? disordersApi.get(result.disorder_id),
        disordersApi.getCriteria(result.disorder_id).catch(() => ({ criteria: [] })),
      ])
      setDisorderDetail(disorder as Disorder)
      const criteriaList: DiagnosticCriteria[] = criteriaRes?.criteria || []
      setDetailCriteria(
        criteriaList.map((c) => ({
          ...c,
          symptom_name: symptomMap.get(c.symptom_id) || `Sintoma #${c.symptom_id}`,
        }))
      )
    } catch {
      message.error('Não foi possível carregar os detalhes do transtorno')
    } finally {
      setDetailLoading(false)
    }
  }

  const topResults = [...results]
    .sort((a, b) => b.inference_probability - a.inference_probability)
    .slice(0, 5)

  // Sintomas marcados na inferência atual (para destacar critérios correspondentes)
  const presentSymptomIds = new Set(
    symptoms.filter((s) => evidence[s.symptom_name]).map((s) => s.symptom_id)
  )
  const presentSymptomNames = symptoms
    .filter((s) => evidence[s.symptom_name])
    .map((s) => s.symptom_description || s.symptom_name)
  const matchedCriteriaCount = detailCriteria.filter((c) => presentSymptomIds.has(c.symptom_id)).length

  const goToFullClassification = (disorderId: number) => {
    setDetailVisible(false)
    navigate(`/admin/disorders?disorder=${disorderId}`)
  }

  const groupedSymptoms: Record<string, Symptom[]> = {}
  symptoms.forEach((s) => {
    const group = SYMPTOM_GROUPS[s.symptom_name] || 'Outros'
    if (!groupedSymptoms[group]) groupedSymptoms[group] = []
    groupedSymptoms[group].push(s)
  })

  const toggleGroup = (group: string) => {
    setExpandedGroups((prev) => ({ ...prev, [group]: !prev[group] }))
  }

  const presentCount = (group: string) =>
    groupedSymptoms[group]?.filter((s) => evidence[s.symptom_name]).length || 0

  const renderDiagnosticSections = (d: Disorder) => {
    const items: any[] = []
    if (d.dsm_criteria) {
      items.push({
        key: 'dsm_criteria',
        label: 'Critérios DSM-5-TR',
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13, lineHeight: 1.6 }}>{d.dsm_criteria}</pre>,
      })
    }
    if (d.dsm_exclusions) {
      items.push({
        key: 'dsm_exclusions',
        label: 'Exclusões DSM-5-TR',
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13, lineHeight: 1.6 }}>{d.dsm_exclusions}</pre>,
      })
    }
    if (d.dsm_differentials) {
      items.push({
        key: 'dsm_differentials',
        label: 'Diagnóstico Diferencial DSM-5-TR',
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13, lineHeight: 1.6 }}>{d.dsm_differentials}</pre>,
      })
    }
    if (d.icd11_exclusions) {
      items.push({
        key: 'icd11_exclusions',
        label: 'Exclusões CID-11',
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13, lineHeight: 1.6 }}>{d.icd11_exclusions}</pre>,
      })
    }
    if (d.icd11_differentials) {
      items.push({
        key: 'icd11_differentials',
        label: 'Diagnóstico Diferencial CID-11',
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13, lineHeight: 1.6 }}>{d.icd11_differentials}</pre>,
      })
    }
    if (d.icd11_codes && d.icd11_codes.length > 0) {
      const icd = d.icd11_codes[0]
      const icdLines = [
        `Código: ${icd.icd11_code}`,
        icd.icd11_title ? `Título CID-11: ${icd.icd11_title}` : null,
        icd.chapter ? `Capítulo CID-11: ${icd.chapter}${icd.chapter_code ? ` (${icd.chapter_code})` : ''}` : null,
        icd.who_url ? `Referência OMS: ${icd.who_url}` : null,
        icd.clinical_description ? `\nDescrição Clínica:\n${icd.clinical_description}` : null,
        icd.diagnostic_requirements ? `\nRequisitos Diagnósticos:\n${icd.diagnostic_requirements}` : null,
      ].filter(Boolean).join('\n')
      items.push({
        key: 'icd11_codes',
        label: 'Informações CID-11',
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13, lineHeight: 1.6 }}>{icdLines}</pre>,
      })
    }
    return items.length > 0 ? <Collapse items={items} size="small" /> : null
  }

  const escapeHtml = (v: string) =>
    v.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  const detailDocumentCss = `
  body { font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; color: #1f1f1f; margin: 32px; line-height: 1.6; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  h2 { font-size: 15px; margin: 22px 0 6px; color: #0958d9; border-bottom: 1px solid #e8e8e8; padding-bottom: 4px; }
  pre { white-space: pre-wrap; font-family: inherit; font-size: 13px; margin: 0; }
  .meta { color: #595959; font-size: 12px; }
  .codes span { display: inline-block; border: 1px solid #d9d9d9; border-radius: 4px; padding: 0 6px; margin-right: 6px; font-size: 12px; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
  th, td { border: 1px solid #e8e8e8; padding: 6px 8px; text-align: left; vertical-align: top; }
  th { background: #fafafa; }
  tr.present td { background: #f6ffed; }
  .badge { background: #52c41a; color: #fff; border-radius: 8px; padding: 0 6px; font-size: 10px; }
  .summary { font-size: 12px; color: #595959; margin: 4px 0; }
  .disclaimer { margin-top: 28px; font-size: 11px; color: #8c8c8c; border-top: 1px solid #e8e8e8; padding-top: 8px; }
  `

  const buildDetailBodyHtml = (d: Disorder, criteria: CriterionWithSymptom[]) => {
    const icd = d.icd11_codes?.[0]
    const section = (title: string, body: string) =>
      `<section><h2>${escapeHtml(title)}</h2><pre>${escapeHtml(body)}</pre></section>`

    const blocks: string[] = []
    if (d.disorder_description) blocks.push(section('Descrição', d.disorder_description))
    if (d.dsm_criteria) blocks.push(section('Critérios DSM-5-TR', d.dsm_criteria))
    if (d.dsm_exclusions) blocks.push(section('Exclusões DSM-5-TR', d.dsm_exclusions))
    if (d.dsm_differentials) blocks.push(section('Diagnóstico Diferencial DSM-5-TR', d.dsm_differentials))
    if (d.icd11_exclusions) blocks.push(section('Exclusões CID-11', d.icd11_exclusions))
    if (d.icd11_differentials) blocks.push(section('Diagnóstico Diferencial CID-11', d.icd11_differentials))
    if (icd) {
      const icdLines = [
        `Código: ${icd.icd11_code}`,
        icd.icd11_title ? `Título CID-11: ${icd.icd11_title}` : '',
        icd.chapter ? `Capítulo CID-11: ${icd.chapter}${icd.chapter_code ? ` (${icd.chapter_code})` : ''}` : '',
        icd.who_url ? `Referência OMS: ${icd.who_url}` : '',
        icd.clinical_description ? `\nDescrição Clínica:\n${icd.clinical_description}` : '',
        icd.diagnostic_requirements ? `\nRequisitos Diagnósticos:\n${icd.diagnostic_requirements}` : '',
      ].filter(Boolean).join('\n')
      blocks.push(section('Informações CID-11', icdLines))
    }

    const rows = criteria.map((c) => {
      const matched = presentSymptomIds.has(c.symptom_id)
      return `<tr class="${matched ? 'present' : ''}">
        <td>${escapeHtml(c.symptom_name || `Sintoma #${c.symptom_id}`)}${matched ? ' <span class="badge">presente</span>' : ''}</td>
        <td>${c.required_presence ? 'Sim' : 'Não'}</td>
        <td>${c.minimum_duration_days ? `${c.minimum_duration_days} dias` : '-'}</td>
        <td>${escapeHtml(c.clinical_notes || '-')}</td>
      </tr>`
    }).join('')

    const criteriaTable = criteria.length > 0 ? `
      <section>
        <h2>Critérios Diagnósticos (Sintomas)</h2>
        <p class="summary">${matchedCriteriaCount} de ${criteria.length} critério(s) correspondem a sintomas marcados nesta inferência.</p>
        <table>
          <thead><tr><th>Sintoma</th><th>Obrigatório</th><th>Duração</th><th>Observações</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </section>` : ''

    const symptomList = presentSymptomNames.length > 0
      ? `<section><h2>Sintomas Marcados na Inferência (${presentSymptomNames.length})</h2><ul>${presentSymptomNames.map((s) => `<li>${escapeHtml(s)}</li>`).join('')}</ul></section>`
      : ''

    return `
  <h1>${escapeHtml(d.disorder_name)}</h1>
  <div class="codes">${[
    d.cid_code ? `<span>CID-10: ${escapeHtml(d.cid_code)}</span>` : '',
    d.dsm_code ? `<span>DSM-5-TR: ${escapeHtml(d.dsm_code)}</span>` : '',
    icd ? `<span>CID-11: ${escapeHtml(icd.icd11_code)}</span>` : '',
  ].filter(Boolean).join('')}</div>
  <p class="meta">${escapeHtml(d.dsm_chapter || '')}${d.dsm_chapter ? ' • ' : ''}Gerado em ${dayjs().format('DD/MM/YYYY HH:mm')} — M.I.N.D</p>
  ${blocks.join('\n')}
  ${symptomList}
  ${criteriaTable}
  <p class="disclaimer">Projeto de portfólio — não autorizado para uso clínico. Documento gerado a partir de dados sintéticos/referência DSM-5-TR e CID-11.</p>`
  }

  const buildDetailHtml = (d: Disorder, criteria: CriterionWithSymptom[]) =>
    `<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8" />
<title>${escapeHtml(d.disorder_name)} — M.I.N.D</title>
<style>${detailDocumentCss}</style></head>
<body>${buildDetailBodyHtml(d, criteria)}</body></html>`

  const exportDisorderDetail = () => {
    if (!disorderDetail) return
    const html = buildDetailHtml(disorderDetail, detailCriteria)
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transtorno-${disorderDetail.disorder_id}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    message.success('Detalhes exportados em HTML')
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Inferência Diagnóstica' }]} style={{ marginBottom: 16 }} />
      <Row gutter={16}>
        <Col xs={24} lg={10}>
          <Card title="Sintomas Observados" styles={{ body: { padding: 12 } }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              <Tag
                color={mode === 'bayesian' ? 'blue' : 'default'}
                style={{ cursor: 'pointer', padding: '4px 12px' }}
                onClick={() => setMode('bayesian')}
              >
                <ThunderboltOutlined /> Bayesiano
              </Tag>
              <Tag
                color={mode === 'criteria' ? 'purple' : 'default'}
                style={{ cursor: 'pointer', padding: '4px 12px' }}
                onClick={() => setMode('criteria')}
              >
                <SafetyOutlined /> Critérios DSM-5
              </Tag>
            </div>

            <Form layout="vertical" size="small">
              <Form.Item label="Paciente" style={{ marginBottom: 8 }}>
                <Select
                  showSearch
                  placeholder="Selecione o paciente..."
                  value={selectedPatient || undefined}
                  onChange={(v) => { setSelectedPatient(v); loadHistory(v) }}
                  options={patients.map((p) => ({ value: p.patient_uuid, label: p.full_name }))}
                />
              </Form.Item>
            </Form>

            <div style={{ maxHeight: isMobile ? 260 : 420, overflowY: 'auto' }}>
              {Object.entries(groupedSymptoms).map(([group, syms]) => (
                <div key={group} style={{ marginBottom: 4 }}>
                  <div
                    style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '6px 8px', cursor: 'pointer', borderRadius: 4,
                      background: presentCount(group) > 0 ? token.colorPrimaryBg : token.colorFillTertiary,
                      border: `1px solid ${token.colorBorderSecondary}`,
                    }}
                    onClick={() => toggleGroup(group)}
                  >
                    <Space>
                      <span style={{
                        display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                        background: GROUP_COLORS[group] || '#999',
                      }} />
                      <Text strong style={{ fontSize: 13 }}>{group}</Text>
                      <Tag style={{ fontSize: 11, lineHeight: '18px' }}>
                        {presentCount(group)}/{syms.length}
                      </Tag>
                    </Space>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {expandedGroups[group] ? '▲' : '▼'}
                    </Text>
                  </div>
                  {expandedGroups[group] && syms.map((s) => (
                    <div
                      key={s.symptom_id}
                      style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '4px 8px 4px 20px', borderBottom: `1px solid ${token.colorSplit}`,
                      }}
                    >
                      <Text style={{ fontSize: 13 }}>{s.symptom_description || s.symptom_name}</Text>
                      <Switch
                        checked={!!evidence[s.symptom_name]}
                        onChange={() => toggleSymptom(s.symptom_name)}
                        size="small"
                        checkedChildren="S"
                        unCheckedChildren="N"
                      />
                    </div>
                  ))}
                </div>
              ))}
            </div>

            <Button
              type="primary"
              icon={<ExperimentOutlined />}
              onClick={handleRun}
              loading={loading}
              block
              size="large"
              style={{ marginTop: 12 }}
            >
              Executar Inferência
            </Button>
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Space direction="vertical" style={{ width: '100%' }} size={12}>
            <Card
              title="Resultados da Inferência"
              size="small"
              extra={results.length > 0 ? (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Top {Math.min(5, results.length)} de {results.length}
                </Text>
              ) : null}
            >
              {results.length === 0 ? (
                <Text type="secondary">Selecione os sintomas e execute a inferência</Text>
              ) : (
                <>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 8, fontSize: 12 }}>
                    <FileSearchOutlined style={{ marginRight: 6 }} />
                    Exibindo os {Math.min(5, results.length)} transtornos mais prováveis. Clique em um transtorno para ver os detalhes.
                  </Text>
                  <Table
                    dataSource={topResults}
                    rowKey="disorder_id"
                    size="small"
                    pagination={false}
                    onRow={(record: InferenceResult) => ({
                      style: { cursor: 'pointer' },
                      onClick: () => openDisorderDetail(record),
                    })}
                    columns={[
                      { title: 'Transtorno', dataIndex: 'disorder_name', ellipsis: true },
                      {
                        title: (
                          <Space size={4}>
                            <span>Probabilidade</span>
                            <Tooltip title="Probabilidade calculada pelo modelo a partir dos sintomas observados">
                              <InfoCircleOutlined style={{ fontSize: 12, color: '#999' }} />
                            </Tooltip>
                          </Space>
                        ),
                        dataIndex: 'inference_probability',
                        width: 170,
                        render: (v: number) => (
                          <Progress
                            percent={Math.round(v * 100)}
                            size="small"
                            status={v >= 0.7 ? 'success' : v >= 0.4 ? 'active' : 'exception'}
                            format={(p) => `${p}%`}
                          />
                        ),
                      },
                      {
                        title: 'Confiança',
                        dataIndex: 'confidence_level',
                        width: 90,
                        render: (v: number) => v != null ? `${Math.round(v * 100)}%` : '-',
                      },
                      {
                        title: 'Códigos',
                        key: 'codes',
                        width: 130,
                        render: (_: unknown, r: InferenceResult) =>
                          [r.cid_code && <Tag key="cid" style={{ fontSize: 11 }}>{r.cid_code}</Tag>,
                           r.dsm_code && <Tag key="dsm" style={{ fontSize: 11 }}>{r.dsm_code}</Tag>]
                            .filter(Boolean),
                      },
                      {
                        title: '',
                        key: 'actions',
                        width: 48,
                        align: 'center' as const,
                        render: (_: unknown, r: InferenceResult) => (
                          <Tooltip title="Ver detalhes do transtorno">
                            <Button
                              type="text"
                              size="small"
                              icon={<FileSearchOutlined />}
                              onClick={(e) => {
                                e.stopPropagation()
                                openDisorderDetail(r)
                              }}
                            />
                          </Tooltip>
                        ),
                      },
                    ]}
                  />
                </>
              )}
            </Card>

            <Card
              title={<Space><HistoryOutlined /> Histórico de Inferências</Space>}
              size="small"
              extra={selectedPatient ? <Text type="secondary" style={{ fontSize: 12 }}>
                {history.length} registro(s)
              </Text> : null}
            >
              {!selectedPatient ? (
                <Text type="secondary">Selecione um paciente para ver o histórico</Text>
              ) : historyLoading ? (
                <Spin />
              ) : history.length === 0 ? (
                <Empty description="Nenhuma inferência anterior" image={Empty.PRESENTED_IMAGE_SIMPLE} />
              ) : (
                <Table
                  dataSource={history}
                  rowKey={(r) => `${r.consultation_uuid}-${r.disorder_name}`}
                  size="small"
                  pagination={{ pageSize: 5, size: 'small' }}
                  columns={[
                    {
                      title: 'Data', dataIndex: 'consultation_date', width: 110,
                      render: (v: string) => dayjs(v).format('DD/MM/YY'),
                    },
                    { title: 'Transtorno', dataIndex: 'disorder_name', ellipsis: true },
                    {
                      title: 'Prob.', dataIndex: 'inference_probability', width: 80,
                      render: (v: number) => `${Math.round(v * 100)}%`,
                    },
                    {
                      title: 'Modelo', dataIndex: 'generated_by_model', width: 100,
                      render: (v: string) => {
                        const isBayes = v.includes('bayesian')
                        return <Tag color={isBayes ? 'blue' : 'purple'} style={{ fontSize: 11 }}>
                          {isBayes ? 'Bayes' : 'Critérios'}
                        </Tag>
                      },
                    },
                  ]}
                />
              )}
            </Card>
          </Space>
        </Col>
      </Row>

      <Drawer
        title={(
          <Space direction="vertical" size={2}>
            <Text strong style={{ fontSize: 16 }}>{disorderDetail?.disorder_name || 'Detalhes do Transtorno'}</Text>
            {disorderDetail && (
              <Space size={4} wrap>
                {disorderDetail.cid_code && <Tag>{disorderDetail.cid_code}</Tag>}
                {disorderDetail.dsm_code && <Tag color="purple">{disorderDetail.dsm_code}</Tag>}
                {disorderDetail.icd11_codes?.[0] && <Tag color="green">{disorderDetail.icd11_codes[0].icd11_code}</Tag>}
                {disorderDetail.is_core && <Tag color="blue">Pipeline Clínico</Tag>}
              </Space>
            )}
          </Space>
        )}
        extra={disorderDetail ? (
          <Space size={4} className="no-print">
            <Tooltip title="Exportar detalhes (.html)">
              <Button size="small" icon={<DownloadOutlined />} onClick={exportDisorderDetail}>
                {isMobile ? null : 'Exportar'}
              </Button>
            </Tooltip>
            <Tooltip title="Imprimir / salvar como PDF">
              <Button size="small" icon={<PrinterOutlined />} onClick={() => window.print()}>
                {isMobile ? null : 'Imprimir'}
              </Button>
            </Tooltip>
          </Space>
        ) : null}
        placement="right"
        width={isMobile ? '100%' : 680}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
        destroyOnClose
      >
        {detailLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 48 }}>
            <Spin tip="Carregando detalhes..." />
          </div>
        ) : disorderDetail ? (
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            <Button
              type="link"
              size="small"
              icon={<LinkOutlined />}
              style={{ paddingLeft: 0 }}
              onClick={() => goToFullClassification(disorderDetail.disorder_id)}
            >
              Ver na classificação completa (DSM-5-TR / CID-11)
            </Button>

            {disorderDetail.dsm_chapter && <Tag color="geekblue">{disorderDetail.dsm_chapter}</Tag>}

            {disorderDetail.disorder_description && (
              <Card size="small" title="Descrição">
                <Text style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{disorderDetail.disorder_description}</Text>
              </Card>
            )}

            <Card size="small" title="Classificações">
              <Descriptions size="small" column={1} bordered>
                <Descriptions.Item label="CID-10">{disorderDetail.cid_code || '-'}</Descriptions.Item>
                <Descriptions.Item label="DSM-5-TR">{disorderDetail.dsm_code || '-'}</Descriptions.Item>
                <Descriptions.Item label="CID-11">
                  {disorderDetail.icd11_codes && disorderDetail.icd11_codes.length > 0
                    ? disorderDetail.icd11_codes.map((icd: ICD11Code) => icd.icd11_code).join(', ')
                    : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="Capítulo DSM-5-TR">{disorderDetail.dsm_chapter || '-'}</Descriptions.Item>
              </Descriptions>
            </Card>

            {renderDiagnosticSections(disorderDetail)}

            <Card
              size="small"
              title={(
                <Space size={6}>
                  <span>Critérios Diagnósticos (Sintomas)</span>
                  {detailCriteria.length > 0 && (
                    <Tag color={matchedCriteriaCount > 0 ? 'green' : 'default'} style={{ fontSize: 11 }}>
                      {matchedCriteriaCount}/{detailCriteria.length} na inferência
                    </Tag>
                  )}
                </Space>
              )}
            >
              {presentSymptomNames.length === 0 && (
                <Alert
                  type="info"
                  showIcon
                  style={{ marginBottom: 8 }}
                  message="Nenhum sintoma marcado na inferência atual — execute uma inferência para comparar os critérios."
                />
              )}
              {detailCriteria.length === 0 ? (
                <Text type="secondary">Nenhum critério cadastrado para este transtorno.</Text>
              ) : (
                <Table
                  dataSource={detailCriteria}
                  rowKey="criteria_id"
                  size="small"
                  pagination={false}
                  onRow={(r: CriterionWithSymptom) => presentSymptomIds.has(r.symptom_id)
                    ? { style: { background: token.colorSuccessBg } }
                    : {}}
                  columns={[
                    {
                      title: 'Sintoma',
                      dataIndex: 'symptom_name',
                      ellipsis: true,
                      render: (v: string, r: CriterionWithSymptom) => presentSymptomIds.has(r.symptom_id) ? (
                        <Space size={4}>
                          <CheckCircleOutlined style={{ color: token.colorSuccess }} />
                          <Text strong>{v}</Text>
                        </Space>
                      ) : v,
                    },
                    {
                      title: 'Na inferência',
                      key: 'present',
                      width: 120,
                      render: (_: unknown, r: CriterionWithSymptom) =>
                        presentSymptomIds.has(r.symptom_id)
                          ? <Tag color="green" style={{ fontSize: 11 }}>Presente</Tag>
                          : <Text type="secondary" style={{ fontSize: 12 }}>—</Text>,
                    },
                    {
                      title: 'Obrigatório',
                      dataIndex: 'required_presence',
                      width: 100,
                      render: (v: boolean) => v ? <Tag color="red">Sim</Tag> : <Tag>Não</Tag>,
                    },
                    {
                      title: 'Duração',
                      dataIndex: 'minimum_duration_days',
                      width: 90,
                      render: (v: number | null | undefined) => v ? `${v}d` : '-',
                    },
                    {
                      title: 'Observações',
                      dataIndex: 'clinical_notes',
                      ellipsis: true,
                      render: (v: string | null | undefined) => v || '-',
                    },
                  ]}
                />
              )}
            </Card>
          </Space>
        ) : (
          <Empty description="Nenhum detalhe disponível" />
        )}
      </Drawer>

      {disorderDetail && (
        <div
          id="mind-print-area"
          className="mind-print-only"
          dangerouslySetInnerHTML={{ __html: buildDetailBodyHtml(disorderDetail, detailCriteria) }}
        />
      )}
    </>
  )
}
