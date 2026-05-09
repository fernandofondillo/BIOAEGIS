"""
LLM Provider Manager for BioFish AI.
Manages multiple LLM providers with auto-detection and fallback.
"""
from __future__ import annotations
import os, re, time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class Provider(Enum):
    GROQ = "groq"
    MINIMAX = "minimax"
    OPENROUTER = "openrouter"
    KIMI = "kimi"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: Provider
    context_window: int = 128000
    speed: str = "medium"
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    is_free: bool = False


@dataclass
class ProviderConfig:
    provider: Provider
    name: str
    api_key: str
    base_url: str
    models: List[str]
    enabled: bool = True
    is_default: bool = False

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 8)


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    raw_response: Optional[Dict] = None
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and bool(self.content)


MODEL_CATALOG: Dict[Provider, List[ModelInfo]] = {
    Provider.GROQ: [
        ModelInfo("groq/Llama-3.3-70B-Instruct", "Llama 3.3 70B", Provider.GROQ, context_window=128000, speed="fast", is_free=True),
        ModelInfo("groq/llama-3.1-8b-instruct", "Llama 3.1 8B", Provider.GROQ, context_window=128000, speed="fast", is_free=True),
        ModelInfo("groq/mixtral-8x7b-32768", "Mixtral 8x7B", Provider.GROQ, context_window=32768, speed="fast", is_free=True),
    ],
    Provider.OPENROUTER: [
        ModelInfo("google/gemini-pro-1.5", "Gemini Pro 1.5", Provider.OPENROUTER, context_window=2000000, speed="medium"),
        ModelInfo("openai/gpt-4o-mini", "GPT-4o Mini", Provider.OPENROUTER, context_window=128000, speed="fast"),
        ModelInfo("anthropic/claude-3.5-haiku", "Claude 3.5 Haiku", Provider.OPENROUTER, context_window=200000, speed="fast"),
    ],
    Provider.MINIMAX: [
        ModelInfo("MiniMax-Text-01", "MiniMax Text-01", Provider.MINIMAX, context_window=1000000, speed="medium"),
    ],
    Provider.OPENAI: [
        ModelInfo("gpt-4o-mini", "GPT-4o Mini", Provider.OPENAI, context_window=128000, speed="fast"),
        ModelInfo("gpt-4o", "GPT-4o", Provider.OPENAI, context_window=128000, speed="medium"),
    ],
    Provider.DEEPSEEK: [
        ModelInfo("deepseek-chat", "DeepSeek Chat", Provider.DEEPSEEK, context_window=64000, speed="fast"),
    ],
    Provider.OLLAMA: [
        ModelInfo("llama3", "Llama 3 (Ollama)", Provider.OLLAMA, context_window=8192, speed="medium"),
    ],
}


KEY_PATTERNS = [
    (r"^gsk_", Provider.GROQ, "https://api.groq.com/openai/v1"),
    (r"^sk-cp-", Provider.MINIMAX, "https://api.minimax.io/anthropic"),
    (r"^sk-or-", Provider.OPENROUTER, "https://openrouter.ai/api/v1"),
    (r"^sk-ant-", Provider.ANTHROPIC, "https://api.anthropic.com"),
    (r"^sk-", Provider.OPENAI, "https://api.openai.com/v1"),
    (r"^ollama:", Provider.OLLAMA, "http://localhost:11434/v1"),
]


def detect_provider(key: str, base_url: str = "") -> Optional[ProviderConfig]:
    if not key or len(key) < 8:
        return None
    if base_url:
        lu = base_url.lower()
        if "groq" in lu: return make_config(Provider.GROQ, key)
        if "minimax" in lu: return make_config(Provider.MINIMAX, key)
        if "openrouter" in lu: return make_config(Provider.OPENROUTER, key)
        if "openai" in lu: return make_config(Provider.OPENAI, key)
        if "anthropic" in lu: return make_config(Provider.ANTHROPIC, key)
        if "deepseek" in lu: return make_config(Provider.DEEPSEEK, key)
        if "ollama" in lu or "localhost" in lu: return make_config(Provider.OLLAMA, key, base_url)
    for pat, prov, url in KEY_PATTERNS:
        if re.match(pat, key):
            return make_config(prov, key, url)
    return None


def make_config(prov: Provider, key: str, url: str = "") -> ProviderConfig:
    models = [m.id for m in MODEL_CATALOG.get(prov, [])]
    default_urls = {
        Provider.GROQ: "https://api.groq.com/openai/v1",
        Provider.MINIMAX: "https://api.minimax.io/anthropic",
        Provider.OPENROUTER: "https://openrouter.ai/api/v1",
        Provider.OPENAI: "https://api.openai.com/v1",
        Provider.ANTHROPIC: "https://api.anthropic.com",
        Provider.DEEPSEEK: "https://api.deepseek.com",
        Provider.KIMI: "https://api.moonshot.cn/v1",
        Provider.OLLAMA: "http://localhost:11434/v1",
    }
    return ProviderConfig(
        provider=prov,
        name=prov.value.upper(),
        api_key=key,
        base_url=url or default_urls.get(prov, ""),
        models=models,
        enabled=True,
    )


class LLMClient:
    def __init__(self):
        self._providers: Dict[Provider, ProviderConfig] = {}
        self._default: Optional[Provider] = None
        self._timeout = 60.0

    def configure(self, api_key: str, provider: str = "", base_url: str = "") -> ProviderConfig:
        cfg = detect_provider(api_key, base_url)
        if not cfg:
            raise ValueError("No se pudo detectar el proveedor desde la key.")
        self._providers[cfg.provider] = cfg
        if self._default is None:
            self._default = cfg.provider
        return cfg

    def configure_multi(self, **keys) -> Dict[str, ProviderConfig]:
        results = {}
        for name, key in keys.items():
            if key:
                try:
                    cfg = self.configure(api_key=key, provider=name.lower())
                    results[name.lower()] = cfg
                except Exception:
                    pass
        return results

    def configure_from_env(self, prefix: str = "BIOFISH_") -> List[ProviderConfig]:
        configured = []
        env_map = [
            ("GROQ_API_KEY", "groq"),
            ("MINIMAX_API_KEY", "minimax"),
            ("OPENROUTER_API_KEY", "openrouter"),
            ("OPENAI_API_KEY", "openai"),
            ("DEEPSEEK_API_KEY", "deepseek"),
        ]
        for env_name, prov_name in env_map:
            key = os.environ.get(env_name) or os.environ.get(prefix + env_name)
            if key and len(key) > 8:
                try:
                    cfg = self.configure(api_key=key, provider=prov_name)
                    configured.append(cfg)
                except Exception:
                    pass
        return configured

    @property
    def providers(self) -> Dict[Provider, ProviderConfig]:
        return self._providers

    @property
    def default_provider(self) -> Optional[Provider]:
        return self._default

    def get_default_config(self) -> Optional[ProviderConfig]:
        if self._default:
            return self._providers.get(self._default)
        if self._providers:
            return list(self._providers.values())[0]
        return None

    def get_model_for_task(self, task: str = "general") -> str:
        if Provider.GROQ in self._providers:
            return "Llama-3.3-70B-Instruct"
        if Provider.DEEPSEEK in self._providers:
            return "deepseek-chat"
        cfg = self.get_default_config()
        return cfg.models[0] if cfg and cfg.models else "gpt-4o-mini"

    def list_providers(self) -> List[Dict]:
        return [
            {"provider": p.value, "configured": c.is_configured,
             "models": len(c.models), "is_default": p == self._default,
             "base_url": c.base_url}
            for p, c in self._providers.items()
        ]

    def health_check(self, provider: Optional[str] = None) -> Dict:
        if provider:
            try:
                p = Provider(provider.lower())
            except ValueError:
                return {"error": f"Unknown provider: {provider}"}
        else:
            p = self._default
        if not p or p not in self._providers:
            return {"error": "No provider configured"}
        cfg = self._providers[p]
        if not cfg.is_configured:
            return {"provider": p.value, "status": "not_configured"}
        return {"provider": p.value, "status": "ready", "base_url": cfg.base_url}

    def summary(self) -> Dict:
        cfg = self.get_default_config()
        return {
            "default_provider": cfg.provider.value if cfg else None,
            "configured_providers": [p.value for p in self._providers],
            "total_providers": len(self._providers),
            "can_call": cfg is not None and cfg.is_configured,
            "providers": self.list_providers(),
        }

    def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs,
    ) -> ChatResponse:
        if not messages:
            return ChatResponse(content="", model="", provider="", error="No messages")
        target = self._default
        if provider:
            try:
                target = Provider(provider.lower().strip())
            except ValueError:
                return ChatResponse(content="", model="", provider="", error=f"Unknown: {provider}")
        if not target or target not in self._providers:
            return ChatResponse(content="", model="", provider="",
                               error="No provider configured. Call configure() first.")
        cfg = self._providers[target]
        if not cfg.is_configured:
            return ChatResponse(content="", model="", provider=target.value,
                               error="API key not set for this provider")
        return self._call_openai_compat(cfg, model or cfg.models[0] if cfg.models else "unknown",
                                       messages, temperature, max_tokens)

    def _call_openai_compat(
        self, config: ProviderConfig, model: str,
        messages: List[ChatMessage], temperature: float, max_tokens: int,
    ) -> ChatResponse:
        start = time.time()
        if not HAS_HTTPX:
            return ChatResponse(content="", model=model, provider=config.provider.value,
                               error="httpx required: pip install httpx")
        headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
        if config.provider == Provider.OPENROUTER:
            headers["HTTP-Referer"] = "https://biofish.ai"
            headers["X-Title"] = "BioFish AI"
        payload = {
            "model": model, "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature, "max_tokens": max_tokens,
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(
                    f"{config.base_url.rstrip('/')}/chat/completions",
                    headers=headers, json=payload, timeout=self._timeout,
                )
                latency = (time.time() - start) * 1000
                if resp.status_code != 200:
                    try:
                        err = resp.json().get("error", {})
                        msg = err.get("message") or resp.text[:200]
                    except Exception:
                        msg = resp.text[:200]
                    return ChatResponse(content="", model=model, provider=config.provider.value,
                                       latency_ms=latency, error=f"HTTP {resp.status_code}: {msg}")
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                return ChatResponse(
                    content=choice.get("message", {}).get("content", ""),
                    model=data.get("model", model),
                    provider=config.provider.value,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    latency_ms=latency,
                    finish_reason=choice.get("finish_reason", "stop"),
                    raw_response=data,
                )
        except Exception as e:
            return ChatResponse(content="", model=model, provider=config.provider.value,
                               latency_ms=(time.time()-start)*1000, error=str(e))


llm_client = LLMClient()
