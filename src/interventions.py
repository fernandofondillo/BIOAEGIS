"""
==============================================================================
INTERVENTIONS ENGINE — BioFish AI
==============================================================================
Motor de simulacion de intervenciones con efectos basados en evidencia.
Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .biofacts import EvidenceLevel


@dataclass
class InterventionEffect:
    biomarker: str
    change_per_month: float
    direction: str
    confidence: float
    evidence_level: EvidenceLevel
    mechanism: str
    time_to_effect_months: int = 3
    ceiling_effect: Optional[float] = None


class InterventionEngine:

    INTERVENTIONS: Dict[str, Dict[str, Any]] = {

        "ayuno_intermitente_16_8": {
            "name": "Ayuno Intermitente 16:8",
            "description": "16 horas ayuno, 8 horas ventana alimentaria",
            "category": "nutrition",
            "duration_days": 84,
            "effects": [
                {"biomarker": "homa_ir", "change_per_month": -0.4, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Mejora sensibilidad insulina via AMPK activation"},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.3, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Reduccion inflammation sistemica"},
                {"biomarker": "ldl_cholesterol", "change_per_month": -8.0, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "B",
                 "mechanism": "Reduccion LDL por perdida grasa y mejora metabolica",
                 "ceiling_effect": 70.0},
                {"biomarker": "triglycerides", "change_per_month": -15.0, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Reduccion TG por mejora sensibilidad insulina",
                 "ceiling_effect": 80.0},
                {"biomarker": "glucose_fasting", "change_per_month": -5.0, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Mejora glucemia en ayunas"},
                {"biomarker": "insulin_fasting", "change_per_month": -1.5, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Reduccion insulina circulante en ayunas"},
                {"biomarker": "ampk_activity", "change_per_month": 20.0, "direction": "increase",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Activacion AMPK por deprivacion energetica"},
                {"biomarker": "mtor_activity", "change_per_month": -15.0, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "B",
                 "mechanism": "Inhibicion parcial mTOR durante ventana ayuno"},
            ],
            "contraindications": [
                "Diabetes tipo 1 insulin-dependiente (riesgo hipoglucemia)",
                "Anorexia u otros trastornos conducta alimentaria",
                "Embarazo o lactancia",
                "IRC severa (eGFR < 30)"
            ],
            "risks": [
                "Hipoglucemia en diabeticos medicados",
                "Irritabilidad inicial transitoria",
                "Posible perdida masa muscular si exceso ayuno"
            ],
        },

        "ejercicio_aerobico_150": {
            "name": "Ejercicio Aerobico 150 min/sem",
            "description": "150 minutos ejercicio moderado o 75 minutos vigoroso por semana",
            "category": "exercise",
            "duration_days": 84,
            "effects": [
                {"biomarker": "vo2max", "change_per_month": 2.5, "direction": "increase",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Aumento VO2max por mejora funcion cardiovascular"},
                {"biomarker": "hdl_cholesterol", "change_per_month": 3.0, "direction": "increase",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Aumento HDL con ejercicio aerobico regular"},
                {"biomarker": "triglycerides", "change_per_month": -15.0, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion TG por oxidacion acidos grasos",
                 "ceiling_effect": 80.0},
                {"biomarker": "homa_ir", "change_per_month": -0.3, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Mejora sensibilidad insulina muscular"},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.4, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Efecto antiinflamatorio ejercicio cronico"},
                {"biomarker": "hr_resting", "change_per_month": -3.0, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion FC en reposo (bradicardia athlete)"},
                {"biomarker": "systolic_bp", "change_per_month": -3.0, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion PA por vasodilatacion periferica cronica",
                 "ceiling_effect": 115.0},
                {"biomarker": "nadi_level", "change_per_month": 10.0, "direction": "increase",
                 "confidence": 0.80, "evidence_level": "B",
                 "mechanism": "Aumento NAD+ muscular por ejercicio cronico"},
                {"biomarker": "hrv_sdnn", "change_per_month": 5.0, "direction": "increase",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Mejora HRV por aumento tono vagal"},
            ],
            "contraindications": [
                "Enfermedad cardiovascular no evaluada (consultar cardiologo)"
            ],
            "risks": [
                "Lesiones por sobreuso si progresion inadecuada",
                "Eventos cardiacos agudos en sedentarios extremos (riesgo bajo)"
            ],
        },

        "hiit_3x": {
            "name": "HIIT 3x/semana",
            "description": "3 sesiones de High Intensity Interval Training por semana",
            "category": "exercise",
            "duration_days": 84,
            "effects": [
                {"biomarker": "vo2max", "change_per_month": 4.0, "direction": "increase",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Mayor aumento VO2max que ejercicio moderado",
                 "time_to_effect_months": 2},
                {"biomarker": "homa_ir", "change_per_month": -0.5, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Mejora sensibilidad insulina post-HIIT"},
                {"biomarker": "triglycerides", "change_per_month": -20.0, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion TG superior a ejercicio moderado",
                 "ceiling_effect": 75.0},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.5, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "B",
                 "mechanism": "Reduccion inflamacion por mioquinas antiinflamatorias"},
                {"biomarker": "glucose_post_prandial", "change_per_month": -10.0, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Mejora disposicion glucosa post-comida"},
            ],
            "contraindications": [
                "Hipertension no controlada",
                "Cardiopatia isquemica sin evaluacion",
            ],
            "risks": [
                "Lesiones musculoesqueleticas si progresion inadecuada",
                "Overtraining si no hay recuperacion suficiente"
            ],
        },

        "resistencia_3x": {
            "name": "Ejercicio de Fuerza 3x/semana",
            "description": "3 sesiones de entrenamiento de fuerza por semana",
            "category": "exercise",
            "duration_days": 84,
            "effects": [
                {"biomarker": "testosterone_male", "change_per_month": 30.0, "direction": "increase",
                 "confidence": 0.75, "evidence_level": "B",
                 "mechanism": "Aumento testosterona con entrenamiento fuerza pesado"},
                {"biomarker": "igf1", "change_per_month": 15.0, "direction": "increase",
                 "confidence": 0.70, "evidence_level": "B",
                 "mechanism": "Aumento IGF-1 por estimulo anabolic muscular"},
                {"biomarker": "homa_ir", "change_per_month": -0.2, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "A",
                 "mechanism": "Mejora sensibilidad insulina en musculo esqueletico"},
            ],
            "contraindications": [
                "Osteoporosis severa (evitar carga axial pesada)",
                "Lesiones musculoesqueleticas activas"
            ],
            "risks": [
                "Lesiones si tecnica inadecuada",
                "Riesgo cardiovascular agudo en hipertensos no diagnosticados"
            ],
        },

        "dieta_mediterranea": {
            "name": "Dieta Mediterranea con AOVE",
            "description": "Dieta mediterranea tradicional con aceite de oliva virgen extra",
            "category": "nutrition",
            "duration_days": 90,
            "effects": [
                {"biomarker": "ldl_cholesterol", "change_per_month": -15.0, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion LDL por acidos grasos monoinsaturados del AOVE",
                 "ceiling_effect": 70.0},
                {"biomarker": "hdl_cholesterol", "change_per_month": 4.0, "direction": "increase",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Aumento HDL por omega-9 y polifenoles del AOVE"},
                {"biomarker": "triglycerides", "change_per_month": -10.0, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Reduccion TG por mejora sensibilidad insulina",
                 "ceiling_effect": 90.0},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.3, "direction": "decrease",
                 "confidence": 0.80, "evidence_level": "A",
                 "mechanism": "Efecto antiinflamatorio polifenoles y omega-3"},
                {"biomarker": "systolic_bp", "change_per_month": -4.0, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion PA por polifenoles y restriccion sodio",
                 "ceiling_effect": 118.0},
            ],
            "contraindications": [],
            "risks": [
                "Ganancia de peso si no hay deficit calorico"
            ],
        },

        "omega3_epa_dha_2g": {
            "name": "Omega-3 EPA+DHA 2g/dia",
            "description": "Suplementacion con 2g de EPA y DHA combinados al dia",
            "category": "supplement",
            "duration_days": 90,
            "effects": [
                {"biomarker": "triglycerides", "change_per_month": -20.0, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion 15-30% TG con 2-4g EPA+DHA/dia (meta-analisis)",
                 "ceiling_effect": 75.0},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.3, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "A",
                 "mechanism": "Reduccion inflamacion por resolvinas y protectinas"},
                {"biomarker": "hdl_cholesterol", "change_per_month": 2.0, "direction": "increase",
                 "confidence": 0.70, "evidence_level": "B",
                 "mechanism": "Ligero aumento HDL"},
                {"biomarker": "diastolic_bp", "change_per_month": -2.0, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "A",
                 "mechanism": "Reduccion PA diastolica por vasodilatacion"},
            ],
            "contraindications": [
                "Anticoagulacion con warfarina (aumenta riesgo sangrado)"
            ],
            "risks": [
                "Aumento tiempo de sangrado",
                "Mal aliento y sabor a pescado (efectos GI menores)"
            ],
        },

        "metformina_850": {
            "name": "Metformina 850mg x2/dia",
            "description": "Metformina como intervencion para longevity (off-label)",
            "category": "pharmaceutical",
            "duration_days": 90,
            "effects": [
                {"biomarker": "hba1c", "change_per_month": -0.27, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion HbA1c 0.5-1.5% en diabeticos T2",
                 "ceiling_effect": 5.5},
                {"biomarker": "homa_ir", "change_per_month": -0.6, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion resistencia insulina por activacion AMPK hepatica"},
                {"biomarker": "ldl_cholesterol", "change_per_month": -8.0, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "A",
                 "mechanism": "Reduccion LDL por mejora metabolica",
                 "ceiling_effect": 75.0},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.3, "direction": "decrease",
                 "confidence": 0.75, "evidence_level": "B",
                 "mechanism": "Efecto antiinflamatorio independiente de glucosa"},
            ],
            "contraindications": [
                "IRC severa (eGFR < 30)",
                "Hepatopatia alcoholica o insuficiencia hepatica",
                "Insuficiencia cardiaca descompensada"
            ],
            "risks": [
                "Deficit de B12 (10-30% con uso prolongado — monitorizar annually)",
                "Acidosis lactica (raro, pero riesgo en IRC)",
                "Molestias GI (nauseas, diarrea) — meist transient"
            ],
        },

        "combinacion_ejercicio_diana": {
            "name": "Plan Combinado: Ejercicio + Dieta",
            "description": "Ejercicio 150min/sem + Dieta mediterranea + Ayuno 16:8",
            "category": "combined",
            "duration_days": 90,
            "effects": [
                {"biomarker": "homa_ir", "change_per_month": -0.7, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Mayor mejora HOMA-IR con combinacion vs monoterapia",
                 "time_to_effect_months": 2},
                {"biomarker": "ldl_cholesterol", "change_per_month": -20.0, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion LDL sinergetica de dieta + ejercicio",
                 "ceiling_effect": 70.0},
                {"biomarker": "triglycerides", "change_per_month": -25.0, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion TG potente con dieta + ejercicio",
                 "ceiling_effect": 80.0},
                {"biomarker": "c_reactive_protein", "change_per_month": -0.6, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Reduccion inflamacion marcada con intervencion dual"},
                {"biomarker": "waist_circumference_male", "change_per_month": -1.0, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion grasa visceral por combinacion diet + ejercicio",
                 "ceiling_effect": 90.0},
                {"biomarker": "vo2max", "change_per_month": 3.0, "direction": "increase",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Aumento VO2max por entrenamiento regular"},
                {"biomarker": "hdl_cholesterol", "change_per_month": 4.5, "direction": "increase",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Mayor aumento HDL con ejercicio + dieta mediterranea"},
                {"biomarker": "hba1c", "change_per_month": -0.13, "direction": "decrease",
                 "confidence": 0.85, "evidence_level": "A",
                 "mechanism": "Mejora glucemia con intervencion combinada",
                 "ceiling_effect": 5.4},
                {"biomarker": "systolic_bp", "change_per_month": -5.0, "direction": "decrease",
                 "confidence": 0.90, "evidence_level": "A",
                 "mechanism": "Reduccion PA mas pronunciada con intervencion dual",
                 "ceiling_effect": 118.0},
            ],
            "contraindications": [
                "Igual que las contraindicaciones individuales"
            ],
            "risks": [
                "Adherencia dificil — compliance a multiples intervenciones es menor",
                "Riesgo overtraining si ejercicio excesivo sin recuperacion"
            ],
        },
    }

    def __init__(self):
        pass

    def get_available_interventions(self) -> List[Dict]:
        return [
            {
                "id": key,
                "name": v["name"],
                "description": v["description"],
                "category": v["category"],
                "effects_count": len(v.get("effects", [])),
                "risks": v.get("risks", []),
                "contraindications": v.get("contraindications", []),
            }
            for key, v in self.INTERVENTIONS.items()
        ]

    def apply(self, intervention_id: str, biomarkers: Dict[str, float]) -> Dict[str, float]:
        if intervention_id not in self.INTERVENTIONS:
            return {}
        intervention = self.INTERVENTIONS[intervention_id]
        changes = {}
        for effect in intervention.get("effects", []):
            biomarker = effect.get("biomarker")
            if biomarker not in biomarkers:
                continue
            if effect.get("confidence", 0) < 0.7:
                continue
            current = biomarkers[biomarker]
            monthly = effect.get("change_per_month", 0)
            direction = effect.get("direction", "increase")
            ceiling = effect.get("ceiling_effect")
            if ceiling is not None:
                if direction == "increase":
                    applied = min(monthly, max(0, ceiling - current) * 0.5)
                else:
                    applied = max(monthly, -(current - ceiling) * 0.5)
            else:
                applied = monthly
            changes[biomarker] = round(current + applied, 2)
        return changes

    def simulate(self, intervention_id: str, biomarkers: Dict[str, float],
                months: int = 3) -> List[Dict[str, Any]]:
        if intervention_id not in self.INTERVENTIONS:
            return []
        intervention = self.INTERVENTIONS[intervention_id]
        projection = []
        simulated = biomarkers.copy()
        for month in range(1, months + 1):
            monthly_changes = {}
            for effect in intervention.get("effects", []):
                biomarker = effect.get("biomarker")
                if biomarker not in simulated or effect.get("confidence", 0) < 0.7:
                    continue
                current = simulated[biomarker]
                monthly = effect.get("change_per_month", 0)
                direction = effect.get("direction", "increase")
                ceiling = effect.get("ceiling_effect")
                new_val = current + monthly
                if ceiling:
                    if direction == "increase":
                        new_val = min(new_val, ceiling)
                    else:
                        new_val = max(new_val, ceiling)
                simulated[biomarker] = new_val
                monthly_changes[biomarker] = round(new_val, 2)
            projection.append({
                "month": month,
                "biomarkers": monthly_changes.copy(),
                "cumulative": simulated.copy(),
            })
        return projection


intervention_engine = InterventionEngine()
