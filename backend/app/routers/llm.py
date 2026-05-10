"""
LLM Router — Gestión de API keys y estado de providers LLM.
Lee la key desde ~/.fenix/providers.toml o variable de entorno.
"""
from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])

GROQ_DEFAULT_MODELS = [
    {"id": "Llama-3.3-70B-Instruct", "name": "Llama 3.3 70B", "context": 128000, "free": True},
    {"id": "Llama-3.1-8B-Instruct",  "name": "Llama 3.1 8B",  "context": 128000, "free": True},
    {"id": "Mixtral-8x7B-32768",     "name": "Mixtral 8x7B",   "context": 32768,  "free": True},
]

def get_api_key() -> str:
    """Busca API key en ~/.fenix/providers.toml o variable de entorno."""
    path = os.path.expanduser("~/.fenix/providers.toml")
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("GROQ_API_KEY="):
                return line.split("=",1)[1].strip()
            if line.startswith("MINIMAX_API_KEY="):
                return line.split("=",1)[1].strip()
    return os.environ.get("GROQ_API_KEY", os.environ.get("MINIMAX_API_KEY", ""))

@router.get("/status")
async def llm_status():
    """Estado actual del proveedor LLM."""
    key = get_api_key()
    has_key = bool(key and len(key) > 10)
    key_preview = key[:6] + "..." if has_key else "NO CONFIGURADA"
    return {
        "provider": "groq",
        "api_key": key_preview,
        "configured": has_key,
        "models": GROQ_DEFAULT_MODELS,
        "docs_url": "https://console.groq.com/keys",
    }

@router.post("/test")
async def llm_test():
    """Prueba de conexión con Groq."""
    import httpx
    key = get_api_key()
    if not key or len(key) < 10:
        return {"success": False, "error": "No hay API key configurada"}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "Llama-3.3-70B-Instruct", "messages": [{"role": "user", "content": "Di hola en una palabra"}], "max_tokens": 5},
            )
            data = r.json()
            if "choices" in data:
                return {"success": True, "response": data["choices"][0]["message"]["content"]}
            return {"success": False, "error": data.get("error", {}).get("message", str(data)[:100])}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/models")
async def list_models():
    return {"models": GROQ_DEFAULT_MODELS}
