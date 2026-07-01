import { useEffect, useState } from 'react'
import { Card, Table, Tag, Button, Typography, Breadcrumb, Space, Modal, Form, Input, Select, message } from 'antd'
import { PlusOutlined, EditOutlined, KeyOutlined } from '@ant-design/icons'
import { adminApi } from '../../api/endpoints'
import type { User } from '../../types'
import { ROLE_LABELS } from '../../utils/constants'

const { Title } = Typography

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [editModal, setEditModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [passwordModal, setPasswordModal] = useState(false)
  const [passwordUser, setPasswordUser] = useState<User | null>(null)
  const [createModal, setCreateModal] = useState(false)
  const [form] = Form.useForm()
  const [pwForm] = Form.useForm()
  const [createForm] = Form.useForm()

  const fetchUsers = (p = page) => {
    setLoading(true)
    adminApi.listUsers(p, 20).then((data) => {
      setUsers(data.users)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetchUsers(1) }, [])

  const handleEdit = (user: User) => {
    setEditingUser(user)
    form.setFieldsValue({ username: user.username, role: user.role, is_active: user.is_active })
    setEditModal(true)
  }

  const handlePassword = (user: User) => {
    setPasswordUser(user)
    pwForm.resetFields()
    setPasswordModal(true)
  }

  const handleCreate = async () => {
    const values = await createForm.validateFields()
    await adminApi.createUser(values)
    message.success('Usuário criado com sucesso')
    setCreateModal(false)
    createForm.resetFields()
    fetchUsers(1)
  }

  const handlePasswordSave = async () => {
    if (!passwordUser) return
    const values = await pwForm.validateFields()
    await adminApi.changePassword(passwordUser.user_uuid, values.new_password)
    message.success('Senha alterada com sucesso')
    setPasswordModal(false)
  }

  const handleSave = async () => {
    if (!editingUser) return
    const values = await form.validateFields()
    await adminApi.updateUser(editingUser.user_uuid, values)
    message.success('Usuário atualizado')
    setEditModal(false)
    fetchUsers(page)
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Admin' }, { title: 'Usuários' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Gerenciar Usuários</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { setCreateModal(true); createForm.resetFields() }}>
            Adicionar Usuário
          </Button>
        </div>
        <Table
          dataSource={users}
          rowKey="user_uuid"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: (p) => { setPage(p); fetchUsers(p) } }}
          columns={[
            { title: 'Usuário', dataIndex: 'username' },
            { title: 'Nome', dataIndex: 'full_name', ellipsis: true },
            {
              title: 'Perfil',
              dataIndex: 'role',
              width: 140,
              render: (v: string) => {
                const colors: Record<string, string> = { admin: 'red', clinician: 'blue', psychologist: 'cyan', psychiatrist: 'purple', clinical_supervisor: 'orange', researcher: 'green', viewer: 'default' }
                return <Tag color={colors[v] || 'default'}>{ROLE_LABELS[v] || v}</Tag>
              },
            },
            {
              title: 'Ativo',
              dataIndex: 'is_active',
              width: 80,
              render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sim' : 'Não'}</Tag>,
            },
            { title: 'Criado em', dataIndex: 'created_at', width: 160 },
            {
              title: 'Ações',
              width: 160,
              render: (_: unknown, record: User) => (
                <Space size="small">
                  <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>Editar</Button>
                  <Button size="small" icon={<KeyOutlined />} onClick={() => handlePassword(record)}>Senha</Button>
                </Space>
              ),
            },
          ]}
        />
      </Card>

      <Modal title="Alterar Senha" open={passwordModal} onOk={handlePasswordSave} onCancel={() => setPasswordModal(false)}>
        <Form form={pwForm} layout="vertical">
          <Form.Item name="new_password" label="Nova Senha" rules={[
            { required: true, message: 'Informe a nova senha' },
            { min: 6, message: 'Mínimo 6 caracteres' },
          ]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="confirm" label="Confirmar Senha" dependencies={['new_password']} rules={[
            { required: true, message: 'Confirme a senha' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('new_password') === value) return Promise.resolve()
                return Promise.reject(new Error('Senhas não conferem'))
              },
            }),
          ]}>
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="Editar Usuário" open={editModal} onOk={handleSave} onCancel={() => setEditModal(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="Nome de Usuário" rules={[
            { min: 3, message: 'Mínimo 3 caracteres' },
          ]}>
            <Input />
          </Form.Item>
          <Form.Item name="role" label="Perfil" rules={[{ required: true }]}>
            <Select options={[
              { value: 'admin', label: 'Administrador' },
              { value: 'clinician', label: 'Clínico' },
              { value: 'psychologist', label: 'Psicólogo' },
              { value: 'psychiatrist', label: 'Psiquiatra' },
              { value: 'clinical_supervisor', label: 'Supervisor Clínico' },
              { value: 'researcher', label: 'Pesquisador' },
              { value: 'viewer', label: 'Visualizador' },
            ]} />
          </Form.Item>
          <Form.Item name="is_active" label="Ativo">
            <Select options={[{ value: true, label: 'Sim' }, { value: false, label: 'Não' }]} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="Adicionar Usuário" open={createModal} onOk={handleCreate} onCancel={() => setCreateModal(false)}>
        <Form form={createForm} layout="vertical">
          <Form.Item name="username" label="Usuário" rules={[
            { required: true, message: 'Obrigatório' },
            { min: 3, message: 'Mínimo 3 caracteres' },
          ]}>
            <Input />
          </Form.Item>
          <Form.Item name="full_name" label="Nome Completo">
            <Input />
          </Form.Item>
          <Form.Item name="password" label="Senha" rules={[
            { required: true, message: 'Obrigatório' },
            { min: 6, message: 'Mínimo 6 caracteres' },
          ]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="role" label="Perfil" rules={[{ required: true, message: 'Obrigatório' }]}>
            <Select options={[
              { value: 'admin', label: 'Administrador' },
              { value: 'clinician', label: 'Clínico' },
              { value: 'psychologist', label: 'Psicólogo' },
              { value: 'psychiatrist', label: 'Psiquiatra' },
              { value: 'clinical_supervisor', label: 'Supervisor Clínico' },
              { value: 'researcher', label: 'Pesquisador' },
              { value: 'viewer', label: 'Visualizador' },
            ]} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
