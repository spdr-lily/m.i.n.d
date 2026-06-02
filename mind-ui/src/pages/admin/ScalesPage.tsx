import { useEffect, useState, useCallback } from 'react'
import {
  Card, Table, Button, Typography, Breadcrumb, Space, Modal, Form, Input,
  InputNumber, message, Popconfirm, Tag, Tooltip,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, OrderedListOutlined } from '@ant-design/icons'
import { scalesApi } from '../../api/scales'
import type { AssessmentScale, ScaleQuestion, ScaleCreateRequest, ScaleQuestionCreateRequest } from '../../types'

const { Title, Text } = Typography

export default function ScalesPage() {
  const [scales, setScales] = useState<AssessmentScale[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [scaleModal, setScaleModal] = useState(false)
  const [editingScale, setEditingScale] = useState<AssessmentScale | null>(null)
  const [scaleForm] = Form.useForm()
  const [questionModal, setQuestionModal] = useState(false)
  const [questionScaleId, setQuestionScaleId] = useState<number | null>(null)
  const [editingQuestion, setEditingQuestion] = useState<ScaleQuestion | null>(null)
  const [questionForm] = Form.useForm()

  const fetchScales = useCallback(() => {
    setLoading(true)
    scalesApi.list((page - 1) * 20, 20).then((data) => {
      setScales(data.scales)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }, [page])

  useEffect(() => { fetchScales() }, [fetchScales])

  const openScaleModal = (scale?: AssessmentScale) => {
    setEditingScale(scale || null)
    scaleForm.setFieldsValue(scale || { scale_name: '', scale_description: '' })
    setScaleModal(true)
  }

  const handleScaleSave = async () => {
    const values = await scaleForm.validateFields()
    if (editingScale) {
      await scalesApi.update(editingScale.scale_id, values)
      message.success('Escala atualizada')
    } else {
      await scalesApi.create(values as ScaleCreateRequest)
      message.success('Escala criada')
    }
    setScaleModal(false)
    fetchScales()
  }

  const handleScaleDelete = async (scaleId: number) => {
    await scalesApi.delete(scaleId)
    message.success('Escala excluida')
    fetchScales()
  }

  const openQuestionModal = (scaleId: number, question?: ScaleQuestion) => {
    setQuestionScaleId(scaleId)
    setEditingQuestion(question || null)
    questionForm.setFieldsValue(question || { question_text: '', question_order: 1 })
    setQuestionModal(true)
  }

  const handleQuestionSave = async () => {
    if (questionScaleId == null) return
    const values = await questionForm.validateFields()
    if (editingQuestion) {
      await scalesApi.updateQuestion(editingQuestion.question_id, values)
      message.success('Pergunta atualizada')
    } else {
      await scalesApi.createQuestion(questionScaleId, values as ScaleQuestionCreateRequest)
      message.success('Pergunta adicionada')
    }
    setQuestionModal(false)
    fetchScales()
  }

  const handleQuestionDelete = async (questionId: number) => {
    await scalesApi.deleteQuestion(questionId)
    message.success('Pergunta excluida')
    fetchScales()
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Admin' }, { title: 'Escalas' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Gerenciar Escalas de Avaliacao</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => openScaleModal()}>
            Nova Escala
          </Button>
        </div>
        <Table
          dataSource={scales}
          rowKey="scale_id"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
          expandable={{
            expandedRowRender: (record) => (
              <div style={{ paddingLeft: 48 }}>
                <div style={{ marginBottom: 8 }}>
                  <Button size="small" icon={<PlusOutlined />} onClick={() => openQuestionModal(record.scale_id)}>
                    Adicionar Pergunta
                  </Button>
                </div>
                <Table
                  dataSource={record.questions || []}
                  rowKey="question_id"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: '#', dataIndex: 'question_order', width: 50 },
                    { title: 'Pergunta', dataIndex: 'question_text', ellipsis: true },
                    {
                      title: 'Acoes',
                      width: 140,
                      render: (_: unknown, q: ScaleQuestion) => (
                        <Space>
                          <Button size="small" icon={<EditOutlined />} onClick={() => openQuestionModal(record.scale_id, q)} />
                          <Popconfirm title="Excluir pergunta?" onConfirm={() => handleQuestionDelete(q.question_id)}>
                            <Button size="small" danger icon={<DeleteOutlined />} />
                          </Popconfirm>
                        </Space>
                      ),
                    },
                  ]}
                  locale={{ emptyText: 'Nenhuma pergunta' }}
                />
              </div>
            ),
          }}
          columns={[
            { title: 'ID', dataIndex: 'scale_id', width: 60 },
            {
              title: 'Nome',
              dataIndex: 'scale_name',
              render: (v: string, r) => {
                const qty = r.questions?.length || 0
                return (
                  <Space>
                    <Text strong>{v}</Text>
                    <Tag icon={<OrderedListOutlined />} color="blue">{qty} perguntas</Tag>
                  </Space>
                )
              },
            },
            { title: 'Descricao', dataIndex: 'scale_description', ellipsis: true },
            {
              title: 'Acoes',
              width: 140,
              render: (_: unknown, record: AssessmentScale) => (
                <Space>
                  <Tooltip title="Editar escala">
                    <Button size="small" icon={<EditOutlined />} onClick={() => openScaleModal(record)} />
                  </Tooltip>
                  <Popconfirm title="Excluir escala e todas as perguntas?" onConfirm={() => handleScaleDelete(record.scale_id)}>
                    <Tooltip title="Excluir escala">
                      <Button size="small" danger icon={<DeleteOutlined />} />
                    </Tooltip>
                  </Popconfirm>
                </Space>
              ),
            },
          ]}
        />
      </Card>

      <Modal
        title={editingScale ? 'Editar Escala' : 'Nova Escala'}
        open={scaleModal}
        onOk={handleScaleSave}
        onCancel={() => setScaleModal(false)}
      >
        <Form form={scaleForm} layout="vertical">
          <Form.Item name="scale_name" label="Nome" rules={[{ required: true, message: 'Informe o nome da escala' }]}>
            <Input placeholder="Ex: PHQ-9" />
          </Form.Item>
          <Form.Item name="scale_description" label="Descricao">
            <Input.TextArea rows={3} placeholder="Descricao da escala" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={editingQuestion ? 'Editar Pergunta' : 'Adicionar Pergunta'}
        open={questionModal}
        onOk={handleQuestionSave}
        onCancel={() => setQuestionModal(false)}
      >
        <Form form={questionForm} layout="vertical">
          <Form.Item name="question_text" label="Texto da Pergunta" rules={[{ required: true, message: 'Informe o texto' }]}>
            <Input.TextArea rows={2} placeholder="Ex: Nos ultimos 2 semanas, com que frequencia..." />
          </Form.Item>
          <Form.Item name="question_order" label="Ordem" rules={[{ required: true, message: 'Informe a ordem' }]}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
