# BIOFISH AI — Plan Maestro de Implementación
## Basado en MiroFish AI × Longevidad × Sistemas Biológicos
## Versión: 1.0 | Fecha: 2026-05-09

---

## Advisors

Consejo multidisciplinar:
- Expertos en inteligencia colectiva y swarm intelligence
- Arquitectos de sistemas complejos adaptativos
- Especialistas en modelado biológico y fisiología sistémica
- Investigadores en longevidad, metabolismo y medicina de precisión
- Expertos en teoría de redes, dinámica social y comportamientos emergentes
- Científicos en biofísica, biología molecular, endocrinología y neuroinmunología
- Arquitectos de IA agéntica y sistemas multiagente
- Diseñadores de plataformas predictivas basadas en simulación
- Expertos en digital twins biológicos
- Especialistas en sistemas de predicción probabilística
- Expertos en causal inference, machine learning y modelos híbridos biofísicos + IA
- Expertos en healthtech, biotech y plataformas SaaS escalables
- Futuristas especializados en medicina preventiva y extensión de vida

---

## 1. QUÉ ES BIOFISH AI

**BioFish AI** es un motor de simulación biológica multi-agente que aplica la arquitectura de MiroFish AI (swarm intelligence × simulación predictiva) al dominio de la salud y la longevidad humana.

Así como MiroFish simula sociedades con miles de agentes para predecir dinámicas sociales, BIOFISH simula el **organismo humano como una red de sistemas biológicos** para predecir trayectorias de salud y evaluar intervenciones.

---

## 2. BASE CONCEPTUAL

### 2.1 Traducción MiroFish → Biología

```
MIROFISH                          BIOFISH
─────────────────────────────────────────────────────────
Mundo: sociedad humana            Mundo: organismo humano
Agentes: personas con             Agentes: sistemas biológicos
  personalidad y memoria             con estado y contexto
Red social: relaciones            Red biológica: señalización
  entre personas                    entre órganos/sistemas
Interacciones: debate,           Interacciones: señales bioquímicas,
  influencia, argumentación          cascadas, feedback loops
Opiniones como estado             Salud como estado (trayectoria)
Dinámica social = evolución       Dinámica biológica = envejecimiento/
  de opiniones en la red           mejora de órganos
Predicción: hacia dónde           Predicción: cómo envejece
  va la opinión pública              cada órgano con intervenciones
```

### 2.2 Motor BIOSIS (Biological Open Simulation Intelligence System)

```
┌──────────────────────────────────────────────────────┐
│  BIOLOGICAL WORLD MODEL                              │
│  Estado del organismo: sangre + tejidos + molecular   │
├──────────────────────────────────────────────────────┤
│  BIOLOGICAL AGENTS (12 sistemas)                    │
│  Cada agente:                                        │
│    - Estado interno del órgano/sistema               │
│    - Señales que recibe (de otros agentes)          │
│    - Señales que emite (a otros agentes)            │
│    - Reglas biológicas propias                      │
│    - Efecto del envejecimiento propio               │
│    - Respuesta a intervenciones                    │
├──────────────────────────────────────────────────────┤
│  SIMULATION LOOP (cada tick = 1 mes simulado)       │
│  1. Propagar señales biológicas compartidas          │
│  2. Cada agente procesa con su estado + señales       │
│  3. Sistema recalcula trayectorias                   │
│  4. Guardar snapshot mensual                        │
├──────────────────────────────────────────────────────┤
│  INTERVENTION ENGINE                                 │
│  Aplicar intervención → recalcular simulación        │
│  Comparar: sin intervención vs con intervención      │
└──────────────────────────────────────────────────────┘
```

---

## 3. ARQUITECTURA DEL SISTEMA

### 3.1 Stack tecnológico

```
Backend:    FastAPI + Python 3.11
LLM:        Groq (gratis, 500K tokens/día) + MiniMax Token Plan
Database:   Supabase (PostgreSQL + Auth + RLS)
Frontend:   React + TypeScript + Vite + TailwindCSS
Simulación: NumPy + SciPy + LLM (reasoning agentes)
Deployment: Railway (backend) + Vercel (frontend)
Dominio:    biofish.ai (pendiente)
```

### 3.2 Estructura del repositorio

```
BIOFISH-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Configuración
│   │   ├── routers/
│   │   │   ├── twin.py            # CRUD del gemelo biológico
│   │   │   ├── simulate.py          # Motor de simulación
│   │   │   ├── chat.py             # BioChat con contexto twin
│   │   │   └── trajectory.py        # Trayectorias temporales
│   │   ├── simulation/
│   │   │   ├── world_model.py      # Modelo biológico del organismo
│   │   │   ├── biological_clock.py  # Relojes biológicos
│   │   │   ├── intervention.py      # Biblioteca de intervenciones
│   │   │   └── simulator.py        # Loop de simulación BIOSIS
│   │   └── agents/
│   │       ├── base_agent.py        # Clase base de agente biológico
│   │       ├── cardiovascular.py     # Agente cardiovascular
│   │       ├── metabolic.py        # Agente metabólico
│   │       ├── hepatic.py          # Agente hepático
│   │       ├── renal.py            # Agente renal
│   │       ├── cognitive.py        # Agente cognitivo
│   │       ├── muscular.py         # Agente muscular
│   │       ├── endocrine.py        # Agente endocrino
│   │       ├── immune.py           # Agente inmunitario
│   │       ├── inflammatory.py     # Agente inflamación
│   │       ├── epigenetic.py       # Agente epigenético
│   │       └── molecular.py         # Agente molecular (NAD+, mTOR, AMPK)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── supabase_schema.sql
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── OnboardingPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── SimulatorPage.tsx
│   │   │   └── ChatPage.tsx
│   │   └── components/
│   │       ├── BodyViz.tsx         # Visualización 3D del cuerpo
│   │       ├── OrganCard.tsx      # Score + reasoning por órgano
│   │       ├── TrajectoryChart.tsx # Gráfico de trayectoria
│   │       └── InterventionPanel.tsx
│   ├── index.html
│   └── package.json
├── docs/
│   ├── BIOLOGY_MODEL.md
│   ├── AGENTS_SPEC.md
│   └── SIMULATION_ENGINE.md
├── README.md
├── SPEC.md
└── LICENSE
```

---

## 4. LOS 12 AGENTES BIOLÓGICOS

### 4.1 Base class

```python
class BiologicalAgent:
    """Clase base — cada agente biológico procesa su órgano/sistema"""

    def __init__(self, organ_id: str, name: str, description: str):
        self.organ_id = organ_id
        self.name = name
        self.description = description
        self.state = {}           # Estado interno del órgano
        self.signals_received = []  # Señales de otros agentes
        self.signals_emitted = []   # Señales que emite

    def receive_signal(self, signal: "BiologicalSignal"):
        """Recibe una señal bioquímica de otro agente"""
        self.signals_received.append(signal)

    def process(self, blood_data: dict, lifestyle: dict, dt: float) -> "OrganState":
        """Procesa su estado interno + señales + datos de sangre"""
        raise NotImplementedError

    def emit_signals(self) -> list["BiologicalSignal"]:
        """Emite señales a otros agentes (efecto en cascada)"""
        return self.signals_emitted

    def apply_intervention(self, intervention: "Intervention", magnitude: float):
        """Responde a una intervención"""
        pass

    def get_reasoning(self) -> str:
        """Genera reasoning clínico como texto (para dashboard y BioChat)"""
        raise NotImplementedError
```

### 4.2 Los 12 agentes y sus responsabilidades

| # | Agente | Entrada clave | Efecto en otros | Estado interno |
|---|---|---|---|---|
| 1 | **Cardiovascular** | LDL, HDL, TG, PCR, tensión | BDNF, señalización vascular | arterial_age, plaque_risk, ldl_ox |
| 2 | **Metabólico** | Glucosa, HbA1c, insulina, cintura | adiponectina, leptina | insulin_resistance, metabolic_flex |
| 3 | **Hepático** | ALT, GGT, AST, albúmina | síntesis proteica, detox | liver_fat, enzyme_balance, detox_capacity |
| 4 | **Renal** | Urea, creatinina, eGFR | presión arterial, filtración | kidney_age, filtration_rate, esrd_risk |
| 5 | **Cognitivo** | TSH, vitamina D, B12, folato | neurotransmisores | cognitive_reserve, neuro_inflammation |
| 6 | **Muscular** | Creatinina, IGF-1, testosterona, ejercicio | creatina quinasa | muscle_mass_index, anabolic_capacity |
| 7 | **Endocrino** | TSH, testosterona, cortisol, DHEA-S | regulación hormonal | hormonal_balance, cortisol_rhythm, thyroid_axis |
| 8 | **Inmunitario** | Leucocitos, linfocitos%, PCR | inmunoglobulinas | immune_senescence, infection_risk |
| 9 | **Inflamatorio** | PCR, ferritina, IL-6, cortisol | IL-6, TNF-α, CRP (cross-organ) | chronic_inflammation_index |
| 10 | **Epigenético** | NAD+, homocisteína, B12, folato | methylation_drift, NAD+/SIRT1 | biological_age_acceleration |
| 11 | **Molecular** | Nutrientes, ayuno, ejercicio | AMPK, mTOR, SIRT1, autofagia | nad_plus, ampk_activity, mtor_activity |
| 12 | **Coach** | Input del usuario, twin_state | Recomendaciones | — |

### 4.3 Sistema de señales biológicas (Bloodstream)

```python
@dataclass
class BiologicalSignal:
    source: str       # agente emisor (ej: "inflammatory")
    target: str      # agente receptor (ej: "cardiovascular")
    signal_type: str # "pro-inflammatory", "anabolic", "catabolic"
    magnitude: float # 0.0 - 1.0

# Ejemplo real:
INFLAMMATION_TO_CV = BiologicalSignal(
    source="inflammatory",
    target="cardiovascular",
    signal_type="pro-inflammatory",
    magnitude=0.7,
)
# Efecto: cardiovascular.reduce_score(0.7 * 0.15)  # -15% por inflamación
```

---

## 5. MOTOR DE SIMULACIÓN BIOSIS

### 5.1 Intervention Library (9 intervenciones iniciales)

```python
INTERVENTIONS = {
    "fasting_16_8": Intervention(
        name="Ayuno intermitente 16:8",
        category=Category.NUTRITION,
        evidence_level="A",
        effects=[
            Effect(agent="molecular",    direction=Direction.UP,   magnitude=0.15, timeline_months=2),
            Effect(agent="molecular",    direction=Direction.DOWN, magnitude=0.20, timeline_months=3),
            Effect(agent="inflammatory", direction=Direction.DOWN, magnitude=0.25, timeline_months=3),
            Effect(agent="metabolic",    direction=Direction.UP,   magnitude=0.08, timeline_months=4),
        ],
        cost_monthly_eur=0,
    ),
    "aerobic_150": Intervention(
        name="Ejercicio aeróbico 150 min/sem",
        category=Category.EXERCISE,
        evidence_level="A",
        effects=[
            Effect(agent="cardiovascular",direction=Direction.UP,   magnitude=0.10, timeline_months=4),
            Effect(agent="cognitive",   direction=Direction.UP,   magnitude=0.07, timeline_months=6),
            Effect(agent="inflammatory",direction=Direction.DOWN, magnitude=0.20, timeline_months=3),
            Effect(agent="molecular",  direction=Direction.UP,   magnitude=0.12, timeline_months=2),
        ],
        cost_monthly_eur=0,
    ),
    "metformin_500": Intervention(
        name="Metformina 500mg/día",
        category=Category.PHARMACEUTICAL,
        evidence_level="B",
        effects=[
            Effect(agent="metabolic",   direction=Direction.UP,   magnitude=0.12, timeline_months=6),
            Effect(agent="molecular",  direction=Direction.UP,   magnitude=0.08, timeline_months=4),
            Effect(agent="inflammatory",direction=Direction.DOWN, magnitude=0.30, timeline_months=3),
        ],
        requires_prescription=True,
        cost_monthly_eur=5,
    ),
    "nmn_300": Intervention(
        name="NMN 300mg/día",
        category=Category.SUPPLEMENT,
        evidence_level="C",
        effects=[
            Effect(agent="molecular",  direction=Direction.UP, magnitude=0.15, timeline_months=3),
            Effect(agent="epigenetic",direction=Direction.UP, magnitude=0.06, timeline_months=6),
            Effect(agent="cognitive", direction=Direction.UP, magnitude=0.05, timeline_months=6),
        ],
        cost_monthly_eur=40,
    ),
    "omega3_2g": Intervention(
        name="Omega-3 2g/día",
        category=Category.SUPPLEMENT,
        evidence_level="A",
        effects=[
            Effect(agent="cardiovascular",direction=Direction.UP,   magnitude=0.08, timeline_months=6),
            Effect(agent="inflammatory",direction=Direction.DOWN, magnitude=0.25, timeline_months=3),
        ],
        cost_monthly_eur=25,
    ),
    "resveratrol_500": Intervention(
        name="Resveratrol 500mg/día",
        category=Category.SUPPLEMENT,
        evidence_level="B",
        effects=[
            Effect(agent="molecular",   direction=Direction.UP,   magnitude=0.10, timeline_months=4),
            Effect(agent="cardiovascular",direction=Direction.UP, magnitude=0.05, timeline_months=6),
        ],
        cost_monthly_eur=20,
    ),
    "sleep_8h": Intervention(
        name="Dormir 8 horas/noche",
        category=Category.LIFESTYLE,
        evidence_level="A",
        effects=[
            Effect(agent="cognitive",    direction=Direction.UP,   magnitude=0.12, timeline_months=2),
            Effect(agent="endocrine",   direction=Direction.UP,   magnitude=0.08, timeline_months=3),
            Effect(agent="inflammatory",direction=Direction.DOWN, magnitude=0.20, timeline_months=3),
        ],
        cost_monthly_eur=0,
    ),
    "strat_reduction": Intervention(
        name="Reducción de estrés (mindfulness 30min/día)",
        category=Category.LIFESTYLE,
        evidence_level="A",
        effects=[
            Effect(agent="endocrine",   direction=Direction.UP,   magnitude=0.10, timeline_months=3),
            Effect(agent="inflammatory",direction=Direction.DOWN, magnitude=0.30, timeline_months=3),
        ],
        cost_monthly_eur=0,
    ),
    "vitd_4000": Intervention(
        name="Vitamina D3 4000UI/día",
        category=Category.SUPPLEMENT,
        evidence_level="A",
        effects=[
            Effect(agent="immune",      direction=Direction.UP,   magnitude=0.08, timeline_months=3),
            Effect(agent="inflammatory",direction=Direction.DOWN, magnitude=0.15, timeline_months=4),
        ],
        cost_monthly_eur=8,
    ),
}
```

### 5.2 Simulation Loop

```python
async def simulate_biosis(
    twin_state: TwinState,
    interventions: list[Intervention],
    months: int = 12,
) -> SimulationResult:
    """
    Simula la evolución del gemelo biológico durante N meses.
    1 tick = 1 mes simulado
    """
    agents = initialize_agents(twin_state)  # 12 agentes
    bloodstream = Bloodstream()
    results = []

    for month in range(months):
        # 1. Propagar señales del bloodstream a cada agente
        bloodstream.propagate_to(agents)

        # 2. Cada agente procesa
        for agent in agents:
            state = agent.process(twin_state.blood_data, twin_state.lifestyle, dt=1/12)

        # 3. Cada agente emite nuevas señales
        for agent in agents:
            new_signals = agent.emit_signals()
            bloodstream.add(new_signals)

        # 4. Aplicar intervenciones este mes
        for intervention in interventions:
            for effect in intervention.effects:
                agent = get_agent(effect.agent, agents)
                agent.apply_intervention(effect, month)

        # 5. Calcular snapshot mensual
        snapshot = calculate_snapshot(agents, month)
        results.append(snapshot)

    return build_simulation_result(results, agents)
```

---

## 6. PLAN DE IMPLEMENTACIÓN POR FASES

### FASE 1 — Fundamentos (Semana 1-2)
**→ Crear repo + Motor de simulación + API básica**

```
□ Crear repositorio GitHub: BIOFISH-AI
□ FastAPI backend con routers (twin, simulate, chat, trajectory)
□ Implementar base_agent.py + biological_signal
□ Implementar Intervention Library (9 intervenciones)
□ Implementar simulator.py (BIOSIS loop)
□ Implementar Biological Clocks (PhenoAge, GrimAge, DunedinPACE, Lifestyle)
□ Supabase schema: users, twins, simulations, interventions, trajectories
□ API endpoints:
    POST /twin/create
    GET  /twin/{id}
    POST /simulate
    GET  /simulate/{id}/results
□ Tests unitarios del motor de simulación
```

### FASE 2 — Motor Completo (Semana 3-4)
**→ 12 agentes + BioChat + Dashboard UI**

```
□ Implementar los 12 BiologicalAgents con lógica completa
□ Bloodstream con propagación de señales cruzadas
□ Intervention Engine con efectos cruzados entre órganos
□ BioChat con contexto twin (Groq API)
□ Comparador de simulaciones (con vs sin intervención)
□ Frontend: Dashboard con scores de órganos + reasoning clínico
□ Frontend: Simulador UI con selección de intervenciones
□ Frontend: BodyViz 3D con highlighting de órganos
□ Tests de integración
```

### FASE 3 — Predicción y Trayectorias (Semana 5-6)
**→ Trayectorias temporales + Visualización completa**

```
□ Motor de predicción de trayectorias (snapshots mensuales)
□ Gráfico de evolución: 6m, 12m, 36m
□ Comparación lado a lado: intervenciones vs baseline
□ Frontend: TrajectoryChart (Recharts)
□ Historial de submissions (múltiples analíticas en el tiempo)
□ DunedinPACE real con múltiples puntos temporales
□ Onboarding completo (intake de datos)
□ Panel molecular visual (NAD+, AMPK, mTOR, Autofagia)
□ Deployment producción (Railway + Vercel)
```

### FASE 4 — Escalabilidad (Semana 7-8)
**→ Multi-user + Métricas + Advanzado**

```
□ CoachAgent proactivo (recomendaciones automáticas)
□ Alertas y notificaciones (scores que bajan)
□ Dashboard de métricas de población (agregado anónimo)
□ Comparador de cohorts (mismos rangos de edad)
□ API pública para integraciones ( wearables, DICOM)
□ PWA o React Native (app mobile)
□ Tests E2E con Playwright
□ Documentación completa
□ CI/CD con GitHub Actions
□ README.md completo con demo
```

---

## 7. ORDEN DE IMPLEMENTACIÓN (para empezar HOY)

```
DÍA 1:
  □ Crear repo GitHub: github.com/fernandofondillo/BIOFISH-AI
  □ Estructura de carpetas backend + frontend
  □ requirements.txt + Dockerfile
  □ supabase_schema.sql

DÍA 2:
  □ base_agent.py + BiologicalSignal
  □ 4 agentes básicos: Cardiovascular, Metabólico, Inflamatorio, Molecular
  □ world_model.py (organismo completo)
  □ Intervention Library (9 intervenciones)
  □ simulator.py (BIOSIS loop)

DÍA 3:
  □ 8 agentes restantes
  □ biological_clock.py (4 relojes)
  □ FastAPI routers (twin, simulate, chat)
  □ Tests unitarios

DÍA 4:
  □ Frontend: Dashboard con OrganCards
  □ BodyViz 3D (cuerpo humano con órganos)
  □ Conectar API al frontend

DÍA 5:
  □ BioChat con contexto twin
  □ Intervention Panel UI
  □ TrajectoryChart con Recharts

DÍA 6:
  □ Auth + Supabase
  □ Historial + múltiples submissions
  □ Deployment Railway + Vercel

DÍA 7:
  □ Tests + polish
  □ Documentación
  □ README.md completo
  □ GitHub Actions CI/CD
```

---

## 8. DIFERENCIACIÓN

| Competidor | Enfoque | Limitación | BIOFISH |
|---|---|---|---|
| InsideTrack | Scoring | No simulación, no multi-agente | ✅ Simulación predictiva real |
| Future | App salud | Gamificación, no agentes | ✅ 12 agentes biológicos |
| Lark | Wearables | Datos limitados | ✅ Sangre completa + estilo de vida |
| AEGIS OS | Relojes biológicos | Scoring estático | ✅ Simulación con intervención |
| OpenAI Health | LLM genérico | Sin modelo biológico | ✅ Motor BIOSIS con 12 agentes |
|修? | No existe | — | ✅ Primero en swarm × biología |

---

## 9. MODELO DE NEGOCIO

```
Freemium:
  GRATIS:
  - Creación de gemelo (datos básicos)
  - Scores de órganos
  - BioChat básico (10 msgs/mes)
  - Simulador de 1 intervención

  PLUS (€9.99/mes):
  - Datos de sangre completos
  - Simulador ilimitado
  - BioChat ilimitado
  - Trayectorias a 36 meses
  - Historial de analíticas
  - Alertas proactivas

  PRO (€29.99/mes):
  - Todo lo anterior
  - API access
  - CoachAgent proactivo
  - Informe mensual personalizado
  - Integración wearables

B2B (Enterprise):
  - Clínicas estéticas y gyms
  - Dashboard de pacientes
  - API para integración EMR/EHR
  - Informes clínicos
  - Custom interventions
  - €199-499/mes por clínica
```

---

## 10. RECURSOS NECESARIOS

```
CONOCIMIENTO:
- Longevidad y envejecimiento: 12 hallmarks (López-Otín et al., 2013)
- Relojes biológicos: PhenoAge, GrimAge, DunedinPACE, Zhang Clock
- Farmacología de intervenciones: meta-análisis de RCTs
- Arquitectura MiroFish/OASIS: CAMEL-AI (Liu et al., 2024)
- Modelado de sistemas complejos adaptativos

DATOS:
- Biomarcadores de sangre (laboratorio clínico)
- Datos de estilo de vida (cuestionario)
- Datos epigenéticos (opcional, expensive)
- Evidencia de intervenciones (RCTs, meta-análisis)

COMPUTACIÓN:
- CPU para simulación (no GPU necesaria)
- Groq API (gratis, 500K tokens/día) para BioChat
- MiniMax Token Plan para reasoning complejo
- Supabase (gratis tier) para database

INFRAESTRUCTURA:
- Railway Hobby ($5/mes) para backend FastAPI
- Vercel (gratis) para frontend
- Supabase (gratis tier) para DB + Auth
- Dominio: biofish.ai (~$10/año)
```

---

*Plan creado: 2026-05-09*
*Basado en: MiroFish AI (OASIS framework) + AEGIS OS + SOMNIUM research*
*Para: Fernando Fondillo / VIHOLABS Biotech*
*Meta: Repositorio GitHub funcional, versión 1.0*