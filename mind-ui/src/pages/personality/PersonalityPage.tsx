import { useEffect, useState, useCallback } from 'react'
import { Card, Select, Typography, Breadcrumb, Tag, Space, Spin, Row, Col, Progress, Empty, Tooltip, Modal, message, Button, Divider } from 'antd'
import { FormOutlined, CheckOutlined } from '@ant-design/icons'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'
import { patientsApi } from '../../api/patients'
import { mlApi, scalesApi } from '../../api/scales'
import type { PatientListItem, PersonalityFactorsResponse, FactorScore } from '../../types'
import { SCALE_OPTIONS } from '../../utils/constants'
const { Title, Text } = Typography

const BFP_FACTORS = ['Abertura', 'Conscienciosidade', 'Extroversão', 'Amabilidade', 'Neuroticismo']
const DT12_SUBSCALES = ['Maquiavelismo', 'Narcisismo', 'Psicopatia']
const HEXACO_FACTORS = ['Honestidade-Humildade', 'Emotionalidade', 'Extroversão', 'Amabilidade', 'Conscienciosidade', 'Abertura à Experiência']
const BIS11_SUBSCALES = ['Atenção', 'Motor', 'Não-planejamento']
const TAS20_SUBSCALES = ['DIF', 'DDF', 'EOT']
const RSES_LABEL = 'Autoestima'

const SEVERITY_COLORS: Record<string, string> = {
  'Muito elevado': '#f5222d', 'Elevado': '#fa541c', 'Elevada': '#fa541c',
  'Moderado': '#faad14', 'Moderada': '#faad14', 'Baixo': '#52c41a',
  'Baixa': '#52c41a', 'Muito baixo': '#8c8c8c', 'Muito baixa': '#8c8c8c',
  'Médio': '#faad14', 'Média': '#faad14',
  'Muito alto': '#f5222d', 'Alto': '#fa541c', 'Ausente': '#52c41a',
}

const FACTOR_COLORS: Record<string, string> = {
  Abertura: '#1677ff', Conscienciosidade: '#52c41a',
  Extroversão: '#faad14', Amabilidade: '#eb2f96', Neuroticismo: '#f5222d',
  'Honestidade-Humildade': '#08979c', Emotionalidade: '#d4380d',
  'Abertura à Experiência': '#722ed1',
  Atenção: '#fa8c16', Motor: '#cf1322', 'Não-planejamento': '#237804',
  DIF: '#d4380d', DDF: '#eb2f96', EOT: '#7cb305',
  Autoestima: '#1677ff',
}

const DATA_SOURCE_LABELS: Record<string, { label: string; color: string }> = {
  real: { label: 'Dados reais (questionário)', color: 'green' },
  ml_predicted: { label: 'Previsto por ML (escalas clínicas)', color: 'blue' },
  unavailable: { label: 'Sem dados disponíveis', color: 'default' },
}

function bfpLevel(score: number) {
  if (score >= 80) return 'Muito alto'
  if (score >= 60) return 'Alto'
  if (score >= 40) return 'Médio'
  if (score >= 20) return 'Baixo'
  return 'Muito baixo'
}

function dt12Level(score: number) {
  if (score >= 54) return 'Muito elevado'
  if (score >= 36) return 'Elevado'
  if (score >= 18) return 'Moderado'
  return 'Baixo'
}

function hexacoLevel(score: number) {
  if (score >= 250) return 'Muito alto'
  if (score >= 200) return 'Alto'
  if (score >= 120) return 'Médio'
  return 'Baixo'
}

function bis11Level(score: number) {
  if (score >= 60) return 'Muito elevada'
  if (score >= 45) return 'Elevada'
  if (score >= 30) return 'Moderada'
  return 'Baixa'
}

function tas20Level(score: number) {
  if (score >= 50) return 'Muito elevada'
  if (score >= 40) return 'Elevada'
  if (score >= 30) return 'Moderada'
  return 'Ausente'
}

function rsesLevel(score: number) {
  if (score >= 35) return 'Elevada'
  if (score >= 25) return 'Média'
  if (score >= 15) return 'Baixa'
  return 'Muito baixa'
}

const LEVEL_FNS: Record<string, (s: number) => string> = {
  bfp: bfpLevel, dt12: dt12Level, hexaco: hexacoLevel,
  bis11: bis11Level, tas20: tas20Level, rses: rsesLevel,
}

function colorForFactor(factor: string): string {
  return FACTOR_COLORS[factor] || '#1677ff'
}

function getFactors(obj: any, keyType: 'factors' | 'subscales' | 'dimensions'): Record<string, FactorScore> {
  return obj?.[keyType] || {}
}

function itemsOf(keyType: 'factors' | 'subscales' | 'dimensions', factors: Record<string, FactorScore>): string[] {
  return Object.keys(factors)
}

function radarTransform(factors: Record<string, FactorScore>, totalMax: number): { factor: string; score: number; fill: string }[] {
  return Object.entries(factors).map(([f, fs]) => ({
    factor: f,
    score: Math.round(((fs?.score || 0) / (fs?.max_possible || totalMax)) * 100),
    fill: colorForFactor(f),
  }))
}

interface ScaleCardProps {
  titleKey: string
  tagColor: string
  tagLabel: string
  title: string
  factorType: 'factors' | 'subscales' | 'dimensions'
  factorNames: string[]
  factors: Record<string, FactorScore>
  totalScore: number
  totalMax: number
  levelFn: (s: number) => string
  showRadar?: boolean
  ds: string
}

function ScaleCard({ tagColor, tagLabel, title, factorType, factorNames, factors, totalScore, totalMax, levelFn, showRadar, ds }: ScaleCardProps) {
  const rd = showRadar && ds === 'real' && Object.keys(factors).length > 0 ? radarTransform(factors, totalMax) : null
  return (
    <Card title={<Space><Tag color={tagColor}>{tagLabel}</Tag> {title}</Space>} size="small" style={{ marginBottom: 16, height: '100%' }}>
      <Row gutter={[8, 16]}>
        {factorNames.map((f) => {
          if (!factors[f]) return null
          const { score, max_possible, description } = factors[f]
          const pct = max_possible > 0 ? Math.round(score / max_possible * 100) : 0
          return (
            <Col span={24} key={f}>
              <div style={{ marginBottom: 2 }}>
                <Tooltip title={description || ''}>
                  <Text style={{ color: colorForFactor(f), fontWeight: 600, fontSize: factorType === 'dimensions' ? 14 : 13 }}>{f}</Text>
                </Tooltip>
                <Text style={{ float: 'right' }}>{score}/{max_possible}</Text>
              </div>
              <Progress percent={pct} strokeColor={colorForFactor(f)} showInfo={false} size="small" />
            </Col>
          )
        })}
      </Row>
      <div style={{ marginTop: 12, textAlign: 'center' }}>
        <Text type="secondary">Total: </Text>
        <Text strong>{totalScore}/{totalMax}</Text>
        <Tag color={SEVERITY_COLORS[levelFn(totalScore)] || 'default'} style={{ marginLeft: 6 }}>
          {levelFn(totalScore)}
        </Tag>
      </div>
      {rd && (
        <div style={{ marginTop: 12, height: 200 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={rd}>
              <PolarGrid />
              <PolarAngleAxis dataKey="factor" fontSize={10} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
              <Radar name={tagLabel} dataKey="score" stroke={tagColor === 'blue' ? '#1677ff' : tagColor === 'volcano' ? '#f5222d' : '#722ed1'} fill={tagColor === 'blue' ? '#1677ff' : tagColor === 'volcano' ? '#f5222d' : '#722ed1'} fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}

export default function PersonalityPage() {
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [patientUuid, setPatientUuid] = useState<string | undefined>()
  const [loading, setLoading] = useState(false)
  const [factors, setFactors] = useState<PersonalityFactorsResponse | null>(null)

  useEffect(() => {
    patientsApi.list(1, 100).then((r) => setPatients(r.patients))
  }, [])

  const fetchFactors = useCallback(async (uuid: string) => {
    setLoading(true)
    try {
      const data = await mlApi.personalityFactors(uuid)
      setFactors(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (patientUuid) {
      setFactors(null)
      fetchFactors(patientUuid)
    }
  }, [patientUuid, fetchFactors])

  const ds = factors?.data_source || 'unavailable'
  const dsInfo = DATA_SOURCE_LABELS[ds] || DATA_SOURCE_LABELS.unavailable

  // ── Questionnaire modal state ──
  const PERSONALITY_SCALE_NAMES = ['BFP', 'DT-12 (Tríade Sombria)', 'HEXACO-60', 'BIS-11', 'TAS-20', 'RSES']
  const [qModalOpen, setQModalOpen] = useState(false)
  const [qScale, setQScale] = useState<string | undefined>()
  const [qQuestions, setQQuestions] = useState<{ question_id: number; question_text: string; response_value: number }[]>([])
  const [qResponses, setQResponses] = useState<Record<number, number>>({})
  const [qLoading, setQLoading] = useState(false)
  const [qSaving, setQSaving] = useState(false)

  const openQModal = () => {
    setQScale(undefined)
    setQQuestions([])
    setQResponses({})
    setQModalOpen(true)
  }

  const handleQScaleChange = async (name: string) => {
    setQScale(name)
    setQResponses({})
    try {
      const qs = await scalesApi.getDetail(name)
      setQQuestions(qs)
    } catch { setQQuestions([]) }
  }

  const handleQSave = async () => {
    if (!patientUuid || !qScale || qQuestions.length === 0) return
    const missing = qQuestions.filter((q) => qResponses[q.question_id] === undefined)
    if (missing.length > 0) {
      message.warning(`Responda todas as questões (${missing.length} pendentes)`)
      return
    }
    setQSaving(true)
    try {
      const values = qQuestions.map((q) => qResponses[q.question_id])
      const res = await scalesApi.apply(patientUuid, qScale, values)
      message.success(`Questionário salvo na consulta ${res.consultation_uuid.slice(0, 8)}...`)
      setQModalOpen(false)
      setQScale(undefined)
      setQQuestions([])
      setQResponses({})
      // Refresh personality data
      setFactors(null)
      fetchFactors(patientUuid)
    } catch { message.error('Erro ao salvar questionário de personalidade') }
    finally { setQSaving(false) }
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Perfil de Personalidade' }]} style={{ marginBottom: 16 }} />
      <Card>
        <Title level={4} style={{ marginBottom: 16 }}>Perfil de Personalidade</Title>
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24} md={10}>
            <Select
              showSearch placeholder="Selecione um paciente" style={{ width: '100%' }}
              value={patientUuid} onChange={setPatientUuid}
              filterOption={(input, option) => (option?.label as string)?.toLowerCase()?.includes(input.toLowerCase())}
              options={patients.map((p) => ({ value: p.patient_uuid, label: `${p.full_name} (${p.patient_uuid?.slice(0, 8)})` }))}
            />
          </Col>
          <Col xs={12} md={7}>
            {patientUuid && <Tag color={dsInfo.color}>{dsInfo.label}</Tag>}
          </Col>
          <Col xs={12} md={7} style={{ textAlign: 'right' }}>
            <Button type="primary" icon={<FormOutlined />} disabled={!patientUuid} onClick={openQModal}>
              Aplicar Questionário
            </Button>
          </Col>
        </Row>

        {!patientUuid && <Empty description="Selecione um paciente para ver o perfil de personalidade" />}
        {patientUuid && loading && <Spin style={{ display: 'block', margin: '40px auto' }} />}

        {patientUuid && !loading && factors && (
          <>
            {/* Row 1: BFP + DT-12 */}
            <Row gutter={16} style={{ marginBottom: 4 }}>
              <Col xs={24} lg={12}>
                <ScaleCard titleKey="bfp" tagColor="blue" tagLabel="BFP"
                  title="Big Five — 5 Fatores (25 itens)"
                  factorType="factors" factorNames={BFP_FACTORS}
                  factors={getFactors(factors.bfp, 'factors')}
                  totalScore={factors.bfp?.total_score || 0} totalMax={factors.bfp?.total_max || 100}
                  levelFn={bfpLevel} showRadar ds={ds} />
              </Col>
              <Col xs={24} lg={12}>
                <ScaleCard titleKey="dt12" tagColor="volcano" tagLabel="DT-12"
                  title="Tríade Sombria — Dirty Dozen (12 itens)"
                  factorType="subscales" factorNames={DT12_SUBSCALES}
                  factors={getFactors(factors.dt12, 'subscales')}
                  totalScore={factors.dt12?.total_score || 0} totalMax={factors.dt12?.total_max || 72}
                  levelFn={dt12Level} ds={ds} />
              </Col>
            </Row>

            {/* Row 2: HEXACO-60 + BIS-11 */}
            <Row gutter={16} style={{ marginBottom: 4 }}>
              <Col xs={24} lg={12}>
                <ScaleCard titleKey="hexaco" tagColor="cyan" tagLabel="HEXACO-60"
                  title="HEXACO — 6 Fatores (60 itens, Lee & Ashton, 2009)"
                  factorType="factors" factorNames={HEXACO_FACTORS}
                  factors={getFactors(factors.hexaco, 'factors')}
                  totalScore={factors.hexaco?.total_score || 0} totalMax={factors.hexaco?.total_max || 300}
                  levelFn={hexacoLevel} showRadar ds={ds} />
              </Col>
              <Col xs={24} lg={12}>
                <ScaleCard titleKey="bis11" tagColor="orange" tagLabel="BIS-11"
                  title="Impulsividade — Barratt (30 itens, 1995)"
                  factorType="subscales" factorNames={BIS11_SUBSCALES}
                  factors={getFactors(factors.bis11, 'subscales')}
                  totalScore={factors.bis11?.total_score || 0} totalMax={factors.bis11?.total_max || 120}
                  levelFn={bis11Level} ds={ds} />
              </Col>
            </Row>

            {/* Row 3: TAS-20 + RSES */}
            <Row gutter={16} style={{ marginBottom: 4 }}>
              <Col xs={24} lg={12}>
                <ScaleCard titleKey="tas20" tagColor="red" tagLabel="TAS-20"
                  title="Alexitimia — Toronto (20 itens, Bagby et al., 1994)"
                  factorType="subscales" factorNames={TAS20_SUBSCALES}
                  factors={getFactors(factors.tas20, 'subscales')}
                  totalScore={factors.tas20?.total_score || 0} totalMax={factors.tas20?.total_max || 100}
                  levelFn={tas20Level} ds={ds} />
              </Col>
              <Col xs={24} lg={12}>
                <ScaleCard titleKey="rses" tagColor="green" tagLabel="RSES"
                  title="Autoestima — Rosenberg (10 itens, 1965)"
                  factorType="dimensions" factorNames={[RSES_LABEL]}
                  factors={{ [RSES_LABEL]: getFactors(factors.rses, 'dimensions')[RSES_LABEL] || { score: 0, max_possible: 40 } }}
                  totalScore={factors.rses?.total_score || 0} totalMax={factors.rses?.total_max || 40}
                  levelFn={rsesLevel} ds={ds} />
              </Col>
            </Row>
          </>
        )}

        {ds === 'ml_predicted' && patientUuid && factors?.feature_scales && (
          <Card size="small" title="Características usadas para predição de personalidade" style={{ marginTop: 16 }}>
            <Row gutter={[8, 8]}>
              {Object.entries(factors.feature_scales).map(([name, val]) => (
                <Col span={6} key={name}>
                  <Text style={{ fontSize: 12 }}>{name}: </Text>
                  <Text strong style={{ fontSize: 12 }}>{val}</Text>
                </Col>
              ))}
            </Row>
          </Card>
        )}
      </Card>

      {/* ── Questionnaire Modal ── */}
      <Modal title="Aplicar Questionário de Personalidade" open={qModalOpen}
        onCancel={() => { setQModalOpen(false); setQQuestions([]) }}
        footer={[
          <Button key="cancel" onClick={() => setQModalOpen(false)}>Cancelar</Button>,
          <Button key="save" type="primary" icon={<CheckOutlined />} loading={qSaving}
            disabled={!qScale || qQuestions.length === 0} onClick={handleQSave}>
            Salvar e Pontuar
          </Button>,
        ]}
        width={700}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Select placeholder="Selecione o questionário de personalidade"
            value={qScale} onChange={handleQScaleChange}
            style={{ width: '100%' }}
            options={PERSONALITY_SCALE_NAMES.map((n) => ({ value: n, label: SCALE_OPTIONS[n]?.label || n }))}
          />
          {qScale && qQuestions.length === 0 && <Spin style={{ display: 'block', margin: 20 }} />}
          {qQuestions.length > 0 && (
            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
              {qQuestions.map((q, i) => {
                const opts = SCALE_OPTIONS[qScale || '']?.options || [
                  { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
                ]
                return (
                  <div key={q.question_id} style={{ marginBottom: 10 }}>
                    <Text style={{ fontSize: 13 }}>{i + 1}. {q.question_text}</Text>
                    <Select
                      style={{ width: '100%', marginTop: 4 }}
                      placeholder="Selecione..."
                      value={qResponses[q.question_id]}
                      onChange={(v) => setQResponses({ ...qResponses, [q.question_id]: v })}
                      options={opts}
                    />
                  </div>
                )
              })}
            </div>
          )}
        </Space>
      </Modal>
    </>
  )
}
