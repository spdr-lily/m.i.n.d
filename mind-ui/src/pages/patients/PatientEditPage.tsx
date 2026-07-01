import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Form, Input, Select, Button, Typography, Breadcrumb, message, Space, Row, Col, Spin } from 'antd'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import { patientsApi, referenceApi } from '../../api/endpoints'
import type { SexType, GenderIdentity, EducationLevel, Ethnicity } from '../../types'

dayjs.extend(customParseFormat)

const { Title } = Typography

export default function PatientEditPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [references, setReferences] = useState<{
    sexes: SexType[]
    genders: GenderIdentity[]
    educations: EducationLevel[]
    ethnicities: Ethnicity[]
  }>({ sexes: [], genders: [], educations: [], ethnicities: [] })
  const navigate = useNavigate()

  useEffect(() => {
    if (!uuid) return
    Promise.all([
      patientsApi.get(uuid),
      referenceApi.sexTypes(),
      referenceApi.genderIdentities(),
      referenceApi.educationLevels(),
      referenceApi.ethnicities(),
    ]).then(([patient, sexes, genders, educations, ethnicities]) => {
      setReferences({ sexes, genders, educations, ethnicities })
      const { identity, profile } = patient
      let birthDisplay = profile.birth_date || ''
      if (birthDisplay && /^\d{4}-\d{2}-\d{2}$/.test(birthDisplay)) {
        const [y, m, d] = birthDisplay.split('-')
        birthDisplay = `${d}/${m}/${y}`
      }
      form.setFieldsValue({
        full_name: identity.full_name,
        birth_date: birthDisplay,
        sex_type_id: profile.sex_type_id,
        gender_identity_id: profile.gender_identity_id,
        education_level_id: profile.education_level_id,
        ethnicity_id: profile.ethnicity_id,
        marital_status: profile.marital_status,
        occupation: profile.occupation,
        trans_status: profile.trans_status,
      })
    }).catch(() => message.error('Erro ao carregar dados do paciente')).finally(() => setLoading(false))
  }, [uuid, form])

  const handleSubmit = async (values: Record<string, unknown>) => {
    if (!uuid) return
    setSaving(true)
    try {
      const v = values as Record<string, unknown>
      const bd = v.birth_date as string
      const parsed = dayjs(bd, 'DD/MM/YYYY', true)
      await patientsApi.update(uuid, {
        birth_date: parsed.isValid() ? parsed.format('YYYY-MM-DD') : undefined,
        sex_type_id: v.sex_type_id as number,
        gender_identity_id: v.gender_identity_id as number,
        education_level_id: v.education_level_id as number,
        ethnicity_id: v.ethnicity_id as number,
        marital_status: (v.marital_status as string) || undefined,
        occupation: (v.occupation as string) || undefined,
        trans_status: (v.trans_status as string) || undefined,
      })
      message.success('Paciente atualizado com sucesso')
      navigate(`/patients/${uuid}`)
    } catch (err) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      message.error(detail || 'Erro ao atualizar paciente')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <>
      <Breadcrumb items={[
        { title: 'Dashboard' },
        { title: 'Pacientes', href: '/patients' },
        { title: form.getFieldValue('full_name') || 'Editar' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <Title level={4}>Editar Paciente</Title>
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ maxWidth: 800 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="full_name" label="Nome Completo">
                <Input disabled />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="birth_date" label="Data de Nascimento" rules={[
                { required: true, message: 'Obrigatório' },
                { pattern: /^\d{2}\/\d{2}\/\d{4}$/, message: 'Formato: DD/MM/AAAA' },
              ]}>
                <Input placeholder="DD/MM/AAAA" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="sex_type_id" label="Sexo" rules={[{ required: true, message: 'Obrigatório' }]}>
                <Select options={references.sexes.map((s) => ({ value: s.sex_type_id, label: s.description }))} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="gender_identity_id" label="Identidade de Gênero" rules={[{ required: true, message: 'Obrigatório' }]}>
                <Select options={references.genders.map((g) => ({ value: g.gender_identity_id, label: g.description }))} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="education_level_id" label="Escolaridade" rules={[{ required: true, message: 'Obrigatório' }]}>
                <Select options={references.educations.map((e) => ({ value: e.education_level_id, label: e.description }))} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="ethnicity_id" label="Etnia" rules={[{ required: true, message: 'Obrigatório' }]}>
                <Select options={references.ethnicities.map((e) => ({ value: e.ethnicity_id, label: e.description }))} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="trans_status" label="Situação Transgênero">
                <Select allowClear options={[
                  { value: 'cis', label: 'Cisgênero' },
                  { value: 'trans', label: 'Transgênero' },
                  { value: 'intersex', label: 'Intersexo' },
                  { value: 'prefer_not_to_say', label: 'Prefiro não informar' },
                ]} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="marital_status" label="Estado Civil">
                <Select allowClear options={[
                  { value: 'solteiro', label: 'Solteiro(a)' },
                  { value: 'casado', label: 'Casado(a)' },
                  { value: 'divorciado', label: 'Divorciado(a)' },
                  { value: 'viuvo', label: 'Viúvo(a)' },
                ]} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="occupation" label="Profissão">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={saving}>Salvar</Button>
              <Button onClick={() => navigate(`/patients/${uuid}`)}>Cancelar</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </>
  )
}
