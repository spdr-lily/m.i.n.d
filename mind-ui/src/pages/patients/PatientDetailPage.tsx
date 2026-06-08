import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Tag, Button, Space, Typography, Breadcrumb, Spin, Table, List } from 'antd'
import { CalendarOutlined, EditOutlined, HistoryOutlined, DownloadOutlined, PushpinFilled, FileTextOutlined } from '@ant-design/icons'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import { reportsApi } from '../../api/reports'
import type { PatientResponse, ConsultationListItem, MedicalReport } from '../../types'

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
  const navigate = useNavigate()

  useEffect(() => {
    if (!uuid) return
    Promise.all([
      patientsApi.get(uuid),
      consultationsApi.list(uuid),
      reportsApi.list(uuid),
    ])
      .then(([p, c, r]) => {
        setPatient(p)
        setConsultations(c.consultations || [])
        setReports(r.filter(rpt => rpt.is_pinned))
      })
      .finally(() => setLoading(false))
  }, [uuid])

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
