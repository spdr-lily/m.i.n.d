import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Tag, Button, Space, Typography, Breadcrumb, Spin, Table } from 'antd'
import { EditOutlined, CalendarOutlined } from '@ant-design/icons'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import type { PatientResponse, ConsultationListItem } from '../../types'

const { Title } = Typography

export default function PatientDetailPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const [patient, setPatient] = useState<PatientResponse | null>(null)
  const [consultations, setConsultations] = useState<ConsultationListItem[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!uuid) return
    Promise.all([
      patientsApi.get(uuid),
      consultationsApi.list(uuid),
    ])
      .then(([p, c]) => {
        setPatient(p)
        setConsultations(c.consultations || [])
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
          <Title level={4}>{identity.full_name}</Title>
          <Space>
            <Button icon={<CalendarOutlined />} onClick={() => navigate(`/consultations/new?patient=${uuid}`)}>
              Nova Consulta
            </Button>
          </Space>
        </div>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="Data Nascimento">{profile.birth_date || '-'}</Descriptions.Item>
          <Descriptions.Item label="Sexo">{sexo}</Descriptions.Item>
          <Descriptions.Item label="Estado Civil">{profile.marital_status || '-'}</Descriptions.Item>
          <Descriptions.Item label="Profissao">{profile.occupation || '-'}</Descriptions.Item>
        </Descriptions>
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
            { title: 'Profissional', dataIndex: 'professional_name', ellipsis: true },
            { title: 'Observacoes', dataIndex: 'consultation_notes', ellipsis: true },
          ]}
          locale={{ emptyText: 'Nenhuma consulta registrada' }}
        />
      </Card>
    </>
  )
}
