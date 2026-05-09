"""
Interventions router — gestión dinámica de intervenciones custom.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import get_conn

router = APIRouter(prefix="/api/v1/interventions", tags=["Interventions"])

BUILTIN_INTERVENTIONS = [
    {"id": "none", "name": "Sin intervención", "icon": "⚪", "color": "#6b7280", "description": "Simular sin cambios", "strength": "none"},
    {"id": "ayuno_intermitente_16_8", "name": "Ayuno 16:8", "icon": "⏰", "color": "#3b82f6", "description": "16h ayuno / 8h comida", "strength": "moderate"},
    {"id": "ejercicio_aerobico_150", "name": "Ejercicio Aeróbico", "icon": "🏃", "color": "#10b981", "description": "150 min/sem moderada", "strength": "moderate"},
    {"id": "hiit_3x", "name": "HIIT 3x", "icon": "⚡", "color": "#f59e0b", "description": "3x HIIT/semana", "strength": "strong"},
    {"id": "dieta_mediterranea", "name": "Dieta Mediterránea", "icon": "🫒", "color": "#22c55e", "description": "Frutas, verduras, aceite de oliva", "strength": "moderate"},
    {"id": "omega3_epa_dha_2g", "name": "Omega-3 (2g)", "icon": "🐟", "color": "#06b6d4", "description": "2g EPA+DHA diarios", "strength": "mild"},
    {"id": "combinacion_ejercicio_diana", "name": "Plan Combinado", "icon": "🎯", "color": "#8b5cf6", "description": "Ejercicio + ayuno + suplementos", "strength": "strong"},
    {"id": "metformina_850", "name": "Metformina 850mg", "icon": "💊", "color": "#ec4899", "description": "Fármaco sensibilizador a insulina", "strength": "pharmacological"},
]

class CustomIntervention(BaseModel):
    name: str
    description: str = ""
    icon: str = "💊"
    color: str = "#8b5cf6"
    strength: str = "moderate"
    effects: str = "{}"  # JSON string with effect multipliers

@router.get("/")
async def list_interventions():
    """Lista intervenciones built-in + custom."""
    conn = get_conn()
    rows = conn.execute("SELECT * FROM custom_interventions").fetchall()
    conn.close()
    custom = [dict(r) for r in rows]
    return {
        "interventions": BUILTIN_INTERVENTIONS + custom,
        "builtin": len(BUILTIN_INTERVENTIONS),
        "custom_count": len(custom),
    }

@router.post("/")
async def add_intervention(i: CustomIntervention):
    """Añade una intervención custom."""
    conn = get_conn()
    conn.execute(
        "INSERT INTO custom_interventions (name, description, icon, color, strength, effects) VALUES (?, ?, ?, ?, ?, ?)",
        (i.name, i.description, i.icon, i.color, i.strength, i.effects),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM custom_interventions WHERE name = ?", (i.name,)).fetchone()
    conn.close()
    return {"status": "added", "intervention": dict(row)}

@router.delete("/{name}")
async def delete_intervention(name: str):
    conn = get_conn()
    cur = conn.execute("DELETE FROM custom_interventions WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(404, "Not found")
    return {"status": "deleted"}