import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Select, Input, Button, Typography, Breadcrumb, message, Space, Table, Tag } from 'antd'
import { consultationsApi } from '../../api/consultations'
import { patientsApi } from '../../api/patients'
import { disordersApi } from '../../api/disorders'
import type { PatientListItem, Symptom } from '../../types'

const { Title, Text } = Typography
const { TextArea } = Input

export default function ConsultationCreatePage() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [patients, setPatients] = useState<PatientListItem[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [selectedSymptoms, setSelectedSymptoms] = useState<{ symptom_id: number; intensity?: number }[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    patientsApi.list(1, 100).then((data) => setPatients(data.patients))
    disordersApi.listSymptoms().then(setSymptoms)
  }, [])

  const handleSubmit = async (values: Record<string, unknown>) => {
    if (selectedSymptoms.length === 0) {
      message.warning('Adicione pelo menos um sintoma')
      return
    }
    setLoading(true)
    try {
      await consultationsApi.create({
        patient_uuid: values.patient_uuid as string,
        professional_uuid: values.professional_uuid as string,
        consultation_notes: values.consultation_notes as string,
        symptoms: selectedSymptoms.map((s) => ({
          symptom_id: s.symptom_id,
          intensity: s.intensity || 1,
        })),
      })
      message.success('Consulta registrada com sucesso')
      navigate('/consultations')
    } catch {
      message.error('Erro ao registrar consulta')
    } finally {
      setLoading(false)
    }
  }

  const addSymptom = (symptomId: number) => {
    if (selectedSymptoms.find((s) => s.symptom_id === symptomId)) return
    setSelectedSymptoms([...selectedSymptoms, { symptom_id: symptomId, intensity: 1 }])
  }

  const removeSymptom = (symptomId: number) => {
    setSelectedSymptoms(selectedSymptoms.filter((s) => s.symptom_id !== symptomId))
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Consultas', href: '/consultations' }, { title: 'Nova' }]} style={{ marginBottom: 16 }} />
      <Card>
        <Title level={4}>Nova Consulta</Title>
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ maxWidth: 800 }}>
          <Form.Item name="patient_uuid" label="Paciente" rules={[{ required: true, message: 'Selecione o paciente' }]}>
            <Select
              showSearch
              placeholder="Buscar paciente..."
              filterOption={(input, option) => (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
              options={patients.map((p) => ({ value: p.patient_uuid, label: p.full_name }))}
            />
          </Form.Item>
          <Form.Item name="professional_uuid" label="Profissional" rules={[{ required: true, message: 'Obrigatório' }]}>
            <Input placeholder="UUID do profissional" />
          </Form.Item>
          <Form.Item name="consultation_notes" label="Observações">
            <TextArea rows={3} />
          </Form.Item>

          <div style={{ marginBottom: 16 }}>
            <Text strong>Sintomas</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="Adicionar sintoma..."
              showSearch
              filterOption={(input, option) => (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
              onSelect={(value) => { if (typeof value === 'number') addSymptom(value) }}
              value={undefined}
              options={symptoms.map((s) => ({ value: s.symptom_id, label: `${s.symptom_name}${s.symptom_description ? ' - ' + s.symptom_description : ''}` }))}
            />
            {selectedSymptoms.length > 0 && (
              <div style={{ marginTop: 8 }}>
                {selectedSymptoms.map((s) => {
                  const symptom = symptoms.find((sym) => sym.symptom_id === s.symptom_id)
                  return (
                    <Tag key={s.symptom_id} closable onClose={() => removeSymptom(s.symptom_id)} style={{ marginBottom: 4 }}>
                      {symptom?.symptom_name || s.symptom_id}
                    </Tag>
                  )
                })}
              </div>
            )}
          </div>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>Salvar Consulta</Button>
              <Button onClick={() => navigate('/consultations')}>Cancelar</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </>
  )
}
