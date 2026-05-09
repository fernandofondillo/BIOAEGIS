# API Reference — BioFish AI

> Documentación de los endpoints de la REST API.

## Base URL

```
http://localhost:8000
```

Swagger UI interactiva: `http://localhost:8000/docs`

## Authentication

No requiere autenticación en desarrollo. Para producción, añade middleware de auth.

## Endpoints

### Simulation

#### `POST /init`
Inicializa un usuario con sus biomarcadores.

**Request body:**
```json
{
  "age": 40,
  "sex": "male",
  "ldl_cholesterol": 155.0,
  "hdl_cholesterol": 42.0,
  "triglycerides": 210.0,
  "glucose_fasting": 102.0,
  "hba1c": 5.8,
  "homa_ir": 3.2,
  "c_reactive_protein": 3.5,
  "systolic_bp": 135.0,
  "vo2max": 32.0,
  "sleep_hours": 6.0,
  "hrv_sdnn": 32.0,
  "exercise_min_per_week": 60,
  ...
}
```

**Response:**
```json
{
  "status": "initialized",
  "user_biomarkers_count": 40,
  "available_agents": ["cardiovascular", "metabolic", ...],
  "initial_clocks": {
    "PhenoAge": { "biological_age": 48.3, "age_acceleration": 8.3 },
    "Lifestyle Age": { "biological_age": 44.1, "age_acceleration": 4.1 }
  },
  "ensemble_summary": {
    "ensemble_biological_age": 46.2,
    "ensemble_acceleration": 6.2,
    "ensemble_pace": 1.16
  }
}
```

#### `POST /simulate`

Ejecuta un tick de simulación.

**Request body:**
```json
{
  "biomarkers": { ... },      // mismos datos de /init
  "question": "¿Debería hacer ayuno intermittent?",
  "intervention": "ayuno_intermitente_16_8",
  "months": 3
}
```

**Response:**
```json
{
  "tick": 3,
  "timestamp": "2026-05-09T18:00:00",
  "agent_outputs": [
    {
      "agent_id": "cardiovascular",
      "assessment": "Riesgo cardiovascular moderado-alto",
      "concerns": [
        "LDL alto (155 mg/dL) — riesgo aterosclerótico elevado",
        "HDL bajo (42 mg/dL) — HDL cardioprotector deficiente"
      ],
      "recommended_actions": [
        "Reducir LDL por debajo de 100 mg/dL"
      ],
      "signals_emitted": [
        { "name": "VASCULAR_STRESS", "priority": "HIGH" }
      ],
      "confidence": 0.85
    }
  ],
  "signals_emitted": [...],
  "moderator_output": {
    "consensus": {
      "recommendation": "El equipo recomienda: Ayuno Intermitente 16:8...",
      "evidence_level": "A",
      "grade": "STRONG FOR",
      "confidence": 0.82,
      "supporting_agents": ["cardiovascular", "metabolic", ...]
    },
    "confidence": 0.82,
    "disclaimer": "Esta información es orientativa..."
  },
  "clocks": {
    "PhenoAge": { "biological_age": 44.2, "age_acceleration": 4.2 },
    "DunedinPACE": { "biological_age": 46.4, "pace": 1.16 }
  },
  "ensemble_summary": {
    "ensemble_biological_age": 45.2,
    "ensemble_pace": 1.13
  }
}
```

---

### LLM Agents

#### `POST /agents/llm/simulate`
Simulación completa con LLM-powered agents.

```json
{
  "agent_ids": ["cardiovascular", "metabolic", "inflammatory", "sleep_recovery"],
  "biomarkers": { ... },
  "intervention": "ayuno_intermitente_16_8",
  "tick": 3
}
```

**Response:**
```json
{
  "llm_provider": "groq",
  "agents_consulted": ["cardiovascular", "metabolic", "inflammatory", "sleep_recovery"],
  "agent_reasonings": [
    {
      "agent_id": "cardiovascular",
      "reasoning": "Analizando los datos del paciente...\nLDL elevado a 155...",
      "assessment": "Riesgo cardiovascular moderado-alto",
      "concerns": ["LDL 155mg/dL es elevado..."],
      "recommended_actions": ["Reducir LDL por debajo de 100..."],
      "signals_to_emit": ["VASCULAR_STRESS"],
      "confidence": 0.85,
      "model_used": "groq/llama-3.3-70b-instruct",
      "latency_ms": 1240.5
    }
  ],
  "moderator_consensus": { ... }
}
```

---

### LLM Providers

#### `POST /llm/configure`

Configura un proveedor LLM.

```json
{
  "api_key": "gsk_...",
  "provider": "groq",
  "set_as_default": true
}
```

#### `POST /llm/chat`

Chat directo con cualquier modelo.

```json
{
  "messages": [
    {"role": "system", "content": "Eres un asistente médico..."},
    {"role": "user", "content": "¿Qué pasa si hago ayuno 16:8?"}
  ],
  "model": "groq/llama-3.3-70b-instruct",
  "temperature": 0.3
}
```

**Response:**
```json
{
  "success": true,
  "content": "El ayuno intermittent 16:8 puede mejorar...",
  "model": "groq/llama-3.3-70b-instruct",
  "provider": "groq",
  "tokens_used": 1240,
  "latency_ms": 890.2
}
```

---

### Biological Clocks

#### `POST /clocks`

Calcula los 4 relojes biológicos.

```json
{
  "age": 40,
  "sex": "male",
  "ldl_cholesterol": 155,
  "hdl_cholesterol": 42,
  "triglycerides": 210,
  "glucose_fasting": 102,
  "hba1c": 5.8,
  "homa_ir": 3.2,
  "c_reactive_protein": 3.5,
  ...
}
```

**Response:**
```json
{
  "clocks": {
    "PhenoAge": {
      "clock_name": "PhenoAge",
      "biological_age": 48.3,
      "chronological_age": 40,
      "age_acceleration": 8.3,
      "interpretation": "Envejecimiento acelerado. Intervención urgente."
    },
    "DunedinPACE": {
      "clock_name": "DunedinPACE",
      "biological_age": 46.4,
      "pace": 1.16,
      "interpretation": "Envejecimiento 16% más rápido que el promedio."
    }
  },
  "ensemble": {
    "ensemble_biological_age": 46.2,
    "ensemble_pace": 1.15,
    "summary_interpretation": "⚡ Envejecimiento biológico acelerado..."
  }
}
```

---

### Interventions

#### `GET /interventions`

Lista las 8 intervenciones disponibles.

#### `POST /interventions/compare`

Compara intervenciones sobre un biomarcador.

```json
{
  "biomarkers": { ... },
  "intervention_ids": ["ayuno_intermitente_16_8", "omega3_epa_dha_2g", "combinacion_ejercicio_diana"],
  "target_biomarker": "triglycerides",
  "months": 6
}
```

**Response:**
```json
{
  "comparison": {
    "ayuno_intermitente_16_8": {
      "intervention": "Ayuno Intermitente 16:8",
      "final_value": 175,
      "total_change": -35
    },
    "omega3_epa_dha_2g": {
      "intervention": "Omega-3 2g/día",
      "final_value": 185,
      "total_change": -25
    },
    "combinacion_ejercicio_diana": {
      "intervention": "Plan Combinado",
      "final_value": 155,
      "total_change": -55
    }
  },
  "target_biomarker": "triglycerides"
}
```