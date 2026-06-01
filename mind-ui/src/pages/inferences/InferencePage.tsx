import { useEffect, useState } from 'react'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Row, Col, Table, Tag, Spin, Switch, Divider, Alert } from 'antd'
import { ExperimentOutlined, ThunderboltOutlined, SafetyOutlined } from '@ant-design/icons'
import { inferencesApi } from '../../api/inferences'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import { disordersApi } from '../../api/disorders'
import type { PatientListItem, Symptom, BayesianResult } from '../../types'

const { Title, Text } = Typography

export default function InferencePage() {
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [selectedPatient, setSelectedPatient] = useState<string>('')
  const [evidence, setEvidence] = useState<Record<string, boolean>>({})
  const [results, setResults] = useState<BayesianResult[]>([])
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<'bayesian' | 'criteria'>('bayesian')

  useEffect(() => {
    patientsApi.list(1, 100).then((data) => setPatients(data.patients))
    disordersApi.listSymptoms().then(setSymptoms)
  }, [])

  const toggleSymptom = (symptomName: string) => {
    setEvidence((prev) => ({ ...prev, [symptomName]: !prev[symptomName] }))
  }

  const handleRun = async () => {
    const activeEvidence = Object.fromEntries(Object.entries(evidence).filter(([, v]) => v))
    if (Object.keys(activeEvidence).length === 0) {
      message.warning('Selecione pelo menos um sintoma')
      return
    }
    setLoading(true)
    try {
      if (mode === 'bayesian') {
        const res = await inferencesApi.runBayesian({ evidence: activeEvidence, top_k: 5 })
        setResults(
          res.map((r) => ({
            ...r,
            confidence: r.posterior_probability,
          }))
        )
      } else {
        const obs = Object.fromEntries(
          Object.entries(activeEvidence).map(([k, v]) => [k, String(v)])
        )
        const res = await inferencesApi.runCriteria({
          consultation_uuid: '',
          observations: obs,
        })
        setResults(
          res.results.map((r) => ({
            disorder_name: r.disorder_name,
            prior_probability: 0,
            posterior_probability: r.probability,
            confidence: r.probability,
            supporting_symptoms: r.supporting_symptoms,
            excluding_symptoms: [],
          }))
        )
      }
    } catch {
      message.error('Erro ao executar inferência')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Inferência Diagnóstica' }]} style={{ marginBottom: 16 }} />
      <Row gutter={16}>
        <Col xs={24} lg={10}>
          <Card title="Sintomas Observados">
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              <Tag
                color={mode === 'bayesian' ? 'blue' : 'default'}
                style={{ cursor: 'pointer', padding: '4px 12px' }}
                onClick={() => setMode('bayesian')}
              >
                <ThunderboltOutlined /> Bayesiano
              </Tag>
              <Tag
                color={mode === 'criteria' ? 'purple' : 'default'}
                style={{ cursor: 'pointer', padding: '4px 12px' }}
                onClick={() => setMode('criteria')}
              >
                <SafetyOutlined /> Critérios DSM-5
              </Tag>
            </div>

            <Alert
              message={mode === 'bayesian' ? 'Rede Bayesiana com Naive Bayes' : 'Avaliação baseada em critérios diagnósticos DSM-5-TR'}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
              {symptoms.map((s) => (
                <div
                  key={s.symptom_id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 0',
                    borderBottom: '1px solid #f0f0f0',
                  }}
                >
                  <Text>{s.symptom_name}</Text>
                  <Switch
                    checked={!!evidence[s.symptom_name]}
                    onChange={() => toggleSymptom(s.symptom_name)}
                    checkedChildren="Presente"
                    unCheckedChildren="Ausente"
                  />
                </div>
              ))}
            </div>

            <Button
              type="primary"
              icon={<ExperimentOutlined />}
              onClick={handleRun}
              loading={loading}
              block
              size="large"
              style={{ marginTop: 16 }}
            >
              Executar Inferência
            </Button>
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card title="Resultados">
            {results.length === 0 ? (
              <Text type="secondary">Selecione os sintomas e execute a inferência para ver os resultados</Text>
            ) : (
              <Table
                dataSource={results}
                rowKey="disorder_name"
                size="small"
                pagination={false}
                columns={[
                  { title: 'Transtorno', dataIndex: 'disorder_name', ellipsis: true },
                  {
                    title: 'Probabilidade',
                    dataIndex: 'posterior_probability',
                    width: 140,
                    render: (v: number) => {
                      const pct = (v * 100).toFixed(1)
                      const color = v > 0.7 ? '#f5222d' : v > 0.4 ? '#fa8c16' : '#52c41a'
                      return (
                        <span>
                          <Tag color={color}>{pct}%</Tag>
                        </span>
                      )
                    },
                  },
                  {
                    title: 'Confiança',
                    dataIndex: 'confidence',
                    width: 140,
                    render: (v: number) => {
                      const pct = (v * 100).toFixed(1)
                      return <Tag>{pct}%</Tag>
                    },
                  },
                  {
                    title: 'Sintomas',
                    dataIndex: 'supporting_symptoms',
                    ellipsis: true,
                    render: (symptoms: string[]) => (
                      <span>
                        {symptoms.slice(0, 3).map((s) => (
                          <Tag key={s} color="blue" style={{ marginBottom: 2 }}>{s}</Tag>
                        ))}
                        {symptoms.length > 3 && <Tag>+{symptoms.length - 3}</Tag>}
                      </span>
                    ),
                  },
                ]}
              />
            )}
          </Card>
        </Col>
      </Row>
    </>
  )
}
