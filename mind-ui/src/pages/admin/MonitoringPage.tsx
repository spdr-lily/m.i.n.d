import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Typography, Breadcrumb, Spin, Alert } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined, ApiOutlined } from '@ant-design/icons'
import { adminApi } from '../../api/endpoints'
import type { MonitoringStats, HealthStatus, RequestLog } from '../../types'

const { Title } = Typography

export default function MonitoringPage() {
  const [stats, setStats] = useState<MonitoringStats | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [requests, setRequests] = useState<RequestLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      adminApi.stats(),
      adminApi.health(),
      adminApi.requests(),
    ])
      .then(([s, h, r]) => {
        setStats(s)
        setHealth(h)
        setRequests(r.requests)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Breadcrumb items={[{ title: 'Admin' }, { title: 'Monitoramento' }]} style={{ marginBottom: 16 }} />
      {health && (
        <Alert
          type={health.status === 'healthy' ? 'success' : 'warning'}
          message={
            <span>
              Status: <strong>{health.status.toUpperCase()}</strong> | Database: {health.database} | Uptime: {Math.floor(health.uptime_seconds / 60)} min
            </span>
          }
          icon={health.status === 'healthy' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Total Requisições" value={stats?.total_requests || 0} prefix={<ApiOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Latência Média" value={stats?.avg_latency_ms?.toFixed(1) || 0} suffix="ms" prefix={<ClockCircleOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="P95 Latência" value={stats?.p95_latency_ms?.toFixed(1) || 0} suffix="ms" prefix={<ClockCircleOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Taxa de Erro"
              value={(stats?.error_rate || 0) * 100}
              suffix="%"
              valueStyle={{ color: (stats?.error_rate || 0) > 0.05 ? '#f5222d' : '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Requisições Recentes" style={{ marginTop: 16 }} size="small">
        <Table
          dataSource={requests.slice(0, 50)}
          rowKey={(r, i) => `${r.timestamp}-${i}`}
          size="small"
          pagination={{ pageSize: 20 }}
          columns={[
            { title: 'Método', dataIndex: 'method', width: 80, render: (v: string) => <Tag>{v}</Tag> },
            { title: 'Path', dataIndex: 'path', ellipsis: true },
            {
              title: 'Status',
              dataIndex: 'status_code',
              width: 80,
              render: (v: number) => <Tag color={v < 400 ? 'green' : 'red'}>{v}</Tag>,
            },
            { title: 'Latência', dataIndex: 'latency_ms', width: 100, render: (v: number) => `${v.toFixed(0)}ms` },
            { title: 'Timestamp', dataIndex: 'timestamp', width: 160 },
          ]}
        />
      </Card>
    </>
  )
}
