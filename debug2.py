#!/usr/bin/env python3
import sys, traceback
sys.path.insert(0, '/workspace/biofish-ai')

print("Starting BioFish AI debug...")

# Import agent FIRST (before anything else that might interfere)
print("Importing agent...")
try:
    from src.agent import agent_registry, get_all_profiles, AgentProfile, AgentOutput
    print(f"  agent OK: {len(get_all_profiles())} profiles")
except Exception as e:
    print(f"  agent FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Now other modules
print("Importing orchestrator...")
try:
    from src.orchestrator import SimulationOrchestrator
    print("  orchestrator OK")
except Exception as e:
    print(f"  orchestrator FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Try _run_agents
print("Running _run_agents...")
USER = {
    'ldl_cholesterol':155,'hdl_cholesterol':42,'triglycerides':210,
    'glucose_fasting':102,'hba1c':5.8,'homa_ir':3.2,
    'c_reactive_protein':3.5,'systolic_bp':135,'vo2max':32,
    'sleep_hours':6,'hrv_sdnn':32,'alt':38,'egfr':85,'creatinine_male':1.0,
    'leukocytes':7500,'lymphocyte_pct':32,'mcv':89,'red_dist_width':13.5,
    'alkaline_phosphatase':80,'tsh':2.5,'testosterone_male':450,
    'cortisol_morning':18,'vitamin_d':22,'vitamin_b12':350,'homocysteine':12,
    'bmi':28,'waist_circumference_male':98,'body_fat_pct_male':26,
    'exercise_minutes_per_week':60,'nadi_level':65,'chronological_age':40,'sex':'male',
}

try:
    o = SimulationOrchestrator()
    outputs = o._run_agents(USER, 1)
    print(f"  _run_agents OK: {len(outputs)} outputs")
except Exception as e:
    print(f"  _run_agents FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Full tick
print("Running initialize_user + run_tick...")
try:
    state = o.initialize_user(USER)
    print(f"  init OK: {state['status']}")
    r1 = o.run_tick(tick=1, intervention='ayuno_intermitente_16_8')
    print(f"  tick 1 OK: {len(r1.agent_outputs)} agents, confidence={r1.moderator_output.get('confidence')}")
    r3 = o.run_tick(tick=3, intervention='combinacion_ejercicio_diana')
    print(f"  tick 3 OK: LDL={r3.user_data.get('ldl_cholesterol')}, HOMA-IR={r3.user_data.get('homa_ir')}")
except Exception as e:
    print(f"  run_tick FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ ALL OK")