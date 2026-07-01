import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card, Button, Space, Typography, Breadcrumb, Spin, List, Tag,
  Modal, Input, Select, Popconfirm, Empty, message,
} from 'antd'
import {
  PlusOutlined, PushpinOutlined, PushpinFilled,
  EditOutlined, DeleteOutlined, PrinterOutlined,
} from '@ant-design/icons'
import { reportsApi } from '../../api/endpoints'
import type { MedicalReport } from '../../types'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

export default function PatientReportsPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const navigate = useNavigate()
  const [reports, setReports] = useState<MedicalReport[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<MedicalReport | null>(null)
  const [formTitle, setFormTitle] = useState('')
  const [formContent, setFormContent] = useState('')
  const [formType, setFormType] = useState('summary')
  const [saving, setSaving] = useState(false)

  const load = () => {
    if (!uuid) return
    setLoading(true)
    reportsApi.list(uuid).then(setReports).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [uuid])

  const openCreate = () => {
    setEditing(null)
    setFormTitle('')
    setFormContent('')
    setFormType('summary')
    setModalOpen(true)
  }

  const openEdit = (r: MedicalReport) => {
    setEditing(r)
    setFormTitle(r.title)
    setFormContent(r.content)
    setFormType(r.report_type)
    setModalOpen(true)
  }

  const handleSave = async () => {
    if (!uuid || !formTitle.trim() || !formContent.trim()) return
    setSaving(true)
    try {
      if (editing) {
        await reportsApi.update(editing.report_uuid, {
          title: formTitle, content: formContent, report_type: formType,
        })
        message.success('Relatório atualizado')
      } else {
        await reportsApi.create(uuid, {
          title: formTitle, content: formContent, report_type: formType,
        })
        message.success('Relatório criado')
      }
      setModalOpen(false)
      load()
    } catch { message.error('Erro ao salvar relatório') }
    finally { setSaving(false) }
  }

  const handleDelete = async (reportUuid: string) => {
    try {
      await reportsApi.delete(reportUuid)
      message.success('Relatório excluído')
      load()
    } catch { message.error('Erro ao excluir') }
  }

  const handleTogglePin = async (reportUuid: string) => {
    try {
      await reportsApi.togglePin(reportUuid)
      load()
    } catch { message.error('Erro ao fixar/desfixar') }
  }

  const handlePrint = (r: MedicalReport) => {
    const w = window.open('', '_blank')
    if (!w) return
    w.document.write(`
      <html><head><title>${r.title}</title>
      <style>body{font-family:sans-serif;padding:40px;max-width:800px;margin:auto}
      h1{font-size:20px;color:#333} .meta{color:#666;font-size:13px;margin-bottom:20px}
      pre{white-space:pre-wrap;font-family:inherit;line-height:1.6}</style>
      </head><body>
      <h1>${r.title}</h1>
      <div class="meta">Tipo: ${r.report_type} | Criado por: ${r.created_by || '-'} | ${new Date(r.created_at).toLocaleDateString('pt-BR')}</div>
      <pre>${r.content}</pre>
      <script>window.print()</script>
      </body></html>
    `)
    w.document.close()
  }

  const reportTypeLabel: Record<string, string> = {
    summary: 'Resumo Clínico',
    discharge: 'Alta',
    referral: 'Encaminhamento',
    evaluation: 'Avaliação',
    other: 'Outro',
  }

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb items={[
        { title: <a onClick={() => navigate('/')}>Início</a> },
        { title: <a onClick={() => navigate('/patients')}>Pacientes</a> },
        { title: 'Relatórios Médicos' },
      ]} style={{ marginBottom: 16 }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Relatórios Médicos</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Novo Relatório</Button>
      </div>

      <Spin spinning={loading}>
        {reports.length === 0 ? (
          <Empty description="Nenhum relatório médico encontrado">
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Criar Primeiro Relatório</Button>
          </Empty>
        ) : (
          <List
            dataSource={reports}
            renderItem={(r) => (
              <Card
                size="small" style={{ marginBottom: 12 }}
                extra={
                  <Space>
                    <Button size="small" icon={r.is_pinned ? <PushpinFilled /> : <PushpinOutlined />}
                      onClick={() => handleTogglePin(r.report_uuid)} />
                    <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
                    <Button size="small" icon={<PrinterOutlined />} onClick={() => handlePrint(r)} />
                    <Popconfirm title="Excluir relatório?" onConfirm={() => handleDelete(r.report_uuid)}>
                      <Button size="small" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                  </Space>
                }
              >
                <Card.Meta
                  title={
                    <Space>
                      {r.is_pinned && <PushpinFilled style={{ color: '#1890ff' }} />}
                      {r.title}
                      <Tag>{reportTypeLabel[r.report_type] || r.report_type}</Tag>
                    </Space>
                  }
                  description={
                    <>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {r.created_by ? `Por ${r.created_by} · ` : ''}
                        {new Date(r.created_at).toLocaleDateString('pt-BR')}
                      </Text>
                      <Paragraph ellipsis={{ rows: 2 }} style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>
                        {r.content}
                      </Paragraph>
                    </>
                  }
                />
              </Card>
            )}
          />
        )}
      </Spin>

      <Modal
        title={editing ? 'Editar Relatório' : 'Novo Relatório'}
        open={modalOpen} onCancel={() => setModalOpen(false)}
        onOk={handleSave} confirmLoading={saving}
        okText="Salvar" width={700}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Select value={formType} onChange={setFormType} style={{ width: 200 }}
            options={[
              { value: 'summary', label: 'Resumo Clínico' },
              { value: 'discharge', label: 'Alta' },
              { value: 'referral', label: 'Encaminhamento' },
              { value: 'evaluation', label: 'Avaliação' },
              { value: 'other', label: 'Outro' },
            ]}
          />
          <Input placeholder="Título do relatório" value={formTitle}
            onChange={e => setFormTitle(e.target.value)} />
          <TextArea rows={12} placeholder="Conteúdo do relatório (formato livre)"
            value={formContent} onChange={e => setFormContent(e.target.value)} />
        </Space>
      </Modal>
    </div>
  )
}
