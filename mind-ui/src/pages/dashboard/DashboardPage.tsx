import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Spin, Typography, List, Badge, Tabs } from 'antd'
import {
  UserOutlined, CalendarOutlined, BellOutlined, ExperimentOutlined,
  ArrowUpOutlined, ArrowDownOutlined, TeamOutlined, MedicineBoxOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, PieChart, Pie, Cell,
} from 'recharts'
import { metricsApi } from '../../api/metrics'
import { patientsApi } from '../../api/patients'
import { alertsApi } from '../../api/alerts'
import type {
  MetricsOverview, PatientListItem, Alert,
  DemographicsResponse, ConsultationMetricsResponse, DisorderPrevalenceItem,
} from '../../types'
import { SEVERITY_COLORS } from '../../utils/constants'

const { Title } = Typography

const SEX_LABELS: Record<string, string> = { '1': 'Masculino', '2': 'Feminino', '0': 'Não informado' }
const PIE_COLORS = ['#1677ff', '#ff69b4', '#d9d9d9']
const BAR_COLORS = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null)
  const [recentPatients, setRecentPatients] = useState<PatientListItem[]>([])
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [demographics, setDemographics] = useState<DemographicsResponse | null>(null)
  const [consultationData, setConsultationData] = useState<ConsultationMetricsResponse | null>(null)
  const [disorders, setDisorders] = useState<DisorderPrevalenceItem[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      try {
        const [m, p, a, demo, cons, dis] = await Promise.all([
          metricsApi.overview().catch(() => null),
          patientsApi.list(1, 5).catch(() => ({ patients: [] as PatientListItem[] })),
          alertsApi.list(false).catch(() => [] as Alert[]),
          metricsApi.demographics().catch(() => null),
          metricsApi.consultationMetrics(30).catch(() => null),
          metricsApi.disorderPrevalence(10).catch(() => []),
        ])
        if (m) setMetrics(m)
        if (p) setRecentPatients(p.patients)
        if (a) setRecentAlerts(a.slice(0, 5))
        if (demo) setDemographics(demo)
        if (cons) setConsultationData(cons)
        if (dis) setDisorders(dis)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  const sexPieData = demographics ? Object.entries(demographics.sex_distribution).map(([k, v]) => ({
    name: SEX_LABELS[k] || `Tipo ${k}`,
    value: v,
  })) : []

  const ageBarData = demographics ? Object.entries(demographics.age_distribution).map(([k, v]) => ({
    name: `${k} anos`,
    value: v,
  })) : []

  const consultChartData = consultationData?.trend?.daily_counts
    ? Object.entries(consultationData.trend.daily_counts).map(([date, count]) => ({
        date: date.slice(5, 10),
        Consultas: count,
        Média: consultationData.trend.moving_avg_7d[date] || null,
      }))
    : []

  const disorderChartData = disorders.filter((d) => d.inference_count > 0).map((d) => ({
    name: d.disorder_name.length > 20 ? d.disorder_name.slice(0, 18) + '..' : d.disorder_name,
    Inferências: d.inference_count,
  }))

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
              suffix={metrics?.avg_confidence ? (
                <Tag color="blue" style={{ marginLeft: 8 }}>
                  {(metrics.avg_confidence * 100).toFixed(0)}% confiança
                </Tag>
              ) : null}
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
          <Card title="Consultas (últimos 30 dias)" size="small">
            {consultChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={consultChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="Consultas" stroke="#1677ff" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="Média" stroke="#52c41a" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Nenhuma consulta nos últimos 30 dias
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Demografia" size="small">
            <Tabs
              size="small"
              items={[
                {
                  key: 'sexo',
                  label: 'Sexo',
                  children: sexPieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <PieChart>
                        <Pie data={sexPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                          {sexPieData.map((_, i) => (
                            <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                      Sem dados demográficos
                    </Typography.Text>
                  ),
                },
                {
                  key: 'idade',
                  label: 'Idade',
                  children: ageBarData.some((d) => d.value > 0) ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={ageBarData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Bar dataKey="value" fill="#1677ff" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                      Sem dados de idade
                    </Typography.Text>
                  ),
                },
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Transtornos mais prevalentes" size="small">
            {disorderChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={disorderChartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="Inferências" fill="#722ed1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Nenhuma inferência diagnóstica registrada
              </Typography.Text>
            )}
          </Card>
        </Col>
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
                { title: 'Idade', dataIndex: 'age', width: 60 },
                { title: 'Sexo', dataIndex: 'sex_type', width: 80, render: (v: string) => <Tag>{v}</Tag> },
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
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
        <Col xs={24} lg={12}>
          <Card title="Distribuição por Sexo" size="small">
            {sexPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={sexPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {sexPieData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados demográficos
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>
    </>
  )
}
