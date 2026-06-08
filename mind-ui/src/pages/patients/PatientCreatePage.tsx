import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Select, Button, Typography, Breadcrumb, message, Space, Row, Col } from 'antd'
import dayjs from 'dayjs'
import { patientsApi } from '../../api/patients'
import { referenceApi } from '../../api/reference'
import type { SexType, GenderIdentity, EducationLevel, Ethnicity } from '../../types'

const { Title } = Typography

export default function PatientCreatePage() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [references, setReferences] = useState<{
    sexes: SexType[]
    genders: GenderIdentity[]
    educations: EducationLevel[]
    ethnicities: Ethnicity[]
  }>({ sexes: [], genders: [], educations: [], ethnicities: [] })
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      referenceApi.sexTypes(),
      referenceApi.genderIdentities(),
      referenceApi.educationLevels(),
      referenceApi.ethnicities(),
    ]).then(([sexes, genders, educations, ethnicities]) => {
      setReferences({ sexes, genders, educations, ethnicities })
    })
  }, [])

  const handleSubmit = async (values: Record<string, unknown>) => {
    setLoading(true)
    try {
      const v = values as Record<string, unknown>
      const payload = {
        identity: {
          full_name: v.full_name as string,
          cpf_hash: (v.cpf_hash as string) || undefined,
          email_hash: (v.email_hash as string) || undefined,
        },
        profile: {
          birth_date: (() => {
            const bd = v.birth_date as string
            const parsed = dayjs(bd, 'DD/MM/YYYY')
            return parsed.isValid() ? parsed.format('YYYY-MM-DD') : bd
          })(),
          sex_type_id: v.sex_type_id as number,
          gender_identity_id: v.gender_identity_id as number,
          education_level_id: v.education_level_id as number,
          ethnicity_id: v.ethnicity_id as number,
          marital_status: (v.marital_status as string) || undefined,
          occupation: (v.occupation as string) || undefined,
          trans_status: (v.trans_status as string) || undefined,
        },
      }
      await patientsApi.create(payload)
      message.success('Paciente cadastrado com sucesso')
      navigate('/patients')
    } catch {
      message.error('Erro ao cadastrar paciente')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Pacientes', href: '/patients' }, { title: 'Novo' }]} style={{ marginBottom: 16 }} />
      <Card>
        <Title level={4}>Novo Paciente</Title>
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ maxWidth: 800 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="full_name" label="Nome Completo" rules={[{ required: true, message: 'Obrigatório' }]}>
                <Input />
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
              <Form.Item name="marital_status" label="Estado Civil">
                <Select
                  allowClear
                  options={[
                    { value: 'solteiro', label: 'Solteiro(a)' },
                    { value: 'casado', label: 'Casado(a)' },
                    { value: 'divorciado', label: 'Divorciado(a)' },
                    { value: 'viuvo', label: 'Viúvo(a)' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="occupation" label="Profissão">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
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
              <Form.Item name="cpf_hash" label="CPF (hash)">
                <Input.Password placeholder="Hash do CPF" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="email_hash" label="E-mail (hash)">
                <Input.Password placeholder="Hash do e-mail" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>Salvar</Button>
              <Button onClick={() => navigate('/patients')}>Cancelar</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </>
  )
}
