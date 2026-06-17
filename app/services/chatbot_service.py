import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.base import (
    AssessmentScale, ChatFeedback, ChatMessage, DiagnosticCriteria,
    Disorder, ICD11Code, ICD11Differential, ICD11Exclusion,
    MIAKnowledge, Medication, Symptom,
)


SENTIMENTO_POSITIVO: set = {
    "bom", "otimo", "otima", "excelente", "melhor", "bem", "obrigado", "obrigada",
    "sim", "positivo", "feliz", "tranquilo", "tranquila", "calma", "calmo",
    "esperanca", "melhora", "recuperacao", "progresso", "alivio", "aliviar",
    "satisfeito", "satisfeita", "confiante", "esperancoso", "otimista",
    "gratidao", "grato", "grata", "alegre", "alegria", "motivado",
}
SENTIMENTO_NEGATIVO: set = {
    "ruim", "pessimo", "pessima", "horrivel", "pior", "mal", "triste",
    "ansioso", "ansiosa", "deprimido", "deprimida", "preocupado", "preocupada",
    "medo", "dor", "sofrimento", "crise", "panico", "angustia", "angustiado",
    "cansado", "cansada", "fadiga", "insonia", "desespero", "desesperado",
    "irritado", "irritada", "solidao", "sozinho", "sozinha", "choro", "chorar",
    "suicida", "morte", "morrer", "pesadelo", "terror", "agonia", "desamparo",
    "fracasso", "inutil", "culpa", "vergonha", "odio", "raiva", "nervoso",
    "inquieto", "inquieta", "tenso", "tensa", "dificuldade", "problema",
}
SENTIMENTO_INTENSIFICADOR: set = {
    "muito", "bastante", "extremamente", "intensamente", "demais",
    "completamente", "totalmente", "profundamente", "fortemente",
}

STOPWORDS: set = {
    "para", "com", "sobre", "como", "qual", "quais", "tem", "tive",
    "esta", "estar", "mas", "mais", "vou", "por", "que",
    "dos", "das", "nas", "nos", "num", "numa", "aos", "aas",
    "voce", "pode", "sao", "seu", "sua", "ela", "ele",
    "isso", "isto", "aquilo", "esse", "essa", "este", "esta",
    "criterio", "criterios", "exclusao", "exclusoes", "diagnostico",
    "diagnosticos", "sintoma", "sintomas", "algum", "alguma",
    "quando", "onde", "aonde", "nisto", "nisso", "daquele",
    "todos", "todas", "nenhum", "nenhuma", "todo", "toda",
    "apenas", "somente", "tambem", "entao", "entao",
    "transtorno", "transtornos",
}


class SentimentoAnalyzer:
    def analisar(self, texto: str) -> Dict:
        tokens = re.findall(r'\w+', texto.lower())
        pontuacao = 0
        intensidade = 1.0
        for t in tokens:
            if t in SENTIMENTO_INTENSIFICADOR:
                intensidade += 0.3
            elif t in SENTIMENTO_POSITIVO:
                pontuacao += 1 * intensidade
                intensidade = 1.0
            elif t in SENTIMENTO_NEGATIVO:
                pontuacao -= 1 * intensidade
                intensidade = 1.0
            else:
                intensidade = 1.0
        if pontuacao > 0:
            rotulo = "positivo"
            score = min(pontuacao / 5.0, 1.0)
        elif pontuacao < 0:
            rotulo = "negativo"
            score = min(abs(pontuacao) / 5.0, 1.0)
        else:
            rotulo = "neutro"
            score = 0.5
        return {"rotulo": rotulo, "score": round(score, 4)}


class MiaService:
    """MIA chatbot service with conversation persistence and ML self-improvement."""

    def __init__(self, session: Session, user_uuid: Optional[str] = None):
        self.session = session
        self.user_uuid = user_uuid
        self.sentimento = SentimentoAnalyzer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def processar_query(self, mensagem: str, session_id: Optional[str] = None) -> Dict:
        """Process a user query, persist conversation, return response."""
        if not session_id:
            session_id = str(uuid4())

        sentimento = self.sentimento.analisar(mensagem)
        termos = self._extrair_termos(mensagem)

        # Check MIA knowledge base first (fast path)
        knowledge_matches = self._buscar_conhecimento(termos)

        # Full disorder search
        transtornos = self._buscar_transtornos(termos)
        resultados = self._montar_resultados(transtornos, termos)
        sintomas = self._buscar_sintomas(termos)
        medicamentos = self._buscar_medicamentos(termos)
        escalas = self._buscar_escalas(termos)

        # Enhance results with inference probabilities
        resultados = self._enriquecer_com_inferencia(resultados, termos)

        # Check for suicidal ideation escalation
        alerta_suicidio = self._detectar_alerta_suicidio(mensagem)

        resposta = self._gerar_resposta(
            resultados, sentimento, mensagem, sintomas, medicamentos, escalas,
            knowledge_matches, alerta_suicidio,
        )

        metadata = {
            "sentimento": sentimento,
            "n_resultados": len(resultados),
            "n_sintomas": len(sintomas),
            "n_medicamentos": len(medicamentos),
            "n_escalas": len(escalas),
            "n_conhecimento": len(knowledge_matches),
            "alerta_suicidio": alerta_suicidio,
        }

        # Persist conversation
        self._salvar_mensagem(session_id, "user", mensagem, None)
        self._salvar_mensagem(session_id, "bot", resposta, metadata)

        # Update knowledge usage counters
        for k in knowledge_matches:
            self._incrementar_uso_conhecimento(k["knowledge_id"])

        return {
            "sentimento": sentimento,
            "resultados": resultados,
            "sintomas": sintomas,
            "medicamentos": medicamentos,
            "escalas": escalas,
            "resposta": resposta,
            "session_id": session_id,
        }

    def register_feedback(
        self, message_id: int, rating: str,
        corrected_text: Optional[str] = None,
    ) -> Dict:
        """Register user feedback on a bot response and trigger learning."""
        feedback = ChatFeedback(
            message_id=message_id,
            user_uuid=self.user_uuid,
            rating=rating,
            corrected_text=corrected_text,
        )
        self.session.add(feedback)
        self.session.flush()

        # Update knowledge base based on feedback
        self._aprender_com_feedback(message_id, rating, corrected_text)

        return {
            "feedback_id": feedback.feedback_id,
            "message_id": message_id,
            "rating": rating,
        }

    def get_conversation_history(
        self, session_id: str, limit: int = 50,
    ) -> List[Dict]:
        """Retrieve conversation history for a session."""
        msgs = (
            self.session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
            .all()
        )
        return [
            {
                "message_id": m.message_id,
                "role": m.role,
                "content": m.content,
                "metadata_json": m.metadata_json,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in msgs
        ]

    # ------------------------------------------------------------------
    # Knowledge base (ML self-improvement)
    # ------------------------------------------------------------------

    def _extrair_termos(self, mensagem: str) -> List[str]:
        termos = re.findall(r'\b[a-zA-ZÀ-ÿ]{3,}\b', mensagem)
        return list(set(t.lower() for t in termos if t.lower() not in STOPWORDS))

    def _buscar_conhecimento(self, termos: List[str]) -> List[Dict]:
        """Fast-path: check MIA knowledge base for known term patterns."""
        if not termos:
            return []
        matches = []
        knowledge = self.session.query(MIAKnowledge).all()
        for k in knowledge:
            try:
                terms = json.loads(k.trigger_terms)
            except (json.JSONDecodeError, TypeError):
                continue
            if any(t in termos for t in terms):
                matches.append({
                    "knowledge_id": k.knowledge_id,
                    "response_template": k.response_template,
                    "confidence": float(k.confidence or 0.5),
                    "disorder_id": k.disorder_id,
                    "scale_name": k.scale_name,
                })
        return sorted(matches, key=lambda x: x["confidence"], reverse=True)[:3]

    def _aprender_com_feedback(
        self, message_id: int, rating: str, corrected_text: Optional[str],
    ):
        """Learn from feedback: update knowledge confidence, create new knowledge."""
        msg = self.session.query(ChatMessage).filter(
            ChatMessage.message_id == message_id
        ).first()
        if not msg or msg.metadata_json is None:
            return

        try:
            meta = json.loads(msg.metadata_json)
        except (json.JSONDecodeError, TypeError):
            return

        n_resultados = meta.get("n_resultados", 0)

        if rating == "positive" and n_resultados > 0:
            termos = self._extrair_termos(msg.content) if msg.role == "user" else []
            if termos:
                existing = self.session.query(MIAKnowledge).filter(
                    MIAKnowledge.trigger_terms == json.dumps(termos, ensure_ascii=False)
                ).first()
                if existing:
                    existing.confidence = min(float(existing.confidence or 0.5) + 0.05, 1.0)
                    existing.positive_feedback = (existing.positive_feedback or 0) + 1
                else:
                    knowledge = MIAKnowledge(
                        trigger_terms=json.dumps(termos, ensure_ascii=False),
                        response_template=msg.content if msg.role == "bot" else "Padrão aprendido via feedback positivo",
                        confidence=0.5,
                        source="learned",
                        times_used=0,
                        positive_feedback=1,
                        negative_feedback=0,
                    )
                    self.session.add(knowledge)
                self.session.flush()

        elif rating == "negative":
            if n_resultados > 0:
                termos = self._extrair_termos(msg.content) if msg.role == "user" else []
                for t in termos:
                    matches = self.session.query(MIAKnowledge).filter(
                        MIAKnowledge.trigger_terms.like(f"%{t}%")
                    ).all()
                    for m in matches:
                        m.confidence = max(float(m.confidence or 0.5) - 0.1, 0.0)
                        m.negative_feedback = (m.negative_feedback or 0) + 1

            if corrected_text:
                corrected_terms = self._extrair_termos(corrected_text)
                if corrected_terms:
                    existing_corrected = self.session.query(MIAKnowledge).filter(
                        MIAKnowledge.trigger_terms == json.dumps(corrected_terms, ensure_ascii=False)
                    ).first()
                    if not existing_corrected:
                        knowledge = MIAKnowledge(
                            trigger_terms=json.dumps(corrected_terms, ensure_ascii=False),
                            response_template=corrected_text,
                            confidence=0.6,
                            source="learned",
                            positive_feedback=0,
                            negative_feedback=0,
                        )
                        self.session.add(knowledge)
                    self.session.flush()

    def _incrementar_uso_conhecimento(self, knowledge_id: int):
        self.session.query(MIAKnowledge).filter(
            MIAKnowledge.knowledge_id == knowledge_id
        ).update({MIAKnowledge.times_used: MIAKnowledge.times_used + 1})
        self.session.flush()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _salvar_mensagem(self, session_id: str, role: str, content: str, metadata: Optional[Dict]):
        msg = ChatMessage(
            session_id=session_id,
            user_uuid=self.user_uuid,
            role=role,
            content=content,
            metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
        )
        self.session.add(msg)
        self.session.flush()

    # ------------------------------------------------------------------
    # Disorder search (existing logic)
    # ------------------------------------------------------------------

    def _buscar_transtornos(self, termos: List[str]) -> List[Disorder]:
        if not termos:
            return []
        padroes = [f"%{t}%" for t in termos]
        filtros_nome = [Disorder.disorder_name.ilike(p) for p in padroes]
        name_matches = (
            self.session.query(Disorder)
            .filter(or_(*filtros_nome))
            .order_by(Disorder.disorder_name)
            .all()
        )
        ids_nome = {d.disorder_id for d in name_matches}
        filtros_texto = []
        for p in padroes:
            filtros_texto.extend([
                Disorder.disorder_description.ilike(p),
                Disorder.dsm_criteria.ilike(p),
                Disorder.dsm_exclusions.ilike(p),
                Disorder.dsm_differentials.ilike(p),
                Disorder.icd11_exclusions.ilike(p),
                Disorder.icd11_differentials.ilike(p),
            ])
        text_matches = (
            self.session.query(Disorder)
            .filter(or_(*filtros_texto))
            .filter(~Disorder.disorder_id.in_(ids_nome)) if ids_nome else
            self.session.query(Disorder)
            .filter(or_(*filtros_texto))
        ).all() if filtros_texto else []
        return name_matches + text_matches

    def _montar_resultados(self, transtornos: List[Disorder], termos: List[str]) -> List[Dict]:
        name_scores = {}
        for t in termos:
            for d in transtornos:
                if t in d.disorder_name.lower():
                    name_lower = d.disorder_name.lower()
                    match_count = sum(1 for term in termos if term in name_lower)
                    match_ratio = match_count / max(len(termos), 1)
                    if d.disorder_id not in name_scores or match_ratio > name_scores[d.disorder_id]:
                        name_scores[d.disorder_id] = match_ratio

        sorted_name_ids = sorted(name_scores.keys(), key=lambda x: name_scores[x], reverse=True)
        name_set = set(sorted_name_ids)

        resultados = []
        for did in sorted_name_ids:
            d = next(di for di in transtornos if di.disorder_id == did)
            resultados.append(self._montar_item(d, termos, True))

        for d in transtornos:
            if d.disorder_id not in name_set:
                resultados.append(self._montar_item(d, termos, False))

        return resultados

    def _montar_item(self, d: Disorder, termos: List[str], is_name_match: bool) -> Dict:
        criterios = self._buscar_criterios(d.disorder_id)
        criterios_texto = self._formatar_criterios(criterios)
        return {
            "disorder_id": d.disorder_id,
            "disorder_name": d.disorder_name,
            "cid_code": d.cid_code,
            "dsm_code": d.dsm_code,
            "disorder_description": d.disorder_description,
            "dsm_criteria": d.dsm_criteria,
            "dsm_exclusions": d.dsm_exclusions,
            "dsm_differentials": d.dsm_differentials,
            "icd11_exclusions": d.icd11_exclusions,
            "icd11_differentials": d.icd11_differentials,
            "criterios_detalhados": criterios_texto,
            "_name_match": is_name_match,
            "inference_probability": None,
        }

    def _buscar_criterios(self, disorder_id: int) -> List[DiagnosticCriteria]:
        return (
            self.session.query(DiagnosticCriteria)
            .filter(DiagnosticCriteria.disorder_id == disorder_id)
            .all()
        )

    def _formatar_criterios(self, criterios: List[DiagnosticCriteria]) -> List[Dict]:
        resultado = []
        for c in criterios:
            sintoma = (
                self.session.query(Symptom)
                .filter(Symptom.symptom_id == c.symptom_id)
                .first()
            )
            resultado.append({
                "criteria_id": c.criteria_id,
                "symptom_name": sintoma.symptom_name if sintoma else None,
                "required_presence": c.required_presence,
                "minimum_duration_days": c.minimum_duration_days,
                "clinical_notes": c.clinical_notes,
            })
        return resultado

    def _buscar_sintomas(self, termos: List[str]) -> List[Dict]:
        if not termos:
            return []
        padroes = [f"%{t}%" for t in termos]
        filtros = [Symptom.symptom_name.ilike(p) for p in padroes]
        encontrados = (
            self.session.query(Symptom)
            .filter(or_(*filtros))
            .order_by(Symptom.symptom_name)
            .limit(10)
            .all()
        )
        return [{"symptom_id": s.symptom_id, "symptom_name": s.symptom_name} for s in encontrados]

    def _buscar_medicamentos(self, termos: List[str]) -> List[Dict]:
        if not termos:
            return []
        padroes = [f"%{t}%" for t in termos]
        filtros = []
        for p in padroes:
            filtros.extend([Medication.name.ilike(p), Medication.active_ingredient.ilike(p)])
        encontrados = (
            self.session.query(Medication)
            .filter(or_(*filtros))
            .order_by(Medication.name)
            .limit(10)
            .all()
        )
        return [{"medication_id": m.medication_id, "name": m.name, "active_ingredient": m.active_ingredient, "classification": m.classification} for m in encontrados]

    def _buscar_escalas(self, termos: List[str]) -> List[Dict]:
        if not termos:
            return []
        padroes = [f"%{t}%" for t in termos]
        filtros = [AssessmentScale.scale_name.ilike(p) for p in padroes]
        encontrados = (
            self.session.query(AssessmentScale)
            .filter(or_(*filtros))
            .order_by(AssessmentScale.scale_name)
            .limit(10)
            .all()
        )
        return [{"scale_id": s.scale_id, "scale_name": s.scale_name, "description": s.scale_description} for s in encontrados]

    # ------------------------------------------------------------------
    # ML integration — enrich results with inference probabilities
    # ------------------------------------------------------------------

    def _enriquecer_com_inferencia(
        self, resultados: List[Dict], termos: List[str],
    ) -> List[Dict]:
        """Apply ML inference probabilities to disorder results based on symptom terms."""
        if not resultados or not termos:
            return resultados

        try:
            from app.ml.predictors.scale_predictor import predict_disorder_risk_from_scales

            feature_vector = self._construir_vetor_sintomas(termos)
            if feature_vector:
                risks = predict_disorder_risk_from_scales(feature_vector)
                if risks and "probabilidades" in risks:
                    prob_map = {}
                    for item in risks["probabilidades"]:
                        prob_map[item.get("nome", "").lower()] = item.get("probabilidade", 0.0)

                    for r in resultados:
                        name_lower = r["disorder_name"].lower()
                        if name_lower in prob_map:
                            r["inference_probability"] = round(prob_map[name_lower], 4)
        except ImportError:
            pass
        except Exception:
            pass

        return resultados

    def _construir_vetor_sintomas(self, termos: List[str]) -> List[float]:
        """Build a simplified feature vector from symptom terms for ML inference."""
        symptom_scale_map = {
            "depressao": 1, "deprimido": 1, "triste": 1, "cansa": 1,
            "ansiedade": 2, "ansioso": 2, "nervoso": 2, "preocupado": 2,
            "insonia": 3, "sono": 3, "dormir": 3,
            "panico": 4, "medo": 4, "ataque": 4,
            "trauma": 5, "transtorno estresse": 5,
            "obsessivo": 6, "compulsivo": 6, "toc": 6,
            "bipolar": 7, "mania": 7, "euforia": 7,
            "alcool": 8, "substancia": 8, "drogas": 8,
            "anorexia": 9, "alimentar": 9, "comer": 9, "peso": 9,
            "autismo": 10, "tea": 10, "autista": 10,
            "tdah": 10, "atencao": 10, "hiperatividade": 10,
        }
        scores = {}
        for t in termos:
            if t in symptom_scale_map:
                key = symptom_scale_map[t]
                scores[key] = scores.get(key, 0) + 1

        if not scores:
            return []

        # Return as ordered feature vector matching scale_predictor expectations
        known_scales = list(range(1, 11))
        return [float(scores.get(s, 0)) for s in known_scales]

    # ------------------------------------------------------------------
    # Suicide alert detection
    # ------------------------------------------------------------------

    def _detectar_alerta_suicidio(self, mensagem: str) -> bool:
        msg_lower = mensagem.lower()
        suicide_terms = {
            "suicida", "suicidio", "morrer", "morte", "acabar com a vida",
            "acabar com tudo", "quero morrer", "vou morrer", "melhor estar morto",
            "nao quero mais viver", "sem esperanca", "desistir",
        }
        return any(t in msg_lower for t in suicide_terms)

    def _formatar_extras(
        self, sintomas: List[Dict] = None, medicamentos: List[Dict] = None, escalas: List[Dict] = None,
    ) -> str:
        partes = []
        n_sintomas = len(sintomas or [])
        n_medicamentos = len(medicamentos or [])
        n_escalas = len(escalas or [])
        if n_sintomas > 0:
            partes.append("**Sintomas encontrados ({}):**".format(n_sintomas))
            for s in sintomas[:5]:
                partes.append("  - {}".format(s['symptom_name']))
        if n_medicamentos > 0:
            partes.append("**Medicamentos encontrados ({}):**".format(n_medicamentos))
            for m in medicamentos[:5]:
                ing = " ({})".format(m['active_ingredient']) if m.get("active_ingredient") else ""
                cls = " - {}".format(m['classification']) if m.get("classification") else ""
                partes.append("  - {}{}{}".format(m['name'], ing, cls))
        if n_escalas > 0:
            partes.append("**Escalas encontradas ({}):**".format(n_escalas))
            for e in escalas[:5]:
                partes.append("  - {}".format(e['scale_name']))
        return "\n\n" + "\n".join(partes) if partes else ""

    # ------------------------------------------------------------------
    # Response generation
    # ------------------------------------------------------------------

    def _gerar_resposta(
        self,
        resultados: List[Dict],
        sentimento: Dict,
        mensagem: str,
        sintomas: List[Dict] = None,
        medicamentos: List[Dict] = None,
        escalas: List[Dict] = None,
        knowledge_matches: List[Dict] = None,
        alerta_suicidio: bool = False,
    ) -> str:
        n = len(resultados)
        n_sintomas = len(sintomas or [])
        n_medicamentos = len(medicamentos or [])
        n_escalas = len(escalas or [])
        tem_extra = n_sintomas > 0 or n_medicamentos > 0 or n_escalas > 0

        # Suicide alert overrides everything
        if alerta_suicidio:
            return (
                "**ALERTA DE CRISE**\n\n"
                "Percebi que sua mensagem pode conter pensamentos relacionados a suicídio ou autolesão. "
                "Isso é muito importante e requer atenção imediata.\n\n"
                "LIGUE AGORA para o Centro de Valorização da Vida (CVV) - 188\n"
                "   Atendimento 24 horas, gratuito e sigiloso.\n\n"
                "Procure o hospital mais proximo ou a UPA (Unidade de Pronto Atendimento).\n\n"
                "Agende uma consulta urgente com seu psiquiatra ou psicologo.\n\n"
                "Voce nao esta sozinho(a). Ha ajuda disponivel."
            )

        # Knowledge base fast-response (prefer when no disorders found)
        if knowledge_matches and n == 0:
            k = knowledge_matches[0]
            extra_section = ""
            if tem_extra:
                extra_section = self._formatar_extras(sintomas, medicamentos, escalas)
            return k["response_template"] + extra_section

        if n == 0 and not tem_extra:
            return (
                "MIA não encontrou transtornos relacionados à sua consulta "
                "no banco de dados. Tente termos mais específicos como o nome "
                "de um transtorno, sintoma, ou critério diagnóstico."
            )

        name_matches = [r for r in resultados if r.get("_name_match")]
        if name_matches:
            mostrados = name_matches
        else:
            mostrados = resultados[:5]

        n_mostra = len(mostrados)
        prefixo = f"Encontrei {n} transtorno{'s' if n > 1 else ''}"
        if n > n_mostra:
            prefixo += f" (mostrando os {n_mostra} mais relevantes)"
        prefixo += ":\n\n"
        resposta = prefixo

        for i, r in enumerate(mostrados, 1):
            nome = r["disorder_name"]
            cid = r["cid_code"] or "—"
            dsm = r["dsm_code"] or "—"
            desc = r["disorder_description"] or ""
            prob = r.get("inference_probability")
            resposta += f"{i}. **{nome}** (CID: {cid} | DSM: {dsm})"
            if prob is not None:
                pct = round(prob * 100, 1)
                bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
                resposta += f"  `{bar} {pct}%`"
            resposta += "\n"
            if desc:
                resposta += f"   {desc[:200]}{'...' if len(desc) > 200 else ''}\n"
            if r["dsm_criteria"]:
                resposta += f"   **Criterios DSM-5-TR:** {r['dsm_criteria'][:300]}{'...' if len(r['dsm_criteria']) > 300 else ''}\n"
            if r["dsm_exclusions"]:
                resposta += f"   **Exclusoes DSM-5:** {r['dsm_exclusions'][:200]}{'...' if len(r['dsm_exclusions']) > 200 else ''}\n"
            if r["icd11_exclusions"]:
                resposta += f"   **Exclusoes CID-11:** {r['icd11_exclusions'][:200]}{'...' if len(r['icd11_exclusions']) > 200 else ''}\n"
            if r["dsm_differentials"]:
                resposta += f"   **Diagnostico Diferencial (DSM-5):** {r['dsm_differentials'][:200]}{'...' if len(r['dsm_differentials']) > 200 else ''}\n"
            if r["criterios_detalhados"]:
                resposta += f"   **Criterios diagnosticos detalhados ({len(r['criterios_detalhados'])} itens):**\n"
                for cr in r["criterios_detalhados"][:10]:
                    sn = cr["symptom_name"] or "Sintoma #" + str(cr["criteria_id"])
                    req = "obrigatório" if cr["required_presence"] else "opcional"
                    dur = f", duração mínima: {cr['minimum_duration_days']} dias" if cr["minimum_duration_days"] else ""
                    resposta += f"     • {sn} ({req}{dur})\n"
            resposta += "\n"

        if tem_extra:
            resposta += self._formatar_extras(sintomas, medicamentos, escalas)

        if sentimento["rotulo"] == "negativo":
            resposta += (
                "\n\nPercebo que você pode estar passando por um momento difícil. "
                "Lembre-se que este é um sistema de apoio ao diagnóstico e "
                "todas as conclusões devem ser validadas por um profissional "
                "de saúde mental qualificado (CRM/CRP)."
            )
        elif sentimento["rotulo"] == "positivo":
            resposta += (
                "\n\nFico feliz em poder ajudar! "
                "Caso precise de mais informações sobre algum transtorno "
                "específico, é só perguntar."
            )
        else:
            resposta += (
                "\n\nPara informações mais detalhadas, pergunte sobre um "
                "transtorno específico, sintoma, medicamento ou escala, "
                "ou consulte a seção de Transtornos no menu Admin."
            )

        return resposta
