import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Spin, Typography, List, Badge } from 'antd'
import {
  UserOutlined,
  CalendarOutlined,
  BellOutlined,
  ExperimentOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { metricsApi } from '../../api/metrics'
import { patientsApi } from '../../api/patients'
import { alertsApi } from '../../api/alerts'
import type { MetricsOverview, PatientListItem, Alert } from '../../types'
import { SEVERITY_COLORS } from '../../utils/constants'

const { Title } = Typography

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null)
  const [recentPatients, setRecentPatients] = useState<PatientListItem[]>([])
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      metricsApi.overview(),
      patientsApi.list(1, 5),
      alertsApi.list(false),
    ])
      .then(([m, p, a]) => {
        setMetrics(m)
        setRecentPatients(p.patients)
        setRecentAlerts(a.slice(0, 5))
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Title level={3}>Dashboard</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/patients')}>
            <Statistic title="Pacientes" value={metrics?.total_patients || 0} prefix={<UserOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/consultations')}>
            <Statistic title="Consultas" value={metrics?.total_consultations || 0} prefix={<CalendarOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Inferências"
              value={metrics?.total_inferences || 0}
              prefix={<ExperimentOutlined />}
              suffix={
                <Tag color="blue" style={{ marginLeft: 8 }}>
                  {metrics?.avg_confidence ? `${(metrics.avg_confidence * 100).toFixed(0)}% confiança` : ''}
                </Tag>
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/alerts')}>
            <Statistic
              title="Alertas Ativos"
              value={metrics?.active_alerts || 0}
              prefix={<BellOutlined />}
              valueStyle={{ color: (metrics?.active_alerts || 0) > 0 ? '#f5222d' : '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Pacientes Recentes" size="small">
            <Table
              dataSource={recentPatients}
              rowKey="patient_uuid"
              size="small"
              pagination={false}
              onRow={(record) => ({
                onClick: () => navigate(`/patients/${record.patient_uuid}`),
                style: { cursor: 'pointer' },
              })}
              columns={[
                { title: 'Nome', dataIndex: 'full_name', ellipsis: true },
                { title: 'Idade', dataIndex: 'age', width: 80 },
                {
                  title: 'Sexo',
                  dataIndex: 'sex_type',
                  width: 80,
                  render: (v: string) => <Tag>{v}</Tag>,
                },
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Alertas Recentes" size="small">
            <List
              dataSource={recentAlerts}
              size="small"
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Badge color={SEVERITY_COLORS[item.severity] || '#faad14'} />}
                    title={
                      <span>
                        <Tag color={SEVERITY_COLORS[item.severity]}>{item.severity}</Tag>
                        {item.alert_type}
                      </span>
                    }
                    description={item.message}
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Nenhum alerta ativo' }}
            />
          </Card>
        </Col>
      </Row>
    </>
  )
}
