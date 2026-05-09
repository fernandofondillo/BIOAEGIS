"""
Memory router — persistencia y trazabilidad de simulaciones.
"""
from fastapi import APIRouter
from app.db import get_conn

router = APIRouter(prefix="/api/v1/memory", tags=["Memory"])

@router.get("/sessions")
async def list_sessions():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, session_id, initial_bio_age, created_at FROM sessions ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return {"sessions": [dict(r) for r in rows]}

@router.get("/simulations/{session_id}")
async def get_simulations(session_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM simulations WHERE session_id = ? ORDER BY created_at DESC LIMIT 20",
        (session_id,),
    ).fetchall()
    conn.close()
    return {"simulations": [dict(r) for r in rows]}

@router.get("/signals/{simulation_id}")
async def get_signal_trail(simulation_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM signal_logs WHERE simulation_id = ? ORDER BY id",
        (simulation_id,),
    ).fetchall()
    conn.close()
    return {"signals": [dict(r) for r in rows]}

@router.delete("/clear")
async def clear_all_memory():
    conn = get_conn()
    conn.executescript(
        "DELETE FROM signal_logs; DELETE FROM agent_logs; DELETE FROM simulations; "
        "DELETE FROM sessions; DELETE FROM custom_parameters; DELETE FROM custom_interventions;"
    )
    conn.commit()
    conn.close()
    return {"status": "memory cleared"}
