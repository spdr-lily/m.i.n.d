import { useEffect, useState } from 'react'
import { Card, Form, Select, Button, Typography, Breadcrumb, message, Space, Row, Col, Tag, Result, Spin, Slider, Divider } from 'antd'
import { ExperimentOutlined } from '@ant-design/icons'
import { scalesApi } from '../../api/scales'
import type { AssessmentScale, ScaleScoreResponse } from '../../types'
import { SCALE_OPTIONS, SEVERITY_COLORS } from '../../utils/constants'

const { Title, Text } = Typography

export default function AssessmentPage() {
  const [scales, setScales] = useState<AssessmentScale[]>([])
  const [selectedScale, setSelectedScale] = useState<AssessmentScale | null>(null)
  const [responses, setResponses] = useState<Record<number, number>>({})
  const [result, setResult] = useState<ScaleScoreResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [initLoading, setInitLoading] = useState(true)

  useEffect(() => {
    scalesApi.list().then((data) => {
      setScales(data)
    }).finally(() => setInitLoading(false))
  }, [])

  const handleScaleSelect = (scaleName: string) => {
    const scale = scales.find((s) => s.scale_name === scaleName)
    setSelectedScale(scale || null)
    setResponses({})
    setResult(null)
  }

  const handleScore = async () => {
    if (!selectedScale) return
    const questionIds = selectedScale.questions.sort((a, b) => a.question_order - b.question_order).map((q) => q.question_id)
    const missing = questionIds.filter((id) => responses[id] === undefined)
    if (missing.length > 0) {
      message.warning(`Responda todas as questões antes de pontuar`)
      return
    }
    setLoading(true)
    try {
      const sortedResponses = questionIds.map((id) => responses[id])
      const res = await scalesApi.score({
        scale_name: selectedScale.scale_name,
        responses: sortedResponses,
      })
      setResult(res)
    } catch {
      message.error('Erro ao calcular pontuação')
    } finally {
      setLoading(false)
    }
  }

  const scaleOptions = scales.map((s) => ({
    value: s.scale_name,
    label: SCALE_OPTIONS[s.scale_name]?.label || s.scale_name,
  }))

  if (initLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Escalas de Avaliação' }]} style={{ marginBottom: 16 }} />
      <Row gutter={16}>
        <Col span={result ? 14 : 24}>
          <Card title="Avaliação Clínica">
            <Form layout="vertical">
              <Form.Item label="Escala">
                <Select
                  placeholder="Selecione uma escala"
                  options={scaleOptions}
                  onChange={handleScaleSelect}
                  value={selectedScale?.scale_name || undefined}
                  allowClear
                  onClear={() => { setSelectedScale(null); setResult(null) }}
                />
              </Form.Item>
            </Form>

            {selectedScale && (
              <div>
                <Divider />
                <Text strong style={{ fontSize: 16 }}>{SCALE_OPTIONS[selectedScale.scale_name]?.label || selectedScale.scale_name}</Text>
                {selectedScale.questions
                  .sort((a, b) => a.question_order - b.question_order)
                  .map((q) => {
                    const opts = SCALE_OPTIONS[selectedScale.scale_name]?.options || [
                      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
                    ]
                    return (
                      <div key={q.question_id} style={{ marginTop: 16 }}>
                        <Text>{q.question_order}. {q.question_text}</Text>
                        <Select
                          style={{ width: '100%', marginTop: 4 }}
                          placeholder="Selecione..."
                          value={responses[q.question_id]}
                          onChange={(v) => setResponses({ ...responses, [q.question_id]: v })}
                          options={opts}
                        />
                      </div>
                    )
                  })}
                <Button
                  type="primary"
                  icon={<ExperimentOutlined />}
                  onClick={handleScore}
                  loading={loading}
                  style={{ marginTop: 16 }}
                  block
                  size="large"
                >
                  Calcular Pontuação
                </Button>
              </div>
            )}
          </Card>
        </Col>

        {result && (
          <Col span={10}>
            <Card title="Resultado">
              <Result
                status={result.severity === 'severe' || result.severity === 'moderate' ? 'warning' : 'success'}
                title={`${result.total_score} pontos`}
                subTitle={
                  <Tag color={SEVERITY_COLORS[result.severity]} style={{ fontSize: 16, padding: '4px 12px' }}>
                    {result.severity.toUpperCase()}
                  </Tag>
                }
              />
              <Text>{result.interpretation}</Text>
            </Card>
          </Col>
        )}
      </Row>
    </>
  )
}
