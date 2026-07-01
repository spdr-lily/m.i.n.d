import { useEffect, useState } from 'react'
import { Card, Table, Tag, Button, Typography, Breadcrumb, Space, Modal, Form, Input, Select, message, Tabs } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import { adminApi } from '../../api/endpoints'
import type { RolePermission, RoutePermission } from '../../types'

const { Title } = Typography

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<RolePermission[]>([])
  const [routes, setRoutes] = useState<RoutePermission[]>([])
  const [loading, setLoading] = useState(true)
  const [showPermModal, setShowPermModal] = useState(false)
  const [showRouteModal, setShowRouteModal] = useState(false)
  const [permForm] = Form.useForm()
  const [routeForm] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    const [p, r] = await Promise.all([adminApi.listPermissions(), adminApi.listRoutePermissions()])
    setPermissions(p.permissions)
    setRoutes(r.routes)
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [])

  const handleAddPermission = async () => {
    const values = await permForm.validateFields()
    await adminApi.addPermission(values)
    message.success('Permissão adicionada')
    setShowPermModal(false)
    permForm.resetFields()
    fetchData()
  }

  const handleRemovePermission = async (id: number) => {
    await adminApi.removePermission(id)
    message.success('Permissão removida')
    fetchData()
  }

  const handleAddRoute = async () => {
    const values = await routeForm.validateFields()
    await adminApi.addRoutePermission(values)
    message.success('Permissão de rota adicionada')
    setShowRouteModal(false)
    routeForm.resetFields()
    fetchData()
  }

  const handleDeleteRoute = async (id: number) => {
    await adminApi.deleteRoutePermission(id)
    message.success('Permissão de rota removida')
    fetchData()
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Admin' }, { title: 'Permissões' }]} style={{ marginBottom: 16 }} />
      <Card loading={loading}>
        <Title level={4}>Gerenciar Permissões</Title>
        <Tabs items={[
          {
            key: 'roles',
            label: 'Permissões por Perfil',
            children: (
              <>
                <Button icon={<PlusOutlined />} onClick={() => setShowPermModal(true)} style={{ marginBottom: 16 }}>
                  Nova Permissão
                </Button>
                <Table
                  dataSource={permissions}
                  rowKey="id"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: 'Perfil', dataIndex: 'role', width: 140 },
                    { title: 'Permissão', dataIndex: 'permission' },
                    {
                      title: 'Ações',
                      width: 80,
                      render: (_: unknown, record: RolePermission) => (
                        <Button danger size="small" icon={<DeleteOutlined />} onClick={() => handleRemovePermission(record.id!)} />
                      ),
                    },
                  ]}
                />
              </>
            ),
          },
          {
            key: 'routes',
            label: 'Permissões de Rota',
            children: (
              <>
                <Button icon={<PlusOutlined />} onClick={() => setShowRouteModal(true)} style={{ marginBottom: 16 }}>
                  Nova Permissão de Rota
                </Button>
                <Table
                  dataSource={routes}
                  rowKey="id"
                  size="small"
                  pagination={false}
                  columns={[
                    { title: 'Método', dataIndex: 'http_method', width: 100, render: (v: string) => <Tag>{v}</Tag> },
                    { title: 'Path', dataIndex: 'path_pattern', width: 280 },
                    { title: 'Permissão', dataIndex: 'permission_required' },
                    { title: 'Descrição', dataIndex: 'description', ellipsis: true },
                    {
                      title: 'Ativo',
                      dataIndex: 'is_active',
                      width: 80,
                      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? 'Sim' : 'Não'}</Tag>,
                    },
                    {
                      title: 'Ações',
                      width: 80,
                      render: (_: unknown, record: RoutePermission) => (
                        <Button danger size="small" icon={<DeleteOutlined />} onClick={() => handleDeleteRoute(record.id!)} />
                      ),
                    },
                  ]}
                />
              </>
            ),
          },
        ]} />
      </Card>

      <Modal title="Nova Permissão" open={showPermModal} onOk={handleAddPermission} onCancel={() => setShowPermModal(false)}>
        <Form form={permForm} layout="vertical">
          <Form.Item name="role" label="Perfil" rules={[{ required: true }]}>
            <Select options={[
              { value: 'admin', label: 'Administrador' },
              { value: 'clinician', label: 'Clínico' },
              { value: 'viewer', label: 'Visualizador' },
            ]} />
          </Form.Item>
          <Form.Item name="permission" label="Permissão" rules={[{ required: true }]}>
            <Input placeholder="Ex: read:sensitive" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="Nova Permissão de Rota" open={showRouteModal} onOk={handleAddRoute} onCancel={() => setShowRouteModal(false)}>
        <Form form={routeForm} layout="vertical">
          <Form.Item name="http_method" label="Método HTTP" rules={[{ required: true }]}>
            <Select options={['GET', 'POST', 'PATCH', 'PUT', 'DELETE'].map((m) => ({ value: m, label: m }))} />
          </Form.Item>
          <Form.Item name="path_pattern" label="Pattern da Rota" rules={[{ required: true }]}>
            <Input placeholder="Ex: /api/sensitive/%" />
          </Form.Item>
          <Form.Item name="permission_required" label="Permissão Necessária" rules={[{ required: true }]}>
            <Input placeholder="Ex: read:sensitive" />
          </Form.Item>
          <Form.Item name="description" label="Descrição">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
