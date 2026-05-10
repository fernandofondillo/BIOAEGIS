export interface AgentOutput {
  agent_id: string;
  agent_name?: string;
  assessment: string;
  reasoning: string;
  concerns: string[];
  recommended_actions: string[];
  confidence: number;
  signals_emitted: string[];
  validated_by_constraints?: boolean;
  validated_by_moderator?: boolean;
}

export interface Signal {
  name: string;
  priority: string;
  reasoning: string;
  emitted_by?: string;
}

export interface EnsembleSummary {
  ensemble_biological_age: number;
  ensemble_pace: number;
  age_acceleration_years: number;
  top_risks: string[];
  top_signals: string[];
  trajectory: string;
  confidence: number;
}

export interface SimResult {
  simulation_id?: number;
  tick?: number;
  biological_age: number;
  ensemble_pace: number;
  confidence: number;
  user_data: Record<string, number>;
  agent_outputs: AgentOutput[];
  signals_emitted: Signal[];
  orchestrator_summary: string;
  moderator_trajectory?: string;
  moderator_concerns?: string[];
  ensemble_summary?: EnsembleSummary;
  before_after?: Record<string, { before: number; after: number }>;
  intervention_name?: string;
}

export interface CustomParam {
  id: number;
  name: string;
  label: string;
  value: number;
  unit: string;
}

export interface CustomInt {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}
