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
  'BFP': {
    label: 'BFP (Big Five)',
    options: [
      { value: 0, label: '0 - Discordo totalmente' },
      { value: 1, label: '1 - Discordo' },
      { value: 2, label: '2 - Neutro' },
      { value: 3, label: '3 - Concordo' },
      { value: 4, label: '4 - Concordo totalmente' },
    ],
  },
  'DT-12 (Tríade Sombria)': {
    label: 'DT-12 (Tríade Sombria)',
    options: [
      { value: 0, label: '0 - Discordo totalmente' },
      { value: 1, label: '1 - Discordo' },
      { value: 2, label: '2 - Discordo parcialmente' },
      { value: 3, label: '3 - Neutro' },
      { value: 4, label: '4 - Concordo parcialmente' },
      { value: 5, label: '5 - Concordo' },
      { value: 6, label: '6 - Concordo totalmente' },
    ],
  },
  'MEMÓRIA': {
    label: 'MEMÓRIA (Avaliação Mnêmica)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' },
    ],
  },
  'QI - RASTREIO': {
    label: 'QI - RASTREIO (Rastreio Cognitivo)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
    ],
  },
  'RECONHECIMENTO DE ROSTOS': {
    label: 'RECONHECIMENTO DE ROSTOS (Processamento Perceptual)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' },
    ],
  },
  'FLUÊNCIA VERBAL': {
    label: 'FLUÊNCIA VERBAL',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' },
    ],
  },
  'TESTE DO RELÓGIO': {
    label: 'TESTE DO RELÓGIO (Função Visuoconstrutiva)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
    ],
  },
  'TRILHAS': {
    label: 'TRILHAS (Função Executiva)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
    ],
  },
  'STROOP': {
    label: 'STROOP (Controle Inibitório)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' },
    ],
  },
  'CANCELAMENTO': {
    label: 'CANCELAMENTO (Atenção Seletiva)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' },
    ],
  },
  'FIGURA COMPLEXA DE REY': {
    label: 'REY (Memória Visuoespacial)',
    options: [
      { value: 0, label: '0' }, { value: 1, label: '1' }, { value: 2, label: '2' }, { value: 3, label: '3' },
    ],
  },
  'HEXACO-60': {
    label: 'HEXACO-60 (Personalidade - 6 Fatores)',
    options: [
      { value: 1, label: '1 - Discordo totalmente' },
      { value: 2, label: '2 - Discordo' },
      { value: 3, label: '3 - Neutro' },
      { value: 4, label: '4 - Concordo' },
      { value: 5, label: '5 - Concordo totalmente' },
    ],
  },
  'BIS-11': {
    label: 'BIS-11 (Impulsividade - Barratt)',
    options: [
      { value: 1, label: '1 - Raramente/Nunca' },
      { value: 2, label: '2 - Ocasionalmente' },
      { value: 3, label: '3 - Frequentemente' },
      { value: 4, label: '4 - Quase sempre/Sempre' },
    ],
  },
  'TAS-20': {
    label: 'TAS-20 (Alexitimia - Toronto)',
    options: [
      { value: 1, label: '1 - Discordo totalmente' },
      { value: 2, label: '2 - Discordo' },
      { value: 3, label: '3 - Neutro' },
      { value: 4, label: '4 - Concordo' },
      { value: 5, label: '5 - Concordo totalmente' },
    ],
  },
  'RSES': {
    label: 'RSES (Autoestima - Rosenberg)',
    options: [
      { value: 0, label: '0 - Discordo totalmente' },
      { value: 1, label: '1 - Discordo' },
      { value: 2, label: '2 - Concordo' },
      { value: 3, label: '3 - Concordo totalmente' },
    ],
  },
}

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrador',
  clinician: 'Clínico',
  psychologist: 'Psicólogo',
  psychiatrist: 'Psiquiatra',
  clinical_supervisor: 'Supervisor Clínico',
  researcher: 'Pesquisador',
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

export const SEVERITY_LABELS: Record<string, string> = {
  critical: 'Crítico',
  high: 'Alto',
  medium: 'Médio',
  low: 'Baixo',
  mild: 'Leve',
  moderate: 'Moderado',
  severe: 'Grave',
  minimal: 'Mínimo',
  absent: 'Ausente',
  none: 'Nenhum',
}

export const NEURO_SCALES: Set<string> = new Set([
  'BFP', 'DT-12 (Tríade Sombria)', 'HEXACO-60', 'BIS-11', 'TAS-20', 'RSES',
  'MEMÓRIA', 'QI - RASTREIO', 'RECONHECIMENTO DE ROSTOS',
  'FLUÊNCIA VERBAL', 'TESTE DO RELÓGIO', 'TRILHAS',
  'STROOP', 'CANCELAMENTO', 'FIGURA COMPLEXA DE REY',
])

export const CLINICAL_SCALES: Set<string> = new Set([
  'PHQ-9', 'GAD-7', 'MADRS', 'MDQ', 'PCL-5', 'Y-BOCS',
  'AUDIT', 'ASRM', 'ASRS', 'AQ-10',
])

export const ALERT_TYPE_LABELS: Record<string, string> = {
  scale_threshold: 'Limiar de Escala',
  suicidal_ideation: 'Ideação Suicida',
  missed_follow_up: 'Sem Retorno',
  high_confidence_diagnosis: 'Diagnóstico Alta Confiança',
  ideacao_suicida: 'Ideação Suicida',
  diagnostico_alta_confianca: 'Diagnóstico Alta Confiança',
  sem_retorno: 'Sem Retorno',
  limiar_escala: 'Limiar de Escala',
}
