import { useEffect, useState, useCallback } from 'react'
import { Card, Table, Typography, Breadcrumb, Tag, Space, Spin, Collapse } from 'antd'
import { disordersApi } from '../../api/disorders'
import type { Disorder, Symptom, DiagnosticCriteria } from '../../types'

const { Title, Text } = Typography

interface CriterionWithSymptom extends DiagnosticCriteria {
  symptom_name?: string
}

interface DisorderRow extends Disorder {
  criteria?: CriterionWithSymptom[]
  criteriaLoading?: boolean
}

export default function DisordersPage() {
  const [disorders, setDisorders] = useState<DisorderRow[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const [disorderList, symptomList] = await Promise.all([
        disordersApi.listDisorders(),
        disordersApi.listSymptoms(),
      ])
      setDisorders(disorderList)
      setSymptoms(symptomList)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const loadCriteria = async (disorderId: number) => {
    setDisorders((prev) =>
      prev.map((d) => (d.disorder_id === disorderId ? { ...d, criteriaLoading: true } : d))
    )
    const symptomMap = new Map(symptoms.map((s) => [s.symptom_id, s.symptom_name]))
    const result = await disordersApi.getCriteria(disorderId)
    const criteriaWithNames = result.criteria.map((c: DiagnosticCriteria) => ({
      ...c,
      symptom_name: symptomMap.get(c.symptom_id) || `Sintoma #${c.symptom_id}`,
    }))
    setDisorders((prev) =>
      prev.map((d) =>
        d.disorder_id === disorderId ? { ...d, criteria: criteriaWithNames, criteriaLoading: false } : d
      )
    )
  }

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'disorder_name',
      key: 'disorder_name',
      width: 180,
      render: (v: string) => <strong>{v}</strong>,
    },
    {
      title: 'CID-11',
      dataIndex: 'cid_code',
      key: 'cid_code',
      width: 100,
      render: (v: string) => <Tag>{v}</Tag>,
    },
    {
      title: 'DSM-5-TR',
      dataIndex: 'dsm_code',
      key: 'dsm_code',
      width: 100,
      render: (v: string) => <Tag>{v}</Tag>,
    },
    {
      title: 'Descrição',
      dataIndex: 'disorder_description',
      key: 'disorder_description',
      ellipsis: true,
    },
  ]

  const renderDiagnosticData = (record: DisorderRow) => {
    const items = []
    if (record.dsm_criteria) {
      items.push({
        key: 'dsm_criteria',
        label: `Critérios DSM-5-TR`,
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13 }}>{record.dsm_criteria}</pre>,
      })
    }
    if (record.dsm_exclusions) {
      items.push({
        key: 'dsm_exclusions',
        label: `Exclusões DSM-5-TR`,
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13 }}>{record.dsm_exclusions}</pre>,
      })
    }
    if (record.dsm_differentials) {
      items.push({
        key: 'dsm_differentials',
        label: `Diagnóstico Diferencial DSM-5-TR`,
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13 }}>{record.dsm_differentials}</pre>,
      })
    }
    if (record.icd11_exclusions) {
      items.push({
        key: 'icd11_exclusions',
        label: `Exclusões CID-11`,
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13 }}>{record.icd11_exclusions}</pre>,
      })
    }
    if (record.icd11_differentials) {
      items.push({
        key: 'icd11_differentials',
        label: `Diagnóstico Diferencial CID-11`,
        children: <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: 13 }}>{record.icd11_differentials}</pre>,
      })
    }
    return items.length > 0
      ? <Collapse items={items} size="small" style={{ marginBottom: 8 }} />
      : null
  }

  return (
    <>
      <Breadcrumb items={[
        { title: 'Dashboard' },
        { title: 'Transtornos' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <Title level={4} style={{ marginBottom: 16 }}>Transtornos (DSM-5-TR / CID-11)</Title>
        <Table
          dataSource={disorders}
          columns={columns}
          rowKey="disorder_id"
          loading={loading}
          pagination={false}
          expandable={{
            expandedRowRender: (record: DisorderRow) => {
              if (record.criteriaLoading) return <Spin />
              return (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {renderDiagnosticData(record)}
                  {record.criteria ? (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #f0f0f0' }}>
                          <th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600 }}>Sintoma</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600 }}>Obrigatório</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600 }}>Duração Mínima</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600 }}>Notas Clínicas</th>
                        </tr>
                      </thead>
                      <tbody>
                        {record.criteria.map((c) => (
                          <tr key={c.criteria_id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                            <td style={{ padding: '8px 12px' }}>{c.symptom_name}</td>
                            <td style={{ padding: '8px 12px' }}>
                              {c.required_presence ? <Tag color="red">Sim</Tag> : <Tag color="default">Não</Tag>}
                            </td>
                            <td style={{ padding: '8px 12px' }}>{c.minimum_duration_days ? `${c.minimum_duration_days} dias` : '-'}</td>
                            <td style={{ padding: '8px 12px' }}>{c.clinical_notes || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <Text type="secondary">Clique para carregar critérios</Text>
                  )}
                </Space>
              )
            },
            onExpand: (expanded: boolean, record: DisorderRow) => {
              if (expanded && !record.criteria) {
                loadCriteria(record.disorder_id)
              }
            },
          }}
        />
      </Card>
    </>
  )
}
