"""
==============================================================================
INTER-AGENT SIGNAL SYSTEM — BioFish AI
==============================================================================

Los 18 agentes se comunican entre ellos mediante SIGNALS.
Una señal es un mensaje estructurado que un agente emite a la red.

Ejemplo:
  Agent Cardiovascular → emite SEÑAL: "VASCULAR_STRESS"
  → Agents que la reciben: Inflammatory, Metabolic, Mitochondrial

Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class SignalPriority(str, Enum):
    """Prioridad de la señal — afecta cómo el moderador la procesa."""
    CRITICAL = "CRITICAL"  # Requiere acción inmediata
    HIGH = "HIGH"          # Importante, actuar en siguiente tick
    NORMAL = "NORMAL"      # Información, procesar normalmente
    LOW = "LOW"            # Background, puede esperar


class SignalCategory(str, Enum):
    """Categoría de la señal."""
    STRESS = "STRESS"
    PROTECTIVE = "PROTECTIVE"
    METABOLIC = "METABOLIC"
    HORMONAL = "HORMONAL"
    INFLAMMATORY = "INFLAMMATORY"
    RECOVERY = "RECOVERY"
    ANABOLIC = "ANABOLIC"
    CATABOLIC = "CATABOLIC"
    ALERT = "ALERT"


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRO DE SEÑALES DEFINIDAS
# ─────────────────────────────────────────────────────────────────────────────

SIGNAL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ── CARDIOVASCULAR ──────────────────────────────────────────────
    "VASCULAR_STRESS": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "El sistema cardiovascular detecta estrés vascular (LDL alto, HTN, inflamación)",
        "emitters": ["cardiovascular"],
        "receivers": ["inflammatory", "metabolic", "hepatic", "molecular"],
        "biomarkers_affected": ["ldl_cholesterol", "systolic_bp", "diastolic_bp", "c_reactive_protein"],
        "recommended_agents_consult": 3,
    },
    "CARDIO_PROTECT": {
        "category": SignalCategory.PROTECTIVE,
        "priority": SignalPriority.NORMAL,
        "description": "El sistema cardiovascular está en modo protector (ejercicio, buena dieta)",
        "emitters": ["cardiovascular", "sports_performance"],
        "receivers": ["inflammatory", "metabolic", "molecular"],
        "biomarkers_affected": ["hdl_cholesterol", "triglycerides", "hr_resting"],
        "recommended_agents_consult": 2,
    },
    "ARTERIAL stiffness": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Rigidez arterial aumentada — predictor de eventos cardiovasculares",
        "emitters": ["cardiovascular"],
        "receivers": ["cognitive", "renal", "inflammatory"],
        "biomarkers_affected": ["systolic_bp", "diastolic_bp"],
        "recommended_agents_consult": 2,
    },

    # ── METABÓLICAS ─────────────────────────────────────────────────
    "INSULIN_RESISTANCE": {
        "category": SignalCategory.METABOLIC,
        "priority": SignalPriority.HIGH,
        "description": "Resistencia a insulina periférica — pre-diabetes o diabetes incipiente",
        "emitters": ["metabolic", "insulin_sensitivity"],
        "receivers": ["cardiovascular", "hepatic", "adipose", "inflammatory", "molecular"],
        "biomarkers_affected": ["homa_ir", "glucose_fasting", "hba1c", "insulin_fasting"],
        "recommended_agents_consult": 4,
    },
    "GLUCOSE_SPIKE": {
        "category": SignalCategory.METABOLIC,
        "priority": SignalPriority.NORMAL,
        "description": "Glucosa post-prandial elevada — indica mala gestión de carbohidratos",
        "emitters": ["metabolic", "nutritional_timing"],
        "receivers": ["cardiovascular", "inflammatory", "adipose"],
        "biomarkers_affected": ["glucose_post_prandial"],
        "recommended_agents_consult": 2,
    },
    "METABOLIC_FLEXIBILITY_LOST": {
        "category": SignalCategory.METABOLIC,
        "priority": SignalPriority.HIGH,
        "description": "El cuerpo ha perdido la capacidad de alternar entre glucosa y grasa como combustible",
        "emitters": ["metabolic_flexibility"],
        "receivers": ["metabolic", "molecular", "adipose", "nutritional_timing"],
        "biomarkers_affected": ["respiratory_quotient", "beta_hydroxybutyrate", "glucose_post_prandial"],
        "recommended_agents_consult": 3,
    },
    "KETONE_PRODUCTION": {
        "category": SignalCategory.METABOLIC,
        "priority": SignalPriority.NORMAL,
        "description": "El cuerpo está produciendo cetonas — en ayuno, dieta keto o ejercicio intenso",
        "emitters": ["metabolic_flexibility", "metabolic"],
        "receivers": ["cardiovascular", "cognitive", "molecular"],
        "biomarkers_affected": ["beta_hydroxybutyrate"],
        "recommended_agents_consult": 2,
    },
    "HYPERGLYCEMIA": {
        "category": SignalCategory.METABOLIC,
        "priority": SignalPriority.CRITICAL,
        "description": "GLUCOSA PELIGROSA: >250mg/dL — riesgo de complications agudas",
        "emitters": ["metabolic"],
        "receivers": ["inflammatory", "cardiovascular", "renal", "molecular"],
        "biomarkers_affected": ["glucose_fasting"],
        "recommended_agents_consult": 3,
    },

    # ── INFLAMATORIAS ─────────────────────────────────────────────
    "PRO_INFLAM": {
        "category": SignalCategory.INFLAMMATORY,
        "priority": SignalPriority.HIGH,
        "description": "Estado pro-inflamatorio crónico — IL-6, PCR, TNF-α elevados",
        "emitters": ["inflammatory", "adipose"],
        "receivers": ["cardiovascular", "cognitive", "hepatic", "molecular", "vascular"],
        "biomarkers_affected": ["c_reactive_protein", "il6", "ferritin", "fibrinogen"],
        "recommended_agents_consult": 4,
    },
    "ANTI_INFLAM": {
        "category": SignalCategory.INFLAMMATORY,
        "priority": SignalPriority.NORMAL,
        "description": "El cuerpo está en modo antiinflamatorio (ejercicio, ayuno, omega-3)",
        "emitters": ["inflammatory", "sports_performance", "metabolic"],
        "receivers": ["cardiovascular", "cognitive", "hepatic", "molecular"],
        "biomarkers_affected": ["c_reactive_protein"],
        "recommended_agents_consult": 2,
    },
    "INFLAMMAGING": {
        "category": SignalCategory.INFLAMMATORY,
        "priority": SignalPriority.HIGH,
        "description": "Inflammaging — inflamación crónica de bajo grado asociada a envejecimiento",
        "emitters": ["inflammatory", "immune", "molecular"],
        "receivers": ["cardiovascular", "cognitive", "muscular", "epigenetic"],
        "biomarkers_affected": ["c_reactive_protein", "il6", "ferritin"],
        "recommended_agents_consult": 4,
    },

    # ── MITOCONDRIALES / MOLECULARES ───────────────────────────────
    "MITOCHONDRIAL_DYSFUNCTION": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Función mitocondrial comprometida — producción de ATP reducida",
        "emitters": ["molecular", "metabolic"],
        "receivers": ["muscular", "cognitive", "cardiovascular"],
        "biomarkers_affected": ["nadi_level", "ampk_activity"],
        "recommended_agents_consult": 2,
    },
    "LONGEVITY_SIGNAL": {
        "category": SignalCategory.PROTECTIVE,
        "priority": SignalPriority.NORMAL,
        "description": "Señales de longevidad activadas — AMPK alta, mTOR baja, autofagia activa",
        "emitters": ["molecular", "epigenetic"],
        "receivers": ["cardiovascular", "cognitive", "muscular", "immune", "inflammatory"],
        "biomarkers_affected": ["ampk_activity", "mtor_activity", "autophagy_marker"],
        "recommended_agents_consult": 3,
    },
    "ANABOLIC_STATE": {
        "category": SignalCategory.ANABOLIC,
        "priority": SignalPriority.NORMAL,
        "description": "El cuerpo está en modo anabólico — síntesis proteica activa, mTOR elevado",
        "emitters": ["muscular", "endocrine", "nutritional_timing"],
        "receivers": ["muscular", "bone", "immune"],
        "biomarkers_affected": ["mtor_activity", "testosterone_male", "igf1"],
        "recommended_agents_consult": 2,
    },
    "CATABOLIC_STATE": {
        "category": SignalCategory.CATABOLIC,
        "priority": SignalPriority.HIGH,
        "description": "El cuerpo está en modo catabólico — degradando tejido (ayuno, enfermedad, overtraining)",
        "emitters": ["molecular", "muscular", "sleep"],
        "receivers": ["muscular", "immune", "endocrine", "adipose"],
        "biomarkers_affected": ["testosterone_male", "cortisol_morning", "igf1"],
        "recommended_agents_consult": 3,
    },
    "AUTOPHAGY_ON": {
        "category": SignalCategory.PROTECTIVE,
        "priority": SignalPriority.NORMAL,
        "description": "Autofagia activa — limpieza celular en curso (ayuno >16h o ejercicio intenso)",
        "emitters": ["molecular"],
        "receivers": ["cardiovascular", "cognitive", "inflammatory", "immune"],
        "biomarkers_affected": ["autophagy_marker"],
        "recommended_agents_consult": 2,
    },

    # ── ADIPOSE / PESO ─────────────────────────────────────────────
    "VISCERAL_FAT_ALERT": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Grasa visceral elevada — riesgo cardiometabólico aumentado",
        "emitters": ["adipose", "metabolic"],
        "receivers": ["cardiovascular", "inflammatory", "metabolic", "hepatic"],
        "biomarkers_affected": ["waist_circumference_male", "waist_circumference_female", "leptin", "adiponectin"],
        "recommended_agents_consult": 3,
    },
    "ADIPOKINE_IMBALANCE": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Leptina alta + adiponectina baja = leptino-resistencia",
        "emitters": ["adipose"],
        "receivers": ["metabolic", "endocrine", "cognitive"],
        "biomarkers_affected": ["leptin", "adiponectin"],
        "recommended_agents_consult": 2,
    },
    "LIPOTOXICITY": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Lipotoxicidad — ácidos grasos libres tóxicos para órganos (hígado, páncreas, vasos)",
        "emitters": ["adipose", "metabolic"],
        "receivers": ["hepatic", "cardiovascular", "renal", "pancreatic"],
        "biomarkers_affected": ["triglycerides", "free_fatty_acids"],
        "recommended_agents_consult": 3,
    },

    # ── HEPÁTICAS ──────────────────────────────────────────────────
    "LIVER_STRESS": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Estrés hepático — ENG o grasa hepática (NAFLD) incipiente",
        "emitters": ["hepatic", "metabolic"],
        "receivers": ["cardiovascular", "metabolic", "inflammatory"],
        "biomarkers_affected": ["alt", "ast", "ggt", "triglycerides"],
        "recommended_agents_consult": 3,
    },
    "NAFLD_ALERT": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.CRITICAL,
        "description": "ENFERMEDAD GRASA HEPÁTICA — NAFLD activo con riesgo de progresión a NASH",
        "emitters": ["hepatic"],
        "receivers": ["cardiovascular", "metabolic", "inflammatory"],
        "biomarkers_affected": ["alt", "ast", "ggt"],
        "recommended_agents_consult": 3,
    },

    # ── RONALES ────────────────────────────────────────────────────
    "KIDNEY_STRESS": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Función renal comprometida — eGFR reducida o ácido úrico alto",
        "emitters": ["renal"],
        "receivers": ["cardiovascular", "endocrine", "inflammatory"],
        "biomarkers_affected": ["egfr", "creatinine_male", "creatinine_female", "uric_acid"],
        "recommended_agents_consult": 2,
    },

    # ── COGNITIVAS ─────────────────────────────────────────────────
    "NEURO_INFLAM": {
        "category": SignalCategory.INFLAMMATORY,
        "priority": SignalPriority.HIGH,
        "description": "Neuroinflamación — el cerebro tiene inflamación elevada (CRP sistémica elevada)",
        "emitters": ["cognitive", "inflammatory"],
        "receivers": ["cognitive", "endocrine", "sleep"],
        "biomarkers_affected": ["c_reactive_protein", "homocysteine"],
        "recommended_agents_consult": 2,
    },
    "COGNITIVE_SUPPORT": {
        "category": SignalCategory.PROTECTIVE,
        "priority": SignalPriority.NORMAL,
        "description": "El cerebro está funcionando bien — flujo sanguíneo cerebral OK, sin neuroinflamación",
        "emitters": ["cognitive", "sleep", "cardiovascular"],
        "receivers": ["cognitive", "endocrine"],
        "biomarkers_affected": ["homocysteine", "vitamin_b12", "tsh"],
        "recommended_agents_consult": 2,
    },

    # ── ENDOCRINAS ────────────────────────────────────────────────
    "HORMONAL_STRESS": {
        "category": SignalCategory.HORMONAL,
        "priority": SignalPriority.HIGH,
        "description": "Eje hormonal desregulado — cortisol alto o testosterona/DHEA baja (adrenal fatigue)",
        "emitters": ["endocrine"],
        "receivers": ["muscular", "cognitive", "immune", "metabolic"],
        "biomarkers_affected": ["cortisol_morning", "dhea_s", "testosterone_male"],
        "recommended_agents_consult": 3,
    },
    "THYROID_ALERT": {
        "category": SignalCategory.HORMONAL,
        "priority": SignalPriority.HIGH,
        "description": "Disfunción tiroidea — TSH alterado (hipo o hipertiroidismo)",
        "emitters": ["endocrine"],
        "receivers": ["cardiovascular", "metabolic", "cognitive", "muscular"],
        "biomarkers_affected": ["tsh", "free_t3", "free_t4"],
        "recommended_agents_consult": 3,
    },
    "CORTISOL_SPIKE": {
        "category": SignalCategory.HORMONAL,
        "priority": SignalPriority.HIGH,
        "description": "Cortisol crónicamente elevado — estrés crónico o dysregulation del eje HPA",
        "emitters": ["endocrine", "sleep"],
        "receivers": ["immune", "muscular", "cognitive", "inflammatory", "metabolic"],
        "biomarkers_affected": ["cortisol_morning", "hr_resting", "hpa_axis"],
        "recommended_agents_consult": 3,
    },

    # ── MUSCULARES ────────────────────────────────────────────────
    "SARCOPENIA_RISK": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Riesgo de sarcopenia — pérdida acelerada de masa muscular",
        "emitters": ["muscular"],
        "receivers": ["metabolic", "bone", "immune", "cardiovascular"],
        "biomarkers_affected": ["creatinine_male", "testosterone_male", "igf1", "protein_intake"],
        "recommended_agents_consult": 3,
    },
    "MUSCLE_PROTECT": {
        "category": SignalCategory.PROTECTIVE,
        "priority": SignalPriority.NORMAL,
        "description": "El músculo está en modo protector anabólico (post-ejercicio de fuerza)",
        "emitters": ["muscular", "sports_performance"],
        "receivers": ["endocrine", "immune", "bone"],
        "biomarkers_affected": ["mtor_activity", "testosterone_male", "igf1"],
        "recommended_agents_consult": 2,
    },
    "OVERTRAINING": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.CRITICAL,
        "description": "SOBRETREENEO — el cuerpo está en déficit de recuperación (cortisol alto, HRV bajo)",
        "emitters": ["sports_performance", "sleep"],
        "receivers": ["immune", "endocrine", "muscular", "cardiovascular"],
        "biomarkers_affected": ["hrv_sdnn", "cortisol_morning", "creatine_kinase"],
        "recommended_agents_consult": 4,
    },

    # ── SUEÑO / RECUPERACIÓN ──────────────────────────────────────
    "SLEEP_DEBT": {
        "category": SignalCategory.RECOVERY,
        "priority": SignalPriority.HIGH,
        "description": "Deuda de sueño acumulada — afecta todos los sistemas (metabolismo, cognition, immunity)",
        "emitters": ["sleep_recovery"],
        "receivers": ["cognitive", "metabolic", "immune", "endocrine", "muscular"],
        "biomarkers_affected": ["sleep_hours", "hrv_sdnn", "cortisol_morning"],
        "recommended_agents_consult": 4,
    },
    "RECOVERY_COMPLETE": {
        "category": SignalCategory.RECOVERY,
        "priority": SignalPriority.NORMAL,
        "description": "El cuerpo ha completado la recuperación — HRV alto, cortisol OK",
        "emitters": ["sleep_recovery"],
        "receivers": ["muscular", "immune", "endocrine", "cardiovascular"],
        "biomarkers_affected": ["hrv_sdnn", "sleep_hours"],
        "recommended_agents_consult": 2,
    },

    # ── OXIDATIVO ─────────────────────────────────────────────────
    "OXIDATIVE_STRESS": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.HIGH,
        "description": "Estrés oxidativo elevado — exceso de ROS sobre antioxidantes",
        "emitters": ["oxidative_stress"],
        "receivers": ["cardiovascular", "cognitive", "molecular", "inflammatory"],
        "biomarkers_affected": ["vitamin_c", "vitamin_e", "glutation", "isoprostanos"],
        "recommended_agents_consult": 3,
    },
    "ANTIOXIDANT_DEFENSE_LOW": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.NORMAL,
        "description": "Defensas antioxidantes insuficientes para neutralizar ROS del exercise/metadata",
        "emitters": ["oxidative_stress"],
        "receivers": ["cardiovascular", "molecular", "inflammatory"],
        "biomarkers_affected": ["vitamin_c", "zinc", "selenium"],
        "recommended_agents_consult": 2,
    },

    # ── NUTRICIONAL ────────────────────────────────────────────────
    "PROTEIN_UNDERRATED": {
        "category": SignalCategory.METABOLIC,
        "priority": SignalPriority.HIGH,
        "description": "Proteína dietética insuficiente — riesgo de sarcopenia y anabolic resistance",
        "emitters": ["nutritional_timing", "muscular"],
        "receivers": ["muscular", "bone", "immune"],
        "biomarkers_affected": ["protein_intake", "creatinine_male"],
        "recommended_agents_consult": 2,
    },
    "CIRCADIAN_MISALIGNMENT": {
        "category": SignalCategory.STRESS,
        "priority": SignalPriority.NORMAL,
        "description": "Desalineación circadiana — comer tarde, dormir tarde, luz azul de noche",
        "emitters": ["nutritional_timing", "sleep_recovery"],
        "receivers": ["metabolic", "endocrine", "cardiovascular", "immune"],
        "biomarkers_affected": ["cortisol_wake_up", "melatonin"],
        "recommended_agents_consult": 3,
    },

    # ── DEPORTE ────────────────────────────────────────────────────
    "VO2MAX_EXCELLENT": {
        "category": SignalCategory.PROTECTIVE,
        "priority": SignalPriority.NORMAL,
        "description": "VO2max óptimo — el mejor predictor de longevidad relacionado con fitness",
        "emitters": ["sports_performance"],
        "receivers": ["cardiovascular", "cognitive", "immune"],
        "biomarkers_affected": ["vo2max"],
        "recommended_agents_consult": 2,
    },
    "INJURY_RISK": {
        "category": SignalCategory.ALERT,
        "priority": SignalPriority.HIGH,
        "description": "Riesgo de lesión elevado — fatiga acumulada, sobreentrenamiento",
        "emitters": ["sports_performance", "muscular"],
        "receivers": ["sports_performance", "immune", "muscular"],
        "biomarkers_affected": ["hrv_sdnn", "creatine_kinase"],
        "recommended_agents_consult": 2,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL CLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Signal:
    """Una señal emitida por un agente biológico."""
    id: str
    name: str
    emitter: str
    timestamp: datetime
    priority: SignalPriority
    category: SignalCategory
    data: Dict[str, Any]
    reasoning: str  # El razonamiento clínico que justificó la emisión
    confidence: float  # 0.0-1.0 — confianza en la precisión de la señal
    validated_by_hard_constraints: bool = False
    rejected_by_moderator: bool = False
    rejection_reason: Optional[str] = None

    @classmethod
    def create(
        cls,
        name: str,
        emitter: str,
        data: Dict[str, Any],
        reasoning: str,
        confidence: float = 0.8,
    ) -> "Signal":
        """Factory method para crear una señal con defaults."""
        registry = SIGNAL_REGISTRY.get(name)
        if registry:
            return cls(
                id=str(uuid.uuid4())[:12],
                name=name,
                emitter=emitter,
                timestamp=datetime.utcnow(),
                priority=registry["priority"],
                category=registry["category"],
                data=data,
                reasoning=reasoning,
                confidence=confidence,
                validated_by_hard_constraints=True,
            )
        else:
            # Señal no registrada — usar defaults
            return cls(
                id=str(uuid.uuid4())[:12],
                name=name,
                emitter=emitter,
                timestamp=datetime.utcnow(),
                priority=SignalPriority.NORMAL,
                category=SignalCategory.METABOLIC,
                data=data,
                reasoning=reasoning,
                confidence=confidence,
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "emitter": self.emitter,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "category": self.category.value,
            "data": self.data,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "validated": self.validated_by_hard_constraints,
            "rejected": self.rejected_by_moderator,
            "rejection_reason": self.rejection_reason,
        }


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL BUS — Sistema de comunicación inter-agente
# ─────────────────────────────────────────────────────────────────────────────

class SignalBus:
    """
    El bus de señales — permite a los agentes emitirse señales entre ellos.
    Inspirado en el event bus pattern de sistemas distribuidos.
    """

    def __init__(self):
        self._signals: List[Signal] = []
        self._subscriptions: Dict[str, Set[str]] = {}  # agent → set of signal_names it receives

    def subscribe(self, agent_name: str, signal_names: List[str]) -> None:
        """Un agente se suscribe a recibir ciertas señales."""
        if agent_name not in self._subscriptions:
            self._subscriptions[agent_name] = set()
        for sig in signal_names:
            self._subscriptions[agent_name].add(sig)

    def emit(self, signal: Signal) -> None:
        """Un agente emite una señal al bus."""
        self._signals.append(signal)

    def get_signals_for_agent(self, agent_name: str) -> List[Signal]:
        """Devuelve todas las señales dirigidas a un agente específico."""
        if agent_name not in self._subscriptions:
            return []
        subscribed = self._subscriptions[agent_name]
        return [s for s in self._signals if s.name in subscribed]

    def get_signals_by_category(self, category: SignalCategory) -> List[Signal]:
        return [s for s in self._signals if s.category == category]

    def get_signals_by_priority(self, priority: SignalPriority) -> List[Signal]:
        return [s for s in self._signals if s.priority == priority]

    def get_critical_signals(self) -> List[Signal]:
        """Devuelve todas las señales CRITICAL — las que requieren acción inmediata."""
        return [s for s in self._signals if s.priority == SignalPriority.CRITICAL]

    def get_high_priority_signals(self) -> List[Signal]:
        return [s for s in self._signals if s.priority == SignalPriority.HIGH]

    def clear_resolved_signals(self, resolved_ids: List[str]) -> None:
        """Elimina señales ya procesadas por el moderador."""
        self._signals = [s for s in self._signals if s.id not in resolved_ids]

    def get_signal_history(self, limit: int = 50) -> List[Signal]:
        return self._signals[-limit:]

    def reset(self) -> None:
        """Limpia todas las señales — se llama entre ticks de simulación."""
        self._signals = []

    def summary(self) -> Dict[str, int]:
        """Resumen de señales en el bus."""
        return {
            "total": len(self._signals),
            "critical": len(self.get_critical_signals()),
            "high": len(self.get_high_priority_signals()),
            "by_category": {c.value: len(self.get_signals_by_category(c)) for c in SignalCategory},
        }


# Singleton
signal_bus = SignalBus()