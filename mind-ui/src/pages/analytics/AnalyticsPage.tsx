import { useEffect, useState } from 'react'
import {
  Card, Col, Row, Spin, Statistic, Table, Select, Typography, Tag, Segmented,
} from 'antd'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend,
} from 'recharts'
import { analyticsApi } from '../../api/analytics'
import type {
  PrevalenceTrendResponse, ComorbidityResponse, ScoreDistributionResponse,
  ScaleSeverityResponse, ProfessionalWorkloadResponse, DemographicSummaryResponse,
  MonthlyConsultationResponse,
} from '../../types'

const { Title } = Typography

type ViewMode = 'prevalence' | 'comorbidity' | 'scores' | 'workload' | 'monthly' | 'severity' | 'demographics'

export default function AnalyticsPage() {
  const [view, setView] = useState<ViewMode>('prevalence')
  const [comorbidityView, setComorbidityView] = useState<'bar' | 'heatmap'>('bar')
  const [loading, setLoading] = useState(false)
  const [prevalence, setPrevalence] = useState<PrevalenceTrendResponse | null>(null)
  const [comorbidity, setComorbidity] = useState<ComorbidityResponse | null>(null)
  const [scores, setScores] = useState<ScoreDistributionResponse | null>(null)
  const [severity, setSeverity] = useState<ScaleSeverityResponse | null>(null)
  const [workload, setWorkload] = useState<ProfessionalWorkloadResponse | null>(null)
  const [demographics, setDemographics] = useState<DemographicSummaryResponse | null>(null)
  const [monthly, setMonthly] = useState<MonthlyConsultationResponse | null>(null)

  useEffect(() => { fetchData() }, [view])

  const fetchData = async () => {
    setLoading(true)
    try {
      switch (view) {
        case 'prevalence': setPrevalence(await analyticsApi.prevalenceTrends(12, 10)); break
        case 'comorbidity': setComorbidity(await analyticsApi.comorbidity(15)); break
        case 'scores': setScores(await analyticsApi.scoreDistributions()); break
        case 'severity': setSeverity(await analyticsApi.scaleSeverity()); break
        case 'workload': setWorkload(await analyticsApi.professionalWorkload()); break
        case 'demographics': setDemographics(await analyticsApi.demographicSummary()); break
        case 'monthly': setMonthly(await analyticsApi.monthlyConsultations(12)); break
      }
    } finally {
      setLoading(false)
    }
  }

  const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16']

  const renderPrevalence = () => {
    if (!prevalence) return null
    const chartData = prevalence.disorders.flatMap((d) =>
      d.data.map((p) => ({ month: p.month, [d.disorder_name]: p.count }))
    )
    const months = [...new Set(chartData.map((d) => d.month))].sort()
    const grouped = months.map((m) => {
      const row: any = { month: m }
      prevalence.disorders.forEach((d) => {
        const found = d.data.find((p) => p.month === m)
        if (found) row[d.disorder_name] = found.count
      })
      return row
    })

    return (
      <>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          {prevalence.disorders.slice(0, 4).map((d) => (
            <Col span={6} key={d.disorder_name}>
              <Card size="small">
                <Statistic title={d.disorder_name} value={d.total} suffix="diagnósticos" />
              </Card>
            </Col>
          ))}
        </Row>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={grouped}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            {prevalence.disorders.map((d, i) => (
              <Line key={d.disorder_name} type="monotone" dataKey={d.disorder_name} stroke={colors[i % colors.length]} strokeWidth={2} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </>
    )
  }

  const renderComorbidity = () => {
    if (!comorbidity) return null
    const data = comorbidity.pairs.slice(0, 15).map((p) => ({
      pair: `${p.disorder_a.substring(0, 25)}…${p.disorder_b.substring(0, 25)}`,
      count: p.co_occurrence_count,
      pct: p.prevalence_pct,
    }))
    return (
      <ResponsiveContainer width="100%" height={450}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="pair" width={280} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="count" fill="#1890ff" name="Co-ocorrências" />
        </BarChart>
      </ResponsiveContainer>
    )
  }

  const renderComorbidityHeatmap = () => {
    if (!comorbidity || comorbidity.pairs.length === 0) return null
    const topPairs = comorbidity.pairs.slice(0, 30)
    const allDisorders = [...new Set(topPairs.flatMap((p) => [p.disorder_a, p.disorder_b]))].slice(0, 12)
    const maxCount = Math.max(...topPairs.map((p) => p.co_occurrence_count), 1)

    const matrixData = allDisorders.map((disorderA) => {
      const row: Record<string, any> = { disorder: disorderA.length > 18 ? disorderA.substring(0, 16) + '..' : disorderA }
      allDisorders.forEach((disorderB) => {
        if (disorderA === disorderB) { row[disorderB] = null; return }
        const pair = topPairs.find(
          (p) => (p.disorder_a === disorderA && p.disorder_b === disorderB) ||
                 (p.disorder_a === disorderB && p.disorder_b === disorderA)
        )
        row[disorderB] = pair ? pair.co_occurrence_count : null
      })
      return row
    })

    const heatColumns = [
      { title: '', dataIndex: 'disorder', key: 'disorder', width: 140, fixed: 'left' as const },
      ...allDisorders.map((name) => ({
        title: name.length > 10 ? name.substring(0, 10) + '..' : name,
        dataIndex: name,
        key: name,
        width: 70,
        render: (val: number | null) => {
          if (val === null) return <div style={{ background: '#f5f5f5', textAlign: 'center', height: 28 }}>-</div>
          const intensity = Math.min(val / maxCount, 1)
          const r = Math.round(255 - intensity * 230)
          const g = Math.round(255 - intensity * 100)
          const b = Math.round(255 - intensity * 30)
          return (
            <div style={{
              background: `rgb(${r}, ${g}, ${b})`,
              textAlign: 'center',
              fontWeight: val > 3 ? 'bold' : 'normal',
              color: intensity > 0.5 ? '#fff' : '#333',
              height: 28,
              lineHeight: '28px',
              fontSize: 12,
            }}>
              {val}
            </div>
          )
        },
      })),
    ]

    return (
      <div>
        <Typography.Text type="secondary" style={{ marginBottom: 12, display: 'block' }}>
          Matriz de comorbidade (top {allDisorders.length} transtornos) — células mais escuras indicam maior co-ocorrência
        </Typography.Text>
        <Table
          dataSource={matrixData}
          columns={heatColumns}
          rowKey="disorder"
          pagination={false}
          size="small"
          scroll={{ x: allDisorders.length * 70 + 140 }}
          bordered
        />
      </div>
    )
  }

  const renderScores = () => {
    if (!scores) return null
    const data = scores.scales.map((s) => ({
      name: s.scale_name.substring(0, 18),
      mean: s.mean_score,
      median: s.median_score,
      max: s.max_score,
    }))
    return (
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="mean" fill="#1890ff" name="Média" />
          <Bar dataKey="median" fill="#52c41a" name="Mediana" />
        </BarChart>
      </ResponsiveContainer>
    )
  }

  const renderSeverity = () => {
    if (!severity) return null
    const severityColors: Record<string, string> = {
      none: '#d9d9d9', mild: '#52c41a', moderate: '#faad14',
      'moderately severe': '#f5222d', severe: '#722ed1', extreme: '#000',
    }
    return (
      <Row gutter={[16, 16]}>
        {severity.scales.map((s) => {
          const chartData = s.severity_levels.map((l) => ({ name: l.severity, count: l.count }))
          return (
            <Col span={8} key={s.scale_name}>
              <Card size="small" title={s.scale_name}>
                <ResponsiveContainer width="100%" height={150}>
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" tick={{ fontSize: 9 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#1890ff">
                      {chartData.map((entry, i) => (
                        <rect key={i} fill={severityColors[entry.name] || '#1890ff'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          )
        })}
      </Row>
    )
  }

  const renderWorkload = () => {
    if (!workload) return null
    const columns = [
      { title: 'Nome', dataIndex: 'full_name', key: 'name' },
      { title: 'Profissão', dataIndex: 'profession', key: 'prof' },
      { title: 'Especialidade', dataIndex: 'specialty', key: 'spec' },
      { title: 'Consultas', dataIndex: 'total_consultations', key: 'consults', sorter: (a: any, b: any) => a.total_consultations - b.total_consultations },
      { title: 'Pacientes', dataIndex: 'unique_patients', key: 'patients' },
      { title: 'Diagnósticos', dataIndex: 'total_diagnoses', key: 'dx' },
      { title: 'Média Sintomas', dataIndex: 'avg_symptoms_per_consult', key: 'symptoms', render: (v: number) => v.toFixed(1) },
    ]
    return <Table dataSource={workload.professionals} columns={columns} rowKey="full_name" pagination={false} size="small" />
  }

  const renderMonthly = () => {
    if (!monthly) return null
    const data = monthly.months.map((m) => ({
      month: m.year_month,
      consultations: m.total_consultations,
      pacientes: m.unique_patients,
      com_inferencia: m.consultations_with_inference,
    }))
    return (
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="consultations" stroke="#1890ff" strokeWidth={2} name="Consultas" />
          <Line type="monotone" dataKey="pacientes" stroke="#52c41a" strokeWidth={2} name="Pacientes" />
          <Line type="monotone" dataKey="com_inferencia" stroke="#faad14" strokeWidth={2} name="C/ Inferência" />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  const renderDemographics = () => {
    if (!demographics) return null
    const columns = [
      { title: 'Faixa Etária', dataIndex: 'age_group', key: 'age' },
      { title: 'Sexo', dataIndex: 'sex', key: 'sex' },
      { title: 'Escolaridade', dataIndex: 'education_level', key: 'edu' },
      { title: 'Etnia', dataIndex: 'ethnicity', key: 'eth' },
      { title: 'Pacientes', dataIndex: 'patient_count', key: 'count', sorter: (a: any, b: any) => a.patient_count - b.patient_count },
      { title: 'Média Consultas', dataIndex: 'avg_consultations', key: 'avg', render: (v: number) => v.toFixed(1) },
    ]
    return (
      <>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}><Card size="small"><Statistic title="Segmentos" value={demographics.total} /></Card></Col>
        </Row>
        <Table dataSource={demographics.demographics} columns={columns} rowKey={(r) => `${r.age_group}-${r.sex}-${r.education_level}-${r.ethnicity}`} pagination={false} size="small" />
      </>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>Analytics — DW Views</Title>
      <Select
        value={view}
        onChange={setView}
        style={{ width: 320, marginBottom: 24 }}
        options={[
          { value: 'prevalence', label: 'Prevalência por Transtorno' },
          { value: 'comorbidity', label: 'Comorbidade (Pares)' },
          { value: 'scores', label: 'Distribuição de Scores' },
          { value: 'severity', label: 'Severidade por Escala' },
          { value: 'workload', label: 'Carga de Trabalho (Profissionais)' },
          { value: 'monthly', label: 'Consultas Mensais' },
          { value: 'demographics', label: 'Segmentação Demográfica' },
        ]}
      />
      <Spin spinning={loading}>
        <Card>
          {view === 'prevalence' && renderPrevalence()}
          {view === 'comorbidity' && (
            <>
              <div style={{ marginBottom: 12 }}>
                <Segmented options={[{ value: 'bar', label: 'Gráfico de Barras' }, { value: 'heatmap', label: 'Matriz de Calor' }]} value={comorbidityView} onChange={(v) => setComorbidityView(v as 'bar' | 'heatmap')} />
              </div>
              {comorbidityView === 'bar' ? renderComorbidity() : renderComorbidityHeatmap()}
            </>
          )}
          {view === 'scores' && renderScores()}
          {view === 'severity' && renderSeverity()}
          {view === 'workload' && renderWorkload()}
          {view === 'monthly' && renderMonthly()}
          {view === 'demographics' && renderDemographics()}
        </Card>
      </Spin>
    </div>
  )
}
