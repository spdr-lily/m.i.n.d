import { useEffect, useState, useCallback, useRef } from 'react'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Row, Col, Table, Tag, Spin, Switch, Divider, Alert, Progress, Collapse, Tooltip, Empty, Space, Grid } from 'antd'
import { ExperimentOutlined, ThunderboltOutlined, SafetyOutlined, HistoryOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { inferencesApi } from '../../api/inferences'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import { disordersApi } from '../../api/disorders'
import type { PatientListItem, Symptom, InferenceResult, Disorder } from '../../types'
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

export default function InferencePage() {
  const screens = useBreakpoint()
  const isMobile = !screens.md
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

  useEffect(() => {
    patientsApi.list(1, 100).then((data) => setPatients(data.patients))
    disordersApi.listSymptoms().then(setSymptoms)
    disordersApi.listDisorders().then((disorders) => {
      const map: Record<number, string> = {}
      for (const d of disorders) {
        map[d.disorder_id] = d.disorder_name
      }
      disorderNameById.current = map
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
      if (!puid) throw new Error('Perfil do paciente nao encontrado')
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
                      background: presentCount(group) > 0 ? '#f0f5ff' : '#fafafa',
                      border: '1px solid #f0f0f0',
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
                        padding: '4px 8px 4px 20px', borderBottom: '1px solid #f5f5f5',
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
            <Card title="Resultados da Inferência" size="small">
              {results.length === 0 ? (
                <Text type="secondary">Selecione os sintomas e execute a inferência</Text>
              ) : (
                <Table
                  dataSource={results}
                  rowKey="disorder_id"
                  size="small"
                  pagination={false}
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
                      width: 200,
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
                      width: 100,
                      render: (v: number) => v != null ? `${Math.round(v * 100)}%` : '-',
                    },
                    {
                      title: 'Códigos',
                      key: 'codes',
                      width: 140,
                      render: (_: unknown, r: InferenceResult) =>
                        [r.cid_code && <Tag key="cid" style={{ fontSize: 11 }}>{r.cid_code}</Tag>,
                         r.dsm_code && <Tag key="dsm" style={{ fontSize: 11 }}>{r.dsm_code}</Tag>]
                          .filter(Boolean),
                    },
                  ]}
                />
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
    </>
  )
}
