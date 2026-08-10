import { theme } from 'antd'

export interface ChartTheme {
  gridStroke: string
  tickColor: string
  tooltipContentStyle: React.CSSProperties
  tooltipLabelStyle: React.CSSProperties
  tooltipItemStyle: React.CSSProperties
}

export function useChartTheme(): ChartTheme {
  const { token } = theme.useToken()
  return {
    gridStroke: token.colorBorderSecondary,
    tickColor: token.colorTextSecondary,
    tooltipContentStyle: {
      background: token.colorBgElevated,
      border: `1px solid ${token.colorBorder}`,
      borderRadius: 8,
      boxShadow: token.boxShadowSecondary,
    },
    tooltipLabelStyle: { color: token.colorText },
    tooltipItemStyle: { color: token.colorText },
  }
}
