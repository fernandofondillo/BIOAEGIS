// BioAEGIS Dashboard v4 — Fernando Fondillo / VIHOLABS
import { useState } from 'react';
import type { AgentOutput, SimResult } from './types';

const API = 'http://localhost:8000';

const ICONS: Record<string,string> = {
  cardiovascular:'❤️', metabolic:'🩸', molecular:'🧬', hepatic:'🫀',
  renal:'🧪', cognitive:'🧠', endocrine:'⚡', muscular:'🦾',
  immune:'🛡️', inflammatory:'🔥', sleep_recovery:'😴',
  sports_performance:'💪', epigenetic:'📋', adipose:'⚖️',
  metabolic_flexibility:'🔋', insulin_sensitivity:'🩹',
  nutritional_timing:'⏰', oxidative_stress:'🆓', default:'🦠',
};

const DEFAULTS = [
  { k:'ldl',l:'LDL Colesterol',u:'mg/dL',v:155 }, { k:'hdl',l:'HDL Colesterol',u:'mg/dL',v:42 },
  { k:'tg',l:'Triglicéridos',u:'mg/dL',v:210 }, { k:'glucose',l:'Glucosa Ayunas',u:'mg/dL',v:102 },
  { k:'hba1c',l:'HbA1c',u:'%',v:5.8 }, { k:'homa_ir',l:'HOMA-IR',u:'',v:3.2 },
  { k:'crp',l:'PCR',u:'mg/L',v:3.5 }, { k:'systolic_bp',l:'Presión Sistólica',u:'mmHg',v:135 },
  { k:'vo2max',l:'VO2max',u:'ml/kg/min',v:32 }, { k:'hrv_sdnn',l:'HRV SDNN',u:'ms',v:32 },
  { k:'waist',l:'Cintura',u:'cm',v:102 }, { k:'bmi',l:'IMC',u:'kg/m²',v:28 },
  { k:'nadi_level',l:'NAD+',u:'%',v:60 }, { k:'vitamin_d',l:'Vitamina D',u:'ng/mL',v:22 },
];

const INTERVENTIONS = [
  { id:'none', n:'Sin intervención', i:'⚪', c:'#6b7280' },
  { id:'ayuno_intermitente_16_8', n:'Ayuno 16:8', i:'⏰', c:'#3b82f6' },
  { id:'ejercicio_aerobico_150', n:'Ejercicio Aeróbico', i:'🏃', c:'#10b981' },
  { id:'hiit_3x', n:'HIIT 3x', i:'⚡', c:'#f59e0b' },
  { id:'dieta_mediterranea', n:'Dieta Mediterránea', i:'🫒', c:'#22c55e' },
  { id:'omega3_epa_dha_2g', n:'Omega-3 2g', i:'🐟', c:'#06b6d4' },
  { id:'combinacion_ejercicio_diana', n:'Plan Combinado', i:'🎯', c:'#8b5cf6' },
  { id:'metformina_850', n:'Metformina', i:'💊', c:'#ec4899' },
];

const AGENT_NAMES: Record<string,string> = {
  cardiovascular:'Dr. Vessels — Cardiovascular', metabolic:'Dra. Glucose — Metabólico',
  molecular:'Dr. Molecular — NAD+/AMPK', hepatic:'Dr. Hepatic — Hígado',
  renal:'Dra. Renal — Riñón', cognitive:'Dr. Cognitive — Cerebro',
  endocrine:'Dra. Endocrine — Hormonas', muscular:'Dr. Muscular — Músculo',
  immune:'Dra. Immune — Inmunidad', inflammatory:'Dr. Inflam — Inflamación',
  sleep_recovery:'Dra. Sleep — Sueño', sports_performance:'Dr. Sports — Rendimiento',
  epigenetic:'Dr. Epigenetic — Epigenética', adipose:'Dra. Adipose — Grasa Visceral',
  metabolic_flexibility:'Dr. Flex — Flexibilidad', insulin_sensitivity:'Dr. Insulin — Insulina',
  nutritional_timing:'Dr. Timing — Timing', oxidative_stress:'Dr. Oxidative — Estrés Oxidativo',
};

// ── Sub-components ──────────────────────────────────────────────────────────

function AgentCard({ out, exp, onToggle, onChat }: { out:AgentOutput; exp:boolean; onToggle:()=>void; onChat:()=>void }) {
  const icon = ICONS[out.agent_id] ?? ICONS.default;
  const name = AGENT_NAMES[out.agent_id] ?? out.agent_id;
  const conf = out.confidence > 0.8 ? '#22c55e' : out.confidence > 0.6 ? '#f59e0b' : '#6b7280';
  return (
    <div className="bg-gray-800/80 rounded-xl border border-gray-700 hover:border-cyan-500/50 transition-all duration-200">
      <div className="flex items-center gap-2 p-4 cursor-pointer" onClick={onToggle}>
        <span className="text-2xl">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-white font-bold text-xs truncate">{name}</div>
          <div className="text-gray-400 text-xs truncate mt-0.5">{out.assessment || 'Sin datos'}</div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="text-xs px-2 py-0.5 rounded-full" style={{background:`${conf}22`,color:conf}}>
            {Math.round(out.confidence*100)}%
          </span>
          <span className="text-gray-600 text-xs">{exp?'▲':'▼'}</span>
        </div>
      </div>
      {exp && (
        <div className="px-4 pb-4 space-y-2 border-t border-gray-700/50">
          {out.reasoning && (
            <div className="bg-cyan-950/30 border border-cyan-800/30 rounded-lg p-3 mt-2">
              <div className="text-cyan-400 text-xs font-bold mb-1">💡 Razonamiento clínico</div>
              <div className="text-gray-300 text-xs leading-relaxed whitespace-pre-wrap">{out.reasoning}</div>
            </div>
          )}
          {out.concerns?.slice(0,2).map((c,i) => (
            <div key={i} className="bg-red-950/30 border border-red-800/30 rounded-lg p-2">
              <div className="text-red-400 text-xs font-bold mb-0.5">⚠️ Concern</div>
              <div className="text-gray-300 text-xs">{c}</div>
            </div>
          ))}
          {out.recommended_actions?.slice(0,2).map((a,i) => (
            <div key={i} className="bg-emerald-950/30 border border-emerald-800/30 rounded-lg p-2">
              <div className="text-emerald-400 text-xs font-bold mb-0.5">✅ Acción recomendada</div>
              <div className="text-gray-300 text-xs">{a}</div>
            </div>
          ))}
          {out.signals_emitted?.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {out.signals_emitted.map((s,i) => (
                <span key={i} className="text-xs bg-cyan-900/40 text-cyan-300 border border-cyan-700 rounded px-2 py-0.5">{s}</span>
              ))}
            </div>
          )}
          <button onClick={(e) => { e.stopPropagation(); onChat(); }}
            className="w-full mt-2 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all">
            💬 Dialogar con este agente
          </button>
        </div>
      )}
    </div>
  );
}

function ChatModal({ agent, onClose }: { agent:AgentOutput; onClose:()=>void }) {
  const [msg, setMsg] = useState('');
  const [history, setHistory] = useState<[string,string][]>([['', agent.reasoning || 'Sin razonamiento registrado. Ejecuta una simulación primero.']]);
  const [loading, setLoading] = useState(false);
  const name = AGENT_NAMES[agent.agent_id] ?? agent.agent_id;
  const send = async () => {
    if (!msg.trim() || loading) return;
    setLoading(true);
    const userMsg = msg;
    setHistory(h => [...h, [userMsg, '']]);
    setMsg('');
    try {
      const r = await fetch(`${API}/api/v1/simulate/chat`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ agent_id: agent.agent_id, message: userMsg, user_data: {} }),
      });
      const d = await r.json();
      setHistory(h => [...h.slice(0,-1), [userMsg, d.response || 'Respuesta recibida']]);
    } catch {
      setHistory(h => [...h.slice(0,-1), [userMsg, 'Error: backend no disponible en puerto 8000']]);
    }
    setLoading(false);
  };
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl flex flex-col max-h-[85vh]" onClick={e=>e.stopPropagation()}>
        <div className="flex items-center justify-between p-5 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{ICONS[agent.agent_id] ?? '🦠'}</span>
            <div>
              <div className="text-white font-black">{name}</div>
              <div className="text-gray-500 text-xs">Agente Biológico — BioAEGIS</div>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-800">✕</button>
        </div>
        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {history.map(([q,a], i) => (
            <div key={i} className="space-y-2">
              {q && <div className="flex justify-end"><div className="bg-purple-700 text-white text-xs rounded-xl rounded-br-none px-4 py-2 max-w-[80%]">{q}</div></div>}
              {a && <div className="flex justify-start"><div className="bg-gray-800 text-gray-200 text-xs rounded-xl rounded-bl-none px-4 py-2 max-w-[85%] whitespace-pre-wrap">{a}</div></div>}
            </div>
          ))}
          {loading && <div className="text-gray-500 text-xs animate-pulse">⏳ El agente está pensando...</div>}
        </div>
        <div className="flex gap-2 p-4 border-t border-gray-700">
          <input className="flex-1 bg-gray-800 border border-gray-600 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-500 focus:border-cyan-500 focus:outline-none" value={msg} onChange={e=>setMsg(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder="Escribe tu pregunta al agente..."/>
          <button onClick={send} disabled={!msg.trim()||loading} className="px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white text-sm font-bold transition-all">Enviar</button>
        </div>
      </div>
    </div>
  );
}

// ── Main App ────────────────────────────────────────────────────────────────
export default function App() {
  const [profileName, setProfileName] = useState('Paciente Principal');
  const [age, setAge] = useState(45);
  const [sex, setSex] = useState<'male'|'female'>('male');
  const [params, setParams] = useState(DEFAULTS);
  const [interventions, setInterventions] = useState<string[]>(['none']);
  const [months, setMonths] = useState(6);
  const [result, setResult] = useState<SimResult|null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [chatAgent, setChatAgent] = useState<AgentOutput|null>(null);
  const [error, setError] = useState('');

  const toggle = (id: string) =>
    setExpanded(s => { const n = new Set(s); n.has(id)?n.delete(id):n.add(id); return n; });

  const runSim = async () => {
    setLoading(true); setError('');
    try {
      const ud: Record<string,string|number> = { chronological_age: age, sex };
      params.forEach(p => { ud[p.k] = p.v; });
      await fetch(`${API}/api/v1/simulate/init`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(ud) });
      // Take first intervention only for API
      const res = await fetch(`${API}/api/v1/simulate/run`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ months, intervention_id: interventions[0], user_data: ud }),
      });
      const data = await res.json();
      setResult(data);
      if (data.error) setError(data.error.slice(0,150));
    } catch(e) {
      setError('Backend no disponible en http://localhost:8000. Ejecuta: PYTHONPATH=~/BIOAEGIS python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000');
    }
    setLoading(false);
  };

  const bioAge = result?.ensemble_summary?.ensemble_biological_age ?? result?.biological_age ?? 0;
  const pace = result?.ensemble_summary?.ensemble_pace ?? result?.ensemble_pace ?? 1.0;
  const paceColor = pace > 1.15 ? '#ef4444' : pace > 1.0 ? '#f59e0b' : '#22c55e';
  const nAgents = result?.agent_outputs?.length ?? 0;
  const nSignals = result?.signals_emitted?.length ?? 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="bg-gray-900/80 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black">
              <span style={{color:'#22d3ee'}}>🐟</span>{' '}
              <span style={{color:'#22d3ee'}}>BioA</span>
              <span style={{color:'#a855f7'}}>EGIS</span>
              <span className="text-gray-500 text-sm ml-2 font-normal">v4 — Gemelo Digital Biológico</span>
            </h1>
            <p className="text-gray-500 text-xs mt-0.5">Fernando Fondillo · VIHOLABS · github.com/fernandofondillo/BIOAEGIS</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-gray-800 rounded-xl px-4 py-2 border border-gray-700">
              <span className="text-gray-400 text-xs">👤</span>
              <input className="bg-transparent text-white text-sm font-semibold w-36 focus:outline-none" value={profileName} onChange={e=>setProfileName(e.target.value)} placeholder="Nombre del perfil..."/>
            </div>
            <div className="flex gap-2 items-center bg-gray-800 rounded-xl px-4 py-2 border border-gray-700">
              <label className="text-gray-400 text-xs">Edad</label>
              <input type="number" value={age} onChange={e=>setAge(Number(e.target.value))} className="w-14 bg-transparent text-white font-bold text-sm text-center"/>
              <select value={sex} onChange={e=>setSex(e.target.value as 'male'|'female')} className="bg-transparent text-white text-sm">
                <option value="male">Hombre</option><option value="female">Mujer</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Error banner */}
        {error && (
          <div className="bg-red-950/50 border border-red-700/50 rounded-xl p-4 text-red-300 text-sm">
            ❌ {error}
          </div>
        )}

        {/* Main grid: interventions + params */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Interventions */}
          <div className="lg:col-span-2 bg-gray-900 rounded-2xl p-5 border border-gray-800">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-black text-white">🧬 Intervenciones</h2>
              <span className="text-xs text-gray-500">Selecciona una · más adelante múltiples</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {INTERVENTIONS.map(it => (
                <button key={it.id}
                  onClick={() => setInterventions([it.id])}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${interventions.includes(it.id) ? 'border-white scale-105' : 'border-gray-700 bg-gray-800 hover:border-gray-500'}`}
                  style={{backgroundColor: interventions.includes(it.id) ? `${it.c}22` : undefined}}>
                  <div className="text-3xl mb-2">{it.i}</div>
                  <div className="font-bold text-white text-xs leading-tight">{it.n}</div>
                </button>
              ))}
            </div>
            <div className="mt-4 text-xs text-gray-500">
              Seleccionada: <span className="text-cyan-400 font-bold">{INTERVENTIONS.find(i=>i.id===interventions[0])?.n}</span>
            </div>
          </div>

          {/* Params panel */}
          <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800 flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-black text-white mb-4">⚙️ Parámetros de Simulación</h2>
              <div className="mb-5">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400 text-sm">Meses de simulación</span>
                  <span className="text-cyan-400 font-black text-lg">{months}</span>
                </div>
                <input type="range" min="1" max="60" value={months} onChange={e=>setMonths(Number(e.target.value))} className="w-full" style={{accentColor:'#22d3ee'}}/>
                <div className="flex justify-between text-xs text-gray-600 mt-1"><span>1 mes</span><span>60 meses</span></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-800 rounded-xl p-3 text-center">
                  <div className="text-3xl font-black text-cyan-400">{bioAge > 0 ? bioAge.toFixed(1) : '--'}</div>
                  <div className="text-xs text-gray-400 mt-1">Edad Biológica</div>
                </div>
                <div className="bg-gray-800 rounded-xl p-3 text-center">
                  <div className="text-3xl font-black" style={{color:paceColor}}>{pace > 0 && pace !== 1.0 ? pace.toFixed(3) : '--'}</div>
                  <div className="text-xs text-gray-400 mt-1">DunedinPACE</div>
                </div>
              </div>
            </div>
            <button onClick={runSim} disabled={loading}
              className="mt-5 w-full py-5 rounded-2xl font-black text-lg transition-all hover:scale-105 disabled:opacity-50"
              style={{background: loading ? '#374151' : 'linear-gradient(135deg,#06b6d4,#a855f7)'}}>
              {loading ? '⏳ Simulando gemelo digital...' : '▶ Ejecutar Gemelo Digital'}
            </button>
          </div>
        </div>

        {/* Orchestrator Panel */}
        <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
          <h2 className="text-lg font-black text-white mb-5">🎛️ Panel del Orquestador — Biosíntesis</h2>
          {bioAge > 0 ? (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-3 text-center">
                {[
                  [bioAge.toFixed(1), 'Edad Biológica', 'text-cyan-400'],
                  [pace.toFixed(3), 'DunedinPACE', paceColor],
                  [String(nAgents), 'Agentes Activos', 'text-emerald-400'],
                  [String(nSignals), 'Señales Emitidas', 'text-yellow-400'],
                ].map(([v,l,c],i) => (
                  <div key={i} className="bg-gray-800 rounded-xl p-4">
                    <div className={`text-3xl font-black ${c}`}>{v}</div>
                    <div className="text-xs text-gray-400 mt-1">{l}</div>
                  </div>
                ))}
              </div>
              {result?.ensemble_summary?.trajectory && (
                <div className="bg-cyan-950/30 border border-cyan-800/30 rounded-xl p-4">
                  <div className="text-cyan-400 text-xs font-bold mb-2">📊 Interpretación del Orquestador</div>
                  <div className="text-gray-200 text-sm leading-relaxed">{result.ensemble_summary.trajectory}</div>
                </div>
              )}
              {result?.orchestrator_summary && (
                <div className="bg-gray-800 rounded-xl p-4">
                  <div className="text-gray-400 text-xs font-bold mb-2">📋 Resumen clínico</div>
                  <div className="text-gray-300 text-sm">{result.orchestrator_summary}</div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-10 text-gray-500">
              <div className="text-5xl mb-3">🐟</div>
              <div className="text-lg font-bold">Gemelo digital listo</div>
              <div className="text-sm mt-1">Pulsa "Ejecutar Gemelo Digital" para iniciar la simulación</div>
            </div>
          )}
        </div>

        {/* Signals */}
        {nSignals > 0 && (
          <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
            <h2 className="text-lg font-black text-white mb-4">🔄 Señales Inter-Agentes</h2>
            <div className="space-y-2">
              {result!.signals_emitted!.map((s,i) => {
                const pc: Record<string,string> = {HIGH:'#ef4444',CRITICAL:'#dc2626',NORMAL:'#f59e0b',LOW:'#6b7280',info:'#6b7280',warning:'#f59e0b',critical:'#ef4444'};
                return (
                  <div key={i} className="flex items-center gap-3 bg-gray-800 rounded-xl p-3">
                    <span className="font-black text-xs w-16 shrink-0" style={{color: pc[s.priority] ?? '#6b7280'}}>{s.priority}</span>
                    <span className="text-cyan-300 w-48 shrink-0 font-medium text-sm">{s.name}</span>
                    {s.emitted_by && <span className="text-gray-500 w-40 shrink-0 text-xs">de: {s.emitted_by}</span>}
                    <span className="text-gray-400 flex-1 text-xs">{s.reasoning?.slice(0,100)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Agents Grid */}
        {nAgents > 0 && (
          <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
            <h2 className="text-lg font-black text-white mb-4">🧠 {nAgents} Agentes Biológicos — Análisis Clínico</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {result!.agent_outputs!.map((out,i) => (
                <AgentCard key={i} out={out} exp={expanded.has(out.agent_id)} onToggle={()=>toggle(out.agent_id)} onChat={()=>setChatAgent(out)}/>
              ))}
            </div>
          </div>
        )}

        {/* Biomarkers panel */}
        <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
          <h2 className="text-lg font-black text-white mb-4">📊 Biomarcadores del Paciente: <span className="text-cyan-400">{profileName}</span></h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 gap-3">
            {params.map(p => (
              <div key={p.k} className="bg-gray-800 rounded-xl p-3">
                <div className="text-gray-400 text-xs mb-1.5">{p.l}</div>
                <div className="flex items-center gap-1.5">
                  <input type="number" value={p.v} onChange={e=>setParams(prev=>prev.map(x=>x.k===p.k?{...x,v:Number(e.target.value)}:x))} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-2 py-1.5 text-white font-bold text-sm text-center" step="0.1"/>
                  <span className="text-gray-500 text-xs w-10 shrink-0">{p.u}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-xs text-gray-500">
            💡 Los cambios en biomarcadores se aplican automáticamente en la siguiente simulación
          </div>
        </div>
      </div>

      {chatAgent && <ChatModal agent={chatAgent} onClose={()=>setChatAgent(null)}/>}
    </div>
  );
}
