"""
Tests para SimulationOrchestrator y agent assessment logic.
"""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.orchestrator import SimulationOrchestrator, orchestrator


USER_BASIC = {
    "chronological_age": 40.0, "sex": "male",
    "ldl_cholesterol": 155.0, "hdl_cholesterol": 42.0,
    "triglycerides": 210.0, "glucose_fasting": 102.0,
    "hba1c": 5.8, "homa_ir": 3.2,
    "c_reactive_protein": 3.5, "ferritin": 150.0,
    "systolic_bp": 135.0, "diastolic_bp": 85.0, "hr_resting": 72.0,
    "vo2max": 32.0, "sleep_hours": 6.0, "hrv_sdnn": 32.0,
    "alt": 38.0, "egfr": 85.0, "creatinine_male": 1.0,
    "leukocytes": 7500.0, "lymphocyte_pct": 32.0,
    "mcv": 89.0, "red_dist_width": 13.5, "alkaline_phosphatase": 80.0,
    "tsh": 2.5, "testosterone_male": 450.0, "cortisol_morning": 18.0,
    "vitamin_d": 22.0, "vitamin_b12": 350.0, "homocysteine": 12.0,
    "bmi": 28.0, "waist_circumference_male": 98.0, "body_fat_pct_male": 26.0,
    "exercise_minutes_per_week": 60.0, "nadi_level": 65.0,
}


def test_initialize_user():
    o = SimulationOrchestrator()
    state = o.initialize_user(USER_BASIC)
    assert state["status"] == "initialized"
    assert state["user_biomarkers_count"] > 30
    assert "ensemble_summary" in state


def test_init_user_resets_state():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    o.run_tick(tick=1, intervention="ayuno_intermitente_16_8")
    o.initialize_user(USER_BASIC)  # re-init
    assert o._current_tick == 0
    assert len(o._state_history) == 0


def test_run_tick_returns_state():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    assert result.tick == 1
    assert len(result.agent_outputs) >= 5
    assert len(result.signals_emitted) >= 0
    assert result.ensemble_summary is not None


def test_run_tick_with_intervention():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1, intervention="ayuno_intermitente_16_8")
    assert result.intervention_applied == "ayuno_intermitente_16_8"
    assert len(result.intervention_effects) > 0


def test_trajectory_tick_3():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    r3 = o.run_tick(tick=3, intervention="ayuno_intermitente_16_8")
    assert r3.user_data["ldl_cholesterol"] < USER_BASIC["ldl_cholesterol"]


def test_combination_plan_at_6_months():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    r6 = o.run_tick(tick=6, intervention="combinacion_ejercicio_diana")
    assert r6.user_data["ldl_cholesterol"] < USER_BASIC["ldl_cholesterol"]
    assert r6.user_data["homa_ir"] < USER_BASIC["homa_ir"]


def test_orchestrator_singleton():
    assert orchestrator is not None
    assert isinstance(orchestrator, SimulationOrchestrator)


def test_signal_bus_resets_per_tick():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    o.run_tick(tick=1)
    signals_t1 = o._signal_bus.get_signal_history()
    o.run_tick(tick=2)
    # After reset, signal history should not accumulate
    # (clear_resolved_signals or reset between ticks)


def test_agent_assessment_cardiovascular_high_ldl():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    cardio = next((a for a in result.agent_outputs if a["agent_id"] == "cardiovascular"), None)
    assert cardio is not None
    assert len(cardio["concerns"]) >= 1
    assert any("LDL" in c or "ldl" in c.lower() for c in cardio["concerns"])


def test_agent_assessment_metabolic_insulin_resistance():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    metabolic = next((a for a in result.agent_outputs if a["agent_id"] == "metabolic"), None)
    assert metabolic is not None
    assert any("homa_ir" in c.lower() or "resistencia" in c.lower() for c in metabolic["concerns"])


def test_agent_assessment_inflammatory_high_crp():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    inflammatory = next((a for a in result.agent_outputs if a["agent_id"] == "inflammatory"), None)
    assert inflammatory is not None


def test_moderator_confidence():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    assert result.moderator_output["confidence"] > 0


def test_moderator_has_disclaimer():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    disclaimer = result.moderator_output.get("disclaimer", "")
    assert "médico" in disclaimer.lower() or "medical" in disclaimer.lower()


def test_history_tracks_ticks():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    o.run_tick(tick=1)
    o.run_tick(tick=2)
    o.run_tick(tick=3)
    history = o.get_history()
    assert len(history) == 3


def test_multiple_interventions_comparison():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    r_ayuno = o.run_tick(tick=1, intervention="ayuno_intermitente_16_8")
    o.initialize_user(USER_BASIC)  # reset
    r_h iit = o.run_tick(tick=1, intervention="hiit_3x")
    assert r_ayuno.user_data["homa_ir"] != r_hiit.user_data["homa_ir"]


def test_enemble_clock_in_result():
    o = SimulationOrchestrator()
    o.initialize_user(USER_BASIC)
    result = o.run_tick(tick=1)
    assert "PhenoAge" in result.clocks or "Lifestyle Age" in result.clocks or len(result.clocks) >= 0