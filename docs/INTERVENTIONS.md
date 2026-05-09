# Intervention Comparison — BioFish AI

> **Compara intervenciones para un paciente específico y elige la mejor.**

## Uso

```bash
python examples/intervention_comparison.py
```

## Caso de estudio

**Perfil:** Hombre 45 años, LDL 168 mg/dL, Triglicéridos 230, HOMA-IR 3.8, PCR 2.8

**Pregunta:** ¿Qué intervención es mejor para reducir mis triglicéridos?

## Interventions disponibles

| ID | Nombre | Efecto en TG/mes | Evidencia | Tiempo |
|---|---|---|---|---|
| `omega3_epa_dha_2g` | Omega-3 2g/día | -20 mg/dL | 🟢 Level A | 3 meses |
| `ayuno_intermitente_16_8` | Ayuno 16:8 | -15 mg/dL | 🟢 Level A | 3 meses |
| `dieta_mediterranea` | Mediterránea | -10 mg/dL | 🟢 Level A | 3 meses |
| `combinacion_ejercicio_diana` | Plan Combinado | -25 mg/dL | 🟢 Level A | 3 meses |

## Resultados esperados

```
Comparación de intervenciones para reducir Triglicéridos
(Usuario: hombre 45 años, baseline TG=230 mg/dL)

Intervención                 | Mes 1   | Mes 3   | Mes 6   | Δ Total
----------------------------|---------|---------|---------|-------
Omega-3 2g/día              | -6.7    | -20.0   | -20.0   | -20.0
Plan Combinado               | -8.3    | -25.0   | -25.0   | -25.0  ⭐
Ayuno 16:8                   | -5.0    | -15.0   | -15.0   | -15.0
Dieta Mediterránea           | -3.3    | -10.0   | -10.0   | -10.0
Sin intervención (baseline)  | 0       | 0       | 0       | 0

⭐ El Plan Combinado es el más efectivo para reducir triglicéridos
   basado en evidencia Level A.

PEERO: requiere más adherencia del paciente.
   Si el paciente no puede hacer ejercicio intenso,
   Omega-3 es la segunda mejor opción con solo 1 pastilla al día.
```

## Ver también

- [API docs](../api/API.md)
- [Biological Clocks](CLOCKS.md)
- [Moderator](MODERATOR.md)