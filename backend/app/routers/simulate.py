"""
Simulate router — conecta con el motor BIOSIS (src/orchestrator)
Guarda historial completo en SQLite para memoria persistente.
"""
import json, uuid
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from app.db import get_conn

router = APIRouter(prefix="/api/v1/simulate", tags=["Simulate"])

class SimulateRunRequest(BaseModel):
    session_id: Optional[str] = None
    months: int = 6
    intervention_id: str = "none"
    user_data: Dict[str, Any]
    custom_biomarkers: Optional[Dict[str, float]] = None

@router.post("/init")
async def init_simulation(user_data: Dict[str, Any]):
    """Inicializa twin con los datos del paciente."""
    try:
        from src.orchestrator import orchestrator
        state = orchestrator.initialize_user(user_data)
        conn = get_conn()
        sid = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO sessions (session_id, user_data_json) VALUES (?, ?)",
            (sid, json.dumps(user_data)),
        )
        conn.commit()
        conn.close()
        ens = state.get("ensemble_summary") or {}
        return {
            "status": "initialized",
            "session_id": sid,
            "ensemble_biological_age": ens.get("ensemble_biological_age", 0),
            "ensemble_pace": ens.get("ensemble_pace", 1.0),
            "agents_loaded": state.get("available_agents", 18),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/run")
async def run_simulation(req: SimulateRunRequest):
    """Ejecuta simulación y devuelve los 18 agentes + señales."""
    try:
        from src.orchestrator import orchestrator
        from src.agent import agent_registry

        if req.intervention_id not in ["none"]:
            from src.interventions import intervention_engine
            known = [i.id for i in intervention_engine.INTERVENTIONS]
            if req.intervention_id not in known:
                conn = get_conn()
                row = conn.execute(
                    "SELECT * FROM custom_interventions WHERE rowid = ?",
                    (int(req.intervention_id),)
                ).fetchone()
                conn.close()
                if row:
                    intervention_engine.add_custom_intervention(dict(row))

        # Mapear keys del frontend → keys del motor biológico
        KEY_MAP = {
            'ldl': 'ldl_cholesterol', 'hdl': 'hdl_cholesterol', 'tg': 'triglycerides',
            'glucose': 'glucose_fasting', 'hba1c': 'hba1c', 'homa_ir': 'c_peptide',
            'crp': 'c_reactive_protein', 'systolic_bp': 'systolic_bp',
            'vo2max': 'vo2max', 'hrv_sdnn': 'hrv_sdnn', 'waist': 'perimeter_waist',
            'bmi': 'bmi', 'nadi_level': 'nampk_activity', 'vitamin_d': 'vitamin_d',
            'sleep_hours': 'sleep_hours', 'exercise_minutes': 'exercise_minutes',
            'alcohol': 'alcohol_units', 'smoker': 'smoker',
            'ast': 'ast', 'alt': 'alt', 'bun': 'bun', 'creatinine': 'creatinine',
            'tsh': 'tsh', 'cortisol': 'cortisol', 'Hb': 'hemoglobin',
            '肌력': 'grip_strength', 'fasting_insulin': 'fasting_insulin',
            'uric_acid': 'uric_acid', 'body_fat_pct': 'body_fat_pct',
        }
        mapped_data = {}
        for k, v in req.user_data.items():
            mapped_key = KEY_MAP.get(k, k)
            mapped_data[mapped_key] = v

        # Rellenar todos los biomarkers posibles con valores seguros
        ALL_BIOMARKERS = [
            'ldl_cholesterol','hdl_cholesterol','triglycerides','glucose_fasting','hba1c',
            'c_peptide','c_reactive_protein','systolic_bp','vo2max','hrv_sdnn','perimeter_waist',
            'bmi','ampk_activity','mtor_activity','sirt1_activity','nad_level','vitamin_d',
            'sleep_hours','exercise_minutes','alcohol_units','smoker','mediterranean_score',
            'stress','hemoglobin','ast','alt','bun','creatinine','tsh','cortisol','fsh','dhea_s',
            'grip_strength','fasting_insulin','uric_acid','body_fat_pct','adiponectin','leptin',
            'lymphocytes_pct','iga','igg','iron','albumin','sodium','egfr','homocysteine',
            'protein_intake_grams','skeletal_muscle_mass','lactate_threshold','hr_resting',
            'time_in_bed','sleep_efficiency','cortisol_wake_up','ketones_blood',
            'respiratory_quotient','fat_oxidation_rate','glutation','superoxide_dismutasa',
            'vitamin_e','telomere_length','epigenetic_age','waist_cm','arm_muscle',
            'alanine_aminotransferasa',
        ]
        for b in ALL_BIOMARKERS:
            if b not in mapped_data:
                if b == 'sex':
                    mapped_data['sex'] = req.user_data.get('sex', 'male')
                elif b in ('smoker',):
                    mapped_data[b] = False
                else:
                    mapped_data[b] = 50.0

        orchestrator.initialize_user(mapped_data)
        results = []
        for tick in range(1, req.months + 1):
            r = orchestrator.run_tick(tick=tick, intervention=req.intervention_id)
            results.append(r)

        final = results[-1]
        ens = final.ensemble_summary or {}

        sim_id = save_simulation(req, final)

        # Normalize agent_outputs: ensure agent_name field exists
        normalized_agents = []
        for a in (final.agent_outputs or []):
            if isinstance(a, dict):
                normalized_agents.append({
                    "agent_id": a.get("agent_id", ""),
                    "agent_name": a.get("name", a.get("agent_id", "")),
                    "assessment": a.get("assessment", ""),
                    "reasoning": a.get("reasoning", ""),
                    "concerns": a.get("concerns", []) if isinstance(a.get("concerns"), list) else [],
                    "recommended_actions": a.get("recommended_actions", []) if isinstance(a.get("recommended_actions"), list) else [],
                    "confidence": float(a.get("confidence", 0.8)),
                    "signals_emitted": a.get("signals_emitted", []) if isinstance(a.get("signals_emitted"), list) else [],
                })

        # Normalize signals
        normalized_signals = []
        for s in (final.signals_emitted or []):
            if isinstance(s, dict):
                normalized_signals.append({
                    "name": s.get("name", ""),
                    "priority": s.get("priority", "info"),
                    "reasoning": s.get("reasoning", ""),
                    "emitted_by": s.get("emitter", s.get("emitted_by", "")),
                })

        # Moderator
        mod = final.moderator_output or {}
        mod_trajectory = mod.get("trajectory_summary", "") if isinstance(mod, dict) else ""

        return {
            "simulation_id": sim_id,
            "tick": req.months,
            "biological_age": ens.get("ensemble_biological_age", 0),
            "ensemble_pace": ens.get("ensemble_pace", 1.0),
            "confidence": 0.85,
            "user_data": final.user_data,
            "ensemble_summary": {
                "ensemble_biological_age": ens.get("ensemble_biological_age", 0),
                "ensemble_pace": ens.get("ensemble_pace", 1.0),
                "age_acceleration_years": ens.get("ensemble_acceleration", 0),
                "top_risks": [],
                "top_signals": [s["name"] for s in normalized_signals[:5]],
                "trajectory": ens.get("summary_interpretation", ""),
                "confidence": 0.85,
            },
            "agent_outputs": normalized_agents,
            "signals_emitted": normalized_signals,
            "orchestrator_summary": ens.get("summary_interpretation", ""),
            "moderator_trajectory": mod_trajectory,
            "moderator_concerns": [],
        }

    except Exception as e:
        import traceback; traceback.print_exc()
        return {
            "error": str(e), "tick": 0, "biological_age": 0,
            "ensemble_pace": 0, "confidence": 0, "user_data": {},
            "agent_outputs": [], "signals_emitted": [],
        }

@router.get("/history/{session_id}")
async def get_simulation_history(session_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM simulations WHERE session_id = ? ORDER BY created_at DESC LIMIT 20",
        (session_id,),
    ).fetchall()
    conn.close()
    return {"simulations": [dict(r) for r in rows]}

@router.get("/agents/{simulation_id}")
async def get_agent_logs(simulation_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM agent_logs WHERE simulation_id = ? ORDER BY tick, agent_id",
        (simulation_id,),
    ).fetchall()
    conn.close()
    return {"agent_logs": [dict(r) for r in rows]}

@router.post("/chat")
async def chat_with_agent(payload: dict):
    """Permite dialogar con un agente específico."""
    try:
        from src.agent import agent_registry
        from src.orchestrator import orchestrator

        agent_id = payload.get("agent_id", "")
        message = payload.get("message", "")
        user_data = payload.get("user_data", {})

        profile = agent_registry.get_agent_profile(agent_id)
        if not profile:
            return {"response": f"Agente {agent_id} no encontrado. Available agents: {', '.join([p.agent_id for p in agent_registry._profiles.values()[:5]])}"}

        # Get Groq API key
        import os
        groq_key = os.environ.get("GROQ_API_KEY", "")
        path = os.path.expanduser("~/.fenix/providers.toml")
        if not groq_key and os.path.exists(path):
            for line in open(path):
                if line.startswith("GROQ_API_KEY="):
                    groq_key = line.split("=",1)[1].strip()

        if groq_key and len(groq_key) > 10:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=30) as client:
                    sys_prompt = f"Eres {profile.name}, {profile.specialty}. Responde en primera persona, máximo 200 palabras. Contexto del paciente: {user_data.get('chronological_age', '?')} años, sex: {user_data.get('sex', '?')}. Pregunta: {message}"
                    r = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                        json={"model": "Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": message}], "max_tokens": 300},
                    )
                    data = r.json()
                    if "choices" in data:
                        return {"response": data["choices"][0]["message"]["content"]}
            except:
                pass

        # Fallback sin LLM
        return {"response": f"[{profile.name}] Gracias por tu pregunta. Como especialista en {profile.specialty}, te recomiendo revisar los datos biométricos del paciente. Los valores actuales muestran indicadores importantes que requieren seguimiento."}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}
    conn = get_conn()
    ens = result.ensemble_summary or {}
    cur = conn.execute(
        """INSERT INTO simulations
           (session_id, months, intervention_id, intervention_name, results_json,
            final_bio_age, final_pace, confidence)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            req.session_id or str(uuid.uuid4()),
            req.months,
            req.intervention_id,
            req.intervention_id,
            json.dumps(result.user_data, default=str),
            ens.get("ensemble_biological_age", 0),
            ens.get("ensemble_pace", 1.0),
            0.85,
        ),
    )
    sim_id = cur.lastrowid
    conn.commit()

    for out in (result.agent_outputs or []):
        if isinstance(out, dict):
            conn.execute(
                """INSERT INTO agent_logs
                   (simulation_id, agent_id, agent_name, tick, reasoning, assessment,
                    concerns, recommended_actions, confidence, signals_emitted)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sim_id,
                    out.get("agent_id", ""),
                    out.get("agent_id", ""),
                    req.months,
                    out.get("reasoning", ""),
                    out.get("assessment", ""),
                    json.dumps(out.get("concerns", [])),
                    json.dumps(out.get("recommended_actions", [])),
                    float(out.get("confidence", 0.8)),
                    json.dumps(out.get("signals_emitted", [])),
                ),
            )
    conn.commit()
    conn.close()
    return sim_id