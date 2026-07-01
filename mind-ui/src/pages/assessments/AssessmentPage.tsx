import { useEffect, useState, useCallback } from 'react'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Space, Row, Col, Tag, Result, Spin, Divider, Table, Empty, Progress } from 'antd'
import { ExperimentOutlined, HistoryOutlined, SaveOutlined } from '@ant-design/icons'
import { scalesApi, patientsApi } from '../../api/endpoints'
import type { AssessmentScale, ScaleScoreResponse, PatientListItem } from '../../types'
import { SCALE_OPTIONS, SEVERITY_COLORS } from '../../utils/constants'
import dayjs from 'dayjs'

const { Title, Text } = Typography

interface PatientAssessment {
  scale_name: string
  consultation_uuid: string
  date: string
  total_score: number
}

export default function AssessmentPage() {
  const [scales, setScales] = useState<AssessmentScale[]>([])
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [selectedPatient, setSelectedPatient] = useState<string>('')
  const [selectedScale, setSelectedScale] = useState<AssessmentScale | null>(null)
  const [responses, setResponses] = useState<Record<number, number>>({})
  const [result, setResult] = useState<ScaleScoreResponse & { consultation_uuid?: string } | null>(null)
  const [history, setHistory] = useState<PatientAssessment[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [initLoading, setInitLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      scalesApi.list(),
      patientsApi.list(1, 100).then((d) => d.patients),
    ]).then(([scaleData, patientData]) => {
      setScales(scaleData.scales)
      setPatients(patientData)
    }).finally(() => setInitLoading(false))
  }, [])

  const loadHistory = useCallback(async (patientUuid: string) => {
    if (!patientUuid) return
    setHistoryLoading(true)
    try {
      const data = await scalesApi.patientHistory(patientUuid)
      setHistory(data.assessments || [])
    } catch {
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  const handlePatientChange = (uuid: string) => {
    setSelectedPatient(uuid)
    loadHistory(uuid)
  }

  const handleScaleSelect = (scaleName: string) => {
    const scale = scales.find((s) => s.scale_name === scaleName)
    setSelectedScale(scale || null)
    setResponses({})
    setResult(null)
  }

  const getSortedResponses = useCallback(() => {
    if (!selectedScale) return { questionIds: [] as number[], values: [] as number[] }
    const questionIds = [...selectedScale.questions].sort((a, b) => a.question_order - b.question_order).map((q) => q.question_id)
    const missing = questionIds.filter((id) => responses[id] === undefined)
    if (missing.length > 0) return { questionIds: [], values: [] }
    return { questionIds, values: questionIds.map((id) => responses[id]) }
  }, [selectedScale, responses])

  const handleScore = async () => {
    if (!selectedScale) return
    const { questionIds, values } = getSortedResponses()
    if (questionIds.length === 0) {
      message.warning('Responda todas as questões antes de pontuar')
      return
    }
    setLoading(true)
    try {
      const res = await scalesApi.score({
        scale_name: selectedScale.scale_name,
        responses: values,
      })
      setResult(res)
    } catch {
      message.error('Erro ao calcular pontuação')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveScore = async () => {
    if (!selectedScale || !selectedPatient) return
    const { questionIds, values } = getSortedResponses()
    if (questionIds.length === 0) {
      message.warning('Responda todas as questões antes de salvar')
      return
    }
    setSaving(true)
    try {
      const res = await scalesApi.apply(selectedPatient, selectedScale.scale_name, values)
      setResult(res)
      message.success(`Avaliação salva na consulta ${res.consultation_uuid.slice(0, 8)}...`)
      if (selectedPatient) loadHistory(selectedPatient)
    } catch {
      message.error('Erro ao salvar avaliação')
    } finally {
      setSaving(false)
    }
  }

  const scaleOptions = scales.map((s) => ({
    value: s.scale_name,
    label: SCALE_OPTIONS[s.scale_name]?.label || s.scale_name,
  }))

  if (initLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Escalas de Avaliação' }]} style={{ marginBottom: 16 }} />
      <Row gutter={16}>
        <Col xs={24} lg={14}>
          <Card title="Avaliação Clínica" size="small">
            <Form layout="vertical" size="small">
              <Form.Item label="Paciente" style={{ marginBottom: 8 }}>
                <Select
                  showSearch
                  placeholder="Selecione o paciente..."
                  value={selectedPatient || undefined}
                  onChange={handlePatientChange}
                  options={patients.map((p) => ({ value: p.patient_uuid, label: p.full_name }))}
                  allowClear
                  onClear={() => { setSelectedPatient(''); setHistory([]) }}
                />
              </Form.Item>
              <Form.Item label="Escala" style={{ marginBottom: 8 }}>
                <Select
                  placeholder="Selecione uma escala"
                  options={scaleOptions}
                  onChange={handleScaleSelect}
                  value={selectedScale?.scale_name || undefined}
                  allowClear
                  onClear={() => { setSelectedScale(null); setResult(null) }}
                />
              </Form.Item>
            </Form>

            {selectedScale && (
              <div>
                <Divider style={{ margin: '8px 0' }} />
                <Text strong style={{ fontSize: 14 }}>{SCALE_OPTIONS[selectedScale.scale_name]?.label || selectedScale.scale_name}</Text>
                {selectedScale.questions
                  .sort((a, b) => a.question_order - b.question_order)
                  .map((q) => {
                    const opts = SCALE_OPTIONS[selectedScale.scale_name]?.options || [
                      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
                    ]
                    return (
                      <div key={q.question_id} style={{ marginTop: 10 }}>
                        <Text style={{ fontSize: 13 }}>{q.question_order}. {q.question_text}</Text>
                        <Select
                          style={{ width: '100%', marginTop: 4 }}
                          placeholder="Selecione..."
                          value={responses[q.question_id]}
                          onChange={(v) => setResponses({ ...responses, [q.question_id]: v })}
                          options={opts}
                        />
                      </div>
                    )
                  })}
                <Space style={{ marginTop: 12, width: '100%' }} direction="vertical">
                  <Button
                    type="primary"
                    icon={<ExperimentOutlined />}
                    onClick={handleScore}
                    loading={loading}
                    block
                    size="large"
                    disabled={!selectedPatient}
                  >
                    Calcular Pontuação
                  </Button>
                  <Button
                    type="default"
                    icon={<SaveOutlined />}
                    onClick={handleSaveScore}
                    loading={saving}
                    block
                    size="large"
                    disabled={!selectedPatient}
                  >
                    Salvar e Pontuar
                  </Button>
                </Space>
              </div>
            )}
          </Card>

          {result && (
            <Card title="Resultado" size="small" style={{ marginTop: 12 }}>
              {result.consultation_uuid && (
                <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                  Consulta: {result.consultation_uuid}
                </Text>
              )}
              <Result
                status={result.severity === 'severe' || result.severity === 'moderate' ? 'warning' : 'success'}
                title={`${result.total_score} pontos`}
                subTitle={
                  <Tag color={SEVERITY_COLORS[result.severity]} style={{ fontSize: 16, padding: '4px 12px' }}>
                    {result.severity.toUpperCase()}
                  </Tag>
                }
              />
              <Text>{result.interpretation}</Text>
            </Card>
          )}
        </Col>

        <Col xs={24} lg={10}>
          <Card
            title={<Space><HistoryOutlined /> Histórico do Paciente</Space>}
            size="small"
            extra={history.length > 0 ? <Text type="secondary" style={{ fontSize: 12 }}>{history.length} registro(s)</Text> : null}
          >
            {!selectedPatient ? (
              <Text type="secondary">Selecione um paciente para ver o histórico</Text>
            ) : historyLoading ? (
              <Spin />
            ) : history.length === 0 ? (
              <Empty description="Nenhuma avaliação anterior" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <Table
                dataSource={history}
                rowKey={(r) => `${r.consultation_uuid}-${r.scale_name}`}
                size="small"
                pagination={{ pageSize: 8, size: 'small' }}
                columns={[
                  {
                    title: 'Data', dataIndex: 'date', width: 90,
                    render: (v: string) => dayjs(v).format('DD/MM'),
                  },
                  {
                    title: 'Escala', dataIndex: 'scale_name', width: 100, ellipsis: true,
                    render: (v: string) => SCALE_OPTIONS[v]?.label?.split(' (')[0] || v,
                  },
                  {
                    title: 'Pontuação', dataIndex: 'total_score', width: 80,
                    render: (v: number) => <Text strong>{v}</Text>,
                  },
                ]}
              />
            )}
          </Card>
        </Col>
      </Row>
    </>
  )
}
