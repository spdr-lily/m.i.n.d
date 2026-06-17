import { useEffect, useState, useCallback, useMemo } from 'react'
import { Card, Table, Typography, Breadcrumb, Tag, Space, Spin, Collapse, Button, Input } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
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

const CHAPTER_ORDER = [
  "Transtornos do Neurodesenvolvimento",
  "Espectro da Esquizofrenia e Outros Transtornos Psicóticos",
  "Transtornos Bipolares e Relacionados",
  "Transtornos Depressivos",
  "Transtornos de Ansiedade",
  "Transtornos Obsessivo-Compulsivos e Relacionados",
  "Transtornos Relacionados a Trauma e Estressores",
  "Transtornos Dissociativos",
  "Transtornos de Sintomas Somáticos e Relacionados",
  "Transtornos Alimentares e da Alimentação",
  "Transtornos da Eliminação",
  "Transtornos do Sono-Vigília",
  "Disfunções Sexuais",
  "Disforia de Gênero",
  "Transtornos Disruptivos, do Controle de Impulsos e da Conduta",
  "Transtornos Relacionados a Substâncias e Aditivos",
  "Transtornos Neurocognitivos",
  "Transtornos da Personalidade",
  "Transtornos Parafílicos",
  "Outros Transtornos Mentais",
]

export default function DisordersPage() {
  const [disorders, setDisorders] = useState<DisorderRow[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [loading, setLoading] = useState(true)
  const [searchText, setSearchText] = useState('')

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

  const grouped = useMemo(() => {
    const chapters: Record<string, DisorderRow[]> = {}
    const uncategorized: DisorderRow[] = []
    const filtered = searchText
      ? disorders.filter((d) => {
          const q = searchText.toLowerCase()
          return (
            d.disorder_name.toLowerCase().includes(q) ||
            (d.cid_code || '').toLowerCase().includes(q) ||
            (d.dsm_code || '').toLowerCase().includes(q) ||
            (d.dsm_chapter || '').toLowerCase().includes(q) ||
            (d.disorder_description || '').toLowerCase().includes(q)
          )
        })
      : disorders
    for (const d of filtered) {
      const ch = d.dsm_chapter || "Sem Capítulo"
      if (CHAPTER_ORDER.includes(ch)) {
        if (!chapters[ch]) chapters[ch] = []
        chapters[ch].push(d)
      } else {
        uncategorized.push(d)
      }
    }
    return { chapters, uncategorized }
  }, [disorders, searchText])

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'disorder_name',
      key: 'disorder_name',
      width: 260,
      render: (v: string, r: DisorderRow) => (
        <Space>
          <strong>{v}</strong>
          {r.is_core && <Tag color="blue" style={{ fontSize: 10 }}>ATIVO</Tag>}
        </Space>
      ),
    },
    {
      title: 'CID-10',
      dataIndex: 'cid_code',
      key: 'cid_code',
      width: 90,
      render: (v: string) => v ? <Tag>{v}</Tag> : null,
    },
    {
      title: 'DSM-5-TR',
      dataIndex: 'dsm_code',
      key: 'dsm_code',
      width: 90,
      render: (v: string) => v ? <Tag>{v}</Tag> : null,
    },
    {
      title: 'Capítulo',
      dataIndex: 'dsm_chapter',
      key: 'dsm_chapter',
      width: 240,
      render: (v: string) => v || '-',
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

  const renderTable = (data: DisorderRow[]) => (
    <Table
      dataSource={data}
      columns={columns}
      rowKey="disorder_id"
      loading={loading}
      pagination={false}
      size="small"
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
                <Space>
                  <Button size="small" onClick={() => loadCriteria(record.disorder_id)} loading={record.criteriaLoading}>
                    Carregar sintomas
                  </Button>
                </Space>
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
  )

  return (
    <>
      <Breadcrumb items={[
        { title: 'Dashboard' },
        { title: 'Transtornos' },
      ]} style={{ marginBottom: 16 }} />
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>
            Classificação Completa DSM-5-TR
            <Tag style={{ marginLeft: 12, fontSize: 11 }}>{disorders.length} transtornos</Tag>
          </Title>
          <Input.Search
            placeholder="Pesquisar transtornos..."
            prefix={<SearchOutlined />}
            allowClear
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 320 }}
          />
        </div>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          <Tag color="blue">ATIVO</Tag> = transtorno com pipeline clínico completo (inferência, ML, escalas, critérios)
        </Text>
        {loading ? <Spin /> : (
          <>
            {CHAPTER_ORDER.map((chapter) => {
              const items = grouped.chapters[chapter]
              if (!items || items.length === 0) return null
              return (
                <Card
                  key={chapter}
                  type="inner"
                  title={<Space><Tag color="purple">{chapter}</Tag><Text type="secondary">{items.length}</Text></Space>}
                  style={{ marginBottom: 12 }}
                >
                  {renderTable(items)}
                </Card>
              )
            })}
            {grouped.uncategorized.length > 0 && (
              <Card
                type="inner"
                title={<Space><Tag>Sem Capítulo</Tag><Text type="secondary">{grouped.uncategorized.length}</Text></Space>}
                style={{ marginBottom: 12 }}
              >
                {renderTable(grouped.uncategorized)}
              </Card>
            )}
          </>
        )}
      </Card>
    </>
  )
}
