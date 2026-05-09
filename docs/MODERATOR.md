# Moderator Agent — BioFish AI

> **El Director Médico del equipo de 18 agentes.**

## Qué es el Moderator

El Moderator no es un agente biológico más. Es el **Chief Medical Officer** del sistema: la capa final que filtra, valida y presenta los resultados al usuario.

```
┌─────────────────────────────────────────────────────────┐
│                    USER QUESTION                        │
│     "¿Debería hacer ayuno intermittent?"              │
└───────────────────────┬─────────────────────────────────┘
                        │
┌─────────────────────▼─────────────────────────────────┐
│           18 BIOLOGICAL AGENTS                           │
│  cardiovascular, metabolic, inflammatory, molecular...    │
│         (cada uno razona, emite señales)                │
└───────────────────────┬─────────────────────────────────┘
                        │
┌─────────────────────▼─────────────────────────────────┐
│           MODERATOR AGENT                               │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │ DR. HALLMARKS (Longevidad)                    │  │
│  │  12 hallmarks del envejecimiento               │  │
│  │  Niveles de evidencia A/B/C                  │  │
│  │  Valida intervenciones                        │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │ DR. MECHANISM (Biología Molecular)             │  │
│  │  Valida plausibilidad biológica               │  │
│  │  Detecta claims mecanísticamente impossibles  │  │
│  │  Detecta claims contradictorios              │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │ CONSENSUS ENGINE                              │  │
│  │  Requiere 3+ agentes en acuerdo             │  │
│  │  Calcula confidence score                   │  │
│  │  Genera recomendación final                 │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │ HARD CONSTRAINTS DB                          │  │
│  │  80+ límites biológicos inviolables          │  │
│  │  Rechaza outputs biológicamente impossibles  │  │
│  └───────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
              ┌───────────────────────┐
              │  USER OUTPUT         │
              │  Recomendación médica │
              │  con evidencia A/B/C │
              └───────────────────────┘
```

## Dr. Hallmarks

**Expertise:** Los 12 hallmarks del envejecimiento (López-Otín 2013) y niveles de evidencia científica.

### Los 12 Hallmarks

```
1. Inestabilidad genómica
2. Acortamiento de telómeros
3. Alteraciones epigenéticas
4. Pérdida de proteostasis
5. Desregulación del sensing de nutrientes
6. Disfunción mitocondrial
7. Senescencia celular
8. Agotamiento de células madre
9. Comunicación intercelular alterada
10. Autofagia desactivada
11. Inflammaging
12. Disbiosis
```

### Niveles de evidencia

| Nivel | Definición | Ejemplo |
|---|---|---|
| **A** | Meta-análisis de RCTs | Ejercicio 150min reduce mortalidad 20-35% |
| **B** | Estudios de cohortes | LDL alto → riesgo cardiovascular |
| **C** | Series de casos, opinión experta | NMN supplementation |
| **D** | Evidencia conflictiva | Resveratrol |

### Validación de intervenciones

```python
DrHallmarks.validate_intervention("rapamicina_5mg")
# → (False, "NO RECOMENDADA: immunosupresión severa.
#     Solo evidencia en modelos animales. Riesgo > beneficio.")

DrHallmarks.validate_intervention("ejercicio_aerobico_150")
# → (True, "RECOMENDADA con evidencia Level A.
#     Meta-análisis 300+ estudios, 6.3M personas.")
```

## Dr. Mechanism

**Expertise:** Biología molecular, vías de señalización, farmacología.

### Vías moleculares validadas

```
AMPK ←→ mTOR ←→ NAD+ ←→ SIRT1
   ↓           ↓        ↓
 Autofagia   Síntesis   Metabolismo
             proteica    mitocondrial
```

### Claims que detecta como impossibles

```
❌ "Voy a bloquear mTOR completamente"
   → ERROR: mTOR es esencial para supervivencia.
     mTOR bloqueo total = apoptosis. No biológicamente possible.

❌ "Voy a eliminar toda la inflamación"
   → ERROR: La inflamación AGUDA es necesaria y protectora.
     Lo que queremos es REDUCIR la inflamación CRÓNICA.

❌ "NAD+ instantáneo"
   → ERROR: Los precursores tardan días-semanas en elevar NAD+.
     No se puede elevar instantáneamente.

❌ "Cetonas en 1 día"
   → ERROR: Entrar en ketosis requiere 2-7 días de restricción de carbs.
```

## Consensus Engine

El Consensus Engine requiere acuerdo entre múltiples agentes antes de recomendar acciones críticas.

### Lógica de consenso

```python
def evaluate_consensus(agent_outputs, concern):
    agreeing = [a for a in agent_outputs
                if concern in a.concerns or concern in a.recommended_actions]
    
    if len(agreeing) >= 3:
        return ConsensusLevel.HIGH  # Recomendación fuerte
    elif len(agreeing) == 2:
        return ConsensusLevel.MODERATE  # Recomendación condicional
    elif len(agreeing) == 1:
        return ConsensusLevel.LOW  # Solo un agente — caution
    else:
        return ConsensusLevel.NONE  # Sin acuerdo
```

### Ejemplo real

```
CONCERNS: "LDL alto (155 mg/dL)"

Cardiovascular: ✅ Acepta — "LDL 155 es alto, reducir"
Hepatic:       ✅ Acepta — "LDL alto implica riesgo hepático"
Metabolic:      ✅ Acepta — "LDL alto amplifica resistencia insulina"
Molecular:      ⚠️ Cautela — "LDL alto no es prioritario vs AMPK"
Cognitive:      ⚠️ Cautela — "No es prioritario para cognición"
Muscular:       ❌ Rechaza — "No afecta al músculo directamente"

CONSENSUS: 3/6 agentes = ACUERDO PARCIAL
GRADE: WEAK FOR
CAVEAT: Solo cardiovascular, hepático y metabolic concuerdan.
         Molecular y cognitive no lo consideran prioritario.
```

## Hard Constraints DB

Límites biológicamente impossibles que ningún agente puede violar:

```python
constraints_db.validate("ldl_cholesterol", 550)
# → (False, "LDL 550 mg/dL está muy por encima
#     del máximo biológico de 400 mg/dL.
#     Valor biológicamente imposible.")

constraints_db.validate("glucose_fasting", 25)
# → (False, "Glucosa 25 mg/dL es hipoglucemia severa.
#     Por debajo de 40 mg/dL riesgo de pérdida de consciencia.")
```

## Output final

El Moderator genera una recomendación estructurada:

```
✅ RECOMENDACIÓN DEL EQUIPO MÉDICO
══════════════════════════════════════════════════════════

El equipo recomienda: Ayuno Intermitente 16:8

📋 NIVEL DE EVIDENCIA: A (Meta-análisis de RCTs)
   Grado: STRONG FOR

🤝 AGENTES CONSULTADOS (8):
   cardiovascular ✅, metabolic ✅, inflammatory ✅,
   hepatic ✅, adipose ✅, molecular ✅, renal ⚠️, cognitive ⚠️

⏱️ PLAZO ESTIMADO: 3 meses
   Cambios esperados:
     LDL: -8 mg/dL
     HOMA-IR: -0.4
     PCR: -0.3 mg/L
     Triglicéridos: -15 mg/dL

⚠️ PRECAUCIONES:
   | Contraindicado en diabetes T1 insulin-dependiente
   | Riesgo de hipoglucemia en medicados
   | No recomendado en trastornos alimentarios

⚡ RIESGOS:
   | Hipoglucemia si medicación antidiabética
   | Irritabilidad inicial (transitoria)

💡 ALTERNATIVA:
   Si no puede hacer ayuno: reducir carbohidratos refinados
   tiene beneficios similares con menos riesgo

🔬 CONFIANZA DEL EQUIPO: 82%
   Basado en 8 agentes y 3 niveles de evidencia

══════════════════════════════════════════════════════════
⚠️ Esta información es orientativa y no sustituye
   el consejo médico profesional.
   Consulta siempre con tu médico antes de hacer
   cambios significativos.
```

## Flujo completo

```
USER INPUT: "¿Debería hacer ayuno intermittent?"

  ↓

1. SimulationOrchestrator.run_tick()
   → Ejecuta 18 agentes deterministas
   → Recopila signals

  ↓

2. Moderator.moderate_intervention("ayuno_16_8", user_data, agent_outputs)
   
   a) Dr. Hallmarks.valida("ayuno_16_8")
      → Evidence: A | Grade: STRONG FOR ✅
   
   b) Dr. Mechanism.valida("ayuno_16_8")
      → Mechanistically plausible ✅
   
   c) Consensus Engine analiza 18 agentes
      → 8/18 concuerdan (buena mayoría)
      → Confidence: 0.82
   
   d) Hard Constraints valida efectos proyectados
      → LDL -8mg/dL es biológicamente possible ✅
   
  ↓

3. ModeratorOutput.to_user_friendly()
   → Texto legible para el usuario
   → Disclaimer médico incluido
   → Level de evidencia visible
   → Caveats y riesgos listados
```