from typing import Dict, List, Tuple, Optional, Protocol

SCORE_OPTIONS = [0, 1, 2, 3]


def _clamp(value: float, max_value: float = 3.0) -> float:
    return max(0.0, min(float(value), max_value))


class ScaleDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        questions: List[str],
        severity_thresholds: List[Tuple[float, str, str]],
        max_score_per_item: float = 3.0,
    ):
        self.name = name
        self.description = description
        self.questions = questions
        self.severity_thresholds = sorted(severity_thresholds, key=lambda t: t[0])
        self.max_score_per_item = max_score_per_item

    def score(self, responses: List[float]) -> float:
        if not responses:
            return 0.0
        total = sum(_clamp(r, self.max_score_per_item) for r in responses[: len(self.questions)])
        return total

    def interpret(self, total_score: float) -> Tuple[str, str]:
        for threshold, severity, interpretation in reversed(self.severity_thresholds):
            if total_score >= threshold:
                return severity, interpretation
        return self.severity_thresholds[0][1], self.severity_thresholds[0][2]


PHQ9 = ScaleDefinition(
    name="PHQ-9",
    description="Questionário de Saúde do Paciente-9 — triagem para depressão",
    questions=[
        "Pouco interesse ou prazer em fazer as coisas",
        "Sentir-se para baixo, deprimido ou sem esperança",
        "Dificuldade para pegar no sono, permanecer dormindo ou dormir demais",
        "Sentir-se cansado ou com pouca energia",
        "Falta de apetite ou comer demais",
        "Sentir-se mal consigo mesmo — ou sentir que é um fracasso ou decepcionou sua família",
        "Dificuldade para se concentrar (ler jornal, assistir TV)",
        "Movimentar-se ou falar tão devagar que outras pessoas notaram? Ou o oposto — tão inquieto que se mexia muito mais que o habitual",
        "Pensamentos de que seria melhor estar morto ou de se machucar de alguma forma",
    ],
    severity_thresholds=[
        (0, "Mínimo", "Nenhum sintoma depressivo significativo."),
        (5, "Leve", "Sintomas depressivos leves. Considere monitoramento e repetir PHQ-9 no retorno."),
        (10, "Moderado", "Sintomas depressivos moderados. Recomenda-se avaliação complementar e possível tratamento."),
        (15, "Moderadamente grave", "Depressão moderadamente grave. Tratamento ativo recomendado (farmacoterapia e/ou psicoterapia)."),
        (20, "Grave", "Depressão grave. Início imediato de farmacoterapia e psicoterapia; considere encaminhamento ao especialista."),
    ],
)


GAD7 = ScaleDefinition(
    name="GAD-7",
    description="Transtorno de Ansiedade Generalizada-7 — triagem para ansiedade",
    questions=[
        "Sentir-se nervoso, ansioso ou com os nervos à flor da pele",
        "Não conseguir parar ou controlar as preocupações",
        "Preocupar-se demais com coisas diferentes",
        "Dificuldade para relaxar",
        "Ficar tão inquieto que é difícil ficar parado",
        "Ficar facilmente aborrecido ou irritado",
        "Sentir medo como se algo terrível pudesse acontecer",
    ],
    severity_thresholds=[
        (0, "Mínimo", "Nenhum sintoma de ansiedade significativo."),
        (5, "Leve", "Ansiedade leve. Considere monitoramento e intervenções psicossociais."),
        (10, "Moderado", "Ansiedade moderada. Avaliação complementar recomendada; considere farmacoterapia e/ou psicoterapia."),
        (15, "Grave", "Ansiedade grave. Tratamento ativo fortemente recomendado; considere encaminhamento ao especialista."),
    ],
)


MADRS = ScaleDefinition(
    name="MADRS",
    description="Escala de Depressão de Montgomery-Åsberg — gravidade da depressão avaliada pelo clínico",
    max_score_per_item=6.0,
    questions=[
        "Tristeza aparente — desânimo, melancolia e desespero (menos que ocasional)",
        "Tristeza relatada — relatos de humor deprimido independentemente da aparência",
        "Tensão interna — sentimentos de desconforto vago, irritabilidade, agitação interna",
        "Sono reduzido — redução da duração ou profundidade do sono em relação ao padrão habitual",
        "Apetite reduzido — sensação de perda de apetite em relação aos hábitos anteriores",
        "Dificuldade de concentração — dificuldade em organizar os pensamentos",
        "Lassidão — dificuldade em iniciar ou lentidão para realizar atividades diárias",
        "Incapacidade de sentir — interesse reduzido pelo ambiente ou atividades",
        "Pensamentos pessimistas — culpa, inferioridade, autorrecriminação, ruína",
        "Pensamentos suicidas — sensação de que a vida não vale a pena, desejo de morrer",
    ],
    severity_thresholds=[
        (0, "Ausente", "Nenhum sintoma depressivo detectado."),
        (7, "Leve", "Depressão leve. Monitoramento clínico recomendado."),
        (20, "Moderado", "Depressão moderada. Farmacoterapia e/ou psicoterapia recomendadas."),
        (35, "Grave", "Depressão grave. Início urgente de terapia antidepressiva e acompanhamento especializado."),
    ],
)


MDQ = ScaleDefinition(
    name="MDQ",
    description="Questionário de Transtorno do Humor — triagem para espectro bipolar",
    max_score_per_item=1.0,
    questions=[
        "Sentiu-se tão bem ou tão eufórico que outras pessoas acharam que você não estava normal?",
        "Sentiu-se tão irritado que gritou com pessoas ou começou brigas?",
        "Sentiu-se muito mais autoconfiante que o habitual?",
        "Dormiu muito menos que o habitual e não se sentiu cansado?",
        "Falou muito mais ou mais rápido que o habitual?",
        "Teve pensamentos acelerados na cabeça?",
        "Distraiu-se facilmente com coisas sem importância?",
        "Teve muito mais energia que o habitual?",
        "Esteve muito mais ativo ou fez muitas coisas ao mesmo tempo?",
        "Esteve muito mais sociável ou extrovertido que o habitual?",
        "Teve muito mais interesse por sexo que o habitual?",
        "Fez coisas que poderiam ter causado problemas (gastos, sexo, investimentos)?",
        "Gastou dinheiro que causou problemas financeiros?",
    ],
    severity_thresholds=[
        (0, "Negativo", "Nenhuma indicação de transtorno do espectro bipolar."),
        (7, "Positivo", "Triagem positiva para transtorno do espectro bipolar. Avaliação diagnóstica completa recomendada."),
    ],
)


PCL5 = ScaleDefinition(
    name="PCL-5",
    description="Lista de Verificação de TEPT para DSM-5 — sintomas de exposição traumática",
    max_score_per_item=4.0,
    questions=[
        "Memórias repetitivas e angustiantes do evento estressante?",
        "Sonhos repetitivos e angustiantes sobre o evento?",
        "Sentir ou agir de repente como se o evento estivesse acontecendo novamente?",
        "Ficar muito perturbado quando algo lembrava o evento?",
        "Ter fortes reações físicas quando lembrado do evento?",
        "Evitar memórias, pensamentos ou sentimentos sobre o evento?",
        "Evitar lembranças externas do evento?",
        "Dificuldade em lembrar partes importantes do evento?",
        "Ter crenças negativas fortes sobre si mesmo ou o mundo?",
        "Culpar a si mesmo ou outros pelo evento?",
        "Ter sentimentos negativos fortes (medo, culpa, vergonha)?",
        "Perda de interesse em atividades que antes gostava?",
        "Sentir-se distante ou afastado dos outros?",
        "Dificuldade em experimentar sentimentos positivos?",
        "Comportamento irritado ou agressivo?",
        "Comportamento imprudente ou autodestrutivo?",
        "Estar excessivamente alerta ou vigilante?",
        "Assustar-se facilmente?",
        "Dificuldade de concentração?",
        "Dificuldade para pegar no sono ou permanecer dormindo?",
    ],
    severity_thresholds=[
        (0, "Nenhum", "Nenhum sintoma de TEPT clinicamente significativo."),
        (31, "Leve", "Sintomas leves de TEPT. Monitorar e considerar psicoterapia."),
        (45, "Moderado", "Sintomas moderados de TEPT. Psicoterapia baseada em evidências (TCC, EMDR) recomendada."),
        (56, "Grave", "Sintomas graves de TEPT. Tratamento intensivo e encaminhamento ao especialista."),
    ],
)


YBOCS = ScaleDefinition(
    name="Y-BOCS",
    description="Escala Obsessivo-Compulsiva de Yale-Brown — gravidade do TOC",
    max_score_per_item=4.0,
    questions=[
        "Tempo gasto com pensamentos obsessivos?",
        "Interferência dos pensamentos obsessivos?",
        "Sofrimento causado pelos pensamentos obsessivos?",
        "Resistência aos pensamentos obsessivos?",
        "Controle sobre os pensamentos obsessivos?",
        "Tempo gasto com comportamentos compulsivos?",
        "Interferência dos comportamentos compulsivos?",
        "Sofrimento ao ser impedido de realizar compulsões?",
        "Resistência às compulsões?",
        "Controle sobre as compulsões?",
    ],
    severity_thresholds=[
        (0, "Nenhum", "Nenhum sintoma de TOC clinicamente significativo."),
        (8, "Leve", "Sintomas leves de TOC. Considere monitoramento e TCC."),
        (16, "Moderado", "Gravidade moderada de TOC. TCC/ERP e farmacoterapia recomendados."),
        (24, "Grave", "Sintomas graves de TOC. Tratamento intensivo e encaminhamento ao especialista."),
        (32, "Extremo", "Sintomas extremos de TOC. Tratamento intensivo urgente necessário."),
    ],
)


AUDIT = ScaleDefinition(
    name="AUDIT",
    description="Teste de Identificação de Transtornos por Uso de Álcool — triagem de consumo alcoólico",
    max_score_per_item=4.0,
    questions=[
        "Com que frequência você consome bebidas alcoólicas?",
        "Quantas doses você consome em um dia típico?",
        "Com que frequência você consome seis ou mais doses em uma ocasião?",
        "Com que frequência você percebeu que não conseguia parar de beber depois de começar?",
        "Com que frequência você deixou de fazer o que era esperado por causa da bebida?",
        "Com que frequência você precisou de uma bebida pela manhã para se sentir melhor?",
        "Com que frequência você sentiu culpa ou remorso após beber?",
        "Com que frequência você não conseguiu se lembrar da noite anterior?",
        "Alguém já se feriu por causa do seu consumo de álcool?",
        "Algum parente, amigo ou médico já sugeriu que você reduzisse a bebida?",
    ],
    severity_thresholds=[
        (0, "Baixo risco", "Uso de álcool de baixo risco. Mantenha o padrão atual."),
        (8, "Risco", "Uso de álcool de risco. Intervenção breve e aconselhamento recomendados."),
        (16, "Nocivo", "Uso nocivo de álcool. Avaliação diagnóstica e intervenção necessárias."),
        (20, "Dependência", "Possível dependência de álcool. Avaliação e tratamento especializado recomendados."),
    ],
)


ASRM = ScaleDefinition(
    name="ASRM",
    description="Escala de Autoavaliação de Mania de Altman — triagem de sintomas maníacos",
    max_score_per_item=4.0,
    questions=[
        "Mais feliz ou animado que o habitual?",
        "Mais autoconfiante que o habitual?",
        "Dormiu menos que o habitual sem se sentir cansado?",
        "Falou mais que o habitual?",
        "Esteve tão ativo que outras pessoas acharam incomum?",
    ],
    severity_thresholds=[
        (0, "Nenhum", "Nenhum sintoma maníaco detectado."),
        (6, "Possível hipomania/mania", "Pontuação elevada sugerindo possível episódio maníaco ou hipomaníaco. Avaliação complementar recomendada."),
        (10, "Mania provável", "Altamente sugestivo de episódio maníaco atual. Avaliação psiquiátrica imediata recomendada."),
    ],
)


ASRS = ScaleDefinition(
    name="ASRS",
    description="Escala de Autorrelato de TDAH em Adultos v1.1 — triagem para TDAH adulto",
    max_score_per_item=4.0,
    questions=[
        "Com que frequência você tem dificuldade para finalizar os últimos detalhes de um projeto?",
        "Com que frequência você tem dificuldade para organizar tarefas?",
        "Com que frequência você tem problemas para lembrar compromissos ou obrigações?",
        "Com que frequência você evita ou adia iniciar tarefas que exigem muita concentração?",
        "Com que frequência você mexe as mãos ou os pés quando precisa ficar sentado por muito tempo?",
        "Com que frequência você se sente excessivamente ativo e compelido a fazer coisas?",
        "Com que frequência você comete erros por descuido em projetos chatos ou difíceis?",
        "Com que frequência você tem dificuldade de manter a atenção em trabalhos repetitivos?",
        "Com que frequência você tem dificuldade de se concentrar no que as pessoas dizem?",
        "Com que frequência você perde ou tem dificuldade de encontrar objetos em casa ou no trabalho?",
        "Com que frequência você se distrai com atividades ou barulho ao redor?",
        "Com que frequência você se levanta em reuniões quando deveria permanecer sentado?",
        "Com que frequência você se sente inquieto ou agitado?",
        "Com que frequência você tem dificuldade para relaxar quando tem tempo livre?",
        "Com que frequência você fala demais em situações sociais?",
        "Com que frequência você completa as frases das pessoas durante uma conversa?",
        "Com que frequência você tem dificuldade para esperar sua vez?",
        "Com que frequência você interrompe os outros quando estão ocupados?",
    ],
    severity_thresholds=[
        (0, "Baixa", "Baixa probabilidade de TDAH adulto."),
        (17, "Moderada", "Probabilidade moderada de TDAH adulto. Parte A positiva se ≥4 de 6 itens pontuados ≥2. Avaliação diagnóstica completa recomendada."),
        (24, "Alta", "Alta probabilidade de TDAH adulto. Avaliação diagnóstica e planejamento de tratamento recomendados."),
    ],
)


AQ10 = ScaleDefinition(
    name="AQ-10",
    description="Quociente do Espectro Autista — 10 itens de triagem para autismo em adultos",
    max_score_per_item=1.0,
    questions=[
        "Costumo notar sons pequenos quando outros não percebem",
        "Geralmente concentro-me mais no quadro geral do que nos pequenos detalhes",
        "Acho fácil fazer mais de uma coisa ao mesmo tempo",
        "Se há uma interrupção, consigo voltar rapidamente ao que estava fazendo",
        "Acho fácil 'ler nas entrelinhas' quando alguém fala comigo",
        "Sei identificar se alguém está ficando entediado ao me ouvir",
        "Ao ler uma história, tenho dificuldade em entender as intenções dos personagens",
        "Gosto de colecionar informações sobre categorias de coisas (tipos de carros, pássaros)",
        "Acho fácil perceber o que alguém está pensando ou sentindo apenas olhando seu rosto",
        "Tenho dificuldade em entender as intenções das pessoas",
    ],
    severity_thresholds=[
        (0, "Negativo", "Baixa probabilidade de transtorno do espectro autista."),
        (6, "Positivo", "Triagem positiva para transtorno do espectro autista. Avaliação diagnóstica completa recomendada."),
    ],
)


SCALES_REGISTRY: Dict[str, ScaleDefinition] = {
    "PHQ-9": PHQ9,
    "GAD-7": GAD7,
    "MADRS": MADRS,
    "MDQ": MDQ,
    "PCL-5": PCL5,
    "Y-BOCS": YBOCS,
    "AUDIT": AUDIT,
    "ASRM": ASRM,
    "ASRS": ASRS,
    "AQ-10": AQ10,
}


def get_scale(name: str) -> Optional[ScaleDefinition]:
    return SCALES_REGISTRY.get(name)


def list_scales() -> Dict[str, str]:
    return {name: scale.description for name, scale in SCALES_REGISTRY.items()}
