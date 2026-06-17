import { useEffect, useState, useCallback } from 'react'
import {
  Card, Table, Tag, Select, Space, Typography, Breadcrumb, Tooltip, Progress,
  Tabs, Row, Col, Statistic, Button, Alert, Divider, Spin,
} from 'antd'
import { WarningOutlined, CheckCircleOutlined, MedicineBoxOutlined, BulbOutlined } from '@ant-design/icons'
import { treatmentsApi } from '../../api/treatments'
import { medicationsApi } from '../../api/medications'
import { disordersApi } from '../../api/disorders'
import { patientsApi } from '../../api/patients'
import type {
  DisorderMedicationAssoc, MedicationStat, Medication, Disorder,
  TreatmentPrediction,
} from '../../types'

const { Title, Text } = Typography

const STRENGTH_COLORS: Record<string, string> = {
  A: 'green', B: 'blue', C: 'orange', D: 'red',
}
const STRENGTH_LABELS: Record<string, string> = {
  A: 'Evidência Forte', B: 'Evidência Moderada', C: 'Evidência Limitada', D: 'Opinião de Especialista',
}
const LINE_LABELS: Record<string, string> = {
  '1': '1ª Linha', '2': '2ª Linha', '3': '3ª Linha', '4': '4ª Linha / Resgate',
}

function probColor(v: number): string {
  if (v >= 0.65) return '#52c41a'
  if (v >= 0.45) return '#1677ff'
  return '#ff4d4f'
}

function probStatus(v: number): 'success' | 'active' | 'exception' {
  if (v >= 0.65) return 'success'
  if (v >= 0.45) return 'active'
  return 'exception'
}

export default function TreatmentEfficacyPage() {
  const [assocs, setAssocs] = useState<DisorderMedicationAssoc[]>([])
  const [medications, setMedications] = useState<Medication[]>([])
  const [disorders, setDisorders] = useState<Disorder[]>([])
  const [patients, setPatients] = useState<{ patient_uuid: string; full_name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDisorder, setSelectedDisorder] = useState<number | undefined>()
  const [selectedMedication, setSelectedMedication] = useState<number | undefined>()
  const [stats, setStats] = useState<MedicationStat[]>([])

  const [predPatient, setPredPatient] = useState<string>()
  const [predDisorder, setPredDisorder] = useState<number>()
  const [predictions, setPredictions] = useState<TreatmentPrediction[]>([])
  const [predicting, setPredicting] = useState(false)
  const [predicted, setPredicted] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const [a, m, d, p] = await Promise.all([
        treatmentsApi.listAssociations(),
        medicationsApi.list(),
        disordersApi.listDisorders(),
        patientsApi.list(1, 200),
      ])
      setAssocs(a)
      setMedications(m)
      setDisorders(d)
      setPatients(p.patients.map(p2 => ({ patient_uuid: p2.patient_uuid, full_name: p2.full_name })))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  useEffect(() => {
    if (selectedDisorder) {
      treatmentsApi.getStats(selectedDisorder).then(r => setStats(r.medication_stats)).catch(() => setStats([]))
    } else {
      setStats([])
    }
  }, [selectedDisorder])

  const filtered = assocs.filter(a => {
    if (selectedDisorder && a.disorder_id !== selectedDisorder) return false
    if (selectedMedication && a.medication_id !== selectedMedication) return false
    return true
  })

  const handlePredict = async () => {
    if (!predPatient || !predDisorder) return
    setPredicting(true)
    setPredicted(false)
    try {
      const medIds = medications.map(m => m.medication_id)
      const result = await treatmentsApi.predict(predPatient, predDisorder, medIds)
      setPredictions(result.predictions.sort((a, b) => b.success_probability - a.success_probability))
      setPredicted(true)
    } catch {
      // handle error
    } finally {
      setPredicting(false)
    }
  }

  const mapColumns = [
    {
      title: 'Medicamento', width: 200,
      sorter: (a: DisorderMedicationAssoc, b: DisorderMedicationAssoc) =>
        (a.medication?.name || '').localeCompare(b.medication?.name || '', 'pt-BR'),
      render: (_: unknown, r: DisorderMedicationAssoc) => (
        <Text strong>{r.medication?.name || '-'}</Text>
      ),
    },
    {
      title: 'Transtorno', width: 280,
      sorter: (a: DisorderMedicationAssoc, b: DisorderMedicationAssoc) =>
        (a.disorder_name || '').localeCompare(b.disorder_name || '', 'pt-BR'),
      render: (_: unknown, r: DisorderMedicationAssoc) => r.disorder_name || '-',
    },
    {
      title: 'Taxa de Sucesso', width: 160,
      sorter: (a: DisorderMedicationAssoc, b: DisorderMedicationAssoc) =>
        (a.success_rate || 0) - (b.success_rate || 0),
      render: (_: unknown, r: DisorderMedicationAssoc) => {
        if (r.success_rate == null) return '-'
        return (
          <Tooltip title={`${(r.success_rate * 100).toFixed(0)}% literatura`}>
            <Progress percent={Math.round(r.success_rate * 100)} size="small"
              strokeColor={r.success_rate >= 0.65 ? '#52c41a' : r.success_rate >= 0.50 ? '#faad14' : '#ff4d4f'} />
          </Tooltip>
        )
      },
    },
    {
      title: 'Falha', width: 70,
      render: (_: unknown, r: DisorderMedicationAssoc) => {
        if (r.failure_rate == null) return '-'
        return <Text type="danger">{(r.failure_rate * 100).toFixed(0)}%</Text>
      },
    },
    {
      title: 'Resposta', width: 100,
      render: (_: unknown, r: DisorderMedicationAssoc) => {
        if (!r.avg_response_weeks) return '-'
        return `${r.avg_response_weeks.toFixed(1)} sem`
      },
    },
    {
      title: 'Linha', width: 80,
      render: (_: unknown, r: DisorderMedicationAssoc) => {
        if (!r.line_of_treatment) return '-'
        return <Tag>{LINE_LABELS[String(r.line_of_treatment)]}</Tag>
      },
    },
    {
      title: 'Evidência', width: 90,
      render: (_: unknown, r: DisorderMedicationAssoc) => {
        if (!r.recommendation_strength) return '-'
        return (
          <Tooltip title={STRENGTH_LABELS[r.recommendation_strength]}>
            <Tag color={STRENGTH_COLORS[r.recommendation_strength] || 'default'}>{r.recommendation_strength}</Tag>
          </Tooltip>
        )
      },
    },
    { title: 'Observações', ellipsis: true, render: (_: unknown, r: DisorderMedicationAssoc) => r.notes || '-' },
  ]

  return (
    <>
      <Breadcrumb items={[
        { title: 'Dashboard' },
        { title: 'Eficácia de Medicamentos' },
      ]} style={{ marginBottom: 16 }} />
      <Tabs defaultActiveKey="map" items={[
        {
          key: 'map',
          label: 'Mapa Medicamento-Transtorno',
          children: (
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <Title level={4} style={{ margin: 0 }}>Mapa de Eficácia</Title>
                <Space>
                  <Select allowClear placeholder="Filtrar Transtorno" style={{ width: 280 }}
                    value={selectedDisorder} onChange={setSelectedDisorder}
                    options={disorders.map(d => ({ value: d.disorder_id, label: d.disorder_name }))}
                    showSearch filterOption={(input, option) =>
                      (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
                  />
                  <Select allowClear placeholder="Filtrar Medicamento" style={{ width: 240 }}
                    value={selectedMedication} onChange={setSelectedMedication}
                    options={medications.map(m => ({ value: m.medication_id, label: m.name }))}
                    showSearch filterOption={(input, option) =>
                      (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
                  />
                </Space>
              </div>
              <Table dataSource={filtered} columns={mapColumns} rowKey="dm_id"
                loading={loading} pagination={{ pageSize: 25, showTotal: (t: number) => `${t} associações` }}
                size="small" />
            </Card>
          ),
        },
        {
          key: 'predict',
          label: <span><BulbOutlined /> Predizer Eficácia (ML)</span>,
          children: (
            <Card>
              <Title level={4} style={{ marginBottom: 16 }}>Predição de Eficácia por Paciente</Title>
              <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
                Selecione um paciente e um diagnóstico para obter a probabilidade de sucesso
                de cada medicamento, combinando dados da literatura com resultados reais.
              </Text>
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} md={8}>
                  <Select showSearch placeholder="Selecionar Paciente" style={{ width: '100%' }}
                    value={predPatient} onChange={v => { setPredPatient(v); setPredicted(false) }}
                    filterOption={(input, option) =>
                      (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
                    options={patients.map(p => ({ value: p.patient_uuid, label: p.full_name }))} />
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Select showSearch placeholder="Selecionar Transtorno" style={{ width: '100%' }}
                    value={predDisorder} onChange={v => { setPredDisorder(v); setPredicted(false) }}
                    filterOption={(input, option) =>
                      (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
                    options={disorders.map(d => ({ value: d.disorder_id, label: d.disorder_name }))} />
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Button type="primary" icon={<BulbOutlined />} onClick={handlePredict}
                    loading={predicting} disabled={!predPatient || !predDisorder}
                    size="large" block>
                    Predizer Eficácia
                  </Button>
                </Col>
              </Row>

              {predicting && <Spin tip="Calculando predições..." style={{ display: 'block', textAlign: 'center', padding: 40 }} />}

              {predicted && predictions.length > 0 && (
                <>
                  <Divider />
                  <Alert
                    type="info"
                    showIcon
                    message="Resultado da Predição ML"
                    description={`Medicamentos ordenados por probabilidade de sucesso para ${patients.find(p => p.patient_uuid === predPatient)?.full_name || ''} com ${disorders.find(d => d.disorder_id === predDisorder)?.disorder_name || ''}. O modelo combina eficácia da literatura (DisorderMedication) com resultados reais de tratamento (TreatmentOutcome).`}
                    style={{ marginBottom: 16 }}
                  />
                  <Row gutter={[16, 16]}>
                    {predictions.slice(0, 20).map(p => (
                      <Col xs={24} sm={12} md={8} lg={6} key={p.medication_id}>
                        <Card
                          size="small"
                          title={<Text strong>{p.medication_name}</Text>}
                          extra={
                            p.recommendation_strength
                              ? <Tag color={STRENGTH_COLORS[p.recommendation_strength] || 'default'}>
                                  {p.recommendation_strength}
                                </Tag>
                              : undefined
                          }
                          style={{ borderLeft: `4px solid ${probColor(p.success_probability)}` }}
                        >
                          <Statistic
                            title="Probabilidade de Sucesso"
                            value={p.success_probability * 100}
                            precision={1}
                            suffix="%"
                            valueStyle={{ color: probColor(p.success_probability) }}
                          />
                          <Progress
                            percent={Math.round(p.success_probability * 100)}
                            status={probStatus(p.success_probability)}
                            size="small"
                            style={{ marginTop: 8 }}
                          />
                          {p.expected_response_weeks && (
                            <Text type="secondary" style={{ display: 'block', marginTop: 8, fontSize: 12 }}>
                              Resposta esperada: ~{p.expected_response_weeks.toFixed(0)} semanas
                            </Text>
                          )}
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </>
              )}

              {predicted && predictions.length === 0 && (
                <Alert type="warning" message="Nenhuma predição disponível" description="Não foram encontrados dados de eficácia para esta combinação de paciente e transtorno." />
              )}
            </Card>
          ),
        },
        {
          key: 'stats',
          label: 'Resultados Reais',
          children: (
            <Row gutter={16}>
              <Col span={24} style={{ marginBottom: 16 }}>
                <Card>
                  <Space>
                    <Select allowClear placeholder="Selecionar Transtorno" style={{ width: 350 }}
                      value={selectedDisorder} onChange={setSelectedDisorder}
                      options={disorders.map(d => ({ value: d.disorder_id, label: d.disorder_name }))}
                      showSearch filterOption={(input, option) =>
                        (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
                    />
                    <Text type="secondary">
                      {selectedDisorder
                        ? `Resultados para ${disorders.find(d => d.disorder_id === selectedDisorder)?.disorder_name || ''}`
                        : 'Selecione um transtorno para ver resultados reais'}
                    </Text>
                  </Space>
                </Card>
              </Col>
              {stats.map(s => (
                <Col xs={24} sm={12} md={8} lg={6} key={s.medication_id}>
                  <Card size="small" title={s.medication_name} style={{ borderLeft: `4px solid ${probColor(s.success_rate)}` }}>
                    <Row gutter={[8, 8]}>
                      <Col span={12}>
                        <Statistic title="Sucesso" value={s.success_rate * 100} suffix="%" precision={0}
                          valueStyle={{ color: probColor(s.success_rate) }} />
                      </Col>
                      <Col span={12}>
                        <Statistic title="Casos" value={s.total_cases} />
                      </Col>
                      <Col span={12}>
                        <Statistic title="Piora" value={s.worsened_count} valueStyle={{ color: '#cf1322' }} />
                      </Col>
                      <Col span={12}>
                        <Statistic title="Descont." value={s.discontinued_count} valueStyle={{ color: '#faad14' }} />
                      </Col>
                      {s.avg_response_weeks && (
                        <Col span={24}>
                          <Text type="secondary">Resposta: {s.avg_response_weeks.toFixed(1)} semanas</Text>
                        </Col>
                      )}
                    </Row>
                  </Card>
                </Col>
              ))}
              {!stats.length && selectedDisorder && (
                <Col span={24}><Card><Text type="secondary">Nenhum resultado de tratamento registrado.</Text></Card></Col>
              )}
            </Row>
          ),
        },
        {
          key: 'outcomes',
          label: 'Histórico de Outcomes',
          children: <OutcomesTab treatmentsApi={treatmentsApi} medications={medications} />,
        },
      ]} />
    </>
  )
}

function OutcomesTab({ treatmentsApi: api, medications }: { treatmentsApi: typeof treatmentsApi; medications: Medication[] }) {
  const [outcomes, setOutcomes] = useState<import('../../types').TreatmentOutcomeItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.listOutcomes().then(setOutcomes).finally(() => setLoading(false))
  }, [])

  const cols = [
    { title: 'Medicação', width: 160, dataIndex: ['medication', 'name'], sorter: (a: any, b: any) => (a.medication?.name || '').localeCompare(b.medication?.name || '') },
    { title: 'Transtorno', width: 200, dataIndex: 'disorder_name', ellipsis: true },
    {
      title: 'Resultado', width: 130,
      render: (_: unknown, r: any) => {
        const colors: Record<string, string> = { improved: 'green', remission: 'blue', no_change: 'orange', worsened: 'red', discontinued: 'default' }
        const labels: Record<string, string> = { improved: 'Melhora', remission: 'Remissão', no_change: 'Sem mudança', worsened: 'Piora', discontinued: 'Descontinuado' }
        return <Tag color={colors[r.outcome] || 'default'}>{labels[r.outcome] || r.outcome}</Tag>
      },
    },
    { title: 'Início', width: 100, dataIndex: 'start_date' },
    { title: 'Adesão', width: 90, dataIndex: 'adherence', render: (v: string) => v ? <Tag>{v}</Tag> : '-' },
    { title: 'Semanas Resposta', width: 130, dataIndex: 'response_weeks', render: (v: number) => v ? `${v.toFixed(1)} sem` : '-' },
    { title: 'Efeitos Colaterais', width: 160, dataIndex: 'side_effects', ellipsis: true, render: (v: string) => v ? <Text type="warning">{v}</Text> : '-' },
  ]

  return (
    <Card>
      <Table dataSource={outcomes} columns={cols} rowKey="outcome_uuid" loading={loading}
        pagination={{ pageSize: 20, showTotal: (t: number) => `${t} outcomes` }} size="small" />
    </Card>
  )
}
