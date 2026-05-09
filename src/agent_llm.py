"""Biological Agent LLM Layer — BioFish AI. Writes agent system prompts and AgentLLM class."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re

from .llm_client import llm_client, LLMClient, ChatMessage
from .agent import AgentProfile, agent_registry


SYSTEM_PROMPTS: Dict[str, str] = {
    "cardiovascular": (
        "Eres el Dr. Vessels cardiologo con 25 anos experiencia. "
        "Especialidad: sistema cardiovascular y presion arterial. "
        "ANALISIS: Evalua riesgo aterosclerotico, enfermedad coronaria e hipertension. "
        "BIOMARCADORES que manejas: LDL (normal<100,alto 160-189,mu alto>=190), "
        "HDL (normal>=60,bajo<40), Trigliceridos (normal<150,altos>=200), "
        "PCR (bajo<1,moderado 1-3,alto 3-10,agudo>10). "
        "RESPUESTA FORMATO: Reasoning: [tu analisis clinico]. "
        "Assessment: [evaluacion del sistema cardiovascular]. "
        "Concerns: [preocupaciones priorizadas]. "
        "Recommended_actions: [acciones concretas]. "
        "Signals_to_emit: [senales hacia otros agentes si corresponde]. "
        "CONOCIMIENTO: LDL>130+PCR>3 = riesgo multiplicado por 2.5. "
        "HDL<40 es factor de riesgo independiente."
    ),
    "metabolic": (
        "Eres la Dra. Glucose endocrinologa experta en metabolismo de la glucosa. "
        "Especialidad: resistencia a insulina, diabetes T2, pre-diabetes y sindrome metabolico. "
        "BIOMARCADORES que manejas: Glucosa ayunas (normal 70-99,pre-diab 100-125,diabetes>=126), "
        "HbA1c (normal<5.7,pre-diab 5.7-6.4,diabetes>=6.5), "
        "HOMA-IR (normal<2.5,resistencia 2.5-5,severa>5). "
        "RESPUESTA FORMATO: Reasoning: [analisis clinico]. "
        "Assessment: [evaluacion del metabolismo]. "
        "Concerns: [preocupaciones]. "
        "Recommended_actions: [acciones]. "
        "Signals_to_emit: [INSULIN_RESISTANCE si aplica]. "
        "CONOCIMIENTO: HOMA-IR>2.5 detecta resistencia a insulina. "
        "Inflamacion cronica empeora resistencia a insulina via TNF-alpha."
    ),
    "inflammatory": (
        "Eres el Dr. Fire inmunologo experto en inflamacion cronica y sistema inmune. "
        "Especialidad: inflamacion de bajo grado (inflammaging) y citoquinas pro-inflamatorias. "
        "BIOMARCADORES que manejas: PCR (bajo<1,moderado 1-3,alto 3-10,agudo>10), "
        "Ferritina (normal 30-300,elevada>300), IL-6 (normal<2,elevada>2). "
        "RESPUESTA FORMATO: Reasoning: [razonamiento]. "
        "Assessment: [nivel de inflamacion]. "
        "Concerns: [preocupaciones]. "
        "Recommended_actions: [acciones]. "
        "Signals_to_emit: [PRO_INFLAM si alta,ANTI_INFLAM si baja]. "
        "CONOCIMIENTO: Inflammaging = driver principal de enfermedades relacionadas con edad."
    ),
    "molecular": (
        "Eres el Dr. NAD biofisico molecular experto en vias de longevidad. "
        "Especialidad: AMPK, mTOR, NAD+, Sirtuinas, autofagia y senescencia celular. "
        "BIOMARCADORES que manejas: NAD+ (declina 10 por decada despues de 40), "
        "AMPK actividad (estimado, activo en ayuno y ejercicio), "
        "mTOR actividad (activo post-comida con proteina). "
        "RESPUESTA FORMATO: Reasoning: [razonamiento sobre estado molecular]. "
        "Assessment: [balance AMPK/mTOR/NAD+]. "
        "Concerns: [preocupaciones]. "
        "Recommended_actions: [acciones para optimizar vias moleculares]. "
        "Signals_to_emit: [LONGEVITY_SIGNAL si optimo]. "
        "CONOCIMIENTO: AMPK= sensor energia celular. mTOR= sensor nutrientes. "
        "Bloqueo TOTAL de mTOR incompatible con vida. Inhibicion PARCIAL es beneficial."
    ),
    "sleep_recovery": (
        "Eres el Dr. Rest especialista en sueno y recuperacion. "
        "Especialidad: arquitectura del sueno, HRV como marcador de recovery y deuda de sueno. "
        "BIOMARCADORES que manejas: Horas sueno (<5.5=deuda severa,6.5-7.5=ok,7.5-9=optimo), "
        "HRV SDNN (<20=estres severo,20-40=moderado,40-70=recovery bueno,>70=excellent). "
        "RESPUESTA FORMATO: Reasoning: [razonamiento sobre sueno y recovery]. "
        "Assessment: [calidad de sueno y HRV]. "
        "Concerns: [preocupaciones]. "
        "Recommended_actions: [mejoras de sueno]. "
        "Signals_to_emit: [SLEEP_DEBT si hay deuda]. "
        "CONOCIMIENTO: 1h de deuda de sueno causa resistencia a insulina en 4 dias."
    ),
    "sports_performance": (
        "Eres Coach Performance especialista en fisiologia del ejercicio. "
        "Especialidad: VO2max, sobreentrenamiento y adaptacion al entrenamiento. "
        "BIOMARCADORES que manejas: VO2max (<20=pobre,20-30=below avg,30-40=promedio,40-50=good,>50=elite), "
        "HRV como marcador de recovery. Minutos ejercicio/semana (<75=sedentario,75-150=moderado,150-300=activo,>300=athlete). "
        "RESPUESTA FORMATO: Reasoning: [razonamiento sobre rendimiento]. "
        "Assessment: [estado de fitness y entrenamiento]. "
        "Concerns: [preocupaciones]. "
        "Recommended_actions: [plan de entrenamiento]. "
        "Signals_to_emit: [TRAINING_STRESS,RECOVERY_DEMAND]. "
        "CONOCIMIENTO: HIIT 3x/sem es lo mas eficiente para mejorar VO2max."
    ),
}


DEFAULT_PROMPT = (
    "Eres un agente biologico especializado en sistemas de salud humana. "
    "Tu rol es analizar datos medicos y emitir recomendaciones basadas en evidencia. "
    "ANALIZA: 1.Los biomarcadores del paciente 2.Las senales que recibes de otros agentes 3.Contexto de intervencion. "
    "RESPUESTA FORMATO: Reasoning: [tu analisis clinico]. "
    "Assessment: [evaluacion]. "
    "Concerns: [preocupaciones priorizadas]. "
    "Recommended_actions: [acciones concretas]. "
    "Signals_to_emit: [senales hacia otros agentes si corresponde]."
)


@dataclass
class AgentThinking:
    agent_id: str
    reasoning: str
    assessment: str
    concerns: List[str]
    recommended_actions: List[str]
    signals_to_emit: List[str]
    confidence: float
    model_used: str
    latency_ms: float
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "reasoning": self.reasoning,
            "assessment": self.assessment,
            "concerns": self.concerns,
            "recommended_actions": self.recommended_actions,
            "signals_to_emit": self.signals_to_emit,
            "confidence": self.confidence,
            "model_used": self.model_used,
            "latency_ms": round(self.latency_ms, 1),
            "error": self.error,
        }


def parse_llm_response(text: str) -> Dict[str, Any]:
    result = {
        "reasoning": "", "assessment": "",
        "concerns": [], "recommended_actions": [], "signals_to_emit": [],
    }
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("Reasoning:"):
            result["reasoning"] = line.split("Reasoning:", 1)[1].strip()
        elif line.startswith("Assessment:"):
            result["assessment"] = line.split("Assessment:", 1)[1].strip()
        elif line.startswith("Concerns:") or line.startswith("Concern:"):
            src = line.split(":", 1)[1]
            for item in re.split(r"[,;\n]", src):
                item = item.strip().lstrip("-0123456789. ").strip()
                if item and len(item) > 3:
                    result["concerns"].append(item)
        elif line.startswith("Actions:") or line.startswith("Recommended_actions:"):
            src = line.split(":", 1)[1]
            for item in re.split(r"[,;\n]", src):
                item = item.strip().lstrip("-0123456789. ").strip()
                if item and len(item) > 3:
                    result["recommended_actions"].append(item)
        elif line.startswith("Signals:") or line.startswith("Signals_to_emit:"):
            src = line.split(":", 1)[1]
            for item in re.split(r"[,;\n]", src):
                item = item.strip().strip("[]").strip()
                if item and len(item) > 2:
                    result["signals_to_emit"].append(item)
    if not result["reasoning"] and text.strip():
        result["reasoning"] = text.strip()[:500]
    return result


class AgentLLM:
    def __init__(self, llm: Optional[LLMClient] = None):
        self._llm = llm or llm_client
        self._prompts = SYSTEM_PROMPTS
        self._default_prompt = DEFAULT_PROMPT

    def think(
        self,
        agent_id: str,
        user_biomarkers: Dict[str, float],
        incoming_signals: Optional[List[Dict]] = None,
        intervention: Optional[str] = None,
        tick: int = 0,
        force_model: Optional[str] = None,
    ) -> AgentThinking:
        profile = agent_registry.get_profile(agent_id)
        if not profile:
            return AgentThinking(
                agent_id=agent_id, reasoning="", assessment="", concerns=[],
                recommended_actions=[], signals_to_emit=[],
                confidence=0.0, model_used="", latency_ms=0.0,
                error=f"Agent {agent_id} no encontrado",
            )

        system_prompt = self._prompts.get(agent_id, self._default_prompt)
        user_message = self._build_context(
            profile, user_biomarkers, incoming_signals or [], intervention, tick
        )

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_message),
        ]

        model = force_model or self._llm.get_model_for_task("medical_reasoning")
        response = self._llm.chat(
            messages=messages,
            model=model,
            temperature=0.3,
            max_tokens=1024,
        )

        if not response.success:
            return AgentThinking(
                agent_id=agent_id, reasoning="", assessment="", concerns=[],
                recommended_actions=[], signals_to_emit=[],
                confidence=0.3, model_used=model,
                latency_ms=response.latency_ms,
                error=response.error or "LLM call failed",
            )

        parsed = parse_llm_response(response.content)
        return AgentThinking(
            agent_id=agent_id,
            reasoning=parsed.get("reasoning", ""),
            assessment=parsed.get("assessment", ""),
            concerns=parsed.get("concerns", []),
            recommended_actions=parsed.get("recommended_actions", []),
            signals_to_emit=parsed.get("signals_to_emit", []),
            confidence=0.85,
            model_used=response.model,
            latency_ms=response.latency_ms,
            error=None,
        )

    def _build_context(
        self,
        profile: AgentProfile,
        biomarkers: Dict[str, float],
        signals: List[Dict],
        intervention: Optional[str],
        tick: int,
    ) -> str:
        relevant = {k: v for k, v in biomarkers.items() if k in profile.biomarkers and v is not None}
        biomark_text = "\n".join(f"- {k}: {v}" for k, v in relevant.items()) or "(sin datos relevantes)"
        signals_text = "\n".join(
            f"- [{s.get('priority', 'NORMAL')}] "
            f"{s.get('name', '?')}: {str(s.get('reasoning', ''))[:60]}"
            for s in signals[-5:]
        ) or "(sin senales entrantes)"
        interv_text = f"Intervencion activa: {intervention}" if intervention else "Sin intervencion activa"
        return (
            f"CONTEXTO DEL PACIENTE\n"
            f"Sistema: {profile.name} ({profile.role})\n"
            f"Especialidad: {profile.specialty}\n"
            f"Biomarcadores relevantes:\n{biomark_text}\n"
            f"Senales recibidas de otros agentes:\n{signals_text}\n"
            f"{interv_text}\n"
            f"Tick de simulacion: {tick} (1 tick = 1 mes)\n\n"
            f"Instruccion: Analiza el estado de {profile.specialty} y genera tu "
            f"razonamiento clinico estructurado."
        )


agent_llm = AgentLLM()
