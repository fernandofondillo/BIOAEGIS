"""
Tests para el LLM Provider Manager.
CLOUDWATCH: Solo testa la lógica de detección y configuración.
No hace llamadas reales a las APIs.
"""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.llm_client import (
    detect_provider_from_key, detect_provider_from_key_with_url,
    Provider, LLMClient, ModelInfo, MODEL_CATALOG,
)


class TestProviderDetection:
    """Tests de auto-detección de proveedores desde API key."""

    def test_groq_key_detected(self):
        cfg = detect_provider_from_key("gsk_abc1234567890abcdef")
        assert cfg is not None
        assert cfg.provider == Provider.GROQ
        assert "groq" in cfg.base_url

    def test_minimax_codeplan_detected(self):
        cfg = detect_provider_from_key("sk-cp-minimax123456789abcdef")
        assert cfg is not None
        assert cfg.provider == Provider.MINIMAX

    def test_openai_key_detected(self):
        cfg = detect_provider_from_key("sk-OpenAIabcdef12345678901234567890")
        assert cfg is not None
        assert cfg.provider in [Provider.OPENAI, Provider.MINIMAX]

    def test_deepseek_key_detected(self):
        cfg = detect_provider_from_key("sk-" + "a" * 48)
        assert cfg is not None
        assert cfg.provider == Provider.DEEPSEEK

    def test_kimi_key_detected(self):
        cfg = detect_provider_from_key("sk-" + "x" * 32)
        assert cfg is not None
        assert cfg.provider == Provider.KIMI

    def test_empty_key_returns_none(self):
        assert detect_provider_from_key("") is None
        assert detect_provider_from_key("abc") is None

    def test_detect_with_url_groq(self):
        cfg = detect_provider_from_key_with_url(
            "gsk_test", "https://api.groq.com/openai/v1"
        )
        assert cfg is not None
        assert cfg.provider == Provider.GROQ

    def test_detect_with_url_openrouter(self):
        cfg = detect_provider_from_key_with_url(
            "sk-or-test", "https://openrouter.ai/api/v1"
        )
        assert cfg is not None
        assert cfg.provider == Provider.OPENROUTER


class TestLLMClientConfiguration:
    """Tests de configuración de proveedores."""

    def test_configure_groq_direct(self):
        client = LLMClient()
        cfg = client.configure(api_key="gsk_test_key_1234567890", provider="groq")
        assert cfg.provider == Provider.GROQ
        assert len(cfg.models) > 0

    def test_configure_minimax_direct(self):
        client = LLMClient()
        cfg = client.configure(api_key="sk-cp-minimax123456789", provider="minimax")
        assert cfg.provider == Provider.MINIMAX

    def test_configure_auto_detect(self):
        client = LLMClient()
        cfg = client.configure(api_key="gsk_abc123", set_as_default=True)
        assert cfg.provider == Provider.GROQ
        assert client.default_provider == Provider.GROQ

    def test_configure_sets_default(self):
        client = LLMClient()
        client.configure(api_key="gsk_first", provider="groq")
        client.configure(api_key="sk-cp-second", provider="minimax", set_as_default=True)
        assert client.default_provider == Provider.MINIMAX

    def test_configure_multi(self):
        client = LLMClient()
        results = client.configure_multi(
            groq_key="gsk_groq_test_123456789",
            deepseek_key="sk-" + "d" * 48,
        )
        assert "groq" in results
        assert "deepseek" in results
        assert client.default_provider in [Provider.GROQ, Provider.DEEPSEEK]

    def test_unknown_provider_raises(self):
        client = LLMClient()
        with pytest.raises(ValueError, match="unknown provider"):
            client.configure(api_key="test", provider="nonexistent")

    def test_invalid_key_raises(self):
        client = LLMClient()
        with pytest.raises(ValueError, match="auto-detect"):
            client.configure(api_key="x", provider=None)


class TestLLMClientStatus:
    """Tests del estado del sistema."""

    def test_summary_empty(self):
        client = LLMClient()
        summary = client.summary()
        assert summary["total_providers"] == 0
        assert summary["can_call"] is False

    def test_summary_after_config(self):
        client = LLMClient()
        client.configure(api_key="gsk_test_groq_key", provider="groq")
        summary = client.summary()
        assert summary["total_providers"] == 1
        assert summary["can_call"] is True

    def test_list_providers_empty(self):
        client = LLMClient()
        assert client.list_providers() == []

    def test_list_providers_after_config(self):
        client = LLMClient()
        client.configure(api_key="gsk_test_key", provider="groq")
        providers = client.list_providers()
        assert len(providers) == 1
        assert providers[0]["provider"] == "groq"


class TestModelCatalog:
    """Tests del catálogo de modelos."""

    def test_groq_has_free_models(self):
        models = MODEL_CATALOG.get(Provider.GROQ, [])
        assert len(models) > 0
        free_models = [m for m in models if m.is_free]
        assert len(free_models) > 0

    def test_all_providers_have_models(self):
        for provider, models in MODEL_CATALOG.items():
            assert len(models) > 0, f"{provider} has no models"

    def test_model_info_attributes(self):
        models = MODEL_CATALOG.get(Provider.GROQ, [])
        model = models[0]
        assert hasattr(model, "id")
        assert hasattr(model, "name")
        assert hasattr(model, "context_window")
        assert hasattr(model, "speed")
        assert hasattr(model, "is_free")


class TestGetModelForTask:
    """Tests de selección de modelo por tarea."""

    def test_groq_selected_when_available(self):
        client = LLMClient()
        client.configure(api_key="gsk_test_key", provider="groq")
        model = client.get_model_for_task("medical_reasoning")
        assert "groq" in model or "llama" in model

    def test_fallback_to_deepseek(self):
        client = LLMClient()
        client.configure(api_key="sk-" + "d" * 48, provider="deepseek")
        model = client.get_model_for_task("analysis")
        assert len(model) > 0

    def test_no_provider_returns_any_model(self):
        client = LLMClient()
        # No provider configured — returns a model string
        model = client.get_model_for_task("general")
        assert isinstance(model, str)
        assert len(model) > 0