import { useState, useRef, useEffect, useCallback } from 'react'
import {
  Card, Input, Button, Typography, Breadcrumb, Spin, Space, Tag, Collapse, Tooltip, Progress,
} from 'antd'
import {
  SendOutlined, RobotOutlined, UserOutlined,
  SmileOutlined, FrownOutlined, MehOutlined,
  LikeOutlined, DislikeOutlined, LikeFilled, DislikeFilled,
  AlertOutlined, ClearOutlined,
} from '@ant-design/icons'
import { chatbotApi, getSessionId, setSessionId, type ChatResponse, type TranstornoResultado } from '../../api/chatbot'

const { Text, Paragraph } = Typography

interface Mensagem {
  tipo: 'user' | 'bot'
  texto: string
  dados?: ChatResponse | null
  timestamp: Date
  message_id?: number
  feedback?: 'positive' | 'negative' | null
}

function SentimentoTag({ rotulo, score }: { rotulo: string; score: number }) {
  const config: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
    positivo: { color: 'green', icon: <SmileOutlined />, label: 'Positivo' },
    negativo: { color: 'red', icon: <FrownOutlined />, label: 'Negativo' },
    neutro: { color: 'blue', icon: <MehOutlined />, label: 'Neutro' },
  }
  const c = config[rotulo] || config.neutro
  return (
    <Tooltip title={`Confiança: ${(score * 100).toFixed(0)}%`}>
      <Tag color={c.color} icon={c.icon}>{c.label}</Tag>
    </Tooltip>
  )
}

function ProbabilityBar({ prob }: { prob: number }) {
  const pct = Math.round(prob * 100)
  const color = pct >= 70 ? '#52c41a' : pct >= 40 ? '#faad14' : '#ff4d4f'
  return (
    <Tooltip title={`Probabilidade inferida: ${pct}%`}>
      <Progress
        percent={pct}
        size="small"
        strokeColor={color}
        format={() => `${pct}%`}
        style={{ margin: '4px 0' }}
      />
    </Tooltip>
  )
}

function TranstornoCard({ t }: { t: TranstornoResultado }) {
  const items: { key: string; label: string; children: React.ReactNode }[] = []

  if (t.dsm_criteria) {
    items.push({
      key: 'criteria',
      label: 'Critérios DSM-5-TR',
      children: <Text style={{ whiteSpace: 'pre-wrap' }}>{t.dsm_criteria}</Text>,
    })
  }
  if (t.dsm_exclusions) {
    items.push({
      key: 'dsm_exc',
      label: 'Exclusões DSM-5',
      children: <Text style={{ whiteSpace: 'pre-wrap' }}>{t.dsm_exclusions}</Text>,
    })
  }
  if (t.icd11_exclusions) {
    items.push({
      key: 'icd11_exc',
      label: 'Exclusões CID-11',
      children: <Text style={{ whiteSpace: 'pre-wrap' }}>{t.icd11_exclusions}</Text>,
    })
  }
  if (t.dsm_differentials) {
    items.push({
      key: 'dsm_diff',
      label: 'Diagnóstico Diferencial (DSM-5)',
      children: <Text style={{ whiteSpace: 'pre-wrap' }}>{t.dsm_differentials}</Text>,
    })
  }
  if (t.icd11_differentials) {
    items.push({
      key: 'icd11_diff',
      label: 'Diagnóstico Diferencial (CID-11)',
      children: <Text style={{ whiteSpace: 'pre-wrap' }}>{t.icd11_differentials}</Text>,
    })
  }
  if (t.criterios_detalhados && t.criterios_detalhados.length > 0) {
    items.push({
      key: 'detalhes',
      label: `Critérios Detalhados (${t.criterios_detalhados.length})`,
      children: (
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          {t.criterios_detalhados.map((c) => (
            <li key={c.criteria_id}>
              <Text strong>{c.symptom_name || 'Sintoma'}</Text>
              <Text> — {c.required_presence ? 'obrigatório' : 'opcional'}</Text>
              {c.minimum_duration_days && (
                <Text> (mín. {c.minimum_duration_days} dias)</Text>
              )}
            </li>
          ))}
        </ul>
      ),
    })
  }

  return (
    <Card
      size="small"
      title={
        <Space>
          <Text strong>{t.disorder_name}</Text>
          {t.cid_code && <Tag>CID: {t.cid_code}</Tag>}
          {t.dsm_code && <Tag>DSM: {t.dsm_code}</Tag>}
          {t.inference_probability != null && (
            <Tag color={t.inference_probability >= 0.5 ? 'green' : 'orange'}>
              ML
            </Tag>
          )}
        </Space>
      }
      style={{ marginBottom: 8 }}
    >
      {t.inference_probability != null && (
        <ProbabilityBar prob={t.inference_probability} />
      )}
      {t.disorder_description && (
        <Paragraph ellipsis={{ rows: 2, expandable: true }}>
          {t.disorder_description}
        </Paragraph>
      )}
      {items.length > 0 && <Collapse ghost items={items} size="small" />}
    </Card>
  )
}

function MensagemBubble({ msg, onFeedback }: { msg: Mensagem; onFeedback?: (message_id: number, rating: 'positive' | 'negative') => void }) {
  const isUser = msg.tipo === 'user'
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 8,
        marginBottom: 16,
        alignItems: 'flex-start',
      }}
    >
      <div
        style={{
          width: 32, height: 32, borderRadius: '50%',
          background: isUser ? '#1677ff' : '#52c41a',
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}
      >
        {isUser ? (
          <UserOutlined style={{ color: '#fff', fontSize: 14 }} />
        ) : (
          <RobotOutlined style={{ color: '#fff', fontSize: 14 }} />
        )}
      </div>
      <div
        style={{
          maxWidth: '80%',
          padding: '10px 14px',
          borderRadius: 12,
          background: isUser ? '#1677ff' : '#f0f0f0',
          color: isUser ? '#fff' : '#000',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}
      >
        {msg.dados && msg.dados.sentimento && msg.tipo === 'bot' && (
          <div style={{ marginBottom: 8 }}>
            <SentimentoTag rotulo={msg.dados.sentimento.rotulo} score={msg.dados.sentimento.score} />
          </div>
        )}
        <Text style={{ color: isUser ? '#fff' : '#000' }}>{msg.texto}</Text>
        {msg.dados?.resultados && msg.dados.resultados.length > 0 && (
          <div style={{ marginTop: 12 }}>
            {msg.dados.resultados.map((t) => (
              <TranstornoCard key={t.disorder_id} t={t} />
            ))}
          </div>
        )}
        {msg.tipo === 'bot' && msg.message_id && onFeedback && (
          <div style={{ marginTop: 8, display: 'flex', gap: 4, alignItems: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>Útil?</Text>
            <Tooltip title="Útil">
              <Button
                type="text"
                size="small"
                icon={msg.feedback === 'positive' ? <LikeFilled style={{ color: '#52c41a' }} /> : <LikeOutlined />}
                onClick={() => onFeedback(msg.message_id!, 'positive')}
              />
            </Tooltip>
            <Tooltip title="Não útil">
              <Button
                type="text"
                size="small"
                icon={msg.feedback === 'negative' ? <DislikeFilled style={{ color: '#ff4d4f' }} /> : <DislikeOutlined />}
                onClick={() => onFeedback(msg.message_id!, 'negative')}
              />
            </Tooltip>
          </div>
        )}
        <div style={{ fontSize: 11, opacity: 0.6, marginTop: 4, textAlign: isUser ? 'right' : 'left' }}>
          {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}

const BOAS_VINDAS: Mensagem = {
  tipo: 'bot',
  texto:
    'Olá! Eu sou a **MIA**, sua assistente de consulta aos critérios diagnósticos do DSM-5-TR e CID-11.\n\n'
    + 'Você pode me perguntar sobre:\n'
    + '• **Transtornos** — "o que é Transtorno Depressivo Maior?"\n'
    + '• **Critérios** — "quais os critérios para TAG?"\n'
    + '• **Exclusões** — "exclusões do TEPT"\n'
    + '• **Diagnóstico Diferencial** — "diferencial do TOC"\n\n'
    + 'Também realizo **análise de sentimento** da sua consulta!\n\n'
    + 'Use os botões 👍/👎 para me ajudar a melhorar!',
  timestamp: new Date(),
}

export default function MiaPage() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([BOAS_VINDAS])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const chatRef = useRef<HTMLDivElement>(null)
  const nextMessageId = useRef(1)

  const scrollAbaixo = useCallback(() => {
    setTimeout(() => {
      chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' })
    }, 50)
  }, [])

  useEffect(() => { scrollAbaixo() }, [mensagens, scrollAbaixo])

  const handleFeedback = useCallback(async (message_id: number, rating: 'positive' | 'negative') => {
    setMensagens((prev) =>
      prev.map((m) =>
        m.message_id === message_id ? { ...m, feedback: m.feedback === rating ? null : rating } : m
      )
    )
    try {
      await chatbotApi.sendFeedback(message_id, rating)
    } catch {
      // silent fail
    }
  }, [])

  const enviar = useCallback(async () => {
    const texto = input.trim()
    if (!texto || loading) return
    setInput('')
    const userMsg: Mensagem = { tipo: 'user', texto, timestamp: new Date() }
    setMensagens((prev) => [...prev, userMsg])
    setLoading(true)
    try {
      const dados = await chatbotApi.ask(texto)
      const mid = nextMessageId.current++
      const botMsg: Mensagem = {
        tipo: 'bot',
        texto: dados.resposta,
        dados,
        timestamp: new Date(),
        message_id: mid,
        feedback: null,
      }
      setMensagens((prev) => [...prev, botMsg])
    } catch {
      const errMsg: Mensagem = {
        tipo: 'bot',
        texto: 'Desculpe, ocorreu um erro ao processar sua consulta. Tente novamente.',
        timestamp: new Date(),
      }
      setMensagens((prev) => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }, [input, loading])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      enviar()
    }
  }

  const handleClearSession = () => {
    setSessionId('')
    setMensagens([BOAS_VINDAS])
    nextMessageId.current = 1
  }

  return (
    <>
      <Breadcrumb
        items={[
          { title: 'Dashboard', href: '/' },
          { title: 'MIA' },
        ]}
        style={{ marginBottom: 16 }}
      />
      <Card
        title={
          <Space>
            <RobotOutlined style={{ fontSize: 20, color: '#52c41a' }} />
            <span>MIA — Assistente Diagnóstico DSM-5-TR / CID-11</span>
          </Space>
        }
        extra={
          <Tooltip title="Nova conversa">
            <Button icon={<ClearOutlined />} size="small" onClick={handleClearSession}>
              Limpar
            </Button>
          </Tooltip>
        }
        style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 140px)' }}
        styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column', padding: 16, overflow: 'hidden' } }}
      >
        <div
          ref={chatRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '0 8px',
            marginBottom: 16,
          }}
        >
          {mensagens.map((msg, i) => (
            <MensagemBubble key={i} msg={msg} onFeedback={handleFeedback} />
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 16 }}>
              <div
                style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: '#52c41a', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                }}
              >
                <RobotOutlined style={{ color: '#fff', fontSize: 14 }} />
              </div>
              <Spin size="small" />
              <Text type="secondary">MIA está analisando...</Text>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Input.TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pergunte sobre transtornos, critérios, exclusões..."
            size="large"
            style={{ flex: 1, resize: 'none' }}
            disabled={loading}
            rows={2}
          />
          <Button type="primary" icon={<SendOutlined />} loading={loading} onClick={enviar} style={{ height: '100%' }}>
            Enviar
          </Button>
        </div>
      </Card>
    </>
  )
}
