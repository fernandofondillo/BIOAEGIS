"""
Parameters router — gestión dinámica de biomarcadores custom.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.db import get_conn

router = APIRouter(prefix="/api/v1/parameters", tags=["Parameters"])

class CustomParameter(BaseModel):
    name: str          # id técnico: "ldl_cholesterol"
    label: str          # nombre visible: "LDL Colesterol"
    unit: str = ""
    category: str = "custom"
    normal_min: Optional[float] = None
    normal_max: Optional[float] = None

@router.get("/")
async def list_parameters():
    """Lista todos los parámetros (built-in + custom)."""
    conn = get_conn()
    rows = conn.execute("SELECT * FROM custom_parameters ORDER BY category, label").fetchall()
    conn.close()
    return {
        "parameters": [dict(r) for r in rows],
        "builtin_count": 13,
        "custom_count": len(rows),
    }

@router.post("/")
async def add_parameter(p: CustomParameter):
    """Añade un nuevo biomarcador custom."""
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO custom_parameters (name, label, unit, category, normal_min, normal_max) VALUES (?, ?, ?, ?, ?, ?)",
            (p.name, p.label, p.unit, p.category, p.normal_min, p.normal_max),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM custom_parameters WHERE name = ?", (p.name,)).fetchone()
        conn.close()
        return {"status": "added", "parameter": dict(row)}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, f"Parameter '{p.name}' already exists")

@router.delete("/{name}")
async def delete_parameter(name: str):
    """Elimina un biomarcador custom."""
    conn = get_conn()
    cur = conn.execute("DELETE FROM custom_parameters WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(404, f"Parameter '{name}' not found")
    return {"status": "deleted", "name": name}