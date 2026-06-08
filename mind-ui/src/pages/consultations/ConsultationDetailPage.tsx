import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card, Descriptions, Table, Tag, Spin, Typography, Breadcrumb, Progress, Space, Divider,
  Button, Row, Col, Collapse, Alert, Tooltip,
} from 'antd'
import {
  ThunderboltOutlined, BulbOutlined, ReloadOutlined, InfoCircleOutlined, FileTextOutlined,
} from '@ant-design/icons'
import { consultationsApi } from '../../api/consultations'
import { inferencesApi } from '../../api/inferences'
import { medicationsApi } from '../../api/medications'
import type { ConsultationResponse, InferenceResponse, ScaleResponseResponse, ConsultationCompleteness, Prescription } from '../../types'
import { scalesApi } from '../../api/scales'
import type { AssessmentScale } from '../../types'

const { Title, Text } = Typography

function probabilityColor(v: number): string {
  if (v >= 0.7) return '#52c41a'
  if (v >= 0.4) return '#1677ff'
  return '#ff4d4f'
}

function probabilityStatus(v: number): 'success' | 'active' | 'exception' {
  if (v >= 0.7) return 'success'
  if (v >= 0.4) return 'active'
  return 'exception'
}

const DISORDER_PT_MAP: Record<string, { name: string; abbr: string }> = {
  'MDD': { name: 'Transtorno Depressivo Maior', abbr: 'TDM' },
  'GAD': { name: 'Transtorno de Ansiedade Generalizada', abbr: 'TAG' },
  'PANIC': { name: 'Transtorno do Pânico', abbr: 'TP' },
  'AGORAPHOBIA': { name: 'Agorafobia', abbr: 'AGO' },
  'BIPOLAR': { name: 'Transtorno Bipolar', abbr: 'TB' },
  'OCD': { name: 'Transtorno Obsessivo-Compulsivo', abbr: 'TOC' },
  'PTSD': { name: 'Transtorno de Estresse Pós-Traumático', abbr: 'TEPT' },
  'SUD': { name: 'Transtorno por Uso de Substâncias', abbr: 'TUS' },
  'ANOREXIA': { name: 'Anorexia Nervosa', abbr: 'AN' },
  'BULIMIA': { name: 'Bulimia Nervosa', abbr: 'BN' },
  'BED': { name: 'Transtorno de Compulsão Alimentar', abbr: 'TCAP' },
  'INSOMNIA': { name: 'Transtorno de Insônia', abbr: 'TI' },
  'PSYCHOTIC': { name: 'Transtorno Psicótico', abbr: 'TPS' },
  'SOMATIC': { name: 'Transtorno de Sintomas Somáticos', abbr: 'TSS' },
  'ASD': { name: 'Transtorno do Espectro Autista', abbr: 'TEA' },
  'ADHD': { name: 'Transtorno de Déficit de Atenção/Hiperatividade', abbr: 'TDAH' },
}

export default function ConsultationDetailPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const [consultation, setConsultation] = useState<ConsultationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [runningCriteria, setRunningCriteria] = useState(false)
  const [runningBayesian, setRunningBayesian] = useState(false)
  const [criteriaResult, setCriteriaResult] = useState<InferenceResponse | null>(null)
  const [bayesianResult, setBayesianResult] = useState<InferenceResponse | null>(null)
  const [scales, setScales] = useState<AssessmentScale[]>([])
  const [scaleScores, setScaleScores] = useState<Record<string, { total: number; severity: string }>>({})
  const [completeness, setCompleteness] = useState<ConsultationCompleteness | null>(null)
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])
  const navigate = useNavigate()

  const fetchConsultation = useCallback(() => {
    if (!uuid) return
    setLoading(true)
    Promise.all([
      consultationsApi.get(uuid),
      scalesApi.list(0, 100),
      consultationsApi.getCompleteness(uuid),
      medicationsApi.listPrescriptions(uuid),
    ]).then(([c, sc, comp, rx]) => {
      setConsultation(c)
      setScales(sc.scales)
      computeScaleScores(c.scale_responses || [], sc.scales)
      setCompleteness(comp)
      setPrescriptions(rx)
    }).finally(() => setLoading(false))
  }, [uuid])

  useEffect(() => { fetchConsultation() }, [fetchConsultation])

  const SCALE_DISORDER_MAP: Record<string, string> = {
    'PHQ-9': 'Depressão',
    'GAD-7': 'Ansiedade',
    'MDQ': 'Transtorno Bipolar',
    'PCL-5': 'TEPT',
    'Y-BOCS': 'TOC',
    'AUDIT': 'Transtornos por Álcool',
    'ASRM': 'Mania',
    'ASRS': 'TDAH',
    'AQ-10': 'Espectro Autista',
  }

  const computeScaleScores = (responses: ScaleResponseResponse[], allScales: AssessmentScale[]) => {
    const scores: Record<string, { total: number; severity: string; disorder: string }> = {}
    const qToScale: Record<number, string> = {}
    for (const scale of allScales) {
      for (const q of scale.questions) {
        qToScale[q.question_id] = scale.scale_name
      }
    }
    const grouped: Record<string, number[]> = {}
    for (const r of responses) {
      const name = qToScale[r.question_id] || 'unknown'
      if (!grouped[name]) grouped[name] = []
      grouped[name].push(r.response_value ?? 0)
    }
    for (const [name, vals] of Object.entries(grouped)) {
      const total = vals.reduce((a, b) => a + b, 0)
      let severity = '-'
      if (name === 'PHQ-9') {
        if (total >= 20) severity = 'Grave'
        else if (total >= 15) severity = 'Moderadamente grave'
        else if (total >= 10) severity = 'Moderado'
        else if (total >= 5) severity = 'Leve'
        else severity = 'Minimo'
      } else if (name === 'GAD-7') {
        if (total >= 15) severity = 'Grave'
        else if (total >= 10) severity = 'Moderado'
        else if (total >= 5) severity = 'Leve'
        else severity = 'Minimo'
      } else if (name === 'MDQ') {
        severity = total >= 7 ? 'Positivo' : 'Negativo'
      } else if (name === 'PCL-5') {
        if (total >= 56) severity = 'Grave'
        else if (total >= 45) severity = 'Moderado'
        else if (total >= 31) severity = 'Leve'
        else severity = 'Minimo'
      } else if (name === 'Y-BOCS') {
        if (total >= 32) severity = 'Extremo'
        else if (total >= 24) severity = 'Grave'
        else if (total >= 16) severity = 'Moderado'
        else if (total >= 8) severity = 'Leve'
        else severity = 'Minimo'
      } else if (name === 'AUDIT') {
        if (total >= 20) severity = 'Dependencia'
        else if (total >= 16) severity = 'Prejudicial'
        else if (total >= 8) severity = 'Risco'
        else severity = 'Baixo risco'
      } else if (name === 'ASRM') {
        if (total >= 10) severity = 'Provavel mania'
        else if (total >= 6) severity = 'Possivel mania'
        else severity = 'Normal'
      } else if (name === 'ASRS') {
        if (total >= 24) severity = 'Alta'
        else if (total >= 17) severity = 'Moderada'
        else severity = 'Baixa'
      } else if (name === 'AQ-10') {
        severity = total >= 6 ? 'Positivo' : 'Negativo'
      }
      scores[name] = { total, severity, disorder: SCALE_DISORDER_MAP[name] || name }
    }
    setScaleScores(scores)
  }

  const handleRunCriteria = async () => {
    if (!uuid) return
    setRunningCriteria(true)
    try {
      const result = await inferencesApi.runCriteria({ consultation_uuid: uuid })
      setCriteriaResult(result)
    } catch {
      // silent
    } finally {
      setRunningCriteria(false)
    }
  }

  const handleRunBayesian = async () => {
    if (!uuid) return
    setRunningBayesian(true)
    try {
      const result = await inferencesApi.runBayesian({ consultation_uuid: uuid })
      setBayesianResult(result)
    } catch {
      // silent
    } finally {
      setRunningBayesian(false)
    }
  }

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  if (!consultation) return <Typography.Text type="danger">Consulta nao encontrada</Typography.Text>

  const professional = consultation.healthcare_professional
  const symptoms = consultation.symptom_observations || []
  const scaleResp = consultation.scale_responses || []
  const inferences = consultation.diagnostic_inferences || []

  return (
    <>
      <Breadcrumb
        items={[
          { title: 'Dashboard' },
          { title: 'Consultas', href: '/consultations' },
          { title: consultation.consultation_date.slice(0, 10) },
        ]}
        style={{ marginBottom: 16 }}
      />
      <Card>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={4} style={{ margin: 0 }}>Consulta - {consultation.consultation_date.slice(0, 10)}</Title>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                loading={runningCriteria}
                onClick={handleRunCriteria}
              >
                Avaliacao por Criterios
              </Button>
              <Button
                icon={<BulbOutlined />}
                loading={runningBayesian}
                onClick={handleRunBayesian}
              >
                Rede Bayesiana
              </Button>
            </Space>
          </Col>
        </Row>
        <Descriptions bordered column={2} size="small" style={{ marginTop: 12 }}>
          <Descriptions.Item label="UUID">{consultation.consultation_uuid}</Descriptions.Item>
          <Descriptions.Item label="Data">{consultation.consultation_date}</Descriptions.Item>
          {professional && (
            <>
              <Descriptions.Item label="Profissional">{professional.full_name}</Descriptions.Item>
              <Descriptions.Item label="Especialidade">{professional.specialty || '-'}</Descriptions.Item>
            </>
          )}
          <Descriptions.Item label="Observacoes" span={2}>
            {consultation.consultation_notes || 'Sem observacoes'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {completeness && (
        <Card size="small" style={{ marginTop: 16 }}>
          <Space align="center" style={{ width: '100%' }}>
            <Progress
              type="circle"
              percent={completeness.score}
              size={64}
              status={completeness.complete ? 'success' : 'active'}
              strokeColor={completeness.complete ? '#52c41a' : completeness.score >= 50 ? '#1677ff' : '#ff4d4f'}
            />
            <div style={{ flex: 1 }}>
              <Text strong style={{ fontSize: 15 }}>Integridade Clinica</Text>
              {completeness.missing.length > 0 && (
                <div style={{ marginTop: 4 }}>
                  {completeness.missing.map((m, i) => (
                    <Tag key={i} color="orange" style={{ marginBottom: 2 }}>{m}</Tag>
                  ))}
                </div>
              )}
              {completeness.complete && (
                <Tag color="green" style={{ marginTop: 4 }}>Prontuario completo</Tag>
              )}
            </div>
          </Space>
        </Card>
      )}

      {consultation.clinical_note && (
        <Card
          title={
            <Space>
              <FileTextOutlined />
              <Text strong>Documentação Clínica (SOAP)</Text>
            </Space>
          }
          size="small"
          style={{ marginTop: 16 }}
        >
          <Descriptions bordered column={2} size="small">
            {consultation.clinical_note.chief_complaint && (
              <Descriptions.Item label="Queixa Principal" span={2}>
                {consultation.clinical_note.chief_complaint}
              </Descriptions.Item>
            )}
            {consultation.clinical_note.history_present_illness && (
              <Descriptions.Item label="HDA" span={2}>
                {consultation.clinical_note.history_present_illness}
              </Descriptions.Item>
            )}
            {consultation.clinical_note.subjective_findings && (
              <Descriptions.Item label="Subjetivo (S)" span={2}>
                {consultation.clinical_note.subjective_findings}
              </Descriptions.Item>
            )}
            {consultation.clinical_note.objective_findings && (
              <Descriptions.Item label="Objetivo (O)" span={2}>
                {consultation.clinical_note.objective_findings}
              </Descriptions.Item>
            )}
            {consultation.clinical_note.clinical_assessment && (
              <Descriptions.Item label="Avaliacao (A)" span={2}>
                {consultation.clinical_note.clinical_assessment}
              </Descriptions.Item>
            )}
            {consultation.clinical_note.treatment_plan && (
              <Descriptions.Item label="Plano (P)" span={2}>
                {consultation.clinical_note.treatment_plan}
              </Descriptions.Item>
            )}
            {consultation.clinical_note.follow_up && (
              <Descriptions.Item label="Acompanhamento" span={2}>
                {consultation.clinical_note.follow_up}
              </Descriptions.Item>
            )}
          </Descriptions>
        </Card>
      )}

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="Observacoes de Sintomas" size="small">
            <Table
              dataSource={symptoms}
              rowKey="observation_id"
              size="small"
              pagination={false}
              columns={[
                { title: 'Sintoma', dataIndex: ['symptom', 'symptom_name'], ellipsis: true },
                { title: 'Intensidade', dataIndex: 'intensity', render: (v: number) => v != null ? `${v}/100` : '-' },
                { title: 'Frequencia', dataIndex: 'frequency', render: (v: string) => v || '-' },
                { title: 'Duracao', dataIndex: 'duration_days', render: (v: number) => v ? `${v}d` : '-' },
              ]}
              locale={{ emptyText: 'Nenhum sintoma' }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Pontuacao de Escalas" size="small">
            {Object.keys(scaleScores).length === 0 ? (
              <Text type="secondary">Nenhuma escala respondida</Text>
            ) : (
              <Table
                dataSource={Object.entries(scaleScores).map(([name, sc]) => ({ name, ...sc }))}
                rowKey="name"
                size="small"
                pagination={false}
                columns={[
                  { title: 'Escala', dataIndex: 'name' },
                  { title: 'Transtorno', dataIndex: 'disorder', ellipsis: true },
                  { title: 'Total', dataIndex: 'total', width: 80 },
                  {
                    title: 'Gravidade',
                    dataIndex: 'severity',
                    width: 180,
                    render: (v: string) => {
                      const colorMap: Record<string, string> = {
                        'Grave': 'red', 'Extremo': 'red', 'Provavel mania': 'red',
                        'Moderado': 'orange', 'Moderadamente grave': 'orange', 'Risco': 'orange',
                        'Moderada': 'orange',
                        'Leve': 'blue', 'Possivel mania': 'blue', 'Positivo': 'gold',
                        'Minimo': 'green', 'Normal': 'green', 'Negativo': 'green',
                        'Baixa': 'green', 'Baixo risco': 'green', 'Dependencia': 'red',
                        'Prejudicial': 'orange', 'Alta': 'red',
                      }
                      return <Tag color={colorMap[v] || 'default'}>{v}</Tag>
                    },
                  },
                ]}
              />
            )}
          </Card>
        </Col>
      </Row>

      {criteriaResult && criteriaResult.inferences.length > 0 && (
        <Card
          title={
            <Space>
              <ThunderboltOutlined />
              <Text strong>Avaliacao por Criterios Diagnosticos (DSM-5-TR)</Text>
              <Tag>{criteriaResult.generated_by_model} v{criteriaResult.model_version}</Tag>
            </Space>
          }
          style={{ marginTop: 16 }}
          size="small"
          extra={
            criteriaResult.requires_human_review && (
              <Tooltip title="Resultado requer revisao clinica">
                <Tag color="warning" icon={<InfoCircleOutlined />}>Revisao obrigatoria</Tag>
              </Tooltip>
            )
          }
        >
          <Table
            dataSource={criteriaResult.inferences}
            rowKey="disorder_id"
            size="small"
            pagination={false}
            columns={[
              {
                title: 'Transtorno',
                dataIndex: 'disorder_name',
                render: (v: string, r) => {
                  const pt = DISORDER_PT_MAP[v]
                  return (
                    <Space direction="vertical" size={0}>
                      <Text strong>{pt ? `${pt.abbr} — ${pt.name}` : v}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {[r.cid_code && `CID: ${r.cid_code}`, r.dsm_code && `DSM: ${r.dsm_code}`].filter(Boolean).join(' | ')}
                      </Text>
                    </Space>
                  )
                },
              },
              {
                title: 'Probabilidade',
                dataIndex: 'inference_probability',
                width: 220,
                render: (v: number) => (
                  <Progress
                    percent={Math.round(v * 100)}
                    size="small"
                    status={probabilityStatus(v)}
                    strokeColor={probabilityColor(v)}
                    format={(p) => `${p}%`}
                  />
                ),
              },
              {
                title: 'Confianca',
                dataIndex: 'confidence_level',
                width: 120,
                render: (v: number) => v != null ? `${Math.round(v * 100)}%` : '-',
              },
            ]}
          />
        </Card>
      )}

      {bayesianResult && bayesianResult.inferences.length > 0 && (
        <Card
          title={
            <Space>
              <BulbOutlined />
              <Text strong>Inferencia por Rede Bayesiana</Text>
              <Tag>{bayesianResult.generated_by_model} v{bayesianResult.model_version}</Tag>
            </Space>
          }
          style={{ marginTop: 16 }}
          size="small"
          extra={
            bayesianResult.requires_human_review && (
              <Tag color="warning" icon={<InfoCircleOutlined />}>Revisao obrigatoria</Tag>
            )
          }
        >
          <Table
            dataSource={bayesianResult.inferences}
            rowKey="disorder_id"
            size="small"
            pagination={false}
            columns={[
              {
                title: 'Transtorno',
                dataIndex: 'disorder_name',
                render: (v: string, r) => {
                  const pt = DISORDER_PT_MAP[v]
                  return (
                    <Space direction="vertical" size={0}>
                      <Text strong>{pt ? `${pt.abbr} — ${pt.name}` : v}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {[r.cid_code && `CID: ${r.cid_code}`, r.dsm_code && `DSM: ${r.dsm_code}`].filter(Boolean).join(' | ')}
                      </Text>
                    </Space>
                  )
                },
              },
              {
                title: 'Probabilidade',
                dataIndex: 'inference_probability',
                width: 220,
                render: (v: number) => (
                  <Progress
                    percent={Math.round(v * 100)}
                    size="small"
                    status={probabilityStatus(v)}
                    strokeColor={probabilityColor(v)}
                    format={(p) => `${p}%`}
                  />
                ),
              },
              {
                title: 'Confianca',
                dataIndex: 'confidence_level',
                width: 120,
                render: (v: number) => v != null ? `${Math.round(v * 100)}%` : '-',
              },
            ]}
          />
        </Card>
      )}

      {!criteriaResult && !bayesianResult && inferences.length === 0 && (
        <Card style={{ marginTop: 16 }}>
          <Alert
            type="info"
            message="Avaliacao Clinica nao iniciada"
            description="Clique em 'Avaliacao por Criterios' ou 'Rede Bayesiana' para calcular as probabilidades diagnosticas com base nos sintomas e escalas registrados."
            showIcon
          />
        </Card>
      )}

      {scaleResp.length > 0 && (
        <Collapse
          items={[{
            key: 'raw-responses',
            label: 'Respostas Originais das Escalas',
            children: (
              <Table
                dataSource={scaleResp}
                rowKey="response_id"
                size="small"
                pagination={false}
                columns={[
                  { title: 'Questao ID', dataIndex: 'question_id', width: 100 },
                  { title: 'Valor', dataIndex: 'response_value', render: (v: number) => v ?? '-' },
                  { title: 'Resposta', dataIndex: 'response_text', ellipsis: true },
                ]}
              />
            ),
          }]}
          style={{ marginTop: 16 }}
        />
      )}

      {prescriptions.length > 0 && (
        <Card title="Prescrições" size="small" style={{ marginTop: 16 }}>
          {prescriptions.map((rx) => (
            <Card
              key={rx.prescription_uuid}
              size="small"
              type="inner"
              title={`Prescrição — ${rx.created_at?.slice(0, 10) || ''}`}
              style={{ marginBottom: 8 }}
              extra={
                <Button
                  size="small"
                  danger
                  onClick={async () => {
                    await medicationsApi.deletePrescription(rx.prescription_uuid)
                    setPrescriptions((prev) => prev.filter((p) => p.prescription_uuid !== rx.prescription_uuid))
                  }}
                >
                  Excluir
                </Button>
              }
            >
              {rx.notes && <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>{rx.notes}</Text>}
              <Table
                dataSource={rx.items}
                rowKey="item_uuid"
                size="small"
                pagination={false}
                columns={[
                  { title: 'Medicamento', dataIndex: ['medication', 'name'], ellipsis: true },
                  { title: 'Dosagem', dataIndex: 'dosage', width: 100 },
                  { title: 'Frequência', dataIndex: 'frequency', width: 120 },
                  { title: 'Via', dataIndex: 'route', width: 80, render: (v: string) => v || '-' },
                  { title: 'Duração', dataIndex: 'duration_days', width: 80, render: (v: number) => v ? `${v}d` : '-' },
                  { title: 'Observações', dataIndex: 'notes', ellipsis: true },
                ]}
                locale={{ emptyText: 'Nenhum item' }}
              />
            </Card>
          ))}
        </Card>
      )}
    </>
  )
}
