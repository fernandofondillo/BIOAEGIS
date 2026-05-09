# Biological Clocks — BioFish AI

> **Cómo medimos tu edad biológica y velocidad de envejecimiento.**

## Conceptos fundamentales

### Edad cronológica vs. biológica

```
EDAD CRONOLÓGICA: los años que has vivido
EDAD BIOLÓGICA: cómo de envejecido está tu cuerpo por dentro
VELOCIDAD DE ENVEJECIMIENTO: cuántos años biológicos envejece tu cuerpo por cada año cronológico
```

Ejemplos reales:
- Persona de 40 años con buena biología → edad biológica 36 (envejeces 10% más lento)
- Persona de 40 años con mala biología → edad biológica 52 (envejeces 30% más rápido)
- Persona de 70 años con excelente biología → edad biológica 55 (parece de 55 a los 70)

---

## Los 4 Relojes

### 1. PhenoAge (Levine 2018, PNAS)

**Paper:** Levine et al. "Ageing-associated decline in biological age." PNAS 2018

**Qué mide:** Estado funcional de tus órganos y sistemas (no solo tiempo vivido).

**Biomarcadores usados (9):**
```
1. Albúmina (g/dL) — función hepática y nutricional
2. Creatinina (mg/dL) — función renal
3. Glucosa (mg/dL) — metabolismo
4. Log(CRP) — inflamación
5. Linfocitos (%) — sistema inmune
6. VCM (fL) — tamaño de glóbulos rojos
7. RDW (%) — variabilidad del tamaño de glóbulos rojos
8. Fosfatasa alcalina (U/L) — función hepática y ósea
9. Edad cronológica
```

**Cómo funciona:**
```python
# Simplified formula
linear_predictor = (
    -19.9067
    + 0.0924 * albumin
    + 0.0016 * creatinine
    + 19.2248 / log(crp)
    + 0.1744 * glucose
    + 0.0734 * lymphocyte_pct
    - 0.0584 * mcv
    + 0.0092 * rdw
    + 0.0195 * alp
    + 0.0792 * chronological_age
)
PhenoAge = 141.5 + log(...) * 10.79
```

**Interpretación:**
| Age Acceleration | Significado |
|---|---|
| < -5 años | Excepcionalmente joven biológicamente |
| -5 a 0 años | Buena biología para tu edad |
| 0 a +5 años | Envejecimiento moderado |
| +5 a +10 años | Envejecimiento acelerado |
| > +10 años | Envejecimiento muy acelerado |

---

### 2. Zhang Age (Zhang 2020, Nature Aging)

**Paper:** Zhang et al. "A new aging-measuring instrument." Nature Aging 2020

**Qué mide:** Envejecimiento funcional de 16 órganos/sistemas.

**Biomarcadores usados (16):**
```
ALT, albúmina, fosfatasa alcalina, creatinina, urea, glucosa,
CRP, VCM, recuento de glóbulos rojos, eosinófilos,
volumen plaquetario medio, leucocitos, linfocitos, neutrófilos,
HDL colesterol, ácido úrico + edad cronológica
```

**Ventaja sobre PhenoAge:** Usa marcadores hepáticos, renales y lipídicos más diversos.

---

### 3. DunedinPACE (Belsky 2022, eLife) ⚡

**Paper:** Belsky et al. "DunedinPACE." eLife 2022

**Qué mide:** La **velocidad** a la que estás envejeciendo.

Este es el reloj más innovador. Mientras PhenoAge y Zhang dicen *"cuántos años biológicos tienes"*, DunedinPACE dice *"cuántos años biológicos envejeces por cada año cronológico"*.

**Cómo funciona:**
```python
# No usa una fórmula directa — requiere datos longitudinales
# (3 analíticas en 12 años para el estudio original)
# BioFish usa una versión cross-sectional proxy:

DunedinPACE = 1 + (biological_age - chronological_age) / chronological_age

Ejemplos:
  PACE = 1.30 → Envejeces 30% más rápido que el promedio
  PACE = 1.00 → Envejeces al ritmo promedio
  PACE = 0.85 → Envejeces 15% más lento que el promedio
```

**Interpretación:**
| PACE | Significado clínico |
|---|---|
| > 1.5 | Envejecimiento severamente acelerado |
| 1.2 - 1.5 | Envejecimiento acelerado |
| 0.9 - 1.1 | Envejecimiento promedio (población general) |
| 0.75 - 0.9 | Envejecimiento lento |
| < 0.75 | Envejecimiento excepcionalmente lento (como centenarios) |

**Evidencia:**
- Cada 0.1 de aumento en PACE = +5% riesgo de enfermedad cardiovascular
- Cada 0.1 de aumento en PACE = +6% riesgo de demencia
- Cada 0.1 de aumento en PACE = +4% riesgo de mortalidad

---

### 4. Lifestyle Age (Meta-análisis propietario)

**Qué mide:** El impacto de tu estilo de vida en tu edad biológica.

**Factores incluidos:**
```
🏃 Ejercicio:
   VO2max < 20 → +8 años
   VO2max 20-28 → +3 años
   VO2max 38-45 → -4 años
   < 30min/semana → +1.5 años

😴 Sueño:
   < 5.5h → +3 años
   < 6.5h → +1.5 años
   7-8h → -1 año

⚖️ Obesidad:
   IMC > 40 → +7 años
   IMC 35-40 → +4 años
   IMC 30-35 → +2.5 años
   IMC 22-25 → -1 año
   Cintura > 110cm → +4 años

🚬 Tabaco:
   Fumador actual → +5 años
   Ex-fumador → +0.1 × años desde que dejarlo

🍷 Alcohol:
   > 14 bebidas/semana → +3 años
   7-14 bebidas/semana → +1 año
   0 (no bebedor) → +0.5 años
   1-7 bebidas/semana → -1 año (protective)

🥗 Dieta mediterránea:
   Adherencia > 0.7 → -2 años
   Adherencia 0.4-0.7 → -0.5 años

😰 Estrés:
   Estrés alto (>0.7/1.0) → +2.5 años
   Estrés moderado → +1 año
```

---

## Ensemble Clock

BioFish combina los 4 relojes en un resultado ensemble:

```python
EnsembleClock.calculate(biomarkers)
# → {
#     "ensemble_biological_age": 45.8,
#     "ensemble_acceleration": 5.8,
#     "ensemble_pace": 1.15,
#     "number_of_clocks": 3,
#     "clocks_included": ["PhenoAge", "Lifestyle Age", "DunedinPACE"],
#     "summary_interpretation": "⚡ Envejecimiento biológico acelerado..."
# }
```

**Cómo funciona:**
```
Ponderación por confianza:
  PhenoAge (confianza 0.85) → peso 0.85
  Lifestyle Age (confianza 0.80) → peso 0.80
  DunedinPACE (confianza 0.78) → peso 0.78

Weighted acceleration = Σ(acceleración × confianza) / Σ(confianza)
  = (8.3 × 0.85 + 4.1 × 0.80 + 0.16 × 40 × 0.78) / (0.85 + 0.80 + 0.78)
  = (7.06 + 3.28 + 4.99) / 2.43
  = 15.33 / 2.43
  = 6.3 años de aceleración ensemble
```

---

## Ejemplo práctico

```
USUARIO: Hombre, 40 años

Biomarcadores clave:
  LDL: 155 (alto)
  HDL: 42 (bajo)
  HOMA-IR: 3.2 (resistencia a insulina)
  PCR: 3.5 (inflamación elevada)
  VO2max: 32 (por debajo de la media)
  Sueño: 6.2h (marginal)
  Ejercicio: 60min/sem (insuficiente)

RESULTADOS:
  PhenoAge: 48.3 años (+8.3 de aceleración)
  Lifestyle: 44.1 años (+4.1 de aceleración)
  DunedinPACE: 1.21 (envejeces 21% más rápido)
  Ensemble: 45.8 años biológicos (+5.8 años)

CONCLUSIÓN:
  ⚡ Envejecimiento acelerado (+5.8 años)
  causa principal: LDL alto + inflamación + VO2max bajo
  recomendación: Plan Combinado (ejercicio + dieta + ayuno)
  impacto esperado: -2.4 años biológicos en 6 meses
```

---

## Limitaciones

1. **PhenoAge y Zhang** requieren analítica de sangre específica (no任何人 tiene MCV, RDW, etc.)
2. **DunedinPACE** está validado hasta los 45 años — extrapolación a mayores puede ser imprecisa
3. **Lifestyle Age** se basa en estimaciones de VO2max cuando no hay prueba de esfuerzo
4. Los relojes miden **correlación con mortalidad**, no causation directa
5. **Un reloj solo no es suficiente** — usar ensemble + contexto clínico

**No usar un solo reloj para decisiones médicas. Siempre complementar con analítica real y consejo profesional.**