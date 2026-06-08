import { useEffect, useState, useCallback } from 'react'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Row, Col, Table, Tag, Spin, Switch, Divider, Alert, Progress, Collapse, Tooltip, Empty } from 'antd'
import { ExperimentOutlined, ThunderboltOutlined, SafetyOutlined, HistoryOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { inferencesApi } from '../../api/inferences'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import { disordersApi } from '../../api/disorders'
import type { PatientListItem, Symptom, InferenceResult } from '../../types'
import dayjs from 'dayjs'

const { Title, Text } = Typography

const SYMPTOM_GROUPS: Record<string, string> = {
  humor_deprimido: 'Depressão',
  anhedonia: 'Depressão',
  alteracao_peso: 'Depressão',
  insonia_hipersonia: 'Depressão',
  agitacao_retardo: 'Depressão',
  fadiga: 'Depressão',
  sentimento_inutilidade: 'Depressão',
  concentracao: 'Depressão',
  pensamento_morte: 'Depressão',
  lentificacao: 'Depressão',
  hipersonia_atipica: 'Depressão',
  choro_frequente: 'Depressão',
  preocupacao_excessiva: 'Ansiedade',
  inquietacao: 'Ansiedade',
  tensao_muscular: 'Ansiedade',
  irritabilidade: 'Ansiedade',
  sono_prejudicado: 'Ansiedade',
  fadiga_constante: 'Ansiedade',
  palpitacoes: 'Pânico',
  sudorese: 'Pânico',
  tremores: 'Pânico',
  sensacao_sufocamento: 'Pânico',
  medo_morrer: 'Pânico',
  dor_peito: 'Pânico',
  nausea_abdominal: 'Pânico',
  tontura_vertigem: 'Pânico',
  parestesias: 'Pânico',
  desrealizacao: 'Pânico',
  medo_enlouquecer: 'Pânico',
  calafrios_ondas_calor: 'Pânico',
  medo_morrer_panico: 'Pânico',
  euforia: 'Bipolar',
  grandiosidade: 'Bipolar',
  logorreia: 'Bipolar',
  reducao_sono: 'Bipolar',
  fuga_ideias: 'Bipolar',
  comportamento_risco: 'Bipolar',
  hiperssexualidade: 'Bipolar',
  gastos_excessivos: 'Bipolar',
  planos_grandiosos: 'Bipolar',
  obsessoes: 'TOC',
  compulsoes: 'TOC',
  simetria_ordenacao: 'TOC',
  verificacao_repetitiva: 'TOC',
  lavagem_limpeza: 'TOC',
  contagem_ritualistica: 'TOC',
  acumulo_objetos: 'TOC',
  reexperiencia: 'PTSD',
  esquiva: 'PTSD',
  hipervigilancia: 'PTSD',
  sonhos_angustia: 'PTSD',
  flashbacks_dissociativos: 'PTSD',
  sobresalto_acentuado: 'PTSD',
  culpa_merito: 'PTSD',
  desesperanca_futuro: 'PTSD',
  amnésia_traumática: 'PTSD',
  crenças_negativas: 'PTSD',
  desejo_intenso: 'Substâncias',
  abstinencia_substancia: 'Substâncias',
  tolerancia_aumentada: 'Substâncias',
  uso_prolongado: 'Substâncias',
  reducao_atividades: 'Substâncias',
  dificuldade_controle: 'Substâncias',
  uso_risco_fisico: 'Substâncias',
  restricao_alimentar: 'Alimentar',
  compulsao_alimentar: 'Alimentar',
  vomito_autoinduzido: 'Alimentar',
  peso_baixo: 'Alimentar',
  medo_ganho_peso: 'Alimentar',
  distorcao_imagem: 'Alimentar',
  comer_oculto: 'Alimentar',
  dificuldade_iniciar_sono: 'Sono',
  despertar_precoce: 'Sono',
  sono_nao_restaurador: 'Sono',
  sonolencia_diurna: 'Sono',
  apneia_sono: 'Sono',
  movimento_pernas: 'Sono',
  delirios_persecutorios: 'Psicótico',
  alucinacoes_auditivas: 'Psicótico',
  alucinacoes_visuais: 'Psicótico',
  discurso_desorganizado: 'Psicótico',
  comportamento_desorganizado: 'Psicótico',
  negativismo_catatonico: 'Psicótico',
  embotamento_afetivo: 'Psicótico',
  sintomas_somaticos: 'Somático',
  preocupacao_saude: 'Somático',
  conversao_sensorial: 'Somático',
  medo_transporte: 'Agorafobia',
  medo_multidoes: 'Agorafobia',
  medo_lugares_abertos: 'Agorafobia',
  medo_lugares_fechados: 'Agorafobia',
  evitacao_fobica: 'Agorafobia',
  deficit_reciprocidade: 'TEA',
  deficit_comunicacao: 'TEA',
  deficit_relacionamento: 'TEA',
  interesses_restritos: 'TEA',
  rigidez_rotina: 'TEA',
  estereotipias: 'TEA',
  hipo_hiper_reatividade: 'TEA',
  desatencao: 'TDAH',
  distraibilidade_externa: 'TDAH',
  esquecimento_atividades: 'TDAH',
  inquietacao_motora: 'TDAH',
  incapacidade_quieto: 'TDAH',
  fala_excessiva: 'TDAH',
  dificuldade_esperar_vez: 'TDAH',
  interrompe_outros: 'TDAH',
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
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [selectedPatient, setSelectedPatient] = useState<string>('')
  const [evidence, setEvidence] = useState<Record<string, boolean>>({})
  const [results, setResults] = useState<InferenceResult[]>([])
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<'bayesian' | 'criteria'>('bayesian')
  const [history, setHistory] = useState<InferenceHistoryItem[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({})

  useEffect(() => {
    patientsApi.list(1, 100).then((data) => setPatients(data.patients))
    disordersApi.listSymptoms().then(setSymptoms)
  }, [])

  const loadHistory = useCallback(async (patientUuid: string) => {
    if (!patientUuid) return
    setHistoryLoading(true)
    try {
      const data = await patientsApi.get(patientUuid)
      const puid = data.profile.profile_uuid
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
                disorder_name: i.disorder?.disorder_name || 'N/A',
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
      .map((s) => ({ symptom_id: s.symptom_id, intensity: 50, frequency: 'daily' }))
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

            <div style={{ maxHeight: 420, overflowY: 'auto' }}>
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
                      <Text style={{ fontSize: 13 }}>{s.symptom_name}</Text>
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
