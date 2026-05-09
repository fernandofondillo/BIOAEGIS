# Changelog — BioFish AI

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-09 — Initial Release

### 🎉 Features

#### 18 Biological Agents
- **Core Systems (12):** Cardiovascular, Metabolic, Inflammatory, Molecular, Epigenetic, Hepatic, Renal, Cognitive, Endocrine, Muscular, Immune, Adipose
- **Specialists (6):** Metabolic Flexibility, Insulin Sensitivity, Sports Performance, Nutritional Timing, Sleep & Recovery, Oxidative Stress
- Each agent has a specialized medical system prompt for LLM-powered reasoning
- Deterministic fallback assessment when LLM is unavailable

#### Multi-Provider LLM System
- **Auto-detection** from API key format (no configuration needed)
- **Providers supported:** Groq (free, 500K/day), MiniMax Code Plan, OpenRouter (140+ models), Kimi/Moonshot, DeepSeek, OpenAI, Anthropic, Ollama local
- **LLMClient** singleton with health checks, fallback order, and model selection per task
- **AgentLLM** layer: each biological agent gets a specialized medical system prompt

#### Anti-Hallucination Architecture
- **Hard Constraints DB:** 80+ biological limits (LDL 0-400, glucose 40-400, etc.)
- **Dr. Hallmarks:** Validates interventions against 12 hallmarks of aging and evidence levels A/B/C
- **Dr. Mechanism:** Detects mechanistically impossible claims (e.g., "completely block mTOR")
- **Consensus Engine:** Requires 3+ agents to agree before critical recommendations
- **Hard Constraints DB:** Automatic rejection of biologically impossible outputs

#### Biological Clocks
- **PhenoAge** (Levine 2018, PNAS) — 9 biomarkers, predicts mortality
- **Zhang Age** (Zhang 2020, Nature Aging) — 16 biomarkers, functional aging
- **DunedinPACE** (Belsky 2022, eLife) — aging **velocity**, not just state
- **Lifestyle Age** (proprietary meta-analysis) — exercise, sleep, diet, stress, HRV

#### Intervention Simulator
- **8 evidence-based interventions** with monthly effects modeled from meta-analyses and RCTs:
  - Ejercicio Aeróbico 150min/sem (Level A)
  - HIIT 3x/semana (Level A)
  - Ayuno Intermitente 16:8 (Level A)
  - Dieta Mediterránea + AOVE (Level A)
  - Omega-3 EPA+DHA 2g/día (Level A)
  - Ejercicio de Fuerza 3x/sem (Level A)
  - Metformina 850mg x2/día (Level A)
  - Plan Combinado (synergistic effects)
- Each with ceiling effects, contraindications, risks, and time-to-effect

#### Signal Bus
- **36 inter-agent signals** defined (VASCULAR_STRESS, INSULIN_RESISTANCE, PRO_INFLAM, etc.)
- Agents subscribe to relevant signals and emit their own
- Signal propagation mirrors real biochemical communication

### 🏗️ Architecture
- `src/constraints.py` — 80+ hard biological limits
- `src/biofacts.py` — Evidence types and BioFacts DB scaffold
- `src/signals.py` — 36 signals + SignalBus class
- `src/biological_clocks.py` — 4 clocks implemented
- `src/agent.py` — 18 agent profiles + AgentRegistry
- `src/moderator.py` — ModeratorAgent with Dr. Hallmarks + Dr. Mechanism
- `src/interventions.py` — 8 interventions with modeled effects
- `src/orchestrator.py` — SimulationOrchestrator + 18 assessment methods
- `src/llm_client.py` — Multi-provider LLM manager
- `src/agent_llm.py` — LLM-powered agent reasoning layer
- `api/main.py` — FastAPI with 15+ endpoints
- `api/llm_routes.py` — LLM provider routes
- `setup_llm.py` — CLI tool for LLM configuration

### 📡 API Endpoints
- `/init`, `/simulate`, `/simulate/trajectory`
- `/clocks`
- `/interventions`, `/interventions/simulate`, `/interventions/compare`
- `/agents`, `/agents/{id}`, `/agents/llm/think`, `/agents/llm/simulate`
- `/llm/`, `/llm/configure`, `/llm/health`, `/llm/chat`

### 🔬 Validation
- Full deterministic simulation tested with real biomarker data
- 7 agents activated in test scenario (cardiovascular, metabolic, inflammatory, molecular, hepatic, renal, sleep)
- Ayuno 16:8 simulation: LDL -8, HOMA-IR -0.4, CRP -0.3 per month
- Plan Combinado at 3 months: LDL -28pts, HOMA-IR -1.1, CRP -0.9

### 📚 Documentation
- Comprehensive README with architecture diagrams
- CONTRIBUTING.md
- API docs via Swagger UI (FastAPI `/docs`)
- System prompts for all 6 main agents with clinical knowledge

---

## [0.1.0] — 2026-05-09 — Proof of Concept

### Initial commit
- MiroFish architecture research and analysis
- BioFish AI concept and specification
- 12 biological agents defined
- PhenoAge and Lifestyle Clock implemented
- First orchestrator prototype