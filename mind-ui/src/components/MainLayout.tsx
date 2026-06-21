import { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown, Typography, theme, FloatButton, Drawer, Grid } from 'antd'
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
  MenuOutlined,
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
const { useBreakpoint } = Grid

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
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)
  const [openKeys, setOpenKeys] = useState<string[]>([])
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { token: themeToken } = theme.useToken()
  const screens = useBreakpoint()
  const isMobile = !screens.md

  const visibleItems = menuStructure(user?.role || '')

  const selectedKey = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '')

  useEffect(() => {
    const path = location.pathname
    if (path === '/' || path === '') { setOpenKeys([]); return }
    for (const [subKey, prefix] of Object.entries(SUBMENU_MAP)) {
      if (path.startsWith(prefix)) {
        setOpenKeys((prev) => prev.includes(subKey) ? prev : [...prev, subKey])
        return
      }
    }
    const clinicoRoutes = ['/patients', '/consultations', '/assessments', '/personality', '/inferences', '/professionals', '/alerts', '/analytics']
    if (clinicoRoutes.some((r) => path.startsWith(r))) {
      setOpenKeys((prev) => prev.includes('clinico') ? prev : [...prev, 'clinico'])
      return
    }
    setOpenKeys([])
  }, [location.pathname])

  useEffect(() => {
    setMobileDrawerOpen(false)
  }, [location.pathname])

  useEffect(() => {
    if (!isMobile) setMobileDrawerOpen(false)
  }, [isMobile])

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

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
    if (isMobile) setMobileDrawerOpen(false)
  }

  const menuComponent = (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      openKeys={isMobile ? openKeys : collapsed ? [] : openKeys}
      onOpenChange={setOpenKeys}
      items={visibleItems}
      onClick={handleMenuClick}
      style={{ borderRight: 0 }}
    />
  )

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {!isMobile && (
        <Sider trigger={null} collapsible collapsed={collapsed} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
          <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid #f0f0f0' }}>
            <div style={{ cursor: 'pointer' }} onClick={() => navigate('/')}>
              <MindLogo size={collapsed ? 40 : 180} collapsed={collapsed} />
            </div>
          </div>
          {menuComponent}
        </Sider>
      )}

      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }} onClick={() => { navigate('/'); setMobileDrawerOpen(false) }}>
            <MindLogo size={120} />
          </div>
        }
        placement="left"
        onClose={() => setMobileDrawerOpen(false)}
        open={isMobile && mobileDrawerOpen}
        width={280}
        styles={{ body: { padding: 0 } }}
      >
        {menuComponent}
      </Drawer>

      <AntLayout>
        <Header
          style={{
            padding: isMobile ? '0 12px' : '0 24px',
            background: themeToken.colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
            height: isMobile ? 56 : 64,
            lineHeight: isMobile ? '56px' : '64px',
          }}
        >
          {isMobile ? (
            <Button type="text" icon={<MenuOutlined />} onClick={() => setMobileDrawerOpen(true)} />
          ) : (
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
            />
          )}
          {isMobile && (
            <Text strong style={{ fontSize: 16, flex: 1, textAlign: 'center' }}>M.I.N.D</Text>
          )}
          <Dropdown menu={userMenu} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: themeToken.colorPrimary }} size={isMobile ? 'small' : 'default'} />
              {!isMobile && <Text>{user?.full_name}</Text>}
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: isMobile ? 12 : 24 }}>
          <Outlet />
        </Content>
      </AntLayout>
      {location.pathname !== '/mia' && (
        <FloatButton
          icon={<MessageOutlined />}
          type="primary"
          tooltip={isMobile ? undefined : "MIA - Assistente Diagnóstico"}
          onClick={() => navigate('/mia')}
          style={{ right: isMobile ? 16 : 24, bottom: isMobile ? 16 : 24 }}
        />
      )}
    </AntLayout>
  )
}
