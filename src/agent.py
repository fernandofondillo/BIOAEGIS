"""
==============================================================================
BIOLOGICAL AGENT — Base class for all 18 agents
==============================================================================

Cada agente es una especialización médica distinta.
Todos heredan de BiologicalAgent y reciben:
  - Sus datos biométricos específicos
  - Las señales que otros agentes emiten
  - El contexto del usuario completo
  - Acceso al BioFacts DB para validación
  - Acceso al Hard Constraints DB

Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

from .signals import Signal, SignalBus, signal_bus
from .constraints import constraints_db, HardConstraintsDB
from .biofacts import BioFactsDB


# ─────────────────────────────────────────────────────────────────────────────
# AGENT PROFILE
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentProfile:
    """Perfil de un agente biológico."""
    id: str
    name: str
    role: str
    specialty: str
    system_prompt: str = ""
    biomarkers: List[str] = field(default_factory=list)
    signal_receives: List[str] = field(default_factory=list)
    signal_emits: List[str] = field(default_factory=list)
    avatar_color: str = "#718096"
    icon: str = "⚪"
    expertise_areas: List[str] = field(default_factory=list)
    expertise_areas: List[str]  # Áreas de conocimiento clínico

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "specialty": self.specialty,
            "biomarkers": self.biomarkers,
            "signal_receives": self.signal_receives,
            "signal_emits": self.signal_emits,
            "avatar_color": self.avatar_color,
            "icon": self.icon,
            "expertise_areas": self.expertise_areas,
        }


# ─────────────────────────────────────────────────────────────────────────────
# AGENT OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentOutput:
    """Output estructurado de un agente tras procesar."""
    agent_id: str
    tick: int
    biomarkers: Dict[str, float]  # Biomarcadores evaluados/modificados
    signals_emitted: List[Signal]
    reasoning: str  # Razonamiento clínico del agente
    assessment: str  # Evaluación del estado actual
    confidence: float = 0.85
    concerns: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    consulted_agents: List[str] = field(default_factory=list)
    validated_by_constraints: bool = False
    validation_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "tick": self.tick,
            "biomarkers": {k: round(v, 2) if isinstance(v, float) else v for k, v in self.biomarkers.items()},
            "signals_emitted": [s.to_dict() for s in self.signals_emitted],
            "reasoning": self.reasoning,
            "assessment": self.assessment,
            "confidence": round(self.confidence, 2),
            "concerns": self.concerns,
            "recommended_actions": self.recommended_actions,
            "consulted_agents": self.consulted_agents,
            "validated": self.validated_by_constraints,
            "validation_errors": self.validation_errors,
        }


# ─────────────────────────────────────────────────────────────────────────────
# BASE BIOLOGICAL AGENT
# ─────────────────────────────────────────────────────────────────────────────

class BiologicalAgent(ABC):
    """
    Clase base abstracta para todos los agentes biológicos.

    Cada agente:
    1. Conoce sus biomarcadores del usuario
    2. Recibe señales de otros agentes
    3. Consulta el Hard Constraints DB para no generar outputs imposibles
    4. Consulta el BioFacts DB para basarse en evidencia
    5. Emite señales a la red
    6. Devuelve un AgentOutput estructurado
    """

    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self._bus: SignalBus = signal_bus
        self._constraints: HardConstraintsDB = constraints_db
        self._biofacts = BioFactsDB()
        self._history: List[AgentOutput] = []

    @abstractmethod
    def assess(self, user_data: Dict, tick: int) -> AgentOutput:
        """
        Método principal que cada agente implementa.

        Args:
            user_data: Todos los datos del usuario (biomarcadores, señales,
                      intervención activa, sim_time)
            tick: Número de tick de simulación (1 mes = 1 tick)

        Returns:
            AgentOutput estructurado
        """
        pass

    def _get_signals_for_me(self) -> List[Signal]:
        """Obtiene las señales dirigidas a este agente."""
        return self._bus.get_signals_for_agent(self.profile.id)

    def _emit_signal(
        self,
        name: str,
        data: Dict[str, Any],
        reasoning: str,
        confidence: float = 0.8,
    ) -> Optional[Signal]:
        """Emite una señal al bus."""
        signal = Signal.create(
            name=name,
            emitter=self.profile.id,
            data=data,
            reasoning=reasoning,
            confidence=confidence,
        )
        self._bus.emit(signal)
        return signal

    def _validate_biomarkers(self, biomarkers: Dict[str, float]) -> tuple[bool, List[str]]:
        """Valida que los biomarcadores estén dentro de límites biológicos."""
        return self._constraints.validate_all(biomarkers)

    def _get_facts_for_category(self, category: str) -> List:
        """Obtiene hechos biológicos validados de una categoría."""
        return self._biofacts.get_facts(category)

    def _reasoning_context(self, user_data: Dict) -> str:
        """Construye el contexto de razonamiento para el LLM."""
        signals = self._get_signals_for_me()
        signals_text = "\n".join([
            f"  - [{s.priority.value}] {s.name}: {s.reasoning[:100]}"
            for s in signals[-5:]
        ]) if signals else "  (sin señales entrantes)"

        my_biomarkers = {k: user_data.get(k) for k in self.profile.biomarkers}
        biomarkers_text = "\n".join([
            f"  - {k}: {v}"
            for k, v in my_biomarkers.items()
            if v is not None
        ])

        return f"""
CONTEXTO DEL AGENTE:
- Nombre: {self.profile.name}
- Rol: {self.profile.role}
- Especialidad: {self.profile.specialty}

BIOMARCADORES BAJO SU RESPONSABILIDAD:
{biomarkers_text or '  (no hay datos disponibles)'}

SEÑALES RECIBIDAS DE OTROS AGENTES (últimas 5):
{signals_text}

INTERVENCIÓN ACTIVA: {user_data.get('active_intervention', 'ninguna')}
"""

    def get_history(self) -> List[AgentOutput]:
        return self._history[-10:]  # Últimos 10 outputs

    def get_summary(self) -> Dict:
        return {
            "profile": self.profile.to_dict(),
            "total_assessments": len(self._history),
            "last_assessment": self._history[-1].to_dict() if self._history else None,
            "signals_emitted_total": sum(len(o.signals_emitted) for o in self._history),
        }


# ─────────────────────────────────────────────────────────────────────────────
# ALL 18 AGENT PROFILES
# ─────────────────────────────────────────────────────────────────────────────

def get_all_profiles() -> Dict[str, AgentProfile]:
    """Devuelve los perfiles de los 18 agentes."""

    profiles = {

        # ═══════════════════════════════════════════════════════════════════
        # CORE — 12 SISTEMAS BIOLÓGICOS
        # ═══════════════════════════════════════════════════════════════════

        "cardiovascular": AgentProfile(
            id="cardiovascular",
            name="Dr. Vessels",
            role="Cardiólogo Experto",
            specialty="Sistema cardiovascular, salud vascular y presión arterial",
            biomarkers=["ldl_cholesterol", "hdl_cholesterol", "triglycerides", "total_cholesterol",
                       "systolic_bp", "diastolic_bp", "hr_resting", "c_reactive_protein",
                       "ldl_oxidation_risk"],
            signal_receives=["PRO_INFLAM", "INSULIN_RESISTANCE", "LIPOTOXICITY", "CORTISOL_SPIKE"],
            signal_emits=["VASCULAR_STRESS", "CARDIO_PROTECT", "ARTERIAL_STIFFNESS"],
            avatar_color="#E53E3E",
            icon="❤️",
            expertise_areas=["Arteriosclerosis", "Enfermedad coronaria", "Hipertensión",
                            "Insuficiencia cardíaca", "Arritmias"],
        ),

        "metabolic": AgentProfile(
            id="metabolic",
            name="Dra. Glucose",
            role="Endocrinóloga Experta",
            specialty="Metabolismo de la glucosa y resistencia a insulina",
            biomarkers=["glucose_fasting", "hba1c", "insulin_fasting", "homa_ir",
                       "c_peptide", "perimeter_waist", "bmi"],
            signal_receives=["CARDIO_PROTECT", "LIPOTOXICITY", "PRO_INFLAM", "CORTISOL_SPIKE"],
            signal_emits=["INSULIN_RESISTANCE", "GLUCOSE_SPIKE", "METABOLIC_STRESS", "HYPERGLYCEMIA"],
            avatar_color="#DD6B20",
            icon="🩸",
            expertise_areas=["Diabetes tipo 2", "Pre-diabetes", "Síndrome metabólico",
                            "Resistencia a insulina", "Obesidad"],
        ),

        "inflammatory": AgentProfile(
            id="inflammatory",
            name="Dr. Fire",
            role="Inmunólogo Experto",
            specialty="Inflamación sistémica, citoquinas y respuesta inmune",
            biomarkers=["c_reactive_protein", "ferritin", "il6", "fibrinogen",
                       "leukocytes", "neutrophils_pct", "lymphocytes_pct"],
            signal_receives=["LIPOTOXICITY", "VISCERAL_FAT_ALERT", "OXIDATIVE_STRESS"],
            signal_emits=["PRO_INFLAM", "ANTI_INFLAM", "INFLAMMAGING", "IMMUNE_ALERT"],
            avatar_color="#D69E2E",
            icon="🔥",
            expertise_areas=["Inflammaging", "Enfermedades autoinmunes", "Cytokine storm",
                            "Inflamación crónica de bajo grado", "CRP y ferritina"],
        ),

        "molecular": AgentProfile(
            id="molecular",
            name="Dr. NAD",
            role="Biólogo Molecular Experto",
            specialty="Vías moleculares de longevidad: AMPK, mTOR, NAD+, autofagia",
            biomarkers=["nadi_level", "ampk_activity", "mtor_activity",
                       "autophagy_marker", "sirt1_activity"],
            signal_receives=["VASCULAR_STRESS", "CATABOLIC_STATE", "CARDIO_PROTECT", "PRO_INFLAM"],
            signal_emits=["LONGEVITY_SIGNAL", "ANABOLIC_STATE", "CATABOLIC_STATE",
                         "AUTOPHAGY_ON", "MITOCHONDRIAL_DYSFUNCTION"],
            avatar_color="#805AD5",
            icon="⚛️",
            expertise_areas=["AMPK", "mTOR", "NAD+", "Sirtuinas", "Autofagia",
                            "Senescencia celular", "Vías de longevidad"],
        ),

        "epigenetic": AgentProfile(
            id="epigenetic",
            name="Dra. Methyl",
            role="Epigenetista Experta",
            specialty="Relojes epigenéticos, metilación del DNA, longitud de telómeros",
            biomarkers=["homocysteine", "vitamin_b12", "folate_rbc", "methylation_index",
                       "telomere_length", "epigenetic_age"],
            signal_receives=["INFLAMMAGING", "OXIDATIVE_STRESS", "PRO_INFLAM"],
            signal_emits=["AGING_ACCEL", "DNA_REPAIR", "EPIGENETIC_DRIFT"],
            avatar_color="#9F7AEA",
            icon="🧬",
            expertise_areas=["Reloj epigenético", "Metilación", "Telómeros",
                            "Reparación del DNA", "Envejecimiento epigenético"],
        ),

        "hepatic": AgentProfile(
            id="hepatic",
            name="Dr. Liver",
            role="Hepatólogo Experto",
            specialty="Función hepática, detoxificación y metabolismo lipídico",
            biomarkers=["alt", "ast", "ggt", "albumin", "bilirubin_total",
                       "iron", "transferrin_saturation"],
            signal_receives=["LIPOTOXICITY", "INSULIN_RESISTANCE", "VISCERAL_FAT_ALERT", "PRO_INFLAM"],
            signal_emits=["LIVER_STRESS", "NAFLD_ALERT", "DETOX_CAPACITY", "LIPID_METABOLISM"],
            avatar_color="#38A169",
            icon="🟢",
            expertise_areas=["NAFLD", "Hígado graso", "Enfermedad hepática alcohólica",
                            "Hepatitis", "Detoxificación", "Colesterol"],
        ),

        "renal": AgentProfile(
            id="renal",
            name="Dr. Filter",
            role="Nefrólogo Experto",
            specialty="Función renal, filtración glomerular y equilibrio hidroelectrolítico",
            biomarkers=["creatinine_male", "creatinine_female", "egfr", "urea_bun",
                       "uric_acid", "potassium", "sodium"],
            signal_receives=["HYPERGLYCEMIA", "HYPERTENSION", "PRO_INFLAM", "CARDIO_PROTECT"],
            signal_emits=["KIDNEY_STRESS", "FILTRATION_OK", "ELECTROLYTE_IMBALANCE", "CKD_ALERT"],
            avatar_color="#3182CE",
            icon="💧",
            expertise_areas=["Enfermedad renal crónica (ERC)", "Filtración glomerular",
                            "Hiperuricemia", "Electrolitos", "Nefrocardiovascular"],
        ),

        "cognitive": AgentProfile(
            id="cognitive",
            name="Dra. Brain",
            role="Neuróloga Experta",
            specialty="Función cognitiva, neurología y salud cerebral",
            biomarkers=["tsh", "vitamin_b12", "folate_rbc", "homocysteine",
                       "vitamin_d", "glucose_fasting"],
            signal_receives=["NEURO_INFLAM", "PRO_INFLAM", "INFLAMMAGING", "VASCULAR_STRESS"],
            signal_emits=["COGNITIVE_SUPPORT", "NEURO_INFLAM", "MOOD_REGULATION", "COGNITIVE_DECLINE"],
            avatar_color="#319795",
            icon="🧠",
            expertise_areas=["Deterioro cognitivo", "Demencia", "Depresión", "Función ejecutiva",
                            "Neuroinflamación", "Reserva cognitiva"],
        ),

        "endocrine": AgentProfile(
            id="endocrine",
            name="Dr. Hormone",
            role="Endocrinólogo Experto",
            specialty="Eje hormonal completo: tiroides, suprarrenales, gónadas",
            biomarkers=["tsh", "free_t3", "free_t4", "testosterone_male", "testosterone_female",
                       "cortisol_morning", "dhea_s", "estradiol_male", "lh", "fsh"],
            signal_receives=["SLEEP_DEBT", "CORTISOL_SPIKE", "OVERTRAINING", "PRO_INFLAM"],
            signal_emits=["HORMONAL_STRESS", "THYROID_ALERT", "CORTISOL_SPIKE",
                         "ANABOLIC_SUPPORT", "HPA_DYSREGULATION"],
            avatar_color="#D53F8C",
            icon="⚖️",
            expertise_areas=["Hipotiroidismo", "Hipertiroidismo", "Disfunción adrenal",
                            "Hipogonadismo", "Cortisol", "DHEA-S", "Hormonas anabólicas"],
        ),

        "muscular": AgentProfile(
            id="muscular",
            name="Coach Muscle",
            role="Especialista en Fisiología del Ejercicio",
            specialty="Masa muscular, fuerza, sarcopenia y respuesta anabólica",
            biomarkers=["creatinine_male", "igf1", "testosterone_male", "protein_intake_grams",
                       "skeletal_muscle_mass"],
            signal_receives=["ANABOLIC_STATE", "CATABOLIC_STATE", "SLEEP_DEBT",
                           "OVERTRAINING", "SARCOPENIA_RISK"],
            signal_emits=["MUSCLE_PROTECT", "SARCOPENIA_RISK", "ANABOLIC_WINDOW",
                         "MUSCLE_BREAKDOWN", "PROTEIN_SYNTHESIS"],
            avatar_color="#ED8936",
            icon="💪",
            expertise_areas=["Sarcopenia", "Anabolismo muscular", "Proteólisis",
                            "Ejercicio de fuerza", "Respuesta anabólica", "IGF-1"],
        ),

        "immune": AgentProfile(
            id="immune",
            name="Dr. Shield",
            role="Inmunólogo Experto",
            specialty="Sistema inmunitario, inmunosenescencia y vigilancia oncológica",
            biomarkers=["leukocytes", "lymphocytes_pct", "iga", "igg", "igm",
                       "cd4_count", "vaccine_response"],
            signal_receives=["PRO_INFLAM", "INFLAMMAGING", "CORTISOL_SPIKE",
                           "SLEEP_DEBT", "OVERTRAINING"],
            signal_emits=["IMMUNE_ACTIVATE", "IMMUNE_EXHAUSTION", "TH1_TH2_BALANCE",
                         "IMMUNOSCENESCENCE", "INFECTION_RISK"],
            avatar_color="#00B5D8",
            icon="🛡️",
            expertise_areas=["Inmunosenescencia", "Infecciones recurrentes",
                            "Inmunodeficiencia", "Vacunación", "Oncología"],
        ),

        "adipose": AgentProfile(
            id="adipose",
            name="Dra. Fat",
            role="Especialista en Tejido Adiposo",
            specialty="Tejido adiposo como órgano endocrino, adipocinas y grasa visceral",
            biomarkers=["leptin", "adiponectin", "bmi", "waist_circumference_male",
                       "waist_circumference_female", "body_fat_pct_male", "body_fat_pct_female"],
            signal_receives=["INSULIN_RESISTANCE", "GLUCOSE_SPIKE", "METABOLIC_FLEXIBILITY_LOST"],
            signal_emits=["VISCERAL_FAT_ALERT", "ADIPOKINE_IMBALANCE", "LIPOTOXICITY",
                         "LEPTIN_SIGNAL", "ADIPONECTIN_LOW"],
            avatar_color="#718096",
            icon="⚪",
            expertise_areas=["Obesidad visceral", "Leptino-resistencia", "Lipotoxicidad",
                            "Adipocinas", "Tejido adiposo marrón", "Grasa subcutánea"],
        ),

        # ═══════════════════════════════════════════════════════════════════
        # NUEVOS — 6 AGENTES DE ALTO VALOR
        # ═══════════════════════════════════════════════════════════════════

        "metabolic_flexibility": AgentProfile(
            id="metabolic_flexibility",
            name="Coach Carb",
            role="Especialista en Flexibilidad Metabólica",
            specialty="Capacidad del cuerpo de alternar entre glucosa y ácidos grasos como combustible",
            biomarkers=["respiratory_quotient", "beta_hydroxybutyrate", "glucose_post_prandial",
                       "ketones_blood", "fat_oxidation_rate", "carbohydrate_tolerance"],
            signal_receives=["INSULIN_RESISTANCE", "GLUCOSE_SPIKE", "CARDIO_PROTECT", "PRO_INFLAM"],
            signal_emits=["METABOLIC_FLEXIBILITY_LOST", "KETONE_PRODUCTION",
                         "FUEL_SWITCH_ABILITY", "FAT_BURN_MODE", "CARB_TOLERANCE"],
            avatar_color="#48BB78",
            icon="🔄",
            expertise_areas=["Ketosis", "Oxidación de grasa", "Metabolic flexibility",
                            "Dieta keto", "Ayuno", "Gluconeogénesis"],
        ),

        "insulin_sensitivity": AgentProfile(
            id="insulin_sensitivity",
            name="Dr. Receptor",
            role="Especialista en Sensibilidad a Insulina",
            specialty="Resistencia a insulina periférica en músculo, hígado y tejido adiposo",
            biomarkers=["homa_ir", "adiponectin", "triglycerides", "alanine_aminotransferasa",
                       "glucose_post_prandial", "insulin_fasting"],
            signal_receives=["VISCERAL_FAT_ALERT", "PRO_INFLAM", "LIPOTOXICITY", "SEDENTARISM"],
            signal_emits=["INSULIN_RESIST_MUSCLE", "INSULIN_RESIST_FAT", "GLUCOSE_DISPOSAL",
                         "INSULIN_CASCADE", "SENSITIVITY_IMPROVED"],
            avatar_color="#F6AD55",
            icon="🎯",
            expertise_areas=["Resistencia a insulina", "Diabetes T2", "HOMA-IR",
                            "Disposición de glucosa", "Sensibilidad periférica"],
        ),

        "sports_performance": AgentProfile(
            id="sports_performance",
            name="Coach Performance",
            role="Especialista en Rendimiento Deportivo",
            specialty="VO2max, economía de carrera, sobreentrenamiento y periodización",
            biomarkers=["vo2max", "hr_resting", "hrv_sdnn", "training_load_trimp",
                       "recovery_days_since_intense", "creatine_kinase", "lactate_threshold"],
            signal_receives=["MUSCLE_PROTECT", "SLEEP_DEBT", "CORTISOL_SPIKE",
                           "ANABOLIC_STATE", "CATABOLIC_STATE"],
            signal_emits=["TRAINING_STRESS", "RECOVERY_DEMAND", "VO2MAX_EXCELLENT",
                         "INJURY_RISK", "OVERTRAINING", "FITNESS_IMPROVING"],
            avatar_color="#FC8181",
            icon="🏃",
            expertise_areas=["VO2max", "Overtraining", "Periodización", "Recuperación",
                            "Lesiones por estrés", "TRIMP", "Economía de carrera"],
        ),

        "nutritional_timing": AgentProfile(
            id="nutritional_timing",
            name="Chef Science",
            role="Nutriólogo Deportivo Experto",
            specialty="Timing nutricional, distribución proteica y sincronización con ritmo circadiano",
            biomarkers=["protein_intake_grams", "protein_per_meal", "hours_since_last_meal",
                       "carbs_pre_workout", "carbs_post_workout", "last_meal_time"],
            signal_receives=["ANABOLIC_STATE", "CATABOLIC_STATE", "MUSCLE_PROTECT",
                           "SLEEP_DEBT", "GLUCOSE_SPIKE"],
            signal_emits=["PROTEIN_UNDERRATED", "CIRCADIAN_MISALIGNMENT",
                         "ANABOLIC_TIMING", "WINDOW_OPTIMAL", "MEAL_FREQUENCY"],
            avatar_color="#B794F4",
            icon="🍽️",
            expertise_areas=["Nutrición deportiva", "Timing de macronutrientes",
                            "Ventana anabólica", "Distribución proteica", "Circadiano"],
        ),

        "sleep_recovery": AgentProfile(
            id="sleep_recovery",
            name="Dr. Rest",
            role="Especialista en Sueño y Recuperación",
            specialty="Arquitectura del sueño, HRV como marcador de recuperación y deuda de sueño",
            biomarkers=["sleep_hours", "sleep_efficiency", "hrv_sdnn", "cortisol_wake_up",
                       "awakenings_count", "time_in_bed", "sleep_debt_hours"],
            signal_receives=["OVERTRAINING", "CORTISOL_SPIKE", "PRO_INFLAM",
                           "CARDIO_PROTECT", "ANABOLIC_STATE"],
            signal_emits=["SLEEP_DEBT", "RECOVERY_COMPLETE", "CORTISOL_DAWN",
                         "HRV_TREND", "REM_DEBT", "ANABOLIC_ENVIRONMENT"],
            avatar_color="#4FD1C5",
            icon="🌙",
            expertise_areas=["Sueño", "HRV", "Arquitectura del sueño", "Cortisol matutino",
                            "Deuda de sueño", "Recuperación", "Nicturia"],
        ),

        "oxidative_stress": AgentProfile(
            id="oxidative_stress",
            name="Dr. Rust",
            role="Especialista en Estrés Oxidativo",
            specialty="Balance ROS/antioxidantes, oxidative damage y supplementation",
            biomarkers=["vitamin_c", "vitamin_e", "zinc", "selenium", "glutation",
                       "isoprostanos", "8ohdg", "superoxide_dismutase"],
            signal_receives=["PRO_INFLAM", "VASCULAR_STRESS", "MITOCHONDRIAL_DYSFUNCTION",
                           "CARDIO_PROTECT", "EXERCISE_ACUTE"],
            signal_emits=["OXIDATIVE_STRESS", "ANTIOXIDANT_DEFENSE_LOW",
                         "ROS_OVERFLOW", "MITOCHONDRIAL_STRESS", "ANTIOXIDANT_BOOST"],
            avatar_color="#A0AEC0",
            icon="🧪",
            expertise_areas=["Estrés oxidativo", "ROS", "Antioxidantes", "Suplementación",
                             "Daño oxidativo", "Mitohormesis"],
        ),
    }

    return profiles


# ─────────────────────────────────────────────────────────────────────────────
# AGENT REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

class AgentRegistry:
    """Registro central de todos los agentes biológicos."""

    def __init__(self):
        self._profiles = get_all_profiles()
        self._instances: Dict[str, BiologicalAgent] = {}

    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        return self._profiles.get(agent_id)

    def get_all_profiles(self) -> List[AgentProfile]:
        return list(self._profiles.values())

    def get_agents_by_signal(self, signal_name: str) -> List[str]:
        """Devuelve qué agentes emiten una señal específica."""
        return [
            pid for pid, p in self._profiles.items()
            if signal_name in p.signal_emits
        ]

    def get_profile_summary(self) -> List[Dict]:
        return [p.to_dict() for p in self._profiles.values()]


# Singleton
agent_registry = AgentRegistry()