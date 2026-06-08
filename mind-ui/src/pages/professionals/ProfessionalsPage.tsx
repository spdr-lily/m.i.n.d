import { useEffect, useState, useCallback } from 'react'
import { Card, Table, Button, Modal, Form, Input, DatePicker, Select, Space, Typography, Breadcrumb, message, Popconfirm, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { professionalsApi } from '../../api/professionals'
import { patientsApi } from '../../api/patients'
import type { HealthcareProfessionalResponse, PatientListItem } from '../../types'
import dayjs from 'dayjs'

const { Title } = Typography

const PROFESSION_OPTIONS = [
  { label: 'Médico(a)', value: 'Médico' },
  { label: 'Psicólogo(a)', value: 'Psicólogo' },
  { label: 'Enfermeiro(a)', value: 'Enfermeiro' },
  { label: 'Assistente Social', value: 'Assistente Social' },
  { label: 'Terapeuta Ocupacional', value: 'Terapeuta Ocupacional' },
  { label: 'Fonoaudiólogo(a)', value: 'Fonoaudiólogo' },
  { label: 'Nutricionista', value: 'Nutricionista' },
  { label: 'Educador Físico', value: 'Educador Físico' },
  { label: 'Outro', value: 'Outro' },
]

export default function ProfessionalsPage() {
  const [professionals, setProfessionals] = useState<HealthcareProfessionalResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<HealthcareProfessionalResponse | null>(null)
  const [saving, setSaving] = useState(false)
  const [patientOptions, setPatientOptions] = useState<{ label: string; value: string }[]>([])
  const [form] = Form.useForm()

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const [profData, patientData] = await Promise.all([
        professionalsApi.list(),
        patientsApi.list().catch(() => ({ patients: [] })),
      ])
      setProfessionals(profData.professionals)
      setPatientOptions(
        (patientData.patients || []).map((p: PatientListItem) => ({
          label: p.full_name,
          value: p.patient_uuid,
        }))
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (professional: HealthcareProfessionalResponse) => {
    setEditing(professional)
    form.setFieldsValue({
      full_name: professional.full_name,
      professional_license: professional.professional_license,
      profession: professional.profession,
      specialty: professional.specialty,
      start_date: professional.start_date ? dayjs(professional.start_date) : null,
      assigned_patient_uuids: (professional.patient_assignments || []).map(a => a.patient_uuid),
    })
    setModalOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const values = await form.validateFields()
      const payload = {
        full_name: values.full_name,
        profession: values.profession,
        professional_license: values.professional_license,
        specialty: values.specialty,
        start_date: values.start_date ? values.start_date.format('YYYY-MM-DD') : null,
        assigned_patient_uuids: values.assigned_patient_uuids || [],
      }
      if (editing) {
        await professionalsApi.update(editing.professional_uuid, payload)
        message.success('Profissional atualizado com sucesso')
      } else {
        await professionalsApi.create(payload)
        message.success('Profissional criado com sucesso')
      }
      setModalOpen(false)
      fetchData()
    } catch {
      message.error('Erro ao salvar profissional')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (uuid: string) => {
    try {
      await professionalsApi.delete(uuid)
      message.success('Profissional excluído com sucesso')
      fetchData()
    } catch {
      message.error('Erro ao excluir profissional')
    }
  }

  const columns = [
    { title: 'Nome', dataIndex: 'full_name', render: (v: string) => <strong>{v}</strong> },
    { title: 'Profissão', dataIndex: 'profession', width: 140 },
    { title: 'Registro', dataIndex: 'professional_license', width: 140 },
    { title: 'Especialidade', dataIndex: 'specialty', width: 160, ellipsis: true },
    {
      title: 'Data de Entrada', dataIndex: 'start_date', width: 130,
      render: (v: string) => v ? dayjs(v).format('DD/MM/YYYY') : '-',
    },
    {
      title: 'Pacientes', dataIndex: 'patient_assignments', width: 140, ellipsis: true,
      render: (assignments: { patient_name?: string }[] | undefined) =>
        assignments?.length
          ? <Tag color="blue">{assignments.length} associado(s)</Tag>
          : <Tag>0</Tag>,
    },
    {
      title: 'Ações', width: 100,
      render: (_: unknown, record: HealthcareProfessionalResponse) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(record)} />
          <Popconfirm title="Excluir profissional?" onConfirm={() => handleDelete(record.professional_uuid)}>
            <Button icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <>
      <Breadcrumb items={[
        { title: 'Dashboard' },
        { title: 'Profissionais' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Profissionais</Title>
          <Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>Novo Profissional</Button>
        </div>
        <Table
          dataSource={professionals}
          columns={columns}
          rowKey="professional_uuid"
          loading={loading}
          pagination={{ pageSize: 20, showTotal: (t: number) => `${t} profissionais` }}
        />
      </Card>
      <Modal
        title={editing ? 'Editar Profissional' : 'Novo Profissional'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        confirmLoading={saving}
        destroyOnClose
        width={520}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="full_name" label="Nome Completo" rules={[{ required: true, message: 'Obrigatório' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="profession" label="Profissão">
            <Select options={PROFESSION_OPTIONS} allowClear placeholder="Selecione" />
          </Form.Item>
          <Form.Item name="professional_license" label="CRM / CRP">
            <Input placeholder="Ex: CRM-SP 123456" />
          </Form.Item>
          <Form.Item name="specialty" label="Especialidade">
            <Input placeholder="Ex: Psiquiatria, Psicologia Clínica" />
          </Form.Item>
          <Form.Item name="start_date" label="Data de Entrada">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="assigned_patient_uuids" label="Pacientes Associados">
            <Select
              mode="multiple"
              options={patientOptions}
              allowClear
              placeholder="Selecione os pacientes"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
