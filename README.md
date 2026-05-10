# 🐟 BioAEGIS — Sistema de Gemelo Digital Biológico

> 18 agentes biológicos · Relojes biológicos · Simulaciones · Dashboard visual

---

## 🚀 Instalación en 30 segundos (Mac / Linux)

Abre Terminal y **copia y pega esta única línea**:

```bash
curl -fsSL https://git.io/bioaegis | bash
```

Eso descarga el proyecto, instala todo, construye el dashboard y arranca el sistema automáticamente.

---

## 📋 Requisitos

- **macOS** o **Linux**
- **Python 3.9+** (se instala solo si no lo tienes)
- **Git** (se instala solo si no lo tienes)
- **API key de Groq** (gratis, 500K tokens/día) — [obtener aquí](https://console.groq.com)

---

## 🛠️ Instalación manual paso a paso

### 1. Clonar el proyecto
```bash
git clone https://github.com/fernandofondillo/BIOAEGIS.git
cd BIOAEGIS
```

### 2. Instalar dependencias Python
```bash
pip3 install --break-system-packages fastapi "uvicorn[standard]" loguru pydantic httpx
```

### 3. Configurar API key de Groq (gratis)
```bash
echo "GROQ_API_KEY=tu_key_de_groq" >> ~/.fenix/providers.toml
```

### 4. Arrancar
```bash
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
```

### 5. Dashboard (en otra ventana de Terminal)
```bash
cd frontend/bioaegis-dashboard/dist
python3 -m http.server 3001
```

### 6. Abrir en el navegador
```
http://localhost:3001
```

---

## 🌐 Dashboard — Qué veras

| Pestaña | Qué contiene |
|---------|-------------|
| **📊 Biomarcadores** | Tus 13+ datos médicos. Edita valores. Añade campos custom |
| **🧬 Simulación** | Selecciona intervención + meses → Ejecuta el gemelo digital |
| **🧠 Memoria** | Historial de simulaciones guardadas |

**Panel de resultados:**
- 🎛️ **Edad Biológica + DunedinPACE**
- 🔄 **Diagrama de Señales Inter-Agentes**
- 🧠 **18 Agentes Biológicos** (expandibles para ver razonamiento completo)
- 📈 **Tabla antes/después** de biomarcadores

---

## 📋 API REST

Documentación interactiva → `http://localhost:8000/docs`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/simulate/init` | POST | Inicializar twin |
| `/api/v1/simulate/run` | POST | Ejecutar simulación |
| `/api/v1/parameters/` | GET/POST | Listar / añadir biomarcadores |
| `/api/v1/interventions/` | GET/POST | Listar / añadir intervenciones |
| `/api/v1/memory/simulations/{sid}` | GET | Historial de sesiones |
| `/api/v1/llm/status` | GET | Estado de API key |

---

## 🔑 Configurar API key

### Groq (gratis — recomendado)
1. https://console.groq.com → Sign up → API Keys → Create new key
2. Edita el archivo:

```bash
nano ~/.fenix/providers.toml
```

Cambia `PEGA_TU_KEY_AQUI` por tu key (empieza por `gsk_`).

### Reiniciar después de cambiar la key:
```bash
pkill -f uvicorn && cd ~/BIOAEGIS/backend && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
```

---

## 🐳 Docker (opcional)

```bash
cd ~/BIOAEGIS
docker compose up
```

---

## 📂 Estructura del proyecto

```
BIOAEGIS/
├── bioaegis.py          ← Script de arranque simplificado
├── install.sh           ← Instalador automático en una línea
├── backend/
│   ├── app/
│   │   ├── main.py          ← FastAPI app
│   │   ├── db.py            ← SQLite (automático)
│   │   └── routers/         ← API endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/bioaegis-dashboard/
│   └── src/App.tsx          ← Dashboard React
├── src/                     ← Motor biológico Python
│   ├── orchestrator.py      ← BIOSIS engine
│   ├── agent.py             ← 18 perfiles de agentes
│   ├── biological_clocks.py  ← PhenoAge, DunedinPACE...
│   ├── constraints.py       ← Hard Constraints DB
│   └── signals.py           ← Signal Bus inter-agente
└── docs/
```

---

## 🧬 Los 18 Agentes Biológicos

| Agente | Sistema | Agente | Sistema |
|--------|---------|--------|---------|
| ❤️ Cardiovascular | Sistema cardiovascular | 🩸 Metabólico | Metabolismo glucosa |
| 🔥 Inflamatorio | Inflamación crónica | 🧬 Molecular | NAD+/AMPK/mTOR |
| 😴 Sleep Recovery | Sueño y HRV | 💪 Sports Performance | VO2max |
| 🫀 Hepático | Función hepática | 🧪 Renal | Función renal |
| 🧠 Cognitivo | Función cognitiva | ⚡ Endocrino | Sistema hormonal |
| 🦾 Muscular | Tejido muscular | 🛡️ Inmune | Sistema inmune |
| ⚖️ Adipose | Grasa visceral | 🔋 Metabolic Flexibility | Flexibilidad metabólica |
| 🩹 Insulin Sensitivity | Sensibilidad insulina | ⏰ Nutritional Timing | Timing nutricional |
| 🆓 Oxidative Stress | Estrés oxidativo | 📋 Epigenético | Metilación del ADN |

---

## 📊 Relojes Biológicos

| Reloj | Referencia |
|-------|-----------|
| **PhenoAge** | Levine et al. 2018, PNAS |
| **Zhang Age** | Zhang et al. 2020, Nature Aging |
| **DunedinPACE** | Belsky et al. 2022, eLife |
| **Lifestyle Age** | Meta-análisis propietario |

---

## 🧪 Intervenciones disponibles

1. Sin intervención
2. Ayuno intermitente 16:8
3. Ejercicio aeróbico 150 min/sem
4. HIIT 3x/semana
5. Dieta Mediterránea
6. Omega-3 (2g EPA+DHA)
7. Plan Combinado (ejercicio + ayuno + suplementos)
8. Metformina 850mg
9. + any custom que añadas

---

## 👨‍💻 Autor

**Fernando Fondillo** — VIHOLABS
https://github.com/fernandofondillo/BIOAEGIS

Licencia: **AGPL-3.0**
