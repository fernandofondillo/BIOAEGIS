"""
==============================================================================
SIMULATION ORCHESTRATOR — BioFish AI BIOSIS Engine
==============================================================================
Orquestador principal de la simulacion multi-agente.
Inspirado en SimulationOrchestrator de MiroFish.
Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from .agent import AgentRegistry, AgentProfile, agent_registry
from .signals import SignalBus, Signal, signal_bus
from .moderator import moderator_agent, ModeratorOutput
from .biological_clocks import EnsembleClock, ClockResult
from .interventions import intervention_engine


@dataclass
class SimulationState:
    tick: int
    timestamp: datetime
    user_data: Dict[str, Any]
    agent_outputs: List[Dict] = field(default_factory=list)
    signals_emitted: List[Dict] = field(default_factory=list)
    moderator_output: Optional[Dict] = None
    clocks: Dict[str, Any] = field(default_factory=dict)
    ensemble_summary: Dict[str, Any] = field(default_factory=dict)
    intervention_applied: Optional[str] = None
    intervention_effects: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "tick": self.tick,
            "timestamp": self.timestamp.isoformat(),
            "user_data": self.user_data,
            "agent_outputs": self.agent_outputs,
            "signals_emitted": self.signals_emitted,
            "moderator_output": self.moderator_output,
            "clocks": self.clocks,
            "ensemble_summary": self.ensemble_summary,
            "intervention_applied": self.intervention_applied,
            "intervention_effects": self.intervention_effects,
        }


class SimulationOrchestrator:
    """
    Orchestrator principal de BioFish AI.
    Coordina los 18 agentes biologicos y el Moderator.
    """

    def __init__(self):
        self._registry = agent_registry
        self._signal_bus = signal_bus
        self._moderator = moderator_agent
        self._intervention_engine = intervention_engine
        self._state_history: List[SimulationState] = []
        self._current_tick = 0
        self._user_biomarkers: Dict[str, float] = {}

    def initialize_user(self, biomarkers: Dict[str, float]) -> Dict:
        """Inicializa un usuario nuevo."""
        self._user_biomarkers = biomarkers
        self._state_history = []
        self._signal_bus.reset()
        self._current_tick = 0
        clocks = self._calculate_clocks(biomarkers)
        return {
            "status": "initialized",
            "user_biomarkers_count": len(biomarkers),
            "available_agents": [p.id for p in self._registry.get_all_profiles()],
            "initial_clocks": {k: v.to_dict() for k, v in clocks.items()},
            "ensemble_summary": EnsembleClock.ensemble_summary(clocks, biomarkers.get("chronological_age", 40)),
        }

    def load_user(self, biomarkers: Dict) -> Dict:
        """Carga un usuario existente."""
        self._user_biomarkers = biomarkers
        self._signal_bus.reset()
        self._current_tick = 0
        clocks = self._calculate_clocks(biomarkers)
        return {
            "status": "loaded",
            "user_biomarkers_count": len(biomarkers),
            "clocks": {k: v.to_dict() for k, v in clocks.items()},
        }

    def run_tick(
        self,
        tick: int,
        question: Optional[str] = None,
        intervention: Optional[str] = None,
    ) -> SimulationState:
        """Ejecuta un tick de simulacion (1 tick = 1 mes simulado)."""
        self._current_tick = tick
        timestamp = datetime.utcnow()

        # Aplicar intervencion si hay
        effects = {}
        if intervention:
            effects = self._intervention_engine.apply(intervention, self._user_biomarkers)
            self._user_biomarkers.update(effects)

        # Reset signal bus para este tick
        self._signal_bus.reset()

        # Ejecutar agentes
        agent_outputs = self._run_agents(self._user_biomarkers, tick)

        # Recopilar senales emitidas
        signals = [s.to_dict() for s in self._signal_bus.get_signal_history(20)]

        # Invocar el Moderator
        if question:
            moderator_output = self._moderator.moderate(
                user_question=question,
                agent_outputs=agent_outputs,
                tick=tick,
                clock_results={},
            )
        elif intervention:
            moderator_output = self._moderator.moderate_intervention(
                intervention=intervention,
                user_data=self._user_biomarkers,
                agent_outputs=agent_outputs,
            )
        else:
            moderator_output = self._moderator.moderate(
                user_question="Estado actual de mi salud",
                agent_outputs=agent_outputs,
                tick=tick,
            )

        # Calcular clocks
        clocks = self._calculate_clocks(self._user_biomarkers)
        clock_dicts = {k: v.to_dict() for k, v in clocks.items()}
        ensemble = EnsembleClock.ensemble_summary(clocks, self._user_biomarkers.get("chronological_age", 40))

        state = SimulationState(
            tick=tick,
            timestamp=timestamp,
            user_data=self._user_biomarkers.copy(),
            agent_outputs=agent_outputs,
            signals_emitted=signals,
            moderator_output=moderator_output.to_dict(),
            clocks=clock_dicts,
            ensemble_summary=ensemble,
            intervention_applied=intervention,
            intervention_effects=effects,
        )
        self._state_history.append(state)
        return state

    def _run_agents(self, biomarkers: Dict, tick: int) -> List[Dict]:
        outputs = []
        profiles = self._registry.get_all_profiles()
        for profile in profiles:
            self._signal_bus.subscribe(profile.id, profile.signal_receives)

        for profile in profiles:
            required = set(profile.biomarkers)
            available = set(k for k, v in biomarkers.items() if v is not None)
            missing_ratio = len(required - available) / max(len(required), 1)
            if missing_ratio > 0.6:
                continue

            agent_data = {
                **biomarkers,
                "tick": tick,
                "active_intervention": (
                    self._state_history[-1].intervention_applied
                    if self._state_history else None
                ),
                "sim_time_months": tick,
            }
            output = self._simulate_agent(profile, agent_data)
            outputs.append(output)

        return outputs

    def _simulate_agent(self, profile: AgentProfile, data: Dict) -> Dict:
        biomarkers = {k: data.get(k) for k in profile.biomarkers if data.get(k) is not None}
        concerns, recommended_actions = [], []
        signals_emitted = []
        assessment = ""
        aid = profile.id

        if aid == "cardiovascular":
            assessment, concerns, recommended_actions = self._assess_cardiovascular(biomarkers, data)
        elif aid == "metabolic":
            assessment, concerns, recommended_actions = self._assess_metabolic(biomarkers, data)
        elif aid == "inflammatory":
            assessment, concerns, recommended_actions = self._assess_inflammatory(biomarkers, data)
        elif aid == "molecular":
            assessment, concerns, recommended_actions = self._assess_molecular(biomarkers, data)
        elif aid == "sleep_recovery":
            assessment, concerns, recommended_actions = self._assess_sleep(biomarkers, data)
        elif aid == "sports_performance":
            assessment, concerns, recommended_actions = self._assess_sports(biomarkers, data)
        elif aid == "hepatic":
            assessment, concerns, recommended_actions = self._assess_hepatic(biomarkers, data)
        elif aid == "renal":
            assessment, concerns, recommended_actions = self._assess_renal(biomarkers, data)
        elif aid == "cognitive":
            assessment, concerns, recommended_actions = self._assess_cognitive(biomarkers, data)
        elif aid == "endocrine":
            assessment, concerns, recommended_actions = self._assess_endocrine(biomarkers, data)
        elif aid == "muscular":
            assessment, concerns, recommended_actions = self._assess_muscular(biomarkers, data)
        elif aid == "immune":
            assessment, concerns, recommended_actions = self._assess_immune(biomarkers, data)
        elif aid == "adipose":
            assessment, concerns, recommended_actions = self._assess_adipose(biomarkers, data)
        elif aid == "metabolic_flexibility":
            assessment, concerns, recommended_actions = self._assess_metaflex(biomarkers, data)
        elif aid == "insulin_sensitivity":
            assessment, concerns, recommended_actions = self._assess_insulin(biomarkers, data)
        elif aid == "nutritional_timing":
            assessment, concerns, recommended_actions = self._assess_nutrition(biomarkers, data)
        elif aid == "oxidative_stress":
            assessment, concerns, recommended_actions = self._assess_oxidative(biomarkers, data)
        elif aid == "epigenetic":
            assessment, concerns, recommended_actions = self._assess_epigenetic(biomarkers, data)
        else:
            assessment = f"Estado general del sistema {profile.specialty}."

        for concern in concerns[:2]:
            sig = self._emit_relevant_signal(aid, concern, biomarkers)
            if sig:
                signals_emitted.append(sig)

        return {
            "agent_id": aid,
            "tick": data.get("tick", 0),
            "biomarkers": biomarkers,
            "signals_emitted": signals_emitted,
            "reasoning": f"[{profile.name}] {assessment}",
            "assessment": assessment,
            "confidence": 0.85,
            "concerns": concerns,
            "recommended_actions": recommended_actions,
            "consulted_agents": [],
        }

    def _assess_cardiovascular(self, b: Dict, d: Dict):
        concerns, actions = [], []
        ldl = b.get("ldl_cholesterol", 0); hdl = b.get("hdl_cholesterol", 0)
        tg = b.get("triglycerides", 0); crp = b.get("c_reactive_protein", 0)
        sbp = b.get("systolic_bp", 0)
        if ldl > 160:
            concerns.append(f"LDL alto ({ldl:.0f} mg/dL) — riesgo aterosclerotico elevado")
            actions.append("Reducir LDL por debajo de 100 mg/dL con dieta mediterranea y/o estatinas")
        if hdl < 40:
            concerns.append(f"HDL bajo ({hdl:.0f} mg/dL) — HDL cardioprotector deficiente")
            actions.append("Ejercicio aerobico regular (150min/sem) eleva HDL 5-10%")
        if tg > 200:
            concerns.append(f"Trigliceridos elevados ({tg:.0f} mg/dL) — riesgo pancreatitis y cardiovascular")
            actions.append("Reducir carbohidratos refinados, aumentar omega-3, ayuno intermittent")
        if crp > 3.0:
            concerns.append(f"PCR elevada ({crp:.1f} mg/L) — inflamacion que acelera arteriosclerosis")
            actions.append("Reducir inflamacion con ejercicio, omega-3, y manejo grasa visceral")
        if sbp > 140:
            concerns.append(f"Hipertension ({sbp:.0f} mmHg) — riesgo ictus e infarto")
            actions.append("Reducir sal, aumentar potasio, ejercicio, manejar estres")
        if not concerns:
            return "Perfil lipidico y cardiovascular dentro de rangos de bajo riesgo.", [], []
        return "", concerns, actions

    def _assess_metabolic(self, b: Dict, d: Dict):
        concerns, actions = [], []
        glucose = b.get("glucose_fasting", 0); hba1c = b.get("hba1c", 0); homa = b.get("homa_ir", 0)
        if glucose > 125:
            concerns.append(f"Glucosa en ayunas elevada ({glucose:.0f} mg/dL) — rango diabetico")
            actions.append("Consulta endocrinologia urgente. Posible diabetes T2.")
        elif glucose > 100:
            concerns.append(f"Glucosa en ayunas en rango pre-diabetico ({glucose:.0f} mg/dL)")
            actions.append("Ayuno intermittent + reducir carbohidratos + ejercicio")
        if hba1c > 6.5:
            concerns.append(f"HbA1c elevada ({hba1c:.1f}%) — diabetes mal controlada")
        elif hba1c > 5.7:
            concerns.append(f"HbA1c en rango pre-diabetes ({hba1c:.1f}%)")
        if homa > 2.5:
            concerns.append(f"HOMA-IR elevado ({homa:.1f}) — resistencia a insulina")
            actions.append("Ayuno intermittent, ejercicio post-carbohidratos, reducir fructose")
        if not concerns:
            return "Metabolismo de la glucosa dentro de rangos normales.", [], []
        return "", concerns, actions

    def _assess_inflammatory(self, b: Dict, d: Dict):
        crp = b.get("c_reactive_protein", 0); ferritin = b.get("ferritin", 0)
        if crp > 10.0:
            return "", [f"PCR muy elevada ({crp:.1f} mg/L) — posible infection o inflamacion aguda"], []
        elif crp > 3.0:
            return ("", [f"PCR elevada ({crp:.1f} mg/L) — inflamacion cronica de bajo grado (inflammaging)"],
                ["Ejercicio cronico + omega-3 + manejo grasa visceral + stress management"])
        if ferritin > 300:
            return "", [f"Ferritina elevada ({ferritin:.0f}) — posible overload hierro o inflamacion"], []
        return "Inflamacion basal dentro de rangos normales — no hay signs de inflammaging activo.", [], []

    def _assess_molecular(self, b: Dict, d: Dict):
        nadi = b.get("nadi_level", 0); vo2 = b.get("vo2max", 0)
        if nadi < 50:
            return "", [f"NAD+ estimado bajo ({nadi:.0f}% max para edad) — funcion mitocondrial comprometida"], ["Ejercicio aerobico (300min/sem) para aumentar NAD+ endogeno 15-30%"]
        if vo2 < 30:
            return "", [f"VO2max bajo ({vo2:.0f}) — capacidad aerobica deficiente"], ["Entrenamiento HIIT: 3x/sem, 20min, ciclos 30s sprint / 90s recovery"]
        if vo2 > 50 and nadi > 70:
            return "Funcion molecular optima — VO2max y NAD+ indican biologia joven y activa.", [], []
        if not nadi and not vo2:
            return "Sin datos moleculares disponibles.", [], []
        return "", [f"NAD+ y VO2max en rango moderado — ejercicio regular mantiene funcion molecular"], []

    def _assess_sleep(self, b: Dict, d: Dict):
        sh = b.get("sleep_hours", 0); hrv = b.get("hrv_sdnn", 0)
        if sh < 5.5:
            return "", [f"Sueno insuficiente ({sh:.1f}h) — deuda de sueno causando resistencia insulina y cortisol elevado"], ["Priorizar 7-8h de sueno. Dormir antes de medianoche."]
        elif sh < 6.5:
            return "", [f"Sueno marginal ({sh:.1f}h) — riesgo de metabolic dysfunction y cognitive decline"], ["Ampliar ventana de sueno a 7-8h."]
        if hrv < 25:
            return "", [f"HRV muy baja ({hrv:.0f}ms) — estres cronico severo o overtraining"], ["Reducir carga entrenamiento 50%. Aumentar descanso."]
        return f"Sueno adecuado ({sh:.1f}h) y HRV en rango de recovery.", [], []

    def _assess_sports(self, b: Dict, d: Dict):
        vo2 = b.get("vo2max", 0); em = d.get("exercise_minutes_per_week", 0)
        if vo2 < 25:
            return "", [f"VO2max muy bajo ({vo2:.0f}) — limita capacidad funcional y longevity"], ["Empezar con caminatas 30min/dia. Progresar a HIIT gradual."]
        elif vo2 < 35:
            return "", [f"VO2max mejorable ({vo2:.0f}) — hay margen significativo de mejora"], ["HIIT 3x/sem: 4-6 intervalos de 30s al 90% VO2max."]
        elif vo2 >= 45:
            return f"VO2max excelente ({vo2:.0f}) — uno de los mejores predictores de longevity.", [], []
        return "", [], []

    def _assess_oxidative(self, b: Dict, d: Dict):
        vitd = b.get("vitamin_d", 0); vitb12 = b.get("vitamin_b12", 0)
        if vitd < 20:
            return "", [f"Vitamina D deficiente ({vitd:.0f} ng/mL) — implica immunosenescencia y inflamacion"], ["Suplementacion 2000-4000 IU/dia de vitamina D3 hasta alcanzar 30+ ng/mL"]
        if vitb12 < 200:
            return "", [f"Vitamina B12 baja ({vitb12:.0f} pg/mL) — riesgo de anemia y neuropatia"], ["B12 oral 1000mcg/dia. Verificar causas."]
        return "Estado nutricional de micronutrientes antioxidante adecuado.", [], []

    def _assess_hepatic(self, b: Dict, d: Dict):
        alt = b.get("alt", 0); ast = b.get("ast", 0); ggt = b.get("ggt", 0)
        if alt > 50 or ast > 50:
            return "", [f"Enzimas hepaticas elevadas (ALT {alt:.0f}], [AST {ast:.0f}) — posible grasa hepatica (NAFLD)", "Reducir fructosa y alcohol. Aumentar ejercicio."]
        if ggt > 60:
            return "", [f"GGT elevada ({ggt:.0f}) — posible esteatosis hepatica o consumo de alcohol"], []
        return "Funcion hepatica dentro de rangos normales.", [], []

    def _assess_renal(self, b: Dict, d: Dict):
        egfr = b.get("egfr", 90); uric = b.get("uric_acid", 0)
        if egfr < 60:
            return "", [f"eGFR reducida ({egfr:.0f}) — posible enfermedad renal cronica"], ["Derivacion nefrologia. Optimizar presion arterial."]
        if uric > 8.0:
            return "", [f"Acido urico elevado ({uric:.1f}) — riesgo de gota y disfuncion endotelial"], ["Reducir purinas (carne roja, alcohol). Aumentar hidratacion."]
        return "Funcion renal dentro de rangos normales.", [], []

    def _assess_cognitive(self, b: Dict, d: Dict):
        h = b.get("homocysteine", 0); b12 = b.get("vitamin_b12", 0)
        if h > 15:
            return "", [f"Homocisteina elevada ({h:.0f}) — factor de riesgo cardiovascular y cognitivo"], ["B12 + Folato + B6. Investigar causa."]
        if b12 < 250 and h > 10:
            return "", [f"B12 baja + homocisteina elevada — riesgo de neuropatia y cognitive decline"], ["Suplementar B12 1000mcg/dia."]
        return "Funcion cognitiva y marcadores neurologicos dentro de rangos normales.", [], []

    def _assess_endocrine(self, b: Dict, d: Dict):
        tsh = b.get("tsh", 0); cortisol = b.get("cortisol_morning", 0)
        if tsh > 4.0:
            return "", [f"TSH elevada ({tsh:.1f}) — hipotiroidismo subclínico"], ["Derivacion endocrinologia. Repetir TSH + T4 libre en 4-6 semanas."]
        if cortisol > 25:
            return "", [f"Cortisol matutino elevado ({cortisol:.0f}) — estres cronico o sindrome de Cushing"], ["Evaluar causa. Manejo de estres, sueno."]
        return "Eje hormonal dentro de rangos normales.", [], []

    def _assess_muscular(self, b: Dict, d: Dict):
        test = b.get("testosterone_male", 0); em = d.get("exercise_minutes_per_week", 0)
        if test < 300 and d.get("chronological_age", 0) > 40:
            return "", [f"Testosterona baja ({test:.0f}) — riesgo de sarcopenia"], ["Ejercicio de fuerza pesado + optimizar sueno + evaluar TRT."]
        if em < 60:
            return "", [f"Ejercicio insuficiente ({em:.0f} min/sem) — riesgo de sarcopenia"], ["Minimo 2 sesiones de fuerza/semana."]
        return "Massa muscular y funcion anabolic dentro de rangos para la edad.", [], []

    def _assess_immune(self, b: Dict, d: Dict):
        w = b.get("leukocytes", 0)
        if w < 4000:
            return "", [f"Leucocitos bajos ({w:.0f}) — immunocompromiso leve"], ["Investigacion de causas. Evaluar status nutricional."]
        if w > 11000:
            return "", [f"Leucocitos elevados ({w:.0f}) — posible infection o inflamacion oculta"], ["Investigacion clinica."]
        return "Sistema inmunitario dentro de rangos normales.", [], []

    def _assess_adipose(self, b: Dict, d: Dict):
        bmi = b.get("bmi", 0); waist = b.get("waist_circumference_male", 0)
        if waist > 102:
            return "", [f"Grasa visceral elevada (cintura {waist:.0f}cm) — riesgo cardiometabolico alto"], ["Prioridad: reduccion grasa visceral con ayuno intermittent + ejercicio aerobico"]
        elif waist > 94:
            return "", [f"Grasa visceral moderada (cintura {waist:.0f}cm) — riesgo cardiometabolico aumentado"], ["Dieta mediterranea + ejercicio 200min/sem."]
        return "Distribucion de grasa corporal dentro de rangos.", [], []

    def _assess_metaflex(self, b: Dict, d: Dict):
        gpp = b.get("glucose_post_prandial", 0); gf = b.get("glucose_fasting", 0)
        if gpp > 0 and gf > 0:
            spike = gpp - gf
            if spike > 60:
                return "", [f"Spike post-prandial excesivo ({spike:.0f} mg/dL) — perdida de metabolic flexibility"], ["Reducir carbohidratos refinados. Protein/fat antes que carbs."]
        return "Flexibilidad metabolica preservada.", [], []

    def _assess_insulin(self, b: Dict, d: Dict):
        homa = b.get("homa_ir", 0); tg = b.get("triglycerides", 0)
        if homa > 2.5:
            return "", [f"HOMA-IR elevado ({homa:.1f}) — resistencia a insulina"], ["Ayuno intermittent + ejercicio post-cibo + reducir fructose + omega-3"]
        if tg > 150:
            return "", [f"Trigliceridos elevados ({tg:.0f}) — associacion con resistencia a insulina"], ["Reducir carbohidratos refinados especialmente fructosa y alcohol."]
        return "Sensibilidad a insulina dentro de rangos.", [], []

    def _assess_nutrition(self, b: Dict, d: Dict):
        sh = b.get("sleep_hours", 0)
        if sh < 6.5:
            return "", [f"Comportamiento nutricional probablemente suboptimal por falta de sueno ({sh:.1f}h)"], ["Priorizar sueno antes de optimizar nutricion."]
        return "Patron nutricional sin alertas especificas.", [], []

    def _assess_epigenetic(self, b: Dict, d: Dict):
        h = b.get("homocysteine", 0)
        if h > 15:
            return "", [f"Homocisteina elevada — impacto en metilacion y epigenetica"], ["B12, folato y B6 para optimizar metilacion."]
        return "Marcadores epigeneticos dentro de rangos.", [], []

    def _emit_relevant_signal(self, agent_id: str, concern: str, biomarkers: Dict) -> Optional[Dict]:
        c = concern.lower()
        signal_map = {
            "ldl": "VASCULAR_STRESS",
            "hdl": "CARDIO_PROTECT",
            "inflamacion": "PRO_INFLAM",
            "crp": "PRO_INFLAM",
            "resistencia": "INSULIN_RESISTANCE",
            "homa": "INSULIN_RESISTANCE",
            "triglicerid": "LIPOTOXICITY",
            "higado": "LIVER_STRESS",
            "renal": "KIDNEY_STRESS",
            "cortisol": "CORTISOL_SPIKE",
            "testosterona": "HORMONAL_STRESS",
            "sueno": "SLEEP_DEBT",
            "vo2": "TRAINING_STRESS",
            "sarcopenia": "SARCOPENIA_RISK",
        }
        for keyword, sig_name in signal_map.items():
            if keyword in c:
                signal = Signal.create(name=sig_name, emitter=agent_id,
                                       data=biomarkers, reasoning=concern, confidence=0.8)
                self._signal_bus.emit(signal)
                return signal.to_dict()
        return None

    def _calculate_clocks(self, biomarkers: Dict) -> Dict[str, ClockResult]:
        return EnsembleClock.calculate(biomarkers)

    def get_history(self, limit: int = 12) -> List[Dict]:
        return [s.to_dict() for s in self._state_history[-limit:]]


orchestrator = SimulationOrchestrator()
