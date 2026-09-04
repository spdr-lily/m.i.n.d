import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Table, Button, Card, Typography, Breadcrumb, theme, Space, DatePicker, Tag } from 'antd'
import dayjs, { Dayjs } from 'dayjs'
import { PlusOutlined } from '@ant-design/icons'
import { consultationsApi } from '../../api/endpoints'
import type { ConsultationListItem } from '../../types'

const { Title, Text } = Typography
const { RangePicker } = DatePicker

type RangeValue = [Dayjs | null, Dayjs | null] | null

export default function ConsultationListPage() {
  const [consultations, setConsultations] = useState<ConsultationListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [range, setRange] = useState<RangeValue>(null)
  const navigate = useNavigate()
  const { token } = theme.useToken()

  useEffect(() => {
    setLoading(true)
    const params: { start_date?: string; end_date?: string } = {}
    if (range && range[0] && range[1]) {
      params.start_date = range[0].format('YYYY-MM-DD')
      params.end_date = range[1].format('YYYY-MM-DD')
    }
    consultationsApi.list(params, page).then((data) => {
      setConsultations(data.consultations)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }, [page, range])

  const isPeriodic = (notes?: string) => notes?.toLowerCase().includes('periódica')

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Consultas' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Consultas</Title>
          <Space wrap>
            <RangePicker
              value={range}
              onChange={(v) => { setPage(1); setRange(v as RangeValue) }}
              format="DD/MM/YYYY"
              allowClear
              placeholder={['De', 'Até']}
            />
            {range && range[0] && range[1] ? (
              <Tag color="blue" style={{ margin: 0 }}>
                {range[0].format('DD/MM/YYYY')} a {range[1].format('DD/MM/YYYY')}
              </Tag>
            ) : null}
            {range && range[0] && range[1] ? (
              <Button size="small" onClick={() => { setPage(1); setRange(null) }}>
                Limpar
              </Button>
            ) : null}
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/consultations/new')}>
              Nova Consulta
            </Button>
          </Space>
        </div>
        <Table
          dataSource={consultations}
          rowKey="consultation_uuid"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
          onRow={(record) => ({ onClick: () => navigate(`/consultations/${record.consultation_uuid}`), style: { cursor: 'pointer' } })}
          columns={[
            {
              title: 'Data',
              dataIndex: 'consultation_date',
              width: 160,
              render: (v: string) => dayjs(v).format('DD/MM/YYYY HH:mm'),
            },
            {
              title: 'Paciente',
              dataIndex: 'patient_name',
              ellipsis: true,
              render: (name: string, record: ConsultationListItem) => (
                <div style={{ lineHeight: 1.4 }}>
                  <div>{name}</div>
                  <Text type="secondary" style={{ fontSize: 11, fontFamily: 'monospace' }}>{record.patient_uuid}</Text>
                </div>
              ),
            },
            { title: 'Profissional', dataIndex: 'professional_name', ellipsis: true },
            {
              title: 'Observações',
              dataIndex: 'consultation_notes',
              ellipsis: true,
              render: (notes: string) => (
                <Space>
                  {isPeriodic(notes) ? <Tag color="green">periódica</Tag> : null}
                  <span>{notes}</span>
                </Space>
              ),
            },
          ]}
        />
      </Card>

      <Button
        type="primary"
        shape="circle"
        size="large"
        icon={<PlusOutlined />}
        onClick={() => navigate('/consultations/new')}
        style={{
          position: 'fixed',
          bottom: 32,
          right: 32,
          width: 56,
          height: 56,
          boxShadow: token.boxShadow,
          zIndex: 1000,
        }}
      />
    </>
  )
}