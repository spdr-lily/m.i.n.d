import { useEffect, useState } from 'react'
import { Card, Table, Tag, Button, Typography, Breadcrumb, Space, Modal, Form, Input, Select, message } from 'antd'
import { PlusOutlined, EditOutlined } from '@ant-design/icons'
import { adminApi } from '../../api/admin'
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
  const [form] = Form.useForm()

  const fetchUsers = () => {
    setLoading(true)
    adminApi.listUsers(page, 20).then((data) => {
      setUsers(data.users)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetchUsers() }, [page])

  const handleEdit = (user: User) => {
    setEditingUser(user)
    form.setFieldsValue({ role: user.role, is_active: user.is_active })
    setEditModal(true)
  }

  const handleSave = async () => {
    if (!editingUser) return
    const values = await form.validateFields()
    await adminApi.updateUser(editingUser.user_uuid, values)
    message.success('Usuário atualizado')
    setEditModal(false)
    fetchUsers()
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Admin' }, { title: 'Usuários' }]} style={{ marginBottom: 16 }} />
      <Card>
        <Title level={4}>Gerenciar Usuários</Title>
        <Table
          dataSource={users}
          rowKey="user_uuid"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
          columns={[
            { title: 'Usuário', dataIndex: 'username' },
            { title: 'Nome', dataIndex: 'full_name', ellipsis: true },
            {
              title: 'Perfil',
              dataIndex: 'role',
              width: 140,
              render: (v: string) => <Tag color={v === 'admin' ? 'red' : v === 'clinician' ? 'blue' : 'default'}>{ROLE_LABELS[v] || v}</Tag>,
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
              width: 100,
              render: (_: unknown, record: User) => (
                <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>Editar</Button>
              ),
            },
          ]}
        />
      </Card>

      <Modal title="Editar Usuário" open={editModal} onOk={handleSave} onCancel={() => setEditModal(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="role" label="Perfil" rules={[{ required: true }]}>
            <Select options={[
              { value: 'admin', label: 'Administrador' },
              { value: 'clinician', label: 'Clínico' },
              { value: 'viewer', label: 'Visualizador' },
            ]} />
          </Form.Item>
          <Form.Item name="is_active" label="Ativo" valuePropName="checked">
            <Select options={[{ value: true, label: 'Sim' }, { value: false, label: 'Não' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
