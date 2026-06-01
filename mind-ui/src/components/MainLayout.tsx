import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown, Typography, theme } from 'antd'
import {
  DashboardOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  AlertOutlined,
  SettingOutlined,
  AuditOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  TeamOutlined,
  MedicineBoxOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { ROLE_LABELS } from '../utils/constants'

const { Header, Sider, Content } = AntLayout
const { Text } = Typography

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard', roles: ['admin', 'clinician', 'viewer'] },
  { key: '/patients', icon: <UserOutlined />, label: 'Pacientes', roles: ['admin', 'clinician', 'viewer'] },
  { key: '/consultations', icon: <CalendarOutlined />, label: 'Consultas', roles: ['admin', 'clinician', 'viewer'] },
  { key: '/assessments', icon: <FileTextOutlined />, label: 'Escalas', roles: ['admin', 'clinician'] },
  { key: '/inferences', icon: <ExperimentOutlined />, label: 'Inferência', roles: ['admin', 'clinician'] },
  { key: '/alerts', icon: <AlertOutlined />, label: 'Alertas', roles: ['admin', 'clinician', 'viewer'] },
  { key: '/admin/users', icon: <TeamOutlined />, label: 'Admin', roles: ['admin'] },
  { key: '/admin/permissions', icon: <SettingOutlined />, label: 'Permissões', roles: ['admin'] },
  { key: '/admin/monitoring', icon: <MedicineBoxOutlined />, label: 'Monitoramento', roles: ['admin'] },
  { key: '/audit', icon: <AuditOutlined />, label: 'Auditoria', roles: ['admin'] },
]

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { token: themeToken } = theme.useToken()

  const visibleItems = menuItems.filter((item) => item.roles.includes(user?.role || ''))

  const selectedKey = '/' + location.pathname.split('/').slice(1, 2).join('/')

  const userMenu = {
    items: [
      { key: 'profile', label: `${user?.full_name} (${ROLE_LABELS[user?.role || '']})`, disabled: true },
      { type: 'divider' as const },
      { key: 'logout', icon: <LogoutOutlined />, label: 'Sair', danger: true },
    ],
    onClick: ({ key }: { key: string }) => {
      if (key === 'logout') {
        logout()
        navigate('/login')
      }
    },
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <Text strong style={{ fontSize: collapsed ? 14 : 18, color: themeToken.colorPrimary }}>
            {collapsed ? 'M' : 'M.I.N.D CDSS'}
          </Text>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={visibleItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <AntLayout>
        <Header
          style={{
            padding: '0 24px',
            background: themeToken.colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown menu={userMenu} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: themeToken.colorPrimary }} />
              <Text>{user?.full_name}</Text>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}
