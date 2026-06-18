import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Tag, Button, Space, Typography, Breadcrumb, Spin, Table, List, Select, Row, Col } from 'antd'
import { CalendarOutlined, EditOutlined, HistoryOutlined, DownloadOutlined, PushpinFilled, FileTextOutlined, LineChartOutlined } from '@ant-design/icons'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import { reportsApi } from '../../api/reports'
import { scalesApi } from '../../api/scales'
import type { PatientResponse, ConsultationListItem, MedicalReport, ScaleHistoryItem } from '../../types'
import { SCALE_OPTIONS, NEURO_SCALES, CLINICAL_SCALES } from '../../utils/constants'

const API_BASE = import.meta.env.VITE_API_URL

function downloadUrl(url: string) {
  const a = document.createElement('a')
  a.href = url
  a.style.display = 'none'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const { Title, Text, Paragraph } = Typography

export default function PatientDetailPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const [patient, setPatient] = useState<PatientResponse | null>(null)
  const [consultations, setConsultations] = useState<ConsultationListItem[]>([])
  const [reports, setReports] = useState<MedicalReport[]>([])
  const [loading, setLoading] = useState(true)
  const [availableScales, setAvailableScales] = useState<string[]>([])
  const [selectedScale, setSelectedScale] = useState<string | null>(null)
  const [scaleHistory, setScaleHistory] = useState<ScaleHistoryItem[]>([])
  const [scaleLoading, setScaleLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!uuid) return
    Promise.all([
      patientsApi.get(uuid),
      consultationsApi.list(uuid),
      reportsApi.list(uuid),
      scalesApi.patientHistory(uuid).catch(() => ({ total: 0, assessments: [] })),
    ])
      .then(([p, c, r, h]) => {
        setPatient(p)
        setConsultations(c.consultations || [])
        setReports(r.filter(rpt => rpt.is_pinned))
        const scales = [...new Set(h.assessments.map((a: any) => a.scale_name))].sort()
        setAvailableScales(scales)
        if (scales.length > 0) setSelectedScale(scales[0])
      })
      .finally(() => setLoading(false))
  }, [uuid])

  useEffect(() => {
    if (!uuid || !selectedScale) return
    setScaleLoading(true)
    scalesApi.history(uuid, selectedScale)
      .then(setScaleHistory)
      .catch(() => setScaleHistory([]))
      .finally(() => setScaleLoading(false))
  }, [uuid, selectedScale])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  if (!patient) return <Typography.Text type="danger">Paciente nao encontrado</Typography.Text>

  const { identity, profile } = patient
  const sexo = profile.sex_type?.description || (profile.sex_type_id === 1 ? 'Masculino' : 'Feminino')

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Pacientes', href: '/patients' }, { title: identity.full_name }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <div>
            <Title level={4} style={{ marginBottom: 4 }}>{identity.full_name}</Title>
            {identity.full_name_encrypted && (
              <Text type="secondary" style={{ fontSize: 11, wordBreak: 'break-all' }}>{identity.full_name_encrypted}</Text>
            )}
          </div>
          <Space>
            <Button icon={<HistoryOutlined />} onClick={() => navigate(`/patients/${uuid}/timeline`)}>
              Linha do Tempo
            </Button>
            <Button icon={<DownloadOutlined />} onClick={() => downloadUrl(`${API_BASE}/patients/${uuid}/export?format=csv`)}>
              Exportar CSV
            </Button>
            <Button icon={<CalendarOutlined />} onClick={() => navigate(`/consultations/new?patient=${uuid}`)}>
              Nova Consulta
            </Button>
            <Button icon={<EditOutlined />} onClick={() => navigate(`/patients/${uuid}/edit`)}>
              Editar
            </Button>
          </Space>
        </div>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="Data Nascimento">{profile.birth_date || '-'}</Descriptions.Item>
          <Descriptions.Item label="Sexo">{sexo}</Descriptions.Item>
          <Descriptions.Item label="Identidade de Gênero">{profile.gender_identity?.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="Escolaridade">{profile.education_level?.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="Etnia">{profile.ethnicity?.description || '-'}</Descriptions.Item>
          <Descriptions.Item label="Estado Civil">{profile.marital_status || '-'}</Descriptions.Item>
          <Descriptions.Item label="Profissão">{profile.occupation || '-'}</Descriptions.Item>
          <Descriptions.Item label="Situação Transgênero">{profile.trans_status ? ({ cis: 'Cisgênero', trans: 'Transgênero', intersex: 'Intersexo', prefer_not_to_say: 'Prefiro não informar' } as Record<string, string>)[profile.trans_status] : '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="Relatorios Medicos" style={{ marginTop: 16 }} size="small"
        extra={<Button size="small" icon={<FileTextOutlined />} onClick={() => navigate(`/patients/${uuid}/reports`)}>Gerenciar</Button>}
      >
        {reports.length === 0 ? (
          <Text type="secondary">Nenhum relatorio fixado. <a onClick={() => navigate(`/patients/${uuid}/reports`)}>Criar relatorio</a></Text>
        ) : (
          <List
            dataSource={reports}
            size="small"
            renderItem={(r) => (
              <List.Item
                actions={[
                  <Button size="small" type="link" onClick={() => navigate(`/patients/${uuid}/reports`)}>Abrir</Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={<PushpinFilled style={{ color: '#1890ff' }} />}
                  title={r.title}
                  description={<Paragraph ellipsis style={{ margin: 0 }}>{r.content}</Paragraph>}
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      {availableScales.length > 0 && (
        <Card title={<Space><LineChartOutlined />Escalas — Tendência</Space>} style={{ marginTop: 16 }} size="small"
          extra={
            <Select size="small" style={{ width: 300 }} value={selectedScale} onChange={setSelectedScale}>
              {availableScales.map((s) => (
                <Select.Option key={s} value={s}>{SCALE_OPTIONS[s]?.label || s}</Select.Option>
              ))}
            </Select>
          }
        >
          {scaleLoading ? (
            <Spin style={{ display: 'block', margin: '20px auto' }} />
          ) : scaleHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={scaleHistory.map((s) => ({ date: s.date.slice(5, 10), score: s.score }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="score" stroke="#1677ff" strokeWidth={2} dot={{ r: 4 }} name={SCALE_OPTIONS[selectedScale!]?.label || selectedScale} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 20 }}>
              Nenhum dado disponível para esta escala
            </Typography.Text>
          )}
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={8}><Typography.Text type="secondary">Registros: </Typography.Text><Typography.Text strong>{scaleHistory.length}</Typography.Text></Col>
            <Col span={8}>
              <Typography.Text type="secondary">Média: </Typography.Text>
              <Typography.Text strong>
                {scaleHistory.length > 0 ? (scaleHistory.reduce((a, b) => a + b.score, 0) / scaleHistory.length).toFixed(1) : '-'}
              </Typography.Text>
            </Col>
            <Col span={8}>
              <Typography.Text type="secondary">Último: </Typography.Text>
              <Typography.Text strong>
                {scaleHistory.length > 0 ? scaleHistory[scaleHistory.length - 1].score.toFixed(1) : '-'}
              </Typography.Text>
            </Col>
          </Row>
        </Card>
      )}

      <Card title="Consultas" style={{ marginTop: 16 }} size="small">
        <Table
          dataSource={consultations}
          rowKey="consultation_uuid"
          size="small"
          pagination={false}
          onRow={(record) => ({
            onClick: () => navigate(`/consultations/${record.consultation_uuid}`),
            style: { cursor: 'pointer' },
          })}
          columns={[
            { title: 'Data', dataIndex: 'consultation_date', width: 160 },
            { title: 'Paciente', dataIndex: 'patient_name', ellipsis: true },
            { title: 'Profissional', dataIndex: 'professional_name', ellipsis: true },
            { title: 'Observacoes', dataIndex: 'consultation_notes', ellipsis: true },
          ]}
          locale={{ emptyText: 'Nenhuma consulta registrada' }}
        />
      </Card>
    </>
  )
}
