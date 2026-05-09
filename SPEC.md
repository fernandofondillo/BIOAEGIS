# BIOFISH AI — Especificación Técnica v1.0
## Sistema de Simulación Biológica Multi-Agente para Longevidad y Salud
## Basado en: MiroFish AI × BIOSIS Engine × Longevidad

---

## 1. Concepto y Visión

**BIOFISH AI** es el primer motor de simulación biológica que aplica inteligencia colectiva multi-agente al organismo humano. Así como MiroFish simula sociedades enteras para predecir dinámicas sociales, BIOFISH simula el cuerpo humano como una red de 12 sistemas biológicos que se comunican, envejecen y responden a intervenciones.

**Feeling:** Deportivo, científico, premium. La experiencia de tener un gemelo digital de tu cuerpo que responde a cada decisión que tomas. Interfaz que parece un cockpit de control de salud personal — oscuro, elegante, con acentos en bioluminiscentes que evocan el interior del cuerpo.

---

## 2. Design Language

### Aesthetic Direction
**Referencia:** Studio Ghibli meets Bloomberg Terminal — ciencia hermosa. Fondo oscuro con visualizaciones biológicas en gradientes cian/magentas que evocan señalización celular. Tipografía técnica pero accesible.

### Color Palette
```
--bg-deep:        #0A0E1A   (fondo principal — azul noche profundo)
--bg-panel:      #111827   (paneles — gris oscuro)
--bg-card:       #1A2235   (cards — gris oscuro azulado)
--text-primary:  #F1F5F9   (texto principal)
--text-muted:   #94A3B8   (texto secundario)
--accent-cyan:   #06B6D4   (señalización — cian bioluminiscente)
--accent-magenta:#D946EF   (alerta — magenta)
--accent-green:  #10B981   (salud buena — verde)
--accent-yellow: #F59E0B   (precaución — amarillo)
--accent-red:    #EF4444   (alerta — rojo)
--glow-cyan:    rgba(6,182,212,0.15)  (glow para órganos)
```

### Typography
```
Display:  "Space Grotesk" — headings, scores, métricas grandes
Body:     "Inter" — texto, descripciones, razonamiento clínico
Mono:     "JetBrains Mono" — datos de laboratorio, valores numéricos
```

### Spatial System
- Grid de 8px base
- Cards: border-radius 12px, padding 24px
- Secciones: spacing 48px entre secciones mayores
- Responsive: mobile-first con breakpoints en 640px, 1024px

---

## 3. Layout y Estructura

### Páginas

```
/             → Landing (hero + cómo funciona + pricing + CTA signup)
/onboarding   → Intake de datos (wizard de 4 pasos)
/dashboard    → Dashboard del gemelo (página principal)
/simulator   → Simulador de intervenciones
/chat        → BioChat con contexto twin
/profile     → Perfil + historial de analíticas
```

### Dashboard Layout

```
┌──────────────────────────────────────────────────────────┐
│ HEADER: Logo + Nav + User Avatar                          │
├──────────────────────────────┬───────────────────────────┤
│                              │                            │
│   BODY VIZ 3D               │   ORGAN CARDS (scroll)    │
│   (cuerpo humano            │   12 órganos con score     │
│    con órganos              │   + reasoning clínico)     │
│    highlighted por          │                            │
│    score)                   │                            │
│                              │                            │
├──────────────────────────────┴───────────────────────────┤
│   BIOLOGICAL CLOCKS BAR                                  │
│   PhenoAge | GrimAge | DunedinPACE | Molecular | ...    │
├─────────────────────────────────────────────────────────┤
│   MOLECULAR PANEL (NAD+ | AMPK | mTOR | Autofagia | IGF-1)│
├─────────────────────────────────────────────────────────┤
│   [Simulador]  [BioChat]  [Historial]  [Descargar]       │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Features e Interacciones

### 4.1 Onboarding (Wizard de 4 pasos)

```
Paso 1 — Datos básicos
  Campos: nombre, edad, sexo biológico, altura, peso, perímetro cintura
  Validación: todos obligatorios

Paso 2 — Analítica de sangre
  Campos: 20+ biomarcadores de laboratorio
  Permitir subir PDF o escribir valores manualmente
  Opción: "No tengo analítica" → usa datos estimados

Paso 3 — Estilo de vida
  Campos: ejercicio, sueño, estrés, tabaco, alcohol, dieta, soledad, red social
  Escala visual (sliders) para cada factor

Paso 4 — Antecedentes y epigenética
  Campos: familia (CV, diabetes, alzheimer), condiciones actuales
  Opcional: test de metilación (subir PDF o valores)
```

### 4.2 Dashboard del Gemelo

```
OrganCard:
  Score circular (0-100) con gradiente de color
  Nombre del órgano + icono
  2 líneas de reasoning clínico
  Click → expande con detalles completos + recomendaciones

BodyViz:
  SVG/Canvas del cuerpo humano
  Órganos highlighted según score (verde=bueno, rojo=malo)
  Hover sobre órgano → muestra tooltip con score + reasoning
  Click sobre órgano → scroll hasta OrganCard correspondiente

Biological Clocks:
  Cards horizontales con:
    - Valor de edad actual
    - Diferencia vs edad cronológica (↑ rojo / ↓ verde)
    - Trend si hay historial (↑ o ↓)
    - Qué significa en 1 frase

Molecular Panel:
  5 barras horizontales (NAD+, AMPK, mTOR, Autofagia, IGF-1)
  Color por nivel (rojo < amarillo < verde)
  Tooltip con explicación de cada biomarcador
```

### 4.3 Simulador de Intervenciones

```
Selección de intervenciones:
  Lista con checkbox
  Cada intervención muestra:
    - Nombre
    - Categoría (nutrition/exercise/supplement/pharmaceutical)
    - Evidence level (A/B/C badge)
    - Coste mensual
    - Efectos esperados en preview

Duración de simulación:
  Botones: 6 meses | 12 meses | 36 meses

Resultado de simulación:
  TrajectoryChart: 2 líneas (con intervención vs sin)
  Impact table: órgano por órgano, magnitud del cambio
  Resumen: años de vida ganados (siappable)
  Coste/beneficio analysis
```

### 4.4 BioChat

```
Ventana de chat con:
  - Historial de conversación
  - Input de texto
  - Contexto del twin visible (collapsible sidebar)

Capacidades:
  - Responder preguntas sobre resultados del gemelo
  - Explicar por qué un órgano tiene cierto score
  - Recomendar intervenciones basadas en datos
  - Simular "qué pasa si" mediante el motor de intervención
  - Sugerir próximos análisis o tests

Límites:
  - Freemium: 10 msgs/mes
  - Plus: ilimitado
```

---

## 5. Component Inventory

### OrganCard
```
Estados: default, hover (glow), expanded, loading (skeleton)
Variantes por score: excellent (>85, verde), good (70-85, cyan), moderate (50-69, yellow), poor (<50, red)
```

### ClockCard
```
Estados: normal, warning (diff > 5 años), critical (diff > 10 años)
Variante: mini (para barra) y expanded (para sección clocks)
```

### InterventionItem
```
Estados: unselected, selected, loading (cuando simula)
Muestra: nombre, categoría badge, evidence level badge, coste, preview de efectos
```

### TrajectoryChart
```
Tipo: Recharts LineChart
Ejes: X = tiempo (meses), Y = score agregado o edad biológica
Líneas: baseline (sin intervención), con_intervención (resaltada)
Tooltip: valor en cada mes para ambas líneas
```

### BioChatMessage
```
Variantes: user_message (derecha, bg-card), agent_message (izquierda, bg-deep, con avatar 🐟)
Estados: sending, sent, error
```

---

## 6. Technical Approach

### Frontend
```
React 18 + TypeScript + Vite
Estado: React Context + useReducer para twin_state
HTTP: fetch API con wrapper typed
Charts: Recharts
3D Body: SVG interactivo (no Three.js — más ligero)
Estilos: TailwindCSS + CSS custom properties para theming
Routing: React Router v6
```

### Backend
```
FastAPI + Python 3.11
Async: asyncio + httpx para llamadas LLM
Validation: Pydantic v2
DB: Supabase (PostgreSQL) via psycopg2
Auth: Supabase Auth (magic link + password)
LLM: Groq SDK (openai-compatible) + MiniMax SDK
CORS: permitiendo frontend Vercel
```

### API Design

```
POST   /api/v1/auth/signup          → Registro
POST   /api/v1/auth/login          → Login
POST   /api/v1/auth/logout         → Logout

POST   /api/v1/twin/create         → Crear gemelo desde datos
GET    /api/v1/twin/{id}           → Obtener gemelo
GET    /api/v1/twin/latest         → Último gemelo del usuario
POST   /api/v1/twin/analytics      → Guardar analítica nueva

POST   /api/v1/simulate            → Correr simulación
GET    /api/v1/simulate/{id}       → Obtener resultados

POST   /api/v1/chat                → BioChat (contexto twin)
GET    /api/v1/chat/history        → Historial de chat

GET    /api/v1/interventions       → Lista de intervenciones disponibles
```

### Data Model (Supabase)

```sql
-- Users (Supabase Auth)

-- Twins
CREATE TABLE twins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  age INTEGER,
  sex CHAR(1),
  blood_data JSONB,
  lifestyle_data JSONB,
  organ_scores JSONB,
  clocks JSONB,
  molecular JSONB,
  reasoning JSONB
);

-- Simulations
CREATE TABLE simulations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  twin_id UUID REFERENCES twins(id),
  user_id UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  interventions JSONB,
  months INTEGER,
  results JSONB
);

-- Chat history
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth_users(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  role CHAR(10),
  content TEXT,
  twin_id UUID REFERENCES twins(id)
);
```

---

## 7. Biological Model

### Los 12 Agentes

| ID | Nombre | Rol | Biomarcadores clave |
|---|---|---|---|
| `cardiovascular` | Sistema Cardiovascular | Pump de sangre y vasos | LDL, HDL, TG, PCR, tensión |
| `metabolic` | Sistema Metabólico | Metabolismo energético | Glucosa, HbA1c, insulina, cintura |
| `hepatic` | Sistema Hepático | Detox y síntesis | ALT, GGT, AST, albúmina |
| `renal` | Sistema Renal | Filtración | Urea, creatinina, eGFR |
| `cognitive` | Sistema Cognitivo | Cerebro y cognition | TSH, vit D, B12, folato |
| `muscular` | Sistema Muscular | Fuerza y masa | Creatinina, IGF-1, testosterona |
| `endocrine` | Sistema Endocrino | Hormonas | TSH, cortisol, DHEA-S, testosterona |
| `immune` | Sistema Inmunitario | Defensa | Leucocitos, linfocitos%, PCR |
| `inflammatory` | Inflamación | Estado inflamatorio crónico | PCR, ferritina, IL-6 |
| `epigenetic` | Epigenética | Reloj epigenético | Homocisteína, NAD+, B12 |
| `molecular` | Sistema Molecular | Vías moleculares | NAD+, AMPK, mTOR |
| `coach` | Coach Agent | Usuario y recomendaciones | — |

### Relojes Biológicos

| Reloj | Método | Datos necesarios |
|---|---|---|
| PhenoAge | Levine 2018 PNAS | 9 biomarcadores de sangre |
| GrimAge proxy | Lu 2019 | Sangre + edad + sexo |
| DunedinPACE | Belsky 2022 eLife | Múltiples analíticas temporales |
| Lifestyle Clock | Meta-análisis | 8 factores de estilo de vida |
| Zhang Clock | Zhang 2020 | Sangre + epigenética |

---

*Spec v1.0 — 2026-05-09*
*Autor: BioFish AI Build System*