import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Card, Form, Select, Input, Button, Typography, Breadcrumb, message, Space,
  DatePicker, Slider, InputNumber, Row, Col, Tag, Divider, Checkbox, Collapse,
} from 'antd'
import { PlusOutlined, DeleteOutlined, CheckSquareOutlined, FileTextOutlined } from '@ant-design/icons'
import { consultationsApi } from '../../api/consultations'
import { patientsApi } from '../../api/patients'
import { professionalsApi } from '../../api/professionals'
import { disordersApi } from '../../api/disorders'
import { scalesApi } from '../../api/scales'
import type { PatientListItem, HealthcareProfessionalResponse, Symptom, AssessmentScale, ClinicalNote } from '../../types'

const { Title, Text } = Typography
const { TextArea } = Input

interface SymptomEntry {
  key: string
  symptom_id: number
  symptom_name: string
  intensity: number
  frequency?: string
  duration_days?: number
  clinical_notes?: string
}

interface ScaleResponseValue {
  question_id: number
  response_value: number
}

const FREQUENCY_OPTIONS = [
  { value: 'daily', label: 'Diaria' },
  { value: 'weekly', label: 'Semanal' },
  { value: 'monthly', label: 'Mensal' },
  { value: 'occasionally', label: 'Ocasional' },
  { value: 'continuous', label: 'Continua' },
]

const SCALE_MAX_MAP: Record<string, number> = {
  'PHQ-9': 3,
  'GAD-7': 3,
  'MDQ': 1,
}

const SCALE_LABELS: Record<string, string[]> = {
  'PHQ-9': ['0 - Nenhum dia', '1 - Varios dias', '2 - Mais da metade', '3 - Quase todos os dias'],
  'GAD-7': ['0 - Nenhum dia', '1 - Varios dias', '2 - Mais da metade', '3 - Quase todos os dias'],
  'MDQ': ['0 - Nao', '1 - Sim'],
}

export default function ConsultationCreatePage() {
  const [form] = Form.useForm()
  const [searchParams] = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [professionals, setProfessionals] = useState<HealthcareProfessionalResponse[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [selectedSymptoms, setSelectedSymptoms] = useState<SymptomEntry[]>([])
  const [scales, setScales] = useState<AssessmentScale[]>([])
  const [selectedScaleIds, setSelectedScaleIds] = useState<number[]>([])
  const [scaleResponses, setScaleResponses] = useState<Record<number, number>>({})
  const [clinicalNote, setClinicalNote] = useState<ClinicalNote>({})
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      patientsApi.list(1, 100),
      professionalsApi.list(),
      disordersApi.listSymptoms(),
      scalesApi.list(),
    ]).then(([p, prof, sym, sc]) => {
      setPatients(p.patients)
      setProfessionals(prof.professionals)
      setSymptoms(sym)
      setScales(sc.scales)
      const preSelected = searchParams.get('patient')
      if (preSelected) {
        form.setFieldsValue({ patient_uuid: preSelected })
      }
    })
  }, [])

  const toggleScale = (scaleId: number) => {
    setSelectedScaleIds((prev) =>
      prev.includes(scaleId) ? prev.filter((id) => id !== scaleId) : [...prev, scaleId]
    )
  }

  const setScaleResponse = (questionId: number, value: number) => {
    setScaleResponses((prev) => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    if (selectedSymptoms.length === 0) {
      message.warning('Adicione pelo menos um sintoma')
      return
    }
    setLoading(true)
    try {
      const patient = patients.find((p) => p.patient_uuid === values.patient_uuid)
      if (!patient) throw new Error('Paciente nao encontrado')
      const patientDetail = await patientsApi.get(values.patient_uuid)
      const puid = patientDetail.profile.profile_uuid
      if (!puid) throw new Error('Perfil do paciente nao encontrado')

      const dateValue = values.consultation_date
      const consultationDate = dateValue
        ? new Date(dateValue.toISOString ? dateValue.toISOString() : dateValue).toISOString()
        : new Date().toISOString()

      const scaleResp = Object.entries(scaleResponses).map(([qId, val]) => ({
        question_id: Number(qId),
        response_value: val,
      }))

      const noteFields: (keyof ClinicalNote)[] = [
        'chief_complaint', 'history_present_illness', 'subjective_findings',
        'objective_findings', 'clinical_assessment', 'treatment_plan', 'follow_up',
      ]
      const hasClinicalNote = noteFields.some((f) => clinicalNote[f])
      const payload = {
        profile_uuid: puid,
        consultation_date: consultationDate,
        professional_uuid: values.professional_uuid || undefined,
        consultation_notes: values.consultation_notes || undefined,
        symptom_observations: selectedSymptoms.map((s) => ({
          symptom_id: s.symptom_id,
          intensity: s.intensity,
          frequency: s.frequency || undefined,
          duration_days: s.duration_days || undefined,
          clinical_notes: s.clinical_notes || undefined,
        })),
        scale_responses: scaleResp.length > 0 ? scaleResp : undefined,
        clinical_note: hasClinicalNote
          ? Object.fromEntries(
              noteFields
                .filter((f) => clinicalNote[f])
                .map((f) => [f, clinicalNote[f]])
            )
          : undefined,
      }

      await consultationsApi.createWithData(payload)
      message.success('Consulta registrada com sucesso')
      navigate('/consultations')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Erro ao registrar consulta'
      message.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const addSymptom = (symptomId: number) => {
    if (selectedSymptoms.find((s) => s.symptom_id === symptomId)) return
    const symptom = symptoms.find((s) => s.symptom_id === symptomId)
    setSelectedSymptoms([
      ...selectedSymptoms,
      {
        key: `${symptomId}-${Date.now()}`,
        symptom_id: symptomId,
        symptom_name: symptom?.symptom_name || `Sintoma #${symptomId}`,
        intensity: 50,
        frequency: undefined,
        duration_days: undefined,
        clinical_notes: undefined,
      },
    ])
  }

  const updateSymptom = (key: string, field: string, value: unknown) => {
    setSelectedSymptoms((prev) =>
      prev.map((s) => (s.key === key ? { ...s, [field]: value } : s))
    )
  }

  const removeSymptom = (key: string) => {
    setSelectedSymptoms(selectedSymptoms.filter((s) => s.key !== key))
  }

  const selectedScales = scales.filter((s) => selectedScaleIds.includes(s.scale_id))

  return (
    <>
      <Breadcrumb
        items={[
          { title: 'Dashboard' },
          { title: 'Consultas', href: '/consultations' },
          { title: 'Nova Consulta' },
        ]}
        style={{ marginBottom: 16 }}
      />
      <Card>
        <Title level={4}>Nova Consulta</Title>
        <Form form={form} layout="vertical" style={{ maxWidth: 960 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="patient_uuid"
                label="Paciente"
                rules={[{ required: true, message: 'Selecione o paciente' }]}
              >
                <Select
                  showSearch
                  placeholder="Buscar paciente..."
                  filterOption={(input, option) =>
                    (option?.label as string || '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={patients.map((p) => ({
                    value: p.patient_uuid,
                    label: `${p.full_name}${p.birth_date ? ` (${p.birth_date})` : ''}`,
                  }))}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="professional_uuid" label="Profissional">
                <Select
                  showSearch
                  allowClear
                  placeholder="Selecione o profissional..."
                  filterOption={(input, option) =>
                    (option?.label as string || '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={professionals.map((p) => ({
                    value: p.professional_uuid,
                    label: `${p.full_name}${p.specialty ? ` (${p.specialty})` : ''}`,
                  }))}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="consultation_date" label="Data da Consulta">
                <DatePicker showTime style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="consultation_notes" label="Observacoes">
            <TextArea rows={3} placeholder="Observacoes da consulta..." />
          </Form.Item>

          <Divider />
          <Collapse
            items={[{
              key: 'clinical-doc',
              label: (
                <Space>
                  <FileTextOutlined />
                  <Text strong style={{ fontSize: 16 }}>Documentacao Clinica (SOAP)</Text>
                </Space>
              ),
              children: (
                <>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>Queixa Principal</Text>
                      <TextArea
                        rows={2}
                        placeholder="Relato do paciente sobre o motivo da consulta..."
                        value={clinicalNote.chief_complaint}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, chief_complaint: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                    <Col span={12}>
                      <Text strong>Historia da Doenca Atual (HDA)</Text>
                      <TextArea
                        rows={2}
                        placeholder="Evolucao dos sintomas, inicio, fatores desencadeantes..."
                        value={clinicalNote.history_present_illness}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, history_present_illness: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                  </Row>
                  <Row gutter={16} style={{ marginTop: 12 }}>
                    <Col span={8}>
                      <Text strong>Subjetivo (S)</Text>
                      <TextArea
                        rows={3}
                        placeholder="Percepcao do paciente, sintomas relatados..."
                        value={clinicalNote.subjective_findings}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, subjective_findings: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                    <Col span={8}>
                      <Text strong>Objetivo (O)</Text>
                      <TextArea
                        rows={3}
                        placeholder="Observacoes clinicas, escalas, exames..."
                        value={clinicalNote.objective_findings}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, objective_findings: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                    <Col span={8}>
                      <Text strong>Avaliacao (A)</Text>
                      <TextArea
                        rows={3}
                        placeholder="Hipotese diagnostica, impressao clinica..."
                        value={clinicalNote.clinical_assessment}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, clinical_assessment: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                  </Row>
                  <Row gutter={16} style={{ marginTop: 12 }}>
                    <Col span={12}>
                      <Text strong>Plano (P)</Text>
                      <TextArea
                        rows={2}
                        placeholder="Tratamento, medicacao, terapias, encaminhamentos..."
                        value={clinicalNote.treatment_plan}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, treatment_plan: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                    <Col span={12}>
                      <Text strong>Acompanhamento</Text>
                      <TextArea
                        rows={2}
                        placeholder="Retorno, monitoramento, reavaliacao..."
                        value={clinicalNote.follow_up}
                        onChange={(e) => setClinicalNote((prev) => ({ ...prev, follow_up: e.target.value }))}
                        style={{ marginTop: 4 }}
                      />
                    </Col>
                  </Row>
                </>
              ),
            }]}
          />

          <Divider />
          <Text strong style={{ fontSize: 16 }}>Sintomas</Text>

          <Select
            style={{ width: '100%', marginTop: 8 }}
            placeholder="Adicionar sintoma..."
            showSearch
            filterOption={(input, option) =>
              (option?.label as string || '').toLowerCase().includes(input.toLowerCase())
            }
            labelInValue={false}
            onChange={(value) => { if (value) addSymptom(Number(value)) }}
            options={symptoms.map((s) => ({
              value: s.symptom_id,
              label: `${s.symptom_name}${s.symptom_description ? ` - ${s.symptom_description}` : ''}`,
            }))}
          />

          {selectedSymptoms.map((entry) => (
            <Card
              key={entry.key}
              size="small"
              style={{ marginTop: 12 }}
              type="inner"
              title={
                <Space>
                  <Text strong>{entry.symptom_name}</Text>
                  <Tag color="blue">ID {entry.symptom_id}</Tag>
                </Space>
              }
              extra={
                <Button
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => removeSymptom(entry.key)}
                />
              }
            >
              <Row gutter={16}>
                <Col span={8}>
                  <Text>Intensidade: {entry.intensity}</Text>
                  <Slider
                    min={0}
                    max={100}
                    value={entry.intensity}
                    onChange={(v) => updateSymptom(entry.key, 'intensity', v)}
                  />
                </Col>
                <Col span={8}>
                  <Text>Frequencia</Text>
                  <Select
                    style={{ width: '100%' }}
                    allowClear
                    placeholder="Selecione..."
                    value={entry.frequency}
                    onChange={(v) => updateSymptom(entry.key, 'frequency', v)}
                    options={FREQUENCY_OPTIONS}
                  />
                </Col>
                <Col span={4}>
                  <Text>Duracao (dias)</Text>
                  <InputNumber
                    style={{ width: '100%' }}
                    min={0}
                    placeholder="Dias"
                    value={entry.duration_days}
                    onChange={(v) => updateSymptom(entry.key, 'duration_days', v)}
                  />
                </Col>
                <Col span={4}>
                  <Text>Notas</Text>
                  <Input
                    placeholder="Notas..."
                    value={entry.clinical_notes}
                    onChange={(e) => updateSymptom(entry.key, 'clinical_notes', e.target.value)}
                  />
                </Col>
              </Row>
            </Card>
          ))}

          <Divider />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <CheckSquareOutlined style={{ fontSize: 18 }} />
            <Text strong style={{ fontSize: 16 }}>Escalas de Avaliacao</Text>
          </div>

          <Space wrap>
            {scales.map((sc) => {
              const checked = selectedScaleIds.includes(sc.scale_id)
              return (
                <Tag
                  key={sc.scale_id}
                  style={{
                    cursor: 'pointer',
                    padding: '4px 12px',
                    fontSize: 14,
                    border: checked ? '2px solid #1677ff' : '1px solid #d9d9d9',
                  }}
                  color={checked ? 'blue' : 'default'}
                  onClick={() => toggleScale(sc.scale_id)}
                >
                  <Space>
                    {checked ? <Checkbox checked /> : <Checkbox checked={false} />}
                    {sc.scale_name}
                  </Space>
                </Tag>
              )
            })}
          </Space>

          {selectedScales.map((sc) => {
            const maxVal = SCALE_MAX_MAP[sc.scale_name] ?? 4
            const labels = SCALE_LABELS[sc.scale_name]
            return (
              <Card
                key={sc.scale_id}
                size="small"
                style={{ marginTop: 12 }}
                type="inner"
                title={<Text strong>{sc.scale_name}</Text>}
              >
                {sc.questions
                  .sort((a, b) => a.question_order - b.question_order)
                  .map((q) => (
                    <Row key={q.question_id} gutter={16} align="middle" style={{ marginBottom: 8 }}>
                      <Col flex="auto">
                        <Text>{q.question_order}. {q.question_text}</Text>
                      </Col>
                      <Col flex="200px">
                        <Select
                          style={{ width: '100%' }}
                          placeholder="Selecione..."
                          value={scaleResponses[q.question_id] ?? null}
                          onChange={(v) => setScaleResponse(q.question_id, v)}
                          options={
                            labels
                              ? labels.map((l, idx) => ({ value: idx, label: l }))
                              : Array.from({ length: maxVal + 1 }, (_, i) => ({ value: i, label: String(i) }))
                          }
                        />
                      </Col>
                    </Row>
                  ))}
              </Card>
            )
          })}

          <Divider />
          <Form.Item>
            <Space>
              <Button type="primary" onClick={handleSubmit} loading={loading} size="large">
                Salvar Consulta
              </Button>
              <Button onClick={() => navigate('/consultations')} size="large">
                Cancelar
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </>
  )
}
