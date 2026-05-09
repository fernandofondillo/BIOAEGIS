"""
BioFish AI — Basic Simulation Example
===================================
Simulación determinista (sin LLM) de un paciente varón de 40 años
con perfil metabólico típico de alguien en pre-diabetes.

Ejecuta:
    python3 examples/basic_simulation.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import SimulationOrchestrator


def run_basic_simulation():
    print("=" * 60)
    print("🐟 BioFish AI — Basic Simulation")
    print("   Deterministic mode (no LLM required)")
    print("=" * 60)

    # Perfil de paciente: varón, 40 años, pre-diabetes
    patient = {
        # Identificación
        "chronological_age": 40.0,
        "sex": "male",
        "height_cm": 178.0,
        "weight_kg": 87.0,

        # Perfil lipídico
        "total_cholesterol": 215.0,
        "ldl_cholesterol": 138.0,
        "hdl_cholesterol": 38.0,
        "triglycerides": 195.0,

        # Glucosa / insulina
        "glucose_fasting": 108.0,
        "glucose_post_prandial": 148.0,
        "hba1c": 6.0,
        "insulin_fasting": 14.5,
        "homa_ir": 3.6,

        # Inflamación
        "c_reactive_protein": 3.2,
        "ferritin": 145.0,

        # Hepática
        "alt": 35.0,
        "ast": 28.0,
        "ggt": 38.0,
        "albumin": 4.2,

        # Renal
        "creatinine_male": 0.98,
        "egfr": 88.0,
        "urea_bun": 28.0,
        "uric_acid": 6.2,

        # Hemograma
        "leukocytes": 7200.0,
        "lymphocyte_pct": 34.0,
        "mcv": 88.0,
        "red_dist_width": 13.4,
        "alkaline_phosphatase": 75.0,

        # Hormonas
        "tsh": 2.2,
        "free_t3": 3.1,
        "free_t4": 1.18,
        "testosterone_male": 465.0,
        "cortisol_morning": 16.5,
        "dhea_s": 210.0,

        # Nutricionales
        "vitamin_d": 22.0,
        "vitamin_b12": 340.0,
        "folate_rbc": 290.0,
        "homocysteine": 11.5,

        # Composición corporal
        "bmi": 27.5,
        "waist_circumference_male": 100.0,
        "body_fat_pct_male": 27.0,

        # Cardiovascular
        "systolic_bp": 132.0,
        "diastolic_bp": 84.0,
        "hr_resting": 74.0,

        # Molecular / fitness
        "nadi_level": 68.0,
        "vo2max": 33.0,

        # Sueño / lifestyle
        "sleep_hours": 6.2,
        "hrv_sdnn": 34.0,
        "exercise_min_per_week": 45.0,
    }

    orch = SimulationOrchestrator()
    init_result = orch.initialize_user(patient)

    print(f"\n📊 Perfil: Hombre, 40 años")
    print(f"   LDL: {patient['ldl_cholesterol']} mg/dL (alto)")
    print(f"   HOMA-IR: {patient['homa_ir']} (resistencia a insulina)")
    print(f"   PCR: {patient['c_reactive_protein']} mg/L (elevada)")
    print(f"   VO2max: {patient['vo2max']} mL/kg/min (por debajo de la media)")

    print(f"\n📈 Biological Clocks (baseline):")
    ens = init_result["ensemble_summary"]
    print(f"   Edad biológica estimada: {ens.get('ensemble_biological_age', 'N/A')} años")
    print(f"   Acceleración: {ens.get('ensemble_acceleration', 'N/A')} años")
    print(f"   DunedinPACE: {ens.get('ensemble_pace', 'N/A')}")
    print(f"   Evaluación: {ens.get('summary_interpretation', 'N/A')[:60]}...")

    # ── ESCENARIO 1: Simular 6 meses con ayuno 16:8 ──────────────────────
    print("\n" + "-" * 60)
    print("📋 ESCENARIO 1: Ayuno Intermitente 16:8 durante 6 meses")
    print("-" * 60)

    r_ayuno = orch.run_tick(tick=6, intervention="ayuno_intermitente_16_8")

    print(f"   Biomarcadores después de 6 meses de ayuno 16:8:")
    print(f"   LDL: {r_ayuno.user_data.get('ldl_cholesterol')} (baseline: 138)")
    print(f"   HOMA-IR: {r_ayuno.user_data.get('homa_ir'):.2f} (baseline: 3.60)")
    print(f"   PCR: {r_ayuno.user_data.get('c_reactive_protein'):.1f} (baseline: 3.2)")
    print(f"   Triglicéridos: {r_ayuno.user_data.get('triglycerides')} (baseline: 195)")

    print(f"\n   Agentes activos: {len(r_ayuno.agent_outputs)}")
    concerns = [c for o in r_ayuno.agent_outputs for c in o.get("concerns", [])]
    print(f"   Preocupaciones detectadas: {len(concerns)}")
    for c in concerns[:4]:
        print(f"     • {c[:80]}")

    print(f"\n   Moderator confidence: {r_ayuno.moderator_output.get('confidence', 'N/A')}")

    # ── ESCENARIO 2: Plan Combinado ─────────────────────────────────────
    print("\n" + "-" * 60)
    print("📋 ESCENARIO 2: Plan Combinado (Ejercicio + Dieta) 6 meses")
    print("-" * 60)

    r_plan = orch.run_tick(tick=6, intervention="combinacion_ejercicio_diana")

    print(f"   Biomarcadores después de 6 meses del Plan Combinado:")
    print(f"   LDL: {r_plan.user_data.get('ldl_cholesterol')} (baseline: 138)")
    print(f"   HOMA-IR: {r_plan.user_data.get('homa_ir'):.2f} (baseline: 3.60)")
    print(f"   PCR: {r_plan.user_data.get('c_reactive_protein'):.1f} (baseline: 3.2)")
    print(f"   Triglicéridos: {r_plan.user_data.get('triglycerides')} (baseline: 195)")
    print(f"   VO2max: {r_plan.user_data.get('vo2max')} (baseline: 33)")

    print(f"\n   Comparación de escenarios:")
    print(f"   {'Intervención':<30} {'LDL final':>10} {'HOMA-IR final':>12} {'PCR final':>10}")
    print(f"   {'-'*30} {'-'*10} {'-'*12} {'-'*10}")
    print(f"   {'Baseline (sin intervención)':<30} {'138':>10} {'3.60':>12} {'3.2':>10}")
    print(f"   {'Ayuno 16:8 (6 meses)':<30} {r_ayuno.user_data.get('ldl_cholesterol'):>10} {r_ayuno.user_data.get('homa_ir'):>12.2f} {r_ayuno.user_data.get('c_reactive_protein'):>10.1f}")
    print(f"   {'Plan Combinado (6 meses)':<30} {r_plan.user_data.get('ldl_cholesterol'):>10} {r_plan.user_data.get('homa_ir'):>12.2f} {r_plan.user_data.get('c_reactive_protein'):>10.1f}")

    # ── ESCENARIO 3: Comparar Omega-3 y Metformina ────────────────────
    print("\n" + "-" * 60)
    print("📋 ESCENARIO 3: Impacto de Omega-3 vs Metformina")
    print("-" * 60)

    r_omega3 = orch.run_tick(tick=3, intervention="omega3_epa_dha_2g")
    r_metformina = orch.run_tick(tick=3, intervention="metformina_850")

    print(f"   Triglicéridos baseline: 195 mg/dL")
    print(f"   Triglicéridos con Omega-3 3 meses: {r_omega3.user_data.get('triglycerides')}")
    print(f"   Triglicéridos con Metformina 3 meses: {r_metformina.user_data.get('triglycerides')}")

    improvement = r_omega3.user_data.get('triglycerides', 195) - 195
    print(f"   Omega-3 reduce TG: {improvement:.0f} mg/dL en 3 meses")
    print(f"   Metformina reduce TG: {r_metformina.user_data.get('triglycerides') - 195:.0f} mg/dL en 3 meses")


if __name__ == "__main__":
    run_basic_simulation()