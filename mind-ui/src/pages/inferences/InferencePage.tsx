import { useEffect, useState } from 'react'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Row, Col, Table, Tag, Spin, Switch, Divider, Alert, Progress } from 'antd'
import { ExperimentOutlined, ThunderboltOutlined, SafetyOutlined } from '@ant-design/icons'
import { inferencesApi } from '../../api/inferences'
import { patientsApi } from '../../api/patients'
import { consultationsApi } from '../../api/consultations'
import { disordersApi } from '../../api/disorders'
import type { PatientListItem, Symptom, InferenceResult } from '../../types'

const { Title, Text } = Typography

export default function InferencePage() {
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [selectedPatient, setSelectedPatient] = useState<string>('')
  const [evidence, setEvidence] = useState<Record<string, boolean>>({})
  const [results, setResults] = useState<InferenceResult[]>([])
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
    if (!selectedPatient) {
      message.warning('Selecione um paciente')
      return
    }
    const presentSymptoms = symptoms
      .filter((s) => evidence[s.symptom_name])
      .map((s) => ({ symptom_id: s.symptom_id, intensity: 50, frequency: 'daily' }))
    if (presentSymptoms.length === 0) {
      message.warning('Selecione pelo menos um sintoma')
      return
    }
    setLoading(true)
    try {
      const patientDetail = await patientsApi.get(selectedPatient)
      const puid = patientDetail.profile.profile_uuid
      if (!puid) throw new Error('Perfil do paciente nao encontrado')
      const created = await consultationsApi.createWithData({
        profile_uuid: puid,
        consultation_date: new Date().toISOString(),
        symptom_observations: presentSymptoms,
      })
      const cuuid = created.consultation_uuid
      if (mode === 'bayesian') {
        const res = await inferencesApi.runBayesian({ consultation_uuid: cuuid })
        setResults(res.inferences)
      } else {
        const res = await inferencesApi.runCriteria({ consultation_uuid: cuuid })
        setResults(res.inferences)
      }
    } catch {
      message.error('Erro ao executar inferencia')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Inferencia Diagnostica' }]} style={{ marginBottom: 16 }} />
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
                <SafetyOutlined /> Criterios DSM-5
              </Tag>
            </div>

            <Alert
              message="Selecione um paciente e os sintomas, depois execute a inferencia"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form layout="vertical">
              <Form.Item label="Paciente">
                <Select
                  showSearch
                  placeholder="Selecione o paciente..."
                  value={selectedPatient || undefined}
                  onChange={setSelectedPatient}
                  options={patients.map((p) => ({ value: p.patient_uuid, label: p.full_name }))}
                />
              </Form.Item>
            </Form>

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
              Executar Inferencia
            </Button>
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card title="Resultados">
            {results.length === 0 ? (
              <Text type="secondary">Selecione os sintomas e execute a inferencia para ver os resultados</Text>
            ) : (
              <Table
                dataSource={results}
                rowKey="disorder_id"
                size="small"
                pagination={false}
                columns={[
                  { title: 'Transtorno', dataIndex: 'disorder_name', ellipsis: true },
                  {
                    title: 'Probabilidade',
                    dataIndex: 'inference_probability',
                    width: 220,
                    render: (v: number) => (
                      <Progress
                        percent={Math.round(v * 100)}
                        size="small"
                        status={v >= 0.7 ? 'success' : v >= 0.4 ? 'active' : 'exception'}
                        format={(p) => `${p}%`}
                      />
                    ),
                  },
                  {
                    title: 'Confianca',
                    dataIndex: 'confidence_level',
                    width: 120,
                    render: (v: number) => v != null ? `${Math.round(v * 100)}%` : '-',
                  },
                  {
                    title: 'Codigos',
                    key: 'codes',
                    render: (_: unknown, r: InferenceResult) =>
                      [r.cid_code && `CID: ${r.cid_code}`, r.dsm_code && `DSM: ${r.dsm_code}`]
                        .filter(Boolean)
                        .join(' | ') || '-',
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
