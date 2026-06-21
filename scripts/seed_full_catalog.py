"""
⚠️  WARNING: DIAGNOSIS RELATIONSHIPS AND SYMPTOM-DISORDER MAPPINGS IN THIS SCRIPT
⚠️  ARE PROCEDURALLY GENERATED BASED ON DSM-5-TR AND ICD-11 AUTHORITY DATA.
⚠️  CLINICAL CRITERIA TEXT IS FROM DSM-5-TR (APA, 2022). PATIENT-LEVEL DATA IS
⚠️  SYNTHETIC — DO NOT USE WITH REAL PATIENTS.

Seed DSM-5-TR criteria, symptoms, relationships, and ICD-11 data for ALL disorders.

Activates the full ~192-disorder catalog with diagnostic criteria text,
ICD-11 exclusions/differentials, symptom mappings, diagnosis relationships,
and scale mappings.

Run after db/seed.py, seed_icd11.py, seed_scales_groups.py.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.base import (
    Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship,
    ICD11Code, ICD11Exclusion, ICD11Differential, ClassificationAuthority,
)
from scripts.dsm5tr_data import DSM5TR_DISORDERS, CORE_DISORDER_NAMES
from scripts.reference_symptom_data import REFERENCE_SYMPTOM_MAP
from scripts.seed_clinical_data import EN_TO_PT_SYMPTOM


# ── DSM-5-TR CRITERIA TEXT FOR ALL DISORDERS ──

# Compact format: (criteria, exclusions, differentials, icd11_exclusions, icd11_differentials)
# For existing core disorders, use empty dict (already seeded by seed_diagnostic_data.py)
DSM5TR_ALL = {
    # ═══ CHAPTER 1: Transtornos do Neurodesenvolvimento ═══
    "Deficiência Intelectual": (
        "A. Déficits em funções intelectuais (raciocínio, solução de problemas, planejamento, "
        "pensamento abstrato, julgamento, aprendizado acadêmico) confirmados por avaliação clínica "
        "e testes de inteligência padronizados.\n"
        "B. Déficits no funcionamento adaptativo resultando em falha em atingir padrões de "
        "independência pessoal e responsabilidade social.\n"
        "C. Início no período do desenvolvimento.",
        "Transtorno do espectro autista (prejuízo social desproporcional); "
        "transtorno específico da aprendizagem (prejuízo circunscrito); "
        "demência (declínio de nível anterior); condição neurológica progressiva.",
        "TEA (interesses restritos, déficits sociais); transtorno específico da aprendizagem "
        "(função específica preservada); transtorno de comunicação; mutismo seletivo; "
        "privação psicossocial grave.",
        "Autism spectrum disorder (6A02); Specific learning disorder (6A03); Dementia.",
        "Autism spectrum disorder (6A02); Specific learning disorder (6A03); "
        "Communication disorders (6A01)."
    ),
    "Atraso Global do Desenvolvimento": (
        "Diagnóstico reservado para crianças menores de 5 anos quando o nível clínico de gravidade "
        "não pode ser avaliado de forma confiável. Caracterizado por atraso significativo em "
        "múltiplas áreas do desenvolvimento: motora grossa/fina, linguagem, cognição, habilidades "
        "sociais e atividades da vida diária.",
        "Deficiência intelectual específica (após 5 anos pode ser especificada); "
        "atraso devido a privação ambiental; condição neurológica progressiva.",
        "TEA com atraso global; transtorno específico de linguagem; paralisia cerebral; "
        "síndromes genéticas.",
        "Autism spectrum disorder (6A02); Cerebral palsy (8D20).",
        "Autism spectrum disorder (6A02); Specific language impairment (6A01); "
        "Cerebral palsy (8D20)."
    ),
    "Transtorno da Linguagem": (
        "A. Dificuldades persistentes na aquisição e uso da linguagem em todas as modalidades "
        "(falada, escrita, linguagem de sinais) devido a déficits na compreensão ou produção.\n"
        "B. Capacidades linguísticas substancialmente abaixo do esperado para a idade.\n"
        "C. Início no período inicial do desenvolvimento.\n"
        "D. Não atribuível a deficiência auditiva, deficiência intelectual ou condição neurológica.",
        "Deficiência auditiva; deficiência intelectual; mutismo seletivo; "
        "TEA (prejuízo social mais amplo); síndrome de Landau-Kleffner.",
        "Transtorno fonológico (apenas produção de sons); TEA; deficiência intelectual "
        "(prejuízo global); mutismo seletivo (fala ausente em contextos específicos); "
        "afasia adquirida; transtorno da comunicação social.",
        "Autism spectrum disorder (6A02); Selective mutism (6B06); "
        "Hearing loss (AB50).",
        "Autism spectrum disorder (6A02); Intellectual developmental disorder (6A00); "
        "Selective mutism (6B06)."
    ),
    "Transtorno Fonológico": (
        "A. Dificuldade persistente na produção de sons da fala que interfere na inteligibilidade "
        "ou impede a comunicação verbal.\n"
        "B. Causa prejuízo na comunicação social e no desempenho acadêmico/ocupacional.\n"
        "C. Início no período inicial do desenvolvimento.\n"
        "D. Não atribuível a condições congênitas, deficiência auditiva ou neurológica.",
        "Transtorno da linguagem (déficit mais amplo); disartria; apraxia de fala na infância; "
        "deficiência auditiva; fissura palatina.",
        "Transtorno da linguagem (compreensão/prejuízo mais amplo); TEA; "
        "apraxia de fala na infância; transtorno de fluência (gagueira).",
        "Language disorder (6A01); Autism spectrum disorder (6A02); "
        "Hearing loss (AB50).",
        "Language disorder (6A01); Speech apraxia; "
        "Autism spectrum disorder (6A02)."
    ),
    "Transtorno da Fluência com Início na Infância (Gagueira)": (
        "A. Alterações na fluência e no padrão temporal da fala inadequadas para a idade.\n"
        "B. Ocorrência frequente de repetições de sons/sílabas, prolongamentos, bloqueios, "
        "palavras substituídas para evitar momentos de gagueira.\n"
        "C. Causa ansiedade ou prejuízo na comunicação social.\n"
        "D. Início no período inicial do desenvolvimento.",
        "Gagueira neurogênica (lesão neurológica); gagueira psicogênica; "
        "disfluência normal do desenvolvimento; TOC (rituais de fala).",
        "Disfluência normal do desenvolvimento (sem ansiedade ou prejuízo); "
        "gagueira neurogênica (relação temporal com lesão); TOC.",
        "Cluttering (F80.81); Tic disorders (8A05); Social anxiety disorder (6B04).",
        "Cluttering; Social anxiety disorder (6B04); Tic disorders (8A05)."
    ),
    "Transtorno da Comunicação Social (Pragmática)": (
        "A. Dificuldades persistentes no uso social da comunicação verbal e não verbal em: "
        "saudações, alternância de turnos, adequação ao contexto, inferência, compreensão de "
        "linguagem não literal.\n"
        "B. Causa prejuízo na comunicação e relacionamentos.\n"
        "C. Início no período inicial do desenvolvimento.\n"
        "D. Não é melhor explicado por TEA, deficiência intelectual ou atraso global.",
        "TEA (presença de interesses restritos e comportamentos repetitivos); "
        "deficiência intelectual; transtorno da linguagem.",
        "TEA (presença dos Critérios B); transtorno da linguagem; "
        "TDAH (fala impulsiva sem déficit pragmático); transtorno de ansiedade social.",
        "Autism spectrum disorder (6A02); Language disorder (6A01); "
        "ADHD (6A05).",
        "Autism spectrum disorder (6A02); Language disorder (6A01); "
        "Social anxiety disorder (6B04)."
    ),
    "Transtorno Específico da Aprendizagem": (
        "A. Dificuldades na aprendizagem e uso de habilidades acadêmicas (leitura, escrita, "
        "matemática) por 6+ meses apesar de intervenções.\n"
        "B. Habilidades acadêmicas substancialmente abaixo do esperado para a idade.\n"
        "C. Início nos anos escolares.\n"
        "D. Não atribuível a deficiência intelectual, neurológica, visual/auditiva ou "
        "instrução inadequada.",
        "Deficiência intelectual (prejuízo global); condição neurológica; "
        "privação educacional; transtorno de comunicação; TDAH (desatenção secundária).",
        "Deficiência intelectual (avaliação de QI global); TDAH (desatenção primária); "
        "transtorno de ansiedade (desempenho escolar prejudicado); "
        "transtorno da linguagem; discalculia secundária.",
        "Intellectual developmental disorder (6A00); ADHD (6A05); "
        "Communication disorders (6A01).",
        "Intellectual developmental disorder (6A00); ADHD (6A05); "
        "Anxiety disorders (6B00-6B0Z)."
    ),
    "Transtorno do Desenvolvimento da Coordenação": (
        "A. Aquisição e execução de habilidades motoras coordenadas substancialmente abaixo do "
        "esperado para a idade cronológica.\n"
        "B. Causa prejuízo no desempenho de atividades da vida diária.\n"
        "C. Início no período inicial do desenvolvimento.\n"
        "D. Não atribuível a condição neurológica, deficiência intelectual ou visual.",
        "Condição neurológica (paralisia cerebral, distrofia muscular); "
        "deficiência intelectual; TDAH (impulsividade motora); "
        "transtorno do movimento estereotipado.",
        "TDAH (inquietação motora sem déficit de coordenação); "
        "transtorno do espectro autista (dispraxia associada); "
        "paralisia cerebral (sinais neurológicos focais).",
        "Cerebral palsy (8D20); ADHD (6A05); Autism spectrum disorder (6A02).",
        "ADHD (6A05); Autism spectrum disorder (6A02); "
        "Cerebral palsy (8D20); Muscular dystrophy (8C70)."
    ),
    "Transtorno do Movimento Estereotipado": (
        "A. Comportamento motor repetitivo, aparentemente impulsivo e não funcional.\n"
        "B. Interfere nas atividades normais ou causa lesão corporal.\n"
        "C. Início no período inicial do desenvolvimento.\n"
        "D. Não atribuível a efeitos de substância ou condição neurológica.\n"
        "E. Não é melhor explicado por TEA ou tricotilomania.",
        "TEA (estereotipias + déficits sociais); TOC (compulsões com função de neutralizar); "
        "transtorno de tique; discinesia tardia; tricotilomania.",
        "TEA (estereotipias + critérios A e B do TEA); TOC; "
        "transtorno de Tourette; discinesia induzida por medicamento.",
        "Autism spectrum disorder (6A02); Tourette disorder (8A05); "
        "Obsessive-compulsive disorder (6B20).",
        "Autism spectrum disorder (6A02); Tic disorders (8A05); "
        "Obsessive-compulsive disorder (6B20)."
    ),
    "Transtorno de Tourette": (
        "A. Múltiplos tiques motores e um ou mais tiques vocais presentes por 1+ ano.\n"
        "B. Início antes dos 18 anos.\n"
        "C. Não atribuível a substância ou condição médica.",
        "Transtorno de tique motor/vocal crônico (apenas motores OU vocais, não ambos); "
        "movimentos estereotipados (sem natureza de tique); TOC (compulsões conscientes); "
        "discinesia tardia.",
        "Transtorno de tique motor/vocal crônico; transtorno de tique transitório; "
        "TOC; coreia de Sydenham; transtorno do movimento estereotipado.",
        "Chronic motor or vocal tic disorder (8A05); Transient tic disorder (8A05); "
        "Obsessive-compulsive disorder (6B20).",
        "Chronic motor or vocal tic disorder (8A05); OCD (6B20); "
        "ADHD (6A05); Stereotypic movement disorder (6A06)."
    ),
    "Transtorno de Tique Motor ou Vocal Crônico": (
        "A. Tiques motores ou vocais únicos ou múltiplos (mas não ambos) presentes por 1+ ano.\n"
        "B. Início antes dos 18 anos.\n"
        "C. Não atribuível a substância ou condição médica.\n"
        "D. Critérios para Tourette nunca foram preenchidos.",
        "Transtorno de Tourette (tanto motores quanto vocais); "
        "transtorno de tique transitório (<1 ano); "
        "movimentos estereotipados; discinesia tardia.",
        "Transtorno de Tourette; transtorno de tique transitório; "
        "TOC; transtorno do movimento estereotipado.",
        "Tourette disorder (8A05); Transient tic disorder (8A05); "
        "Stereotypic movement disorder (6A06).",
        "Tourette disorder (8A05); Transient tic disorder (8A05); "
        "OCD (6B20)."
    ),
    "Transtorno de Tique Transitório": (
        "A. Tiques motores e/ou vocais.\n"
        "B. Presentes há menos de 1 ano.\n"
        "C. Início antes dos 18 anos.\n"
        "D. Não atribuível a substância ou condição médica.\n"
        "E. Critérios para Tourette ou tique crônico nunca foram preenchidos.",
        "Transtorno de Tourette; transtorno de tique crônico; "
        "movimentos estereotipados; efeito colateral medicamentoso.",
        "Tique fisiológico transitório (estresse, fadiga); Tourette; "
        "tique crônico; movimentos estereotipados.",
        "Tourette disorder (8A05); Chronic tic disorder (8A05).",
        "Tourette disorder (8A05); Chronic tic disorder (8A05); "
        "Stereotypic movement disorder (6A06)."
    ),

"Deficiência Intelectual Leve": (
        'A. Preenche os critérios diagnósticos para deficiência intelectual.\nB. A gravidade é especificada como leve (qi aproximadamente 50-70) com base no nível de comprometimento funcional e no suporte necessário.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Deficiência Intelectual; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Deficiência Intelectual Moderada": (
        'A. Preenche os critérios diagnósticos para deficiência intelectual.\nB. A gravidade é especificada como moderada (qi aproximadamente 35-49) com base no nível de comprometimento funcional e no suporte necessário.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Deficiência Intelectual; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Deficiência Intelectual Grave": (
        'A. Preenche os critérios diagnósticos para deficiência intelectual.\nB. A gravidade é especificada como grave (qi aproximadamente 20-34) com base no nível de comprometimento funcional e no suporte necessário.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Deficiência Intelectual; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Deficiência Intelectual Profunda": (
        'A. Preenche os critérios diagnósticos para deficiência intelectual.\nB. A gravidade é especificada como profunda (qi abaixo de 20) com base no nível de comprometimento funcional e no suporte necessário.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Deficiência Intelectual; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Deficiência Intelectual Não Especificada": (
        'A. Sintomas característicos de deficiência intelectual que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Deficiência Intelectual; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno da Comunicação Não Especificado": (
        'A. Sintomas característicos de transtorno da linguagem que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno da Linguagem; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Déficit de Atenção/Hiperatividade — Apresentação Combinada": (
        'A. Preenche os critérios diagnósticos para transtorno de déficit de atenção/hiperatividade.\nB. O subtipo apresentação combinada (sintomas significativos tanto de desatenção quanto de hiperatividade/impulsividade nos últimos 6 meses) é especificado com base nas características predominantes da apresentação clínica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Déficit de Atenção/Hiperatividade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Déficit de Atenção/Hiperatividade — Apresentação Predominante com Desatenção": (
        'A. Preenche os critérios diagnósticos para transtorno de déficit de atenção/hiperatividade.\nB. O subtipo apresentação predominante com desatenção (sintomas significativos de desatenção, mas não de hiperatividade/impulsividade nos últimos 6 meses) é especificado com base nas características predominantes da apresentação clínica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Déficit de Atenção/Hiperatividade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Déficit de Atenção/Hiperatividade — Apresentação Predominante com Hiperatividade": (
        'A. Preenche os critérios diagnósticos para transtorno de déficit de atenção/hiperatividade.\nB. O subtipo apresentação predominante com hiperatividade/impulsividade (sintomas significativos de hiperatividade/impulsividade, mas não de desatenção nos últimos 6 meses) é especificado com base nas características predominantes da apresentação clínica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Déficit de Atenção/Hiperatividade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Déficit de Atenção/Hiperatividade — Outra Apresentação Especificada": (
        'A. Sintomas característicos de transtorno de déficit de atenção/hiperatividade que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno de déficit de atenção/hiperatividade, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Déficit de Atenção/Hiperatividade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Déficit de Atenção/Hiperatividade Não Especificado": (
        'A. Sintomas característicos de transtorno de déficit de atenção/hiperatividade que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Déficit de Atenção/Hiperatividade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Específico da Aprendizagem Não Especificado": (
        'A. Sintomas característicos de transtorno específico da aprendizagem que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Específico da Aprendizagem; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Específico da Aprendizagem — com Prejuízo na Expressão Escrita": (
        'A. Preenche os critérios diagnósticos para transtorno específico da aprendizagem.\nB. O subtipo prejuízo na expressão escrita (precisão ortográfica, gramática, clareza da organização escrita) é especificado com base nas características predominantes da apresentação clínica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Específico da Aprendizagem; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Específico da Aprendizagem — com Prejuízo na Matemática": (
        'A. Preenche os critérios diagnósticos para transtorno específico da aprendizagem.\nB. O subtipo prejuízo na matemática (senso numérico, memorização de fatos aritméticos, raciocínio matemático) é especificado com base nas características predominantes da apresentação clínica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Específico da Aprendizagem; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Tique Especificado": (
        'A. Sintomas característicos de transtorno de tourette que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno de tourette, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Tourette; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Tique Não Especificado": (
        'A. Sintomas característicos de transtorno de tourette que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Tourette; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Outro Transtorno do Neurodesenvolvimento Especificado": (
        'A. Sintomas característicos de transtorno do espectro autista que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno do espectro autista, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno do Espectro Autista; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno do Neurodesenvolvimento Não Especificado": (
        'A. Sintomas característicos de transtorno do espectro autista que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno do Espectro Autista; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 2: Espectro da Esquizofrenia ═══
    "Transtorno Delirante": (
        "A. Presença de um ou mais delírios com duração de 1 mês ou mais.\n"
        "B. Critério A para esquizofrenia nunca foi preenchido (alucinações, se presentes, não são "
        "proeminentes).\n"
        "C. Funcionamento psicossocial não está acentuadamente prejudicado.\n"
        "D. Episódios maníacos/depressivos, se presentes, são breves.\n"
        "E. Não atribuível a substância ou condição médica.",
        "Esquizofrenia (sintomas negativos, alucinações proeminentes, desorganização); "
        "TOC com insight pobre; TEA; transtorno psicótico induzido por substância; "
        "transtorno delirante orgânico.",
        "Esquizofrenia paranóide; transtorno esquizoafetivo; transtorno bipolar com psicose; "
        "TOC (obsessões com insight pobre); transtorno de personalidade paranoide "
        "(crenças menos fixas e mais plausíveis).",
        "Schizophrenia (6A20); Acute and transient psychotic disorder (6A23); "
        "Bipolar type I disorder (6A60).",
        "Schizophrenia (6A20); Schizoaffective disorder (6A21); "
        "Bipolar type I disorder (6A60); OCD (6B20)."
    ),
    "Transtorno Psicótico Breve": (
        "A. Presença de 1+ sintoma: delírios, alucinações, discurso desorganizado, "
        "comportamento grosseiramente desorganizado/catatônico.\n"
        "B. Duração de 1 dia a 1 mês.\n"
        "C. Não atribuível a substância, condição médica ou transtorno de humor.",
        "Transtorno esquizofreniforme (1-6 meses); esquizofrenia (6+ meses); "
        "transtorno psicótico induzido por substância; transtorno factício; "
        "simulação.",
        "Transtorno esquizofreniforme; esquizofrenia; transtorno bipolar com psicose; "
        "depressão maior com psicose; estresse pós-traumático com flashbacks psicóticos.",
        "Schizophrenia (6A20); Schizophreniform disorder; "
        "Substance-induced psychotic disorder (6C4E).",
        "Schizophrenia (6A20); Schizoaffective disorder (6A21); "
        "Bipolar type I disorder (6A60); Acute stress reaction (Q24.1)."
    ),
    "Transtorno Esquizofreniforme": (
        "A. Critérios A para esquizofrenia.\n"
        "B. Duração de 1 a 6 meses.\n"
        "C. Não requer prejuízo funcional.",
        "Esquizofrenia (6+ meses); transtorno psicótico breve (<1 mês); "
        "transtorno esquizoafetivo; transtorno bipolar com psicose.",
        "Esquizofrenia (diferença temporal); transtorno psicótico breve; "
        "transtorno delirante (delírios não-bizarrros); "
        "transtorno de humor com características psicóticas.",
        "Schizophrenia (6A20); Acute and transient psychotic disorder (6A23); "
        "Delusional disorder (6A24).",
        "Schizophrenia (6A20); Delusional disorder (6A24); "
        "Bipolar type I disorder (6A60)."
    ),
    "Transtorno Esquizoafetivo": (
        "A. Período ininterrupto de doença com episódio de humor maior (depressivo ou maníaco) "
        "concomitante com Critério A de esquizofrenia.\n"
        "B. Delírios ou alucinações por 2+ semanas na ausência de episódio de humor.\n"
        "C. Episódios de humor presentes na maior parte do tempo.\n"
        "D. Não atribuível a substância ou condição médica.",
        "Esquizofrenia (sintomas psicóticos sem episódios de humor proeminentes); "
        "transtorno bipolar com psicose (psicose apenas durante episódios de humor); "
        "transtorno psicótico induzido por substância.",
        "Esquizofrenia; transtorno bipolar tipo I; depressão maior com características "
        "psicóticas; transtorno esquizofreniforme.",
        "Schizophrenia (6A20); Bipolar type I disorder (6A60); "
        "Depressive disorders with psychotic symptoms (6A70-6A71).",
        "Schizophrenia (6A20); Bipolar type I disorder (6A60); "
        "Depressive disorders with psychotic symptoms (6A70-6A71)."
    ),
    "Transtorno Psicótico Induzido por Substância": (
        "A. Delírios ou alucinações proeminentes.\n"
        "B. Evidência de desenvolvimento durante ou logo após intoxicação/abstinência.\n"
        "C. Não é melhor explicado por transtorno psicótico primário.\n"
        "D. Ocorre exclusivamente durante delirium.",
        "Transtorno psicótico primário (esquizofrenia, bipolar); delirium; "
        "transtorno psicótico devido a condição médica.",
        "Esquizofrenia; transtorno bipolar com psicose; transtorno delirante; "
        "intoxicação por substância sem transtorno psicótico.",
        "Schizophrenia (6A20); Delirium (6D70); "
        "Bipolar type I disorder (6A60).",
        "Schizophrenia (6A20); Bipolar type I disorder (6A60); "
        "Delirium (6D70)."
    ),
    "Transtorno Psicótico Devido a Outra Condição Médica": (
        "A. Delírios ou alucinações proeminentes.\n"
        "B. Evidência de que os sintomas são consequência direta de condição médica.\n"
        "C. Não é melhor explicado por transtorno mental.\n"
        "D. Não ocorre exclusivamente durante delirium.",
        "Transtorno psicótico primário; delirium; transtorno psicótico induzido por substância; "
        "simulação.",
        "Esquizofrenia; transtorno bipolar; transtorno delirante; "
        "delirium; transtorno neurocognitivo.",
        "Schizophrenia (6A20); Delirium (6D70); "
        "Neurocognitive disorders (6D71-6D7Z).",
        "Schizophrenia (6A20); Delirium (6D70); "
        "Substance-induced psychotic disorder (6C4E)."
    ),
    "Catatonia": (
        "A. Marcada perturbação psicomotora envolvendo 3+ sintomas: estupor, catalepsia, "
        "flexibilidade cérea, mutismo, negativismo, posturação, maneirismos, estereotipias, "
        "agitação, caretas, ecolalia, ecopraxia.",
        "Discinesia tardia (história de antipsicóticos); encefalite; síndrome serotoninérgica; "
        "síndrome neuroléptica maligna; mutismo seletivo; TEA com catatonia.",
        "Síndrome neuroléptica maligna; encefalite autoimune; estado de mal epiléptico não-convulsivo; "
        "TEA (comportamentos repetitivos); transtorno do movimento estereotipado.",
        "Neuroleptic malignant syndrome (8D86); Encephalitis (1D00); "
        "Autism spectrum disorder (6A02).",
        "Neuroleptic malignant syndrome (8D86); Encephalitis (1D00); "
        "Parkinsonism (8A60)."
    ),

"Catatonia Associada a Transtorno Mental": (
        'A. Preenche os critérios diagnósticos para catatonia.\nB. O quadro catatônico ocorre no contexto de um transtorno mental (ex.: transtorno do humor, psicótico).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Catatonia; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Catatonia Devido a Outra Condição Médica": (
        'A. Preenche os critérios para catatonia.\nB. A etiologia é atribuída a condição médica geral (ex.: encefalite, acidente vascular cerebral, neoplasia), conforme evidenciado por história clínica, exame físico e exames complementares.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Catatonia; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Catatonia Não Especificada": (
        'A. Sintomas característicos de catatonia que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Catatonia; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Outro Transtorno do Espectro da Esquizofrenia Especificado": (
        'A. Sintomas característicos de esquizofrenia / transtorno psicótico que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para esquizofrenia / transtorno psicótico, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Esquizofrenia / Transtorno Psicótico; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno do Espectro da Esquizofrenia Não Especificado": (
        'A. Sintomas característicos de esquizofrenia / transtorno psicótico que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Esquizofrenia / Transtorno Psicótico; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 3: Transtornos Bipolares ═══
    "Transtorno Ciclotímico": (
        "A. Numerosos períodos de sintomas hipomaníacos e depressivos subclínicos por 2+ anos "
        "(1 ano para adolescentes).\n"
        "B. Sintomas não preenchem critérios para episódio hipomaníaco ou depressivo maior.\n"
        "C. Sem período assintomático > 2 meses.\n"
        "D. Não atribuível a substância ou condição médica.",
        "Transtorno bipolar tipo II (presença de episódio depressivo maior); "
        "transtorno de personalidade borderline (instabilidade reativa vs. cíclica); "
        "TDAH em adultos.",
        "Bipolar tipo II; transtorno de personalidade borderline; "
        "TDAH; transtorno depressivo persistente; "
        "transtorno de ansiedade generalizada.",
        "Bipolar type II disorder (6A61); Borderline personality disorder (6D11); "
        "ADHD (6A05).",
        "Bipolar type II disorder (6A61); Dysthymic disorder (6A72); "
        "Borderline personality disorder (6D11); ADHD (6A05)."
    ),
    "Transtorno Bipolar Induzido por Substância": (
        "A. Elevação ou irritabilidade proeminente e persistente do humor.\n"
        "B. Evidência de desenvolvimento durante ou logo após intoxicação/abstinência.\n"
        "C. Não é melhor explicado por transtorno bipolar primário.",
        "Transtorno bipolar primário; transtorno por uso de substância comórbido; "
        "transtorno de humor devido a condição médica.",
        "Transtorno bipolar tipo I/II; TDAH; transtorno de personalidade borderline; "
        "intoxicação por estimulantes.",
        "Bipolar type I/II disorder (6A60-6A61); ADHD (6A05); "
        "Borderline personality disorder (6D11).",
        "Bipolar type I/II disorder (6A60-6A61); ADHD (6A05); "
        "Substance intoxication (6C4E)."
    ),
    "Transtorno Bipolar Devido a Outra Condição Médica": (
        "A. Elevação ou irritabilidade proeminente e persistente do humor.\n"
        "B. Evidência de que é consequência direta de condição médica.\n"
        "C. Não é melhor explicado por transtorno mental.\n"
        "D. Não ocorre exclusivamente durante delirium.",
        "Transtorno bipolar primário; transtorno de humor induzido por substância; "
        "delirium; transtorno de personalidade.",
        "Transtorno bipolar tipo I/II; doença de Cushing; hipertireoidismo; "
        "esclerose múltipla; AVE; delirium.",
        "Bipolar disorders (6A60-6A61); Cushing syndrome (5A70); "
        "Hyperthyroidism (5A02); Delirium (6D70).",
        "Bipolar disorders (6A60-6A61); Delirium (6D70); "
        "Substance-induced mood disorder."
    ),

"Outro Transtorno Bipolar Especificado": (
        'A. Sintomas característicos de transtorno bipolar tipo i que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno bipolar tipo i, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Bipolar Tipo I; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Bipolar Não Especificado": (
        'A. Sintomas característicos de transtorno bipolar tipo i que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Bipolar Tipo I; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 4: Transtornos Depressivos ═══
    "Transtorno Disruptivo da Desregulação do Humor": (
        "A. Explosões de raiva severas e recorrentes (verbais ou físicas) desproporcionais.\n"
        "B. Inconsistentes com o nível de desenvolvimento.\n"
        "C. Ocorrem 3+ vezes/semana.\n"
        "D. Humor persistentemente irritável entre explosões.\n"
        "E. Presente por 12+ meses em 2+ ambientes.\n"
        "F. Diagnóstico entre 6-18 anos.\n"
        "G. Início antes dos 10 anos.",
        "Transtorno bipolar (episódios distintos de mania/hipomania); "
        "TOD (humor raivoso crônico sem explosões severas); "
        "depressão maior (episódios distintos sem irritabilidade crônica); "
        "TDAH; transtorno explosivo intermitente.",
        "Transtorno bipolar (especialmente em crianças); TOD; "
        "transtorno explosivo intermitente; TDAH; "
        "depressão maior; ansiedade de separação.",
        "Bipolar disorders (6A60-6A61); Oppositional defiant disorder (6C90); "
        "Intermittent explosive disorder (6C70).",
        "Bipolar disorders (6A60-6A61); Oppositional defiant disorder (6C90); "
        "ADHD (6A05); Major depressive disorder (6A70-6A71)."
    ),
    "Transtorno Disfórico Pré-Menstrual": (
        "A. Na maioria dos ciclos, 5+ sintomas na semana pré-menstrual com melhora na semana "
        "pós-menstrual: labilidade afetiva, irritabilidade, humor deprimido, ansiedade, "
        "anedonia, fadiga, alterações do sono/apetite, sintomas físicos.\n"
        "B. 1+ dos seguintes: labilidade afetiva, irritabilidade, humor deprimido, ansiedade.\n"
        "C. Prejuízo no funcionamento.\n"
        "D. Não é exacerbação de transtorno preexistente.",
        "TDM (sintomas não limitados à fase lútea); TAG; transtorno bipolar; "
        "síndrome pré-menstrual (menos sintomas, sem prejuízo funcional); "
        "transtorno disfórico pré-menstrual mascarado.",
        "TDM; TAG; transtorno bipolar; síndrome pré-menstrual; "
        "transtorno de personalidade borderline.",
        "Premenstrual syndrome (GA34.4); Major depressive disorder (6A70-6A71); "
        "Bipolar disorders (6A60-6A61).",
        "Major depressive disorder (6A70-6A71); Bipolar disorder (6A60-6A61); "
        "Premenstrual syndrome (GA34.4)."
    ),
    "Transtorno Depressivo Induzido por Substância": (
        "A. Humor deprimido ou anedonia proeminente.\n"
        "B. Desenvolvimento durante ou logo após intoxicação/abstinência.\n"
        "C. Não é melhor explicado por depressão primária.",
        "Transtorno depressivo maior (primário); transtorno bipolar; "
        "transtorno de adaptação; transtorno de ansiedade.",
        "TDM; transtorno de adaptação com humor deprimido; "
        "transtorno bipolar; transtorno depressivo persistente.",
        "Major depressive disorder (6A70); Recurrent depressive disorder (6A71); "
        "Adjustment disorder (6B43).",
        "Major depressive disorder (6A70-6A71); Adjustment disorder (6B43); "
        "Dysthymic disorder (6A72)."
    ),
    "Transtorno Depressivo Devido a Outra Condição Médica": (
        "A. Humor deprimido ou anedonia proeminente.\n"
        "B. Evidência de que é consequência direta de condição médica.\n"
        "C. Não ocorre exclusivamente durante delirium.",
        "TDM primário; transtorno de adaptação; transtorno depressivo induzido por substância; "
        "transtorno bipolar.",
        "TDM; hipotireoidismo; doença de Parkinson; AVE; "
        "doença de Cushing; lúpus eritematoso sistêmico; dor crônica.",
        "Major depressive disorder (6A70-6A71); Hypothyroidism (5A00); "
        "Parkinson disease (8A60).",
        "Major depressive disorder (6A70-6A71); Substance-induced depressive disorder."
    ),

"Outro Transtorno Depressivo Especificado": (
        'A. Sintomas característicos de transtorno depressivo maior que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno depressivo maior, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Depressivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Depressivo Não Especificado": (
        'A. Sintomas característicos de transtorno depressivo maior que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Depressivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 5: Transtornos de Ansiedade ═══
    "Transtorno de Ansiedade de Separação": (
        "A. Medo ou ansiedade excessiva quanto à separação de figuras de apego.\n"
        "B. Preocupação persistente sobre perda ou dano às figuras de apego.\n"
        "C. Recusa a sair de perto de casa ou figuras de apego.\n"
        "D. Pesadelos ou sintomas físicos relacionados à separação.\n"
        "E. Presente por 4+ semanas em crianças, 6+ meses em adultos.\n"
        "F. Causa prejuízo clinicamente significativo.",
        "TAG (preocupação difusa não focada em figuras de apego); "
        "transtorno do pânico (ataques inesperados); "
        "mutismo seletivo; TEPT; agorafobia.",
        "TAG; transtorno do pânico; agorafobia; fobia específica; "
        "transtorno de ansiedade social; TOD (recusa escolar).",
        "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
        "Agoraphobia (6B02); Social anxiety disorder (6B04).",
        "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
        "Agoraphobia (6B02); Oppositional defiant disorder (6C90)."
    ),
    "Mutismo Seletivo": (
        "A. Fala consistentemente ausente em situações sociais específicas onde se espera que fale, "
        "apesar de falar em outras situações.\n"
        "B. Interfere no funcionamento educacional/ocupacional.\n"
        "C. Duração de 1+ mês.\n"
        "D. Não atribuível a desconforto com o idioma ou transtorno da comunicação.",
        "Transtorno da comunicação (déficit de linguagem); "
        "TEA (déficits sociais mais amplos); "
        "transtorno de ansiedade social (medo de avaliação, não apenas de falar); "
        "mutismo traumático; fobia específica.",
        "Transtorno de ansiedade social; TEA; transtorno da linguagem; "
        "mutismo devido a trauma; transtorno de comunicação social.",
        "Social anxiety disorder (6B04); Autism spectrum disorder (6A02); "
        "Language disorder (6A01).",
        "Social anxiety disorder (6B04); Autism spectrum disorder (6A02); "
        "Communication disorders (6A01)."
    ),
    "Fobia Específica": (
        "A. Medo ou ansiedade intensa em relação a objeto ou situação específica.\n"
        "B. Situação quase sempre provoca medo/ansiedade.\n"
        "C. Ativamente evitada ou suportada com intensa ansiedade.\n"
        "D. Medo desproporcional ao perigo real.\n"
        "E. Persiste por 6+ meses.\n"
        "F. Causa sofrimento ou prejuízo.\n"
        "G. Não atribuível a outro transtorno mental.",
        "Agorafobia (múltiplas situações temidas); "
        "transtorno de ansiedade social (foco social); "
        "transtorno do pânico (ataques inesperados); TOC; TEPT.",
        "Agorafobia; transtorno de ansiedade social; "
        "transtorno do pânico; TAG; "
        "hipocondria (medo de doença); transtorno de ansiedade de doença.",
        "Agoraphobia (6B02); Social anxiety disorder (6B04); "
        "Panic disorder (6B01).",
        "Agoraphobia (6B02); Social anxiety disorder (6B04); "
        "Panic disorder (6B01); Health anxiety disorder (6B23)."
    ),
    "Transtorno de Ansiedade Induzido por Substância": (
        "A. Ansiedade ou ataques de pânico proeminentes.\n"
        "B. Evidência de desenvolvimento durante ou logo após intoxicação/abstinência.\n"
        "C. Não é melhor explicado por transtorno de ansiedade primário.",
        "Transtorno de ansiedade primário (TAG, pânico); "
        "transtorno de ansiedade devido a condição médica; "
        "delirium; síndrome de abstinência.",
        "TAG; transtorno do pânico; transtorno de ansiedade social; "
        "hipertireoidismo; feocromocitoma; abstinência alcoólica.",
        "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
        "Hyperthyroidism (5A02).",
        "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
        "Social anxiety disorder (6B04)."
    ),
    "Transtorno de Ansiedade Devido a Outra Condição Médica": (
        "A. Ansiedade ou ataques de pânico proeminentes.\n"
        "B. Evidência de que os sintomas são consequência direta de condição médica.\n"
        "C. Não é melhor explicado por transtorno mental.\n"
        "D. Não ocorre exclusivamente durante delirium.",
        "Transtorno de ansiedade primário; transtorno de ansiedade induzido por substância; "
        "transtorno de adaptação; delirium.",
        "TAG; transtorno do pânico; hipertireoidismo; "
        "hiperparatireoidismo; feocromocitoma; arritmia cardíaca; asma; DPOC.",
        "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
        "Hyperthyroidism (5A02); Pheochromocytoma (5A70).",
        "Generalized anxiety disorder (6B00); Panic disorder (6B01); "
        "Adjustment disorder (6B43)."
    ),

"Outro Transtorno de Ansiedade Especificado": (
        'A. Sintomas característicos de transtorno de ansiedade generalizada que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno de ansiedade generalizada, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Ansiedade Generalizada; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Ansiedade Não Especificado": (
        'A. Sintomas característicos de transtorno de ansiedade generalizada que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Ansiedade Generalizada; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 6: Transtornos Obsessivo-Compulsivos ═══
    "Transtorno Dismórfico Corporal": (
        "A. Preocupação com um ou mais defeitos na aparência que não são observáveis ou parecem "
        "menores para outros.\n"
        "B. Comportamentos repetitivos ou atos mentais em resposta à preocupação.\n"
        "C. Causa sofrimento ou prejuízo clinicamente significativo.",
        "Transtorno de ansiedade social (foco em avaliação, não em defeito específico); "
        "TOC (obsessões sem foco exclusivo na aparência); "
        "transtorno alimentar (peso/forma corporal vs. defeito específico); "
        "transtorno de ansiedade de doença (foco em doença, não em aparência).",
        "TOC; transtorno alimentar; transtorno de ansiedade social; "
        "transtorno de ansiedade de doença; transtorno factício; "
        "transtorno de personalidade narcisista (preocupação excessiva com aparência).",
        "Obsessive-compulsive disorder (6B20); Eating disorders (6B80-6B82); "
        "Social anxiety disorder (6B04); Health anxiety disorder (6B23).",
        "OCD (6B20); Social anxiety disorder (6B04); "
        "Anorexia nervosa (6B80); Body integrity dysphoria."
    ),
    "Transtorno de Acumulação": (
        "A. Dificuldade persistente em descartar posses, independentemente do valor.\n"
        "B. Percebida como necessidade de guardar itens e sofrimento ao descartá-los.\n"
        "C. Acúmulo que compromete o uso de áreas da vida.\n"
        "D. Causa sofrimento ou prejuízo clinicamente significativo.\n"
        "E. Não atribuível a condição médica.",
        "TOC (acumulação como compulsão, geralmente com outras obsessões); "
        "transtorno de acumulação animal; colecionismo (organizado, sem prejuízo); "
        "depressão maior (anedonia); demência; síndrome de Diógenes.",
        "TOC; colecionismo normal; depressão maior; "
        "transtorno de personalidade obsessivo-compulsiva; "
        "demência frontotemporal; síndrome de Prader-Willi.",
        "OCD (6B20); Hoarding due to organic brain disorder; "
        "Frontotemporal dementia (6D81).",
        "OCD (6B20); Depressive disorders (6A70-6A71); "
        "Frontotemporal dementia (6D81)."
    ),
    "Tricotilomania": (
        "A. Arrancar cabelos recorrentemente, resultando em perda capilar.\n"
        "B. Tentativas repetidas de parar ou reduzir.\n"
        "C. Causa sofrimento ou prejuízo clinicamente significativo.\n"
        "D. Não atribuível a condição médica (alopecia) ou substância.\n"
        "E. Não é melhor explicado por outro transtorno mental.",
        "Transtorno de escoriação (pele vs. cabelo); TOC (compulsão consciente com obsessão); "
        "transtorno do movimento estereotipado; alopecia areata; "
        "transtorno dismórfico corporal (arrancar por defeito percebido).",
        "TOC; transtorno de escoriação; transtorno do movimento estereotipado; "
        "transtorno de personalidade borderline; alopecia.",
        "OCD (6B20); Skin picking disorder (6B25); "
        "Stereotypic movement disorder (6A06).",
        "OCD (6B20); Skin picking disorder (6B25); "
        "Stereotypic movement disorder (6A06)."
    ),
    "Transtorno de Escoriação (Skin Picking)": (
        "A. Beliscar a pele recorrentemente, resultando em lesões.\n"
        "B. Tentativas repetidas de parar ou reduzir.\n"
        "C. Causa sofrimento ou prejuízo clinicamente significativo.\n"
        "D. Não atribuível a condição médica (sarna, psoríase) ou substância.\n"
        "E. Não é melhor explicado por outro transtorno mental.",
        "Tricotilomania (cabelo vs. pele); TOC; "
        "transtorno do movimento estereotipado; "
        "condição dermatológica primária; autolesão não suicida.",
        "TOC; tricotilomania; autolesão não suicida (borderline); "
        "transtorno factício; condição dermatológica.",
        "OCD (6B20); Trichotillomania (6B25); "
        "Factitial dermatitis (sindrômico).",
        "OCD (6B20); Trichotillomania (6B25); "
        "Borderline personality disorder (6D11)."
    ),
    "TOC Induzido por Substância": (
        "A. Sintomas obsessivo-compulsivos proeminentes.\n"
        "B. Evidência de desenvolvimento durante intoxicação/abstinência.\n"
        "C. Não é melhor explicado por TOC primário.",
        "TOC primário; TOC devido a condição médica; "
        "TOC + transtorno por uso de substância comórbido.",
        "TOC; transtorno de ansiedade; síndrome de Tourette; "
        "coreia de Sydenham (PANDAS).",
        "OCD (6B20); Tic disorders (8A05); "
        "Substance-induced anxiety disorder."
    ),

"TOC Devido a Outra Condição Médica": (
        'A. Preenche os critérios para transtorno obsessivo-compulsivo.\nB. A etiologia é atribuída a condição médica (ex.: lesão cerebral, infecção), conforme evidenciado por história clínica, exame físico e exames complementares.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Obsessivo-Compulsivo; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Outro Transtorno Obsessivo-Compulsivo Especificado": (
        'A. Sintomas característicos de transtorno obsessivo-compulsivo que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno obsessivo-compulsivo, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Obsessivo-Compulsivo; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Obsessivo-Compulsivo Não Especificado": (
        'A. Sintomas característicos de transtorno obsessivo-compulsivo que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Obsessivo-Compulsivo; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 7: Transtornos Relacionados a Trauma ═══
    "Transtorno de Apego Reativo": (
        "A. Padrão inibido emocionalmente e retraído em relação a cuidadores.\n"
        "B. Perturbação social e emocional persistente: sofrimento mínimo, reciprocidade social "
        "reduzida, regulação emocional prejudicada.\n"
        "C. Cuidados extremamente insuficientes (privação, negligência).\n"
        "D. Início antes dos 5 anos.\n"
        "E. Critérios para TEA não preenchidos.",
        "TEA (déficits sociais mesmo com cuidados adequados); "
        "deficiência intelectual; transtorno de estresse pós-traumático; "
        "depressão maior na infância.",
        "TEA; deficiência intelectual; transtorno de engajamento social desinibido; "
        "TEPT; depressão infantil; transtorno de adaptação.",
        "Autism spectrum disorder (6A02); Intellectual developmental disorder (6A00); "
        "PTSD (6B40).",
        "Autism spectrum disorder (6A02); Disinhibited social engagement disorder; "
        "PTSD (6B40)."
    ),
    "Transtorno de Engajamento Social Desinibido": (
        "A. Comportamento excessivamente familiar com estranhos: aproximação ativa, "
        "falta de verificação com cuidador, aceitação de estranhos.\n"
        "B. Cuidados extremamente insuficientes.\n"
        "C. Início antes dos 5 anos.",
        "TDAH (impulsividade generalizada, não específica a estranhos); "
        "TEA (déficit social qualitativo); síndrome de Williams; "
        "transtorno de apego reativo (inibido vs. desinibido).",
        "TDAH; síndrome de Williams; "
        "transtorno de apego reativo; comportamento normal em crianças pequenas.",
        "ADHD (6A05); Williams syndrome (LD90); "
        "Reactive attachment disorder (6B44).",
        "ADHD (6A05); Autism spectrum disorder (6A02); "
        "Reactive attachment disorder (6B44)."
    ),
    "Transtorno de Estresse Agudo": (
        "A. Exposição a morte real/ameaçadora, lesão grave ou violência sexual.\n"
        "B. 9+ sintomas de qualquer categoria: intrusão, humor negativo, dissociação, evitação, "
        "excitação.\n"
        "C. Duração de 3 dias a 1 mês.\n"
        "D. Causa sofrimento ou prejuízo significativo.",
        "TEPT (duração > 1 mês); transtorno de adaptação (estressor menos severo); "
        "transtorno de pânico; transtorno psicótico breve; "
        "traumatismo cranioencefálico.",
        "TEPT; transtorno de adaptação; TAG; depressão maior; "
        "transtorno do pânico; amnésia dissociativa; psicose breve.",
        "PTSD (6B40); Adjustment disorder (6B43); "
        "Acute stress reaction (Q24.1).",
        "PTSD (6B40); Adjustment disorder (6B43); "
        "Panic disorder (6B01)."
    ),
    "Transtornos de Adaptação": (
        "A. Sintomas emocionais ou comportamentais em resposta a estressor identificável dentro "
        "de 3 meses.\n"
        "B. Sofrimento desproporcional ou prejuízo no funcionamento.\n"
        "C. Não preenche critérios para outro transtorno mental.\n"
        "D. Duração de até 6 meses após término do estressor.",
        "TDM (sintomas mais severos e persistentes); TAG (preocupação não relacionada a estressor); "
        "TEPT (estressor traumático); TEA (sem estressor identificável); "
        "transtorno de ansiedade de doença.",
        "TDM; TAG; TEPT; transtorno de estresse agudo; "
        "transtorno de pânico; transtorno de sintomas somáticos; luto.",
        "Major depressive disorder (6A70); Generalized anxiety disorder (6B00); "
        "PTSD (6B40); Prolonged grief disorder (6B42).",
        "Major depressive disorder (6A70-6A71); GAD (6B00); "
        "Acute stress reaction (Q24.1); PTSD (6B40)."
    ),
    "Transtorno de Luto Prolongado": (
        "A. Morte de alguém próximo há 12+ meses.\n"
        "B. Dor intensa e persistente: anseio, preocupação com o falecido, dor emocional intensa.\n"
        "C. Causa prejuízo em múltiplos domínios.\n"
        "D. Não atribuível a transtorno depressivo ou TEPT.",
        "TDM (humor deprimido generalizado, não focado na perda); "
        "TEPT (estressor traumático, revivência, evitação); "
        "transtorno de adaptação (estressor não limitado a luto); "
        "luto normal (variação cultural).",
        "TDM; TEPT; transtorno de adaptação; "
        "ansiedade de separação; luto normal.",
        "Major depressive disorder (6A70-6A71); PTSD (6B40); "
        "Adjustment disorder (6B43).",
        "Major depressive disorder (6A70-6A71); PTSD (6B40); "
        "Anxiety disorders (6B00-6B0Z)."
    ),

"Outro Transtorno Relacionado a Trauma Especificado": (
        'A. Sintomas característicos de transtorno de estresse pós-traumático que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno de estresse pós-traumático, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Estresse Pós-Traumático; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Relacionado a Trauma Não Especificado": (
        'A. Sintomas característicos de transtorno de estresse pós-traumático que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Estresse Pós-Traumático; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 8: Transtornos Dissociativos ═══
    "Transtorno Dissociativo de Identidade": (
        "A. Perturbação da identidade caracterizada por 2+ estados de personalidade distintos.\n"
        "B. Lacunas recorrentes na recordação de eventos cotidianos.\n"
        "C. Causa sofrimento ou prejuízo.\n"
        "D. Não é parte de prática cultural ou religiosa.\n"
        "E. Não atribuível a substância ou condição médica.",
        "Transtorno de estresse pós-traumático (flashbacks sem alteração de personalidade); "
        "transtorno de conversão; simulação; transtorno factício; "
        "esquizofrenia; transtorno bipolar.",
        "TEPT; transtorno de conversão; depressão maior; "
        "esquizofrenia; transtorno de personalidade borderline; "
        "transtorno factício; simulação.",
        "PTSD (6B40); Schizophrenia (6A20); "
        "Borderline personality disorder (6D11); Factitious disorder (6D50).",
        "PTSD (6B40); Borderline personality disorder (6D11); "
        "Conversion disorder (6B60); Schizophrenia (6A20)."
    ),
    "Amnésia Dissociativa": (
        "A. Incapacidade de recordar informações autobiográficas, geralmente traumáticas.\n"
        "B. Causa sofrimento ou prejuízo.\n"
        "C. Não atribuível a substância, condição neurológica, TEPT ou TDI.",
        "Amnésia devido a trauma cranioencefálico; amnésia psicogênica; "
        "convulsões; AVE; demência; transtorno dissociativo de identidade; "
        "simulação.",
        "TEPT (amnésia como parte do quadro); TDI; "
        "amnésia neurológica; transtorno neurocognitivo; "
        "crise não-epiléptica psicogênica.",
        "PTSD (6B40); DID (6B61); "
        "Neurological amnesia; Neurocognitive disorders (6D71-6D7Z).",
        "PTSD (6B40); DID (6B61); Neurocognitive disorders (6D71-6D7Z); "
        "Conversion disorder (6B60)."
    ),
    "Transtorno de Despersonalização/Desrealização": (
        "A. Experiências persistentes de despersonalização e/ou desrealização.\n"
        "B. Preservação do senso de realidade durante episódios.\n"
        "C. Causa sofrimento ou prejuízo.\n"
        "D. Não atribuível a substância, condição médica ou outro transtorno mental.",
        "TEPT (despersonalização como sintoma dissociativo); "
        "transtorno do pânico (despersonalização durante ataques); "
        "depressão maior; esquizofrenia; efeito de substância; "
        "epilepsia do lobo temporal.",
        "TEPT; transtorno do pânico; depressão maior; "
        "esquizofrenia; TDI; epilepsia; enxaqueca; "
        "ansiedade generalizada.",
        "PTSD (6B40); Panic disorder (6B01); "
        "Depressive disorders (6A70-6A71); Temporal lobe epilepsy (8A61).",
        "PTSD (6B40); Panic disorder (6B01); "
        "Depressive disorders (6A70-6A71); Schizophrenia (6A20)."
    ),

"Outro Transtorno Dissociativo Especificado": (
        'A. Sintomas característicos de transtorno dissociativo de identidade que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno dissociativo de identidade, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Dissociativo de Identidade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Dissociativo Não Especificado": (
        'A. Sintomas característicos de transtorno dissociativo de identidade que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Dissociativo de Identidade; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 9: Transtornos de Sintomas Somáticos ═══
    "Transtorno de Ansiedade de Doença": (
        "A. Preocupação com ter ou adquirir doença grave.\n"
        "B. Sintomas somáticos ausentes ou leves.\n"
        "C. Ansiedade elevada acerca da saúde.\n"
        "D. Comportamentos excessivos relacionados à saúde.\n"
        "E. Presente por 6+ meses.",
        "Transtorno de sintomas somáticos (sintomas somáticos proeminentes); "
        "transtorno de pânico (ataques focados em sintomas corporais); "
        "TAG (preocupação em múltiplos domínios); TOC (saúde como obsessão).",
        "Transtorno de sintomas somáticos; transtorno do pânico; TAG; "
        "TOC; depressão maior; transtorno delirante (tipo somático); "
        "transtorno factício; simulação.",
        "Somatic symptom disorder (6C20); Panic disorder (6B01); "
        "GAD (6B00); OCD (6B20); Hypochondriasis (ICD-10 F45.2).",
        "Somatic symptom disorder (6C20); Panic disorder (6B01); "
        "GAD (6B00); OCD (6B20); Delusional disorder (6A24)."
    ),
    "Transtorno Conversivo (Transtorno de Sintomas Neurológicos Funcionais)": (
        "A. Sintomas neurológicos motores ou sensoriais.\n"
        "B. Achados clínicos incompatíveis com condições neurológicas.\n"
        "C. Causa sofrimento ou prejuízo.\n"
        "D. Não atribuível a outra condição médica.",
        "Condição neurológica genuína (esclerose múltipla, AVE, epilepsia); "
        "transtorno factício; simulação; "
        "transtorno de sintomas somáticos (sintomas sem alteração neurológica funcional).",
        "Esclerose múltipla; epilepsia; AVE; miastenia gravis; "
        "neuropatia periférica; doença de Parkinson; "
        "transtorno factício; simulação.",
        "Multiple sclerosis (8A40); Epilepsy (8A61); Stroke (8B20); "
        "Factitious disorder (6D50).",
        "Multiple sclerosis (8A40); Epilepsy (8A61); "
        "Somatic symptom disorder (6C20); Factitious disorder (6D50)."
    ),
    "Transtorno Factício": (
        "A. Falsificação de sinais ou sintomas físicos/psicológicos.\n"
        "B. O indivíduo se apresenta como doente.\n"
        "C. Engano evidente mesmo sem incentivo externo.\n"
        "D. Não é melhor explicado por outro transtorno mental.",
        "Simulação (incentivo externo: financeiro, legal); "
        "transtorno de sintomas somáticos (sem falsificação consciente); "
        "transtorno conversivo; hipocondria.",
        "Simulação; transtorno de sintomas somáticos; "
        "transtorno conversivo; transtorno factício por procuração; "
        "condição médica genuína.",
        "Malingering (Z76.5); Somatic symptom disorder (6C20); "
        "Conversion disorder (6B60).",
        "Somatic symptom disorder (6C20); Conversion disorder (6B60); "
        "Malingering."
    ),
    "Fatores Psicológicos que Afetam Outras Condições Médicas": (
        "A. Condição médica presente.\n"
        "B. Fatores psicológicos ou comportamentais a afetam adversamente.\n"
        "C. Os fatores influenciam o curso, tratamento ou qualidade de vida.",
        "Transtorno de sintomas somáticos (sintomas que causam sofrimento); "
        "transtorno de adaptação; não adesão ao tratamento sem fatores psicológicos.",
        "Transtorno de sintomas somáticos; transtorno de ansiedade de doença; "
        "transtorno de adaptação; depressão maior comórbida.",
        "Somatic symptom disorder (6C20); Health anxiety disorder (6B23); "
        "Adjustment disorder (6B43).",
        "Somatic symptom disorder (6C20); Adjustment disorder (6B43); "
        "Depressive disorders (6A70-6A71)."
    ),

"Outro Transtorno de Sintomas Somáticos Especificado": (
        'A. Sintomas característicos de transtorno de sintomas somáticos que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno de sintomas somáticos, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Sintomas Somáticos; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno de Sintomas Somáticos Não Especificado": (
        'A. Sintomas característicos de transtorno de sintomas somáticos que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Sintomas Somáticos; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 10: Transtornos Alimentares ═══
    "Pica": (
        "A. Ingestão persistente de substâncias não nutritivas por 1+ mês.\n"
        "B. Para a idade de desenvolvimento.\n"
        "C. Não é parte de prática cultural.\n"
        "D. Se presente com outro transtorno mental ou condição médica, é grave o suficiente.",
        "Transtorno alimentar restritivo-evitativo (seletividade alimentar, não ingestão de "
        "não-nutrientes); TEA (comportamento sensorial atípico); "
        "esquizofrenia (pica por delírio).",
        "TEA (comportamento de pica associado); deficiência intelectual; "
        "transtorno alimentar restritivo-evitativo; "
        "deficiência de ferro (causa ou efeito).",
        "Autism spectrum disorder (6A02); ARFID (6B83); "
        "Intellectual developmental disorder (6A00).",
        "Autism spectrum disorder (6A02); ARFID (6B83); "
        "Iron deficiency anemia (3A00)."
    ),
    "Transtorno de Ruminação": (
        "A. Regurgitação repetida de alimentos por 1+ mês.\n"
        "B. Não é atribuível a condição gastrointestinal.\n"
        "C. Não ocorre exclusivamente durante anorexia, bulimia ou TAREA.\n"
        "D. Se presente com deficiência intelectual, é grave o suficiente.",
        "Anorexia/bulimia nervosa (preocupação com peso/forma); "
        "refluxo gastroesofágico; estenose pilórica; "
        "síndrome de ruminação em deficiência intelectual.",
        "Anorexia nervosa; bulimia nervosa; "
        "refluxo gastroesofágico; gastroparesia; "
        "TAREA (evitação sensorial, não regurgitação).",
        "Anorexia nervosa (6B80); Bulimia nervosa (6B81); "
        "GERD (DA22); Gastroparesis."
    ),
    "Transtorno Alimentar Restritivo-Evitante": (
        "A. Perturbação alimentar: desinteresse por comida, evitação sensorial, "
        "preocupação com consequências aversivas.\n"
        "B. Perda de peso significativa, déficit nutricional, dependência de suplementos.\n"
        "C. Não é melhor explicado por anorexia ou bulimia.\n"
        "D. Não atribuível a condição médica ou indisponibilidade de comida.\n"
        "E. Início antes dos 6 anos.",
        "Anorexia nervosa (preocupação com peso/forma); bulimia nervosa; "
        "pica; TEA (seletividade alimentar); "
        "fobia específica (medo de engasgar); condição médica.",
        "Anorexia nervosa; pica; TEA; "
        "fobia específica (vômito, engasgo); "
        "transtorno de ansiedade; TOC (alimentar).",
        "Anorexia nervosa (6B80); Pica (6B84); "
        "Autism spectrum disorder (6A02).",
        "Anorexia nervosa (6B80); Bulimia nervosa (6B81); "
        "Autism spectrum disorder (6A02); OCD (6B20)."
    ),

"Outro Transtorno Alimentar Especificado": (
        'A. Sintomas característicos de anorexia nervosa que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para anorexia nervosa, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Anorexia Nervosa; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Alimentar Não Especificado": (
        'A. Sintomas característicos de anorexia nervosa que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Anorexia Nervosa; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 11: Transtornos da Eliminação ═══
    "Enurese": (
        "A. Eliminação repetida de urina na cama/roupa (involuntária ou intencional).\n"
        "B. 2+ vezes/semana por 3+ meses.\n"
        "C. Idade cronológica de 5+ anos.\n"
        "D. Não atribuível a condição médica ou diuréticos.",
        "Condição médica (infecção urinária, diabetes, bexiga neurogênica); "
        "incontinência por estresse; epilepsia; apneia do sono; "
        "medicação (lítio, diuréticos).",
        "Infecção urinária; diabetes mellitus/insipidus; "
        "bexiga neurogênica; enurese noturna primária; "
        "transtorno de ansiedade de separação (enurese secundária).",
        "Urinary tract infection (GC08); Diabetes mellitus (5A10); "
        "Sleep disorders (7A00-7A0Z).",
        "UTI (GC08); Diabetes (5A10); "
        "Separation anxiety disorder (6B05)."
    ),
    "Encoprese": (
        "A. Eliminação repetida de fezes em locais inadequados.\n"
        "B. 1+ vez/mês por 3+ meses.\n"
        "C. Idade cronológica de 4+ anos.\n"
        "D. Não atribuível a condição médica ou laxantes.",
        "Condição médica (doença de Hirschsprung, constipação crônica, "
        "fissura anal, lesão medular); "
        "transtorno desafiador opositivo (intencional); "
        "transtorno factício.",
        "Constipação crônica com transbordamento; "
        "doença de Hirschsprung; lesão medular; "
        "TOD; encoprese retentiva vs. não-retentiva.",
        "Hirschsprung disease (DA30); Chronic constipation (DA92); "
        "Oppositional defiant disorder (6C90).",
        "Chronic constipation (DA92); Hirschsprung disease (DA30); "
        "ODD (6C90)."
    ),

"Outro Transtorno da Eliminação Especificado": (
        'A. Sintomas característicos de enurese que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para enurese, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Enurese; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno da Eliminação Não Especificado": (
        'A. Sintomas característicos de enurese que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Enurese; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 12: Transtornos do Sono-Vigília ═══
    "Transtorno de Hipersonolência": (
        "A. Sonolência excessiva apesar de sono principal ≥ 7 horas.\n"
        "B. Períodos recorrentes de sono irresistível ou lapsos de sono.\n"
        "C. Ocorre 3+ vezes/semana por 3+ meses.\n"
        "D. Causa sofrimento ou prejuízo.",
        "Narcolepsia (cataplexia, alucinações hipnagógicas); "
        "apneia do sono; síndrome das pernas inquietas; "
        "insônia crônica; privação de sono; transtorno do ritmo circadiano; "
        "depressão maior; hipersonia induzida por substância.",
        "Narcolepsia; apneia obstrutiva do sono; "
        "privação de sono; hipersonia idiopática; "
        "síndrome de Kleine-Levin; depressão atípica.",
        "Narcolepsy (7A20); Obstructive sleep apnoea (7A41); "
        "Depressive disorders (6A70-6A71).",
        "Narcolepsy (7A20); OSA (7A41); "
        "Depressive disorders (6A70-6A71); Kleine-Levin syndrome."
    ),
    "Narcolepsia": (
        "A. Ataques recorrentes de sono irresistível 3+ vezes/semana por 3+ meses.\n"
        "B. 1+ dos seguintes: cataplexia, deficiência de hipocretina, "
        "início REM em 15 min no MSLT.\n"
        "C. Não atribuível a substância ou condição médica.",
        "Transtorno de hipersonolência (sem cataplexia); "
        "apneia obstrutiva do sono; privação de sono; "
        "síndrome de Kleine-Levin; epilepsia; AVE; tumor cerebral.",
        "Transtorno de hipersonolência; apneia do sono; "
        "síndrome de Kleine-Levin; convulsões; "
        "narcolepsia tipo 1 vs. tipo 2.",
        "Hypersomnolence disorder (7A21); OSA (7A41); "
        "Kleine-Levin syndrome (7A22).",
        "Hypersomnolence disorder (7A21); OSA (7A41); "
        "Kleine-Levin syndrome (7A22)."
    ),
    "Apneia Obstrutiva do Sono": (
        "A. Pausas respiratórias recorrentes durante o sono.\n"
        "B. Ronco forte, sono não restaurador, sonolência diurna.\n"
        "C. AHI ≥ 5 na polissonografia.",
        "Apneia central do sono (sem esforço respiratório); "
        "hipersonia (sem apneia); privação de sono; "
        "síndrome de hipoventilação; doença pulmonar obstrutiva.",
        "Apneia central do sono; ronco primário; "
        "síndrome de resistência das vias aéreas superiores; "
        "narcolepsia; hipersonia.",
        "Central sleep apnoea (7A42); Primary snoring; "
        "Narcolepsy (7A20).",
        "Central sleep apnoea (7A42); Hypersomnolence (7A21); "
        "Narcolepsy (7A20)."
    ),
    "Apneia Central do Sono": (
        "A. Pausas respiratórias sem esforço respiratório.\n"
        "B. AHI ≥ 5 com > 50% eventos centrais.\n"
        "C. Falta de ar ao deitar ou sono fragmentado.",
        "Apneia obstrutiva do sono (esforço respiratório presente); "
        "hipoventilação; insuficiência cardíaca; AVE; "
        "medicação opioide.",
        "Apneia obstrutiva do sono; hipoventilação central; "
        "insuficiência cardíaca; AVE; uso de opioides.",
        "OSA (7A41); Heart failure (BD10); "
        "Opioid-induced sleep apnoea."
    ),
    "Transtorno do Ritmo Circadiano do Sono-Vigília": (
        "A. Padrão persistente de perturbação do sono devido a alteração circadiana.\n"
        "B. Insônia ou sonolência excessiva.\n"
        "C. Prejuízo clinicamente significativo.\n"
        "D. Duração de 3+ meses.",
        "Insônia (sem alteração circadiana); hipersonia; "
        "privação voluntária de sono; trabalho noturno; "
        "depressão maior (despertar precoce).",
        "Insônia; hipersonia; distúrbio do sono por trabalho em turnos; "
        "jet lag; depressão maior; transtorno de personalidade."
    ),
    "Transtorno do Despertar do Sono Não REM (Sonambulismo)": (
        "A. Episódios repetidos de levantar e andar durante sono N3.\n"
        "B. Dificuldade em despertar, confusão ao despertar.\n"
        "C. Geralmente amnésia do evento.\n"
        "D. Causa prejuízo ou risco.",
        "Transtorno comportamental do sono REM; "
        "crise noturna (epilepsia do lobo frontal); "
        "terror noturno; amnésia dissociativa; simulação.",
        "Terror noturno; transtorno comportamental do sono REM; "
        "epilepsia noturna; sonilóquio; estado confusional.",
        "REM sleep behaviour disorder (7A40); "
        "Sleep-related hypermotor epilepsy (8A61).",
        "REM sleep behaviour disorder (7A40); Nightmare disorder (7A45); "
        "Sleep-related epilepsy (8A61)."
    ),
    "Terror Noturno": (
        "A. Episódios de gritos de medo intenso com despertar parcial do sono N3.\n"
        "B. Difícil consolar, confusão, amnésia.\n"
        "C. Causa prejuízo ou sofrimento.",
        "Pesadelo (sono REM, conteúdo onírico lembrado); "
        "crise noturna; transtorno do pânico noturno; "
        "TEPT (pesadelos traumáticos).",
        "Pesadelo; transtorno do pânico noturno; "
        "TEPT; sonambulismo; epilepsia noturna.",
        "Nightmare disorder (7A45); Panic disorder (6B01); "
        "PTSD (6B40)."
    ),
    "Transtorno do Pesadelo": (
        "A. Sonhos extensos, bem lembrados e extremamente disféricos.\n"
        "B. Geralmente envolvendo ameaça à sobrevivência.\n"
        "C. Rápido despertar com orientação preservada.\n"
        "D. Causa sofrimento ou prejuízo.",
        "Terror noturno (sono N3, amnésia); TEPT (pesadelos traumáticos recorrentes); "
        "transtorno do pânico noturno; pesadelo induzido por medicamento.",
        "TEPT; terror noturno; transtorno do pânico noturno; "
        "transtorno comportamental do sono REM; "
        "pesadelo por retirada de supressor REM."
    ),
    "Transtorno Comportamental do Sono REM": (
        "A. Episódios de vocalização e/ou movimentos complexos durante o sono REM.\n"
        "B. Sonhos representados comportamentalmente.\n"
        "C. Acordar orientado e alerta.\n"
        "D. Polissonografia mostra REM sem atonia.\n"
        "E. Não atribuível a substância ou condição médica.",
        "Sonambulismo (sono N3); epilepsia noturna; "
        "TEPT (comportamento noturno); terror noturno; "
        "doença de Parkinson; narcolepsia.",
        "Sonambulismo; epilepsia noturna; "
        "TEPT; terror noturno; narcolepsia; "
        "doença de Parkinson; demência com corpos de Lewy."
    ),
    "Síndrome das Pernas Inquietas": (
        "A. Necessidade urgente de mover as pernas com sensações desconfortáveis.\n"
        "B. Piora ao repouso, melhora com movimento.\n"
        "C. Piora à noite.\n"
        "D. 3+ vezes/semana.\n"
        "E. Causa prejuízo ou sofrimento.",
        "Cãibras noturnas; neuropatia periférica; claudicação; "
        "acatisia (medicação); doença vascular periférica; "
        "artrite; posição desconfortável; mioclonia noturna."
    ),

"Transtorno do Sono Induzido por Substância": (
        'A. Os sintomas são consistentes com disfunção sexual/outro transtorno, mas são inteiramente atribuíveis aos efeitos fisiológicos diretos de uma substância (droga de abuso, medicamento ou toxina).\nB. Os sintomas não são mais bem explicados por um transtorno primário ou outra condição médica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Insônia; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Outro Transtorno do Sono-Vigília Especificado": (
        'A. Sintomas característicos de transtorno de insônia que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno de insônia, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Insônia; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno do Sono-Vigília Não Especificado": (
        'A. Sintomas característicos de transtorno de insônia que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno de Insônia; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 13: Disfunções Sexuais ═══
    "Ejaculação Retardada": (
        "A. Atraso acentuado ou ausência de ejaculação.\n"
        "B. Presente em 75-100% das atividades sexuais.\n"
        "C. Duração de 6+ meses.\n"
        "D. Causa sofrimento clinicamente significativo.\n"
        "E. Não atribuível exclusivamente a relação, substância ou condição médica grave.",
        "Ejaculação retardada devido a medicamento (ISRS, antipsicóticos); "
        "condição neurológica (lesão medular, neuropatia); "
        "hipogonadismo; cirurgia pélvica; ansiedade de desempenho."
    ),
    "Transtorno Erétil": (
        "A. Dificuldade em obter/manter ereção.\n"
        "B. 75-100% das oportunidades.\n"
        "C. 6+ meses.\n"
        "D. Sofrimento significativo.\n"
        "E. Não atribuível a estresse relacional, substância ou condição médica grave.",
        "Disfunção erétil por condição médica (vascular, neurológica, hormonal); "
        "medicação (antidepressivos, anti-hipertensivos); "
        "transtorno de ansiedade; transtorno depressivo."
    ),
    "Transtorno do Orgasmo Feminino": (
        "A. Ausência ou atraso acentuado do orgasmo.\n"
        "B. 75-100% das oportunidades.\n"
        "C. 6+ meses.\n"
        "D. Sofrimento significativo.\n"
        "E. Não atribuível a estresse, substância ou condição médica.",
        "Anorgasmia devido a medicamento (ISRS); "
        "condição neurológica; trauma pélvico; "
        "transtorno de interesse/excitação sexual; vaginismo."
    ),
    "Transtorno do Interesse/Excitação Sexual Feminino": (
        "A. Falta ou redução do interesse/excitação sexual.\n"
        "B. 6+ meses.\n"
        "C. Sofrimento significativo.\n"
        "D. Não atribuível a estresse, transtorno mental, substância ou condição médica.",
        "Transtorno depressivo maior (anedonia); "
        "transtorno de ansiedade; uso de ISRS; "
        "disfunção sexual relacionada a trauma; "
        "menopausa; hipotireoidismo."
    ),
    "Transtorno da Dor Gênito-Pélvica/Penetração": (
        "A. Dificuldade persistente com penetração vaginal.\n"
        "B. Dor pélvica durante tentativa.\n"
        "C. Medo de dor.\n"
        "D. Tensão dos músculos pélvicos.\n"
        "E. 6+ meses.\n"
        "F. Sofrimento significativo.",
        "Condição médica (infecção, endometriose, vaginismo); "
        "TEPT (trauma sexual); transtorno de ansiedade; "
        "vaginismo primário; dispareunia."
    ),
    "Transtorno do Desejo Sexual Hipoativo Masculino": (
        "A. Déficit de desejo/ideação sexual.\n"
        "B. 6+ meses.\n"
        "C. Sofrimento significativo.\n"
        "D. Não atribuível a estresse, transtorno, substância ou condição médica.",
        "TDM (anedonia); hipogonadismo; "
        "medicação (ISRS, anti-hipertensivos); "
        "transtorno de ansiedade de desempenho; "
        "estresse relacional."
    ),
    "Ejaculação Prematura": (
        "A. Ejaculação antes ou logo após a penetração (~1 minuto).\n"
        "B. Presente em 75-100% das atividades.\n"
        "C. 6+ meses.\n"
        "D. Sofrimento significativo.\n"
        "E. Não atribuível a substância.",
        "Ejaculação prematura devido a substância (abstinência de opioides); "
        "prostatite; hipertireoidismo; "
        "ansiedade de desempenho; transtorno erétil associado."
    ),

"Disfunção Sexual Induzida por Substância": (
        'A. Os sintomas são consistentes com disfunção sexual/outro transtorno, mas são inteiramente atribuíveis aos efeitos fisiológicos diretos de uma substância (droga de abuso, medicamento ou toxina).\nB. Os sintomas não são mais bem explicados por um transtorno primário ou outra condição médica.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Erétil; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Outra Disfunção Sexual Especificada": (
        'A. Sintomas característicos de transtorno erétil que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno erétil, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Erétil; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Disfunção Sexual Não Especificada": (
        'A. Sintomas característicos de transtorno erétil que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Erétil; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 14: Disforia de Gênero ═══
    "Disforia de Gênero em Crianças": (
        "A. Incongruência marcante entre gênero experienciado/expresso e gênero designado por 6+ meses.\n"
        "B. 6+ critérios: forte desejo de ser do outro gênero, preferência por roupas do outro "
        "gênero, papéis de faz-de-conta, brinquedos/atividades tipicamente do outro gênero, "
        "preferência por brincar com crianças do outro gênero, aversão a características sexuais "
        "próprias.\n"
        "C. Causa sofrimento ou prejuízo.",
        "Transtorno de personalidade (adulto); inconformidade de gênero sem disforia; "
        "comportamento cross-gender não patológico; TEA (interesse fixo em cross-gender); "
        "esquizofrenia (delírio de pertencer ao outro sexo).",
        "Inconformidade de gênero (sem sofrimento); TEA; "
        "TOC (obsessões com identidade de gênero); "
        "transtorno de personalidade borderline; transtorno transvéstico.",
        "Gender incongruence without distress; Autism spectrum disorder (6A02); "
        "Transvestic disorder (6D30).",
        "Autism spectrum disorder (6A02); Body dysmorphic disorder (6B21); "
        "Transvestic disorder (6D30)."
    ),
    "Disforia de Gênero em Adolescentes e Adultos": (
        "A. Incongruência marcante entre gênero experienciado e designado por 6+ meses.\n"
        "B. 2+ critérios: incongruência entre sexo primário/secundário e gênero, forte desejo "
        "de livrar-se das características sexuais, forte desejo de pertencer ao outro gênero, "
        "forte desejo de ser tratado como o outro gênero.\n"
        "C. Causa sofrimento ou prejuízo.",
        "Inconformidade de gênero sem disforia; travestismo fetichista; "
        "esquizofrenia; TOC; transtorno de personalidade borderline; "
        "transtorno dismórfico corporal.",
        "Disforia de gênero em crianças (idade); inconformidade de gênero; "
        "transtorno transvéstico; TEA; TOC; esquizofrenia.",
        "Gender incongruence without distress; Transvestic disorder (6D30); "
        "Body dysmorphic disorder (6B21); Schizophrenia (6A20).",
        "Gender incongruence; Transvestic disorder (6D30); "
        "OCD (6B20); Body dysmorphic disorder (6B21)."
    ),

"Outra Disforia de Gênero Especificada": (
        'A. Sintomas característicos de disforia de gênero em crianças que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para disforia de gênero em crianças, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Disforia de Gênero em Crianças; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Disforia de Gênero Não Especificada": (
        'A. Sintomas característicos de disforia de gênero em crianças que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Disforia de Gênero em Crianças; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 15: Transtornos Disruptivos ═══
    "Transtorno Opositivo-Desafiador": (
        "A. Padrão de humor raivoso/irritável, comportamento questionador/desafiador ou "
        "vingativo por 6+ meses com 4+ sintomas.\n"
        "B. Causa prejuízo no funcionamento social/acadêmico.\n"
        "C. Não ocorre exclusivamente durante psicose, TDM ou transtorno disruptivo.",
        "Transtorno explosivo intermitente (explosões agressivas impulsivas); "
        "transtorno da conduta (violação de direitos dos outros); "
        "TDAH (desatenção/impulsividade sem oposição); "
        "depressão maior (irritabilidade); transtorno bipolar.",
        "TDAH; transtorno explosivo intermitente; transtorno da conduta; "
        "depressão maior; transtorno bipolar; "
        "comportamento opositivo normal (adolescência); TEA.",
        "ADHD (6A05); Conduct disorder (6C91); "
        "Intermittent explosive disorder (6C70); Bipolar disorder (6A60-6A61).",
        "ADHD (6A05); Conduct disorder (6C91); Bipolar disorder (6A60-6A61); "
        "Major depressive disorder (6A70-6A71)."
    ),
    "Transtorno Explosivo Intermitente": (
        "A. Explosões comportamentais impulsivas e agressivas desproporcionais.\n"
        "B. Média de 2+ explosões/semana por 3 meses (ou 3+ explosões com dano em 12 meses).\n"
        "C. Prejuízo ou sofrimento.\n"
        "D. Não atribuível a transtorno mental, substância ou condição médica.",
        "TOD (humor irritável crônico); transtorno da conduta (violação de regras); "
        "TDAH (impulsividade sem agressividade); "
        "transtorno de personalidade antissocial/borderline; "
        "delirium; demência; traumatismo cranioencefálico; epilepsia.",
        "TOD; TDAH; transtorno da conduta; "
        "transtorno de personalidade borderline; "
        "depressão com irritabilidade; mania; "
        "transtorno disruptivo da desregulação do humor.",
        "ODD (6C90); Conduct disorder (6C91); ADHD (6A05); "
        "Disruptive mood dysregulation disorder (6A73).",
        "ODD (6C90); Conduct disorder (6C91); ADHD (6A05); "
        "Borderline personality disorder (6D11)."
    ),
    "Transtorno da Conduta": (
        "A. Padrão repetitivo de violação de direitos básicos dos outros ou normas sociais.\n"
        "B. 3+ critérios em 12 meses: agressão, destruição, engano, furto, violação grave de regras.\n"
        "C. Prejuízo clinicamente significativo.\n"
        "D. Início antes dos 18 anos.\n"
        "E. Se 18+, critérios para TPAS não preenchidos.",
        "TDAH (impulsividade sem violação de direitos); TOD (sem agressão grave); "
        "transtorno explosivo intermitente (explosões impulsivas); "
        "depressão/mania (irritabilidade); TEPT; abuso; transtorno de adaptação.",
        "TOD; TDAH; TPAS; transtorno explosivo intermitente; "
        "depressão maior; transtorno bipolar; "
        "transtorno por uso de substância; psicose.",
        "ODD (6C90); ADHD (6A05); Antisocial personality disorder (6D11); "
        "Intermittent explosive disorder (6C70).",
        "ODD (6C90); ADHD (6A05); Antisocial personality disorder (6D11); "
        "Bipolar disorder (6A60-6A61)."
    ),
    "Piromania": (
        "A. Incêndio deliberado em múltiplas ocasiões.\n"
        "B. Tensão antes do ato.\n"
        "C. Fascínio por fogo.\n"
        "D. Prazer ao causar incêndios.\n"
        "E. Não para ganho, vingança ou devido a psicose.",
        "Transtorno da conduta (incêndio como parte de comportamento antissocial); "
        "TPAS; transtorno explosivo intermitente; "
        "esquizofrenia (delírio); transtorno neurocognitivo; "
        "intoxicação por substância.",
        "Transtorno da conduta; TPAS; transtorno explosivo intermitente; "
        "esquizofrenia; mania; intoxicação; demência."
    ),
    "Cleptomania": (
        "A. Falha recorrente em resistir a impulsos de furtar objetos.\n"
        "B. Sensação de tensão antes do furto.\n"
        "C. Prazer ou alívio durante o furto.\n"
        "D. Não por vingança ou delírio.\n"
        "E. Causa prejuízo ou sofrimento.",
        "Furto comum (planejado, por ganho); transtorno da conduta/TPAS; "
        "transtorno bipolar (comportamento impulsivo); "
        "esquizofrenia; TOC; transtorno neurocognitivo; "
        "transtorno factício."
    ),

"Outro Transtorno Disruptivo Especificado": (
        'A. Sintomas característicos de transtorno opositivo-desafiador que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno opositivo-desafiador, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Opositivo-Desafiador; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Disruptivo Não Especificado": (
        'A. Sintomas característicos de transtorno opositivo-desafiador que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Opositivo-Desafiador; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 16: Transtornos por Substâncias ═══
    "Transtorno por Uso de Álcool": (
        "A. Padrão problemático de uso de álcool com 2+ critérios em 12 meses (mesmos 11 do TUS).\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de álcool; intoxicação alcoólica sem transtorno; "
        "transtorno bipolar (uso secundário); TPAS.",
        "Transtorno bipolar; TPAS; depressão maior; "
        "transtorno de ansiedade social; TEPT.",
        "Hazardous alcohol use (QE10); Bipolar disorders (6A60-6A61).",
        "Bipolar disorders (6A60-6A61); Depressive disorders (6A70-6A71); "
        "PTSD (6B40); Social anxiety disorder (6B04)."
    ),
    "Intoxicação Alcoólica": (
        "A. Sintomas reversíveis após ingestão recente de álcool: fala arrastada, incoordenação, "
        "marcha instável, nistagmo, prejuízo de atenção/memória, estupor/coma.\n"
        "B. Não atribuível a condição médica.",
        "Intoxicação por outra substância; trauma cranioencefálico; "
        "encefalopatia; hipoglicemia; delirium; AVE."
    ),
    "Abstinência Alcoólica": (
        "A. Sintomas após cessação/redução do uso de álcool: hiperatividade autonômica, "
        "tremor, insônia, náusea, alucinações, agitação, ansiedade, convulsões.\n"
        "B. Causa sofrimento ou prejuízo.",
        "Ansiedade generalizada; transtorno do pânico; "
        "intoxicação por estimulante; delirium tremens; "
        "encefalopatia de Wernicke; convulsão por abstinência alcoólica."
    ),
    "Transtorno por Uso de Cannabis": (
        "A. Padrão problemático de uso de cannabis com 2+ dos seguintes critérios em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância\n"
        "11. abstinência (irritabilidade, ansiedade, insônia, diminuição apetite, humor deprimido)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de cannabis; intoxicação canábica sem transtorno; "
        "transtorno de ansiedade primário; transtorno do pânico; "
        "síndrome amotivacional sem uso atual; transtorno bipolar.",
        "Transtorno de ansiedade social; TAG; transtorno do pânico; "
        "transtorno bipolar; depressão maior; TDAH; "
        "transtorno de personalidade borderline; síndrome amotivacional.",
        "Hazardous cannabis use (QE12); Cannabis intoxication (6C41.1); "
        "Bipolar disorders (6A60-6A61).",
        "Bipolar disorders (6A60-6A61); Depressive disorders (6A70-6A71); "
        "Anxiety disorders (6B00-6B0Z); ADHD (6A05)."
    ),
    "Transtorno por Uso de Alucinógenos": (
        "A. Padrão problemático de uso de alucinógenos (incluindo LSD, dissociativos, "
        "feniclidina) com 2+ dos seguintes critérios em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância (cruzada com outros alucinógenos)\n"
        "11. abstinência (não bem estabelecida para esta classe)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de alucinógenos; intoxicação alucinógena sem transtorno; "
        "transtorno psicótico primário (esquizofrenia); transtorno delirante; "
        "transtorno de pânico com flashbacks.",
        "Esquizofrenia; transtorno esquizofreniforme; transtorno delirante; "
        "transtorno psicótico breve; transtorno de pânico; "
        "transtorno de estresse pós-traumático; enxaqueca com aura.",
        "LSD use disorder (6C43.0); Dissociative drug use disorder (6C44); "
        "Phencyclidine use disorder (6C45); Schizophrenia (6A20).",
        "Schizophrenia (6A20); Brief psychotic disorder (6A23); "
        "Delusional disorder (6A24); Panic disorder (6B01); PTSD (6B40)."
    ),
    "Transtorno por Uso de Inalantes": (
        "A. Padrão problemático de uso de inalantes (hidrocarbonetos voláteis) com 2+ critérios "
        "em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância\n"
        "11. abstinência (não bem estabelecida para esta classe)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de inalantes; intoxicação por inalante sem transtorno; "
        "transtorno neurocognitivo devido a exposição crônica a inalantes; "
        "transtorno por uso de outra substância.",
        "Transtorno neurocognitivo maior/leve (exposição crônica a inalantes); "
        "transtorno por uso de álcool ou outras substâncias; "
        "transtorno da conduta (comportamento antissocial associado).",
        "Inhalant use disorder (6C46); "
        "Neurocognitive disorder due to inhalant exposure (6D7Y).",
        "Alcohol use disorder (6C41); Stimulant use disorders (6C47-6C48); "
        "Conduct disorder (6C91)."
    ),
    "Transtorno por Uso de Opioides": (
        "A. Padrão problemático de uso de opioides com 2+ dos seguintes critérios em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância\n"
        "11. abstinência (humor disfórico, náusea, sudorese, midríase, diarreia, lacrimejamento, "
        "bocejos, febre, insônia)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de opioides; dor crônica com uso adequado de opioides; "
        "síndrome de abstinência opioide sem transtorno; "
        "intoxicação opioide não problemática.",
        "Transtorno depressivo maior (anedonia); transtorno de ansiedade; "
        "síndrome de dor crônica primária; transtorno de personalidade borderline; "
        "transtorno factício com sintomas de dor.",
        "Opioid use disorder (6C40); Opioid intoxication (6C40.1); "
        "Opioid withdrawal (6C40.3).",
        "Depressive disorders (6A70-6A71); Chronic pain (MG30); "
        "Borderline personality disorder (6D11); Factitious disorder (6D50)."
    ),
    "Transtorno por Uso de Sedativos/Hipnóticos/Ansiolíticos": (
        "A. Padrão problemático de uso de sedativos/hipnóticos/ansiolíticos (benzodiazepínicos, "
        "barbitúricos, Z-drugs) com 2+ critérios em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância\n"
        "11. abstinência (hiperatividade autonômica, tremor, insônia, ansiedade, náusea, "
        "alucinações, convulsões, delirium)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de sedativos; uso terapêutico sob prescrição; "
        "transtorno de ansiedade primário (TAG, pânico) com uso secundário; "
        "transtorno do sono primário; abstinência alcoólica.",
        "TAG; transtorno do pânico; transtorno de ansiedade social; "
        "insônia primária; transtorno depressivo maior; "
        "transtorno bipolar (uso de sedativos para mania).",
        "Sedative/hypnotic/anxiolytic use disorder (6C42); "
        "Benzodiazepine withdrawal (6C42.3); GAD (6B00); Panic disorder (6B01).",
        "GAD (6B00); Panic disorder (6B01); Insomnia disorders (7A00-7A01); "
        "Depressive disorders (6A70-6A71); Alcohol use disorder (6C41)."
    ),
    "Transtorno por Uso de Estimulantes": (
        "A. Padrão problemático de uso de estimulantes (cocaína, anfetaminas, metanfetamina, "
        "metilfenidato) com 2+ critérios em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância\n"
        "11. abstinência (humor disfórico, fadiga, sonhos vívidos, insônia/hipersonia, aumento "
        "apetite, agitação psicomotora)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de estimulantes; uso terapêutico sob prescrição (TDAH); "
        "transtorno bipolar (uso secundário ou estado misto); "
        "TDAH com uso de medicamento estimulante prescrito; transtorno de ansiedade.",
        "Transtorno bipolar (mania/hipomania induzida por estimulantes); "
        "TDAH; transtorno de ansiedade; TAG; "
        "transtorno do pânico; transtorno de personalidade borderline; "
        "transtorno psicótico induzido por estimulantes.",
        "Cocaine use disorder (6C47); Amphetamine use disorder (6C48); "
        "Cocaine intoxication (6C47.1); Stimulant withdrawal (6C48.3); "
        "Bipolar disorders (6A60-6A61).",
        "Bipolar disorders (6A60-6A61); ADHD (6A05); "
        "Psychotic disorders (6A20-6A2Z); Panic disorder (6B01)."
    ),
    "Transtorno por Uso de Tabaco": (
        "A. Padrão problemático de uso de tabaco com 2+ dos seguintes critérios em 12 meses:\n"
        "1. consumido em quantidades maiores ou por mais tempo que o pretendido\n"
        "2. desejo persistente ou esforços malsucedidos para reduzir/controlar\n"
        "3. muito tempo gasto obtendo/usando/recuperando-se\n"
        "4. fissura\n"
        "5. falha em cumprir obrigações\n"
        "6. uso continuado apesar de problemas sociais\n"
        "7. atividades abandonadas/reduzidas\n"
        "8. uso em situações de perigo\n"
        "9. uso continuado apesar de problema físico/psicológico\n"
        "10. tolerância (perda do efeito estimulante)\n"
        "11. abstinência (irritabilidade, ansiedade, dificuldade de concentração, aumento apetite, "
        "humor deprimido, insônia)\n"
        "B. Especificadores: leve (2-3), moderado (4-5), grave (6+).",
        "Uso não problemático de tabaco; nicotina de reposição terapêutica; "
        "transtorno depressivo maior com tabagismo secundário; "
        "transtorno de ansiedade com tabagismo secundário.",
        "Transtorno depressivo maior; TAB; TAG; "
        "transtorno de ansiedade social; TDAH; "
        "transtorno por uso de álcool/cannabis (poli-uso); "
        "esquizofrenia (alta prevalência de tabagismo).",
        "Tobacco use disorder (6C4A); Nicotine withdrawal (6C4A.3); "
        "Hazardous tobacco use (QE11).",
        "Depressive disorders (6A70-6A71); Anxiety disorders (6B00-6B0Z); "
        "Schizophrenia (6A20); Alcohol use disorder (6C41)."
    ),
    "Transtorno do Jogo (Jogo Patológico)": (
        "A. Comportamento problemático de jogo com 4+ dos seguintes critérios em 12 meses:\n"
        "1. necessidade de apostar quantias crescentes para atingir excitação\n"
        "2. inquietação ou irritabilidade ao tentar reduzir/parar\n"
        "3. esforços repetidos malsucedidos para controlar\n"
        "4. preocupação com jogo (reviver experiências, planejar)\n"
        "5. joga quando se sente angustiado\n"
        "6. volta no outro dia para recuperar perdas\n"
        "7. mente para esconder envolvimento\n"
        "8. põe em risco relacionamentos/trabalho\n"
        "9. depende de outros financeiramente\n"
        "B. O comportamento de jogo não é melhor explicado por episódio maníaco.",
        "Jogo social ou profissional sem prejuízo; "
        "transtorno bipolar (jogo excessivo durante mania/hipomania); "
        "transtorno de personalidade antissocial; "
        "transtorno obsessivo-compulsivo (jogo como compulsão?); "
        "transtorno por uso de substância (jogo associado a álcool).",
        "Transtorno bipolar (episódio maníaco com gastos excessivos); "
        "TPAS; TOC; transtorno explosivo intermitente; "
        "transtorno por uso de álcool ou outras substâncias; "
        "jogo problemático (subclínico, sem 4 critérios).",
        "Gambling disorder (6C50); Bipolar type I disorder (6A60); "
        "OCD (6B20); Antisocial personality disorder (6D11).",
        "Bipolar type I disorder (6A60); OCD (6B20); "
        "Antisocial personality disorder (6D11); Substance use disorders (6C4)."
    ),

    # ═══ CHAPTER 17: Transtornos Neurocognitivos ═══
    "Delirium": (
        "A. Perturbação na atenção (capacidade reduzida de dirigir, focar, sustentar e "
        "desviar a atenção) e na consciência (orientação reduzida ao ambiente).\n"
        "B. Desenvolvimento em horas a dias e tendência a flutuar ao longo do dia.\n"
        "C. Déficit cognitivo adicional (memória, orientação, linguagem, percepção).\n"
        "D. Não é melhor explicado por transtorno neurocognitivo preexistente.\n"
        "E. Evidência de causa fisiológica direta (condição médica, intoxicação/abstinência, "
        "toxina, múltiplas etiologias).",
        "Demência (início insidioso, declínio progressivo, sem flutuação); "
        "transtorno neurocognitivo leve; esquizofrenia (sem flutuação); "
        "transtorno psicótico breve; depressão maior (pseudodemência); "
        "AVE; encefalite; estado de mal epiléptico não-convulsivo.",
        "Demência; transtorno neurocognitivo maior; delírio sobreposto à demência; "
        "transtorno psicótico induzido por substância; esquizofrenia; "
        "mania (agitação); depressão psicótica; encefalopatia metabólica; "
        "encefalopatia de Wernicke; abstinência alcoólica.",
        "Delirium (6D70); Dementia (6D71-6D7Z); "
        "Substance intoxication/withdrawal (6C4E).",
        "Dementia (6D71-6D7Z); Psychotic disorders (6A20-6A2Z); "
        "Wernicke encephalopathy (5B51); Encephalitis (1D00)."
    ),
    "Transtorno Neurocognitivo Maior": (
        "A. Declínio cognitivo significativo em 1+ domínios (atenção complexa, função executiva, "
        "aprendizagem/memória, linguagem, percepto-motora, cognição social) baseado em:\n"
        "1. preocupação do paciente, informante ou clínico\n"
        "2. prejuízo substancial em testes cognitivos padronizados\n"
        "B. Os déficits cognitivos interferem na independência nas atividades da vida diária.\n"
        "C. Não ocorre exclusivamente no contexto de delirium.\n"
        "D. Não é melhor explicado por outro transtorno mental.",
        "Transtorno neurocognitivo leve (independência preservada); "
        "delirium (início agudo, flutuação, alteração de consciência); "
        "depressão maior (pseudodemência, declínio cognitivo reversível); "
        "esquizofrenia (declínio do período do desenvolvimento); simulação.",
        "Transtorno neurocognitivo leve; delirium; depressão maior; "
        "transtorno factício; simulação; "
        "TDAH em adultos; deficiência intelectual; TEA; "
        "transtorno psicótico; envelhecimento normal.",
        "Delirium (6D70); Major neurocognitive disorder due to Alzheimer (6D71); "
        "Vascular dementia (6D72); Frontotemporal dementia (6D81); "
        "Dementia with Lewy bodies (6D82).",
        "Mild neurocognitive disorder (6D7Y); Depression (6A70-6A71); "
        "Schizophrenia (6A20); ADHD (6A05); Factitious disorder (6D50)."
    ),
    "Transtorno Neurocognitivo Leve": (
        "A. Declínio cognitivo modesto em 1+ domínios (atenção complexa, função executiva, "
        "aprendizagem/memória, linguagem, percepto-motora, cognição social) baseado em:\n"
        "1. preocupação do paciente, informante ou clínico\n"
        "2. prejuízo modesto em testes cognitivos padronizados\n"
        "B. Os déficits cognitivos NÃO interferem na independência (mas podem exigir maior esforço).\n"
        "C. Não ocorre exclusivamente no contexto de delirium.\n"
        "D. Não é melhor explicado por outro transtorno mental.",
        "Transtorno neurocognitivo maior (independência prejudicada); "
        "delirium; depressão maior; ansiedade; "
        "privação de sono; efeito de substância; envelhecimento normal; "
        "deficiência intelectual; TDAH; TEA.",
        "Transtorno neurocognitivo maior; depressão maior; "
        "ansiedade generalizada; TDAH; "
        "transtorno neurocognitivo induzido por substância; "
        "envelhecimento cognitivo normal; privação de sono; "
        "transtorno factício; simulação.",
        "Mild neurocognitive disorder (6D7Y); "
        "Major neurocognitive disorder (6D71-6D7Z); "
        "Delirium (6D70); Normal ageing (MG2A).",
        "Major neurocognitive disorder (6D71-6D7Z); "
        "Depressive disorders (6A70-6A71); ADHD (6A05); "
        "Anxiety disorders (6B00-6B0Z); Substance-related disorders (6C4)."
    ),

"Transtorno Neurocognitivo Maior — Degeneração Lobar Frontotemporal": (
        'A. Preenche os critérios para transtorno neurocognitivo maior.\nB. A etiologia é atribuída a degeneração lobar frontotemporal (mutações nos genes mapt, grn, c9orf72), conforme evidenciado por história clínica, exame físico e exames complementares.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Neurocognitivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Neurocognitivo Maior — Corpos de Lewy": (
        'A. Preenche os critérios para transtorno neurocognitivo maior.\nB. A etiologia é atribuída a doença de corpos de lewy difusos (depósitos de alfa-sinucleína no córtex), conforme evidenciado por história clínica, exame físico e exames complementares.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Neurocognitivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Neurocognitivo Maior — Vascular": (
        'A. Preenche os critérios para transtorno neurocognitivo maior.\nB. A etiologia é atribuída a doença cerebrovascular (infartos múltiplos ou extensos, lesão da substância branca), conforme evidenciado por história clínica, exame físico e exames complementares.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Neurocognitivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Neurocognitivo Maior — Traumatismo Cranioencefálico": (
        'A. Preenche os critérios para transtorno neurocognitivo maior.\nB. A etiologia é atribuída a traumatismo cranioencefálico (lesão cerebral traumática com perda de consciência ou amnésia pós-traumática), conforme evidenciado por história clínica, exame físico e exames complementares.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Neurocognitivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Outro Transtorno Neurocognitivo Especificado": (
        'A. Sintomas característicos de transtorno neurocognitivo maior que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno neurocognitivo maior, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Neurocognitivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Neurocognitivo Não Especificado": (
        'A. Sintomas característicos de transtorno neurocognitivo maior que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Neurocognitivo Maior; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 18: Transtornos da Personalidade ═══
    "Transtorno da Personalidade Paranoide": (
        "A. Desconfiança generalizada de que os outros estão explorando, enganando ou "
        "prejudicando, presente desde o início da vida adulta, com 4+:\n"
        "1. suspeita sem fundamento de que outros estão prejudicando\n"
        "2. preocupação com dúvidas sobre lealdade/confiança\n"
        "3. relutância em confiar nos outros\n"
        "4. percebe significados ocultos em comentários benignos\n"
        "5. guarda rancor persistentemente\n"
        "6. reage exageradamente a ameaças percebidas\n"
        "7. suspeita da fidelidade sexual.\n"
        "B. Não ocorre exclusivamente durante esquizofrenia, transtorno bipolar ou outro transtorno psicótico.",
        "Esquizofrenia paranoide (delírios fixos, alucinações); "
        "transtorno delirante (delírios não-bizarros sem desconfiança generalizada); "
        "transtorno de personalidade esquizotípica (crenças estranhas, pensamento mágico); "
        "transtorno de personalidade borderline (instabilidade relacional); "
        "transtorno de personalidade narcisista (inveja, arrogância).",
        "Esquizofrenia (6A20); transtorno delirante (6A24); "
        "TP esquizotípica (6D12); TP borderline (6D11); "
        "transtorno de ansiedade social (medo de avaliação).",
        "Schizophrenia (6A20); Delusional disorder (6A24); "
        "Schizotypal disorder (6D12); Borderline PD (6D11).",
        "Schizophrenia (6A20); Schizotypal disorder (6D12); "
        "Delusional disorder (6A24); Social anxiety disorder (6B04)."
    ),
    "Transtorno da Personalidade Esquizoide": (
        "A. Padrão de distanciamento social e restrição de expressão emocional, presente desde "
        "o início da vida adulta, com 4+:\n"
        "1. não deseja nem gosta de relacionamentos próximos\n"
        "2. prefere atividades solitárias\n"
        "3. pouco ou nenhum interesse em experiências sexuais\n"
        "4. prazer em poucas ou nenhuma atividade\n"
        "5. falta de amigos próximos ou confidentes\n"
        "6. indiferente a críticas ou elogios\n"
        "7. afeto embotado, distanciamento emocional.\n"
        "B. Não ocorre exclusivamente durante esquizofrenia, transtorno bipolar ou TEA.",
        "Esquizofrenia (delírios, alucinações, sintomas negativos proeminentes); "
        "transtorno de personalidade esquizotípica (distorções perceptivas); "
        "TEA (interesses restritos, déficits de comunicação social); "
        "depressão maior (anedonia, retraimento social).",
        "TEA; TP esquizotípica; TP paranoide; "
        "esquizofrenia (pródromo); depressão maior; "
        "TP esquiva (deseja relacionamentos mas evita por medo).",
        "Schizophrenia (6A20); Schizotypal disorder (6D12); "
        "Autism spectrum disorder (6A02).",
        "Autism spectrum disorder (6A02); Schizotypal disorder (6D12); "
        "Avoidant personality disorder (6D10); Depressive disorders (6A70-6A71)."
    ),
    "Transtorno da Personalidade Esquizotípica": (
        "A. Padrão de déficits sociais e interpessoais com desconforto agudo e distorções "
        "cognitivas/perceptivas, presente desde o início da vida adulta, com 5+:\n"
        "1. ideias de referência\n"
        "2. crenças estranhas ou pensamento mágico\n"
        "3. experiências perceptivas incomuns\n"
        "4. pensamento e fala estranhos\n"
        "5. desconfiança ou ideação paranoide\n"
        "6. afeto inadequado ou restrito\n"
        "7. comportamento ou aparência excêntrica\n"
        "8. falta de amigos próximos\n"
        "9. ansiedade social excessiva que não diminui com familiaridade.\n"
        "B. Não ocorre exclusivamente durante esquizofrenia, transtorno bipolar ou TEA.",
        "Esquizofrenia (sintomas psicóticos francos, duração 6+ meses); "
        "transtorno delirante (delírio fixo sem pensamento desorganizado); "
        "TEA (interesses restritos, linguagem concreta); "
        "TP paranoide (desconfiança sem pensamento mágico).",
        "Esquizofrenia; TP paranoide; TP esquizoide; "
        "TEA; TOC (crenças estranhas?); "
        "transtorno de ansiedade social (sem distorções perceptivas).",
        "Schizophrenia (6A20); Delusional disorder (6A24); "
        "Autism spectrum disorder (6A02); Schizoid PD (6D12).",
        "Schizophrenia (6A20); Autism spectrum disorder (6A02); "
        "Paranoid PD (6D12); Schizoid PD (6D12); Social anxiety disorder (6B04)."
    ),
    "Transtorno da Personalidade Borderline": (
        "A. Padrão de instabilidade nas relações interpessoais, autoimagem e afetos, e "
        "impulsividade acentuada, presente desde o início da vida adulta, com 5+:\n"
        "1. esforços desesperados para evitar abandono real ou imaginado\n"
        "2. relacionamentos intensos e instáveis (idealização/depreciação)\n"
        "3. perturbação da identidade (autoimagem instável)\n"
        "4. impulsividade em 2+ áreas (gastos, sexo, substâncias, direção, alimentação)\n"
        "5. comportamento suicida, gestos ou automutilação recorrentes\n"
        "6. instabilidade afetiva (episódios de disforia, irritabilidade, ansiedade)\n"
        "7. sensação crônica de vazio\n"
        "8. raiva intensa e inadequada ou dificuldade de controlá-la\n"
        "9. ideação paranoide transitória ou sintomas dissociativos sob estresse.\n"
        "B. Não ocorre exclusivamente durante depressão maior ou transtorno bipolar.",
        "Transtorno bipolar (episódios distintos, humor elevado/irritável); "
        "depressão maior (episódios distintos); "
        "TP histriônica (instabilidade emocional, busca de atenção); "
        "TP narcisista (grandiosidade, falta de empatia); "
        "TP antissocial (impulsividade, manipulação); "
        "TEPT (história de trauma, revivência).",
        "Transtorno bipolar tipo I/II; depressão maior; "
        "transtorno ciclotímico; TP histriônica; "
        "TP narcisista; TDAH; TEPT; "
        "transtorno dissociativo de identidade; transtorno por uso de substância.",
        "Bipolar disorders (6A60-6A61); Depressive disorders (6A70-6A71); "
        "Histrionic PD (6D11); PTSD (6B40); Cyclothymic disorder (6A62).",
        "Bipolar disorders (6A60-6A61); Depressive disorders (6A70-6A71); "
        "PTSD (6B40); ADHD (6A05); Substance use disorders (6C4)."
    ),
    "Transtorno da Personalidade Histriônica": (
        "A. Padrão de emocionalidade excessiva e busca de atenção, presente desde o início "
        "da vida adulta, com 5+:\n"
        "1. desconforto quando não é o centro das atenções\n"
        "2. comportamento sedutor ou provocativo inadequado\n"
        "3. emoções superficiais que mudam rapidamente\n"
        "4. usa aparência física para chamar atenção\n"
        "5. fala impressionista (carente de detalhes)\n"
        "6. teatral, exagerado\n"
        "7. sugestionável (influenciado por outros)\n"
        "8. considera relações mais íntimas do que realmente são.\n"
        "B. Não ocorre exclusivamente durante depressão maior ou transtorno bipolar.",
        "TP borderline (instabilidade, automutilação, vazio); "
        "TP narcisista (grandiosidade, necessidade de admiração); "
        "transtorno bipolar (episódios maníacos/hipomaníacos); "
        "transtorno dismórfico corporal; transtorno conversivo; "
        "transtorno factício.",
        "TP borderline; TP narcisista; TP antissocial; "
        "transtorno de conversão; transtorno dismórfico corporal; "
        "transtorno bipolar; TDAH; transtorno por uso de substância.",
        "Borderline PD (6D11); Narcissistic PD (6D11); "
        "Bipolar disorders (6A60-6A61); Conversion disorder (6B60).",
        "Borderline PD (6D11); Narcissistic PD (6D11); "
        "Bipolar disorders (6A60-6A61); Body dysmorphic disorder (6B21)."
    ),
    "Transtorno da Personalidade Narcisista": (
        "A. Padrão de grandiosidade, necessidade de admiração e falta de empatia, presente "
        "desde o início da vida adulta, com 5+:\n"
        "1. senso grandioso de importância (exagera realizações, espera ser reconhecido como superior)\n"
        "2. preocupação com fantasias de sucesso, poder, beleza ou amor ideal\n"
        "3. acredita ser especial e único\n"
        "4. exige admiração excessiva\n"
        "5. sente-se no direito (expectativas irracionais de tratamento favorável)\n"
        "6. explora os outros para atingir seus fins\n"
        "7. falta de empatia (reluta em reconhecer sentimentos alheios)\n"
        "8. inveja dos outros ou acredita que outros o invejam\n"
        "9. atitude arrogante, insolente.\n"
        "B. Não ocorre exclusivamente durante transtorno bipolar, TPAS ou TUS.",
        "Transtorno bipolar (mania/hipomania com grandiosidade); "
        "TP antissocial (impulsividade, violação de regras); "
        "TP histriônica (busca de atenção sem grandiosidade); "
        "TP borderline (instabilidade, raiva, mas sem grandiosidade); "
        "transtorno por uso de substância; anorexia nervosa.",
        "Transtorno bipolar; TP antissocial; TP histriônica; "
        "TP borderline; TEA (falta de empatia sem grandiosidade); "
        "transtorno dismórfico corporal; "
        "comportamento narcisista normal (adolescência).",
        "Bipolar disorders (6A60-6A61); Antisocial PD (6D11); "
        "Histrionic PD (6D11); Anorexia nervosa (6B80).",
        "Bipolar disorders (6A60-6A61); Antisocial PD (6D11); "
        "Substance use disorders (6C4); Body dysmorphic disorder (6B21)."
    ),
    "Transtorno da Personalidade Esquiva": (
        "A. Padrão de inibição social, sentimentos de inadequação e hipersensibilidade a "
        "avaliação negativa, presente desde o início da vida adulta, com 4+:\n"
        "1. evita atividades profissionais que envolvam contato interpessoal por medo de crítica\n"
        "2. reluta em se envolver com pessoas sem certeza de ser aceito\n"
        "3. contido em relacionamentos íntimos por medo de vergonha\n"
        "4. preocupação com crítica ou rejeição em situações sociais\n"
        "5. inibido em novas situações interpessoais\n"
        "6. vê-se como socialmente inepto, inferior ou pouco atraente\n"
        "7. reluta em assumir riscos pessoais para evitar possível vergonha.\n"
        "B. Não ocorre exclusivamente durante depressão maior, ansiedade social ou transtorno do pânico.",
        "Transtorno de ansiedade social (medo de avaliação em situações específicas); "
        "TP dependente (desejo de ser cuidado, submissão); "
        "transtorno do pânico com agorafobia; "
        "TP esquizoide (distanciamento sem desejo de relacionamentos).",
        "Transtorno de ansiedade social (fobia social generalizada vs. TP esquiva); "
        "depressão maior; transtorno do pânico com agorafobia; "
        "TAG; TP esquizoide (não deseja relações); TP dependente.",
        "Social anxiety disorder (6B04); Agoraphobia (6B02); "
        "Dependent PD (6D10); Schizoid PD (6D12).",
        "Social anxiety disorder (6B04); Agoraphobia (6B02); "
        "Schizoid PD (6D12); Dependent PD (6D10); "
        "Depressive disorders (6A70-6A71)."
    ),
    "Transtorno da Personalidade Dependente": (
        "A. Necessidade excessiva de ser cuidado com comportamento submisso, apego e medo de "
        "separação, presente desde o início da vida adulta, com 5+:\n"
        "1. dificuldade em tomar decisões sem conselho e reasseguramento\n"
        "2. precisa que outros assumam responsabilidade por áreas importantes da vida\n"
        "3. dificuldade em expressar discordância por medo de perder apoio\n"
        "4. dificuldade em iniciar projetos por falta de autoconfiança\n"
        "5. faz de tudo para obter apoio e cuidado (tarefas desagradáveis)\n"
        "6. sente-se desconfortável ou desamparado quando sozinho\n"
        "7. termina relacionamento e busca imediatamente nova fonte de cuidado\n"
        "8. preocupação em cuidar de si mesmo.\n"
        "B. Não ocorre exclusivamente durante transtorno de ansiedade de separação, depressão ou agorafobia.",
        "Transtorno de ansiedade de separação (medo quanto a figuras de apego); "
        "transtorno do pânico com agorafobia (dependência de acompanhante); "
        "depressão maior (passividade secundária); "
        "TP histriônica (dependência de aprovação, busca de atenção).",
        "Transtorno de ansiedade de separação; agorafobia; "
        "depressão maior; TP histriônica; TP borderline; "
        "TP esquiva; comportamento dependente normal; "
        "doença médica com dependência real.",
        "Separation anxiety disorder (6B05); Agoraphobia (6B02); "
        "Depressive disorders (6A70-6A71); Histrionic PD (6D11).",
        "Separation anxiety disorder (6B05); Agoraphobia (6B02); "
        "Borderline PD (6D11); Avoidant PD (6D10)."
    ),
    "Transtorno da Personalidade Obsessivo-Compulsiva": (
        "A. Padrão de preocupação com ordem, perfeccionismo e controle mental/interpessoal às "
        "custas da flexibilidade e eficiência, presente desde o início da vida adulta, com 4+:\n"
        "1. preocupação com detalhes, regras, listas, ordem\n"
        "2. perfeccionismo que interfere na conclusão de tarefas\n"
        "3. dedicação excessiva ao trabalho em detrimento do lazer\n"
        "4. inflexibilidade em questões de moral, ética ou valores\n"
        "5. incapacidade de descartar objetos (diferente de acumulação)\n"
        "6. relutância em delegar tarefas sem submissão total\n"
        "7. avareza em relação a si e aos outros\n"
        "8. rigidez e teimosia.\n"
        "B. Não ocorre exclusivamente durante TOC, transtorno alimentar ou transtorno neurocognitivo.",
        "TOC (obsessões/compulsões egodistônicas, diferentes do perfeccionismo egossintônico); "
        "transtorno de acumulação (acumulação de objetos, não apenas incapacidade de descartar); "
        "anorexia nervosa (restrição alimentar com medo de peso); "
        "transtorno neurocognitivo (rigidez adquirida).",
        "TOC; transtorno de acumulação; anorexia nervosa; "
        "transtorno do espectro autista (rigidez, interesses restritos); "
        "transtorno neurocognitivo frontotemporal; "
        "transtorno de personalidade paranoide (inflexibilidade).",
        "OCD (6B20); Hoarding disorder (6B24); "
        "Anorexia nervosa (6B80); Autism spectrum disorder (6A02).",
        "OCD (6B20); Hoarding disorder (6B24); "
        "Anorexia nervosa (6B80); Autism spectrum disorder (6A02); "
        "Frontotemporal dementia (6D81)."
    ),
    "Transtorno da Personalidade Antissocial": (
        "A. Padrão de desrespeito e violação dos direitos alheios, presente desde os 15 anos, "
        "com 3+:\n"
        "1. incapacidade de adequar-se a normas sociais\n"
        "2. mentira repetida, uso de pseudônimos, trapaça\n"
        "3. impulsividade ou incapacidade de planejar\n"
        "4. irritabilidade e agressividade (brigas, agressões)\n"
        "5. desrespeito pela segurança própria ou alheia\n"
        "6. irresponsabilidade consistente (falha em manter trabalho/obrigações)\n"
        "7. ausência de remorso.\n"
        "B. Idade atual ≥ 18 anos.\n"
        "C. Evidência de transtorno da conduta com início antes dos 15 anos.\n"
        "D. Não ocorre exclusivamente durante esquizofrenia ou transtorno bipolar.",
        "Transtorno da conduta (idade <18, sem padrão completo); "
        "transtorno explosivo intermitente (impulsividade sem violação de direitos); "
        "transtorno por uso de substância (comportamento secundário); "
        "transtorno bipolar (mania com comportamento antissocial).",
        "Transtorno da conduta; TOD; transtorno explosivo intermitente; "
        "TP borderline; TP narcisista; "
        "transtorno bipolar; transtorno por uso de substância; "
        "transtorno neurocognitivo frontotemporal; simulação.",
        "Conduct disorder (6C91); Intermittent explosive disorder (6C70); "
        "Bipolar disorders (6A60-6A61); Substance use disorders (6C4).",
        "Conduct disorder (6C91); Borderline PD (6D11); "
        "Narcissistic PD (6D11); Bipolar disorders (6A60-6A61); "
        "Substance use disorders (6C4); Frontotemporal dementia (6D81)."
    ),

"Outro Transtorno da Personalidade Especificado": (
        'A. Sintomas característicos de transtorno da personalidade borderline que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno da personalidade borderline, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno da Personalidade Borderline; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno da Personalidade Não Especificado": (
        'A. Sintomas característicos de transtorno da personalidade borderline que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno da Personalidade Borderline; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

    # ═══ CHAPTER 19: Transtornos Parafílicos ═══
    "Transtorno Voyeurista": (
        "A. Excitação sexual recorrente e intensa ao observar pessoa sem suspeita nua, "
        "em atividade sexual ou em atos íntimos, presente por 6+ meses.\n"
        "B. O indivíduo agiu com pessoa não consentida OU o desejo/atitude "
        "causa sofrimento ou comprometimento significativo.\n"
        "C. Idade ≥ 18 anos.",
        "Comportamento voyeurista normativo (sem sofrimento, consentido); "
        "comportamento sexual entre adultos consentidos; "
        "exibicionismo (foco em expor, não observar); "
        "mania (hipersexualidade generalizada); "
        "transtorno neurocognitivo (desinibição adquirida).",
        "Transtorno exhibitionista; transtorno de sadismo sexual; "
        "transtorno frotteurista; hipersexualidade secundária a transtorno bipolar; "
        "transtorno neurocognitivo maior; TUS.",
        "Exhibitionistic disorder (6D34); Frotteuristic disorder (6D35); "
        "Sexual sadism disorder (6D37).",
        "Exhibitionistic disorder (6D34); Frotteuristic disorder (6D35); "
        "Bipolar type I disorder (6A60); Neurocognitive disorders (6D71-6D7Z)."
    ),
    "Transtorno Exhibitionista": (
        "A. Excitação sexual recorrente e intensa pela exposição dos próprios genitais a "
        "pessoa sem suspeita, presente por 6+ meses.\n"
        "B. O indivíduo agiu com pessoa não consentida OU o desejo causa "
        "sofrimento ou comprometimento significativo.",
        "Comportamento exhibitionista normativo (clubes, consentido); "
        "transtorno voyeurista; transtorno transvéstico; "
        "mania (hipersexualidade); intoxicação por substância; "
        "transtorno neurocognitivo (desinibição).",
        "Transtorno voyeurista; transtorno frotteurista; "
        "transtorno de sadismo sexual; transtorno transvéstico; "
        "hipersexualidade maníaca; delírio erótico; "
        "transtorno neurocognitivo; TUS.",
        "Voyeuristic disorder (6D33); Frotteuristic disorder (6D35); "
        "Transvestic disorder (6D30); Bipolar disorders (6A60-6A61).",
        "Voyeuristic disorder (6D33); Frotteuristic disorder (6D35); "
        "Bipolar type I disorder (6A60); Neurocognitive disorders (6D71-6D7Z)."
    ),
    "Transtorno Frotteurista": (
        "A. Excitação sexual recorrente e intensa por tocar ou esfregar-se em pessoa não "
        "consentida, presente por 6+ meses.\n"
        "B. O indivíduo agiu com pessoa não consentida OU o desejo causa "
        "sofrimento ou comprometimento significativo.",
        "Transtorno voyeurista (observação); transtorno exhibitionista (exposição); "
        "mania (hipersexualidade desinibida); "
        "intoxicação por substância; "
        "transtorno neurocognitivo (desinibição adquirida).",
        "Transtorno voyeurista; transtorno exhibitionista; "
        "transtorno de sadismo sexual; hipersexualidade; "
        "transtorno neurocognitivo; TUS; "
        "comportamento agressivo não sexual.",
        "Voyeuristic disorder (6D33); Exhibitionistic disorder (6D34); "
        "Sexual sadism disorder (6D37); Bipolar disorders (6A60-6A61).",
        "Voyeuristic disorder (6D33); Exhibitionistic disorder (6D34); "
        "Bipolar type I disorder (6A60); Neurocognitive disorders (6D71-6D7Z)."
    ),
    "Transtorno de Masoquismo Sexual": (
        "A. Excitação sexual recorrente e intensa ao ser humilhado, agredido ou fazer sofrer, "
        "presente por 6+ meses.\n"
        "B. O comportamento real OU o desejo causa sofrimento ou comprometimento significativo.",
        "Prática BDSM normativa entre adultos consentidos (sem sofrimento/comprometimento); "
        "transtorno de sadismo sexual (papel ativo vs. passivo); "
        "transtorno de personalidade borderline (autolesão não sexual); "
        "depressão maior (comportamento autodestrutivo).",
        "Transtorno de sadismo sexual; TP borderline; "
        "transtorno factício; autolesão não suicida; "
        "depressão maior; transtorno dissociativo.",
        "Sexual sadism disorder (6D37); Borderline PD (6D11); "
        "Non-suicidal self-injury (MB23.E).",
        "Sexual sadism disorder (6D37); Borderline PD (6D11); "
        "Depressive disorders (6A70-6A71); Factitious disorder (6D50)."
    ),
    "Transtorno de Sadismo Sexual": (
        "A. Excitação sexual recorrente e intensa pelo sofrimento físico ou psicológico de "
        "outra pessoa, presente por 6+ meses.\n"
        "B. O indivíduo agiu com pessoa não consentida OU o desejo causa "
        "sofrimento ou comprometimento significativo.",
        "Prática BDSM normativa (consentida, sem sofrimento); "
        "transtorno de masoquismo sexual (papel passivo); "
        "TP antissocial (violência sem componente sexual); "
        "transtorno explosivo intermitente; mania.",
        "Transtorno de masoquismo sexual; TP antissocial; "
        "transtorno explosivo intermitente; "
        "transtorno da conduta; transtorno psicótico.",
        "Sexual masochism disorder (6D36); Antisocial PD (6D11); "
        "Intermittent explosive disorder (6C70).",
        "Sexual masochism disorder (6D36); Antisocial PD (6D11); "
        "Conduct disorder (6C91); Bipolar disorders (6A60-6A61)."
    ),
    "Transtorno Pedofílico": (
        "A. Excitação sexual recorrente e intensa por atividade sexual com criança(s) pré-púbere(s) "
        "(geralmente ≤ 13 anos), presente por 6+ meses.\n"
        "B. O indivíduo agiu com a criança OU o desejo causa sofrimento ou comprometimento.\n"
        "C. Idade ≥ 16 anos e ≥ 5 anos mais velho que a criança.\n"
        "D. Não inclui adolescente em relacionamento sexual com outro adolescente.",
        "Comportamento sexual entre adolescentes (idade próxima, consentido); "
        "interesse sexual por crianças sem sofrimento/atuação (pedofilia não transtorno); "
        "transtorno exhibitionista; transtorno voyeurista; "
        "TOC (obsessões sexuais egodistônicas); "
        "mania (hipersexualidade generalizada); transtorno neurocognitivo.",
        "Transtorno exhibitionista; transtorno voyeurista; "
        "TOC; TUS; transtorno bipolar; "
        "transtorno neurocognitivo maior; "
        "deficiência intelectual; abuso sexual na infância (história).",
        "Exhibitionistic disorder (6D34); Voyeuristic disorder (6D33); "
        "OCD (6B20); Bipolar disorders (6A60-6A61).",
        "Exhibitionistic disorder (6D34); Voyeuristic disorder (6D33); "
        "OCD (6B20); Bipolar disorders (6A60-6A61); "
        "Intellectual developmental disorder (6A00); Dementia (6D71-6D7Z)."
    ),
    "Transtorno Fetichista": (
        "A. Excitação sexual recorrente e intensa por objetos não vivos ou partes do corpo "
        "específicas, presente por 6+ meses.\n"
        "B. Causa sofrimento ou comprometimento clinicamente significativo.\n"
        "C. O foco não se limita a roupas femininas usadas em cross-dressing (transtorno transvéstico).",
        "Comportamento fetichista normativo (sem sofrimento/comprometimento); "
        "transtorno transvéstico (excitação por trajar-se do sexo oposto, não pelo objeto); "
        "TOC (obsessões sexuais); transtorno dismórfico corporal.",
        "Transtorno transvéstico; TOC; "
        "transtorno dismórfico corporal; "
        "comportamento fetichista normal (parafilia não transtorno).",
        "Transvestic disorder (6D30); OCD (6B20); "
        "Body dysmorphic disorder (6B21).",
        "Transvestic disorder (6D30); OCD (6B20); "
        "Body dysmorphic disorder (6B21)."
    ),
    "Transtorno Transvéstico": (
        "A. Excitação sexual recorrente e intensa por trajar-se do sexo oposto, presente por "
        "6+ meses.\n"
        "B. O comportamento real OU o desejo causa sofrimento ou comprometimento significativo.",
        "Disforia de gênero (incongruência de gênero sem excitação sexual pelo trajar-se); "
        "transtorno fetichista (excitação pelo objeto, não pelo cross-dressing); "
        "comportamento transvéstico normativo (sem sofrimento/comprometimento); "
        "inconformidade de gênero sem disforia.",
        "Disforia de gênero; transtorno fetichista; "
        "inconformidade de gênero; TOC (obsessões com identidade de gênero); "
        "mania (comportamento cross-gender em episódio maníaco).",
        "Gender dysphoria (HA60-6D31); Fetishistic disorder (6D38); "
        "OCD (6B20); Bipolar disorders (6A60-6A61).",
        "Gender dysphoria (6D31); Fetishistic disorder (6D38); "
        "OCD (6B20); Body dysmorphic disorder (6B21)."
    ),

"Outro Transtorno Parafílico Especificado": (
        'A. Sintomas característicos de transtorno voyeurista que causam sofrimento ou prejuízo clinicamente significativo.\nB. Os sintomas preenchem a maioria dos critérios para transtorno voyeurista, mas não todos, e o clínico opta por especificar a razão.',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Voyeurista; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),
    "Transtorno Parafílico Não Especificado": (
        'A. Sintomas característicos de transtorno voyeurista que causam sofrimento ou prejuízo clinicamente significativo.\nB. Não há informação suficiente para fazer um diagnóstico mais específico (ex.: em contextos de emergência, ou quando o paciente não pode ser avaliado adequadamente).',
        'Excluir diagnósticos primários que expliquem melhor os sintomas; transtorno devido a condição médica; transtorno induzido por substância; transtorno do espectro da esquizofrenia; transtorno de personalidade pré-existente.',
        'Considerar: Transtorno Voyeurista; outros transtornos da mesma classe diagnóstica; transtorno factício; simulação; transtorno de personalidade; transtorno devido a condição médica; transtorno induzido por substância.',
        'Conditions classifiable elsewhere; substance-induced disorders; disorders due to known medical conditions.',
        'All specific disorder codes in the diagnostic class; substance-induced disorders; disorders due to known medical conditions.',
    ),

# Total supplemental entries: 62

    # ═══ CHAPTER 20: Outros Transtornos Mentais ═══
    "Outro Transtorno Mental Especificado": (
        "A. Sintomas característicos de um transtorno mental que causam sofrimento ou prejuízo "
        "clinicamente significativo.\n"
        "B. Os sintomas preenchem critérios parciais para um transtorno específico mas não "
        "satisfazem todos os critérios para qualquer transtorno na classe diagnóstica.\n"
        "C. O clínico opta por comunicar a razão específica pela qual os critérios não foram "
        "preenchidos (ex.: 'transtorno depressivo especificado, duração breve').",
        "Não aplicável (categoria residual); "
        "transtorno mental não especificado (clínico não especifica a razão); "
        "transtorno factício; simulação; "
        "transtorno de adaptação (estressor identificável).",
        "Todos os transtornos mentais específicos devem ser excluídos antes de usar esta categoria; "
        "transtorno de adaptação; transtorno factício; simulação.",
        "All specific disorder codes; "
        "Adjustment disorder (6B43); Factitious disorder (6D50).",
        "All specific disorder codes; "
        "Adjustment disorder (6B43); "
        "Mental disorder not otherwise specified."
    ),
    "Transtorno Mental Não Especificado": (
        "A. Sintomas característicos de um transtorno mental que causam sofrimento ou prejuízo "
        "clinicamente significativo.\n"
        "B. Não há informação suficiente para fazer um diagnóstico específico (ex.: em contextos "
        "de emergência onde não é possível determinar se os sintomas são primários ou induzidos).",
        "Outro transtorno mental especificado (clínico especifica a razão); "
        "transtorno de adaptação; transtorno factício; simulação; "
        "sintomas subclínicos (sem sofrimento/prejuízo).",
        "Outro transtorno mental especificado (razão conhecida); "
        "transtorno de adaptação; "
        "todos os transtornos mentais específicos devem ser considerados.",
        "Other specified mental disorder; "
        "Adjustment disorder (6B43); Factitious disorder (6D50).",
        "All specific disorder codes; "
        "Adjustment disorder (6B43); "
        "Other specified mental disorder."
    ),
}


# ═══ DIAGNOSIS RELATIONSHIPS FOR REFERENCE DISORDERS ═══
# Format: (source_name, target_name, type, weight)
# type: "comorbidity", "exclusion", "hierarchical"

# Map DSM5TR_ALL keys and shorthand names to full DB names
_NAME_MAP = {
    # Phase 1: DSM5TR_ALL keys that don't match DB names
    "Tricotilomania": "Tricotilomania (Transtorno de Arrancar Cabelo)",
    "Catatonia": "Catatonia Associada a Transtorno Mental",
    "Transtorno Específico da Aprendizagem": "Transtorno Específico da Aprendizagem — com Prejuízo na Leitura",
    "Transtorno Neurocognitivo Maior": "Transtorno Neurocognitivo Maior — Doença de Alzheimer",
    # Phase 3: shorthand names in relationships
    "TDAH": "Transtorno de Déficit de Atenção/Hiperatividade",
    "Transtorno de Pânico": "Transtorno do Pânico",
    "Transtorno de Identidade Dissociativa": "Transtorno Dissociativo de Identidade",
    "Transtorno Desafiador Opositivo": "Transtorno Opositivo-Desafiador",
    "Transtorno de Adaptação": "Transtornos de Adaptação",
    "Transtorno de Escoriação": "Transtorno de Escoriação (Skin Picking)",
    "Disforia de Gênero": "Disforia de Gênero em Adolescentes e Adultos",
}


def _resolve(name):
    return _NAME_MAP.get(name, name)


REFERENCE_RELATIONSHIPS = [
    # ── Chapter 1: Neurodesenvolvimento ──
    ("Deficiência Intelectual", "Transtorno do Espectro Autista", "comorbidity", 0.4),
    ("Transtorno do Espectro Autista", "Deficiência Intelectual", "comorbidity", 0.4),
    ("Deficiência Intelectual", "TDAH", "comorbidity", 0.3),
    ("TDAH", "Deficiência Intelectual", "comorbidity", 0.3),
    ("Transtorno da Linguagem", "Transtorno do Espectro Autista", "hierarchical", 0.0),
    ("Transtorno Específico da Aprendizagem — com Prejuízo na Leitura", "TDAH", "comorbidity", 0.4),
    ("TDAH", "Transtorno Específico da Aprendizagem — com Prejuízo na Leitura", "comorbidity", 0.4),
    ("Transtorno de Tourette", "TDAH", "comorbidity", 0.5),
    ("TDAH", "Transtorno de Tourette", "comorbidity", 0.5),
    ("Transtorno de Tourette", "Transtorno Obsessivo-Compulsivo", "comorbidity", 0.4),
    ("Transtorno Obsessivo-Compulsivo", "Transtorno de Tourette", "comorbidity", 0.4),

    # ── Chapter 2: Psicóticos ──
    ("Transtorno Delirante", "Esquizofrenia / Transtorno Psicótico", "hierarchical", 0.0),
    ("Transtorno Psicótico Breve", "Esquizofrenia / Transtorno Psicótico", "hierarchical", 0.0),
    ("Transtorno Esquizofreniforme", "Esquizofrenia / Transtorno Psicótico", "hierarchical", 0.0),
    ("Transtorno Esquizoafetivo", "Transtorno Bipolar Tipo I", "hierarchical", 0.0),
    ("Transtorno Esquizoafetivo", "Esquizofrenia / Transtorno Psicótico", "hierarchical", 0.0),

    # ── Chapter 3: Bipolar ──
    ("Transtorno Bipolar Tipo II", "Transtorno Depressivo Maior", "hierarchical", 0.0),
    ("Transtorno Bipolar Tipo II", "Transtorno Bipolar Tipo I", "hierarchical", 0.0),
    ("Transtorno Ciclotímico", "Transtorno Bipolar Tipo I", "hierarchical", 0.0),
    ("Transtorno Ciclotímico", "Transtorno Bipolar Tipo II", "hierarchical", 0.0),

    # ── Chapter 4: Depressivos ──
    ("Transtorno Disruptivo da Desregulação do Humor", "Transtorno Bipolar Tipo I", "exclusion", 0.0),
    ("Transtorno Disruptivo da Desregulação do Humor", "Transtorno Depressivo Maior", "hierarchical", 0.0),
    ("Transtorno Depressivo Persistente (Distimia)", "Transtorno Depressivo Maior", "hierarchical", 0.0),
    ("Transtorno Disfórico Pré-Menstrual", "Transtorno Depressivo Maior", "hierarchical", 0.0),

    # ── Chapter 5: Ansiedade ──
    ("Transtorno de Ansiedade Social", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.5),
    ("Transtorno de Ansiedade Generalizada", "Transtorno de Ansiedade Social", "comorbidity", 0.5),
    ("Transtorno de Ansiedade Social", "Transtorno Depressivo Maior", "comorbidity", 0.4),
    ("Transtorno de Pânico", "Agorafobia", "comorbidity", 0.7),
    ("Agorafobia", "Transtorno de Pânico", "comorbidity", 0.7),
    ("Mutismo Seletivo", "Transtorno de Ansiedade Social", "hierarchical", 0.0),

    # ── Chapter 6: TOC ──
    ("Transtorno de Acumulação", "Transtorno Obsessivo-Compulsivo", "hierarchical", 0.0),
    ("Tricotilomania", "Transtorno Obsessivo-Compulsivo", "hierarchical", 0.0),
    ("Transtorno de Escoriação", "Transtorno Obsessivo-Compulsivo", "hierarchical", 0.0),

    # ── Chapter 7: Trauma ──
    ("Transtorno de Estresse Pós-Traumático", "Transtorno de Estresse Agudo", "hierarchical", 0.0),
    ("Transtorno de Adaptação", "Transtorno Depressivo Maior", "hierarchical", 0.0),
    ("Transtorno de Adaptação", "Transtorno de Ansiedade Generalizada", "hierarchical", 0.0),
    ("Transtorno de Estresse Pós-Traumático", "Transtorno de Pânico", "comorbidity", 0.4),
    ("Transtorno de Estresse Pós-Traumático", "Transtorno por Uso de Substâncias", "comorbidity", 0.4),

    # ── Chapter 8: Dissociativos ──
    ("Transtorno de Identidade Dissociativa", "Transtorno de Estresse Pós-Traumático", "comorbidity", 0.8),
    ("Transtorno de Identidade Dissociativa", "Transtorno Depressivo Maior", "comorbidity", 0.5),
    ("Amnésia Dissociativa", "Transtorno de Estresse Pós-Traumático", "hierarchical", 0.0),

    # ── Chapter 9: Somáticos ──
    ("Transtorno de Ansiedade de Doença", "Transtorno de Sintomas Somáticos", "hierarchical", 0.0),
    ("Transtorno de Sintomas Somáticos", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.5),
    ("Transtorno de Sintomas Somáticos", "Transtorno Depressivo Maior", "comorbidity", 0.4),
    ("Transtorno Factício", "Transtorno de Sintomas Somáticos", "hierarchical", 0.0),

    # ── Chapter 10: Alimentares ──
    ("Anorexia Nervosa", "Transtorno Depressivo Maior", "comorbidity", 0.5),
    ("Bulimia Nervosa", "Transtorno Depressivo Maior", "comorbidity", 0.5),
    ("Bulimia Nervosa", "Anorexia Nervosa", "hierarchical", 0.0),
    ("Transtorno de Compulsão Alimentar", "Transtorno Depressivo Maior", "comorbidity", 0.4),
    ("Transtorno de Compulsão Alimentar", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.3),
    ("Transtorno Alimentar Restritivo-Evitante", "Transtorno do Espectro Autista", "comorbidity", 0.3),
    ("Transtorno de Ruminação", "Anorexia Nervosa", "hierarchical", 0.0),

    # ── Chapter 12: Sono-Vigília ──
    ("Transtorno de Insônia", "Transtorno Depressivo Maior", "comorbidity", 0.6),
    ("Transtorno de Insônia", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.5),
    ("Transtorno de Hipersonolência", "Transtorno Depressivo Maior", "comorbidity", 0.4),
    ("Narcolepsia", "Transtorno de Hipersonolência", "hierarchical", 0.0),
    ("Apneia Obstrutiva do Sono", "Transtorno Depressivo Maior", "comorbidity", 0.3),
    ("Apneia Obstrutiva do Sono", "Transtorno de Insônia", "comorbidity", 0.4),
    ("Síndrome das Pernas Inquietas", "Transtorno de Insônia", "comorbidity", 0.5),
    ("Transtorno Comportamental do Sono REM", "Transtorno de Estresse Pós-Traumático", "hierarchical", 0.0),

    # ── Chapter 13: Disfunções Sexuais ──
    ("Transtorno Erétil", "Transtorno Depressivo Maior", "comorbidity", 0.3),
    ("Transtorno do Interesse/Excitação Sexual Feminino", "Transtorno Depressivo Maior", "comorbidity", 0.3),

    # ── Chapter 14: Disforia de Gênero ──
    ("Disforia de Gênero", "Transtorno Depressivo Maior", "comorbidity", 0.4),
    ("Disforia de Gênero", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.3),

    # ── Chapter 15: Disruptivos ──
    ("Transtorno Desafiador Opositivo", "TDAH", "comorbidity", 0.5),
    ("TDAH", "Transtorno Desafiador Opositivo", "comorbidity", 0.5),
    ("Transtorno da Conduta", "Transtorno Desafiador Opositivo", "hierarchical", 0.0),
    ("Transtorno da Conduta", "TDAH", "comorbidity", 0.4),
    ("Transtorno da Conduta", "Transtorno por Uso de Substâncias", "comorbidity", 0.5),
    ("Transtorno Explosivo Intermitente", "TDAH", "comorbidity", 0.3),
    ("Transtorno Explosivo Intermitente", "Transtorno Desafiador Opositivo", "hierarchical", 0.0),

    # ── Chapter 16: Substâncias ──
    ("Transtorno por Uso de Substâncias", "Transtorno Depressivo Maior", "comorbidity", 0.4),
    ("Transtorno por Uso de Substâncias", "Transtorno de Estresse Pós-Traumático", "comorbidity", 0.4),
    ("Transtorno por Uso de Substâncias", "Transtorno Bipolar Tipo I", "comorbidity", 0.3),
    ("Transtorno por Uso de Substâncias", "Esquizofrenia / Transtorno Psicótico", "comorbidity", 0.3),
    ("Transtorno por Uso de Substâncias", "TDAH", "comorbidity", 0.3),
    ("Intoxicação Alcoólica", "Transtorno por Uso de Substâncias", "hierarchical", 0.0),
    ("Abstinência Alcoólica", "Transtorno por Uso de Substâncias", "hierarchical", 0.0),

    # ── Chapter 17: Neurocognitivos ──
    ("Transtorno Neurocognitivo Maior", "Transtorno Depressivo Maior", "comorbidity", 0.3),
    ("Delirium", "Transtorno Neurocognitivo Maior", "hierarchical", 0.0),

    # ── Chapter 18: Personalidade ──
    ("Transtorno da Personalidade Borderline", "Transtorno Depressivo Maior", "comorbidity", 0.5),
    ("Transtorno da Personalidade Borderline", "Transtorno Bipolar Tipo I", "hierarchical", 0.0),
    ("Transtorno da Personalidade Borderline", "Transtorno de Estresse Pós-Traumático", "comorbidity", 0.4),
    ("Transtorno da Personalidade Borderline", "Transtorno por Uso de Substâncias", "comorbidity", 0.4),
    ("Transtorno da Personalidade Antissocial", "Transtorno da Conduta", "hierarchical", 0.0),
    ("Transtorno da Personalidade Antissocial", "Transtorno por Uso de Substâncias", "comorbidity", 0.5),
    ("Transtorno da Personalidade Esquiva", "Transtorno de Ansiedade Social", "hierarchical", 0.0),
    ("Transtorno da Personalidade Esquiva", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.4),
    ("Transtorno da Personalidade Dependente", "Transtorno de Ansiedade Generalizada", "comorbidity", 0.3),
    ("Transtorno da Personalidade Obsessivo-Compulsiva", "Transtorno Obsessivo-Compulsivo", "hierarchical", 0.0),
    ("Transtorno da Personalidade Paranoide", "Esquizofrenia / Transtorno Psicótico", "hierarchical", 0.0),

    # ── Chapter 19: Parafílicos ──
    ("Transtorno Voyeurista", "Transtorno da Personalidade Antissocial", "comorbidity", 0.3),
    ("Transtorno Exhibitionista", "Transtorno da Personalidade Antissocial", "comorbidity", 0.3),
    ("Transtorno Pedofílico", "Transtorno da Personalidade Antissocial", "comorbidity", 0.3),
]


def seed():
    """Seed DSM-5-TR criteria text, ICD-11 exclusions/differentials, and diagnosis relationships
    for all ~173 reference disorders. Skips the 19 core disorders (already seeded by
    seed_diagnostic_data.py)."""
    db = SessionLocal()
    try:
        disorders = {d.disorder_name: d for d in db.query(Disorder).all()}
        who = db.query(ClassificationAuthority).filter_by(short_name="WHO").first()
        if not who:
            print("ERROR: WHO authority not found. Run db/seed.py first.")
            return

        # ── Phase 1: Update Disorder text columns ──
        update_count = 0
        for disorder_name, data in DSM5TR_ALL.items():
            if disorder_name in CORE_DISORDER_NAMES:
                continue

            db_name = _resolve(disorder_name)
            disorder = disorders.get(db_name)
            if not disorder:
                print(f"  WARNING: Disorder '{disorder_name}' (resolved: '{db_name}') not found in DB")
                continue

            if isinstance(data, str):
                if data in ("", "|"):
                    print(f"  SKIP: '{disorder_name}' — placeholder/empty entry")
                else:
                    print(f"  WARNING: '{disorder_name}' — unexpected string value")
                continue

            if data is None:
                print(f"  SKIP: '{disorder_name}' — None entry")
                continue

            if not isinstance(data, tuple):
                continue

            # Unpack tuple safely (handles 2, 3, 4, or 5 elements)
            if len(data) >= 5:
                criteria, exclusions, differentials, icd11_excl, icd11_diff = data[:5]
            elif len(data) == 4:
                criteria, exclusions, differentials, icd11_excl = data
                icd11_diff = ""
            elif len(data) == 3:
                criteria, exclusions, differentials = data
                icd11_excl = ""
                icd11_diff = ""
            elif len(data) == 2:
                criteria, exclusions = data
                differentials = ""
                icd11_excl = ""
                icd11_diff = ""
            else:
                continue

            disorder.dsm_criteria = criteria or ""
            disorder.dsm_exclusions = exclusions or ""
            disorder.dsm_differentials = differentials or ""
            disorder.icd11_exclusions = icd11_excl or ""
            disorder.icd11_differentials = icd11_diff or ""
            update_count += 1

        db.commit()
        print(f"OK - {update_count} disorders updated with DSM-5-TR criteria text")

        # ── Phase 2: Seed ICD-11 exclusions and differentials ──
        excl_count = 0
        diff_count = 0
        icd11_codes = {c.icd11_title: c for c in db.query(ICD11Code).all()}

        for disorder_name, data in DSM5TR_ALL.items():
            if disorder_name in CORE_DISORDER_NAMES:
                continue
            if isinstance(data, str) or data is None or not isinstance(data, tuple):
                continue

            db_name = _resolve(disorder_name)
            disorder = disorders.get(db_name)
            if not disorder:
                continue

            # Get ICD-11 code records for this disorder
            icd_records = db.query(ICD11Code).filter_by(disorder_id=disorder.disorder_id).all()
            for icd in icd_records:
                if icd.authority_id is None and who:
                    icd.authority_id = who.authority_id

                # Parse icd11_exclusions text
                icd11_excl_text = ""
                if len(data) >= 4:
                    icd11_excl_text = data[3] or ""
                if icd11_excl_text:
                    for excl_item in icd11_excl_text.split(";"):
                        excl_item = excl_item.strip()
                        if excl_item:
                            existing = db.query(ICD11Exclusion).filter_by(
                                code_id=icd.code_id, excluded_title=excl_item[:500]
                            ).first()
                            if not existing:
                                db.add(ICD11Exclusion(
                                    code_id=icd.code_id,
                                    excluded_title=excl_item[:500],
                                    reason="Exclusion per ICD-11 CDDR",
                                ))
                                excl_count += 1

                # Parse icd11_differentials text
                icd11_diff_text = ""
                if len(data) >= 5:
                    icd11_diff_text = data[4] or ""
                elif len(data) == 4:
                    pass
                if icd11_diff_text:
                    for diff_item in icd11_diff_text.split(";"):
                        diff_item = diff_item.strip()
                        if diff_item:
                            existing = db.query(ICD11Differential).filter_by(
                                code_id=icd.code_id, differential_title=diff_item[:500]
                            ).first()
                            if not existing:
                                db.add(ICD11Differential(
                                    code_id=icd.code_id,
                                    differential_title=diff_item[:500],
                                    distinguishing_features="See ICD-11 CDDR for full differential guidance.",
                                ))
                                diff_count += 1

        db.commit()
        print(f"OK - {excl_count} ICD-11 exclusions seeded")
        print(f"OK - {diff_count} ICD-11 differentials seeded")

        # ── Phase 3: Diagnosis relationships for reference disorders ──
        rel_count = 0
        for src_name_raw, tgt_name_raw, rtype, weight in REFERENCE_RELATIONSHIPS:
            src_name = _resolve(src_name_raw)
            tgt_name = _resolve(tgt_name_raw)
            src = disorders.get(src_name)
            tgt = disorders.get(tgt_name)
            if not src or not tgt:
                missing = src_name if not src else tgt_name
                print(f"  WARNING: Disorder '{missing}' not found for relationship")
                continue

            existing = db.query(DiagnosisRelationship).filter_by(
                source_disorder_id=src.disorder_id,
                target_disorder_id=tgt.disorder_id,
            ).first()
            if not existing:
                db.add(DiagnosisRelationship(
                    source_disorder_id=src.disorder_id,
                    target_disorder_id=tgt.disorder_id,
                    relationship_type=rtype,
                    relationship_weight=weight,
                ))
                rel_count += 1

        # Also add relationships that reference core disorders as source/target
        # (only the ones that aren't already in db/seed.py's relationships list)
        core_ref_relationships = [
            # Already seeded in db/seed.py — skip to avoid duplicates
        ]

        db.commit()
        print(f"OK - {rel_count} diagnosis relationships seeded for reference disorders")

        # ── Phase 4: Diagnostic criteria (symptom mappings) for reference disorders ──
        # Build a map of symptom_name -> Symptom object
        all_symptoms = {s.symptom_name: s for s in db.query(Symptom).all()}
        crit_count = 0
        skipped_no_symptom = 0

        for disorder_name, symptom_list in REFERENCE_SYMPTOM_MAP.items():
            db_name = _resolve(disorder_name)
            disorder = disorders.get(db_name)
            if not disorder:
                # Try exact match
                disorder = disorders.get(disorder_name)
            if not disorder:
                print(f"  WARNING: Disorder '{disorder_name}' not found for criteria mapping")
                continue

            # Skip if this disorder already has DiagnosticCriteria records
            existing_dc = db.query(DiagnosticCriteria).filter(
                DiagnosticCriteria.disorder_id == disorder.disorder_id
            ).count()
            if existing_dc > 0:
                continue

            for symptom_key, desc_text, required, min_dur in symptom_list:
                # Look up symptom by its Portuguese name (snake_case key -> pt_name)
                # The symptom_key is the English key, but the Symptom table stores
                # Portuguese snake_case names. We need EN_TO_PT mapping.
                # Import EN_TO_PT mapping inline (available from seed_clinical_data.py)
                # Actually, we handle this by trying to match symptom_name directly

                pt_name = EN_TO_PT_SYMPTOM.get(symptom_key)
                if not pt_name:
                    skipped_no_symptom += 1
                    continue

                symptom = all_symptoms.get(pt_name)
                if not symptom:
                    skipped_no_symptom += 1
                    continue

                existing = db.query(DiagnosticCriteria).filter_by(
                    disorder_id=disorder.disorder_id,
                    symptom_id=symptom.symptom_id,
                ).first()
                if not existing:
                    db.add(DiagnosticCriteria(
                        disorder_id=disorder.disorder_id,
                        symptom_id=symptom.symptom_id,
                        required_presence=required,
                        minimum_duration_days=min_dur if min_dur else None,
                        clinical_notes=desc_text,
                    ))
                    crit_count += 1

        db.commit()
        print(f"OK - {crit_count} diagnostic criteria seeded for reference disorders")
        if skipped_no_symptom:
            print(f"  ({skipped_no_symptom} symptom keys skipped — EN_TO_PT_SYMPTOM or Symptom DB record missing)")
        print("\nSeed do catálogo completo finalizado!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
