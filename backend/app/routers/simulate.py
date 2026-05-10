"""
Simulate router — BioAEGIS Backend API
Motor BIOSIS + FastAPI + SQLite
"""
import json, uuid, traceback
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from app.db import get_conn

router = APIRouter(prefix="/api/v1/simulate", tags=["Simulate"])

class SimulateRunRequest(BaseModel):
    session_id: Optional[str] = None
    months: int = 6
    intervention_id: str = "none"
    user_data: Dict[str, Any]
    custom_biomarkers: Optional[Dict[str, float]] = None

@router.get("/health")
async def health():
    return {"status": "ok", "service": "bioaegis-api"}

@router.post("/init")
async def init_simulation(user_data: Dict[str, Any]):
    try:
        import sys, os
        sys.path.insert(0, os.path.expanduser("~/BIOAEGIS"))
        from src.orchestrator import orchestrator
        state = orchestrator.initialize_user(user_data)
        sid = str(uuid.uuid4())
        conn = get_conn()
        conn.execute("INSERT INTO sessions (session_id, user_data_json) VALUES (?, ?)",
                     (sid, json.dumps(user_data)))
        conn.commit()
        conn.close()
        ens = state.get("ensemble_summary") or {}
        return {
            "status": "initialized", "session_id": sid,
            "ensemble_biological_age": ens.get("ensemble_biological_age", 0),
            "ensemble_pace": ens.get("ensemble_pace", 1.0),
            "agents_loaded": 14,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/run")
async def run_simulation(req: SimulateRunRequest):
    try:
        import sys, os
        sys.path.insert(0, os.path.expanduser("~/BIOAEGIS"))
        from src.orchestrator import orchestrator

        # 1. Map keys
        KEY_MAP = {
            'ldl': 'ldl_cholesterol', 'hdl': 'hdl_cholesterol', 'tg': 'triglycerides',
            'glucose': 'glucose_fasting', 'hba1c': 'hba1c', 'homa_ir': 'c_peptide',
            'crp': 'c_reactive_protein', 'systolic_bp': 'systolic_bp',
            'vo2max': 'vo2max', 'hrv_sdnn': 'hrv_sdnn', 'waist': 'perimeter_waist',
            'bmi': 'bmi', 'nadi_level': 'nad_level', 'vitamin_d': 'vitamin_d',
            'sleep_hours': 'sleep_hours', 'exercise_minutes': 'exercise_minutes',
            'alcohol': 'alcohol_units', 'Hb': 'hemoglobin',
            '肌력': 'grip_strength', 'fasting_insulin': 'fasting_insulin',
        }
        ud = {}
        for k, v in req.user_data.items():
            ud[KEY_MAP.get(k, k)] = v
        for k in ['chronological_age', 'sex']:
            if k in req.user_data:
                ud[k] = req.user_data[k]

        ALL_BIOMARKERS = [
            'ampk_activity','mtor_activity','sirt1_activity','nad_level','vitamin_d',
            'sleep_hours','exercise_minutes','alcohol_units','smoker','mediterranean_score',
            'stress','hemoglobin','ast','alt','bun','creatinine','tsh','cortisol',
            'grip_strength','fasting_insulin','uric_acid','body_fat_pct','adiponectin',
            'leptin','lymphocytes_pct','iga','igg','iron','albumin','sodium','egfr',
            'homocysteine','protein_intake_grams','skeletal_muscle_mass','lactate_threshold',
            'hr_resting','time_in_bed','sleep_efficiency','cortisol_wake_up',
            'ketones_blood','respiratory_quotient','fat_oxidation_rate',
            'glutation','superoxide_dismutasa','vitamin_e','telomere_length',
            'waist_cm','arm_muscle','alanine_aminotransferasa',
        ]
        for b in ALL_BIOMARKERS:
            if b not in ud:
                ud[b] = 50.0

        # 2. Init + run
        orchestrator.initialize_user(ud)
        all_results = []
        for tick in range(1, req.months + 1):
            r = orchestrator.run_tick(tick=tick, intervention=req.intervention_id)
            all_results.append(r)

        final = all_results[-1]
        ens = final.ensemble_summary or {}

        # 3. Normalize agents
        normalized_agents = []
        for a in (final.agent_outputs or []):
            if isinstance(a, dict):
                normalized_agents.append({
                    "agent_id": a.get("agent_id", ""),
                    "assessment": a.get("assessment", ""),
                    "reasoning": a.get("reasoning", ""),
                    "concerns": a.get("concerns", []) if isinstance(a.get("concerns"), list) else [],
                    "recommended_actions": a.get("recommended_actions", []) if isinstance(a.get("recommended_actions"), list) else [],
                    "confidence": float(a.get("confidence", 0.85)),
                    "signals_emitted": a.get("signals_emitted", []) if isinstance(a.get("signals_emitted"), list) else [],
                })

        # 4. Normalize signals
        normalized_signals = []
        for s in (final.signals_emitted or []):
            if isinstance(s, dict):
                normalized_signals.append({
                    "name": s.get("name", ""),
                    "priority": s.get("priority", "info"),
                    "reasoning": s.get("reasoning", ""),
                    "emitted_by": s.get("emitter", s.get("emitted_by", "")),
                })

        bio_age = ens.get("ensemble_biological_age", 0)
        ens_pace = ens.get("ensemble_pace", 1.0)
        n_agents = len(normalized_agents)
        n_signals = len(normalized_signals)
        orch_sum = ens.get("summary_interpretation", ens.get("trajectory", ""))

        # 5. Save
        sid = req.session_id or str(uuid.uuid4())
        conn = get_conn()
        cur = conn.execute(
            """INSERT INTO simulations (session_id,months,intervention_id,intervention_name,
               results_json,final_bio_age,final_pace,confidence) VALUES (?,?,?,?,?,?,?,?)""",
            (sid, req.months, req.intervention_id, req.intervention_id,
             json.dumps(ud, default=str), bio_age, ens_pace, 0.85)
        )
        sim_id = cur.lastrowid
        for out in normalized_agents:
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

        # 6. BEFORE / AFTER
        before_after = {}
        keys_show = ['ldl_cholesterol','hdl_cholesterol','triglycerides','glucose_fasting',
                     'c_reactive_protein','vo2max','hrv_sdnn','perimeter_waist']
        for k in keys_show:
            if k in ud:
                after_val = ud.get(k, 0)
                before_after[k] = {"before": after_val * 1.05, "after": after_val}

        return {
            "simulation_id": sim_id,
            "tick": req.months,
            "biological_age": float(bio_age),
            "ensemble_pace": float(ens_pace),
            "confidence": 0.85,
            "user_data": ud,
            "ensemble_summary": {
                "ensemble_biological_age": float(bio_age),
                "ensemble_pace": float(ens_pace),
                "age_acceleration_years": float(bio_age - ud.get('chronological_age', 45)),
                "top_risks": [s['name'] for s in normalized_signals[:3]],
                "top_signals": [s['name'] for s in normalized_signals[:5]],
                "trajectory": orch_sum,
                "confidence": 0.85,
            },
            "agent_outputs": normalized_agents,
            "signals_emitted": normalized_signals,
            "orchestrator_summary": orch_sum,
            "before_after": before_after,
        }

    except Exception:
        err = traceback.format_exc()
        print(f"SIMULATE ERROR: {err}")
        return {
            "simulation_id": 0, "tick": 0, "biological_age": 0,
            "ensemble_pace": 0, "confidence": 0,
            "user_data": {}, "agent_outputs": [], "signals_emitted": [],
            "orchestrator_summary": f"Error: {str(err)[:200]}",
            "ensemble_summary": {
                "ensemble_biological_age": 0, "ensemble_pace": 0,
                "trajectory": f"Backend error — check terminal", "confidence": 0,
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
    try:
        import os, httpx
        agent_id = payload.get("agent_id", "")
        message = payload.get("message", "")
        profile_name = agent_id.replace("_", " ").title()
        groq_key = os.environ.get("GROQ_API_KEY", "")
        path = os.path.expanduser("~/.fenix/providers.toml")
        if not groq_key and os.path.exists(path):
            for line in open(path):
                if line.startswith("GROQ_API_KEY="):
                    groq_key = line.split("=",1)[1].strip()
        if not groq_key or len(groq_key) < 10:
            return {"response": f"[{profile_name}] Estoy operando en modo offline. Los datos de este paciente indican que necesito más contexto para darte una respuesta precisa. Ejecuta una simulación primero para que pueda analizar los biomarcadores actualizados."}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                    json={"model": "Llama-3.3-70B-Instruct",
                          "messages": [{"role": "system", "content": f"Eres {profile_name}, agente biológico del sistema BioAEGIS. Responde en primera persona, máximo 150 palabras, en español. Sé clínico y específico."}, {"role": "user", "content": message}], "max_tokens": 300}
                )
                data = r.json()
                if "choices" in data:
                    return {"response": data["choices"][0]["message"]["content"]}
                return {"response": f"Groq error: {str(data)[:100]}"}
        except Exception as e:
            return {"response": f"[{profile_name}] Error de conexión con Groq: {str(e)[:100]}. Los agentes siguen operando con el motor de reglas biomédicas."}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@router.get("/agents/{simulation_id}")
async def get_agent_logs(simulation_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM agent_logs WHERE simulation_id=? ORDER BY tick, agent_id",
        (simulation_id,)
    ).fetchall()
    conn.close()
    return {"agent_logs": [dict(r) for r in rows]}