import { useEffect, useState } from 'react'
import { Card, Table, Tag, Typography, Breadcrumb, Spin, Select, Space } from 'antd'
import { auditApi } from '../../api/audit'
import type { AuditLog } from '../../types'

const { Title } = Typography

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [entityFilter, setEntityFilter] = useState<string>('')
  const [operationFilter, setOperationFilter] = useState<string>('')

  const fetchLogs = () => {
    setLoading(true)
    auditApi.list(page, 20, entityFilter || undefined, operationFilter || undefined)
      .then((data) => {
        setLogs(data.logs)
        setTotal(data.total)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchLogs() }, [page, entityFilter, operationFilter])

  const operationColors: Record<string, string> = {
    CREATE: 'green',
    READ: 'blue',
    UPDATE: 'orange',
    DELETE: 'red',
    LOGIN: 'purple',
  }

  return (
    <>
      <Breadcrumb items={[{ title: 'Dashboard' }, { title: 'Auditoria' }]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>Logs de Auditoria</Title>
          <Space>
            <Select
              placeholder="Filtrar entidade"
              allowClear
              style={{ width: 160 }}
              value={entityFilter || undefined}
              onChange={(v) => { setEntityFilter(v || ''); setPage(1) }}
              options={[
                { value: 'Patient', label: 'Paciente' },
                { value: 'Consultation', label: 'Consulta' },
                { value: 'User', label: 'Usuário' },
                { value: 'Inference', label: 'Inferência' },
              ]}
            />
            <Select
              placeholder="Filtrar operação"
              allowClear
              style={{ width: 140 }}
              value={operationFilter || undefined}
              onChange={(v) => { setOperationFilter(v || ''); setPage(1) }}
              options={[
                { value: 'CREATE', label: 'Criação' },
                { value: 'READ', label: 'Leitura' },
                { value: 'UPDATE', label: 'Atualização' },
                { value: 'DELETE', label: 'Exclusão' },
              ]}
            />
          </Space>
        </div>
        <Table
          dataSource={logs}
          rowKey="audit_id"
          loading={loading}
          pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
          columns={[
            { title: 'Operação', dataIndex: 'operation_type', width: 110, render: (v: string) => <Tag color={operationColors[v]}>{v}</Tag> },
            { title: 'Entidade', dataIndex: 'entity_name', width: 120 },
            { title: 'ID', dataIndex: 'entity_id', width: 120, ellipsis: true },
            { title: 'Usuário', dataIndex: 'performed_by', width: 120 },
            {
              title: 'Status',
              dataIndex: 'status_code',
              width: 80,
              render: (v: number) => <Tag color={v && v < 400 ? 'green' : 'red'}>{v || '-'}</Tag>,
            },
            { title: 'Latência', dataIndex: 'latency_ms', width: 90, render: (v: number) => v ? `${v.toFixed(0)}ms` : '-' },
            { title: 'IP', dataIndex: 'ip_address', width: 130 },
            { title: 'Data', dataIndex: 'created_at', width: 160 },
          ]}
          expandable={{
            rowExpandable: (record) => !!record.old_data || !!record.new_data,
            expandedRowRender: (record) => (
              <div style={{ padding: 8 }}>
                {record.old_data && (
                  <div>
                    <Tag color="orange">Dados Antigos</Tag>
                    <pre style={{ fontSize: 12, maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(record.old_data, null, 2)}</pre>
                  </div>
                )}
                {record.new_data && (
                  <div>
                    <Tag color="green">Dados Novos</Tag>
                    <pre style={{ fontSize: 12, maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(record.new_data, null, 2)}</pre>
                  </div>
                )}
              </div>
            ),
          }}
        />
      </Card>
    </>
  )
}
