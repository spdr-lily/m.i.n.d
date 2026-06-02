import logo from '../assets/logo.png'

interface MindLogoProps {
  size?: number
  collapsed?: boolean
}

export default function MindLogo({ size = 64, collapsed }: MindLogoProps) {
  const h = collapsed ? size : Math.round(size * 64 / 240)
  const w = collapsed ? size : size
  return (
    <img
      src={logo}
      alt="MIND"
      width={w}
      height={h}
      style={{ objectFit: 'contain', display: 'block', maxWidth: '100%' }}
    />
  )
}
