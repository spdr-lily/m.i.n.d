import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Button, Input, Card, Space, Tag, Typography, Breadcrumb } from 'antd'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { patientsApi } from '../../api/patients'
import type { PatientListItem } from '../../types'

const { Title } = Typography

export default function PatientListPage() {
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    patientsApi.list(page).then((data) => {
      setPatients(data.patients)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }, [page])

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Pacientes' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Pacientes</Title>
          <Space>
            <Input prefix={<SearchOutlined />} placeholder="Buscar paciente..." value={search} onChange={(e) => setSearch(e.target.value)} allowClear />
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/patients/new')}>
              Novo Paciente
            </Button>
          </Space>
        </div>
        <Table
          dataSource={search ? patients.filter((p) => p.full_name.toLowerCase().includes(search.toLowerCase())) : patients}
          rowKey="patient_uuid"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
          onRow={(record) => ({ onClick: () => navigate(`/patients/${record.patient_uuid}`), style: { cursor: 'pointer' } })}
          columns={[
            { title: 'Nome', dataIndex: 'full_name', ellipsis: true },
            { title: 'Idade', dataIndex: 'age', width: 80 },
            { title: 'Sexo', dataIndex: 'sex_type', width: 100, render: (v: string) => <Tag>{v}</Tag> },
            { title: 'Data Nasc.', dataIndex: 'birth_date', width: 120 },
          ]}
        />
      </Card>
    </>
  )
}
