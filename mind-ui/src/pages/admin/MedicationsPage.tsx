import { useEffect, useState, useCallback } from 'react'
import { Card, Table, Button, Modal, Form, Input, Select, Space, Typography, Breadcrumb, message, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { medicationsApi } from '../../api/endpoints'
import type { Medication } from '../../types'

const { Title } = Typography

const CLASSIFICATION_OPTIONS = [
  'Antidepressivo (ISRS)', 'Antidepressivo (ISRSN)', 'Antidepressivo (NDRI)',
  'Antidepressivo (NaSSA)', 'Antipsicótico (Atípico)', 'Antipsicótico (Típico)',
  'Estabilizador de Humor', 'Ansiolítico (Benzodiazepínico)',
  'Psicoestimulante', 'Hipnótico', 'Outro',
]

export default function MedicationsPage() {
  const [medications, setMedications] = useState<Medication[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Medication | null>(null)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const data = await medicationsApi.list()
      setMedications(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const openCreate = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const openEdit = (med: Medication) => {
    setEditing(med)
    setModalOpen(true)
  }

  useEffect(() => {
    if (!modalOpen) return
    if (editing) {
      form.setFieldsValue(editing)
    } else {
      setTimeout(() => form.resetFields(), 0)
    }
  }, [modalOpen])

  const handleSave = async () => {
    setSaving(true)
    try {
      const values = await form.validateFields()
      const cleaned = {
        name: values.name,
        ...(values.active_ingredient ? { active_ingredient: values.active_ingredient } : {}),
        ...(values.classification ? { classification: values.classification } : {}),
        ...(values.description ? { description: values.description } : {}),
      }
      if (editing) {
        await medicationsApi.update(editing.medication_id, cleaned)
      } else {
        await medicationsApi.create(cleaned)
      }
      message.success(editing ? 'Medicamento atualizado' : 'Medicamento criado')
      setModalOpen(false)
      fetchData()
    } catch (err: unknown) {
      console.error('Medication save error:', err)
      const anyErr = err as { response?: { data?: { detail?: string } }; message?: string }
      const detail = anyErr?.response?.data?.detail || anyErr?.message
      if (detail) message.error(`Erro: ${detail}`)
      throw err
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await medicationsApi.delete(id)
      message.success('Medicamento excluído')
      fetchData()
    } catch {
      message.error('Erro ao excluir medicamento')
    }
  }

  const classifications: string[] = [...new Set(medications.map((m) => m.classification).filter((c): c is string => !!c))]

  const columns = [
    { title: 'ID', dataIndex: 'medication_id', width: 60, sorter: (a: Medication, b: Medication) => a.medication_id - b.medication_id },
    {
      title: 'Nome', dataIndex: 'name', width: 200,
      sorter: (a: Medication, b: Medication) => a.name.localeCompare(b.name, 'pt-BR'),
      render: (v: string) => <strong>{v}</strong>,
    },
    { title: 'Princípio Ativo', dataIndex: 'active_ingredient', width: 180 },
    {
      title: 'Classificação', dataIndex: 'classification', width: 220,
      filters: classifications.map((c) => ({ text: c as string, value: c as string })),
      onFilter: (value: unknown, record: Medication) => record.classification === value,
      render: (v: string) => v || '-',
    },
    { title: 'Descrição', dataIndex: 'description', ellipsis: true },
    {
      title: 'Ações', width: 120,
      render: (_: unknown, record: Medication) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(record)} />
          <Popconfirm title="Excluir medicamento?" onConfirm={() => handleDelete(record.medication_id)}>
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
        { title: 'Medicamentos' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Medicamentos</Title>
          <Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>Novo Medicamento</Button>
        </div>
        <Table
          dataSource={medications}
          columns={columns}
          rowKey="medication_id"
          loading={loading}
          pagination={{ pageSize: 50, showTotal: (t: number) => `${t} medicamentos` }}
        />
      </Card>
      <Modal
        title={editing ? 'Editar Medicamento' : 'Novo Medicamento'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        confirmLoading={saving}
        destroyOnClose
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Nome" rules={[{ required: true, message: 'Obrigatório' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="active_ingredient" label="Princípio Ativo">
            <Input />
          </Form.Item>
          <Form.Item name="classification" label="Classificação">
            <Select allowClear options={CLASSIFICATION_OPTIONS.map((c) => ({ value: c, label: c }))} />
          </Form.Item>
          <Form.Item name="description" label="Descrição">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
