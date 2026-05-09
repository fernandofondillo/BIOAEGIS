"""
==============================================================================
MODERATOR AGENT — Dr. Hallmarks + Dr. Mechanism + Consensus Engine
==============================================================================

El MODERATOR es el DIRECTOR MÉDICO del equipo de 18 agentes.
No es un agente más — es el validador científico que:
  1. Recibe las recomendaciones de los agentes
  2. Las valida contra Dr. Hallmarks (longevidad) y Dr. Mechanism (biología molecular)
  3. Consulta Hard Constraints DB para asegurar biológicamente posible
  4. Genera CONSENSUS entre múltiples agentes
  5. Presenta el resultado final al usuario

Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .signals import Signal, SignalBus, SignalPriority, signal_bus
from .constraints import constraints_db, HardConstraintsDB
from .biofacts import BioFactsDB, BioFact, EvidenceLevel, RecommendationGrade


# ─────────────────────────────────────────────────────────────────────────────
# CONSENSUS RESULT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ConsensusResult:
    """Resultado del consensus engine."""
    recommendation: str
    supporting_agents: List[str]
    evidence_level: EvidenceLevel
    recommendation_grade: RecommendationGrade
    confidence: float
    caveats: List[str]
    risks: List[str]
    alternative: Optional[str] = None
    biomarker_changes: Dict[str, float] = field(default_factory=dict)
    timeframe_months: int = 3


@dataclass
class ModeratorOutput:
    """Output final del moderador — lo que ve el usuario."""
    tick: int
    timestamp: datetime
    user_question: str
    agents_consulted: List[str]
    consensus: ConsensusResult
    raw_agent_outputs: List[Dict]  # Para que el usuario pueda ver el reasoning de cada agente
    clock_results: Dict  # Resultados de los biological clocks
    critical_signals: List[Dict]  # Señales CRITICAL sin resolver
    confidence: float
    disclaimer: str = (
        "Esta información es orientativa y no sustituye el consejo médico profesional. "
        "Consulta siempre con tu médico antes de hacer cambios significativos."
    )

    def to_dict(self) -> Dict:
        return {
            "tick": self.tick,
            "timestamp": self.timestamp.isoformat(),
            "user_question": self.user_question,
            "agents_consulted": self.agents_consulted,
            "consensus": {
                "recommendation": self.consensus.recommendation,
                "supporting_agents": self.consensus.supporting_agents,
                "evidence_level": self.consensus.evidence_level.value,
                "grade": self.consensus.recommendation_grade.value,
                "confidence": round(self.consensus.confidence, 2),
                "caveats": self.consensus.caveats,
                "risks": self.consensus.risks,
                "alternative": self.consensus.alternative,
                "biomarker_changes": {k: round(v, 2) for k, v in self.consensus.biomarker_changes.items()},
                "timeframe_months": self.consensus.timeframe_months,
            },
            "clock_results": self.clock_results,
            "critical_signals": self.critical_signals,
            "confidence": round(self.confidence, 2),
            "disclaimer": self.disclaimer,
        }

    def to_user_friendly(self) -> str:
        """Convierte el output a texto legible para el usuario."""
        c = self.consensus
        grade_emoji = {
            "STRONG FOR": "✅",
            "WEAK FOR": "🟡",
            "NEUTRAL": "⚪",
            "WEAK AGAINST": "🟠",
            "STRONG AGAINST": "🚫",
        }.get(c.recommendation_grade.value, "⚪")

        return f"""
{grade_emoji} RECOMENDACIÓN DEL EQUIPO MÉDICO
{'═' * 45}
{c.recommendation}

📋 NIVEL DE EVIDENCIA: {c.evidence_level.value}
   Grado de recomendación: {c.recommendation_grade.value}

🤝 AGENTES CONSULTADOS ({len(self.agents_consulted)}):
   {', '.join(self.agents_consulted)}

⏱️ PLAZO ESTIMADO: {c.timeframe_months} meses
   Cambios esperados en biomarcadores:
   {', '.join([f"{k}: {v:+.1f}" for k, v in c.biomarker_changes.items()]) or 'No cuantificados aún'}

⚠️ PRECAUCIONES:
   {' | '.join(c.caveats) if c.caveats else 'Ninguna específica'}

⚡ RIESGOS:
   {' | '.join(c.risks) if c.risks else 'No identificados'}

💡 ALTERNATIVA:
   {c.alternative or 'No disponible'}

🔬 CONFIANZA DEL EQUIPO: {int(c.confidence * 100)}%
   ({len(self.agents_consulted)} agentes en consenso)

{'=' * 45}
{self.disclaimer}
"""


# ─────────────────────────────────────────────────────────────────────────────
# DR. HALLMARKS — LONGEVIDAD EXPERT
# ─────────────────────────────────────────────────────────────────────────────

class DrHallmarks:
    """
    Dr. Hallmarks — Experto en Longevidad.
    Conocimiento: Los 12 hallmarks del envejecimiento (López-Otín 2013),
    intervenciones que funcionan en humanos, niveles de evidencia.
    """

    HALLMARKS = [
        "Genomic instability",
        "Telomere attrition",
        "Epigenetic alterations",
        "Loss of proteostasis",
        "Deregulated nutrient sensing",
        "Mitochondrial dysfunction",
        "Cellular senescence",
        "Stem cell exhaustion",
        "Altered intercellular communication",
        "Disabled macroautophagy",
        "Inflammaging",
        "Dysbiosis",
    ]

    INTERVENTIONS_EVIDENCE: Dict[str, Dict[str, Any]] = {
        "ejercicio_aerobico": {
            "hallmark": ["mitochondrial dysfunction", "deregulated nutrient sensing",
                        "cellular senescence", "inflammaging"],
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.STRONG_FOR,
            "effect": "Reduce mortalidad 20-35%, mejora VO2max 15-30% en 12 semanas",
            "caveats": "Riesgo cardiaco agudo si >90% VO2max sin evaluación previa",
        },
        "ejercicio_resistencia": {
            "hallmark": ["stem cell exhaustion", "mitochondrial dysfunction", "proteostasis"],
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.STRONG_FOR,
            "effect": "Preserva masa muscular, previene sarcopenia, mejora densidad ósea",
            "caveats": "En >65 años consultar cardiólogo antes de ejercicio de alta intensidad",
        },
        "ayuno_intermitente": {
            "hallmark": ["deregulated nutrient sensing", "disabled macroautophagy",
                        "inflammaging", "mitochondrial dysfunction"],
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.STRONG_FOR,
            "effect": "Mejora HOMA-IR 10-25%, reduce CRP 10-20% en 12 semanas",
            "caveats": "En diabéticos T1/T2 insulin-dependientes: riesgo hipoglucemia. No en anorexia.",
        },
        "dieta_mediterranea": {
            "hallmark": ["inflammaging", "dyskiosis", "cardiovascular risk"],
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.STRONG_FOR,
            "effect": "Reduce eventos cardiovasculares 30% (PREDIMED trial)",
            "caveats": "Beneficio desaparece si se usan aceites refinados en vez de AOVE",
        },
        "omega3_epa_dha": {
            "hallmark": ["inflammaging", "cardiovascular risk"],
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.STRONG_FOR,
            "effect": "Reduce triglicéridos 15-30%, reduce riesgo cardiovascular",
            "caveats": "Puede aumentar tiempo de sangrado — precaución en anticoagulados",
        },
        "metformina": {
            "hallmark": ["deregulated nutrient sensing", "mitochondrial dysfunction",
                        "inflammaging"],
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.WEAK_FOR,
            "effect": "Reduce HbA1c 1-1.5%, reduce progresión a diabetes 31% (DPP study)",
            "caveats": "Causa déficit B12 (10-30% uso prolongado). Contraindicada en IRC severa.",
        },
        "resveratrol": {
            "hallmark": ["mitochondrial dysfunction", "inflammaging"],
            "evidence": EvidenceLevel.C,
            "grade": RecommendationGrade.NEUTRAL,
            "effect": "Mejora marginal sensibilidad a insulina en algunos estudios",
            "caveats": "Dosis >250mg/día puede interactuar con warfarina",
        },
        "nmn_suplemento": {
            "hallmark": ["mitochondrial dysfunction", "deregulated nutrient sensing"],
            "evidence": EvidenceLevel.C,
            "grade": RecommendationGrade.NEUTRAL,
            "effect": "Aumenta NAD+ 40-100% en sangre. Outcome clínico aún no establecido.",
            "caveats": "No es standard of care. Costo elevado. Evidencia clínica débil.",
        },
        "rapamicina": {
            "hallmark": ["deregulated nutrient sensing", "disabled macroautophagy",
                        "cellular senescence"],
            "evidence": EvidenceLevel.C,
            "grade": RecommendationGrade.STRONG_AGAINST,
            "effect": "Extiende lifespan 10-25% en ratones. En humanos: immunosupresión severa.",
            "caveats": "NO USAR sin supervisión oncológica. Auto-experimentación es peligrosa.",
        },
    }

    @classmethod
    def validate_intervention(
        cls, intervention_name: str, context: Dict
    ) -> Tuple[bool, str, RecommendationGrade, List[str]]:
        """
        Valida si una intervención tiene sentido desde la perspectiva de longevity.

        Returns: (is_valid, explanation, grade, caveats)
        """
        intervention_key = intervention_name.lower().replace(" ", "_")
        if intervention_key not in cls.INTERVENTIONS_EVIDENCE:
            return (
                True,  # No tenemos info — no bloqueamos
                f"No tenemos datos de evidencia para '{intervention_name}' en nuestra base.",
                RecommendationGrade.NEUTRAL,
                []
            )

        info = cls.INTERVENTIONS_EVIDENCE[intervention_key]
        hallmarks = info["hallmark"]
        evidence = info["evidence"]
        grade = info["grade"]
        caveats = [info.get("caveats", "")] if info.get("caveats") else []

        evidence_icons = {"A": "🟢", "B": "🟡", "C": "⚪", "D": "🔴"}
        icon = evidence_icons.get(evidence.value, "⚪")

        explanation = (
            f"'{intervention_name}' actúa sobre: {', '.join(hallmarks)}. "
            f"Evidencia: {evidence.value} {icon}. "
            f"Efecto: {info['effect']}."
        )

        if grade == RecommendationGrade.STRONG_AGAINST:
            return False, explanation, grade, caveats

        return True, explanation, grade, caveats

    @classmethod
    def get_recommended_interventions(cls, current_biomarkers: Dict) -> List[Dict]:
        """Devuelve intervenciones recomendadas según el perfil del usuario."""
        recommendations = []

        # Ejercicio siempre recomendado si no hay contraindicación
        recommendations.append({
            "intervention": "Ejercicio aeróbico 150-300 min/sem",
            "evidence": EvidenceLevel.A,
            "grade": RecommendationGrade.STRONG_FOR,
            "reason": "Intervención con mayor nivel de evidencia para reducir mortalidad y mejorar función mitocondrial",
        })

        if current_biomarkers.get("ldl_cholesterol", 0) > 130:
            recommendations.append({
                "intervention": "Dieta mediterránea con AOVE",
                "evidence": EvidenceLevel.A,
                "grade": RecommendationGrade.STRONG_FOR,
                "reason": "Reduce eventos cardiovasculares 30% (PREDIMED)",
            })

        if current_biomarkers.get("homa_ir", 0) > 2.5:
            recommendations.append({
                "intervention": "Ayuno intermitente 16:8",
                "evidence": EvidenceLevel.A,
                "grade": RecommendationGrade.STRONG_FOR,
                "reason": "Mejora HOMA-IR 10-25% en 12 semanas",
            })

        if current_biomarkers.get("c_reactive_protein", 0) > 3.0:
            recommendations.append({
                "intervention": "EPA+DHA 2-3g/día + ejercicio",
                "evidence": EvidenceLevel.A,
                "grade": RecommendationGrade.STRONG_FOR,
                "reason": "Reduce PCR 10-20%, efecto antiinflamatorio aditivo con ejercicio",
            })

        return recommendations


# ─────────────────────────────────────────────────────────────────────────────
# DR. MECHANISM — BIOLOGÍA MOLECULAR EXPERT
# ─────────────────────────────────────────────────────────────────────────────

class DrMechanism:
    """
    Dr. Mechanism — Experto en Biología Molecular.
    Valida mecanismos: si el agente dice "voy a bloquear mTOR completamente",
    este doctor dice "imposible — mTOR es esencial para supervivencia".
    """

    MOLECULAR_PATHWAYS = {
        "AMPK": {
            "activators": ["ayuno", "ejercicio", "metformina", "AICAR"],
            "inhibitors": ["insulina", "glucosa alta", "aminoácidos"],
            "downstream": ["mTOR inhibition", "autophagy activation", "fatty acid oxidation",
                          "glucose uptake improvement", "mitochondrial biogenesis"],
            "clinical_relevance": "AMPK es el master regulator del metabolism — su activación mejora sensibilidad a insulina y reduce inflamación.",
        },
        "mTOR": {
            "activators": ["aminoácidos (especialmente leucina)", "insulina", "IGF-1",
                          "glucosa", "growth factors"],
            "inhibitors": ["rapamicina", "ayuno prolongado (>24h)", "AMPK activation"],
            "downstream": ["protein synthesis", "cell growth", "lipogenesis",
                          "inflammation promotion", "autophagy inhibition"],
            "clinical_relevance": "mTOR es esencial — su bloqueo total es incompatible con vida. La inhibición PARCIAL (rapamicina en dosis bajas) mimetiza ayuno.",
        },
        "NAD+": {
            "precursors": ["NMN", "NR", "nicotinamida", "tryptophan"],
            "consumers": ["SIRT1", "SIRT3", "PARPs", "CD38"],
            "declines_with_age": "NAD+ declina ~10% por década después de los 40",
            "clinical_relevance": "Elevar NAD+ con precursores tiene sentido mecanístico pero el beneficio clínico en humanos aún no está demostrado.",
        },
        "SIRT1": {
            "requires": ["NAD+ as cofactor"],
            "activators": ["resveratrol (indirecto)", "ejercicio", "ayuno",
                          "calorie restriction"],
            "effects": ["deacetylates p53 (anti-aging)", "activates PGC-1alpha (mitochondrial biogenesis)",
                       "improves insulin sensitivity", "reduces inflammation"],
            "clinical_relevance": "SIRT1 es el mediator principal de los beneficios del ayuno y ejercicio.",
        },
        "IGF-1": {
            "high_levels": ["anabolism", "muscle growth", "cell proliferation"],
            "low_levels": ["longevity association (IGF-1 bajo = más longevity en algunos modelos)"],
            "note": "En humanos la relación IGF-1/longevity es compleja. IGF-1 bajo tiene beneficios para longevity pero también riesgo de sarcopenia.",
        },
        "Cortisol": {
            "chronic_elevated": ["muscle breakdown", "immune suppression", "insulin resistance",
                                "neurogenesis inhibition", "visceral fat accumulation"],
            "normal_pattern": "Cortisol alto al despertar (CAR), declive durante el día",
            "clinical_relevance": "Cortisol crónicamente elevado (por estrés o sueño deficiente) acelera envejecimiento y sarcopenia.",
        },
    }

    @classmethod
    def validate_mechanistic_claim(
        cls,
        claim: str,
        biomarkers: Dict
    ) -> Tuple[bool, str, List[str]]:
        """
        Valida si un claim mechanístico es biológicamente plausible.

        Returns: (is_plausible, explanation, warnings)
        """
        warnings = []
        claim_lower = claim.lower()

        # Claim: "bloquear mTOR completamente"
        if any(word in claim_lower for word in ["bloquear mtor completamente", "bloquear mtor al 100%", "mtor inhibition total"]):
            return (
                False,
                "ERROR: mTOR NO puede bloquearse completamente. mTOR es esencial para síntesis proteica en músculo, función inmune (células T), y supervivencia celular. Bloqueo total = apoptosis. Use 'inhibición parcial' en su lugar.",
                ["Bloqueo total de mTOR es biológicamente imposible", "Considere ayuno 16-24h para inhibición fisiológica parcial"]
            )

        # Claim: "aumentar NAD+ instantáneamente"
        if any(word in claim_lower for word in ["nad+ instantáneo", "subir nad+ inmediato"]):
            return (
                False,
                "ERROR: NAD+ no puede elevarse instantáneamente. Los precursores (NMN, NR) tardan días-semanas en elevar NAD+ sistémico. Los niveles intramusculares de NAD+ tardan más.",
                ["NAD+ elevation takes 1-4 weeks with supplementation", "Ejercicio aeróbico es el método más rápido y barato de aumentar NAD+ endógeno"]
            )

        # Claim: "eliminar toda inflamación"
        if any(word in claim_lower for word in ["eliminar toda inflamación", "eliminar inflammation completamente"]):
            return (
                False,
                "ERROR: La inflamación AGUDA es necesaria y protectora (respuesta inmune). Lo que queremos es REDUCIR la inflamación CRÓNICA DE BAJO GRADO, no eliminarla. Sin inflamación no hay defensa contra infecciones.",
                ["Inflamación aguda es necesaria y protectora", "El objetivo es reducir inflammation crónica a niveles bajos, no eliminarla"]
            )

        # Claim: "cetonas instantáneas"
        if any(word in claim_lower for word in ["cetonas inmediatas", "entrar en ketosis en 1 día"]):
            return (
                False,
                "ERROR: Entrar en ketosis nutricional (betahydroxybutyrate >0.5mmol/L) requiere typically 2-4 días de ayuno o <20g net carbs/día. En personas con resistencia a insulina puede tardar 1-2 semanas.",
                ["Ketosis takes 2-7 days to achieve with carbohydrate restriction", "La metabolic flexibility afecta la velocidad de entrada en ketosis"]
            )

        return True, f"Claim '{claim}' es biológicamente plausible.", []

    @classmethod
    def get_pathway_context(cls, pathway: str) -> Dict:
        return cls.MOLECULAR_PATHWAYS.get(pathway, {})


# ─────────────────────────────────────────────────────────────────────────────
# MODERATOR AGENT — Consensus Engine
# ─────────────────────────────────────────────────────────────────────────────

class ModeratorAgent:
    """
    El Moderator Agent.
    Coordina el consensus entre agentes y genera el output final.
    """

    def __init__(self):
        self._bus = signal_bus
        self._constraints = constraints_db
        self._biofacts = BioFactsDB()
        self._hallmarks = DrHallmarks()
        self._mechanism = DrMechanism()

    def moderate(
        self,
        user_question: str,
        agent_outputs: List[Dict],
        tick: int,
        clock_results: Optional[Dict] = None,
    ) -> ModeratorOutput:
        """
        Método principal — genera el output del moderador.

        Args:
            user_question: La pregunta o intervención del usuario
            agent_outputs: Lista de outputs de los agentes biológicos
            tick: Número de tick de simulación
            clock_results: Resultados de biological clocks (opcional)

        Returns:
            ModeratorOutput — el output final formateado para el usuario
        """
        agents_consulted = [o.get("agent_id", "unknown") for o in agent_outputs]
        all_concerns = []
        all_recommendations = []
        all_signals = []
        all_biomarker_changes = {}

        # 1. Recopilar todas las preocupaciones y recomendaciones
        for output in agent_outputs:
            all_concerns.extend(output.get("concerns", []))
            all_recommendations.extend(output.get("recommended_actions", []))
            all_biomarker_changes.update(output.get("biomarkers", {}))
            all_signals.extend(output.get("signals_emitted", []))

        # 2. Validar contra Dr. Mechanism (biología molecular)
        mechanism_validations = []
        for recommendation in all_recommendations[:3]:  # Validar top 3
            is_valid, explanation, warnings = self._mechanism.validate_mechanistic_claim(
                recommendation, all_biomarker_changes
            )
            mechanism_validations.append({
                "recommendation": recommendation,
                "is_valid": is_valid,
                "explanation": explanation,
                "warnings": warnings,
            })

        # 3. Validar intervenciones contra Dr. Hallmarks
        hallmarks_validations = []
        for rec in all_recommendations[:3]:
            is_valid, explanation, grade, caveats = self._hallmarks.validate_intervention(rec, all_biomarker_changes)
            hallmarks_validations.append({
                "intervention": rec,
                "is_valid": is_valid,
                "explanation": explanation,
                "grade": grade,
                "caveats": caveats,
            })

        # 4. Consensus — determinar la recomendación principal
        valid_recommendations = [
            v["intervention"] for v in hallmarks_validations
            if v["is_valid"] and v["grade"] in [
                RecommendationGrade.STRONG_FOR, RecommendationGrade.WEAK_FOR
            ]
        ]

        # 5. Consensus grade basado en evidencia
        evidence_levels = [
            v["grade"] for v in hallmarks_validations
            if v["is_valid"]
        ]
        best_evidence = min(evidence_levels, default=EvidenceLevel.C)

        # 6. Calcular confianza
        confidences = [o.get("confidence", 0.7) for o in agent_outputs]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        mechanism_penalty = sum(1 for v in mechanism_validations if not v["is_valid"]) * 0.1
        final_confidence = max(0.1, avg_confidence - mechanism_penalty)

        # 7. Generate consensus recommendation text
        if valid_recommendations:
            primary_rec = valid_recommendations[0]
            supporting = [v["explanation"] for v in hallmarks_validations if v["is_valid"]][:2]
            caveats = [c for v in hallmarks_validations for c in v.get("caveats", [])]
            consensus_text = self._generate_consensus_text(primary_rec, supporting, all_concerns)
        else:
            primary_rec = "Consulta médica requerida"
            consensus_text = (
                "Los datos requieren evaluación médica profesional. "
                "El equipo de agentes recomienda consultar con un especialista antes de actuar."
            )
            caveats = ["Esta herramienta no sustituye el diagnóstico médico profesional"]

        # 8. Critical signals
        critical_signals = self._bus.get_critical_signals()
        critical_signals_dicts = [s.to_dict() for s in critical_signals]

        # 9. Build ConsensusResult
        consensus = ConsensusResult(
            recommendation=consensus_text,
            supporting_agents=agents_consulted,
            evidence_level=best_evidence,
            recommendation_grade=RecommendationGrade.STRONG_FOR if valid_recommendations else RecommendationGrade.NEUTRAL,
            confidence=final_confidence,
            caveats=caveats[:3],
            risks=[c for c in all_concerns if any(risk in c.lower() for risk in ["riesgo", "peligro", "grave", "crítico"])],
            alternative=self._get_alternativeRecommendation(valid_recommendations),
            biomarker_changes=all_biomarker_changes,
            timeframe_months=3,
        )

        return ModeratorOutput(
            tick=tick,
            timestamp=datetime.utcnow(),
            user_question=user_question,
            agents_consulted=agents_consulted,
            consensus=consensus,
            raw_agent_outputs=agent_outputs,
            clock_results=clock_results or {},
            critical_signals=critical_signals_dicts,
            confidence=final_confidence,
        )

    def _generate_consensus_text(
        self,
        primary: str,
        supporting_explanations: List[str],
        concerns: List[str],
    ) -> str:
        """Genera texto de consenso legible."""
        explanation = supporting_explanations[0] if supporting_explanations else ""

        if concerns:
            top_concern = concerns[0]
            text = (
                f"El equipo recomienda: {primary}. "
                f"{explanation} "
                f"Principal preocupación identificada: {top_concern}."
            )
        else:
            text = f"El equipo recomienda: {primary}. {explanation}"

        return text

    def _get_alternativeRecommendation(self, primary_recs: List[str]) -> Optional[str]:
        """Genera una recomendación alternativa de menor intervención."""
        alternatives = {
            "ejercicio aeróbico 150-300 min/sem": "Caminar 30 min/día tiene beneficios significativos aunque menores",
            "ayuno intermitente 16:8": "Reducir azúcares añadidos y carbohidratos refinados es un primer paso efectivo",
            "dieta mediterránea": "Una dieta rica en verduras y frutas ya aporta beneficios medibles",
            "suplementos de nad+": "El ejercicio aeróbico es el método más barato y efectivo de aumentar NAD+ endógeno",
        }
        if primary_recs:
            return alternatives.get(primary_recs[0].lower(), None)
        return None

    def moderate_intervention(
        self,
        intervention: str,
        user_data: Dict,
        agent_outputs: List[Dict],
    ) -> ModeratorOutput:
        """
        Valida una intervención específica solicitada por el usuario.
        Este es el método más usado — cuando el usuario pregunta:
        "¿Debería hacer ayuno 16:8?"
        """
        # Validar con Dr. Hallmarks
        is_valid, explanation, grade, caveats = \
            self._hallmarks.validate_intervention(intervention, user_data)

        # Validar con Dr. Mechanism
        is_mechanistically_valid, mechanism_explanation, warnings = \
            self._mechanism.validate_mechanistic_claim(intervention, user_data)

        if not is_valid or not is_mechanistically_valid:
            consensus_text = (
                f"⚠️ INTERVENCIÓN NO RECOMENDADA: {intervention}\n\n"
                f"{explanation}\n\n"
                f"Validación mecánica: {mechanism_explanation}\n\n"
                f"Riesgos identificados:\n" +
                "\n".join([f"  - {w}" for w in warnings])
            )
        else:
            consensus_text = (
                f"✅ {intervention} ESTÁ RECOMENDADO.\n\n"
                f"{explanation}\n"
                f"Evidencia: {grade.value}\n"
                f"Nota: {caveats[0] if caveats else 'Sin precauciones especiales.'}"
            )

        agents = [o.get("agent_id", "unknown") for o in agent_outputs]

        consensus = ConsensusResult(
            recommendation=consensus_text,
            supporting_agents=agents,
            evidence_level=EvidenceLevel.A if is_valid else EvidenceLevel.C,
            recommendation_grade=grade,
            confidence=0.8 if (is_valid and is_mechanistically_valid) else 0.4,
            caveats=caveats,
            risks=warnings,
            alternative=self._get_alternativeRecommendation([intervention]) if is_valid else None,
            biomarker_changes={},
            timeframe_months=3,
        )

        return ModeratorOutput(
            tick=0,
            timestamp=datetime.utcnow(),
            user_question=intervention,
            agents_consulted=agents,
            consensus=consensus,
            raw_agent_outputs=agent_outputs,
            clock_results={},
            critical_signals=[],
            confidence=consensus.confidence,
        )


# Singleton
moderator_agent = ModeratorAgent()