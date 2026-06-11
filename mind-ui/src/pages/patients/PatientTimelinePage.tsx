import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Typography, Breadcrumb, Spin, Tag, Collapse, Descriptions, Empty } from 'antd'
import {
  CalendarOutlined, UserOutlined, FileTextOutlined,
  MedicineBoxOutlined, ExperimentOutlined, WarningOutlined,
} from '@ant-design/icons'
import { timelineApi } from '../../api/timeline'
import type { TimelineResponse, TimelineEvent } from '../../types'

const { Title, Text } = Typography

const EVENT_COLORS: Record<string, string> = {
  consultation: 'blue',
  episode: 'orange',
}

const EVENT_LABELS: Record<string, string> = {
  consultation: 'Consulta',
  episode: 'Episódio Clínico',
}

export default function PatientTimelinePage() {
  const { uuid } = useParams<{ uuid: string }>()
  const [data, setData] = useState<TimelineResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!uuid) return
    timelineApi.get(uuid)
      .then(setData)
      .finally(() => setLoading(false))
  }, [uuid])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
  if (!data) return <Text type="danger">Paciente não encontrado</Text>

  return (
    <>
      <Breadcrumb items={[
        { title: 'Dashboard' },
        { title: 'Pacientes', href: '/patients' },
        { title: data.patient_name, href: `/patients/${uuid}` },
        { title: 'Linha do Tempo' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>
            <CalendarOutlined /> Linha do Tempo Clínica — {data.patient_name}
          </Title>
          <Tag color="blue">{data.events.length} evento{(data.events.length !== 1 ? 's' : '')}</Tag>
        </div>
        {data.events.length === 0 ? (
          <Empty description="Nenhum evento clínico registrado" />
        ) : (
          <TimelineList events={data.events} navigate={navigate} />
        )}
      </Card>
    </>
  )
}

function TimelineList({ events, navigate }: { events: TimelineEvent[]; navigate: ReturnType<typeof useNavigate> }) {
  return (
    <div style={{ position: 'relative' }}>
      {events.map((ev, idx) => {
        const color = EVENT_COLORS[ev.event_type] || 'gray'
        const label = EVENT_LABELS[ev.event_type] || ev.event_type

        if (ev.event_type === 'consultation' && ev.consultation) {
          const c = ev.consultation
          return (
            <div key={c.consultation_uuid} style={{ display: 'flex', marginBottom: 24, gap: 16 }}>
              <div style={{
                width: 40, height: 40, borderRadius: '50%',
                background: '#1677ff', color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, fontSize: 18,
              }}>
                <UserOutlined />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div>
                    <Text strong style={{ fontSize: 16 }}>{label}</Text>
                    <Tag color={color} style={{ marginLeft: 8 }}>{new Date(c.consultation_date).toLocaleDateString('pt-BR')}</Tag>
                  </div>
                  <a onClick={() => navigate(`/consultations/${c.consultation_uuid}`)} style={{ cursor: 'pointer' }}>
                    Ver consulta →
                  </a>
                </div>

                <Card size="small" style={{ background: '#fafafa' }}>
                  {c.professional_name && (
                    <Text type="secondary"><UserOutlined /> {c.professional_name}</Text>
                  )}
                  {c.consultation_notes && (
                    <div style={{ marginTop: 4 }}><Text italic>"{c.consultation_notes}"</Text></div>
                  )}
                  <Collapse ghost size="small" items={[
                    ...(c.symptoms.length > 0 ? [{
                      key: 'symptoms',
                      label: <span><WarningOutlined /> Sintomas ({c.symptoms.length})</span>,
                      children: <div>{c.symptoms.map((s, i) => (
                        <Tag key={i} style={{ marginBottom: 4 }}>{s.symptom_name}{s.intensity ? ` (${s.intensity}%)` : ''}{s.frequency ? ` - ${s.frequency}` : ''}</Tag>
                      ))}</div>,
                    }] : []),
                    ...(c.scale_scores.length > 0 ? [{
                      key: 'scales',
                      label: <span><ExperimentOutlined /> Escalas ({c.scale_scores.length})</span>,
                      children: <div>{c.scale_scores.map((s, i) => (
                        <div key={i} style={{ marginBottom: 4 }}>
                          <Text>{s.scale_name}: </Text>
                          <Tag color="purple">{s.total_score} pts</Tag>
                        </div>
                      ))}</div>,
                    }] : []),
                    ...(c.inferences.length > 0 ? [{
                      key: 'inferences',
                      label: <span><ExperimentOutlined /> Inferências Diagnósticas ({c.inferences.length})</span>,
                      children: <div>{c.inferences.map((inf, i) => (
                        <div key={i} style={{ marginBottom: 4 }}>
                          <Text>{inf.disorder_name}</Text>
                          <Tag color="volcano">{(inf.inference_probability * 100).toFixed(1)}%</Tag>
                        </div>
                      ))}</div>,
                    }] : []),
                    ...(c.prescriptions.length > 0 ? [{
                      key: 'prescriptions',
                      label: <span><MedicineBoxOutlined /> Prescrições ({c.prescriptions.length})</span>,
                      children: <div>{c.prescriptions.map((p, i) => (
                        <div key={i} style={{ marginBottom: 4 }}>
                          <Text>{p.medication_name}</Text>
                          <Descriptions size="small" column={2} style={{ marginLeft: 16 }}>
                            <Descriptions.Item label="Dosagem">{p.dosage}</Descriptions.Item>
                            <Descriptions.Item label="Frequência">{p.frequency}</Descriptions.Item>
                            {p.route && <Descriptions.Item label="Via">{p.route}</Descriptions.Item>}
                            {p.duration_days && <Descriptions.Item label="Duração">{p.duration_days} dias</Descriptions.Item>}
                          </Descriptions>
                        </div>
                      ))}</div>,
                    }] : []),
                    ...(c.clinical_note ? [{
                      key: 'note',
                      label: <span><FileTextOutlined /> Nota Clínica</span>,
                      children: <Descriptions size="small" column={1}>
                        {c.clinical_note.chief_complaint && <Descriptions.Item label="Queixa Principal">{c.clinical_note.chief_complaint}</Descriptions.Item>}
                        {c.clinical_note.clinical_assessment && <Descriptions.Item label="Avaliação">{c.clinical_note.clinical_assessment}</Descriptions.Item>}
                        {c.clinical_note.treatment_plan && <Descriptions.Item label="Plano">{c.clinical_note.treatment_plan}</Descriptions.Item>}
                      </Descriptions>,
                    }] : []),
                  ]} />
                </Card>
              </div>
            </div>
          )
        }

        if (ev.event_type === 'episode' && ev.episode) {
          const e = ev.episode
          return (
            <div key={e.episode_uuid} style={{ display: 'flex', marginBottom: 24, gap: 16 }}>
              <div style={{
                width: 40, height: 40, borderRadius: '50%',
                background: '#fa8c16', color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, fontSize: 18,
              }}>
                <WarningOutlined />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <Text strong style={{ fontSize: 16 }}>{label}</Text>
                <Tag color={color} style={{ marginLeft: 8 }}>
                  {e.episode_start ? new Date(e.episode_start).toLocaleDateString('pt-BR') : '?'}
                  {e.episode_end ? ` → ${new Date(e.episode_end).toLocaleDateString('pt-BR')}` : ''}
                </Tag>
                <Card size="small" style={{ background: '#fafafa', marginTop: 8 }}>
                  {e.episode_type && <Tag color="orange">{e.episode_type}</Tag>}
                  {e.clinical_description && <Text style={{ display: 'block' }}>{e.clinical_description}</Text>}
                </Card>
              </div>
            </div>
          )
        }

        return null
      })}
    </div>
  )
}
