#!/usr/bin/env python3
"""
BioFish AI — LLM Setup Script
==============================
Configura los proveedores LLM para BioFish AI de forma interactiva.

Uso:
    python3 setup_llm.py
    python3 setup_llm.py --env          # Lee de variables de entorno
    python3 setup_llm.py --groq gsk_...  # Configura Groq directamente
    python3 setup_llm.py --all-in-one   # Auto-detecta todas las keys del environment

Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.llm_client import (
    LLMClient, llm_client, Provider, detect_provider_from_key,
    MODEL_CATALOG, ProviderConfig, ChatMessage, ChatResponse
)


def print_banner():
    print("=" * 55)
    print("  🐟 BioFish AI — LLM Provider Setup")
    print("=" * 55)
    print()
    print("Proveedores soportados:")
    print("  groq       → Gratis, 500K tokens/día, ultrarrápido")
    print("  minimax    → Tu Code Plan MiniMax")
    print("  openrouter → 140+ modelos (OpenAI, Anthropic, Google...)")
    print("  kimi      → Moonshot AI (China)")
    print("  openai    → GPT-4, GPT-4o")
    print("  deepseek  → DeepSeek Chat/Coder (barato)")
    print("  ollama    → Local (no necesita API key)")
    print()


def detect_and_configure_from_env() -> dict:
    """Auto-detecta y configura todos los proveedores desde variables de entorno."""
    print("🔍 Buscando variables de entorno...")

    results = {}
    providers_found = []

    # Priority order
    env_mappings = [
        # (env_var, provider_name, base_url_if_needed)
        ("GROQ_API_KEY", "groq", None),
        ("MINIMAX_API_KEY", "minimax", None),
        ("MULTIMAX_API_KEY", "minimax", "https://api.minimax.io/anthropic"),
        ("OPENROUTER_API_KEY", "openrouter", None),
        ("KIMI_API_KEY", "kimi", None),
        ("OPENAI_API_KEY", "openai", None),
        ("DEEPSEEK_API_KEY", "deepseek", None),
        ("ANTHROPIC_API_KEY", "anthropic", None),
    ]

    for env_var, provider_name, default_url in env_mappings:
        api_key = os.environ.get(env_var)
        if api_key and len(api_key) > 8:
            try:
                config = llm_client.configure(
                    api_key=api_key,
                    provider=provider_name,
                    base_url=default_url,
                    set_as_default=(len(providers_found) == 0),
                )
                results[provider_name] = {
                    "status": "✅ configured",
                    "api_key_suffix": api_key[-4:],
                    "models": len(config.models),
                    "is_default": config.provider == llm_client.default_provider,
                }
                providers_found.append(provider_name)
                print(f"  ✅ {provider_name.upper()}: configurado (key termina en ...{api_key[-4:]})")
            except Exception as e:
                results[provider_name] = {"status": f"❌ error: {e}"}
                print(f"  ❌ {provider_name.upper()}: {e}")

    # Ollama local
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    if os.environ.get("OLLAMA_ENABLED", "").lower() in ["1", "true", "yes"]:
        try:
            config = llm_client.configure(
                api_key="ollama-local",
                provider="ollama",
                base_url=ollama_url,
                set_as_default=False,
            )
            results["ollama"] = {
                "status": "✅ configured",
                "url": ollama_url,
                "is_default": False,
            }
            providers_found.append("ollama")
            print(f"  ✅ OLLAMA: configurado ({ollama_url})")
        except Exception as e:
            results["ollama"] = {"status": f"❌ error: {e}"}

    return results, providers_found


def configure_interactive():
    """Configura proveedores de forma interactiva (para usuarios con keys)."""
    print("\n📝 CONFIGURACIÓN MANUAL")
    print("(Copia y pega tu API key cuando se pida)")
    print()

    configured = []

    # Groq
    groq_key = input("Groq API key (ENTER para saltar): ").strip()
    if groq_key and len(groq_key) > 10:
        try:
            cfg = llm_client.configure(api_key=groq_key, provider="groq")
            configured.append(cfg)
            print(f"  ✅ Groq configurado — models: {len(cfg.models)}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # OpenRouter
    or_key = input("OpenRouter API key (ENTER para saltar): ").strip()
    if or_key and len(or_key) > 10:
        try:
            cfg = llm_client.configure(api_key=or_key, provider="openrouter")
            configured.append(cfg)
            print(f"  ✅ OpenRouter configurado — {len(cfg.models)} modelos")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # MiniMax
    mm_key = input("MiniMax API key (ENTER para saltar): ").strip()
    if mm_key and len(mm_key) > 10:
        try:
            cfg = llm_client.configure(api_key=mm_key, provider="minimax")
            configured.append(cfg)
            print(f"  ✅ MiniMax configurado")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Kimi / Moonshot
    kimi_key = input("Kimi (Moonshot) API key (ENTER para saltar): ").strip()
    if kimi_key and len(kimi_key) > 10:
        try:
            cfg = llm_client.configure(api_key=kimi_key, provider="kimi")
            configured.append(cfg)
            print(f"  ✅ Kimi configurado — {len(cfg.models)} modelos")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # DeepSeek
    ds_key = input("DeepSeek API key (ENTER para saltar): ").strip()
    if ds_key and len(ds_key) > 10:
        try:
            cfg = llm_client.configure(api_key=ds_key, provider="deepseek")
            configured.append(cfg)
            print(f"  ✅ DeepSeek configurado")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Ollama local
    ollama = input("Ollama URL (ENTER para localhost:11434): ").strip()
    ollama = ollama or "http://localhost:11434/v1"
    if ollama:
        try:
            cfg = llm_client.configure(
                api_key="ollama-local",
                provider="ollama",
                base_url=ollama,
                set_as_default=False,
            )
            configured.append(cfg)
            print(f"  ✅ Ollama configurado — {ollama}")
        except Exception as e:
            print(f"  ❌ Ollama: {e}")

    return configured


def test_providers():
    """Hace health check de todos los proveedores configurados."""
    print("\n🧪 HEALTH CHECK")
    print("-" * 40)

    if not llm_client.providers:
        print("  ⚠️  No hay proveedores configurados")
        return

    for prov in llm_client.providers:
        result = llm_client.health_check(provider=prov.value)
        status = result.get("status", "unknown")
        latency = result.get("latency_ms", 0)
        error = result.get("error", "")
        model = result.get("model_used", "")
        emoji = "✅" if status == "healthy" else "❌"
        if status == "healthy":
            print(f"  {emoji} {prov.value.upper()}: OK ({latency:.0f}ms) — {model}")
        else:
            print(f"  {emoji} {prov.value.upper()}: {error or status}")


def generate_env_template():
    """Genera el template de variables de entorno."""
    print("\n📄 TEMPLATE .env para BioFish AI:")
    print("-" * 40)
    template = """# BioFish AI — LLM Configuration
# Copia este archivo a .env y rellena tus API keys

# === PRIORIDAD 1: Groq (GRATIS, rápido) ===
# Consigue tu key en: https://console.groq.com/keys
# Límite: 500K tokens/día gratis
GROQ_API_KEY=tu_key_de_groq_aqui

# === PRIORIDAD 2: MiniMax Code Plan ===
# Tu token Code Plan específico
MINIMAX_API_KEY=sk-cp-...

# === OpenRouter (muchos modelos) ===
# Consigue tu key en: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-...

# === Kimi / Moonshot AI (China) ===
KIMI_API_KEY=tu_key_de_kimi_aqui

# === OpenAI (GPT-4) ===
OPENAI_API_KEY=sk-...

# === DeepSeek (barato) ===
DEEPSEEK_API_KEY=sk-...

# === Ollama local (sin coste) ===
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_ENABLED=false

# === Configuración rápida ===
# Copia todas las keys que tengas y el sistema auto-detectará el mejor modelo
"""
    print(template)


def save_config(path: str = "llm_config.json"):
    """Guarda la configuración de proveedores en un archivo JSON."""
    config_data = {
        "default_provider": llm_client.default_provider.value if llm_client.default_provider else None,
        "providers": {
            p.value: {
                "base_url": cfg.base_url,
                "models": cfg.models,
                "enabled": cfg.enabled,
            }
            for p, cfg in llm_client.providers.items()
        },
    }
    with open(path, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"\n💾 Configuración guardada en {path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="BioFish AI — LLM Provider Setup")
    parser.add_argument("--env", action="store_true", help="Leer keys desde variables de entorno")
    parser.add_argument("--interactive", action="store_true", help="Configuración interactiva")
    parser.add_argument("--groq", help="Configurar Groq directamente")
    parser.add_argument("--minimax", help="Configurar MiniMax directamente")
    parser.add_argument("--openrouter", help="Configurar OpenRouter directamente")
    parser.add_argument("--kimi", help="Configurar Kimi directamente")
    parser.add_argument("--ollama", help="URL de Ollama local")
    parser.add_argument("--all-in-one", action="store_true", help="Auto-detectar todas las keys del environment")
    parser.add_argument("--test", action="store_true", help="Ejecutar health check después de configurar")
    parser.add_argument("--save", action="store_true", help="Guardar config en llm_config.json")
    parser.add_argument("--template", action="store_true", help="Mostrar template de variables de entorno")
    parser.add_argument("--show", action="store_true", help="Mostrar config actual")
    parser.add_argument("--list-models", action="store_true", help="Listar modelos disponibles")

    args = parser.parse_args()

    print_banner()

    if args.template:
        generate_env_template()
        return

    if args.show:
        summary = llm_client.summary()
        print("Configuración actual:")
        print(json.dumps(summary, indent=2))
        return

    if args.list_models:
        print("\n📦 Modelos disponibles por proveedor:")
        print("-" * 50)
        for provider, models in MODEL_CATALOG.items():
            free = [m for m in models if m.is_free]
            print(f"\n  {provider.value.upper()} ({len(models)} modelos, {len(free)} gratuitos):")
            for m in models[:5]:
                cost = "GRATIS" if m.is_free else f"${m.cost_per_1k_input}/1K in"
                print(f"    • {m.id}: {cost} | context: {m.context_window:,}")
            if len(models) > 5:
                print(f"    ... y {len(models)-5} más")
        return

    # Configure providers
    if args.all_in_one or args.env:
        results, found = detect_and_configure_from_env()
        print(f"\n📊 Resumen: {len(found)} proveedores encontrados")
        for p, r in results.items():
            print(f"  {p}: {r['status']}")

    if args.groq:
        try:
            cfg = llm_client.configure(api_key=args.groq, provider="groq")
            print(f"✅ Groq configurado: {len(cfg.models)} modelos")
        except Exception as e:
            print(f"❌ Groq: {e}")

    if args.minimax:
        try:
            cfg = llm_client.configure(api_key=args.minimax, provider="minimax")
            print(f"✅ MiniMax configurado")
        except Exception as e:
            print(f"❌ MiniMax: {e}")

    if args.openrouter:
        try:
            cfg = llm_client.configure(api_key=args.openrouter, provider="openrouter")
            print(f"✅ OpenRouter: {len(cfg.models)} modelos")
        except Exception as e:
            print(f"❌ OpenRouter: {e}")

    if args.kimi:
        try:
            cfg = llm_client.configure(api_key=args.kimi, provider="kimi")
            print(f"✅ Kimi configurado")
        except Exception as e:
            print(f"❌ Kimi: {e}")

    if args.ollama:
        try:
            cfg = llm_client.configure(api_key="ollama-local", provider="ollama", base_url=args.ollama)
            print(f"✅ Ollama: {args.ollama}")
        except Exception as e:
            print(f"❌ Ollama: {e}")

    if args.interactive:
        configure_interactive()

    # If no args, try env variables
    if not any([args.all_in_one, args.env, args.groq, args.minimax,
                args.openrouter, args.kimi, args.ollama, args.interactive]):
        print("📌 Modo automático: buscando keys en environment...")
        results, found = detect_and_configure_from_env()
        if not found:
            print("  ⚠️  No se encontraron API keys en environment.")
            print()
            print("Opciones:")
            print("  python3 setup_llm.py --env              → buscar en vars de entorno")
            print("  python3 setup_llm.py --interactive       → configuración manual")
            print("  python3 setup_llm.py --template          → ver template de .env")
            print("  python3 setup_llm.py --groq <tu_key>   → configurar Groq directo")
            print("  python3 setup_llm.py --all-in-one       → auto-detectar todas las keys")
        else:
            print(f"\n✅ {len(found)} proveedores encontrados")

    if args.test or (llm_client.providers and any([args.all_in_one, args.env, args.groq, args.minimax, args.openrouter, args.kimi, args.ollama, args.interactive])):
        test_providers()

    if args.save:
        save_config()

    # Final summary
    if llm_client.providers:
        print("\n" + "=" * 55)
        print("  🐟 BioFish AI LLM Status")
        print("=" * 55)
        summary = llm_client.summary()
        print(f"  Default: {summary['default_provider']}")
        print(f"  Proveedores configurados: {summary['total_providers']}")
        print(f"  Can call: {'✅ SÍ' if summary['can_call'] else '❌ NO'}")
        print()
        for p in summary["providers"]:
            default_marker = " ← DEFAULT" if p["is_default"] else ""
            model_count = f"({p['models']} models)" if p['configured'] else ""
            print(f"  {'✅' if p['configured'] else '⚠️'}  {p['provider'].upper()} {model_count}{default_marker}")


if __name__ == "__main__":
    main()