from typing import Dict, List, Tuple, Optional

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


BFP = ScaleDefinition(
    name="BFP",
    description="Bateria Fatorial da Personalidade — avaliação dos 5 grandes fatores (Big Five) adaptada ao contexto clínico brasileiro. 25 itens (5 por fator: Abertura, Conscienciosidade, Extroversão, Amabilidade, Neuroticismo)",
    max_score_per_item=4.0,
    questions=[
        "Abertura - Gosto de explorar ideias novas e diferentes culturas",
        "Abertura - Tenho interesses artísticos e aprecio a beleza nas artes e na natureza",
        "Abertura - Sou curioso(a) sobre como as coisas funcionam",
        "Abertura - Valorizo experiências incomuns e viagens a lugares novos",
        "Abertura - Gosto de refletir sobre conceitos abstratos e filosóficos",
        "Conscienciosidade - Sou organizado(a) e mantenho minhas coisas em ordem",
        "Conscienciosidade - Cumpro prazos e responsabilidades com disciplina",
        "Conscienciosidade - Planejo com antecedência antes de agir",
        "Conscienciosidade - Sou meticuloso(a) e atento(a) aos detalhes",
        "Conscienciosidade - Persisto nas tarefas até concluí-las",
        "Extroversão - Sou comunicativo(a) e gosto de conversar com pessoas",
        "Extroversão - Sinto-me energizado(a) em ambientes sociais e festas",
        "Extroversão - Faço amizades com facilidade",
        "Extroversão - Gosto de ser o centro das atenções em situações sociais",
        "Extroversão - Prefiro trabalhar em grupo do que sozinho(a)",
        "Amabilidade - Procuro manter boas relações e evitar conflitos",
        "Amabilidade - Sou empático(a) e me importo com os sentimentos alheios",
        "Amabilidade - Confio nas pessoas até que provem o contrário",
        "Amabilidade - Colaboro e coopero com os outros voluntariamente",
        "Amabilidade - Trato a todos com respeito e cordialidade",
        "Neuroticismo - Costumo me preocupar facilmente com situações cotidianas",
        "Neuroticismo - Fico tenso(a) e nervoso(a) com frequência",
        "Neuroticismo - Tenho oscilações frequentes de humor",
        "Neuroticismo - Sinto-me inseguro(a) sobre minhas decisões",
        "Neuroticismo - Fico facilmente irritado(a) ou frustrado(a)",
    ],
    severity_thresholds=[
        (0, "Baixo", "Escore baixo neste fator. Considere contexto clínico e observação comportamental para interpretação."),
        (40, "Médio", "Escore médio. Traço de personalidade dentro da faixa esperada na população geral."),
        (70, "Alto", "Escore alto neste fator. Traço marcante que pode influenciar o quadro clínico e a adesão ao tratamento."),
        (90, "Muito alto", "Escore muito alto. Traço predominante que merece atenção na formulação do caso e plano terapêutico."),
    ],
)


DT12 = ScaleDefinition(
    name="DT-12 (Tríade Sombria)",
    description="Dirty Dozen (Jonason & Webster, 2010) — 12 itens para avaliação da Tríade Sombria da personalidade: Maquiavelismo, Narcisismo e Psicopatia. Adaptada ao contexto clínico brasileiro.",
    max_score_per_item=6.0,
    questions=[
        "Maquiavelismo - Costumo usar manipulação para conseguir o que quero",
        "Maquiavelismo - Tendo a bajular pessoas para obter vantagens",
        "Maquiavelismo - Utilizo outras pessoas para alcançar meus objetivos",
        "Maquiavelismo - Costumo explorar os outros em benefício próprio",
        "Narcisismo - Acredito que sou mais especial do que as outras pessoas",
        "Narcisismo - Gosto de ser o centro das atenções e receber admiração",
        "Narcisismo - Sinto que mereço tratamento diferenciado",
        "Narcisismo - Busco reconhecimento e status social",
        "Psicopatia - Tenho dificuldade em sentir culpa ou remorso",
        "Psicopatia - Sou insensível aos sentimentos dos outros",
        "Psicopatia - Tendo a ser impulsivo(a) e agir sem pensar nas consequências",
        "Psicopatia - Sinto tédio com facilidade e busco emoções fortes",
    ],
    severity_thresholds=[
        (0, "Baixo", "Escore baixo na Tríade Sombria. Traços de personalidade antissocial pouco proeminentes."),
        (30, "Moderado", "Escore moderado. Presença de traços da personalidade sombria que podem influenciar o funcionamento interpessoal."),
        (50, "Elevado", "Escore elevado. Traços marcantes de maquiavelismo, narcisismo e/ou psicopatia. Recomenda-se avaliação aprofundada da personalidade."),
        (65, "Muito elevado", "Escore muito elevado. Padrão significativo de traços sombrios. Avaliação para transtornos de personalidade do Cluster B recomendada."),
    ],
)

MEMORIA = ScaleDefinition(
    name="MEMÓRIA",
    description="Teste de Rastreio de Funções Mnêmicas — avaliação breve de memória de trabalho, curto prazo, longo prazo, episódica e semântica",
    max_score_per_item=2.0,
    questions=[
        "Registro: capacidade de repetir imediatamente uma sequência de 5 palavras (0=0 palavras, 1=2-3 palavras, 2=4-5 palavras)",
        "Memória de trabalho: consegue repetir 4 dígitos em ordem inversa (0=não, 1=parcial, 2=sim)",
        "Aprendizagem verbal: após 3 tentativas, quantas das 5 palavras recorda (0=0-1, 1=2-3, 2=4-5)",
        "Memória episódica recente - recordação tardia: quantas palavras recorda após 5 minutos (0=0-1, 1=2-3, 2=4-5)",
        "Memória episódica - reconhecimento: reconhece as palavras-alvo entre distratores (0=não, 1=parcial, 2=sim)",
        "Memória semântica: nomeia corretamente 3 figuras de categorias distintas (0=0, 1=1-2, 2=3)",
        "Memória prospectiva: lembra-se de pedir um objeto após intervalo (0=não, 1=com pista, 2=sim)",
        "Orientação têmporo-espacial: sabe dia, mês, ano e local (0=0-2, 1=3, 2=4 corretos)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento mnêmico grave. Avaliação neuropsicológica completa e investigação etiológica urgentes."),
        (5, "Déficit moderado", "Comprometimento mnêmico moderado. Sugere-se avaliação neuropsicológica detalhada e exames complementares."),
        (9, "Déficit leve", "Comprometimento mnêmico leve. Monitorar evolução; considerar queixas subjetivas e impacto funcional."),
        (13, "Normal", "Função mnêmica dentro da faixa esperada para a idade e escolaridade."),
        (16, "Normal superior", "Função mnêmica acima da média. Desempenho preservado em todos os domínios avaliados."),
    ],
)

QI_RASTREIO = ScaleDefinition(
    name="QI - RASTREIO",
    description="Teste de Rastreio Cognitivo — estimativa breve de funcionamento intelectual com domínios verbal, raciocínio perceptual, memória de trabalho e velocidade de processamento",
    max_score_per_item=3.0,
    questions=[
        "Vocabulário: define corretamente palavras de complexidade crescente (0=não, 1=parcial, 2=definição adequada, 3=elaboração precisa)",
        "Analogias verbais: identifica relação entre pares de palavras (0=não, 1=parcial, 2=adequado, 3=superior)",
        "Raciocínio matricial: completa padrões visuais abstratos (0=não, 1=1 padrão, 2=2 padrões, 3=todos)",
        "Cubos: constrói padrões geométricos com blocos coloridos (0=não, 1=com ajuda, 2=sem ajuda, 3=rápido e preciso)",
        "Memória de trabalho — dígitos ordem direta: repete até 7 dígitos (0=<4, 1=4-5, 2=6, 3=7)",
        "Memória de trabalho — dígitos ordem inversa: repete até 5 dígitos ao contrário (0=<3, 1=3, 2=4, 3=5)",
        "Velocidade de processamento: completa código símbolo-número em 120s (0=<20, 1=20-35, 2=36-50, 3=>50 corretos)",
        "Conhecimento geral: responde a perguntas de cultura geral (0=0-1, 1=2-3, 2=4-5, 3=6 corretas)",
        "Raciocínio aritmético: resolve problemas numéricos simples (0=não, 1=com ajuda, 2=sem ajuda, 3=rápido)",
        "Compreensão: explica situações sociais e normas (0=não, 1=parcial, 2=adequado, 3=elaborado)",
    ],
    severity_thresholds=[
        (0, "Muito abaixo da média", "Sugere deficiência intelectual (QI estimado <70). Avaliação neuropsicológica completa e multidisciplinar necessária."),
        (8, "Abaixo da média", "Funcionamento intelectual abaixo do esperado (QI estimado 70-85). Investigar causas e considerar suporte educacional/ocupacional."),
        (15, "Médio inferior", "Funcionamento intelectual médio-inferior (QI estimado 85-95). Acompanhar desenvolvimento e queixas específicas."),
        (20, "Média", "Funcionamento intelectual na média (QI estimado 95-110). Dentro do esperado para a população geral."),
        (25, "Médio superior", "Funcionamento intelectual acima da média (QI estimado 110-120). Bom potencial cognitivo."),
        (28, "Superior", "Funcionamento intelectual superior (QI estimado >120). Capacidade cognitiva elevada."),
    ],
)


RECONHECIMENTO_ROSTOS = ScaleDefinition(
    name="RECONHECIMENTO DE ROSTOS",
    description="Teste de Reconhecimento de Rostos — avaliação da percepção facial e memória para faces, adaptado do Benton Facial Recognition Test e Warrington Recognition Memory Test",
    max_score_per_item=2.0,
    questions=[
        "Identificação imediata: de 3 fotos, aponta a que corresponde à foto-alvo (0=não, 1=com pista, 2=sim)",
        "Identificação diferida: após 5 minutos, reconhece o rosto-alvo entre 6 distratores (0=não, 1=parcial, 2=sim)",
        "Discriminação de identidade: duas fotos da mesma pessoa em ângulos diferentes (0=não, 1=parcial, 2=sim)",
        "Discriminação de emoção: identifica expressão facial (alegria, tristeza, raiva, medo) (0=0-1, 1=2-3, 2=4 corretas)",
        "Reconhecimento de faces familiares: identifica rostos de figuras públicas conhecidas (0=0, 1=1-2, 2=3+)",
        "Matching de faces sob ruído: reconhece o mesmo rosto em condições de iluminação/ângulo alterados (0=não, 1=parcial, 2=sim)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento grave no reconhecimento facial. Sugere prosopagnosia ou déficit perceptivo visual. Avaliação neuropsicológica completa necessária."),
        (4, "Déficit moderado", "Comprometimento moderado no processamento facial. Pode impactar interações sociais. Investigar hipótese de Transtorno do Espectro Autista ou lesão occipito-temporal."),
        (7, "Déficit leve", "Déficit leve no reconhecimento facial. Monitorar queixas sociais e funcionamento interpessoal."),
        (10, "Normal", "Reconhecimento facial dentro da faixa esperada. Habilidade preservada de percepção e memória para faces."),
    ],
)

FLUENCIA_VERBAL = ScaleDefinition(
    name="FLUÊNCIA VERBAL",
    description="Teste de Fluência Verbal — avaliação das funções executivas e linguagem através de fluência fonológica (FAS) e semântica (animais)",
    max_score_per_item=2.0,
    questions=[
        "Fluência fonológica - letra F: número de palavras iniciadas com F em 1 minuto (0=<5, 1=5-9, 2=10+)",
        "Fluência fonológica - letra A: número de palavras iniciadas com A em 1 minuto (0=<5, 1=5-9, 2=10+)",
        "Fluência fonológica - letra S: número de palavras iniciadas com S em 1 minuto (0=<5, 1=5-9, 2=10+)",
        "Fluência semântica - animais: número de animais nomeados em 1 minuto (0=<10, 1=10-15, 2=16+)",
        "Fluência semântica - frutas: número de frutas nomeadas em 1 minuto (0=<6, 1=6-10, 2=11+)",
        "Erros de perseveração: repetiu palavras já ditas durante o teste (0=3+, 1=1-2, 2=0)",
        "Erros de intrusão: palavras fora da categoria solicitada (0=3+, 1=1-2, 2=0)",
        "Estratégia de clusterização: agrupa palavras por subcategorias (0=ausente, 1=parcial, 2=presente)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento grave da fluência verbal. Sugere disfunção executiva significativa (lesão frontal ou demência). Avaliação neuropsicológica urgente."),
        (5, "Déficit moderado", "Queda moderada na fluência verbal. Pode indicar comprometimento das funções executivas ou de linguagem. Investigar TDAH, depressão ou declínio cognitivo."),
        (9, "Déficit leve", "Fluência verbal discretamente reduzida. Pode estar associada a ansiedade, depressão leve ou fadiga."),
        (13, "Normal", "Fluência verbal dentro da faixa esperada para idade e escolaridade. Função executiva e linguagem preservadas."),
    ],
)

TESTE_RELOGIO = ScaleDefinition(
    name="TESTE DO RELÓGIO",
    description="Teste do Desenho do Relógio — rastreio cognitivo para funções visuoespaciais, planejamento motor e memória semântica (pontuação de Shulman adaptada)",
    max_score_per_item=3.0,
    questions=[
        "Desenho do relógio (cópia): copia o desenho de um relógio com todos os números e ponteiros (0=ausente, 1=reconhecível, 2=bom, 3=perfeito)",
        "Desenho do relógio (comando): desenha um relógio marcando 11h10 de memória (0=ausente, 1=reconhecível, 2=bom, 3=perfeito)",
        "Disposição dos números: números distribuídos corretamente ao redor do círculo (0=não, 1=parcial, 2=sim, 3=preciso)",
        "Ponteiros: posição correta dos ponteiros de hora e minuto (0=não, 1=um correto, 2=ambos aproximados, 3=ambos precisos)",
        "Planejamento: organização espacial demonstra planejamento prévio (0=desorganizado, 1=regular, 2=bom, 3=excelente)",
        "Integridade do círculo: o contorno do relógio é preservado (0=não, 1=irregular, 2=bom, 3=perfeito)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Desorganização visuoespacial grave. Altamente sugestivo de comprometimento cognitivo (demência ou lesão de hemisfério direito). Encaminhamento para avaliação neurológica."),
        (6, "Déficit moderado", "Comprometimento moderado das habilidades visuoespaciais e de planejamento. Recomenda-se avaliação neuropsicológica completa."),
        (10, "Déficit leve", "Leve dificuldade visuoespacial ou de planejamento. Pode estar relacionada a fadiga, ansiedade ou envelhecimento normal."),
        (14, "Normal", "Habilidades visuoespaciais e de planejamento preservadas. Desempenho adequado para a faixa etária."),
    ],
)

TRILHAS = ScaleDefinition(
    name="TRILHAS",
    description="Teste de Trilhas A e B (Trail Making Test) — avaliação da atenção sustentada, velocidade de processamento e flexibilidade cognitiva",
    max_score_per_item=3.0,
    questions=[
        "Trilhas A - tempo: segundos para conectar números 1-25 em ordem crescente (0=>120s, 1=60-120s, 2=30-59s, 3=<30s)",
        "Trilhas A - erros: quantidade de erros cometidos na parte A (0=5+, 1=3-4, 2=1-2, 3=0)",
        "Trilhas B - tempo: segundos para alternar entre números e letras (1-A-2-B...) (0=>180s, 1=120-180s, 2=60-119s, 3=<60s)",
        "Trilhas B - erros: quantidade de erros na parte B (0=5+, 1=3-4, 2=1-2, 3=0)",
        "Índice B-A: diferença de tempo entre parte B e parte A (0=>90s, 1=60-90s, 2=30-59s, 3=<30s)",
        "Perseveração: repetiu o mesmo tipo de estímulo sem alternar (0=4+, 1=2-3, 2=1, 3=0)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento grave da atenção e flexibilidade cognitiva. Sugere disfunção executiva significativa (lesão frontal ou demência). Avaliação neurológica necessária."),
        (6, "Déficit moderado", "Comprometimento moderado da velocidade de processamento e/ou flexibilidade cognitiva. Pode estar associado a TDAH, depressão ou lesão cerebral."),
        (10, "Déficit leve", "Leve lentificação do processamento ou dificuldade de alternância. Pode refletir ansiedade, fadiga ou envelhecimento normal."),
        (14, "Normal", "Velocidade de processamento e flexibilidade cognitiva preservadas. Alternância entre estímulos adequada."),
    ],
)

STROOP = ScaleDefinition(
    name="STROOP",
    description="Teste de Stroop (Victoria Version) — avaliação do controle inibitório, atenção seletiva e velocidade de processamento",
    max_score_per_item=2.0,
    questions=[
        "Cartão 1 - pontos: tempo para nomear cores de pontos (0=>20s, 1=10-20s, 2=<10s)",
        "Cartão 1 - erros: erros na nomeação de cores dos pontos (0=3+, 1=1-2, 2=0)",
        "Cartão 2 - palavras neutras: tempo para nomear cores de palavras neutras (0=>25s, 1=12-25s, 2=<12s)",
        "Cartão 2 - erros: erros na nomeação de palavras neutras (0=3+, 1=1-2, 2=0)",
        "Cartão 3 - Stroop: tempo para nomear cor da tinta de palavras incongruentes (ex: VERDE escrito em vermelho) (0=>40s, 1=20-40s, 2=<20s)",
        "Cartão 3 - erros: erros na condição incongruente (interferência) (0=3+, 1=1-2, 2=0)",
        "Índice de interferência: aumento de tempo entre cartão 2 e cartão 3 (0=>20s, 1=10-20s, 2=<10s)",
        "Correções espontâneas: autocorrigiu erros sem intervenção (0=nenhuma, 1=algumas, 2=sim)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento grave do controle inibitório. Elevada suscetibilidade à interferência. Sugere disfunção executiva frontal significativa."),
        (5, "Déficit moderado", "Dificuldade moderada no controle inibitório. Pode estar associada a TDAH, TOC, ansiedade ou lesão frontal."),
        (9, "Déficit leve", "Leve dificuldade de inibição de respostas automáticas. Pode refletir fadiga, ansiedade ou variação normal."),
        (13, "Normal", "Controle inibitório preservado. Capacidade adequada de suprimir respostas automáticas e manter atenção seletiva."),
    ],
)

CANCELAMENTO = ScaleDefinition(
    name="CANCELAMENTO",
    description="Teste de Cancelamento — avaliação da atenção seletiva, sustentada e velocidade perceptomotora",
    max_score_per_item=2.0,
    questions=[
        "Cancelamento de símbolos: número de alvos cancelados em 60s (0=<30%, 1=30-70%, 2=>70%)",
        "Erros de omissão: alvos não identificados (0=10+, 1=4-9, 2=<4)",
        "Erros de comissão: não-alvos marcados como alvos (0=5+, 1=2-4, 2=<2)",
        "Tempo total: segundos para concluir o cancelamento (0=>180s, 1=90-180s, 2=<90s)",
        "Estratégia de busca: padrão organizado vs aleatório (0=aleatório, 1=parcialmente organizado, 2=sistemático)",
        "Fadigabilidade: desempenho piora na segunda metade do teste (0=queda >50%, 1=queda 20-50%, 2=queda <20%)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento grave da atenção seletiva e sustentada. Incapacidade de manter foco visual e motor. Sugere lesão de hemisfério direito ou delirium."),
        (3, "Déficit moderado", "Comprometimento moderado da atenção. Pode estar associado a TDAH, depressão, ansiedade ou fadiga significativa."),
        (6, "Déficit leve", "Leve dificuldade atencional. Possível impacto de estresse, privação de sono ou transtorno de ansiedade."),
        (9, "Normal", "Atenção seletiva e sustentada preservadas. Exploração visual eficiente e organizada."),
    ],
)

REY = ScaleDefinition(
    name="FIGURA COMPLEXA DE REY",
    description="Figura Complexa de Rey-Osterrieth — avaliação da praxia construtiva, memória visuoespacial, planejamento e organização",
    max_score_per_item=3.0,
    questions=[
        "Cópia - precisão: fidelidade da reprodução dos elementos da figura (0=irreconhecível, 1=parcial, 2=bom, 3=excelente)",
        "Cópia - organização: sequência lógica de construção (0=desorganizado, 1=parcial, 2=organizado, 3=sistemático)",
        "Cópia - tempo: minutos para completar a cópia (0=>10min, 1=6-10min, 2=3-5min, 3=<3min)",
        "Memória imediata (3min): elementos recordados após 3 minutos (0=<3, 1=3-8, 2=9-14, 3=15+)",
        "Memória tardia (30min): elementos recordados após 30 minutos (0=<3, 1=3-8, 2=9-14, 3=15+)",
        "Reconhecimento: identifica elementos da figura entre distratores (0=<50%, 1=50-69%, 2=70-89%, 3=90%+)",
        "Escore de retenção: % preservado entre cópia e memória tardia (0=<30%, 1=30-49%, 2=50-69%, 3=70%+)",
        "Detalhes vs global: foco excessivo em detalhes sem integrar o todo (0=apenas detalhes, 1=detalhes > global, 2=equilíbrio, 3=integração perfeita)",
    ],
    severity_thresholds=[
        (0, "Déficit grave", "Comprometimento grave da praxia construtiva e memória visuoespacial. Sugere lesão de hemisfério direito, demência ou amnésia significativa."),
        (8, "Déficit moderado", "Comprometimento moderado da memória visuoespacial e/ou organização perceptual. Pode estar associado a declínio cognitivo, TEPT ou depressão grave."),
        (14, "Déficit leve", "Leve dificuldade visuoconstrutiva ou de memória visuoespacial. Monitorar queixas cognitivas e impacto funcional."),
        (19, "Normal", "Praxia construtiva, planejamento visuoespacial e memória visuoespacial preservados. Organização perceptual adequada."),
    ],
)

HEXACO_60 = ScaleDefinition(
    name="HEXACO-60",
    description="HEXACO-60 — Inventário HEXACO de Personalidade (Lee & Ashton, 2009), 60 itens medindo 6 dimensões: Honestidade-Humildade, Emotionalidade, Extroversão, Amabilidade, Conscienciosidade, Abertura à Experiência. Adaptado para o contexto clínico brasileiro.",
    max_score_per_item=5.0,
    questions=[
        "Honestidade-Humildade - Sinto que sou uma pessoa comum e não melhor que os outros",
        "Honestidade-Humildade - Não me interessaria por pertences caros mesmo que pudesse pagar",
        "Honestidade-Humildade - Acho errado tirar vantagem de alguém mesmo que a oportunidade apareça",
        "Honestidade-Humildade - Nunca usaria bajulação para conseguir algo que quero",
        "Honestidade-Humildade - Sei que sou superior ao que as pessoas pensam (R)",
        "Honestidade-Humildade - Sou atraído(a) por riqueza e luxo (R)",
        "Honestidade-Humildade - Seria tentado(a) a falsificar documentos se não houvesse risco (R)",
        "Honestidade-Humildade - Gosto de exibir minhas posses e conquistas (R)",
        "Honestidade-Humildade - Acho que mereço tratamento especial (R)",
        "Honestidade-Humildade - Prefiro manter os pés no chão a sonhar com grande riqueza",
        "Emotionalidade - Fico ansioso(a) quando algo ameaçador acontece",
        "Emotionalidade - Preciso de apoio emocional em momentos difíceis",
        "Emotionalidade - Sinto meus sentimentos intensamente",
        "Emotionalidade - Choro facilmente ao ver filmes ou situações tristes",
        "Emotionalidade - Tenho medo de situações perigosas",
        "Emotionalidade - Mesmo pequenas críticas me afetam profundamente",
        "Emotionalidade - Sou capaz de lidar com emergências sem me desesperar (R)",
        "Emotionalidade - Fico tenso(a) quando percebo que alguém está irritado(a) comigo",
        "Emotionalidade - Preocupo-me com coisas que podem dar errado",
        "Emotionalidade - Sou emocionalmente estável e difícil de abalar (R)",
        "Extroversão - Gosto de conversar com pessoas que não conheço",
        "Extroversão - Sinto-me energizado(a) ao estar em grupos sociais",
        "Extroversão - Sou animado(a) e otimista na maioria das situações",
        "Extroversão - Prefiro trabalhar em equipe do que sozinho(a)",
        "Extroversão - Falo pouco quando conheço pessoas novas (R)",
        "Extroversão - Evito ser o centro das atenções (R)",
        "Extroversão - Sinto-me desconfortável em festas cheias de estranhos (R)",
        "Extroversão - Considero-me uma pessoa tímida e reservada (R)",
        "Extroversão - Tenho facilidade para iniciar conversas",
        "Extroversão - Prefiro passar tempo sozinho(a) a estar com muitas pessoas (R)",
        "Amabilidade - Trato todos com respeito independentemente de quem são",
        "Amabilidade - Nunca guardo rancor de quem me magoou",
        "Amabilidade - Sou tolerante com os erros e defeitos dos outros",
        "Amabilidade - Consigo ver o lado bom mesmo de pessoas difíceis",
        "Amabilidade - Costumo criticar os outros com facilidade (R)",
        "Amabilidade - Fico irritado(a) com pessoas que não concordam comigo (R)",
        "Amabilidade - Acredito que as pessoas geralmente têm boas intenções",
        "Amabilidade - Perdoo com facilidade quando alguém me pede desculpas",
        "Amabilidade - Sou teimoso(a) e mantenho minha posição (R)",
        "Amabilidade - Julgo as pessoas com severidade quando erram (R)",
        "Conscienciosidade - Planejo com antecedência para evitar imprevistos",
        "Conscienciosidade - Cumpro prazos e compromissos rigorosamente",
        "Conscienciosidade - Mantenho minhas coisas organizadas e no lugar certo",
        "Conscienciosidade - Trabalho de forma disciplinada mesmo sem supervisão",
        "Conscienciosidade - Tomo decisões com cuidado e ponderação",
        "Conscienciosidade - Deixo tarefas importantes para a última hora (R)",
        "Conscienciosidade - Sou desleixado(a) com minha aparência e ambiente (R)",
        "Conscienciosidade - Tenho dificuldade em seguir rotinas e horários (R)",
        "Conscienciosidade - Evito responsabilidades sempre que possível (R)",
        "Conscienciosidade - Ajo por impulso sem pensar nas consequências (R)",
        "Abertura à Experiência - Gosto de explorar ideias novas e diferentes",
        "Abertura à Experiência - Tenho interesse por arte, música e literatura",
        "Abertura à Experiência - Sinto curiosidade sobre como as coisas funcionam",
        "Abertura à Experiência - Gosto de viajar e conhecer culturas diferentes",
        "Abertura à Experiência - Prefiro a rotina e o previsível ao novo (R)",
        "Abertura à Experiência - Acho difícil me interessar por temas abstratos (R)",
        "Abertura à Experiência - Tenho imaginação fértil e criativa",
        "Abertura à Experiência - Gosto de discutir questões filosóficas e existenciais",
        "Abertura à Experiência - Prefiro atividades práticas a teóricas (R)",
        "Abertura à Experiência - Fico entediado(a) com conversas sobre ideias complexas (R)",
    ],
    severity_thresholds=[
        (0, "Baixo", "Escore baixo no HEXACO-60. Perfil com possíveis escores reduzidos em múltiplos fatores. Considere avaliação clínica aprofundada."),
        (120, "Médio", "Escore médio no HEXACO-60. Perfil dentro da faixa populacional esperada na maioria dos fatores."),
        (200, "Alto", "Escore alto no HEXACO-60. Traços de personalidade marcantes em múltiplas dimensões. Considere correlações clínicas."),
        (250, "Muito alto", "Escore muito alto. Perfil com pontuações elevadas em várias dimensões. Avaliação da personalidade recomendada para contexto clínico."),
    ],
)

BIS_11 = ScaleDefinition(
    name="BIS-11",
    description="Barratt Impulsiveness Scale (Patton, Stanford & Barratt, 1995) — 30 itens para avaliação da impulsividade em 3 subescalas: Atenção (8 itens), Motora (11 itens) e Não-planejamento (11 itens). Adaptada e validada para o português brasileiro (Malloy-Diniz et al., 2010).",
    max_score_per_item=4.0,
    questions=[
        "Atenção - Planejo tarefas com cuidado e antecedência (R)",
        "Atenção - Tomo decisões rapidamente e sem pensar muito",
        "Atenção - Distraio-me com facilidade durante conversas",
        "Atenção - Sou uma pessoa concentrada e focada (R)",
        "Atenção - Tenho pensamentos rápidos que se atropelam",
        "Atenção - Mudo de hobbies e interesses com frequência",
        "Atenção - Gasto mais do que ganho ou deveria",
        "Atenção - Fico entediado(a) facilmente com tarefas repetitivas",
        "Motor - Ajo por impulso sem planejar",
        "Motor - Faço coisas no calor do momento que depois lamento",
        "Motor - Compro coisas por impulso sem necessidade real",
        "Motor - Como mesmo quando não estou com fome",
        "Motor - Tenho relações sexuais sem proteção adequada",
        "Motor - Falo o que penso sem filtrar na hora errada",
        "Motor - Tenho dificuldade em controlar impulsos agressivos",
        "Motor - Começo novos projetos sem terminar os anteriores",
        "Motor - Mudo de emprego ou curso por decisões impulsivas",
        "Motor - Arrisco-me em atividades perigosas sem pensar nos riscos",
        "Motor - Sinto urgência em satisfazer desejos imediatamente",
        "Não-planejamento - Penso nas consequências antes de agir (R)",
        "Não-planejamento - Planejo meu orçamento e finanças com cuidado (R)",
        "Não-planejamento - Preparo-me com antecedência para compromissos (R)",
        "Não-planejamento - Considero todas as opções antes de decidir (R)",
        "Não-planejamento - Invisto tempo para tomar decisões importantes (R)",
        "Não-planejamento - Organizo meu tempo de forma eficiente (R)",
        "Não-planejamento - Mantenho uma rotina estável de atividades (R)",
        "Não-planejamento - Penso a longo prazo antes de fazer mudanças (R)",
        "Não-planejamento - Uso listas e lembretes para não esquecer tarefas (R)",
        "Não-planejamento - Avalio prós e contras antes de agir (R)",
        "Não-planejamento - Estabeleço metas e planejo etapas para alcançá-las (R)",
    ],
    severity_thresholds=[
        (0, "Baixa", "Baixo nível de impulsividade. Bom controle inibitório e capacidade de planejamento."),
        (30, "Moderada", "Impulsividade moderada. Pode impactar o funcionamento diário em situações específicas."),
        (45, "Elevada", "Impulsividade elevada. Associada a TDAH, transtornos do humor, uso de substâncias e transtornos da personalidade. Avaliação clínica recomendada."),
        (60, "Muito elevada", "Impulsividade muito elevada. Forte correlação clínica com TDAH, transtorno bipolar, borderline e dependência química. Intervenção especializada necessária."),
    ],
)

TAS_20 = ScaleDefinition(
    name="TAS-20",
    description="Toronto Alexithymia Scale (Bagby, Parker & Taylor, 1994) — 20 itens para avaliação da alexitimia em 3 fatores: Dificuldade em Identificar Sentimentos (DIF, 7 itens), Dificuldade em Descrever Sentimentos (DDF, 5 itens) e Pensamento Externamente Orientado (EOT, 8 itens). Versão validada para o português brasileiro.",
    max_score_per_item=5.0,
    questions=[
        "DIF - Frequentemente não sei exatamente qual emoção estou sentindo",
        "DIF - Tenho dificuldade em encontrar palavras para expressar meus sentimentos",
        "DIF - Sinto sensações físicas estranhas que nem os médicos entendem",
        "DIF - Consigo descrever meus sentimentos com facilidade (R)",
        "DIF - Prefiro deixar os problemas se resolverem sozinhos a analisar minhas emoções",
        "DIF - Quando estou chateado(a), não sei se estou triste, com medo ou com raiva",
        "DIF - Frequentemente fico confuso(a) sobre o que estou sentindo em meu corpo",
        "DDF - Acho difícil dizer aos outros como me sinto por dentro",
        "DDF - As pessoas me dizem que falo pouco sobre meus sentimentos",
        "DDF - Tenho palavras suficientes para descrever minhas emoções (R)",
        "DDF - Consigo falar facilmente sobre meus sentimentos íntimos (R)",
        "DDF - Prefiro falar sobre atividades cotidianas do que sobre emoções",
        "EOT - As pessoas me pedem que fale mais sobre meus sentimentos",
        "EOT - Olhar para o céu ou contemplar a natureza me traz paz interior (R)",
        "EOT - Acho que é perda de tempo tentar entender o que sinto",
        "EOT - Sonhar acordado(a) é perda de tempo (R)",
        "EOT - Prefiro conversas sobre fatos do dia a dia a conversas sobre sentimentos",
        "EOT - Mesmo quando estou angustiado(a), raramente analiso o que estou sentindo",
        "EOT - Buscar significados ocultos nas emoções é uma perda de tempo",
        "EOT - Ter pensamentos íntimos sobre os sentimentos é desnecessário",
    ],
    severity_thresholds=[
        (0, "Ausente", "Baixa probabilidade de alexitimia. Habilidade preservada de identificar e descrever emoções."),
        (30, "Moderada", "Possível alexitimia leve a moderada. Alguma dificuldade no processamento emocional que pode impactar a regulação afetiva."),
        (40, "Elevada", "Alexitimia moderada a elevada. Dificuldade significativa em identificar, descrever e processar emoções. Comum em transtornos do espectro autista, TEPT, depressão e transtornos somatoformes."),
        (50, "Muito elevada", "Alexitimia elevada. Forte tendência ao pensamento externamente orientado com pobre consciência emocional. Associada a transtornos psicossomáticos, DST e dificuldades na terapia."),
    ],
)

RSES = ScaleDefinition(
    name="RSES",
    description="Rosenberg Self-Esteem Scale (Rosenberg, 1965) — 10 itens para avaliação global da autoestima. Amplamente validada internacionalmente, incluindo versão brasileira (Hutz & Zanon, 2011). Escala unifatorial com 5 itens positivos e 5 reversos.",
    max_score_per_item=4.0,
    questions=[
        "Autoestima - Sinto que sou uma pessoa de valor, pelo menos num plano igual aos outros",
        "Autoestima - Sinto que tenho várias boas qualidades",
        "Autoestima - No geral, tenho tendência a me sentir um fracasso (R)",
        "Autoestima - Sou capaz de fazer as coisas tão bem quanto a maioria das pessoas",
        "Autoestima - Sinto que não tenho muito do que me orgulhar (R)",
        "Autoestima - Tenho uma atitude positiva em relação a mim mesmo(a)",
        "Autoestima - No conjunto, estou satisfeito(a) comigo mesmo(a)",
        "Autoestima - Gostaria de ter mais respeito por mim mesmo(a) (R)",
        "Autoestima - Às vezes me sinto realmente inútil (R)",
        "Autoestima - Às vezes acho que não sou bom(a) em nada (R)",
    ],
    severity_thresholds=[
        (0, "Muito baixa", "Autoestima significativamente rebaixada. Associada a depressão grave, risco suicida e baixa adesão ao tratamento. Intervenção psicológica prioritária."),
        (15, "Baixa", "Autoestima abaixo da média. Associada a quadros depressivos, ansiedade social e insegurança interpessoal. Recomenda-se acompanhamento psicológico."),
        (25, "Média", "Autoestima dentro da faixa populacional esperada. Autopercepção equilibrada com capacidade de reconhecer qualidades e limitações."),
        (35, "Elevada", "Autoestima elevada. Boa autoconfiança e autovalorização. Pode indicar resiliência ou, em casos extremos, traços narcisistas. Avaliar contexto clínico."),
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
    "BFP": BFP,
    "DT-12 (Tríade Sombria)": DT12,
    "HEXACO-60": HEXACO_60,
    "BIS-11": BIS_11,
    "TAS-20": TAS_20,
    "RSES": RSES,
    "MEMÓRIA": MEMORIA,
    "QI - RASTREIO": QI_RASTREIO,
    "RECONHECIMENTO DE ROSTOS": RECONHECIMENTO_ROSTOS,
    "FLUÊNCIA VERBAL": FLUENCIA_VERBAL,
    "TESTE DO RELÓGIO": TESTE_RELOGIO,
    "TRILHAS": TRILHAS,
    "STROOP": STROOP,
    "CANCELAMENTO": CANCELAMENTO,
    "FIGURA COMPLEXA DE REY": REY,
}


def get_scale(name: str) -> Optional[ScaleDefinition]:
    return SCALES_REGISTRY.get(name)


def list_scales() -> Dict[str, str]:
    return {name: scale.description for name, scale in SCALES_REGISTRY.items()}


SCALE_DISORDER_MAP: Dict[str, List[Tuple[float, List[str]]]] = {
    "PHQ-9": [
        (15, ["Depressivo Maior", "Depressivo Persistente", "Disruptivo da Desregulação do Humor",
              "Transtorno Depressivo Devido", "Transtorno Depressivo Induzido"]),
        (10, ["Depressivo", "Disfórico Pré-Menstrual", "Adaptação", "Luto Prolongado"]),
        (8, ["Ansiedade", "Insônia", "Anorexia", "Bulimia", "Compulsão Alimentar",
              "Sintomas Somáticos", "Fibromialgia"]),
        (5, ["Alimentar", "Sono", "Fadiga", "Pica", "Ruminação",
              "Transtorno Mental", "Transtorno Alimentar"]),
    ],
    "MADRS": [
        (20, ["Depressivo Maior", "Depressivo Persistente"]),
        (10, ["Depressivo", "Disfórico"]),
    ],
    "BFP": [
        (70, ["Sintomas Somáticos", "Depressivo Maior", "Ansiedade", "Insônia"]),
        (55, ["Personalidade Paranoide", "Personalidade Esquizoide", "Personalidade Esquizotípica",
               "Personalidade Antissocial", "Personalidade Borderline", "Personalidade Histriônica",
               "Personalidade Narcisista", "Personalidade Esquiva", "Personalidade Dependente",
               "Personalidade Obsessivo-Compulsiva"]),
        (45, ["Pânico", "Fobia", "Ansiedade Social", "Estresse Pós-Traumático", "Anorexia",
               "Sono REM", "Sono-Vigília", "Ritmo Circadiano", "Sono Induzido"]),
        (35, ["Factício", "Disforia de Gênero", "Catatonia",
               "Transtorno do Desenvolvimento", "Transtorno da Comunicação",
               "Transtorno de Tique", "Transtorno do Movimento",
               "Desejo Sexual Hipoativo", "Orgasmo Feminino"]),
    ],
    "DT-12 (Tríade Sombria)": [
        (50, ["Uso de Substâncias", "Uso de Álcool", "Personalidade Antissocial",
               "Personalidade Borderline", "Personalidade Histriônica",
               "Personalidade Narcisista", "Obsessivo-Compulsivo",
               "Transtorno da Conduta", "Transtorno Opositivo-Desafiador"]),
        (30, ["Personalidade", "Jogo Patológico", "Explosivo Intermitente",
               "Cleptomania", "Piromania", "Transtorno Explosivo",
               "Voyeurista", "Exhibitionista", "Frotteurista",
               "Pedofílico", "Sadismo", "Masoquismo",
               "Fetichista", "Transvéstico", "Parafílico",
               "Disfunção Sexual", "Desejo Sexual", "Ejaculação",
               "Erétil", "Orgasmo Feminino"]),
    ],
    "GAD-7": [
        (10, ["Ansiedade Generalizada", "Pânico", "Agorafobia", "Ansiedade Social",
               "Ansiedade de Separação"]),
        (8, ["Fobia Específica", "Mutismo Seletivo", "Ansiedade Induzido",
              "Ansiedade Devido"]),
        (6, ["Ansiedade", "Estresse Agudo", "Sintomas Somáticos",
              "Ansiedade de Doença", "Pânico", "Agorafobia"]),
        (4, ["Catatonia", "Sexual", "Sono", "Eliminação",
              "Transtorno Mental", "Disfunção Sexual",
              "Apneia", "Hipersonolência", "Narcolepsia",
              "Pesadelo", "Sonambulismo",
              "Neurodesenvolvimento", "Disruptivo",
              "Fatores Psicológicos", "Terror Noturno",
              "Pernas Inquietas", "Ejaculação",
              "Erétil", "Orgasmo Feminino",
              "Gênito-Pélvica", "Penetração"]),
    ],
    "MDQ": [
        (7, ["Bipolar", "Ciclotímico"]),
    ],
    "ASRM": [
        (6, ["Bipolar", "Ciclotímico"]),
    ],
    "PCL-5": [
        (31, ["Estresse Pós-Traumático", "Estresse Agudo", "Apego Reativo",
               "Engajamento Social Desinibido"]),
        (20, ["Luto Prolongado", "Adaptação", "Transtornos de Adaptação",
               "Transtorno Relacionado a Trauma"]),
        (15, ["Depressivo", "Ansiedade", "Dissociativo", "Conversivo",
               "Sintomas Somáticos", "Dissociativo de Identidade",
               "Amnésia Dissociativa", "Despersonalização"]),
    ],
    "Y-BOCS": [
        (16, ["Obsessivo-Compulsivo", "TOC"]),
        (8, ["Dismórfico Corporal", "Acumulação", "Tricotilomania",
              "Escoriação", "Transtorno de Ansiedade de Doença",
              "Transtorno de Tourette", "Tique"]),
        (5, ["Eliminação", "Enurese", "Encoprese",
              "Pica", "Ruminação"]),
    ],
    "AUDIT": [
        (16, ["Uso de Álcool", "Uso de Substâncias", "Intoxicação Alcoólica",
               "Abstinência Alcoólica", "Transtorno por Uso"]),
        (8, ["Uso de Cannabis", "Uso de Alucinógenos", "Uso de Inalantes",
               "Uso de Opioides", "Uso de Sedativos", "Uso de Estimulantes",
               "Uso de Tabaco", "Jogo Patológico", "Transtorno do Jogo"]),
    ],
    "ASRS": [
        (17, ["Déficit de Atenção", "Hiperatividade", "TDAH"]),
        (5, ["Aprendizagem", "Coordenação"]),
    ],
    "AQ-10": [
        (6, ["Espectro Autista", "Autismo", "Autista"]),
        (3, ["Comunicação Social", "Comunicação Não Especificado",
              "Linguagem", "Fonológico", "Fluência com Início na Infância",
              "Gagueira", "Atraso Global do Desenvolvimento",
              "Coordenação", "Movimento Estereotipado"]),
    ],
    "RECONHECIMENTO DE ROSTOS": [
        (7, ["Espectro Autista", "Esquizofrenia", "Neurocognitivo Maior",
              "Transtorno Delirante", "Transtorno Esquizoafetivo",
              "Psicótico"]),
    ],
    "MEMÓRIA": [
        (8, ["Neurocognitivo", "Delirium", "Depressivo Maior",
              "Transtorno Depressivo", "Esquizofrenia",
              "Transtorno Esquizofreniforme", "Psicótico",
              "Dissociativo", "Transtorno Dissociativo",
              "Sono REM", "Sono-Vigília", "Ritmo Circadiano",
              "Pesadelo", "Sonambulismo", "Hipersonolência",
              "Pernas Inquietas", "Apneia", "Narcolepsia",
              "Terror Noturno"]),
    ],
    "QI-RASTREIO": [
        (8, ["Deficiência Intelectual", "Neurocognitivo", "Delirium",
              "Atraso Global do Desenvolvimento", "Esquizofrenia",
              "Transtorno Específico da Aprendizagem"]),
    ],
    "FLUÊNCIA VERBAL": [
        (9, ["Déficit de Atenção", "Depressivo", "Esquizofrenia",
              "Neurocognitivo", "Delirium", "Transtorno Delirante",
              "Transtorno Psicótico Breve", "Transtorno Esquizoafetivo",
              "Psicótico", "Esquizofreniforme"]),
    ],
    "TESTE DO RELÓGIO": [
        (10, ["Esquizofrenia", "Neurocognitivo", "Delirium", "Depressivo Maior",
               "Transtorno Delirante", "Esquizofreniforme", "Psicótico"]),
    ],
    "TRILHAS": [
        (10, ["Déficit de Atenção", "Ansiedade", "Depressivo",
               "Neurocognitivo", "Delirium", "Transtorno Delirante",
               "Esquizofrenia", "Transtorno Obsessivo-Compulsivo",
               "Esquizofreniforme", "Psicótico",
               "Transtorno de Tourette", "Tique"]),
    ],
    "STROOP": [
        (9, ["Déficit de Atenção", "Obsessivo-Compulsivo", "Ansiedade",
              "Neurocognitivo", "Delirium", "Esquizofrenia",
              "Psicótico", "Transtorno de Tourette", "Tique"]),
    ],
    "CANCELAMENTO": [
        (6, ["Déficit de Atenção", "Ansiedade", "Delirium",
              "Neurocognitivo", "Esquizofrenia",
              "Psicótico", "Tique"]),
    ],
    "FIGURA COMPLEXA DE REY": [
        (14, ["Estresse Pós-Traumático", "Depressivo", "Neurocognitivo",
               "Esquizofrenia", "Transtorno Delirante",
               "Psicótico", "Dissociativo"]),
    ],
    "HEXACO-60": [
        (250, ["Transtorno de Personalidade"]),
        (200, ["Ansiedade Generalizada", "Depressivo Maior", "Transtorno Bipolar",
                "Transtorno Obsessivo-Compulsivo", "Transtorno de Ansiedade"]),
        (160, ["Estresse Pós-Traumático", "Pânico", "Agorafobia", "Fobia",
                "Anorexia", "Bulimia", "Transtorno Alimentar"]),
        (120, ["Sintomas Somáticos", "Insônia", "Uso de Substâncias"]),
    ],
    "BIS-11": [
        (60, ["Déficit de Atenção", "TDAH", "Transtorno Bipolar",
               "Personalidade Borderline", "Uso de Substâncias",
               "Personalidade Antissocial", "Personalidade Narcisista",
               "Transtorno Explosivo Intermitente", "Jogo Patológico"]),
        (45, ["Depressivo", "Ansiedade", "Pânico", "Estresse Pós-Traumático",
               "Anorexia", "Bulimia", "Compulsão Alimentar",
               "Personalidade Histriônica", "Cleptomania",
               "Piromania", "Transtorno da Conduta",
               "Transtorno Opositivo-Desafiador"]),
        (30, ["Personalidade Esquiva", "Personalidade Dependente",
               "Transtorno de Tique", "Tourette", "Parafílico",
               "Voyeurista", "Exhibitionista", "Frotteurista",
               "Pedofílico", "Sadismo", "Masoquismo"]),
    ],
    "TAS-20": [
        (50, ["Espectro Autista", "Transtorno do Desenvolvimento",
               "Transtorno da Comunicação Social",
               "Transtorno de Personalidade Esquizoide",
               "Transtorno de Personalidade Esquizotípica",
               "Transtorno Neurocognitivo Leve"]),
        (40, ["Depressivo Maior", "Estresse Pós-Traumático",
               "Transtorno de Sintomas Somáticos",
               "Transtorno de Conversão", "Transtorno Dissociativo",
               "Transtorno de Pânico", "Transtorno de Ansiedade Generalizada",
               "Transtorno do Interesse", "Transtorno do Desejo",
               "Orgasmo Feminino"]),
        (30, ["Anorexia Nervosa", "Bulimia Nervosa",
               "Transtorno de Ansiedade Social",
               "Transtorno Obsessivo-Compulsivo",
               "Transtorno de Adaptação", "Luto Prolongado",
               "Transtorno Mental Não Especificado"]),
    ],
    "RSES": [
        (15, ["Depressivo Maior", "Transtorno Depressivo Persistente",
               "Transtorno de Ansiedade Social", "Personalidade Esquiva",
               "Transtorno de Adaptação", "Luto Prolongado",
               "Anorexia Nervosa", "Transtorno Dismórfico Corporal",
               "Desejo Sexual Hipoativo", "Orgasmo Feminino",
               "Dor Gênito-Pélvica"]),
        (25, ["Depressivo", "Fobia Social", "Personalidade Dependente",
               "Transtorno de Sintomas Somáticos", "Bulimia Nervosa",
               "Transtorno de Compulsão Alimentar",
               "Disfunção Sexual", "Ejaculação", "Erétil"]),
        (35, ["Personalidade Narcisista", "Personalidade Histriônica",
               "Transtorno Bipolar", "Transtorno Delirante"]),
    ],
}
