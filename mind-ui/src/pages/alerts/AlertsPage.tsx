import { useEffect, useState } from 'react'
import { Card, Table, Tag, Button, Typography, Breadcrumb, Spin, Space, Badge } from 'antd'
import { CheckCircleOutlined, BellOutlined } from '@ant-design/icons'
import { alertsApi } from '../../api/endpoints'
import type { Alert } from '../../types'
import { SEVERITY_COLORS, SEVERITY_LABELS, ALERT_TYPE_LABELS } from '../../utils/constants'

const { Title } = Typography

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [showResolved, setShowResolved] = useState(false)

  const fetchAlerts = () => {
    setLoading(true)
    alertsApi.list(showResolved ? true : false).then(setAlerts).finally(() => setLoading(false))
  }

  useEffect(() => { fetchAlerts() }, [showResolved])

  const handleResolve = async (id: number) => {
    await alertsApi.resolve(id)
    fetchAlerts()
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Alertas' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Alertas Clínicos</Title>
          <Button onClick={() => setShowResolved(!showResolved)} icon={<BellOutlined />}>
            {showResolved ? 'Ocultar resolvidos' : 'Mostrar resolvidos'}
          </Button>
        </div>
        <Table
          dataSource={alerts}
          rowKey="alert_id"
          loading={loading}
          pagination={{ pageSize: 20 }}
          columns={[
            {
              title: 'Severidade',
              dataIndex: 'severity',
              width: 110,
              render: (v: string) => <Tag color={SEVERITY_COLORS[v]}>{SEVERITY_LABELS[v] || v}</Tag>,
            },
            {
              title: 'Tipo',
              dataIndex: 'alert_type',
              width: 160,
              render: (v: string) => <span>{ALERT_TYPE_LABELS[v] || v}</span>,
            },
            { title: 'Mensagem', dataIndex: 'message', ellipsis: true },
            { title: 'Data', dataIndex: 'created_at', width: 160 },
            {
              title: 'Ações',
              width: 100,
              render: (_: unknown, record: Alert) =>
                !record.resolved ? (
                  <Button size="small" icon={<CheckCircleOutlined />} onClick={() => handleResolve(record.alert_id)}>
                    Resolver
                  </Button>
                ) : (
                  <Tag color="green">Resolvido</Tag>
                ),
            },
          ]}
        />
      </Card>
    </>
  )
}
