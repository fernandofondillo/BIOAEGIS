"""
BioFish AI — FastAPI Backend
API para el motor de simulacion multi-agente biologico.
Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.orchestrator import orchestrator
from src.biological_clocks import EnsembleClock
from src.interventions import intervention_engine
from src.agent import agent_registry
from src.moderator import moderator_agent

app = FastAPI(
    title="BioFish AI API",
    description="Biological Swarm Intelligence — Simulador multi-agente para salud y longevity",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REQUEST / RESPONSE MODELS ────────────────────────────────────────

class BiomarkerInput(BaseModel):
    """Datos del usuario — todos los biomarcadores disponibles."""
    age: int = Field(default=40, ge=18, le=100)
    sex: str = Field(default="male", pattern="^(male|female)$")
    # Lipidos
    total_cholesterol: float = 200.0
    ldl_cholesterol: float = 130.0
    hdl_cholesterol: float = 50.0
    triglycerides: float = 150.0
    # Glucosa
    glucose_fasting: float = 95.0
    glucose_post_prandial: float = 120.0
    hba1c: float = 5.4
    insulin_fasting: float = 8.0
    homa_ir: float = 1.8
    # Inflamacion
    c_reactive_protein: float = 1.5
    ferritin: float = 100.0
    # Hepatica
    alt: float = 25.0
    ast: float = 22.0
    ggt: float = 30.0
    albumin: float = 4.3
    # Renal
    creatinine: float = 0.95
    egfr: float = 90.0
    urea_bun: float = 28.0
    uric_acid: float = 5.5
    # Hemograma
    leukocytes: float = 7000.0
    lymphocytes_pct: float = 35.0
    mcv: float = 88.0
    red_dist_width: float = 13.0
    # Hormonas
    tsh: float = 2.0
    free_t3: float = 3.0
    free_t4: float = 1.2
    testosterone_male: float = 500.0
    cortisol_morning: float = 15.0
    dhea_s: float = 200.0
    # Nutricionales
    vitamin_d: float = 25.0
    vitamin_b12: float = 400.0
    folate_rbc: float = 300.0
    homocysteine: float = 10.0
    # Composicion corporal
    bmi: float = 26.0
    waist_cm: float = 95.0
    body_fat_pct: float = 25.0
    # Cardiovascular
    systolic_bp: float = 125.0
    diastolic_bp: float = 80.0
    hr_resting: float = 65.0
    # Molecular / fitness
    nadi_level: float = 70.0
    vo2max: float = 38.0
    # Sueno / lifestyle
    sleep_hours: float = 7.0
    hrv_sdnn: float = 45.0
    exercise_min_per_week: int = 120
    smoker: bool = False
    alcohol_drinks_per_week: int = 7
    stress_level: float = 0.5

    def to_biomarkers(self) -> Dict[str, float]:
        sex = self.sex
        waist_key = "waist_circumference_male" if sex == "male" else "waist_circumference_female"
        cr_key = "creatinine_male" if sex == "male" else "creatinine_female"
        bf_key = "body_fat_pct_male" if sex == "male" else "body_fat_pct_female"
        return {
            "chronological_age": float(self.age),
            "sex": self.sex,
            "total_cholesterol": self.total_cholesterol,
            "ldl_cholesterol": self.ldl_cholesterol,
            "hdl_cholesterol": self.hdl_cholesterol,
            "triglycerides": self.triglycerides,
            "glucose_fasting": self.glucose_fasting,
            "glucose_post_prandial": self.glucose_post_prandial,
            "hba1c": self.hba1c,
            "insulin_fasting": self.insulin_fasting,
            "homa_ir": self.homa_ir,
            "c_reactive_protein": self.c_reactive_protein,
            "ferritin": self.ferritin,
            "alt": self.alt,
            "ast": self.ast,
            "ggt": self.ggt,
            "albumin": self.albumin,
            cr_key: self.creatinine,
            "egfr": self.egfr,
            "urea_bun": self.urea_bun,
            "uric_acid": self.uric_acid,
            "leukocytes": self.leukocytes,
            "lymphocyte_pct": self.lymphocytes_pct,
            "mcv": self.mcv,
            "red_dist_width": self.red_dist_width,
            "tsh": self.tsh,
            "free_t3": self.free_t3,
            "free_t4": self.free_t4,
            "testosterone_male": self.testosterone_male,
            "cortisol_morning": self.cortisol_morning,
            "dhea_s": self.dhea_s,
            "vitamin_d": self.vitamin_d,
            "vitamin_b12": self.vitamin_b12,
            "folate_rbc": self.folate_rbc,
            "homocysteine": self.homocysteine,
            "bmi": self.bmi,
            waist_key: self.waist_cm,
            bf_key: self.body_fat_pct,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "hr_resting": self.hr_resting,
            "nadi_level": self.nadi_level,
            "vo2max": self.vo2max,
            "sleep_hours": self.sleep_hours,
            "hrv_sdnn": self.hrv_sdnn,
            "exercise_minutes_per_week": float(self.exercise_min_per_week),
            "smoker": self.smoker,
            "alcohol_drinks_per_week": float(self.alcohol_drinks_per_week),
            "stress_level": self.stress_level,
        }


class SimulationRequest(BaseModel):
    biomarkers: BiomarkerInput
    question: Optional[str] = None
    intervention: Optional[str] = None
    months: int = Field(default=3, ge=1, le=60)


class InterventionSimulateRequest(BaseModel):
    biomarkers: BiomarkerInput
    intervention_id: str
    months: int = Field(default=3, ge=1, le=36)


class CompareRequest(BaseModel):
    biomarkers: BiomarkerInput
    intervention_ids: List[str]
    target_biomarker: str
    months: int = 3


# ── ENDPOINTS ──────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "BioFish AI API",
        "version": "1.0.0",
        "description": "Biological Swarm Intelligence — 18 biological agents + Moderator",
        "docs": "/docs",
        "agents": len(agent_registry.get_all_profiles()),
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/init")
def init_user(data: BiomarkerInput):
    """Inicializa un usuario con sus biomarcadores."""
    biomarkers = data.to_biomarkers()
    result = orchestrator.initialize_user(biomarkers)
    return result


@app.post("/simulate")
def simulate(request: SimulationRequest):
    """Ejecuta un tick de simulacion."""
    biomarkers = request.biomarkers.to_biomarkers()
    state = orchestrator.run_tick(
        tick=0,
        question=request.question,
        intervention=request.intervention,
    )
    return state.to_dict()


@app.post("/simulate/trajectory")
def simulate_trajectory(request: SimulationRequest):
    """Simula la trayectoria a N meses con una intervencion."""
    biomarkers = request.biomarkers.to_biomarkers()
    intervention = request.intervention
    months = request.months
    trajectory = []

    for month in range(1, months + 1):
        state = orchestrator.run_tick(tick=month, intervention=intervention)
        trajectory.append({
            "month": month,
            "summary": state.ensemble_summary,
            "clocks": state.clocks,
            "biomarkers": state.user_data,
        })

    return {"trajectory": trajectory, "intervention": intervention, "months": months}


@app.post("/clocks")
def calculate_clocks(data: BiomarkerInput):
    """Calcula todos los relojes biologicos."""
    biomarkers = data.to_biomarkers()
    clocks = EnsembleClock.calculate(biomarkers)
    clock_dicts = {k: v.to_dict() for k, v in clocks.items()}
    ensemble = EnsembleClock.ensemble_summary(clocks, biomarkers.get("chronological_age", 40))
    return {"clocks": clock_dicts, "ensemble": ensemble}


@app.get("/interventions")
def list_interventions():
    """Lista todas las intervenciones disponibles."""
    return {"interventions": intervention_engine.get_available_interventions()}


@app.post("/interventions/simulate")
def simulate_intervention(request: InterventionSimulateRequest):
    """Simula los efectos de una intervencion a N meses."""
    biomarkers = request.biomarkers.to_biomarkers()
    projection = intervention_engine.simulate(request.intervention_id, biomarkers, request.months)
    return {
        "intervention_id": request.intervention_id,
        "projection": projection,
        "target_biomarkers": list(set(e.get("biomarker") for e in
            intervention_engine.INTERVENTIONS.get(request.intervention_id, {}).get("effects", []))),
    }


@app.post("/interventions/compare")
def compare_interventions(request: CompareRequest):
    """Compara multiples intervenciones sobre un biomarcador."""
    biomarkers = request.biomarkers.to_biomarkers()
    comparison = intervention_engine.compare_interventions(
        biomarkers, request.intervention_ids, request.target_biomarker, request.months
    )
    return {"comparison": comparison, "target_biomarker": request.target_biomarker}


@app.post("/validate_intervention")
def validate_intervention(data: BiomarkerInput, intervention: str):
    """Valida una intervencion para un usuario especifico."""
    biomarkers = data.to_biomarkers()
    output = moderator_agent.moderate_intervention(
        intervention=intervention,
        user_data=biomarkers,
        agent_outputs=[],
    )
    return output.to_dict()


@app.get("/agents")
def list_agents():
    """Lista los 18 perfiles de agentes disponibles."""
    return {
        "agents": agent_registry.get_profile_summary(),
        "total": len(agent_registry.get_all_profiles()),
    }


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    """Obtiene el perfil de un agente especifico."""
    profile = agent_registry.get_profile(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return profile.to_dict()


# ── RUN ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
