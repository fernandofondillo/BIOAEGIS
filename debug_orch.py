#!/usr/bin/env python3
"""Debug script for BioFish AI orchestrator."""
import sys
sys.path.insert(0, '/workspace/biofish-ai')

from src.agent import agent_registry

profiles = agent_registry.get_all_profiles()
print(f"Profiles loaded: {len(profiles)}")

# Find cardiovascular profile
card = agent_registry.get_profile('cardiovascular')
print(f"Cardiovascular profile: {card}")

# Test _assess_cardiovascular
from src.orchestrator import SimulationOrchestrator

orch = SimulationOrchestrator()
print("Orchestrator instantiated")

# Simulate just the _run_agents method
USER = {
    'chronological_age':40,'sex':'male',
    'ldl_cholesterol':155,'hdl_cholesterol':42,'triglycerides':210,
    'glucose_fasting':102,'hba1c':5.8,'homa_ir':3.2,
    'c_reactive_protein':3.5,'systolic_bp':135,
}

# Call _run_agents directly
try:
    outputs = orch._run_agents(USER, 1)
    print(f"_run_agents returned: {len(outputs)} outputs")
except Exception as e:
    import traceback
    print(f"ERROR in _run_agents: {e}")
    traceback.print_exc()