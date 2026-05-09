"""
LLM routes — Endpoints para gestión de proveedores LLM en BioFish AI.
Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.llm_client import (
    llm_client, LLMClient, Provider, ChatMessage, ChatResponse,
    MODEL_CATALOG, detect_provider_from_key, ProviderConfig
)
from src.agent_llm import agent_llm, AgentLLM


router = APIRouter(prefix="/llm", tags=["LLM Providers"])


# ── REQUEST / RESPONSE MODELS ────────────────────────────────────────────

class ConfigureProviderRequest(BaseModel):
    api_key: str = Field(..., min_length=8, description="API key del proveedor")
    provider: Optional[str] = Field(None, description="Nombre del proveedor (groq, minimax, openrouter, kimi, openai, deepseek, ollama). Si es None → auto-detecta")
    base_url: Optional[str] = Field(None, description="URL base de la API (solo si el proveedor no es auto-detectable)")
    set_as_default: bool = Field(True, description="Hacer este proveedor el default")


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "..."}]
    model: Optional[str] = Field(None, description="Modelo a usar (ej: 'groq/llama-3.3-70b-instruct')")
    provider: Optional[str] = Field(None, description="Proveedor específico")
    temperature: float = Field(0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(2048, ge=1, le=32768)


class AgentThinkRequest(BaseModel):
    agent_id: str = Field(..., description="ID del agente biológico (ej: 'cardiovascular', 'metabolic')")
    biomarkers: Dict[str, float]
    incoming_signals: List[Dict] = Field(default_factory=list)
    intervention: Optional[str] = None
    tick: int = 0
    force_model: Optional[str] = None


# ── ENDPOINTS ───────────────────────────────────────────────────────────

@router.get("/")
def llm_status():
    """Estado del sistema LLM."""
    return llm_client.summary()


@router.get("/providers")
def list_providers():
    """Lista todos los proveedores configurados."""
    return {"providers": llm_client.list_providers()}


@router.get("/models")
def list_all_models():
    """Lista todos los modelos disponibles por proveedor."""
    result = {}
    for provider, models in MODEL_CATALOG.items():
        result[provider.value] = [
            {
                "id": m.id,
                "name": m.name,
                "context_window": m.context_window,
                "speed": m.speed,
                "is_free": m.is_free,
                "cost_per_1k_input": m.cost_per_1k_input,
                "cost_per_1k_output": m.cost_per_1k_output,
                "daily_limit": m.daily_limit,
            }
            for m in models
        ]
    return {"catalog": result}


@router.post("/configure")
def configure_provider(req: ConfigureProviderRequest):
    """Configura un proveedor LLM."""
    try:
        config = llm_client.configure(
            api_key=req.api_key,
            provider=req.provider,
            base_url=req.base_url,
            set_as_default=req.set_as_default,
        )
        return {
            "status": "configured",
            "provider": config.provider.value,
            "models_count": len(config.models),
            "is_default": config.provider == llm_client.default_provider,
            "base_url": config.base_url,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/configure/multi")
def configure_multi(keys: Dict[str, Optional[str]]):
    """Configura múltiples proveedores a la vez."""
    results = {}
    for prov_name, key in keys.items():
        if key and len(key) > 8:
            try:
                cfg = llm_client.configure(api_key=key, provider=prov_name, set_as_default=False)
                results[prov_name] = {"status": "✅", "models": len(cfg.models)}
            except Exception as e:
                results[prov_name] = {"status": f"❌ {e}"}
    return {"results": results}


@router.post("/configure/from-env")
def configure_from_env():
    """Auto-detecta y configura proveedores desde variables de entorno."""
    configured = llm_client.configure_from_env(env_prefix="BIOFISH_")
    return {
        "status": "done",
        "configured_count": len(configured),
        "providers": [c.provider.value for c in configured],
    }


@router.get("/health")
def health_check(provider: Optional[str] = None):
    """Health check de uno o todos los proveedores."""
    if provider:
        return llm_client.health_check(provider=provider)
    else:
        results = {}
        for p in llm_client.providers:
            results[p.value] = llm_client.health_check(provider=p.value)
        return {"providers": results}


@router.post("/chat")
def chat(req: ChatRequest):
    """Envía un mensaje de chat a través del proveedor configurado."""
    messages = [ChatMessage(role=m["role"], content=m["content"]) for m in req.messages]
    response = llm_client.chat(
        messages=messages,
        model=req.model,
        provider=req.provider,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )
    return {
        "success": response.success,
        "content": response.content,
        "model": response.model,
        "provider": response.provider,
        "tokens_used": response.tokens_used,
        "latency_ms": round(response.latency_ms, 1),
        "finish_reason": response.finish_reason,
        "error": response.error,
    }


@router.post("/agents/think")
def agent_think(req: AgentThinkRequest):
    """Hace pensar a un agente biológico con LLM."""
    result = agent_llm.think(
        agent_id=req.agent_id,
        user_biomarkers=req.biomarkers,
        incoming_signals=req.incoming_signals,
        intervention=req.intervention,
        tick=req.tick,
        force_model=req.force_model,
    )
    return result.to_dict()


@router.post("/agents/think/batch")
def agent_think_batch(requests: List[AgentThinkRequest]):
    """Hace pensar a múltiples agentes consecutivamente."""
    results = []
    for req in requests:
        result = agent_llm.think(
            agent_id=req.agent_id,
            user_biomarkers=req.biomarkers,
            incoming_signals=req.incoming_signals,
            intervention=req.intervention,
            tick=req.tick,
            force_model=req.force_model,
        )
        results.append(result.to_dict())
    return {"results": results}


@router.get("/models/best/{task}")
def best_model_for_task(task: str):
    """Sugiere el mejor modelo para una tarea."""
    model = llm_client.get_model_for_task(task)
    return {
        "task": task,
        "recommended_model": model,
        "default_provider": llm_client.default_provider.value if llm_client.default_provider else None,
    }


@router.post("/providers/detect")
def detect_provider(api_key: str, base_url: Optional[str] = None):
    """Detecta el proveedor desde el formato de la API key."""
    if base_url:
        config = detect_provider_from_key_with_url(api_key, base_url)
    else:
        config = detect_provider_from_key(api_key)

    if config:
        return {
            "detected": True,
            "provider": config.provider.value,
            "base_url": config.base_url,
            "models_count": len(config.models),
        }
    return {"detected": False, "error": "Could not detect provider from key format"}