#!/usr/bin/env python3
"""Test import chain for BioFish AI modules."""
import sys
sys.path.insert(0, '/workspace/biofish-ai')

results = []

# Step 1: llm_client
try:
    from src import llm_client as lc
    results.append(("llm_client", "OK"))
except Exception as e:
    results.append(("llm_client", str(e)[:80]))

# Step 2: agent
try:
    from src import agent as ag
    results.append(("agent", "OK"))
except Exception as e:
    results.append(("agent", str(e)[:80]))

# Step 3: agent_llm (depends on llm_client)
try:
    from src import agent_llm as al
    results.append(("agent_llm", f"OK ({len(al.SYSTEM_PROMPTS)} prompts)"))
except Exception as e:
    results.append(("agent_llm", str(e)[:120]))

# Step 4: orchestrator
try:
    from src import orchestrator as orch
    results.append(("orchestrator", "OK"))
except Exception as e:
    results.append(("orchestrator", str(e)[:80]))

# Step 5: run simulation
if "OK" in results[-1][1] if results else False:
    try:
        USER = {
            'chronological_age':40,'sex':'male',
            'ldl_cholesterol':155,'hdl_cholesterol':42,'triglycerides':210,
            'glucose_fasting':102,'hba1c':5.8,'homa_ir':3.2,
            'c_reactive_protein':3.5,'systolic_bp':135,'vo2max':32,
            'sleep_hours':6,'hrv_sdnn':32,'alt':38,'egfr':85,'creatinine_male':1.0,
            'leukocytes':7500,'lymphocyte_pct':32,'mcv':89,'red_dist_width':13.5,
            'alkaline_phosphatase':80,'tsh':2.5,'testosterone_male':450,
            'cortisol_morning':18,'vitamin_d':22,'vitamin_b12':350,'homocysteine':12,
            'bmi':28,'waist_circumference_male':98,'body_fat_pct_male':26,
            'exercise_minutes_per_week':60,'nadi_level':65,
        }
        orch.orchestrator.initialize_user(USER)
        r = orch.orchestrator.run_tick(tick=6, intervention='combinacion_ejercicio_diana')
        ldl = r.user_data.get('ldl_cholesterol')
        ens = r.ensemble_summary.get('ensemble_biological_age')
        results.append(("simulation", f"OK LDL={ldl}, ENS={ens}"))
    except Exception as e:
        results.append(("simulation", f"FAIL: {e}"[:80]))

# Print results
for name, status in results:
    ok = "OK" in status or "OK" in name
    print(f"  {'OK' if ok else 'FAIL'}  {name}: {status}")
