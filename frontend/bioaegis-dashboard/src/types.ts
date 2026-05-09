export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AgentOutput {
  agent_id: string;
  assessment: string;
  concerns: string[];
  recommended_actions: string[];
  confidence: number;
  signals_emitted: { name: string; priority: string }[];
}

export interface EnsembleSummary {
  ensemble_biological_age: number;
  dunedin_pace: number;
  [key: string]: number | string;
}

export interface SimulationResult {
  tick: number;
  biological_age: number;
  ensemble_pace: number;
  confidence: number;
  user_data: Record<string, number>;
  agent_outputs: AgentOutput[];
  signals_emitted: { name: string; priority: string; reasoning: string }[];
  ensemble_summary?: EnsembleSummary;
  moderator_output?: {
    concerns: string[];
    trajectory: string;
    recommendations: string[];
    overall_confidence: number;
  };
}

export interface UserProfile {
  age: number;
  sex: 'male' | 'female';
  ldl: number; hdl: number; tg: number;
  glucose: number; hba1c: number; homa_ir: number;
  crp: number; systolic_bp: number; vo2max: number;
  sleep_hours: number; hrv_sdnn: number; alt: number; egfr: number;
  waist: number; bmi: number;
  exercise_minutes: number; nadi_level: number; vitamin_d: number;
}

export interface Intervention {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}