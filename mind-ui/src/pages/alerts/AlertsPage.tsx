import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card, Table, Tag, Button, Typography, Breadcrumb, Space, Modal, Input,
  Row, Col, Tooltip, Drawer, Descriptions, Select, Badge, Divider, Empty, Progress, Statistic,
} from 'antd'
import {
  CheckCircleOutlined, BellOutlined, WarningOutlined, InfoCircleOutlined,
  FileTextOutlined, UserOutlined, MedicineBoxOutlined, EyeOutlined,
  FilterOutlined, ReloadOutlined, ClockCircleOutlined,
} from '@ant-design/icons'
import { alertsApi } from '../../api/endpoints'
import type { Alert } from '../../types'
import { SEVERITY_COLORS, SEVERITY_LABELS, ALERT_TYPE_LABELS } from '../../utils/constants'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/pt-br'

dayjs.extend(relativeTime)
dayjs.locale('pt-br')

const { Title, Text } = Typography
const { TextArea } = Input

const SEVERITY_ORDER: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }

const SEVERITY_ICONS: Record<string, React.ReactNode> = {
  critical: <WarningOutlined style={{ color: '#cf1322' }} />,
  high: <WarningOutlined style={{ color: '#f5222d' }} />,
  medium: <InfoCircleOutlined style={{ color: '#fa8c16' }} />,
  low: <InfoCircleOutlined style={{ color: '#faad14' }} />,
}

const SEVERITY_BG: Record<string, string> = {
  critical: '#fff1f0',
  high: '#fff2e8',
  medium: '#fff7e6',
  low: '#fffbe6',
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  scale_threshold: <MedicineBoxOutlined />,
  ideacao_suicida: <WarningOutlined />,
  missed_follow_up: <ClockCircleOutlined />,
  diagnostico_alta_confianca: <InfoCircleOutlined />,
}

export default function AlertsPage() {
  const navigate = useNavigate()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [showResolved, setShowResolved] = useState(false)
  const [resolveModalOpen, setResolveModalOpen] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [resolveNotes, setResolveNotes] = useState('')
  const [resolving, setResolving] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [detailAlert, setDetailAlert] = useState<Alert | null>(null)
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<string | null>(null)

  const fetchAlerts = () => {
    setLoading(true)
    alertsApi.list({ resolved: showResolved }).then(setAlerts).finally(() => setLoading(false))
  }

  useEffect(() => { fetchAlerts() }, [showResolved])

  const filteredAlerts = useMemo(() => {
    let result = [...alerts]
    if (filterSeverity) result = result.filter(a => a.severity === filterSeverity)
    if (filterType) result = result.filter(a => a.alert_type === filterType)
    return result
  }, [alerts, filterSeverity, filterType])

  const counts = useMemo(() => {
    const active = alerts.filter(a => !a.resolved)
    return {
      total: active.length,
      critical: active.filter(a => a.severity === 'critical').length,
      high: active.filter(a => a.severity === 'high').length,
      medium: active.filter(a => a.severity === 'medium').length,
      low: active.filter(a => a.severity === 'low').length,
      byType: active.reduce((acc, a) => { acc[a.alert_type] = (acc[a.alert_type] || 0) + 1; return acc }, {} as Record<string, number>),
    }
  }, [alerts])

  const uniqueTypes = useMemo(() => [...new Set(alerts.map(a => a.alert_type))], [alerts])

  const openResolveModal = (alert: Alert) => {
    setSelectedAlert(alert)
    setResolveNotes('')
    setResolveModalOpen(true)
  }

  const handleResolve = async () => {
    if (!selectedAlert) return
    setResolving(true)
    try {
      await alertsApi.resolve(selectedAlert.alert_id, resolveNotes || undefined)
      setResolveModalOpen(false)
      setSelectedAlert(null)
      fetchAlerts()
    } finally {
      setResolving(false)
    }
  }

  const openDetail = (alert: Alert) => {
    setDetailAlert(alert)
    setDrawerOpen(true)
  }

  const severityTag = (v: string) => (
    <Tag color={SEVERITY_COLORS[v]} icon={SEVERITY_ICONS[v]} style={{ fontWeight: 600 }}>
      {SEVERITY_LABELS[v] || v}
    </Tag>
  )

  const timeAgo = (date: string) => {
    const d = dayjs(date)
    const now = dayjs()
    const diffDays = now.diff(d, 'day')
    if (diffDays > 30) return d.format('DD/MM/YY')
    if (diffDays > 0) return `há ${diffDays}d`
    const diffHours = now.diff(d, 'hour')
    if (diffHours > 0) return `há ${diffHours}h`
    return 'agora'
  }

  const columns = [
    {
      title: '',
      width: 4,
      render: (_: unknown, record: Alert) => (
        <div style={{
          width: 4, height: '100%', borderRadius: 2,
          background: SEVERITY_COLORS[record.severity] || '#d9d9d9',
        }} />
      ),
    },
    {
      title: 'Severidade',
      dataIndex: 'severity',
      width: 120,
      sorter: (a: Alert, b: Alert) => (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9),
      defaultSortOrder: 'ascend' as const,
      render: severityTag,
    },
    {
      title: 'Tipo',
      dataIndex: 'alert_type',
      width: 180,
      filters: uniqueTypes.map(t => ({ text: ALERT_TYPE_LABELS[t] || t, value: t })),
      onFilter: (value: unknown, record: Alert) => record.alert_type === value,
      render: (v: string) => (
        <Space size={6}>
          <span style={{ color: SEVERITY_COLORS[alerts.find(a => a.alert_type === v)?.severity || 'medium'] }}>
            {TYPE_ICONS[v] || <BellOutlined />}
          </span>
          <Text>{ALERT_TYPE_LABELS[v] || v}</Text>
        </Space>
      ),
    },
    {
      title: 'Paciente',
      dataIndex: 'patient_name',
      width: 200,
      render: (name: string | null, record: Alert) => name ? (
        <Space size={6}>
          <div style={{
            width: 28, height: 28, borderRadius: '50%', background: '#e6f4ff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12, fontWeight: 600, color: '#1677ff', flexShrink: 0,
          }}>
            {name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
          </div>
          <div>
            <Text strong style={{ fontSize: 13 }}>{name}</Text>
            {record.patient_uuid && (
              <div>
                <Button
                  type="link"
                  size="small"
                  style={{ padding: 0, fontSize: 11 }}
                  onClick={(e) => { e.stopPropagation(); navigate(`/patients/${record.patient_uuid}`) }}
                >
                  Ver prontuário
                </Button>
              </div>
            )}
          </div>
        </Space>
      ) : <Text type="secondary">—</Text>,
    },
    {
      title: 'Mensagem',
      dataIndex: 'message',
      ellipsis: true,
      render: (msg: string, record: Alert) => (
        <Tooltip title={msg}>
          <Text ellipsis style={{ cursor: 'pointer', maxWidth: 340, display: 'block' }}>{msg}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Quando',
      dataIndex: 'created_at',
      width: 130,
      sorter: (a: Alert, b: Alert) => dayjs(a.created_at).unix() - dayjs(b.created_at).unix(),
      render: (v: string) => (
        <Tooltip title={dayjs(v).format('DD/MM/YYYY HH:mm:ss')}>
          <Space direction="vertical" size={0}>
            <Text type="secondary" style={{ fontSize: 13 }}>{timeAgo(v)}</Text>
            <Text style={{ fontSize: 11, color: '#8c8c8c' }}>{dayjs(v).format('DD/MM HH:mm')}</Text>
          </Space>
        </Tooltip>
      ),
    },
    {
      title: 'Ações',
      width: 140,
      render: (_: unknown, record: Alert) => (
        <Space size={4}>
          <Tooltip title="Ver detalhes">
            <Button size="small" icon={<EyeOutlined />} onClick={() => openDetail(record)} />
          </Tooltip>
          {!record.resolved ? (
            <Button
              size="small"
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => openResolveModal(record)}
            >
              Resolver
            </Button>
          ) : (
            <Tag color="green" icon={<CheckCircleOutlined />}>Resolvido</Tag>
          )}
        </Space>
      ),
    },
  ]

  const stats = (
    <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
      <Col xs={12} sm={6}>
        <Card size="small" hoverable style={{ borderTop: '3px solid #f5222d' }}>
          <Statistic
            title={<Text type="secondary">Crítico</Text>}
            value={counts.critical}
            valueStyle={{ color: counts.critical > 0 ? '#cf1322' : undefined, fontSize: 28, fontWeight: 700 }}
            prefix={<WarningOutlined />}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card size="small" hoverable style={{ borderTop: '3px solid #fa8c16' }}>
          <Statistic
            title={<Text type="secondary">Alto</Text>}
            value={counts.high}
            valueStyle={{ color: counts.high > 0 ? '#f5222d' : undefined, fontSize: 28, fontWeight: 700 }}
            prefix={<WarningOutlined />}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card size="small" hoverable style={{ borderTop: '3px solid #faad14' }}>
          <Statistic
            title={<Text type="secondary">Médio</Text>}
            value={counts.medium}
            valueStyle={{ color: counts.medium > 0 ? '#fa8c16' : undefined, fontSize: 28, fontWeight: 700 }}
            prefix={<InfoCircleOutlined />}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card size="small" hoverable style={{ borderTop: '3px solid #fadb14' }}>
          <Statistic
            title={<Text type="secondary">Baixo</Text>}
            value={counts.low}
            valueStyle={{ fontSize: 28, fontWeight: 700 }}
            prefix={<InfoCircleOutlined />}
          />
        </Card>
      </Col>
    </Row>
  )

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Alertas' }]} style={{ marginBottom: 16 }} />

      {stats}

      <Card
        title={
          <Space align="center">
            <BellOutlined />
            <Text strong style={{ fontSize: 16 }}>Alertas Clínicos</Text>
            {!showResolved && counts.total > 0 && (
              <Badge count={counts.total} style={{ backgroundColor: counts.critical > 0 ? '#cf1322' : '#f5222d' }} />
            )}
          </Space>
        }
        extra={
          <Space wrap>
            <Select
              placeholder="Severidade"
              allowClear
              size="small"
              style={{ width: 130 }}
              value={filterSeverity}
              onChange={setFilterSeverity}
              options={[
                { label: 'Crítico', value: 'critical' },
                { label: 'Alto', value: 'high' },
                { label: 'Médio', value: 'medium' },
                { label: 'Baixo', value: 'low' },
              ]}
            />
            <Select
              placeholder="Tipo"
              allowClear
              size="small"
              style={{ width: 180 }}
              value={filterType}
              onChange={setFilterType}
              options={uniqueTypes.map(t => ({ label: ALERT_TYPE_LABELS[t] || t, value: t }))}
            />
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={fetchAlerts}
              loading={loading}
            >
              Atualizar
            </Button>
            <Button
              size="small"
              onClick={() => setShowResolved(!showResolved)}
              icon={showResolved ? <BellOutlined /> : <CheckCircleOutlined />}
            >
              {showResolved ? 'Ativos' : 'Resolvidos'}
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={filteredAlerts}
          rowKey="alert_id"
          loading={loading}
          pagination={{
            pageSize: 15,
            showSizeChanger: false,
            showTotal: (total, range) => `${range[0]}–${range[1]} de ${total} alertas`,
          }}
          columns={columns}
          rowClassName={(record) => record.resolved ? 'ant-table-row-disabled' : ''}
          style={{ opacity: showResolved ? 0.65 : 1 }}
          locale={{
            emptyText: (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  showResolved
                    ? 'Nenhum alerta resolvido encontrado.'
                    : 'Nenhum alerta clínico ativo no momento.'
                }
              />
            ),
          }}
          onRow={(record) => ({
            onClick: () => openDetail(record),
            style: {
              cursor: 'pointer',
              background: !record.resolved ? SEVERITY_BG[record.severity] : undefined,
            },
          })}
        />
      </Card>

      {/* Resolve modal */}
      <Modal
        title={
          <Space>
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
            <span>Resolver Alerta</span>
          </Space>
        }
        open={resolveModalOpen}
        onOk={handleResolve}
        onCancel={() => setResolveModalOpen(false)}
        okText="Confirmar Resolução"
        cancelText="Cancelar"
        okButtonProps={{ loading: resolving, danger: selectedAlert?.severity === 'critical' }}
        width={520}
      >
        {selectedAlert && (
          <div>
            <Card size="small" style={{ marginBottom: 16, background: SEVERITY_BG[selectedAlert.severity] || '#fafafa' }}>
              <Space direction="vertical" size={6} style={{ width: '100%' }}>
                <Space>
                  {severityTag(selectedAlert.severity)}
                  <Text strong>{ALERT_TYPE_LABELS[selectedAlert.alert_type] || selectedAlert.alert_type}</Text>
                </Space>
                {selectedAlert.patient_name && (
                  <Space>
                    <UserOutlined />
                    <Text strong>{selectedAlert.patient_name}</Text>
                  </Space>
                )}
                <Text>{selectedAlert.message}</Text>
                {selectedAlert.scale_name && (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Escala: {selectedAlert.scale_name}
                    {selectedAlert.actual_score != null && ` — Pontuação: ${selectedAlert.actual_score.toFixed(1)}`}
                    {selectedAlert.threshold_score != null && ` (limiar: ${selectedAlert.threshold_score.toFixed(1)})`}
                  </Text>
                )}
                {selectedAlert.disorder_name && (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    Transtorno: {selectedAlert.disorder_name}
                    {selectedAlert.probability != null && ` — ${(selectedAlert.probability * 100).toFixed(0)}%`}
                  </Text>
                )}
              </Space>
            </Card>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              <FileTextOutlined /> Observação de resolução (opcional):
            </Text>
            <TextArea
              rows={3}
              placeholder="Ex: Paciente contatado, tratamento iniciado, falso positivo..."
              value={resolveNotes}
              onChange={(e) => setResolveNotes(e.target.value)}
              maxLength={500}
              showCount
            />
          </div>
        )}
      </Modal>

      {/* Detail drawer */}
      <Drawer
        title={detailAlert ? (
          <Space>
            {severityTag(detailAlert.severity)}
            <Text strong>Detalhes do Alerta</Text>
          </Space>
        ) : 'Detalhes'}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={480}
        extra={
          detailAlert && !detailAlert.resolved ? (
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => { setDrawerOpen(false); openResolveModal(detailAlert) }}
            >
              Resolver
            </Button>
          ) : undefined
        }
      >
        {detailAlert && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Severidade">{severityTag(detailAlert.severity)}</Descriptions.Item>
              <Descriptions.Item label="Tipo">
                <Space>
                  {TYPE_ICONS[detailAlert.alert_type]}
                  {ALERT_TYPE_LABELS[detailAlert.alert_type] || detailAlert.alert_type}
                </Space>
              </Descriptions.Item>
              {detailAlert.patient_name && (
                <Descriptions.Item label="Paciente">
                  <Space>
                    <UserOutlined />
                    <Text strong>{detailAlert.patient_name}</Text>
                    {detailAlert.patient_uuid && (
                      <Button
                        type="link"
                        size="small"
                        onClick={() => navigate(`/patients/${detailAlert.patient_uuid}`)}
                      >
                        Ver prontuário
                      </Button>
                    )}
                  </Space>
                </Descriptions.Item>
              )}
              <Descriptions.Item label="Mensagem">{detailAlert.message}</Descriptions.Item>
              <Descriptions.Item label="Criado em">
                {dayjs(detailAlert.created_at).format('DD/MM/YYYY HH:mm:ss')}
                <Text type="secondary" style={{ marginLeft: 8 }}>({timeAgo(detailAlert.created_at)})</Text>
              </Descriptions.Item>
            </Descriptions>

            {(detailAlert.scale_name || detailAlert.disorder_name || detailAlert.consultation_uuid) && (
              <>
                <Divider orientation="left" style={{ fontSize: 13 }}>Contexto Clínico</Divider>
                <Descriptions column={1} size="small" bordered>
                  {detailAlert.scale_name && (
                    <Descriptions.Item label="Escala">{detailAlert.scale_name}</Descriptions.Item>
                  )}
                  {detailAlert.actual_score != null && (
                    <Descriptions.Item label="Pontuação">
                      <Space>
                        <Progress
                          percent={Math.round((detailAlert.actual_score / (detailAlert.threshold_score || 100)) * 100)}
                          size="small"
                          style={{ width: 120, margin: 0 }}
                          status={detailAlert.severity === 'critical' ? 'exception' : 'active'}
                          showInfo={false}
                        />
                        <Text strong>{detailAlert.actual_score.toFixed(1)}</Text>
                        {detailAlert.threshold_score != null && (
                          <Text type="secondary">/ {detailAlert.threshold_score.toFixed(1)} (limiar)</Text>
                        )}
                      </Space>
                    </Descriptions.Item>
                  )}
                  {detailAlert.disorder_name && (
                    <Descriptions.Item label="Transtorno">
                      <Text strong>{detailAlert.disorder_name}</Text>
                      {detailAlert.probability != null && (
                        <Text type="secondary" style={{ marginLeft: 8 }}>
                          {(detailAlert.probability * 100).toFixed(0)}% probabilidade
                        </Text>
                      )}
                    </Descriptions.Item>
                  )}
                  {detailAlert.consultation_uuid && (
                    <Descriptions.Item label="Consulta">
                      <Button
                        type="link"
                        size="small"
                        style={{ padding: 0 }}
                        onClick={() => navigate(`/consultations/${detailAlert.consultation_uuid}`)}
                      >
                        {detailAlert.consultation_uuid.slice(0, 8)}…
                      </Button>
                    </Descriptions.Item>
                  )}
                </Descriptions>
              </>
            )}

            {detailAlert.resolved && (
              <>
                <Divider orientation="left" style={{ fontSize: 13 }}>Resolução</Divider>
                <Descriptions column={1} size="small" bordered>
                  <Descriptions.Item label="Resolvido em">
                    {detailAlert.resolved_at ? dayjs(detailAlert.resolved_at).format('DD/MM/YYYY HH:mm:ss') : '—'}
                  </Descriptions.Item>
                  {detailAlert.resolution_notes && (
                    <Descriptions.Item label="Observação">{detailAlert.resolution_notes}</Descriptions.Item>
                  )}
                  {detailAlert.resolved_by && (
                    <Descriptions.Item label="Resolvido por">{detailAlert.resolved_by}</Descriptions.Item>
                  )}
                </Descriptions>
              </>
            )}
          </>
        )}
      </Drawer>
    </>
  )
}
