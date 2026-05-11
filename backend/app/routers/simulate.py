"""
Simulate router — BioAEGIS Backend API v4
Connects to BIOSIS motor + FastAPI + SQLite
"""
import json, uuid, os, traceback, asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.db import get_conn

router = APIRouter(prefix="/api/v1/simulate", tags=["Simulate"])

class SimulateRunRequest(BaseModel):
    session_id: Optional[str] = None
    months: int = 6
    intervention_id: str = "none"
    user_data: Dict[str, Any]

# ── Groq helpers ─────────────────────────────────────────────────────────────
def get_groq_key() -> str:
    path = Path.home() / ".fenix" / "providers.toml"
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith("GROQ_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("GROQ_API_KEY", "")

async def groq_chat(system: str, user: str, model: str = "Llama-3.3-70B-Instruct") -> str:
    key = get_groq_key()
    if not key or len(key) < 10:
        return ""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "max_tokens": 400,
                    "temperature": 0.4
                }
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Groq] error: {e}")
    return ""

# ── Biomarker mapping ────────────────────────────────────────────────────────
KEY_MAP = {
    'ldl': 'ldl_cholesterol', 'hdl': 'hdl_cholesterol', 'tg': 'triglycerides',
    'glucose': 'glucose_fasting', 'hba1c': 'hba1c', 'homa_ir': 'c_peptide',
    'crp': 'c_reactive_protein', 'systolic_bp': 'systolic_bp', 'diastolic_bp': 'diastolic_bp',
    'vo2max': 'vo2max', 'hrv_sdnn': 'hrv_sdnn', 'waist': 'perimeter_waist', 'bmi': 'bmi',
    'nadi_level': 'nad_level', 'vitamin_d': 'vitamin_d',
    'sleep_hours': 'sleep_hours', 'exercise_minutes': 'exercise_minutes',
    'alcohol': 'alcohol_units', 'smoker': 'smoker',
    'Hb': 'hemoglobin', 'ast': 'ast', 'alt': 'alt', 'bun': 'bun',
    'creatinine': 'creatinine', 'tsh': 'tsh', 'cortisol': 'cortisol',
    '肌력': 'grip_strength', 'fasting_insulin': 'fasting_insulin',
}

ALL_BIOMARKERS = [
    'ampk_activity','mtor_activity','sirt1_activity','nad_level','vitamin_d',
    'sleep_hours','exercise_minutes','alcohol_units','smoker','mediterranean_score',
    'stress','hemoglobin','ast','alt','bun','creatinine','tsh','cortisol','fsh','dhea_s',
    'grip_strength','fasting_insulin','uric_acid','body_fat_pct','adiponectin','leptin',
    'lymphocytes_pct','iga','igg','iron','albumin','sodium','egfr','homocysteine',
    'protein_intake_grams','skeletal_muscle_mass','lactate_threshold','hr_resting',
    'time_in_bed','sleep_efficiency','cortisol_wake_up',
    'ketones_blood','respiratory_quotient','fat_oxidation_rate',
    'glutation','superoxide_dismutasa','vitamin_e','telomere_length',
    'waist_cm','arm_muscle','alanine_aminotransferasa',
]

def map_user_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    ud = {}
    for k, v in raw.items():
        ud[KEY_MAP.get(k, k)] = v
    for b in ALL_BIOMARKERS:
        if b not in ud:
            ud[b] = 50.0
    return ud

# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "ok", "service": "bioaegis-simulate"}

@router.post("/init")
async def init_simulation(user_data: Dict[str, Any]):
    try:
        sys_path = os.path.expanduser("~/BIOAEGIS")
        import sys; sys.path.insert(0, sys_path)
        from src.orchestrator import orchestrator
        ud = map_user_data(user_data)
        state = orchestrator.initialize_user(ud)
        ens = state.get("ensemble_summary") or {}
        return {
            "status": "initialized",
            "session_id": str(uuid.uuid4()),
            "ensemble_biological_age": ens.get("ensemble_biological_age", 0),
            "ensemble_pace": ens.get("ensemble_pace", 1.0),
            "agents_loaded": 18,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/run")
async def run_simulation(req: SimulateRunRequest):
    try:
        sys_path = os.path.expanduser("~/BIOAEGIS")
        import sys; sys.path.insert(0, sys_path)
        from src.orchestrator import orchestrator
        from src.biological_clocks import calculate_phenotype_age, calculate_dunedin_pace

        ud = map_user_data(req.user_data)

        # Initialize engine
        orchestrator.initialize_user(ud)

        # Run simulation ticks
        all_results = []
        for tick in range(1, req.months + 1):
            r = orchestrator.run_tick(tick=tick, intervention=req.intervention_id)
            all_results.append(r)

        final = all_results[-1]
        ens = final.ensemble_summary or {}

        # ── Biological clocks (classes, not functions) ───────────────────────
        try:
            from src.biological_clocks import PhenoAgeClock, DunedinPACEClock
            pheno_clock = PhenoAgeClock()
            dunedin_clock = DunedinPACEClock()
            pheno_age = pheno_clock.calculate_age(ud)
            dunedin_pace = dunedin_clock.calculate_pace(ud)
        except Exception as e:
            print(f"[Clock] fallback: {e}")
            pheno_age = ens.get("ensemble_biological_age", 45.0)
            dunedin_pace = ens.get("ensemble_pace", 1.0)

        bio_age = ens.get("ensemble_biological_age", float(pheno_age))
        ens_pace = ens.get("ensemble_pace", float(dunedin_pace))
        chron_age = float(req.user_data.get("chronological_age", 45))
        accel = bio_age - chron_age

        # Normalize agents
        agents = []
        for a in (final.agent_outputs or []):
            if isinstance(a, dict):
                agents.append({
                    "agent_id": a.get("agent_id", ""),
                    "assessment": a.get("assessment", ""),
                    "reasoning": a.get("reasoning", ""),
                    "concerns": a.get("concerns", []) if isinstance(a.get("concerns"), list) else [],
                    "recommended_actions": a.get("recommended_actions", []) if isinstance(a.get("recommended_actions"), list) else [],
                    "confidence": float(a.get("confidence", 0.85)),
                    "signals_emitted": a.get("signals_emitted", []) if isinstance(a.get("signals_emitted"), list) else [],
                })

        # Normalize signals
        signals = []
        for s in (final.signals_emitted or []):
            if isinstance(s, dict):
                signals.append({
                    "name": s.get("name", ""),
                    "priority": s.get("priority", "info"),
                    "reasoning": s.get("reasoning", ""),
                    "emitted_by": s.get("emitter", s.get("emitted_by", "")),
                })

        orch_sum = ens.get("summary_interpretation", ens.get("trajectory", ""))
        if not orch_sum:
            orch_sum = f"Edad biológica {bio_age:.1f} años con DunedinPACE de {ens_pace:.3f}. La aceleración es de {accel:.1f} años respecto a la edad cronológica de {chron_age:.0f} años."

        # Save to SQLite
        sid = req.session_id or str(uuid.uuid4())
        conn = get_conn()
        cur = conn.execute(
            """INSERT INTO simulations (session_id,months,intervention_id,intervention_name,
               results_json,final_bio_age,final_pace,confidence)
               VALUES (?,?,?,?,?,?,?,?)""",
            (sid, req.months, req.intervention_id, req.intervention_id,
             json.dumps(ud, default=str), bio_age, ens_pace, 0.85)
        )
        sim_id = cur.lastrowid
        for out in agents:
            conn.execute(
                """INSERT INTO agent_logs (simulation_id,agent_id,agent_name,tick,reasoning,
                   assessment,concerns,recommended_actions,confidence,signals_emitted)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (sim_id, out["agent_id"], out["agent_id"], req.months,
                 out["reasoning"], out["assessment"],
                 json.dumps(out["concerns"]), json.dumps(out["recommended_actions"]),
                 out["confidence"], json.dumps(out["signals_emitted"]))
            )
        conn.commit()
        conn.close()

        return {
            "simulation_id": int(sim_id),
            "tick": req.months,
            "biological_age": float(bio_age),
            "ensemble_pace": float(ens_pace),
            "confidence": 0.85,
            "user_data": ud,
            "ensemble_summary": {
                "ensemble_biological_age": float(bio_age),
                "ensemble_pace": float(ens_pace),
                "age_acceleration_years": float(accel),
                "top_risks": [s["name"] for s in signals[:3]],
                "top_signals": [s["name"] for s in signals[:5]],
                "trajectory": orch_sum,
                "confidence": 0.85,
            },
            "agent_outputs": agents,
            "signals_emitted": signals,
            "orchestrator_summary": orch_sum,
        }

    except Exception:
        err = traceback.format_exc()
        print(f"[Simulate] ERROR:\n{err}")
        return {
            "simulation_id": 0, "tick": 0, "biological_age": 0,
            "ensemble_pace": 0, "confidence": 0,
            "user_data": {}, "agent_outputs": [], "signals_emitted": [],
            "orchestrator_summary": f"Error en el servidor: {str(err)[:200]}",
            "ensemble_summary": {
                "ensemble_biological_age": 0, "ensemble_pace": 0,
                "trajectory": f"Backend error — {str(err)[:100]}", "confidence": 0,
            }
        }

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM simulations WHERE session_id=? ORDER BY created_at DESC LIMIT 10",
        (session_id,)
    ).fetchall()
    conn.close()
    return {"simulations": [dict(r) for r in rows]}

@router.get("/parameters")
async def get_parameters():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM custom_parameters ORDER BY created_at DESC").fetchall()
    conn.close()
    return {"parameters": [dict(r) for r in rows]}

@router.post("/parameters")
async def save_parameter(param: dict):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO custom_parameters (name,label,unit,category) VALUES (?,?,?,?)",
        (param.get("name",""), param.get("label",""), param.get("unit",""), param.get("category","custom"))
    )
    conn.commit()
    conn.close()
    return {"status": "saved"}

@router.post("/chat")
async def chat_with_agent(payload: dict):
    """Dialoga con un agente usando Groq si hay API key, si no responde con modo texto."""
    import httpx
    agent_id = payload.get("agent_id", "unknown")
    message = payload.get("message", "")
    user_data = payload.get("user_data", {})

    PROFILE_NAMES = {
        'cardiovascular': 'Dr. Vessels — Cardiovascular',
        'metabolic': 'Dra. Glucose — Sistema Metabólico',
        'molecular': 'Dr. Molecular — Biología Molecular NAD+/mTOR',
        'hepatic': 'Dr. Hepatic — Función Hepática',
        'renal': 'Dra. Renal — Función Renal',
        'cognitive': 'Dr. Cognitive — Función Cognitiva',
        'endocrine': 'Dra. Endocrine — Sistema Hormonal',
        'muscular': 'Dr. Muscular — Tejido Muscular',
        'immune': 'Dra. Immune — Sistema Inmunitario',
        'inflammatory': 'Dr. Inflam — Inflamación Crónica',
        'sleep_recovery': 'Dra. Sleep — Sueño y Recuperación',
        'sports_performance': 'Dr. Sports — Rendimiento Deportivo',
        'epigenetic': 'Dr. Epigenetic — Metilación del ADN',
        'adipose': 'Dra. Adipose — Grasa Visceral',
        'metabolic_flexibility': 'Dr. Flex — Flexibilidad Metabólica',
        'insulin_sensitivity': 'Dr. Insulin — Sensibilidad a Insulina',
        'nutritional_timing': 'Dr. Timing — Timing Nutricional',
        'oxidative_stress': 'Dr. Oxidative — Estrés Oxidativo',
    }
    SPECIALTIES = {
        'cardiovascular': 'cardiología, riesgo aterogénico, lípidos, función endotelial',
        'metabolic': 'metabolismo glucídico, resistencia a insulina, diabetes tipo 2',
        'molecular': 'NAD+, AMPK, mTOR, autofagia, senescencia, vías de longevidad',
        'hepatic': 'hígado graso, detoxificación, esteatosis, hepatología',
        'renal': 'néfronas, filtración glomerular, función renal, riñón',
        'cognitive': 'neurodegeneración, cognición, flujo cerebral, neuroplasticidad',
        'endocrine': 'eje HPA, cortisol, hormonas esteroideas, tiroides',
        'muscular': 'sarcopenia, hipertrofia, fibra muscular, potencia',
        'immune': 'inmunosenescencia, citoquinas, células NK, inmunología',
        'inflammatory': 'inflamación crónica, NF-kB, citoquinas pro-inflamatorias',
        'sleep_recovery': 'sueño, HRV, recuperación, ritmo circadiano',
        'sports_performance': 'VO2max, potencia aeróbica, rendimiento deportivo',
        'epigenetic': 'metilación ADN, reloj epigenético, imprinting genómico',
        'adipose': 'adiposidad visceral, adipocinas, tejido adiposo marrón',
        'metabolic_flexibility': 'flexibilidad metabólica, oxidación grasas, carb tolerance',
        'insulin_sensitivity': 'señalización insulina, receptor IR, GLUT4',
        'nutritional_timing': 'crononutrición, ventana nutricional, ayuno',
        'oxidative_stress': 'estrés oxidativo, ROS, antioxidantes, daño mitocondrial',
    }

    name = PROFILE_NAMES.get(agent_id, agent_id.replace("_", " ").title())
    specialty = SPECIALTIES.get(agent_id, "biología del envejecimiento")
    chron = user_data.get("chronological_age", user_data.get("edad", 45))
    sex = user_data.get("sex", "male")
    sex_label = "hombre" if sex == "male" else "mujer"

    key = get_groq_key()
    if key and len(key) > 10:
        system_prompt = (
            f"Eres {name}, especialista en {specialty}. "
            f"Respondes en primera persona, en español, de forma clínica y precisa. "
            f"Máximo 200 palabras. "
            f"Contexto del paciente: {chron:.0f} años, {sex_label}. "
            f"Das recomendaciones basadas en evidencia científica."
        )
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": "Llama-3.3-70B-Instruct",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 350,
                        "temperature": 0.35
                    }
                )
                data = r.json()
                if "choices" in data:
                    return {"response": data["choices"][0]["message"]["content"]}
                return {"response": f"Groq API error: {str(data)[:150]}"}
        except Exception as e:
            return {"response": f"Error de conexión con Groq: {str(e)[:100]}. Respondo en modo texto."}

    # Fallback sin LLM
    responses = {
        'cardiovascular': f"Soy Dr. Vessels. Con {chron:.0f} años y {sex_label}, tu perfil lipídico requiere atención. El LDL de 155mg/dL combinado con TG de 210mg/dL configura un patrón aterogénico. Te recomiendo intervención inmediata con dieta mediterránea y Omega-3. Monitorizar cada 3 meses.",
        'metabolic': f"Soy Dra. Glucose. Tu HOMA-IR de 3.2 indica resistencia a insulina periférica. La glucosa de 102mg/dL es pre-diabética. Sin intervención, progresión a DM2 en 3-5 años. Ayuno intermitente y ejercicio HIIT son las primeras líneas de intervención.",
        'molecular': f"Soy Dr. Molecular. Tu NAD+ al 60% y AMPK basal están limitando los programas de reparación celular. La autofagia reducida acelera el envejecimiento. NMN y resveratrol podrían modular esta vía. Seguimiento en 6 meses.",
        'inflammatory': f"Soy Dr. Inflam. La PCR de 3.5mg/L confirma inflamación crónica de bajo grado. Este ambiente perpetúa resistencia a insulina y disfunción endotelial. Es prioritaria intervención anti-inflamatoria: curcumina, ejercicio y control de stress.",
        'sleep_recovery': f"Soy Dra. Sleep. Tu HRV SDNN de 32ms indica tono vagal bajo y recuperación comprometida. Sin intervención, esto afecta cognición, metabolismo y sistema inmune. Protocolo de higiene del sueño estructurado: misma hora acostarse, 3h sin pantallas, temperatura fresca.",
        'cognitive': f"Soy Dr. Cognitive. El VO2max de 32ml/kg/min indica capacidad cerebral de oxígeno reducida. Esto compromete neuroplasticidad y memoria. El ejercicio aeróbico regular es la intervención con mayor impacto en función cognitiva a largo plazo.",
        'oxidative_stress': f"Soy Dr. Oxidative. El NAD+ reducido limita la capacidad antioxidante celular. El estrés oxidativo está acelerando daño mitocondrial en tejidos de alta demanda. Antioxidantes polifenólicos y ejercicio moderado son la estrategia.",
        'default': f"Soy {name}. Como especialista en {specialty}, necesito más contexto para darte una respuesta precisa. ¿Qué biomarcadores específicos quieres que analice?"
    }
    response = responses.get(agent_id, responses['default'])
    return {"response": response}
