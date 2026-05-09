import { useState, useCallback } from 'react';

const API = 'http://localhost:8000';

const BUILTIN_PARAMS = [
  { key: 'ldl', label: 'LDL Colesterol', unit: 'mg/dL', value: 155 },
  { key: 'hdl', label: 'HDL Colesterol', unit: 'mg/dL', value: 42 },
  { key: 'tg', label: 'Triglicéridos', unit: 'mg/dL', value: 210 },
  { key: 'glucose', label: 'Glucosa Ayunas', unit: 'mg/dL', value: 102 },
  { key: 'hba1c', label: 'HbA1c', unit: '%', value: 5.8 },
  { key: 'homa_ir', label: 'HOMA-IR', unit: '', value: 3.2 },
  { key: 'crp', label: 'PCR', unit: 'mg/L', value: 3.5 },
  { key: 'systolic_bp', label: 'Presión Sistólica', unit: 'mmHg', value: 135 },
  { key: 'vo2max', label: 'VO2max', unit: 'ml/kg/min', value: 32 },
  { key: 'hrv_sdnn', label: 'HRV SDNN', unit: 'ms', value: 32 },
  { key: 'waist', label: 'Cintura', unit: 'cm', value: 102 },
  { key: 'bmi', label: 'IMC', unit: 'kg/m²', value: 28 },
  { key: 'nadi_level', label: 'NAD+', unit: '%', value: 60 },
  { key: 'vitamin_d', label: 'Vitamina D', unit: 'ng/mL', value: 22 },
];

const AGENT_ICONS: Record<string, string> = {
  cardiovascular: '❤️', metabolic: '🩸', inflammatory: '🔥', molecular: '🧬',
  sleep_recovery: '😴', sports_performance: '💪', hepatic: '🫀', renal: '🧪',
  cognitive: '🧠', endocrine: '⚡', muscular: '🦾', immune: '🛡️',
  epigenetic: '📋', adipose: '⚖️', metabolic_flexibility: '🔋',
  insulin_sensitivity: '🩹', nutritional_timing: '⏰', oxidative_stress: '🆓', default: '🦠',
};

const BUILTIN_INTERVENTIONS = [
  { id: 'none', name: 'Sin intervención', icon: '⚪', color: '#6b7280', description: 'Simular sin cambios' },
  { id: 'ayuno_intermitente_16_8', name: 'Ayuno 16:8', icon: '⏰', color: '#3b82f6', description: '16h ayuno / 8h comida' },
  { id: 'ejercicio_aerobico_150', name: 'Ejercicio Aeróbico', icon: '🏃', color: '#10b981', description: '150 min/sem moderada' },
  { id: 'hiit_3x', name: 'HIIT 3x', icon: '⚡', color: '#f59e0b', description: '3x HIIT/sem' },
  { id: 'dieta_mediterranea', name: 'Dieta Mediterránea', icon: '🫒', color: '#22c55e', description: 'Frutas, verduras, aceite de oliva' },
  { id: 'omega3_epa_dha_2g', name: 'Omega-3 (2g)', icon: '🐟', color: '#06b6d4', description: '2g EPA+DHA diarios' },
  { id: 'combinacion_ejercicio_diana', name: 'Plan Combinado', icon: '🎯', color: '#8b5cf6', description: 'Ejercicio+ayuno+suplementos' },
  { id: 'metformina_850', name: 'Metformina', icon: '💊', color: '#ec4899', description: 'Fármaco sensibilizador insulina' },
];

// Types
interface CustomParam { id: number; name: string; label: string; value: number; unit: string; }
interface CustomInt { id: string; name: string; description: string; icon: string; color: string; }
interface AgentOut {
  agent_id: string; assessment: string; concerns: string[];
  recommended_actions: string[]; confidence: number;
  signals_emitted: Array<{ name: string; priority: string }>;
}
interface SimResult {
  agent_outputs: AgentOut[]; signals_emitted: Array<{ name: string; priority: string; reasoning: string; emitted_by?: string }>;
  user_data: Record<string, number>; biological_age: number; ensemble_pace: number; confidence: number;
  orchestrator_summary?: string; moderator_trajectory?: string; moderator_concerns?: string[];
}

// Sub-components
function AgentCard({ out, expanded, onToggle }: { out: AgentOut; expanded: boolean; onToggle: () => void }) {
  const icon = AGENT_ICONS[out.agent_id] ?? AGENT_ICONS.default;
  const conf = out.confidence > 0.8 ? '#22c55e' : out.confidence > 0.6 ? '#f59e0b' : '#6b7280';
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-4 cursor-pointer hover:border-cyan-500 transition-all" onClick={onToggle}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{icon}</span>
        <span className="text-white font-semibold text-sm capitalize">{out.agent_id.replace(/_/g, ' ')}</span>
        <div className="ml-auto"><span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: conf+'33', color: conf }}>{Math.round(out.confidence*100)}%</span></div>
      </div>
      <p className="text-gray-300 text-xs line-clamp-2">{out.assessment}</p>
      {expanded && (
        <div className="mt-3 space-y-2">
          {out.concerns.slice(0,2).map((c,i) => <div key={i} className="text-xs bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-2">⚠️ {c}</div>)}
          {out.recommended_actions.slice(0,2).map((a,i) => <div key={i} className="text-xs bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg p-2">✅ {a}</div>)}
          {out.signals_emitted?.length > 0 && <div className="flex flex-wrap gap-1 mt-2">
            {out.signals_emitted.map((s,i) => <span key={i} className="text-xs bg-cyan-900/40 text-cyan-300 border border-cyan-700 rounded px-1.5 py-0.5">{s.name}</span>)}
          </div>}
        </div>
      )}
    </div>
  );
}

function SignalFlow({ signals }: { signals: SimResult['signals_emitted'] }) {
  if (!signals?.length) return <div className="text-gray-500 text-sm text-center py-6">Sin señales emitidas en esta simulación</div>;
  const pc: Record<string,string> = { HIGH: '#ef4444', CRITICAL: '#dc2626', NORMAL: '#f59e0b', LOW: '#6b7280' };
  const organs = [' Cardiovascular',' Metabólico',' Inflamación',' Molecular',' Sueño',' Rendimiento'];
  const icons = ['❤️','🩸','🔥','🧬','😴','💪'];
  return (
    <div className="bg-gray-900 rounded-xl p-5 border border-gray-700">
      <h3 className="text-white font-bold text-sm mb-4">🔄 Señales Inter-Agentes — Biosíntesis</h3>
      <div className="space-y-1 mb-4">
        {signals.map((s,i) => (
          <div key={i} className="flex items-center gap-2 text-xs bg-gray-800 rounded-lg p-2">
            <span className="font-bold w-14 shrink-0" style={{ color: pc[s.priority]??'#6b7280' }}>{s.priority}</span>
            <span className="text-cyan-300 w-44 shrink-0 truncate font-medium">{s.name}</span>
            {s.emitted_by && <span className="text-gray-500 w-36 shrink-0 truncate">de: {s.emitted_by}</span>}
            <span className="text-gray-400 flex-1 truncate">{s.reasoning?.slice(0,70)}</span>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2">
        {organs.map((org,i) => {
          const em = signals.filter(s => s.emitted_by?.includes(org.trim()));
          const rc = signals.filter(s => s.name.includes(org.trim()));
          return (
            <div key={i} className="bg-gray-800 rounded-lg p-3 text-center">
              <div className="text-2xl mb-1">{icons[i]}</div>
              <div className="text-xs text-gray-400">{org}</div>
              {em.length>0 && <div className="text-xs text-red-400 mt-1">→ {em.length}</div>}
              {rc.length>0 && <div className="text-xs text-green-400 mt-1">← {rc.length}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function OrchestratorPanel({ r }: { r: SimResult }) {
  const pc = r.ensemble_pace > 1.2 ? '#ef4444' : r.ensemble_pace > 1.0 ? '#f59e0b' : '#22c55e';
  return (
    <div className="bg-gray-900 rounded-xl p-5 border border-gray-700">
      <h3 className="text-white font-bold text-sm mb-4">🎛️ Panel del Orquestador — Biosíntesis</h3>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        {[
          [r.biological_age.toFixed(1), 'Edad Biológica Final', 'text-cyan-400'],
          [r.ensemble_pace.toFixed(3), 'DunedinPACE', pc+''],
          [r.agent_outputs.length.toString(), 'Agentes Activos', 'text-emerald-400'],
          [r.signals_emitted.length.toString(), 'Señales Emitidas', 'text-yellow-400'],
        ].map(([v,l,c],i) => (
          <div key={i} className="bg-gray-800 rounded-xl p-3">
            <div className={`text-2xl font-black ${c}`}>{v}</div>
            <div className="text-xs text-gray-400 mt-1">{l}</div>
          </div>
        ))}
      </div>
      {r.orchestrator_summary && <div className="bg-gray-800 rounded-lg p-3 mb-3">
        <div className="text-xs font-bold text-cyan-400 mb-1">📋 Conclusión del Orquestador</div>
        <div className="text-xs text-gray-300">{r.orchestrator_summary}</div>
      </div>}
      {r.moderator_trajectory && <div className="bg-yellow-900/10 border border-yellow-700/30 rounded-lg p-3">
        <div className="text-xs font-bold text-yellow-400 mb-1">🩺 Moderador Clínico</div>
        <div className="text-xs text-gray-300 mb-2">{r.moderator_trajectory}</div>
        {r.moderator_concerns && r.moderator_concerns.length > 0 && <div className="flex flex-wrap gap-1">
          {r.moderator_concerns.map((c: string, i: number) => <span key={i} className="text-xs bg-yellow-900/40 text-yellow-300 rounded px-2 py-0.5">{c}</span>)}
        </div>}
      </div>}
    </div>
  );
}

function AddParamModal({ onAdd, onClose }: { onAdd: (p: {name:string;label:string;value:number;unit:string})=>void; onClose:()=>void }) {
  const [name,setName]=useState(''); const [label,setLabel]=useState(''); const [value,setValue]=useState(0); const [unit,setUnit]=useState('');
  const handle=()=>{ if(name&&label) onAdd({name: name.toLowerCase().replace(/\s+/g,'_'), label, value, unit}); onClose(); };
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-[22rem]" onClick={e=>e.stopPropagation()}>
        <h3 className="text-white font-black text-lg mb-4">➕ Añadir Biomarcador</h3>
        <div className="space-y-3">
          <div><label className="text-xs text-gray-400 block mb-1">Nombre visible</label>
            <input className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm" value={label} onChange={e=>setLabel(e.target.value)} placeholder="ej: Ferritina"/></div>
          <div><label className="text-xs text-gray-400 block mb-1">ID técnico (sin espacios)</label>
            <input className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm" value={name} onChange={e=>setName(e.target.value)} placeholder="ej: ferritina"/></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="text-xs text-gray-400 block mb-1">Valor</label>
              <input type="number" className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm" value={value} onChange={e=>setValue(parseFloat(e.target.value)||0)}/></div>
            <div><label className="text-xs text-gray-400 block mb-1">Unidad</label>
              <input className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm" value={unit} onChange={e=>setUnit(e.target.value)} placeholder="ej: ng/mL"/></div>
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button onClick={onClose} className="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-xl text-sm font-semibold transition-all">Cancelar</button>
          <button onClick={handle} className="flex-1 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-bold">Añadir ➕</button>
        </div>
      </div>
    </div>
  );
}

function AddInterventionModal({ onAdd, onClose }: { onAdd: (i: CustomInt)=>void; onClose:()=>void }) {
  const [name,setName]=useState(''); const [desc,setDesc]=useState(''); const [icon,setIcon]=useState('💊'); const [color,setColor]=useState('#8b5cf6');
  const colors=['#3b82f6','#10b981','#f59e0b','#22c55e','#06b6d4','#8b5cf6','#ec4899','#ef4444'];
  const handle=()=>{ if(name) onAdd({id:`custom_${Date.now()}`, name, description:desc, icon, color}); onClose(); };
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-[22rem]" onClick={e=>e.stopPropagation()}>
        <h3 className="text-white font-black text-lg mb-4">➕ Añadir Intervención</h3>
        <div className="space-y-3">
          <div><label className="text-xs text-gray-400 block mb-1">Nombre</label>
            <input className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm" value={name} onChange={e=>setName(e.target.value)} placeholder="ej: Keto Dieta 4 semanas"/></div>
          <div><label className="text-xs text-gray-400 block mb-1">Descripción</label>
            <textarea className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm resize-none" rows={2} value={desc} onChange={e=>setDesc(e.target.value)}/></div>
          <div><label className="text-xs text-gray-400 block mb-1">Icono (emoji)</label>
            <input className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm" value={icon} onChange={e=>setIcon(e.target.value)}/></div>
          <div><label className="text-xs text-gray-400 block mb-2">Color</label>
            <div className="flex gap-2">{colors.map(c=><button key={c} onClick={()=>setColor(c)} className="w-8 h-8 rounded-full border-2 transition-all" style={{backgroundColor:c, borderColor: color===c?'white':'transparent'}}/>)}</div>
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button onClick={onClose} className="flex-1 py-2.5 bg-gray-700 text-gray-300 rounded-xl text-sm font-semibold">Cancelar</button>
          <button onClick={handle} className="flex-1 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-bold">Añadir ➕</button>
        </div>
      </div>
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState<'biomarkers'|'simulation'|'memory'>('biomarkers');
  const [params, setParams] = useState(BUILTIN_PARAMS);
  const [customParams, setCustomParams] = useState<CustomParam[]>([]);
  const [interventions, _setInterventions] = useState(BUILTIN_INTERVENTIONS);
  const [customInts, setCustomInts] = useState<CustomInt[]>([]);
  const [selectedInt, setSelectedInt] = useState('none');
  const [months, setMonths] = useState(6);
  const [result, setResult] = useState<SimResult|null>(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [showAddParam, setShowAddParam] = useState(false);
  const [showAddInt, setShowAddInt] = useState(false);
  const [age, setAge] = useState(40);
  const [sex, setSex] = useState<'male'|'female'>('male');

  const buildUserData = useCallback(() => {
    const ud: Record<string,string|number> = { chronological_age: age, sex };
    params.forEach(p => { ud[p.key] = p.value; });
    customParams.forEach(p => { ud[p.name] = p.value; });
    return ud;
  }, [params, customParams, age, sex]);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const ud = buildUserData();
      await fetch(`${API}/api/v1/simulate/init`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(ud) });
      const res = await fetch(`${API}/api/v1/simulate/run`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ months, intervention_id: selectedInt, user_data: ud }),
      });
      const data = await res.json();
      setResult(data);
    } catch { alert('Backend no disponible en '+API+'. Asegúrate de que el servidor está corriendo.'); }
    setLoading(false);
  };

  const toggleAgent = (id: string) =>
    setExpanded(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });

  const addParam = (p: {name:string;label:string;value:number;unit:string}) =>
    setCustomParams(prev => [...prev, { id: Date.now(), ...p }]);

  const addInt = (i: CustomInt) => setCustomInts(prev => [...prev, i]);

  const allParams = [...params, ...customParams.map(p => ({ key: p.name, label: p.label, value: p.value, unit: p.unit }))];
  const allInts = [...interventions, ...customInts];
  const bioAge = result?.biological_age ?? age;
  const pace = result?.ensemble_pace ?? 1.0;
  const paceColor = pace > 1.2 ? '#ef4444' : pace > 1.0 ? '#f59e0b' : '#22c55e';

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* HEADER */}
      <div style={{background:'linear-gradient(135deg,#0a0a1a,#1a1040,#0a0a1a)'}} className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black tracking-tight">
              <span style={{color:'#22d3ee'}}>🐟</span>{' '}<span style={{color:'#22d3ee'}}>BioA</span><span style={{color:'#a855f7'}}>EGIS</span>
              <span className="text-gray-500 text-base ml-2">v1.0</span>
            </h1>
            <p className="text-gray-500 text-xs mt-0.5">Sistema de Gemelo Digital Biológico — Fernando Fondillo / VIHOLABS</p>
          </div>
          <div className="text-right text-xs text-gray-500">github.com/fernandofondillo/BIOAEGIS</div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* TABS */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {([['biomarkers','📊 Biomarcadores'],['simulation','🧬 Simulación'],['memory','🧠 Memoria']] as const).map(([t,l]) => (
            <button key={t} onClick={()=>setTab(t)}
              className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all ${tab===t?'bg-white text-gray-900':'bg-gray-800 text-gray-400 hover:text-white'}`}>
              {l}
            </button>
          ))}
        </div>

        {/* ── TAB: BIOMARKERS ── */}
        {tab==='biomarkers' && (
          <div>
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-xl font-black">Datos Biométricos</h2>
                <p className="text-gray-500 text-sm">{allParams.length} parámetros registrados</p>
              </div>
              <div className="flex gap-3 items-center">
                <div className="flex gap-2 items-center bg-gray-900 rounded-xl px-4 py-2 border border-gray-700">
                  <label className="text-xs text-gray-400">Edad</label>
                  <input type="number" value={age} onChange={e=>setAge(parseInt(e.target.value)||40)} className="w-16 bg-transparent text-white font-bold text-sm"/>
                  <label className="text-xs text-gray-400 ml-2">Sexo</label>
                  <select value={sex} onChange={e=>setSex(e.target.value as 'male'|'female')} className="bg-transparent text-white text-sm">
                    <option value="male">Hombre</option><option value="female">Mujer</option>
                  </select>
                </div>
                <button onClick={()=>setShowAddParam(true)}
                  className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-bold transition-all">
                  ➕ Añadir Dato
                </button>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-3">
              {allParams.map(p => (
                <div key={p.key} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <div className="text-xs text-gray-400 mb-2">{p.label}</div>
                  <div className="flex items-center gap-2">
                    <input type="number" value={p.value} onChange={e=>{
                      const v=parseFloat(e.target.value)||0;
                      setParams(prev=>prev.map(x=>x.key===p.key?{...x,value:v}:x));
                      setCustomParams(prev=>prev.map(x=>x.name===p.key?{...x,value:v}:x));
                    }} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white font-bold text-lg" step="0.1"/>
                    <span className="text-xs text-gray-500 w-14">{p.unit}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── TAB: SIMULATION ── */}
        {tab==='simulation' && (
          <div>
            <div className="grid grid-cols-3 gap-4 mb-4">
              {/* INTERVENTIONS */}
              <div className="col-span-2 bg-gray-900 rounded-2xl p-5 border border-gray-800">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-black">Intervenciones</h2>
                  <button onClick={()=>setShowAddInt(true)} className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold">
                    ➕ Añadir
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {allInts.map((int,i) => (
                    <button key={`${int.id}-${i}`} onClick={()=>setSelectedInt(int.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${selectedInt===int.id?'border-white scale-105':'border-gray-700 bg-gray-800 hover:border-gray-500'}`}
                      style={{backgroundColor: selectedInt===int.id ? `${int.color}22`:undefined}}>
                      <div className="text-xl mb-1">{int.icon}</div>
                      <div className="font-semibold text-white text-xs leading-tight">{int.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* PARAMS */}
              <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800 flex flex-col justify-between">
                <div>
                  <h2 className="text-lg font-black mb-4">Parámetros</h2>
                  <div className="mb-4">
                    <label className="text-sm text-gray-400 mb-2 block">Meses: <strong className="text-white">{months}</strong></label>
                    <input type="range" min="1" max="60" value={months} onChange={e=>setMonths(parseInt(e.target.value))} className="w-full" style={{accentColor:'#22d3ee'}}/>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    <div className="bg-gray-800 rounded-lg p-2 text-center"><div className="text-xl font-black text-cyan-400">{bioAge.toFixed(1)}</div><div className="text-xs text-gray-400">Edad Bio</div></div>
                    <div className="bg-gray-800 rounded-lg p-2 text-center"><div className="text-xl font-black" style={{color:paceColor}}>{pace.toFixed(3)}</div><div className="text-xs text-gray-400">PACE</div></div>
                  </div>
                </div>
                <button onClick={runSimulation} disabled={loading}
                  className="w-full py-4 rounded-xl font-black text-lg transition-all hover:scale-105 disabled:opacity-50"
                  style={{background:'linear-gradient(135deg,#06b6d4,#a855f7)'}}>
                  {loading ? '⏳ Simulando...':'▶ Ejecutar Gemelo Digital'}
                </button>
              </div>
            </div>

            {/* RESULTS */}
            {result && (
              <>
                <OrchestratorPanel r={result} />
                <div className="mt-4"><SignalFlow signals={result.signals_emitted}/></div>
                <div className="mt-4">
                  <h2 className="text-lg font-black mb-3">🧠 18 Agentes Biológicos — Análisis Clínico</h2>
                  <div className="grid grid-cols-3 gap-3">
                    {result.agent_outputs.map((out,i) => (
                      <AgentCard key={i} out={out} expanded={expanded.has(out.agent_id)} onToggle={()=>toggleAgent(out.agent_id)}/>
                    ))}
                  </div>
                  {result.agent_outputs.length===0 && (
                    <div className="text-center py-10 text-gray-500">Sin datos de agentes — conecta con el backend en puerto 8000</div>
                  )}
                </div>
              </>
            )}

            {!result&&!loading&&(
              <div className="text-center py-16">
                <div className="text-6xl mb-4">🐟</div>
                <div className="text-xl font-bold text-gray-300">Gemelo digital listo</div>
                <div className="text-sm text-gray-500 mt-2">Selecciona intervención y haz clic en "Ejecutar"</div>
              </div>
            )}
          </div>
        )}

        {/* ── TAB: MEMORY ── */}
        {tab==='memory'&&(
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🧠</div>
            <div className="text-2xl font-black mb-2">Memoria Persistente</div>
            <div className="text-gray-500 max-w-lg mx-auto">Los resultados se guardan en SQLite. Despliega el backend para activar la memoria.</div>
            <div className="mt-6 grid grid-cols-3 gap-4 max-w-2xl mx-auto text-left">
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800"><div className="text-2xl mb-2">📊</div><div className="text-sm font-bold text-white">Historial de Sesiones</div><div className="text-xs text-gray-400 mt-1">Cada simulación se guarda con su sesión</div></div>
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800"><div className="text-2xl mb-2">🔗</div><div className="text-sm font-bold text-white">Trazabilidad de Agentes</div><div className="text-xs text-gray-400 mt-1">Cada agente registra reasoning y acciones</div></div>
              <div className="bg-gray-900 rounded-xl p-4 border border-gray-800"><div className="text-2xl mb-2">🧬</div><div className="text-sm font-bold text-white">Trail de Señales</div><div className="text-xs text-gray-400 mt-1">Las señales entre órganos quedan registradas</div></div>
            </div>
          </div>
        )}
      </div>

      {showAddParam && <AddParamModal onAdd={addParam} onClose={()=>setShowAddParam(false)}/>}
      {showAddInt && <AddInterventionModal onAdd={addInt} onClose={()=>setShowAddInt(false)}/>}
    </div>
  );
}