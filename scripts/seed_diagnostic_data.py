"""Seed comprehensive diagnostic data: DSM-5-TR criteria, ICD-11 exclusions, differentials.

Data mined from DSM-5-TR (APA, 2022) and ICD-11 CDDR (WHO, 2024).
"""
from app.core.database import SessionLocal
from app.models.base import (
    Disorder, ICD11Code, ICD11Exclusion, ICD11Differential,
    ClassificationAuthority,
)


DSM5TR_CRITERIA = {
    "Transtorno Depressivo Maior": {
        "criteria": (
            "A. Cinco (ou mais) dos seguintes sintomas estiveram presentes durante o mesmo período "
            "de 2 semanas e representam uma mudança em relação ao funcionamento anterior; pelo menos "
            "um dos sintomas é (1) humor deprimido ou (2) perda de interesse ou prazer.\n"
            "1. Humor deprimido na maior parte do dia, quase todos os dias.\n"
            "2. Acentuada diminuição de interesse ou prazer em todas ou quase todas as atividades.\n"
            "3. Perda ou ganho significativo de peso sem estar fazendo dieta, ou diminuição ou "
            "aumento do apetite quase todos os dias.\n"
            "4. Insônia ou hipersonia quase todos os dias.\n"
            "5. Agitação ou retardo psicomotor quase todos os dias.\n"
            "6. Fadiga ou perda de energia quase todos os dias.\n"
            "7. Sentimentos de inutilidade ou culpa excessiva/inapropriada.\n"
            "8. Capacidade diminuída de concentração ou indecisão.\n"
            "9. Pensamentos recorrentes de morte, ideação suicida ou tentativa de suicídio.\n"
            "B. Os sintomas causam sofrimento clinicamente significativo ou prejuízo funcional.\n"
            "C. O episódio não é atribuível aos efeitos de uma substância ou condição médica.\n"
            "D. A ocorrência do episódio não é melhor explicada por transtorno esquizoafetivo, "
            "esquizofrenia ou outro transtorno psicótico.\n"
            "E. Nunca houve episódio maníaco ou hipomaníaco."
        ),
        "exclusions": (
            "Episódio depressivo devido a outra condição médica; transtorno por uso de substância; "
            "transtorno esquizoafetivo; esquizofrenia; transtorno delirante; transtorno bipolar; "
            "transtorno depressivo persistente (distimia - se não houver episódio maior); "
            "luto não complicado (embora a distinção seja clínica e de julgamento)."
        ),
        "differentials": (
            "Transtorno bipolar (especialmente BP II - episódios hipomaníacos podem não ser "
            "relatados espontaneamente); transtorno de ansiedade generalizada; transtorno de "
            "estresse pós-traumático; transtorno de adaptação; transtorno depressivo persistente "
            "(distimia); transtorno de sintomas somáticos; transtorno por uso de substância; "
            "transtorno de pânico com agorafobia."
        ),
        "icd11_exclusions": (
            "Recurrent depressive disorder (6A71); Adjustment disorder (6B43); "
            "Bipolar or related disorders (BlockL2-6A6); "
            "Symptoms attributable to substances or medical conditions."
        ),
        "icd11_differentials": (
            "Bipolar type I/II disorder (6A60/6A61); Generalized anxiety disorder (6B00); "
            "Panic disorder (6B01); Mixed depressive and anxiety disorder (6A73); "
            "Prolonged grief disorder (6B42); Schizoaffective disorder (6A21)."
        ),
    },
    "Transtorno de Ansiedade Generalizada": {
        "criteria": (
            "A. Ansiedade e preocupação excessivas ocorrendo na maioria dos dias por pelo menos "
            "6 meses, com diversos eventos ou atividades.\n"
            "B. O indivíduo considera difícil controlar a preocupação.\n"
            "C. A ansiedade e preocupação estão associadas a três (ou mais) dos seguintes sintomas "
            "(apenas um item é exigido para crianças):\n"
            "1. Inquietação ou sensação de estar no limite.\n"
            "2. Fatigabilidade.\n"
            "3. Dificuldade de concentração ou mente vazia.\n"
            "4. Irritabilidade.\n"
            "5. Tensão muscular.\n"
            "6. Perturbação do sono (dificuldade em conciliar ou manter o sono, ou sono insatisfatório).\n"
            "D. A ansiedade, preocupação ou sintomas físicos causam sofrimento ou prejuízo funcional.\n"
            "E. A perturbação não é atribuível aos efeitos de uma substância ou condição médica.\n"
            "F. A perturbação não é melhor explicada por outro transtorno mental."
        ),
        "exclusions": (
            "Ansiedade devido a condição médica geral (hipertireoidismo, arritmias, asma); "
            "transtorno por uso de substância (cafeína, estimulantes, abstinência de sedativos); "
            "transtorno de pânico; transtorno obsessivo-compulsivo; transtorno de ansiedade social; "
            "transtorno de estresse pós-traumático; transtorno de ansiedade de doença."
        ),
        "differentials": (
            "Transtorno de pânico (ataques abruptos vs. preocupação difusa); transtorno de "
            "ansiedade social (foco em desempenho social); transtorno obsessivo-compulsivo "
            "(obsessões/compulsões egodistônicas vs. preocupação difusa); transtorno de estresse "
            "pós-traumático (relação temporal com trauma); depressão maior (ruminação pessimista "
            "vs. preocupação antecipatória); transtorno de ansiedade de doença (foco em saúde); "
            "transtorno de adaptação (estressor identificável,时限 menor)."
        ),
        "icd11_exclusions": (
            "Panic disorder (6B01); Depressive disorders (6A70-6A71); "
            "Obsessive-compulsive disorder (6B20); Health anxiety disorder (6B23)."
        ),
        "icd11_differentials": (
            "Panic disorder (6B01); Single episode depressive disorder (6A70); "
            "Mixed depressive and anxiety disorder (6A73); Social anxiety disorder (6B04); "
            "Obsessive-compulsive disorder (6B20)."
        ),
    },
    "Transtorno do Pânico": {
        "criteria": (
            "A. Ataques de pânico inesperados e recorrentes.\n"
            "B. Pelo menos um dos ataques foi seguido por 1 mês (ou mais) de uma ou ambas: "
            "1. Preocupação persistente acerca de ataques adicionais ou suas consequências.\n"
            "2. Mudança desadaptativa no comportamento relacionada aos ataques.\n"
            "C. A perturbação não é atribuível aos efeitos de uma substância ou condição médica.\n"
            "D. A perturbação não é melhor explicada por outro transtorno mental (ansiedade social, "
            "fobia específica, agorafobia, TOC, TEPT, transtorno de ansiedade de separação).\n"
            "Ataque de pânico: surto abrupto de medo intenso ou desconforto que alcança pico em "
            "minutos, com 4+ sintomas: palpitações, sudorese, tremores, sensação de sufocamento, "
            "dor no peito, náusea, tontura, calafrios/ondas de calor, parestesias, desrealização, "
            "medo de perder o controle, medo de morrer."
        ),
        "exclusions": (
            "Ataques de pânico devido a condição médica (hipertireoidismo, feocromocitoma, "
            "arritmias, asma, DPOC); transtorno por uso de substância (estimulantes, cafeína, "
            "maconha); transtorno de ansiedade generalizada; agorafobia sem pânico; "
            "fobia específica; transtorno de ansiedade social."
        ),
        "differentials": (
            "Transtorno de ansiedade generalizada (ansiedade persistente vs. paroxística); "
            "agorafobia (pode ocorrer com ou sem pânico); transtorno de pânico noturno vs. "
            "transtorno do sono; transtorno de estresse pós-traumático (flashbacks autonômicos); "
            "prolapso da válvula mitral; transtorno de ansiedade de doença; transtorno de "
            "conversão; síndrome do seio carotídeo."
        ),
        "icd11_exclusions": (
            "Agoraphobia (6B02); Specific phobia (6B03); Social anxiety disorder (6B04); "
            "Generalized anxiety disorder (6B00); Health anxiety disorder (6B23)."
        ),
        "icd11_differentials": (
            "Generalized anxiety disorder (6B00); Agoraphobia (6B02); Social anxiety disorder (6B04); "
            "Specific phobia (6B03); Health anxiety disorder (6B23)."
        ),
    },
    "Transtorno de Estresse Pós-Traumático": {
        "criteria": (
            "A. Exposição a morte real ou ameaçadora, lesão grave ou violência sexual através de "
            "experiência direta, testemunho, conhecimento (familiar/amigo próximo) ou exposição "
            "repetida a detalhes aversivos.\n"
            "B. Presença de 1+ sintoma intrusivo: memórias angustiantes recorrentes, sonhos "
            "angustiantes, flashbacks dissociativos, sofrimento psicológico intenso ou reações "
            "fisiológicas a estímulos que simbolizam o trauma.\n"
            "C. Esquiva persistente de estímulos associados ao trauma (1+ sintoma).\n"
            "D. Alterações negativas em cognições e humor (2+ sintomas): amnésia dissociativa, "
            "crenças negativas persistentes, distorções cognitivas sobre causa/consequências, "
            "estado emocional negativo persistente, diminuição do interesse, desapego, "
            "incapacidade de experimentar emoções positivas.\n"
            "E. Alterações na excitação e reatividade (2+ sintomas): comportamento irritado/irritabilidade, "
            "comportamento imprudente/autodestrutivo, hipervigilância, resposta de sobressalto "
            "exagerada, problemas de concentração, perturbação do sono.\n"
            "F. Duração da perturbação > 1 mês.\n"
            "G. Sofrimento clinicamente significativo ou prejuízo funcional.\n"
            "H. Não atribuível a substância ou condição médica."
        ),
        "exclusions": (
            "Transtorno de adaptação (estressor não-traumático, < 1 mês); transtorno de estresse "
            "agudo (3 dias a 1 mês); transtorno de luto prolongado; depressão maior (sem trauma "
            "identificável); transtorno de ansiedade generalizada; transtorno de pânico; "
            "transtorno obsessivo-compulsivo; transtorno de estresse pós-traumático complexo (CID-11)."
        ),
        "differentials": (
            "Transtorno de estresse agudo (diferença temporal 3-30 dias); transtorno de adaptação "
            "(estressor menos severo, sem todos os clusters sintomáticos); depressão maior (humor "
            "deprimido, anedonia, sem reexperiência/esquiva); transtorno obsessivo-compulsivo "
            "(obsessões sem relação com trauma); transtorno de pânico (ataques sem gatilho "
            "traumático específico); transtorno de ansiedade generalizada (preocupação difusa "
            "sem foco traumático); transtorno por uso de substância; TEPT complexo (CID-11: "
            "distúrbios graves e persistentes na regulação do afeto, identidade e relacionamentos)."
        ),
        "icd11_exclusions": (
            "Acute stress reaction (Q24.1); Adjustment disorder (6B43); "
            "Complex post-traumatic stress disorder (6B41); Prolonged grief disorder (6B42)."
        ),
        "icd11_differentials": (
            "Complex PTSD (6B41); Adjustment disorder (6B43); Generalized anxiety disorder (6B00); "
            "Panic disorder (6B01); Depressive disorders (6A70-6A71); "
            "Substance use disorders (6C40-6C4Z)."
        ),
    },
    "Transtorno Depressivo Persistente (Distimia)": {
        "criteria": (
            "A. Humor deprimido na maior parte do dia, na maioria dos dias, por pelo menos 2 anos "
            "(1 ano para crianças/adolescentes).\n"
            "B. Presença de 2+ sintomas: 1. Pouco apetite ou alimentação em excesso. "
            "2. Insônia ou hipersonia. 3. Baixa energia ou fadiga. 4. Baixa autoestima. "
            "5. Dificuldade de concentração ou indecisão. 6. Sentimentos de desesperança.\n"
            "C. Durante o período de 2 anos, o indivíduo nunca esteve sem os sintomas por mais "
            "de 2 meses consecutivos.\n"
            "D. Não houve episódio depressivo maior nos primeiros 2 anos (se houver, considera-se "
            "TDM crônico, não distimia).\n"
            "E. Nunca houve episódio maníaco/hipomaníaco.\n"
            "F. Não é melhor explicado por transtorno psicótico.\n"
            "G. Não é atribuível a substância ou condição médica.\n"
            "H. Causa sofrimento ou prejuízo clinicamente significativo."
        ),
        "exclusions": (
            "Depressão maior crônica (episódio maior nos primeiros 2 anos); depressão maior "
            "recorrente com recuperação incompleta entre episódios; transtorno bipolar; "
            "transtorno psicótico; transtorno por uso de substância; condição médica."
        ),
        "differentials": (
            "Depressão maior (episódio franco vs. curso crônico de baixa intensidade); depressão "
            "maior com remissão parcial (história de episódios maiores distintos); transtorno de "
            "ansiedade generalizada (preocupação vs. humor deprimido); transtorno de personalidade "
            "dependente ou esquiva (início precoce e padrão persistente); transtorno de adaptação "
            "com humor deprimido (estressor identificável, duração < 2 anos)."
        ),
        "icd11_exclusions": (
            "Single episode depressive disorder (6A70); Recurrent depressive disorder (6A71); "
            "Bipolar or related disorders (BlockL2-6A6)."
        ),
        "icd11_differentials": (
            "Recurrent depressive disorder (6A71); Generalized anxiety disorder (6B00); "
            "Mixed depressive and anxiety disorder (6A73); Bipolar type II disorder (6A61); "
            "Schizoaffective disorder (6A21)."
        ),
    },
    "Transtorno de Ansiedade Social": {
        "criteria": (
            "A. Medo ou ansiedade intensos acerca de 1+ situações sociais nas quais o indivíduo "
            "é exposto a possível escrutínio por parte de outros.\n"
            "B. O indivíduo teme agir de forma a mostrar sintomas de ansiedade que serão "
            "avaliados negativamente.\n"
            "C. As situações sociais quase sempre provocam medo ou ansiedade.\n"
            "D. As situações sociais são evitadas ou suportadas com intensa ansiedade.\n"
            "E. O medo ou ansiedade é desproporcional à ameaça real.\n"
            "F. Persiste por 6+ meses.\n"
            "G. Causa sofrimento ou prejuízo clinicamente significativo.\n"
            "H. Não é atribuível a substância ou condição médica.\n"
            "I. Não é melhor explicado por outro transtorno (pânico, agorafobia, TOC, TEPT, "
            "transtorno dismórfico corporal).\n"
            "J. Se presente outra condição médica (doença de Parkinson, obesidade, cicatrizes), "
            "o medo é claramente excessivo ou não relacionado."
        ),
        "exclusions": (
            "Transtorno de pânico (ataques em situações sociais podem ser secundários); agorafobia "
            "(medo de múltiplas situações, não apenas sociais); transtorno de ansiedade generalizada "
            "(preocupação difusa); transtorno dismórfico corporal (foco em defeito físico percebido); "
            "TEPT (relação com trauma)."
        ),
        "differentials": (
            "Transtorno de pânico com agorafobia (ataques de pânico como foco principal); "
            "agorafobia (medo de múltiplas situações, não apenas interação social); transtorno de "
            "ansiedade generalizada (preocupação excessiva em múltiplos domínios); transtorno de "
            "personalidade esquiva (mais generalizado, não restrito a situações sociais); "
            "mutismo seletivo (em crianças); fobia específica (situação específica)."
        ),
        "icd11_exclusions": (
            "Panic disorder (6B01); Agoraphobia (6B02); Specific phobia (6B03); "
            "Body dysmorphic disorder (6B21)."
        ),
        "icd11_differentials": (
            "Panic disorder (6B01); Agoraphobia (6B02); Specific phobia (6B03); "
            "Generalized anxiety disorder (6B00); Schizoid personality disorder (6D11); "
            "Avoidant personality disorder (6D12)."
        ),
    },
    "Transtorno Bipolar Tipo I": {
        "criteria": (
            "A. Preenchimento dos critérios para pelo menos um episódio maníaco.\n"
            "Episódio maníaco: período distinto de humor anormal e persistentemente elevado, "
            "expansivo ou irritável, e aumento anormal e persistente da atividade ou energia, "
            "com duração mínima de 1 semana (ou qualquer duração se hospitalização necessária), "
            "presente na maior parte do dia, quase todos os dias.\n"
            "3+ sintomas (4+ se humor apenas irritável):\n"
            "1. Autoestima inflada ou grandiosidade.\n"
            "2. Redução da necessidade de sono.\n"
            "3. Fala mais acelerada ou pressão para falar.\n"
            "4. Fuga de ideias ou pensamento acelerado.\n"
            "5. Distraibilidade (relatada ou observada).\n"
            "6. Aumento da atividade dirigida a objetivos ou agitação psicomotora.\n"
            "7. Envolvimento excessivo em atividades de alto risco (gastos, sexo, investimentos).\n"
            "B. O episódio causa prejuízo acentuado no funcionamento ou requer hospitalização, "
            "ou apresenta características psicóticas.\n"
            "C. Não é atribuível a substância ou condição médica.\n"
            "Nota: Episódio hipomaníaco ou depressivo maior pode preceder ou seguir o episódio maníaco."
        ),
        "exclusions": (
            "Transtorno bipolar tipo II (apenas episódios hipomaníacos, nunca maníacos); "
            "transtorno esquizoafetivo; esquizofrenia; transtorno delirante; transtorno por "
            "uso de substância (cocaína, anfetaminas, corticosteroides); condição médica "
            "(hipertireoidismo, doença de Cushing, esclerose múltipla)."
        ),
        "differentials": (
            "Transtorno bipolar tipo II (hipomania vs. mania); transtorno de déficit de atenção/"
            "hiperatividade (hiperatividade/impulsividade sem episódios distintos de humor); "
            "transtorno de personalidade borderline (instabilidade afetiva reativa vs. episódica); "
            "transtorno por uso de substância (intoxicação/abstinência mimetizando mania); "
            "esquizofrenia (sintomas psicóticos persistentes sem episódios de humor); "
            "transtorno de estresse pós-traumático (hipervigilância, irritabilidade)."
        ),
        "icd11_exclusions": (
            "Bipolar type II disorder (6A61); Schizoaffective disorder (6A21); "
            "Schizophrenia (6A20); Substance-induced mood disorder."
        ),
        "icd11_differentials": (
            "Bipolar type II disorder (6A61); Recurrent depressive disorder (6A71); "
            "Schizoaffective disorder (6A21); Schizophrenia (6A20); "
            "ADHD (6A05); Borderline personality disorder (6D11)."
        ),
    },
    "Transtorno Bipolar Tipo II": {
        "criteria": (
            "A. Preenchimento dos critérios para pelo menos um episódio hipomaníaco E pelo menos "
            "um episódio depressivo maior.\n"
            "Episódio hipomaníaco: período distinto de humor anormal e persistentemente elevado, "
            "expansivo ou irritável, com aumento anormal e persistente da atividade ou energia, "
            "com duração mínima de 4 dias consecutivos, presente na maior parte do dia, quase todos "
            "os dias. Mesmos sintomas do episódio maníaco (3+ ou 4+).\n"
            "O episódio representa uma mudança clara no funcionamento, mas NÃO causa prejuízo "
            "acentuado no funcionamento social/ocupacional, NÃO requer hospitalização e NÃO "
            "apresenta características psicóticas.\n"
            "B. Nunca houve episódio maníaco.\n"
            "C. A ocorrência do episódio não é atribuível a substância ou condição médica.\n"
            "D. Causa sofrimento ou prejuízo clinicamente significativo."
        ),
        "exclusions": (
            "Transtorno bipolar tipo I (presença de mania); transtorno ciclotímico (sintomas "
            "hipomaníacos e depressivos subclínicos crônicos sem episódios maiores); depressão "
            "maior (se episódios hipomaníacos não forem identificados); transtorno esquizoafetivo."
        ),
        "differentials": (
            "Transtorno bipolar tipo I (mania vs. hipomania); depressão maior (pacientes podem "
            "não relatar hipomania espontaneamente); transtorno ciclotímico (flutuações crônicas "
            "menos severas); transtorno de personalidade borderline (reatividade emocional "
            "desencadeada por eventos interpessoais); TDAH em adultos; transtorno por uso de "
            "substância; transtorno de ansiedade generalizada."
        ),
        "icd11_exclusions": (
            "Bipolar type I disorder (6A60); Cyclothymic disorder (6A62); "
            "Schizoaffective disorder (6A21)."
        ),
        "icd11_differentials": (
            "Bipolar type I disorder (6A60); Recurrent depressive disorder (6A71); "
            "Cyclothymic disorder (6A62); Schizoaffective disorder (6A21); "
            "ADHD (6A05); Borderline personality disorder (6D11)."
        ),
    },
    "Transtorno Obsessivo-Compulsivo": {
        "criteria": (
            "A. Presença de obsessões, compulsões ou ambas.\n"
            "Obsessões: pensamentos, impulsos ou imagens recorrentes e persistentes, "
            "experimentados como intrusivos e indesejados, que causam ansiedade ou sofrimento. "
            "O indivíduo tenta ignorar, suprimir ou neutralizar com outro pensamento/ação.\n"
            "Compulsões: comportamentos repetitivos (lavar, verificar) ou atos mentais (rezar, "
            "contar) que o indivíduo se sente compelido a executar para prevenir ou reduzir a "
            "ansiedade ou evitar um evento temido.\n"
            "B. As obsessões ou compulsões consomem tempo (1+ hora/dia) ou causam sofrimento/"
            "prejuízo clinicamente significativo.\n"
            "C. Não é atribuível a substância ou condição médica.\n"
            "D. Não é melhor explicado por outro transtorno mental."
        ),
        "exclusions": (
            "Transtorno de ansiedade generalizada (preocupação excessiva vs. obsessões); "
            "transtorno dismórfico corporal; tricotilomania; transtorno de escoriação; "
            "transtorno de acumulação; TOC devido a substância ou condição médica; "
            "tiques motores simples (sem componente obsessivo-compulsivo); transtorno do "
            "espectro autista (interesses fixos vs. obsessões)."
        ),
        "differentials": (
            "Transtorno de ansiedade generalizada (preocupações com eventos da vida real vs. "
            "obsessões egodistônicas); transtorno dismórfico corporal (foco em defeito físico "
            "percebido); transtorno de acumulação (dificuldade em descartar objetos); "
            "transtorno de tique (tiques simples/múltiplos sem obsessões); transtorno do "
            "espectro autista (comportamentos repetitivos sem neutralização de obsessões); "
            "transtorno psicótico (obsessões com insight pobre vs. delírios); TDAH; depressão "
            "maior (ruminação passiva vs. obsessões ativas)."
        ),
        "icd11_exclusions": (
            "Generalized anxiety disorder (6B00); Health anxiety disorder (6B23); "
            "Body dysmorphic disorder (6B21); Hoarding disorder (6B24); "
            "Tic disorders (8A05)."
        ),
        "icd11_differentials": (
            "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
            "Body dysmorphic disorder (6B21); Hoarding disorder (6B24); "
            "Schizophrenia (6A20); Depressive disorders (6A70-6A71)."
        ),
    },
    "Agorafobia": {
        "criteria": (
            "A. Medo ou ansiedade intensos acerca de 2+ situações:\n"
            "1. Uso de transporte público.\n"
            "2. Estar em espaços abertos.\n"
            "3. Estar em espaços fechados.\n"
            "4. Estar em uma multidão ou fila.\n"
            "5. Estar fora de casa sozinho.\n"
            "B. O indivíduo teme ou evita estas situações devido a pensamentos de que pode ser "
            "difícil escapar ou obter ajuda caso desenvolva sintomas tipo pânico ou outros "
            "sintomas incapacitantes.\n"
            "C. As situações quase sempre provocam medo ou ansiedade.\n"
            "D. As situações são ativamente evitadas ou exigem presença de acompanhante.\n"
            "E. O medo é desproporcional ao perigo real.\n"
            "F. Persiste por 6+ meses.\n"
            "G. Causa sofrimento ou prejuízo clinicamente significativo.\n"
            "H. Outra condição médica não explica melhor os sintomas."
        ),
        "exclusions": (
            "Transtorno de pânico sem agorafobia; fobia específica (situação única); "
            "transtorno de ansiedade social (foco em interação social); transtorno de "
            "estresse pós-traumático; transtorno de ansiedade de separação."
        ),
        "differentials": (
            "Transtorno de pânico (pode preceder ou coexistir com agorafobia); fobia específica "
            "(medo de uma única situação, sem o padrão de múltiplas situações temidas); "
            "transtorno de ansiedade social (medo específico de avaliação social negativa); "
            "transtorno de estresse pós-traumático (esquiva de situações relacionadas ao trauma); "
            "transtorno de ansiedade de separação (medo de separação de figuras de apego)."
        ),
        "icd11_exclusions": (
            "Panic disorder (6B01); Specific phobia (6B03); Social anxiety disorder (6B04); "
            "Separation anxiety disorder (6B05)."
        ),
        "icd11_differentials": (
            "Panic disorder (6B01); Specific phobia (6B03); Social anxiety disorder (6B04); "
            "Generalized anxiety disorder (6B00); Body dysmorphic disorder (6B21)."
        ),
    },
    "Transtorno por Uso de Substâncias": {
        "criteria": (
            "A. Padrão problemático de uso de substância levando a prejuízo ou sofrimento "
            "clinicamente significativo, manifestado por 2+ dos seguintes no período de 12 meses:\n"
            "1. Uso em quantidades maiores ou por mais tempo que o pretendido.\n"
            "2. Desejo persistente ou esforços malsucedidos para reduzir/controlar o uso.\n"
            "3. Grande quantidade de tempo gasto obtendo, usando ou se recuperando da substância.\n"
            "4. Fissura (craving) ou desejo intenso pela substância.\n"
            "5. Uso recorrente resultando em falha em cumprir obrigações no trabalho/escola/casa.\n"
            "6. Uso continuado apesar de problemas sociais ou interpessoais persistentes.\n"
            "7. Abandono ou redução de atividades sociais/ocupacionais/recreativas.\n"
            "8. Uso recorrente em situações de risco físico.\n"
            "9. Uso continuado apesar de problema físico ou psicológico persistente.\n"
            "10. Tolerância (necessidade de doses maiores ou efeito diminuído).\n"
            "11. Abstinência (síndrome característica ou uso para aliviar/evitar abstinência).\n"
            "Especificadores: gravidade (leve 2-3, moderado 4-5, grave 6+), remissão precoce/"
            "sustentada, ambiente controlado, manutenção."
        ),
        "exclusions": (
            "Uso não problemático de substância; efeitos colaterais de medicação prescrita; "
            "transtorno bipolar (comportamento de risco durante mania); transtorno de "
            "personalidade antissocial (uso instrumental); transtorno psicótico induzido "
            "por substância (se limitado à intoxicação/abstinência)."
        ),
        "differentials": (
            "Transtorno bipolar (episódio maníaco com abuso de substância secundário); "
            "transtorno de personalidade antissocial (uso de substância como parte de padrão "
            "mais amplo de comportamento); transtorno de ansiedade social (automedicação com "
            "álcool); transtorno de estresse pós-traumático (automedicação); transtorno de "
            "déficit de atenção/hiperatividade (impulsividade e busca de novidades); "
            "transtorno psicótico primário (alucinações/delírios independentes do uso)."
        ),
        "icd11_exclusions": (
            "Hazardous substance use (QE10); Substance intoxication (6C4E); "
            "Bipolar type I disorder (6A60) - behavioral disinhibition."
        ),
        "icd11_differentials": (
            "Bipolar disorders (6A60-6A61); Schizophrenia (6A20); "
            "PTSD (6B40); ADHD (6A05); Antisocial personality disorder (6D11)."
        ),
    },
    "Anorexia Nervosa": {
        "criteria": (
            "A. Restrição da ingestão calórica em relação às necessidades, levando a peso corporal "
            "significativamente baixo no contexto da idade, sexo, trajetória de desenvolvimento "
            "e saúde física.\n"
            "B. Medo intenso de ganhar peso ou de engordar, ou comportamento persistente que "
            "interfere no ganho de peso, mesmo com peso baixo.\n"
            "C. Perturbação na forma como o peso ou a forma corporal são vivenciados, influência "
            "indevida do peso/forma na autoavaliação, ou falta de reconhecimento da gravidade "
            "do baixo peso.\n"
            "Especificadores: tipo restritivo vs. purgativo/compulsão alimentar; em remissão; "
            "gravidade (IMC)."
        ),
        "exclusions": (
            "Bulimia nervosa (episódios de compulsão + purgação com peso normal ou acima); "
            "transtorno de compulsão alimentar (sem comportamento compensatório); condição "
            "médica causando perda de peso (neoplasia, doença inflamatória intestinal, diabetes "
            "não controlado); depressão maior com perda de apetite (sem distorção de imagem); "
            "transtorno dismórfico corporal (foco em parte específica do corpo)."
        ),
        "differentials": (
            "Bulimia nervosa (peso normalmente na faixa normal ou acima, com compulsões e "
            "comportamentos compensatórios regulares); transtorno de compulsão alimentar "
            "(sem restrição significativa ou baixo peso); depressão maior (perda de peso "
            "sem medo de engordar ou distorção de imagem); condição médica geral (perda de "
            "peso involuntária); transtorno de ansiedade social (evitação de comer em público); "
            "transtorno do espectro autista (restrição alimentar por seletividade sensorial); "
            "transtorno factício; transtorno dismórfico corporal."
        ),
        "icd11_exclusions": (
            "Bulimia nervosa (6B81); Binge-eating disorder (6B82); "
            "Depressive disorders (6A70-6A71)."
        ),
        "icd11_differentials": (
            "Bulimia nervosa (6B81); Binge-eating disorder (6B82); "
            "Major depressive disorder (6A70-6A71); Body dysmorphic disorder (6B21); "
            "Social anxiety disorder (6B04)."
        ),
    },
    "Bulimia Nervosa": {
        "criteria": (
            "A. Episódios recorrentes de compulsão alimentar caracterizados por:\n"
            "1. Ingestão em um período de 2 horas de grandes quantidades de alimento.\n"
            "2. Sensação de perda de controle sobre a ingestão.\n"
            "B. Comportamentos compensatórios recorrentes e inadequados: vômito autoinduzido, "
            "uso de laxantes/diuréticos, jejum, exercício excessivo.\n"
            "C. A compulsão e os comportamentos compensatórios ocorrem em média 1+ vez/semana "
            "por 3 meses.\n"
            "D. A autoavaliação é indevidamente influenciada pelo peso e forma corporal.\n"
            "E. A perturbação não ocorre exclusivamente durante episódios de anorexia nervosa."
        ),
        "exclusions": (
            "Anorexia nervosa tipo purgativo (peso significativamente baixo); transtorno de "
            "compulsão alimentar (sem comportamentos compensatórios regulares); síndrome de "
            "Kleine-Levin; depressão maior com hiperfagia (sem comportamentos compensatórios); "
            "condição neurológica (lesão hipotalâmica)."
        ),
        "differentials": (
            "Anorexia nervosa tipo purgativo (baixo peso IMC < 18.5); transtorno de compulsão "
            "alimentar (sem comportamentos compensatórios); transtorno depressivo maior "
            "(hiperfagia sem preocupação com peso/forma); transtorno de personalidade "
            "borderline (comportamento impulsivo alimentar como parte de padrão mais amplo); "
            "síndrome do comer noturno."
        ),
        "icd11_exclusions": (
            "Anorexia nervosa (6B80); Binge-eating disorder (6B82); "
            "Depressive disorders (6A70-6A71)."
        ),
        "icd11_differentials": (
            "Anorexia nervosa (6B80); Binge-eating disorder (6B82); "
            "Major depressive disorder (6A70-6A71); Borderline personality disorder (6D11)."
        ),
    },
    "Transtorno de Compulsão Alimentar": {
        "criteria": (
            "A. Episódios recorrentes de compulsão alimentar (como na bulimia).\n"
            "B. Os episódios estão associados a 3+:\n"
            "1. Comer muito mais rapidamente que o normal.\n"
            "2. Comer até sentir-se desconfortavelmente cheio.\n"
            "3. Comer grandes quantidades sem fome física.\n"
            "4. Comer sozinho por vergonha da quantidade.\n"
            "5. Sentir-se desgostoso, deprimido ou culpado após comer.\n"
            "C. Sofrimento acentuado em relação à compulsão.\n"
            "D. Compulsões ocorrem 1+ vez/semana por 3 meses.\n"
            "E. Sem comportamentos compensatórios regulares (vs. bulimia)."
        ),
        "exclusions": (
            "Bulimia nervosa (comportamentos compensatórios regulares); anorexia nervosa "
            "(restrição significativa e baixo peso); compulsão alimentar devido a condição "
            "médica (lesão hipotalâmica, síndrome de Prader-Willi); depressão atípica; "
            "transtorno por uso de substância."
        ),
        "differentials": (
            "Bulimia nervosa (mesma compulsão + comportamentos compensatórios); obesidade "
            "sem compulsão (comer em excesso sem episódios discretos de perda de controle); "
            "depressão maior (hiperfagia sem episódios de compulsão); transtorno de ansiedade "
            "(comer emocional sem episódios discretos); síndrome do comer noturno."
        ),
        "icd11_exclusions": (
            "Bulimia nervosa (6B81); Anorexia nervosa (6B80); "
            "Depressive disorders (6A70-6A71); Prader-Willi syndrome (LD90)."
        ),
        "icd11_differentials": (
            "Bulimia nervosa (6B81); Anorexia nervosa (6B80); "
            "Major depressive disorder (6A70-6A71); Generalized anxiety disorder (6B00)."
        ),
    },
    "Transtorno de Insônia": {
        "criteria": (
            "A. Queixa predominante de insatisfação com a quantidade ou qualidade do sono, "
            "com 1+ dos seguintes:\n"
            "1. Dificuldade para iniciar o sono.\n"
            "2. Dificuldade para manter o sono (despertares frequentes ou dificuldade em "
            "voltar a dormir).\n"
            "3. Despertar precoce com incapacidade de retomar o sono.\n"
            "B. Causa sofrimento ou prejuízo clinicamente significativo.\n"
            "C. Ocorre pelo menos 3 noites por semana.\n"
            "D. Presente por pelo menos 3 meses.\n"
            "E. Apesar da oportunidade adequada para dormir.\n"
            "F. Não é melhor explicado por outro transtorno do sono (narcolepsia, apneia, "
            "transtorno do ritmo circadiano, parassonia).\n"
            "G. Não é atribuível a substância ou condição médica.\n"
            "H. Transtornos mentais coexistentes não explicam adequadamente a insônia."
        ),
        "exclusions": (
            "Privação de sono voluntária; apneia obstrutiva do sono; síndrome das pernas "
            "inquietas; narcolepsia; transtorno do ritmo circadiano; insônia devido a "
            "substância (cafeína, estimulantes, álcool); condição médica (dor crônica, "
            "hipertireoidismo, asma noturna)."
        ),
        "differentials": (
            "Apneia obstrutiva do sono (ronco, pausas respiratórias, sonolência diurna); "
            "síndrome das pernas inquietas (urgência de mover as pernas à noite); narcolepsia "
            "(ataques de sono, cataplexia); transtorno do ritmo circadiano (fase atrasada/"
            "avançada); depressão maior (despertar precoce característico); transtorno de "
            "ansiedade generalizada (dificuldade em conciliar sono por preocupação); "
            "transtorno por uso de substância; condição clínica (hipertireoidismo, refluxo)."
        ),
        "icd11_exclusions": (
            "Obstructive sleep apnoea (7A41); Restless legs syndrome (7A80); "
            "Circadian rhythm sleep-wake disorder (7A60); "
            "Substance-induced sleep disorder (7A0Y)."
        ),
        "icd11_differentials": (
            "Generalized anxiety disorder (6B00); Major depressive disorder (6A70-6A71); "
            "Obstructive sleep apnoea (7A41); Restless legs syndrome (7A80); "
            "Circadian rhythm sleep-wake disorder (7A60)."
        ),
    },
    "Esquizofrenia / Transtorno Psicótico": {
        "criteria": (
            "A. 2+ dos seguintes sintomas por 1 mês (pelo menos 1 deve ser 1-3):\n"
            "1. Delírios.\n"
            "2. Alucinações.\n"
            "3. Discurso desorganizado.\n"
            "4. Comportamento grosseiramente desorganizado ou catatônico.\n"
            "5. Sintomas negativos (embotamento afetivo, alogia, avolição).\n"
            "B. Disfunção social/laboral por parte significativa do tempo desde o início.\n"
            "C. Sinais contínuos persistem por 6+ meses (incluindo 1 mês de sintomas ativos).\n"
            "D. Excluídos: transtorno esquizoafetivo e transtorno de humor com características psicóticas.\n"
            "E. Não atribuível a substância ou condição médica.\n"
            "F. Se história de autismo ou TDC, o diagnóstico adicional de esquizofrenia é feito "
            "apenas se delírios ou alucinações proeminentes estiverem presentes por 1+ mês."
        ),
        "exclusions": (
            "Transtorno esquizoafetivo (episódios de humor concomitantes com sintomas psicóticos); "
            "transtorno bipolar com características psicóticas (episódio de humor proeminente); "
            "depressão maior com características psicóticas; transtorno delirante (delírios sem "
            "outros sintomas); transtorno psicótico breve (1-30 dias); transtorno esquizofreniforme "
            "(1-6 meses); TEPT com flashbacks psicóticos; transtorno factício; transtorno de "
            "personalidade esquizotípica."
        ),
        "differentials": (
            "Transtorno esquizoafetivo (episódios de humor proeminentes durante a maior parte "
            "da doença); transtorno bipolar (episódios de humor distintos com psicose apenas "
            "durante mania/depressão); depressão maior com psicose; transtorno delirante "
            "(delírios não-bizarros, sem alucinações proeminentes ou desorganização); "
            "transtorno do espectro autista (déficits sociais sem delírios/alucinações); "
            "transtorno obsessivo-compulsivo (obsessões com insight pobre); transtorno por "
            "uso de substância (psicose induzida); transtorno de personalidade esquizotípica "
            "(crenças estranhas sem psicose franca)."
        ),
        "icd11_exclusions": (
            "Schizoaffective disorder (6A21); Acute and transient psychotic disorder (6A23); "
            "Delusional disorder (6A24); Bipolar type I disorder (6A60); "
            "Substance-induced psychotic disorder (6C4E)."
        ),
        "icd11_differentials": (
            "Schizoaffective disorder (6A21); Acute and transient psychotic disorder (6A23); "
            "Delusional disorder (6A24); Bipolar type I disorder (6A60); "
            "Depressive disorders with psychotic symptoms (6A70-6A71); "
            "Substance-induced psychotic disorder (6C4E); Autism spectrum disorder (6A02)."
        ),
    },
    "Transtorno de Sintomas Somáticos": {
        "criteria": (
            "A. Um ou mais sintomas somáticos que causam sofrimento ou resultam em prejuízo "
            "significativo na vida diária.\n"
            "B. Pensamentos, sentimentos ou comportamentos excessivos relacionados aos sintomas "
            "somáticos ou à preocupação com a saúde, manifestados por 1+:\n"
            "1. Pensamentos desproporcionais e persistentes sobre a gravidade dos sintomas.\n"
            "2. Ansiedade persistentemente elevada acerca da saúde ou dos sintomas.\n"
            "3. Tempo e energia excessivos dedicados aos sintomas ou preocupações de saúde.\n"
            "C. Embora qualquer sintoma somático possa não estar continuamente presente, o "
            "estado de ser sintomático é persistente (tipicamente > 6 meses).\n"
            "Especificador: com dor predominante."
        ),
        "exclusions": (
            "Condição médica geral confirmada com sintomas proporcionais; transtorno de "
            "ansiedade de doença (preocupação com ter/desenvolver doença, sem sintomas somáticos "
            "proeminentes); transtorno de conversão (sintomas neurológicos funcionais); "
            "transtorno factício (falsificação de sintomas); simulação (incentivo externo); "
            "hipocondria (transtorno de ansiedade de doença no DSM-5)."
        ),
        "differentials": (
            "Transtorno de ansiedade de doença (preocupação com ter ou adquirir doença, "
            "sintomas somáticos ausentes ou leves); transtorno de conversão (sintomas "
            "neurológicos funcionais - paralisia, crises, cegueira); transtorno factício "
            "(falsificação consciente de sintomas); simulação (motivação externa); depressão "
            "maior (sintomas somáticos como parte de quadro depressivo); transtorno de pânico "
            "(sintomas somáticos paroxísticos); transtorno de ansiedade generalizada (tensão "
            "muscular, fadiga, sem foco em doença)."
        ),
        "icd11_exclusions": (
            "Health anxiety disorder (6B23); Bodily distress disorder (6C20); "
            "Dissociative neurological symptom disorder (6B60); Factitious disorder (6D50)."
        ),
        "icd11_differentials": (
            "Health anxiety disorder (6B23); Bodily distress disorder (6C20); "
            "Panic disorder (6B01); Generalized anxiety disorder (6B00); "
            "Depressive disorders (6A70-6A71); Factitious disorder (6D50)."
        ),
    },
    "Transtorno do Espectro Autista": {
        "criteria": (
            "A. Déficits persistentes na comunicação social e interação social em múltiplos "
            "contextos (3/3 necessários):\n"
            "1. Déficit na reciprocidade socioemocional (abordagem social anormal, dificuldade "
            "em manter conversação bidirecional, redução de interesses/emoções compartilhados).\n"
            "2. Déficit em comportamentos comunicativos não verbais (contato visual, linguagem "
            "corporal, expressões faciais, gestos).\n"
            "3. Déficit em desenvolver, manter e compreender relacionamentos (dificuldade com "
            "comportamento apropriado ao contexto, fazer amigos, interesse por pares).\n"
            "B. Padrões restritos e repetitivos de comportamento, interesses ou atividades (2/4):\n"
            "1. Movimentos motores, uso de objetos ou fala estereotipados/repetitivos.\n"
            "2. Insistência nas mesmas coisas, adesão inflexível a rotinas ou rituais.\n"
            "3. Interesses altamente restritos e fixos, anormais em intensidade ou foco.\n"
            "4. Hiper ou hiporreatividade a estímulos sensoriais.\n"
            "C. Sintomas presentes no período inicial do desenvolvimento.\n"
            "D. Causam prejuízo clinicamente significativo no funcionamento.\n"
            "E. Não melhor explicados por deficiência intelectual (embora comorbida)."
        ),
        "exclusions": (
            "Transtorno de déficit de atenção/hiperatividade (déficits sociais secundários à "
            "desatenção/impulsividade); transtorno de ansiedade social (medo de avaliação "
            "negativa, habilidades sociais intactas); mutismo seletivo; transtorno do espectro "
            "autista pode ser diagnosticado com TDAH; deficiência intelectual sem TEA; "
            "transtorno de linguagem; transtorno de personalidade esquiva ou esquizotípica; "
            "esquizofrenia (início na infância é raro)."
        ),
        "differentials": (
            "TDAH (desatenção/hiperatividade sem déficits qualitativos na comunicação social); "
            "transtorno de ansiedade social (medo de avaliação negativa vs. déficit de "
            "habilidades sociais); deficiência intelectual isolada (sem déficits proporcionais "
            "de comunicação social); transtorno de linguagem (déficit específico de linguagem "
            "com habilidades sociais preservadas); transtorno de personalidade esquizotípica "
            "(crenças estranhas, ideação paranoide); mutismo seletivo; síndrome de Rett; "
            "esquizofrenia infantil (alucinações/delírios proeminentes)."
        ),
        "icd11_exclusions": (
            "ADHD (6A05); Social anxiety disorder (6B04); Selective mutism (6B06); "
            "Language disorders (6A01); Childhood-onset fluency disorder (6A01)."
        ),
        "icd11_differentials": (
            "ADHD (6A05); Social anxiety disorder (6B04); Selective mutism (6B06); "
            "Language disorders (MA80); Intellectual developmental disorder (6A00); "
            "Schizophrenia (6A20); Obsessive-compulsive disorder (6B20); "
            "Rett syndrome (LD90)."
        ),
    },
    "Transtorno de Déficit de Atenção/Hiperatividade": {
        "criteria": (
            "A. Padrão persistente de desatenção e/ou hiperatividade-impulsividade que interfere "
            "no funcionamento ou desenvolvimento, com 6+ sintomas (5+ se 17+ anos) por 6+ meses.\n"
            "Desatenção:\n"
            "a. Frequentemente não presta atenção a detalhes ou comete erros por descuido.\n"
            "b. Dificuldade em sustentar a atenção em tarefas ou brincadeiras.\n"
            "c. Parece não escutar quando abordado diretamente.\n"
            "d. Não segue instruções e não termina tarefas.\n"
            "e. Dificuldade em organizar tarefas e atividades.\n"
            "f. Evita ou reluta em envolver-se em tarefas que exijam esforço mental Sustentado.\n"
            "g. Perde objetos necessários para tarefas ou atividades.\n"
            "h. Facilmente distraído por estímulos externos.\n"
            "i. Esquecimento em atividades cotidianas.\n"
            "Hiperatividade-Impulsividade:\n"
            "a. Agita ou batuca mãos/pés, ou remexe-se na cadeira.\n"
            "b. Levanta-se da cadeira em situações em que se espera que fique sentado.\n"
            "c. Corre ou sobe em coisas em situações inapropriadas (em adolescentes/adultos, "
            "inquietação subjetiva).\n"
            "d. Incapacidade de brincar ou envolver-se em atividades de lazer calmamente.\n"
            "e. 'Não para' ou age como se estivesse 'movido a motor'.\n"
            "f. Fala excessivamente.\n"
            "g. Responde antes de a pergunta ser concluída.\n"
            "h. Dificuldade em esperar sua vez.\n"
            "i. Interrompe ou se intromete nas conversas/atividades dos outros.\n"
            "B. Vários sintomas presentes antes dos 12 anos.\n"
            "C. Vários sintomas presentes em 2+ ambientes.\n"
            "D. Evidência clara de interferência no funcionamento social/acadêmico/ocupacional.\n"
            "E. Não ocorre exclusivamente durante esquizofrenia, transtorno psicótico ou de humor."
        ),
        "exclusions": (
            "Transtorno do espectro autista (déficits sociais qualitativos vs. hiperatividade); "
            "transtorno bipolar (episódios de humor distintos); transtorno de ansiedade "
            "(inquietação por ansiedade); depressão (diminuição da concentração); "
            "transtorno de personalidade borderline (instabilidade afetiva); "
            "condição médica (hipertireoidismo, privação de sono)."
        ),
        "differentials": (
            "Transtorno do espectro autista (deficits qualitativos na comunicação social, "
            "interesses restritos); transtorno bipolar (episódios distintos de mania/hipomania); "
            "transtorno de ansiedade generalizada (inquietação por preocupação); depressão "
            "maior (déficit de concentração secundário ao humor deprimido); transtorno "
            "desafiador opositivo (comportamento opositivo vs. desatenção); transtorno de "
            "personalidade borderline (instabilidade emocional relacional); TDAH e TEA "
            "frequentemente co-ocorrem e podem ser diagnosticados conjuntamente."
        ),
        "icd11_exclusions": (
            "Autism spectrum disorder (6A02); Bipolar disorders (6A60-6A61); "
            "Generalized anxiety disorder (6B00); Depressive disorders (6A70-6A71)."
        ),
        "icd11_differentials": (
            "Autism spectrum disorder (6A02); Bipolar type I/II disorder (6A60-6A61); "
            "Generalized anxiety disorder (6B00); Depressive disorders (6A70-6A71); "
            "Oppositional defiant disorder (6C90); Specific learning disorder (6A03)."
        ),
    },
}


def seed():
    db = SessionLocal()
    try:
        disorders = {d.disorder_name: d for d in db.query(Disorder).all()}
        who = db.query(ClassificationAuthority).filter_by(short_name="WHO").first()
        apa = db.query(ClassificationAuthority).filter_by(short_name="APA").first()

        if not who or not apa:
            print("ERROR: Classification authorities not found. Run db/seed.py first.")
            return

        criteria_count = 0
        icd11_count = 0
        exclusion_count = 0
        differential_count = 0

        for disorder_name, data in DSM5TR_CRITERIA.items():
            disorder = disorders.get(disorder_name)
            if not disorder:
                print(f"  WARNING: Disorder '{disorder_name}' not found")
                continue

            # Update Disorder with DSM-5-TR criteria + exclusions + differentials
            disorder.dsm_criteria = data["criteria"]
            disorder.dsm_exclusions = data["exclusions"]
            disorder.dsm_differentials = data["differentials"]
            disorder.icd11_exclusions = data.get("icd11_exclusions", "")
            disorder.icd11_differentials = data.get("icd11_differentials", "")
            criteria_count += 1

            # Link existing ICD-11 codes to WHO authority
            icd11_records = db.query(ICD11Code).filter_by(disorder_id=disorder.disorder_id).all()
            for icd in icd11_records:
                if icd.authority_id is None:
                    icd.authority_id = who.authority_id
                    icd11_count += 1

        db.commit()
        print(f"OK - {criteria_count} disorders updated with DSM-5-TR criteria")
        print(f"OK - {icd11_count} ICD-11 codes linked to WHO authority")

        # Seed structured ICD-11 exclusions and differentials from the DSM5TR data
        for disorder_name, data in DSM5TR_CRITERIA.items():
            disorder = disorders.get(disorder_name)
            if not disorder:
                continue

            icd_records = db.query(ICD11Code).filter_by(disorder_id=disorder.disorder_id).all()
            for icd in icd_records:
                # Parse and seed exclusions
                excl_text = data.get("icd11_exclusions", "")
                if excl_text:
                    for excl_item in excl_text.split(";"):
                        excl_item = excl_item.strip()
                        if excl_item:
                            existing = db.query(ICD11Exclusion).filter_by(
                                code_id=icd.code_id, excluded_title=excl_item
                            ).first()
                            if not existing:
                                db.add(ICD11Exclusion(
                                    code_id=icd.code_id,
                                    excluded_title=excl_item[:500] if len(excl_item) > 500 else excl_item,
                                    reason="Exclusion per ICD-11 CDDR",
                                ))
                                exclusion_count += 1

                # Parse and seed differentials
                diff_text = data.get("icd11_differentials", "")
                if diff_text:
                    for diff_item in diff_text.split(";"):
                        diff_item = diff_item.strip()
                        if diff_item:
                            existing = db.query(ICD11Differential).filter_by(
                                code_id=icd.code_id, differential_title=diff_item
                            ).first()
                            if not existing:
                                db.add(ICD11Differential(
                                    code_id=icd.code_id,
                                    differential_title=diff_item[:500] if len(diff_item) > 500 else diff_item,
                                    distinguishing_features="See ICD-11 CDDR for full differential guidance.",
                                ))
                                differential_count += 1

        db.commit()
        print(f"OK - {exclusion_count} ICD-11 exclusions seeded")
        print(f"OK - {differential_count} ICD-11 differentials seeded")
        print("\nSeed de dados diagnósticos completo!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
