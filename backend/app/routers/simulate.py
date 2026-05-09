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
    # Datos custom del frontend
    custom_biomarkers: Optional[Dict[str, float]] = None

@router.post("/init")
async def init_simulation(user_data: Dict[str, Any]):
    """Inicializa twin con los datos del paciente (incluye custom biomarkers)."""
    try:
        from src.orchestrator import orchestrator
        state = orchestrator.initialize_user(user_data)
        # Guardar sesión
        conn = get_conn()
        sid = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO sessions (session_id, user_data_json) VALUES (?, ?)",
            (sid, json.dumps(user_data)),
        )
        conn.commit()
        conn.close()
        return {
            "status": "initialized",
            "session_id": sid,
            "ensemble_biological_age": state.get("ensemble_bio_age", 0),
            "dunedin_pace": state.get("dunedin_pace", 0),
            "agents_loaded": 18,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/run")
async def run_simulation(req: SimulateRunRequest):
    """Ejecuta simulación y guarda TODA la trazabilidad de agentes en SQLite."""
    try:
        from src.orchestrator import orchestrator
        from src.agent import agent_registry

        # Asegurar que la intervención existe
        if req.intervention_id not in ["none"]:
            from src.interventions import intervention_engine
            known = [i.id for i in intervention_engine.INTERVENTIONS]
            if req.intervention_id not in known:
                # Es custom — buscar en la DB
                conn = get_conn()
                row = conn.execute(
                    "SELECT * FROM custom_interventions WHERE rowid = ?",
                    (int(req.intervention_id),)
                ).fetchone()
                conn.close()
                if row:
                    intervention_engine.add_custom_intervention(dict(row))

        orchestrator.initialize_user(req.user_data)
        results = []
        for tick in range(1, req.months + 1):
            r = orchestrator.run_tick(tick=tick, intervention=req.intervention_id)
            results.append(r)

        final = results[-1]

        # Guardar simulación en SQLite
        sim_id = save_simulation(req, final)

        return {
            "simulation_id": sim_id,
            "tick": req.months,
            "biological_age": final.user_data.get("ensemble_biological_age", 0),
            "ensemble_pace": final.user_data.get("dunedin_pace", 0),
            "confidence": 0.85,
            "user_data": final.user_data,
            "agent_outputs": final.agent_outputs,
            "signals_emitted": final.signals_emitted or [],
            "orchestrator_summary": final.orchestrator_summary or "",
            "moderator_trajectory": final.moderator_trajectory or "",
            "moderator_concerns": final.moderator_concerns or [],
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
    """Obtiene historial de simulaciones de una sesión."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM simulations WHERE session_id = ? ORDER BY created_at DESC LIMIT 20",
        (session_id,),
    ).fetchall()
    conn.close()
    return {"simulations": [dict(r) for r in rows]}

@router.get("/agents/{simulation_id}")
async def get_agent_logs(simulation_id: int):
    """Obtiene logs completos de los 18 agentes en una simulación."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM agent_logs WHERE simulation_id = ? ORDER BY tick, agent_id",
        (simulation_id,),
    ).fetchall()
    conn.close()
    return {"agent_logs": [dict(r) for r in rows]}


def save_simulation(req: SimulateRunRequest, result) -> int:
    """Guarda resultado de simulación y logs de agentes en SQLite."""
    conn = get_conn()
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
            result.user_data.get("ensemble_biological_age", 0),
            result.user_data.get("dunedin_pace", 0),
            0.85,
        ),
    )
    sim_id = cur.lastrowid
    conn.commit()

    # Guardar logs de agentes
    for out in (result.agent_outputs or []):
        conn.execute(
            """INSERT INTO agent_logs
               (simulation_id, agent_id, agent_name, tick, reasoning, assessment,
                concerns, recommended_actions, confidence, signals_emitted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                sim_id,
                out.get("agent_id", ""),
                out.get("name", out.get("agent_id", "")),
                req.months,
                out.get("reasoning", ""),
                out.get("assessment", ""),
                json.dumps(out.get("concerns", [])),
                json.dumps(out.get("recommended_actions", [])),
                out.get("confidence", 0),
                json.dumps(out.get("signals_emitted", [])),
            ),
        )

    # Guardar signals
    for sig in (result.signals_emitted or []):
        conn.execute(
            "INSERT INTO signal_logs (simulation_id, signal_name, signal_priority, reasoning, emitted_by) VALUES (?, ?, ?, ?, ?)",
            (sim_id, sig.get("name", ""), sig.get("priority", ""), sig.get("reasoning", ""), sig.get("emitted_by", "")),
        )

    conn.commit()
    conn.close()
    return sim_id