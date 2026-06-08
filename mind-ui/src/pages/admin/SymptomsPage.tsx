import { useEffect, useState, useCallback } from 'react'
import { Card, Table, Button, Modal, Form, Input, Space, Typography, Breadcrumb, message, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { disordersApi } from '../../api/disorders'
import type { Symptom } from '../../types'

const { Title } = Typography

export default function SymptomsPage() {
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Symptom | null>(null)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const data = await disordersApi.listSymptoms()
      setSymptoms(data)
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

  const openEdit = (symptom: Symptom) => {
    setEditing(symptom)
    form.setFieldsValue({
      symptom_name: symptom.symptom_name,
      symptom_description: symptom.symptom_description,
    })
    setModalOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const values = await form.validateFields()
      if (editing) {
        await disordersApi.updateSymptom(editing.symptom_id, values)
        message.success('Sintoma atualizado com sucesso')
      } else {
        await disordersApi.createSymptom(values)
        message.success('Sintoma criado com sucesso')
      }
      setModalOpen(false)
      fetchData()
    } catch {
      message.error('Erro ao salvar sintoma')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await disordersApi.deleteSymptom(id)
      message.success('Sintoma excluído com sucesso')
      fetchData()
    } catch {
      message.error('Erro ao excluir sintoma')
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'symptom_id', width: 60 },
    { title: 'Nome', dataIndex: 'symptom_name', width: 250, render: (v: string) => <strong>{v}</strong> },
    { title: 'Descrição', dataIndex: 'symptom_description', ellipsis: true },
    {
      title: 'Ações', width: 120,
      render: (_: unknown, record: Symptom) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(record)} />
          <Popconfirm title="Excluir sintoma?" onConfirm={() => handleDelete(record.symptom_id)}>
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
        { title: 'Sintomas' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Sintomas (DSM-5-TR)</Title>
          <Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>Novo Sintoma</Button>
        </div>
        <Table
          dataSource={symptoms}
          columns={columns}
          rowKey="symptom_id"
          loading={loading}
          pagination={{ pageSize: 50, showTotal: (t: number) => `${t} sintomas` }}
        />
      </Card>
      <Modal
        title={editing ? 'Editar Sintoma' : 'Novo Sintoma'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        confirmLoading={saving}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="symptom_name" label="Nome" rules={[{ required: true, message: 'Obrigatório' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="symptom_description" label="Descrição">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
