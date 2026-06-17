import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown, Typography, theme, FloatButton } from 'antd'
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
  OrderedListOutlined,
  UnorderedListOutlined,
  MessageOutlined,
  ToolOutlined,
  SafetyOutlined,
  ProfileOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'
import { ROLE_LABELS } from '../utils/constants'
import MindLogo from './MindLogo'

const { Header, Sider, Content } = AntLayout
const { Text } = Typography

const SUBMENU_MAP: Record<string, string> = { clinico: '/patients', admin: '/admin', ferramentas: '/mia' }

const menuStructure = (role: string) => [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  {
    key: 'clinico', icon: <UserOutlined />, label: 'Clínico',
    children: [
      { key: '/patients', icon: <UserOutlined />, label: 'Pacientes' },
      { key: '/consultations', icon: <CalendarOutlined />, label: 'Consultas' },
      { key: '/assessments', icon: <FileTextOutlined />, label: 'Escalas' },
      { key: '/personality', icon: <ProfileOutlined />, label: 'Personalidade' },
      { key: '/inferences', icon: <ExperimentOutlined />, label: 'Inferência' },
      { key: '/professionals', icon: <TeamOutlined />, label: 'Profissionais' },
      { key: '/alerts', icon: <AlertOutlined />, label: 'Alertas' },
    ].filter(i => (['admin', 'clinician'].includes(role) ? true : ['/patients', '/consultations', '/professionals', '/personality'].includes(i.key))),
  },
  {
    key: 'admin', icon: <SafetyOutlined />, label: 'Administração',
    children: [
      { key: '/admin/users', icon: <TeamOutlined />, label: 'Usuários' },
      { key: '/admin/disorders', icon: <OrderedListOutlined />, label: 'Transtornos' },
      { key: '/admin/scales', icon: <ProfileOutlined />, label: 'Gerenciar Escalas' },
      { key: '/admin/symptoms', icon: <UnorderedListOutlined />, label: 'Sintomas' },
      { key: '/admin/medications', icon: <MedicineBoxOutlined />, label: 'Medicamentos' },
      { key: '/treatment/efficacy', icon: <MedicineBoxOutlined />, label: 'Eficácia de Medicamentos' },
      { key: '/admin/permissions', icon: <SettingOutlined />, label: 'Permissões' },
      { key: '/admin/monitoring', icon: <DashboardOutlined />, label: 'Monitoramento' },
    ].filter(i => role === 'admin' || ['/admin/disorders', '/admin/scales', '/admin/symptoms', '/admin/medications'].includes(i.key)),
  },
  {
    key: 'ferramentas', icon: <ToolOutlined />, label: 'Ferramentas',
    children: [
      { key: '/mia', icon: <MessageOutlined />, label: 'MIA' },
      { key: '/audit', icon: <AuditOutlined />, label: 'Auditoria' },
      { key: '/analytics', icon: <DashboardOutlined />, label: 'Analytics' },
    ].filter(i => role === 'admin' || i.key === '/mia'),
  },
]

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [openKeys, setOpenKeys] = useState<string[]>([])
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { token: themeToken } = theme.useToken()

  const visibleItems = menuStructure(user?.role || '')

  const selectedKey = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '')

  // Auto-open parent submenu based on current route
  useEffect(() => {
    const path = location.pathname
    if (path === '/' || path === '') { setOpenKeys([]); return }
    for (const [subKey, prefix] of Object.entries(SUBMENU_MAP)) {
      if (path.startsWith(prefix)) {
        setOpenKeys((prev) => prev.includes(subKey) ? prev : [...prev, subKey])
        return
      }
    }
    // Check clinico routes individually (diagnostic, personality, etc.)
    const clinicoRoutes = ['/patients', '/consultations', '/assessments', '/personality', '/inferences', '/professionals', '/alerts', '/analytics']
    if (clinicoRoutes.some((r) => path.startsWith(r))) {
      setOpenKeys((prev) => prev.includes('clinico') ? prev : [...prev, 'clinico'])
      return
    }
    setOpenKeys([])
  }, [location.pathname])

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
          <div style={{ cursor: 'pointer' }} onClick={() => navigate('/')}>
            <MindLogo size={collapsed ? 40 : 180} collapsed={collapsed} />
          </div>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          openKeys={collapsed ? [] : openKeys}
          onOpenChange={setOpenKeys}
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
      {location.pathname !== '/mia' && (
        <FloatButton
          icon={<MessageOutlined />}
          type="primary"
          tooltip="MIA - Assistente Diagnóstico"
          onClick={() => navigate('/mia')}
          style={{ right: 24, bottom: 24 }}
        />
      )}
    </AntLayout>
  )
}
