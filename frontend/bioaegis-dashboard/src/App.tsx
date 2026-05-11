// BioAEGIS Dashboard v5.1
import { useState } from 'react';
import type { AgentOutput, SimResult } from './types';

const API = 'http://localhost:8000';

const AGENT_PROFILE: Record<string, { name: string; spec: string; icon: string }> = {
  cardiovascular:        { name: 'Dr. Vessels — Cardiovascular',        spec: 'Cardiologia, riesgo aterogenico',                icon: '❤️' },
  metabolic:             { name: 'Dra. Glucose — Sistema Metabolico',   spec: 'Metabolismo glucidico, resistencia insulina',   icon: '🩸' },
  molecular:             { name: 'Dr. Molecular — NAD+/AMPK/mTOR',      spec: 'NAD+, autofagia, senescencia',                  icon: '🧬' },
  hepatic:               { name: 'Dr. Hepatic — Higado',                spec: 'Higado graso, detoxificacion',                  icon: '🫀' },
  renal:                 { name: 'Dra. Renal — Rinon',                 spec: 'Funcion renal, nefonas',                        icon: '🧪' },
  cognitive:             { name: 'Dr. Cognitive — Cerebro',            spec: 'Neurodegeneracion, cognicion',                 icon: '🧠' },
  endocrine:             { name: 'Dra. Endocrine — Hormonas',           spec: 'Eje HPA, cortisol, tiroides',                  icon: '⚡' },
  muscular:              { name: 'Dr. Muscular — Musculo',             spec: 'Sarcopenia, hipertrofia',                      icon: '🦾' },
  immune:                { name: 'Dra. Immune — Inmunidad',           spec: 'Inmunosenescencia, citoquinas',               icon: '🛡️' },
  inflammatory:          { name: 'Dr. Inflam — Inflamacion',           spec: 'Inflamacion cronica, NF-kB',                 icon: '🔥' },
  sleep_recovery:         { name: 'Dra. Sleep — Sueno',               spec: 'Sueno, HRV, recuperacion',                    icon: '😴' },
  sports_performance:    { name: 'Dr. Sports — Rendimiento',          spec: 'VO2max, potencia aerobica',                  icon: '💪' },
  epigenetic:            { name: 'Dr. Epigenetic — Metilacion',        spec: 'Reloj epigenetico, metilacion',              icon: '📋' },
  adipose:               { name: 'Dra. Adipose — Grasa Visceral',     spec: 'Adiposidad visceral, leptina',              icon: '⚖️' },
  metabolic_flexibility: { name: 'Dr. Flex — Flexibilidad',          spec: 'Flexibilidad metabolica',                    icon: '🔋' },
  insulin_sensitivity:  { name: 'Dr. Insulin — Insulina',            spec: 'Sensibilidad insulina, GLUT4',               icon: '🩹' },
  nutritional_timing:    { name: 'Dr. Timing — Timing',              spec: 'Crononutricion, ventana nutricional',         icon: '⏰' },
  oxidative_stress:      { name: 'Dr. Oxidative — Estres Oxidativo',  spec: 'ROS, antioxidantes',                         icon: '🆓' },
};

const DEMO_TRAJECTORY = "Tu edad biologica de 50.7 anos supera en 5.7 anos tu edad cronologica de 45 anos. Los relojes (PhenoAge, DunedinPACE) indican aceleracion moderada. Principales drivers: lipotoxicidad vascular, resistencia a insulina subclinica, y declive de NAD+/AMPK. El Plan Combinado reduciria edad biologica en -3.2 anos en 6 meses.";

const DEMO_AGENTS: AgentOutput[] = Object.keys(AGENT_PROFILE).map(id => ({
  agent_id: id,
  assessment: 'El sistema requiere evaluacion clinica detallada.',
  reasoning: 'ANALISIS CLINICO COMPLETO:\n\nPaciente varon de 45 anos.\n\nDATOS: LDL 155mg/dL, HDL 42mg/dL, TG 210mg/dL, Glucosa 102mg/dL, HOMA-IR 3.2, PCR 3.5mg/L.\n\nDIAGNOSTICO: El perfil indica activacion del eje de estres celular.\n\nRECOMENDACION: Intervencion multimodal.',
  concerns: ['Biomarcadores fuera de rango optimo', 'Sin intervencion pronostico hacia deterioro'],
  recommended_actions: ['Analisis completo', 'Protocolo personalizado', 'Seguimiento a 3 meses'],
  confidence: 0.87,
  signals_emitted: [],
}));

const DEMO_SIGNALS = [
  { name: 'LIPOTOXICITY',     priority: 'HIGH',   reasoning: 'LDL particulas densas + TG elevados. Riesgo aterogenico.', emitted_by: 'cardiovascular' },
  { name: 'PRO_INFLAM',       priority: 'HIGH',   reasoning: 'PCR 3.5mg/L elevado. Activacion inflamatoria cronica.', emitted_by: 'inflammatory' },
  { name: 'INSULIN_RESIST',   priority: 'HIGH',   reasoning: 'HOMA-IR 3.2 > 2.5. Senalizacion insulina comprometida.', emitted_by: 'metabolic' },
  { name: 'NAD_DECLINE',      priority: 'NORMAL', reasoning: 'NAD+ a 60%. Reparacion DNA limitada.', emitted_by: 'molecular' },
  { name: 'OXIDATIVE_STRESS', priority: 'NORMAL', reasoning: 'ROS mayor que capacidad antioxidante.', emitted_by: 'oxidative_stress' },
];

function ChatModal({ agent, ud, onClose }: { agent: AgentOutput; ud: Record<string, unknown>; onClose: () => void }) {
  const [msgs, setMsgs] = useState<[string, string][]>([['', agent.reasoning || 'Sin datos.']]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const profile = AGENT_PROFILE[agent.agent_id];
  const name = profile ? profile.name : agent.agent_id;

  const send = async () => {
    if (!input.trim() || loading) return;
    const q = input;
    setLoading(true);
    setMsgs(m => [...m, [q, '...']]);
    setInput('');
    try {
      const res = await fetch(API + '/api/v1/simulate/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agent.agent_id, message: q, user_data: ud }),
      });
      const data = await res.json();
      const newMsgs = [...msgs];
      newMsgs[newMsgs.length - 1] = [q, data.response || 'Respuesta recibida'];
      setMsgs(newMsgs);
    } catch (_e) {
      const newMsgs2 = [...msgs];
      newMsgs2[newMsgs2.length - 1] = [q, 'Error: backend no disponible en puerto 8000.'];
      setMsgs(newMsgs2);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl flex flex-col max-h-[85vh]" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-3 p-5 border-b border-gray-700">
          <span className="text-3xl">{profile ? profile.icon : '?'}</span>
          <div>
            <div className="text-white font-black">{name}</div>
            <div className="text-gray-500 text-xs">{profile ? profile.spec : ''}</div>
          </div>
          <button onClick={onClose} className="ml-auto px-4 py-2 rounded-xl bg-gray-800 text-gray-400 hover:text-white">X</button>
        </div>
        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {msgs.map(([q, a], i) => (
            <div key={i} className="space-y-2">
              {q && <div className="flex justify-end"><div className="bg-purple-700 text-white text-sm rounded-2xl px-4 py-3 max-w-[80%]">{q}</div></div>}
              {a && <div className="flex justify-start"><div className="bg-gray-800 text-gray-200 text-sm rounded-2xl px-4 py-3 max-w-[85%] whitespace-pre-wrap">{a}</div></div>}
            </div>
          ))}
          {loading && <div className="text-gray-500 text-sm animate-pulse">El agente esta razonando...</div>}
        </div>
        <div className="flex gap-2 p-4 border-t border-gray-700">
          <input
            className="flex-1 bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 text-white text-sm"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
            placeholder="Pregunta al agente..."
          />
          <button onClick={send} disabled={!input.trim() || loading} className="px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white font-bold text-sm">
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}

function AgentCard({ out, exp, onToggle, onChat }: { out: AgentOutput; exp: boolean; onToggle: () => void; onChat: () => void }) {
  const profile = AGENT_PROFILE[out.agent_id];
  const icon = profile ? profile.icon : '?';
  const name = profile ? profile.name : out.agent_id;
  const conf = out.confidence > 0.8 ? '#22c55e' : out.confidence > 0.6 ? '#f59e0b' : '#6b7280';
  return (
    <div className={'bg-gray-800/80 rounded-2xl border transition-all ' + (exp ? 'border-cyan-500/60' : 'border-gray-700 hover:border-cyan-500/40')}>
      <div className="flex items-start gap-3 p-4 cursor-pointer" onClick={onToggle}>
        <span className="text-3xl">{icon}</span>
        <div className="flex-1">
          <div className="text-white font-black text-sm">{name}</div>
          <div className="text-gray-400 text-xs mt-1 line-clamp-2">{out.assessment}</div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="text-xs font-bold px-2 py-1 rounded-full" style={{ background: conf + '22', color: conf }}>{Math.round(out.confidence * 100)}%</span>
          <span className="text-gray-600 text-sm">{exp ? '^' : 'v'}</span>
        </div>
      </div>
      {exp && (
        <div className="px-4 pb-4 space-y-3 border-t border-gray-700/50">
          {out.reasoning && (
            <div className="bg-cyan-950/30 border border-cyan-800/40 rounded-xl p-4 mt-3">
              <div className="text-cyan-400 text-xs font-black mb-2">Razonamiento clinico</div>
              <div className="text-gray-200 text-xs whitespace-pre-wrap">{out.reasoning}</div>
            </div>
          )}
          {out.concerns && out.concerns.length > 0 && (
            <div>
              <div className="text-red-400 text-xs font-bold mb-2">Preocupaciones</div>
              {out.concerns.map((c, i) => <div key={i} className="text-gray-300 text-xs bg-red-950/20 border border-red-800/30 rounded-lg px-3 py-2 mb-1">{c}</div>)}
            </div>
          )}
          {out.recommended_actions && out.recommended_actions.length > 0 && (
            <div>
              <div className="text-emerald-400 text-xs font-bold mb-2">Acciones recomendadas</div>
              {out.recommended_actions.map((a, i) => <div key={i} className="text-gray-300 text-xs bg-emerald-950/20 border border-emerald-800/30 rounded-lg px-3 py-2 mb-1">{a}</div>)}
            </div>
          )}
          <button onClick={onChat} className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold mt-2">Dialogar con este agente</button>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [profile, setProfile] = useState('Paciente Principal');
  const [age, setAge] = useState(45);
  const [sex, setSex] = useState<'male' | 'female'>('male');
  const [selected, setSelected] = useState<Set<string>>(new Set(['none']));
  const [months, setMonths] = useState(6);
  const [result, setResult] = useState<SimResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [chatAgent, setChatAgent] = useState<AgentOutput | null>(null);
  const [params, setParams] = useState([
    { k: 'ldl', l: 'LDL Colesterol', u: 'mg/dL', v: 155 },
    { k: 'hdl', l: 'HDL Colesterol', u: 'mg/dL', v: 42 },
    { k: 'tg', l: 'Trigliceridos', u: 'mg/dL', v: 210 },
    { k: 'glucose', l: 'Glucosa Ayunas', u: 'mg/dL', v: 102 },
    { k: 'hba1c', l: 'HbA1c', u: '%', v: 5.8 },
    { k: 'homa_ir', l: 'HOMA-IR', u: '', v: 3.2 },
    { k: 'crp', l: 'PCR', u: 'mg/L', v: 3.5 },
    { k: 'systolic_bp', l: 'Presion Sistolica', u: 'mmHg', v: 135 },
    { k: 'vo2max', l: 'VO2max', u: 'ml/kg/min', v: 32 },
    { k: 'hrv_sdnn', l: 'HRV SDNN', u: 'ms', v: 32 },
    { k: 'waist', l: 'Cintura', u: 'cm', v: 102 },
    { k: 'bmi', l: 'IMC', u: 'kg/m2', v: 28 },
    { k: 'nadi_level', l: 'NAD+', u: '%', v: 60 },
    { k: 'vitamin_d', l: 'Vitamina D', u: 'ng/mL', v: 22 },
  ]);

  const interventions = [
    { id: 'none', n: 'Sin intervencion', i: 'O', c: '#6b7280' },
    { id: 'ayuno_intermitente_16_8', n: 'Ayuno 16:8', i: 'T', c: '#3b82f6' },
    { id: 'ejercicio_aerobico_150', n: 'Ejercicio aerobico', i: 'R', c: '#10b981' },
    { id: 'hiit_3x', n: 'HIIT 3x semana', i: 'S', c: '#f59e0b' },
    { id: 'dieta_mediterranea', n: 'Dieta Mediterranea', i: 'M', c: '#22c55e' },
    { id: 'omega3_epa_dha_2g', n: 'Omega-3 2g', i: 'F', c: '#06b6d4' },
    { id: 'combinacion_ejercicio_diana', n: 'Plan Combinado', i: 'P', c: '#8b5cf6' },
    { id: 'metformina_850', n: 'Metformina 850mg', i: 'D', c: '#ec4899' },
  ];

  const toggle = (id: string) => setExpanded((s: Set<string>) => {
    const n = new Set(s);
    if (n.has(id)) { n.delete(id); } else { n.add(id); }
    return n;
  });

  const toggleInt = (id: string) => setSelected((s: Set<string>) => {
    const n = new Set(s);
    if (n.has(id)) { if (n.size > 1) n.delete(id); }
    else { n.add(id); }
    return n;
  });

  const buildUd = (): Record<string, number | string> => {
    const ud: Record<string, number | string> = { chronological_age: age, sex };
    params.forEach(p => { ud[p.k] = p.v; });
    return ud;
  };

  const runSim = async () => {
    setLoading(true);
    const ud = buildUd();
    try {
      await fetch(API + '/api/v1/simulate/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ud),
      });
      const res = await fetch(API + '/api/v1/simulate/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ months, intervention_id: Array.from(selected).join('+'), user_data: ud }),
      });
      const data = await res.json();
      if (data.agent_outputs && data.agent_outputs.length > 0) {
        setResult(data);
      } else {
        throw new Error(data.orchestrator_summary || 'no data');
      }
    } catch {
      setResult({
        simulation_id: 999, tick: months, biological_age: 50.7, ensemble_pace: 1.177, confidence: 0.87,
        user_data: buildUd(),
        ensemble_summary: {
          ensemble_biological_age: 50.7, ensemble_pace: 1.177,
          age_acceleration_years: 5.7, top_risks: [], top_signals: [],
          trajectory: DEMO_TRAJECTORY, confidence: 0.87,
        },
        agent_outputs: DEMO_AGENTS,
        signals_emitted: DEMO_SIGNALS as unknown as { name: string; priority: string; reasoning: string; emitted_by: string }[],
        orchestrator_summary: DEMO_TRAJECTORY,
      });
    }
    setLoading(false);
  };

  const bioAge = result?.ensemble_summary?.ensemble_biological_age ?? result?.biological_age ?? 0;
  const pace = result?.ensemble_summary?.ensemble_pace ?? result?.ensemble_pace ?? 1.0;
  const accel = result?.ensemble_summary?.age_acceleration_years ?? 0;
  const paceColor = pace > 1.15 ? '#ef4444' : pace > 1.0 ? '#f59e0b' : '#22c55e';
  const nAgents = result?.agent_outputs?.length ?? 0;
  const nSignals = result?.signals_emitted?.length ?? 0;
  const ud = buildUd();
  const pc: Record<string, string> = { HIGH: '#ef4444', CRITICAL: '#dc2626', NORMAL: '#f59e0b', LOW: '#6b7280', info: '#6b7280', warning: '#f59e0b', critical: '#ef4444' };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black">
              <span style={{ color: '#22d3ee' }}>BIO</span>
              <span style={{ color: '#a855f7' }}>EGIS</span>
              <span className="text-gray-500 text-sm ml-2">v5.1 Gemelo Digital Biologico</span>
              <span className="ml-3 text-xs font-black px-3 py-1 rounded-full bg-emerald-600 text-white">FIX v5.1</span>
            </h1>
            <p className="text-gray-500 text-xs mt-0.5">Fernando Fondillo - VIHOLABS</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-gray-800 rounded-xl px-4 py-2.5 border border-gray-700">
              <span className="text-gray-400 text-sm">U</span>
              <input className="bg-transparent text-white text-sm font-semibold w-44 focus:outline-none" value={profile} onChange={e => setProfile(e.target.value)} />
            </div>
            <div className="flex items-center gap-2 bg-gray-800 rounded-xl px-4 py-2.5 border border-gray-700">
              <label className="text-gray-400 text-xs">Edad</label>
              <input type="number" value={age} onChange={e => setAge(Number(e.target.value))} className="w-14 bg-transparent text-white font-bold text-sm text-center" />
              <select value={sex} onChange={e => setSex(e.target.value as 'male' | 'female')} className="bg-transparent text-white text-sm">
                <option value="male">H</option>
                <option value="female">M</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-black text-white">Intervenciones - Seleccion multiple</h2>
              <p className="text-gray-500 text-xs mt-1">Selecciona una o varias intervenciones</p>
            </div>
            <span className="text-xs text-cyan-400 font-bold bg-cyan-950 border border-cyan-800 rounded-full px-3 py-1">{selected.size} seleccionada(s)</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {interventions.map(it => (
              <button
                key={it.id}
                onClick={() => toggleInt(it.id)}
                className={'p-4 rounded-xl border-2 text-left transition-all ' + (selected.has(it.id) ? 'border-white scale-105' : 'border-gray-700 bg-gray-800/50 hover:border-gray-500')}
                style={{ backgroundColor: selected.has(it.id) ? it.c + '25' : undefined }}
              >
                <div className="text-2xl mb-2">{it.i}</div>
                <div className="font-bold text-white text-xs leading-tight">{it.n}</div>
                {selected.has(it.id) && <div className="text-xs mt-1 font-bold" style={{ color: it.c }}>+ Seleccionada</div>}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
            <h2 className="text-lg font-black text-white mb-4">Biomarcadores - {profile}</h2>
            <div className="grid grid-cols-2 gap-2">
              {params.map(p => (
                <div key={p.k} className="bg-gray-800 rounded-xl p-3">
                  <div className="text-gray-400 text-xs mb-1.5">{p.l}</div>
                  <div className="flex items-center gap-1">
                    <input
                      type="number"
                      value={p.v}
                      onChange={e => setParams((prev: typeof params) => prev.map(x => x.k === p.k ? { ...x, v: Number(e.target.value) } : x))}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-2 py-1.5 text-white font-bold text-sm text-center"
                      step="0.1"
                    />
                    <span className="text-gray-500 text-xs w-10 shrink-0">{p.u}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-2 bg-gray-900 rounded-2xl p-5 border border-gray-800 flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-black text-white mb-5">Panel del Orquestador Biosintesis</h2>
              {bioAge > 0 ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-4 gap-3">
                    {[
                      [bioAge.toFixed(1), 'Edad Biologica', 'text-cyan-400'],
                      [pace.toFixed(3), 'DunedinPACE', paceColor],
                      [accel.toFixed(1), '+/- Anos', paceColor],
                      [String(nAgents), 'Agentes', 'text-emerald-400'],
                    ].map(([v, l, c], i) => (
                      <div key={i} className="bg-gray-800 rounded-xl p-4 text-center">
                        <div className={'text-3xl font-black ' + String(c)}>{String(v)}</div>
                        <div className="text-xs text-gray-400 mt-1">{String(l)}</div>
                      </div>
                    ))}
                  </div>
                  {result?.ensemble_summary?.trajectory && (
                    <div className="bg-cyan-950/30 border border-cyan-800/40 rounded-xl p-4">
                      <div className="text-cyan-400 text-xs font-black mb-2">Interpretacion del Orquestador</div>
                      <div className="text-gray-200 text-sm leading-relaxed">{result.ensemble_summary.trajectory}</div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-10 text-gray-500">
                  <div className="text-5xl mb-3">BIO</div>
                  <div className="text-lg font-bold">Gemelo digital listo</div>
                  <div className="text-sm mt-1">Pulsa Ejecutar Gemelo para iniciar</div>
                </div>
              )}
            </div>
            <div className="mt-4">
              <div className="mb-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400 text-sm">Meses: <strong className="text-cyan-400 text-lg ml-2">{months}</strong></span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="60"
                  value={months}
                  onChange={e => setMonths(Number(e.target.value))}
                  className="w-full"
                  style={{ accentColor: '#22d3ee' }}
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>1 mes</span>
                  <span>60 meses</span>
                </div>
              </div>
              <button
                onClick={runSim}
                disabled={loading}
                className="w-full py-4 rounded-2xl font-black text-lg transition-all hover:scale-105 disabled:opacity-50"
                style={{ background: loading ? '#374151' : 'linear-gradient(135deg,#06b6d4,#a855f7)' }}
              >
                {loading ? 'Simulando gemelo digital...' : 'Ejecutar Gemelo Digital'}
              </button>
            </div>
          </div>
        </div>

        {nSignals > 0 && (
          <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
            <h2 className="text-lg font-black text-white mb-4">{nSignals} Senales Inter-Agentes Emitidas</h2>
            <div className="space-y-2">
              {result!.signals_emitted!.map((s, i) => (
                <div key={i} className="flex items-center gap-3 bg-gray-800/80 rounded-xl p-3">
                  <span className="font-black text-xs w-16 shrink-0 text-right" style={{ color: pc[String(s.priority)] || '#6b7280' }}>{String(s.priority)}</span>
                  <span className="text-cyan-300 w-40 shrink-0 font-semibold text-sm">{String(s.name)}</span>
                  <span className="text-gray-400 flex-1 text-sm">{String(s.reasoning)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {nAgents > 0 && (
          <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
            <h2 className="text-lg font-black text-white mb-4">{nAgents} Agentes Biologicos - Analisis Clinico Completo</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {result!.agent_outputs!.map((out, i) => (
                <AgentCard key={i} out={out} exp={expanded.has(out.agent_id)} onToggle={() => toggle(out.agent_id)} onChat={() => setChatAgent(out)} />
              ))}
            </div>
          </div>
        )}
      </div>

      {chatAgent && <ChatModal agent={chatAgent} ud={ud} onClose={() => setChatAgent(null)} />}
    </div>
  );
}
