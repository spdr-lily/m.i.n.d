import { useRef, useState } from 'react'
import { Button, message, theme } from 'antd'
import { DownloadOutlined } from '@ant-design/icons'
import { toPng } from 'html-to-image'

interface ChartSaverProps {
  filename: string
  children: React.ReactNode
  style?: React.CSSProperties
}

export default function ChartSaver({ filename, children, style }: ChartSaverProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [saving, setSaving] = useState(false)
  const { token } = theme.useToken()

  const handleSave = async () => {
    if (!ref.current) return
    setSaving(true)
    try {
      const dataUrl = await toPng(ref.current, {
        backgroundColor: token.colorBgContainer,
        pixelRatio: 2,
      })
      const link = document.createElement('a')
      link.download = filename
      link.href = dataUrl
      link.click()
      message.success('Gráfico salvo como imagem')
    } catch {
      message.error('Erro ao salvar gráfico como imagem')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ position: 'relative', ...style }}>
      <div style={{ position: 'absolute', top: 0, right: 0, zIndex: 2 }}>
        <Button size="small" icon={<DownloadOutlined />} loading={saving} onClick={handleSave}>
          Salvar gráfico
        </Button>
      </div>
      <div ref={ref}>{children}</div>
    </div>
  )
}
