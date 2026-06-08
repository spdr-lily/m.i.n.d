export const SCALE_OPTIONS: Record<string, { label: string; options: { value: number; label: string }[] }> = {
  'PHQ-9': {
    label: 'PHQ-9 (Depressão)',
    options: [
      { value: 0, label: 'Nenhuma vez' },
      { value: 1, label: 'Vários dias' },
      { value: 2, label: 'Mais da metade dos dias' },
      { value: 3, label: 'Quase todos os dias' },
    ],
  },
  'GAD-7': {
    label: 'GAD-7 (Ansiedade)',
    options: [
      { value: 0, label: 'Nenhuma vez' },
      { value: 1, label: 'Vários dias' },
      { value: 2, label: 'Mais da metade dos dias' },
      { value: 3, label: 'Quase todos os dias' },
    ],
  },
  MADRS: {
    label: 'MADRS (Depressão - clinician-rated)',
    options: [
      { value: 0, label: '0' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5' },
      { value: 6, label: '6' },
    ],
  },
  MDQ: {
    label: 'MDQ (Bipolar)',
    options: [
      { value: 0, label: 'Não' },
      { value: 1, label: 'Sim' },
    ],
  },
  'PCL-5': {
    label: 'PCL-5 (TEPT)',
    options: [
      { value: 0, label: '0 - Nada' },
      { value: 1, label: '1 - Um pouco' },
      { value: 2, label: '2 - Moderadamente' },
      { value: 3, label: '3 - Bastante' },
      { value: 4, label: '4 - Extremamente' },
    ],
  },
  'Y-BOCS': {
    label: 'Y-BOCS (TOC)',
    options: [
      { value: 0, label: '0' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
    ],
  },
  AUDIT: {
    label: 'AUDIT (Álcool)',
    options: [
      { value: 0, label: '0' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
    ],
  },
  ASRM: {
    label: 'ASRM (Mania)',
    options: [
      { value: 0, label: '0' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
    ],
  },
  ASRS: {
    label: 'ASRS (TDAH adulto)',
    options: [
      { value: 0, label: '0 - Nunca' },
      { value: 1, label: '1 - Raramente' },
      { value: 2, label: '2 - Às vezes' },
      { value: 3, label: '3 - Frequentemente' },
      { value: 4, label: '4 - Muito frequente' },
    ],
  },
  'AQ-10': {
    label: 'AQ-10 (Autismo)',
    options: [
      { value: 0, label: 'Discordo' },
      { value: 1, label: 'Concordo' },
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
