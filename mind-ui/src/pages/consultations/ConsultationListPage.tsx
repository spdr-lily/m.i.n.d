import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Table, Button, Card, Typography, Breadcrumb, message, Tag } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { consultationsApi } from '../../api/consultations'
import type { ConsultationResponse } from '../../types'

const { Title } = Typography

export default function ConsultationListPage() {
  const [consultations, setConsultations] = useState<ConsultationResponse[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    consultationsApi.list(undefined, page).then((data) => {
      setConsultations(data.consultations)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }, [page])

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Consultas' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Consultas</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/consultations/new')}>
            Nova Consulta
          </Button>
        </div>
        <Table
          dataSource={consultations}
          rowKey="consultation_uuid"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
          onRow={(record) => ({ onClick: () => navigate(`/consultations/${record.consultation_uuid}`), style: { cursor: 'pointer' } })}
          columns={[
            { title: 'Data', dataIndex: 'consultation_date', width: 160 },
            { title: 'Paciente', dataIndex: 'patient_uuid', ellipsis: true, render: (v: string) => <Tag>{v.slice(0, 8)}...</Tag> },
            { title: 'Profissional', dataIndex: 'professional_name', ellipsis: true },
            { title: 'Observações', dataIndex: 'consultation_notes', ellipsis: true },
          ]}
        />
      </Card>
    </>
  )
}
