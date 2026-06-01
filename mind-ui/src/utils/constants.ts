export const SCALE_OPTIONS: Record<string, { label: string; options: { value: number; label: string }[] }> = {
  phq9: {
    label: 'PHQ-9 (Depressão)',
    options: [
      { value: 0, label: 'Nenhuma vez' },
      { value: 1, label: 'Vários dias' },
      { value: 2, label: 'Mais da metade dos dias' },
      { value: 3, label: 'Quase todos os dias' },
    ],
  },
  gad7: {
    label: 'GAD-7 (Ansiedade)',
    options: [
      { value: 0, label: 'Nenhuma vez' },
      { value: 1, label: 'Vários dias' },
      { value: 2, label: 'Mais da metade dos dias' },
      { value: 3, label: 'Quase todos os dias' },
    ],
  },
}

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrador',
  clinician: 'Clínico',
  viewer: 'Visualizador',
}

export const SEVERITY_COLORS: Record<string, string> = {
  minimal: '#52c41a',
  mild: '#faad14',
  moderate: '#fa8c16',
  severe: '#f5222d',
  absent: '#52c41a',
  none: '#52c41a',
  low: '#faad14',
  medium: '#fa8c16',
  high: '#f5222d',
  critical: '#cf1322',
}
