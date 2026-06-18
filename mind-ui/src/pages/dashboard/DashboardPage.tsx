import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Spin, Typography, List, Badge, Tabs, Space, Select, Progress } from 'antd'
import {
  UserOutlined, CalendarOutlined, BellOutlined, ExperimentOutlined,
  ArrowUpOutlined, ArrowDownOutlined, TeamOutlined, MedicineBoxOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts'
import { metricsApi } from '../../api/metrics'
import { patientsApi } from '../../api/patients'
import { alertsApi } from '../../api/alerts'
import type {
  MetricsOverview, PatientListItem, Alert,
  DemographicsResponse, ConsultationMetricsResponse, DisorderPrevalenceItem,
  PrevalenceTrendItem, ScaleTrendItem, MLDashboardResponse,
} from '../../types'
import { SEVERITY_COLORS, SEVERITY_LABELS, ALERT_TYPE_LABELS, SCALE_OPTIONS, NEURO_SCALES, CLINICAL_SCALES } from '../../utils/constants'

const { Title } = Typography

const SEX_LABELS: Record<string, string> = { '7': 'Masculino', '8': 'Feminino', '1': 'Masculino', '2': 'Feminino', '0': 'Não informado' }
const PIE_COLORS = ['#1677ff', '#ff69b4', '#d9d9d9', '#52c41a', '#ffe600', '#722ed1']
const GENDER_PIE_COLORS = ['#52c41a', '#722ed1', '#1677ff', '#ff69b4', '#ffe600', '#13c2c2']

const SEX_COLOR_MAP: Record<string, string> = {
  'Masculino': '#1677ff',
  'Feminino': '#ff69b4',
  'Não informado': '#d9d9d9',
}

const GENDER_COLOR_MAP: Record<string, string> = {
  'Masculino': '#1677ff',
  'Feminino': '#ff69b4',
  'Não-Binário': '#ffe600',
  'Prefiro não informar': '#d9d9d9',
  'Não informado': '#d9d9d9',
}
const BAR_COLORS = ['#1677ff', '#52c41a', '#ffe600', '#f5222d', '#722ed1']
const EDU_COLORS = ['#ebd9b4', '#b8d4b0', '#8db5d8', '#5b8db5', '#3d5a80']
const ETHNICITY_COLORS = ['#8B4513', '#DEB887', '#2F2F2F', '#F0C75E', '#CD853F']

const EDU_ORDER = ['Ensino Fundamental', 'Ensino Médio', 'Ensino Superior Incompleto', 'Ensino Superior', 'Pós-graduação']

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null)
  const [recentPatients, setRecentPatients] = useState<PatientListItem[]>([])
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [demographics, setDemographics] = useState<DemographicsResponse | null>(null)
  const [consultationData, setConsultationData] = useState<ConsultationMetricsResponse | null>(null)
  const [disorders, setDisorders] = useState<DisorderPrevalenceItem[]>([])
  const [prevalenceTrends, setPrevalenceTrends] = useState<PrevalenceTrendItem[]>([])
  const [comorbidityPairs, setComorbidityPairs] = useState<any[]>([])
  const [selectedScale, setSelectedScale] = useState<string>('PHQ-9')
  const [scaleTrend, setScaleTrend] = useState<ScaleTrendItem | null>(null)
  const [scaleTrendLoading, setScaleTrendLoading] = useState(false)
  const [mlData, setMlData] = useState<MLDashboardResponse | null>(null)
  const [mlLoading, setMlLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!selectedScale) return
    setScaleTrendLoading(true)
    metricsApi.scaleTrends(selectedScale, 90).then(setScaleTrend).catch(() => setScaleTrend(null))
      .finally(() => setScaleTrendLoading(false))
  }, [selectedScale])

  useEffect(() => {
    const load = async () => {
      try {
        const [m, p, a, demo, cons, dis, pt, com] = await Promise.all([
          metricsApi.overview().catch(() => null),
          patientsApi.list(1, 5).catch(() => ({ patients: [] as PatientListItem[] })),
          alertsApi.list(false).catch(() => [] as Alert[]),
          metricsApi.demographics().catch(() => null),
          metricsApi.consultationMetrics(30).catch(() => null),
          metricsApi.disorderPrevalence(10).catch(() => []),
          metricsApi.prevalenceTrends(12).catch(() => []),
          metricsApi.comorbidity(10).catch(() => null),
        ])
        if (m) setMetrics(m)
        if (p) setRecentPatients(p.patients)
        if (a) setRecentAlerts(a.slice(0, 5))
        if (demo) setDemographics(demo)
        if (cons) setConsultationData(cons)
        if (dis) setDisorders(dis)
        if (pt) setPrevalenceTrends(pt)
        if (com) setComorbidityPairs(com.pairs || [])
      } finally {
        setLoading(false)
      }
    }
    load()
    setMlLoading(true)
    metricsApi.mlDashboard().then(setMlData).catch(() => null).finally(() => setMlLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  const sexPieData = demographics?.sex_distribution
    ? Object.entries(demographics.sex_distribution).map(([k, v]) => ({
        name: SEX_LABELS[k] || `Tipo ${k}`,
        value: v,
      })) : []

  const genderPieData = demographics?.gender_identity_distribution
    ? Object.entries(demographics.gender_identity_distribution).map(([k, v]) => ({
        name: k,
        value: v,
      })) : []

  const ageBarData = demographics?.age_distribution
    ? Object.entries(demographics.age_distribution).map(([k, v]) => ({
        name: `${k} anos`,
        value: v,
      })) : []

  const eduBarData = demographics?.education_level_distribution
    ? Object.entries(demographics.education_level_distribution)
        .sort((a, b) => EDU_ORDER.indexOf(a[0]) - EDU_ORDER.indexOf(b[0]))
        .map(([k, v]) => ({ name: k, value: v })) : []

  const ethnicityBarData = demographics?.ethnicity_distribution
    ? Object.entries(demographics.ethnicity_distribution)
        .sort((a, b) => b[1] - a[1])
        .map(([k, v]) => ({ name: k, value: v })) : []

  const consultChartData = consultationData?.trend?.daily_counts
    ? Object.entries(consultationData.trend.daily_counts).map(([date, count]) => ({
        date: date.slice(5, 10),
        Consultas: count,
        Média: consultationData.trend.moving_avg_7d?.[date] ?? null,
      }))
    : []

  const disorderChartData = disorders.filter((d) => d.inference_count > 0).map((d) => ({
    name: d.disorder_name.length > 20 ? d.disorder_name.slice(0, 18) + '..' : d.disorder_name,
    Inferências: d.inference_count,
  }))

  const prevalenceLineData = (() => {
    if (!prevalenceTrends.length) return []
    const months = new Set<string>()
    prevalenceTrends.forEach((t) => t.monthly_counts.forEach((m) => months.add(m.month)))
    const sortedMonths = Array.from(months).sort()
    return sortedMonths.map((month) => {
      const point: Record<string, any> = { month: month.slice(5) }
      prevalenceTrends.forEach((t) => {
        const found = t.monthly_counts.find((m) => m.month === month)
        point[t.disorder_name] = found ? found.count : 0
      })
      return point
    })
  })()
  const prevalenceColors = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa541c', '#a0d911', '#2f54eb']

  const comorbidityPairsSorted = [...comorbidityPairs].sort((a, b) => b.count - a.count).slice(0, 20)

  const scaleTrendChartData = scaleTrend?.trend?.scores
    ? Object.entries(scaleTrend.trend.scores).map(([date, score]) => ({
        date: date.slice(5, 10),
        'Média Diária': score,
        'Média Móvel (3)': scaleTrend.trend.moving_avg_3[date] ?? null,
      }))
    : []

  const clinicalOptions = Object.keys(SCALE_OPTIONS)
    .filter((k) => CLINICAL_SCALES.has(k))
    .map((key) => ({ value: key, label: SCALE_OPTIONS[key].label }))
  const neuroOptions = Object.keys(SCALE_OPTIONS)
    .filter((k) => NEURO_SCALES.has(k))
    .map((key) => ({ value: key, label: SCALE_OPTIONS[key].label }))

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
                        <Pie data={sexPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }: { name: string; percent?: number }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                          {sexPieData.map((_, i) => (
                            <Cell key={i} fill={SEX_COLOR_MAP[sexPieData[i].name] || PIE_COLORS[i % PIE_COLORS.length]} />
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
                  key: 'identidade',
                  label: 'Identidade de Gênero',
                  children: genderPieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <PieChart>
<Pie data={genderPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }: { name: string; percent?: number }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                          {genderPieData.map((_, i) => (
                            <Cell key={i} fill={GENDER_COLOR_MAP[genderPieData[i].name] || GENDER_PIE_COLORS[i % GENDER_PIE_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                      Sem dados de identidade de gênero
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
                {
                  key: 'escolaridade',
                  label: 'Escolaridade',
                  children: eduBarData.some((d) => d.value > 0) ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={eduBarData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" allowDecimals={false} />
                        <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                          {eduBarData.map((_, i) => (
                            <Cell key={i} fill={EDU_COLORS[i % EDU_COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                      Sem dados de escolaridade
                    </Typography.Text>
                  ),
                },
                {
                  key: 'etnia',
                  label: 'Etnia',
                  children: ethnicityBarData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={ethnicityBarData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" allowDecimals={false} />
                        <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                          {ethnicityBarData.map((_, i) => (
                            <Cell key={i} fill={ETHNICITY_COLORS[i % ETHNICITY_COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                      Sem dados de etnia
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
                  <Bar dataKey="Inferências" radius={[0, 4, 4, 0]}>
                    {disorderChartData.map((_, i) => {
                      let color = '#1677ff'
                      if (i < 1) color = '#ff0000'
                      else if (i < 2) color = '#ff8500'
                      else if (i < 3) color = '#ffbc00'
                      else if (i < 4) color = '#52c41a'
                      return <Cell key={i} fill={color} />
                    })}
                  </Bar>
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
          <Card title="Tendência de Prevalência (12 meses)" size="small">
            {prevalenceLineData.length > 0 && prevalenceTrends.length <= 10 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={prevalenceLineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {prevalenceTrends.map((t, i) => (
                    <Line key={t.disorder_name} type="monotone" dataKey={t.disorder_name} stroke={prevalenceColors[i % prevalenceColors.length]} strokeWidth={2} dot={false} connectNulls />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            ) : prevalenceLineData.length > 0 ? (
              <Table dataSource={prevalenceTrends} rowKey="disorder_name" size="small" pagination={false}
                columns={[
                  { title: 'Transtorno', dataIndex: 'disorder_name', ellipsis: true },
                  { title: 'Total', dataIndex: 'total_count', width: 60 },
                ]}
              />
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Nenhum dado de prevalência disponível
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Comorbidades mais frequentes" size="small">
            {comorbidityPairsSorted.length > 0 ? (
              <Table dataSource={comorbidityPairsSorted} rowKey={(r) => `${r.disorder_a}-${r.disorder_b}`} size="small" pagination={false}
                columns={[
                  { title: 'Transtorno A', dataIndex: 'disorder_a', ellipsis: true },
                  { title: 'Transtorno B', dataIndex: 'disorder_b', ellipsis: true },
                  { title: 'Co-ocorrências', dataIndex: 'count', width: 110, render: (v: number) => <Tag color={v >= 5 ? '#f5222d' : v >= 3 ? '#faad14' : '#1677ff'}>{v}</Tag> },
                ]}
              />
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Nenhum dado de comorbidade disponível
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Modelos ML em Produção" size="small" loading={mlLoading}>
            {mlData?.models?.length ? (
              <List
                dataSource={mlData.models}
                size="small"
                split={false}
                renderItem={(m) => (
                  <List.Item style={{ padding: '6px 0' }}>
                    <Space direction="vertical" style={{ width: '100%' }} size={2}>
                      <Space>
                        <Tag color="green">{m.stage}</Tag>
                        <Typography.Text strong style={{ fontSize: 13 }}>{m.name}</Typography.Text>
                      </Space>
                      <Typography.Text type="secondary" style={{ fontSize: 11 }}>{m.description}</Typography.Text>
                      <Space size={16}>
                        <Typography.Text style={{ fontSize: 12 }}>
                          R²: <Tag color={m.r2 >= 0.4 ? 'blue' : m.r2 >= 0.2 ? 'orange' : 'red'}>{m.r2.toFixed(3)}</Tag>
                        </Typography.Text>
                        <Typography.Text style={{ fontSize: 12 }}>
                          MAE: <Tag>{m.mae.toFixed(2)}</Tag>
                        </Typography.Text>
                      </Space>
                    </Space>
                  </List.Item>
                )}
              />
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Nenhum modelo em produção
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title={<Space>Tendências de Escalas <Select size="small" style={{ width: 360 }} value={selectedScale} onChange={setSelectedScale}>
            <Select.OptGroup label="Clínicas">
              {clinicalOptions.map((o) => <Select.Option key={o.value} value={o.value}>{o.label}</Select.Option>)}
            </Select.OptGroup>
            <Select.OptGroup label="Neuropsicológicas">
              {neuroOptions.map((o) => <Select.Option key={o.value} value={o.value}>{o.label}</Select.Option>)}
            </Select.OptGroup>
          </Select></Space>} size="small">
            {scaleTrendLoading ? (
              <Spin style={{ display: 'block', margin: '40px auto' }} />
            ) : scaleTrendChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={scaleTrendChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="Média Diária" stroke="#1677ff" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="Média Móvel (3)" stroke="#52c41a" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Nenhum dado disponível para a escala selecionada
              </Typography.Text>
            )}
            {scaleTrend && scaleTrend.statistics && (
              <Row gutter={16} style={{ marginTop: 8 }}>
                <Col span={6}><Typography.Text type="secondary">Registros: </Typography.Text><Typography.Text strong>{scaleTrend.total_records}</Typography.Text></Col>
                <Col span={6}><Typography.Text type="secondary">Média: </Typography.Text><Typography.Text strong>{scaleTrend.statistics.mean}</Typography.Text></Col>
                <Col span={6}><Typography.Text type="secondary">Mín: </Typography.Text><Typography.Text strong>{scaleTrend.statistics.min}</Typography.Text></Col>
                <Col span={6}><Typography.Text type="secondary">Máx: </Typography.Text><Typography.Text strong>{scaleTrend.statistics.max}</Typography.Text></Col>
              </Row>
            )}
          </Card>
        </Col>
      </Row>

      {/* ── ML Dashboard Section ────────────────────────────────────────── */}
      <Title level={5} style={{ marginTop: 24, marginBottom: 12 }}>Resultados de Machine Learning</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Personalidade Média (BFP)" size="small" loading={mlLoading}>
            {mlData?.personality?.bfp_averages ? (
              (() => {
                const radarData = Object.entries(mlData.personality.bfp_averages).map(([factor, score]) => ({
                  factor,
                  score,
                  max: 20,
                }))
                return (
                  <>
                    <ResponsiveContainer width="100%" height={240}>
                      <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="factor" tick={{ fontSize: 10 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 20]} tick={false} axisLine={false} />
                        <Radar name="Média" dataKey="score" stroke="#1677ff" fill="#1677ff" fillOpacity={0.3} />
                      </RadarChart>
                    </ResponsiveContainer>
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', fontSize: 12 }}>
                      Baseado em {mlData.personality.total_assessments} avaliações
                    </Typography.Text>
                  </>
                )
              })()
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados de personalidade
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="HEXACO-60 Média" size="small" loading={mlLoading}>
            {mlData?.personality?.hexaco_averages ? (
              (() => {
                const radarData = Object.entries(mlData.personality.hexaco_averages).map(([factor, score]) => ({
                  factor: factor.length > 14 ? factor.slice(0, 13) + '..' : factor,
                  score,
                  max: 50,
                }))
                return (
                  <ResponsiveContainer width="100%" height={240}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="factor" tick={{ fontSize: 9 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 50]} tick={false} axisLine={false} />
                      <Radar name="Média" dataKey="score" stroke="#08979c" fill="#08979c" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                )
              })()
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados HEXACO-60
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Tríade Sombria Média (DT-12)" size="small" loading={mlLoading}>
            {mlData?.personality?.dt12_averages ? (
              (() => {
                const radarDT = Object.entries(mlData.personality.dt12_averages).map(([sub, score]) => ({
                  subscale: sub,
                  score,
                  max: 24,
                }))
                return (
                  <>
                    <ResponsiveContainer width="100%" height={240}>
                      <RadarChart data={radarDT}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="subscale" tick={{ fontSize: 10 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 24]} tick={false} axisLine={false} />
                        <Radar name="Média" dataKey="score" stroke="#722ed1" fill="#722ed1" fillOpacity={0.3} />
                      </RadarChart>
                    </ResponsiveContainer>
                    <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', fontSize: 12 }}>
                      Subescalas da Tríade Sombria
                    </Typography.Text>
                  </>
                )
              })()
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados da Tríade Sombria
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 4 }}>
        <Col xs={24} lg={8}>
          <Card title="BIS-11 Média (Impulsividade)" size="small" loading={mlLoading}>
            {mlData?.personality?.bis11_averages ? (
              (() => {
                const radarData = Object.entries(mlData.personality.bis11_averages).map(([sub, score]) => ({
                  subscale: sub,
                  score,
                  max: 40,
                }))
                return (
                  <ResponsiveContainer width="100%" height={240}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subscale" tick={{ fontSize: 10 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 40]} tick={false} axisLine={false} />
                      <Radar name="Média" dataKey="score" stroke="#fa8c16" fill="#fa8c16" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                )
              })()
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados BIS-11
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="TAS-20 Média (Alexitimia)" size="small" loading={mlLoading}>
            {mlData?.personality?.tas20_averages ? (
              (() => {
                const radarData = Object.entries(mlData.personality.tas20_averages).map(([sub, score]) => ({
                  subscale: sub,
                  score,
                  max: 33,
                }))
                return (
                  <ResponsiveContainer width="100%" height={240}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subscale" tick={{ fontSize: 10 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 33]} tick={false} axisLine={false} />
                      <Radar name="Média" dataKey="score" stroke="#d4380d" fill="#d4380d" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                )
              })()
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados TAS-20
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="RSES Média (Autoestima)" size="small" loading={mlLoading}>
            {mlData?.personality?.rses_averages ? (
              (() => {
                const score = mlData.personality.rses_averages['Autoestima'] || 0
                const pct = Math.round((score / 40) * 100)
                return (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Typography.Title level={2} style={{ color: '#1677ff', margin: 0 }}>{score.toFixed(1)}</Typography.Title>
                    <Typography.Text type="secondary">/ 40 pontos</Typography.Text>
                    <Progress percent={pct} strokeColor="#1677ff" style={{ marginTop: 16 }} />
                    <Typography.Text type="secondary" style={{ display: 'block', marginTop: 8, fontSize: 12 }}>
                      Média de autoestima entre pacientes avaliados
                    </Typography.Text>
                  </div>
                )
              })()
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados RSES
              </Typography.Text>
            )}
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} md={12}>
          <Card title="Eficácia de Medicamentos" size="small" loading={mlLoading}>
            {mlData?.efficacy ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic title="Associações" value={mlData.efficacy.total_associations} suffix="med-transtorno" />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Outcomes Registrados" value={mlData.efficacy.total_outcomes} />
                  </Col>
                </Row>
                <Typography.Text strong style={{ marginTop: 8, display: 'block' }}>Por linha de tratamento</Typography.Text>
                {mlData.efficacy.by_line_of_treatment.map((line) => (
                  <div key={line.line} style={{ marginTop: 6 }}>
                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Tag>{({1:'1ª Linha',2:'2ª Linha',3:'3ª Linha',4:'4ª Linha'})[line.line] || `Linha ${line.line}`}</Tag>
                      <Typography.Text type="secondary">{line.count} associações</Typography.Text>
                    </Space>
                    <Progress percent={Math.round(line.avg_success_rate * 100)}
                      status={line.avg_success_rate >= 0.6 ? 'success' : line.avg_success_rate >= 0.3 ? 'active' : 'exception'}
                      size="small" format={() => `${(line.avg_success_rate * 100).toFixed(0)}%`} />
                  </div>
                ))}
                {mlData.efficacy.outcome_distribution?.improved && (
                  <>
                    <Typography.Text strong style={{ marginTop: 8, display: 'block' }}>Distribuição de desfechos</Typography.Text>
                    <Row gutter={8} style={{ marginTop: 4 }}>
                      {Object.entries(mlData.efficacy.outcome_distribution).map(([k, v]) => (
                        <Col span={8} key={k}>
                          <Tag color={k === 'improved' || k === 'remission' ? 'green' : k === 'no_change' ? 'orange' : k === 'worsened' ? 'red' : 'default'}
                            style={{ width: '100%', textAlign: 'center', marginBottom: 4 }}>
                            {k.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}: {v}
                          </Tag>
                        </Col>
                      ))}
                    </Row>
                  </>
                )}
              </Space>
            ) : (
              <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center', padding: 40 }}>
                Sem dados de eficácia
              </Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} md={12}>
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
                        <Tag color={SEVERITY_COLORS[item.severity]}>{SEVERITY_LABELS[item.severity] || item.severity}</Tag>
                        {ALERT_TYPE_LABELS[item.alert_type] || item.alert_type}
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
