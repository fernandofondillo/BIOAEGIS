# 🐟 BioFish AI

> **Biological Swarm Intelligence** — Simulador multi-agente del organismo humano.
> 18 agentes biológicos especializados + Dr. Hallmarks (Longevidad) + Dr. Mechanism (Biología Molecular) + Moderator (Consenso Médico).
> Inspirado en [MiroFish AI](https://github.com/666ghj/MiroFish) (110K+ GitHub stars), adaptado para salud y longevidad.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/fernandofondillo/BIOFISH-AI)](https://github.com/fernandofondillo/BIOFISH-AI/stargazers)
[![Issues](https://img.shields.io/github/issues/fernandofondillo/BIOFISH-AI)](https://github.com/fernandofondillo/BIOFISH-AI/issues)

---

## 🤖 Qué es BioFish AI

BioFish AI simula el **cuerpo humano como una red de 18 agentes biológicos especializados** que se comunican entre ellos mediante señales bioquímicas. Cada agente razona como un médico especialista real — cardiólogos, endocrinólogos, inmuno-ólogos — basándose en tus analíticas de sangre y estilo de vida.

**A diferencia de un chatbot médico genérico**, BioFish AI:

- ✅Tiene **18 agentes especializados** trabajando en equipo
- ✅ Los agentes **se comunican entre ellos** (señal busbioquímico)
- ✅ Un **Moderator con 2 expertos validadores** elimina alucinaciones
- ✅ **Relojes biológicos reales** (PhenoAge, DunedinPACE, Zhang Age, Lifestyle)
- ✅ **Simulador de intervenciones** con efectos mensualizados basados en evidencia
- ✅ Respeta **límites biológicos** (Hard Constraints DB — 80+ biomarcadores)
- ✅ Funciona **con o sin LLM** (modo determinista fallback)

---

## 🧠 Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────┐
│                     USER DATA                           │
│     (sangre, estilo de vida, analíticas)               │
└──────────────────────┬────────────────────────────────┘
                       │
┌─────────────────────▼────────────────────────────────┐
│            LLM PROVIDER MANAGER                         │
│  Auto-detecta: Groq · MiniMax · OpenRouter · Kimi ·    │
│  DeepSeek · Ollama local · OpenAI · Anthropic          │
└──────────────────────┬────────────────────────────────┘
                       │
┌─────────────────────▼────────────────────────────────┐
│         18 BIOLOGICAL AGENTS (LLM-Powered)              │
│                                                         │
│  Cardiovascular  ·  Metabolic  ·  Inflammatory  ·        │
│  Molecular  ·  Epigenetic  ·  Hepatic  ·  Renal  ·     │
│  Cognitive  ·  Endocrine  ·  Muscular  ·  Immune  ·    │
│  Adipose  ·  Metabolic Flexibility  ·  Insulin Sens.  │
│  Sports Performance  ·  Nutritional Timing  ·        │
│  Sleep & Recovery  ·  Oxidative Stress                 │
│         ↓ (Signal Bus — 36 señales inter-agente)        │
│         ↕                                             │
│  🩺 MODERATOR AGENT                                    │
│  ├── Dr. Hallmarks (12 hallmarks + evidencia A/B/C)    │
│  ├── Dr. Mechanism (validación mecanística)            │
│  └── Consensus Engine (requiere acuerdo de ≥3 agentes)│
└──────────────────────┬────────────────────────────────┘
                       │
┌─────────────────────▼────────────────────────────────┐
│         VALIDATION LAYERS (Anti-alucinaciones)           │
│                                                         │
│  Hard Constraints DB  ─ 80+ límites biológicos            │
│  BioFacts DB        ─ Papers peer-reviewed             │
│  Signal Bus         ─ Señales validadas                │
└──────────────────────┬────────────────────────────────┘
                       │
┌─────────────────────▼────────────────────────────────┐
│         OUTPUTS                                          │
│                                                         │
│  🏥 Recomendación médica con nivel de evidencia        │
│  📊 Biological clocks (PhenoAge · Zhang · DunedinPACE) │
│  📈 Trayectoria proyectada a 6/12/36 meses              │
│  🧬 Intervención simulada con efectos mensualizados    │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ Demo rápida

```python
from src.orchestrator import orchestrator
from src.llm_client import llm_client

# 1. Configura tu LLM (Groq gratis, MiniMax, OpenRouter...)
llm_client.configure(api_key="gsk_tu_key", provider="groq")

# 2. Inicializa con los datos del paciente
orchestrator.initialize_user({
    "chronological_age": 40, "sex": "male",
    "ldl_cholesterol": 155, "hdl_cholesterol": 42,
    "homa_ir": 3.2, "c_reactive_protein": 3.5,
    "vo2max": 32, "sleep_hours": 6,
    # ... 40+ biomarcadores
})

# 3. Simula una intervención (ej: ayuno 16:8 durante 6 meses)
result = orchestrator.run_tick(
    tick=6,
    intervention="ayuno_intermitente_16_8"
)

print(result.ensemble_summary["ensemble_biological_age"])
# → 43.2 años (era 45.6, mejoró -2.4 años en 6 meses)

print(result.moderator_output.to_user_friendly())
# ✅ RECOMENDACIÓN DEL EQUIPO MÉDICO
# El equipo recomienda: Ayuno Intermitente 16:8
# Nivel de evidencia: A (Meta-análisis de RCTs)
# Agentes consultados: cardiovascular, metabolic, inflammatory...
```

---

## 🚀 Quick Start

### Opción 1: Docker (recomendado)

```bash
git clone https://github.com/fernandofondillo/BIOFISH-AI.git
cd BIOFISH-AI

# Configura tus API keys
cp .env.example .env
# Edita .env con tus keys

docker compose up -d
# API docs → http://localhost:8000/docs
```

### Opción 2: Local (Python 3.11+)

```bash
git clone https://github.com/fernandofondillo/BIOFISH-AI.git
cd BIOFISH-AI

pip install -r requirements.txt

# Configura tu LLM (Groq gratis — 500K tokens/día)
export GROQ_API_KEY=gsk_tu_key

python3 setup_llm.py --test        # Verifica conectividad
python3 test_system.py             # Test completo del sistema

cd api && uvicorn main:app --port 8000 --reload
```

---

## 🔑 Configuración de proveedores LLM

BioFish AI auto-detecta el proveedor desde el formato de tu API key:

| API key empieza con | Proveedor | Coste | Límite |
|---|---|---|---|
| `gsk_` | **Groq** ⭐ | **Gratis** | 500K tokens/día |
| `sk-cp-` | **MiniMax** | Tu Code Plan | Tu plan |
| `sk-or-` | **OpenRouter** | $0.0001-0.5/1K | Tu crédito |
| `sk-` (48 hex) | **DeepSeek** | **Barato** | Rate limited |
| `moonshot-` | **Kimi/Moonshot** | Medio | China |
| `sk-ant-` | **Anthropic** | $0.003-0.015/1K | Tu crédito |
| `ollama:` | **Ollama local** | **Gratis** | Ilimitado |

```bash
# Ejemplo: Groq (gratis, ultra-rápido)
export GROQ_API_KEY=gsk_abc123456789

# Ejemplo: MiniMax Code Plan
export MINIMAX_API_KEY=sk-cp-minimax123456

# Ejemplo: múltiples proveedores (fallback automático)
export GROQ_API_KEY=gsk_...
export MINIMAX_API_KEY=sk-cp-...
export OPENROUTER_API_KEY=sk-or-...

# El sistema usa Groq por defecto; si falla, prueba MiniMax, etc.
```

---

## 📡 API Endpoints

Documentación completa en `http://localhost:8000/docs` (Swagger UI).

### Simulation
```
POST /init                    Inicializa usuario con biomarcadores
POST /simulate                 Ejecuta 1 tick de simulación
POST /simulate/trajectory     Simula trayectoria a N meses
```

### Biological Clocks
```
POST /clocks                   Calcula PhenoAge + Zhang + DunedinPACE + Lifestyle
```

### Interventions
```
GET  /interventions            Lista las 8 intervenciones disponibles
POST /interventions/simulate   Proyecta efectos de 1 intervención
POST /interventions/compare     Compara 2+ intervenciones sobre 1 biomarcador
```

### Agents
```
GET  /agents                   Lista los 18 perfiles de agentes
GET  /agents/{id}              Perfil detallado de 1 agente
POST /agents/llm/think         Un agente razona con LLM
POST /agents/llm/think/batch   Múltiples agentes reasoning
POST /agents/llm/simulate     Workflow completo: agentes + Moderator
```

### LLM Providers
```
GET  /llm/                    Estado del sistema LLM
POST /llm/configure            Configura un proveedor
POST /llm/configure/multi      Configura varios a la vez
POST /llm/configure/from-env   Auto-detecta desde variables de entorno
GET  /llm/health              Health check de proveedores
POST /llm/chat                Chat directo con cualquier modelo
```

---

## 🧬 Los 18 Agentes Biológicos

### Core Systems (12)
| Agente | Rol | Señales que emite |
|---|---|---|
| ❤️ Cardiovascular | Cardiólogo — riesgo aterosclerótico | VASCULAR_STRESS, CARDIO_PROTECT |
| 🩸 Metabolic | Endocrinólogo — glucosa/insulina | INSULIN_RESISTANCE, GLUCOSE_SPIKE |
| 🔥 Inflammatory | Inmunólogo — inflamación crónica | PRO_INFLAM, ANTI_INFLAM |
| ⚛️ Molecular | Biólogo molecular — AMPK/mTOR/NAD+ | LONGEVITY_SIGNAL, ANABOLIC_STATE |
| 🧬 Epigenetic | Epigenetista — relojes epigenéticos | AGING_ACCEL, DNA_REPAIR |
| 🟢 Hepatic | Hepatólogo — función hepática | LIVER_STRESS, NAFLD_ALERT |
| 💧 Renal | Nefrólogo — función renal | KIDNEY_STRESS, ELECTROLYTE_IMBALANCE |
| 🧠 Cognitive | Neurólogo — función cognitiva | COGNITIVE_SUPPORT, NEURO_INFLAM |
| ⚖️ Endocrine | Endocrinólogo — eje hormonal | HORMONAL_STRESS, THYROID_ALERT |
| 💪 Muscular | Fisiólogo — masa muscular | MUSCLE_PROTECT, SARCOPENIA_RISK |
| 🛡️ Immune | Inmunólogo — sistema inmune | IMMUNE_ACTIVATE, IMMUNE_EXHAUSTION |
| ⚪ Adipose | Especialista — tejido adiposo | VISCERAL_FAT_ALERT, LIPOTOXICITY |

### Specialists (6)
| Agente | Rol | Añadido por |
|---|---|---|
| 🔄 Metabolic Flexibility | Flexibilidad metabólica (glucosa ↔ grasa) | Meta-bolismo |
| 🎯 Insulin Sensitivity | Resistencia periférica a insulina | Meta-bolismo |
| 🏃 Sports Performance | VO2max, sobreentrenamiento | Rendimiento |
| 🍽️ Nutritional Timing | Timing nutricional y circadiano | Nutrición |
| 🌙 Sleep & Recovery | HRV, arquitectura del sueño | Recuperación |
| 🧪 Oxidative Stress | Balance ROS/antioxidantes | Oxidativo |

---

## 🏥 El Moderator — Director Médico

El Moderator es el **Chief Medical Officer** del equipo. No es un agente más — es el validador que filtra las salidas de los 18 agentes antes de presentar resultados al usuario:

### Dr. Hallmarks (Longevidad)
- Valida que las intervenciones tengan **evidencia en humanos** (no solo modelos animales)
- Clasifica por **nivel de evidencia A/B/C**
- Detecta intervenciones sin soporte científico

### Dr. Mechanism (Biología Molecular)
- Detecta errores mecanísticos: *"bloquear mTOR completamente"* → biológicamente imposible
- Valida la **plausibilidad biológica** de cada claim
- Detecta claims que contradicen la fisiología conocida

### Consensus Engine
- Requiere acuerdo de **3+ agentes** antes de recomendaciones críticas
- El nivel de evidencia sube si múltiples agentes concuerdan
- Si hay contradicción → se presenta la discrepancia al usuario

### Hard Constraints DB
- **80+ límites biológicos** inviolables (LDL 0-400mg/dL, Glucosa 40-400mg/dL...)
- Cualquier output fuera de rango → **rechazado automáticamente**
- El LLM no puede inventar valores imposibles

---

## ⏱️ Relojes Biológicos

| Reloj | Paper | Qué mide |
|---|---|---|
| **PhenoAge** | Levine 2018, PNAS | Edad fenotípica (9 biomarcadores) |
| **Zhang Age** | Zhang 2020, Nat. Aging | Envejecimiento funcional (16 biomarcadores) |
| **DunedinPACE** | Belsky 2022, eLife | **Velocidad** de envejecimiento ⚡ |
| **Lifestyle Age** | Meta-análisis propio | Impacto del estilo de vida |

DunedinPACE es el más innovador: mide **cuánto estás envejeciendo por año cronológico**:
- 1.0 = ritmo promedio
- 1.5 = envejeces 50% más rápido
- 0.7 = envejeces 30% más lento (como centenario)

---

## 💊 Intervenciones (8 con evidencia)

| Intervención | Evidencia | Efectos principales |
|---|---|---|
| **Ejercicio Aeróbico 150min/sem** | 🟢 Level A | ↓ mortalidad 20-35%, ↑ VO2max, ↓ PCR |
| **HIIT 3x/semana** | 🟢 Level A | ↑ VO2max 15-30%, ↓ HOMA-IR |
| **Ayuno Intermitente 16:8** | 🟢 Level A | ↓ HOMA-IR 10-25%, ↓ inflamación |
| **Dieta Mediterránea + AOVE** | 🟢 Level A | ↓ eventos CV 30% (PREDIMED) |
| **Omega-3 EPA+DHA 2g/día** | 🟢 Level A | ↓ triglicéridos 15-30% |
| **Ejercicio de Fuerza 3x/sem** | 🟢 Level A | ↑ masa muscular, ↑ densidad ósea |
| **Metformina 850mg x2/día** | 🟢 Level A | ↓ HbA1c 0.5-1.5%, ↓ progresión a diabetes 31% |
| **Plan Combinado (todo junto)** | 🟢 Level A | Efectos sinérgicos máx. |

---

## 🔬 Validación científica

Todos los efectos de las intervenciones están basados en **meta-análisis y RCTs publicados**:

- **Arem et al. 2015** — Exercise and mortality (JAMA IM) — 6.3M personas
- **Estruch et al. 2013** — PREDIMED trial (NEJM) — 7,447 pacientes
- **Patterson & Sears 2017** — Intermittent Fasting (Annu Rev Nutr)
- **Belsky et al. 2022** — DunedinPACE (eLife) — Cohorte de 817 personas desde birth
- **Levine et al. 2018** — PhenoAge (PNAS) — 9,826 personas

---

## 📁 Estructura del proyecto

```
biofish-ai/
├── src/                        # Código fuente principal
│   ├── __init__.py
│   ├── constraints.py          # Hard Constraints DB (80+ límites biológicos)
│   ├── biofacts.py            # BioFacts DB (evidencia científica)
│   ├── signals.py             # Signal Bus (36 señales inter-agente)
│   ├── biological_clocks.py   # 4 relojes biológicos
│   ├── agent.py              # 18 perfiles + AgentRegistry
│   ├── moderator.py           # Moderator + Dr. Hallmarks + Dr. Mechanism
│   ├── interventions.py      # 8 intervenciones basadas en evidencia
│   ├── orchestrator.py       # SimulationOrchestrator principal
│   ├── llm_client.py         # Multi-provider LLM manager
│   └── agent_llm.py          # Biological agents con razonamiento LLM
│
├── api/                        # FastAPI REST API
│   ├── main.py               # Endpoints principales
│   └── llm_routes.py         # Rutas LLM
│
├── tests/                      # Tests unitarios
│   ├── test_agents.py
│   ├── test_orchestrator.py
│   ├── test_llm_client.py
│   ├── test_interventions.py
│   └── test_moderator.py
│
├── examples/                   # Ejemplos de uso
│   ├── basic_simulation.py
│   ├── llm_powered_simulation.py
│   ├── trajectory_analysis.py
│   └── intervention_comparison.py
│
├── scripts/                   # Scripts auxiliares
│   ├── setup_llm.py          # Configuración de proveedores LLM
│   └── benchmark.py           # Benchmarks de rendimiento
│
├── configs/                   # Archivos de configuración
│   └── groq_models.json      # Catálogo de modelos Groq
│
├── docs/                      # Documentación
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── CLOCKS.md
│   ├── INTERVENTIONS.md
│   ├── MODERATOR.md
│   └── API.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml            # Tests + linting
│       └── release.yml         # Release automation
│
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── setup.cfg
├── pyproject.toml
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## 🧪 Tests

```bash
# Todos los tests
pytest tests/ -v

# Solo tests de lógica determinista (no requieren LLM)
pytest tests/ -v -k "not llm"

# Cobertura
pytest tests/ --cov=src --cov-report=html
```

---

## 🤝 Contribuir

1. **Fork** el repositorio
2. Crea una rama: `git checkout -b feature/nueva-intervencion`
3. Commit: `git commit -m "feat: añadir intervención X con evidencia"`
4. Push: `git push origin feature/nueva-intervencion`
5. Abre un **Pull Request**

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías detalladas.

---

## ⚠️ Disclaimer médico

**BioFish AI es una herramienta de investigación y orientación, NO un dispositivo médico.**

- Los resultados son **orientativos y basados en modelos matemáticos y literatura científica**
- **No sustituyen el diagnóstico, tratamiento o consejo de un profesional sanitario**
- Consulta siempre con tu médico antes de hacer cambios en medicación o estilo de vida
- Los efectos proyectados son **estimaciones poblacionales**, no garantías individuales
- El sistema no debe utilizarse para autodiagnóstico

---

## 📜 Licencia

**AGPL-3.0** — [LICENSE](LICENSE)

---

## 🐟 BioFish AI — Biological Swarm Intelligence

*Tu organismo tiene un equipo de 18 expertos trabajando para ti.*

**Autor:** Fernando Fondillo — VIHOLABS
**GitHub:** [fernandofondillo/BIOFISH-AI](https://github.com/fernandofondillo/BIOFISH-AI)
**Web:** biofish.ai