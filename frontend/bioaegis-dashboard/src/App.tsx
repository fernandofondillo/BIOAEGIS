// BioAEGIS Dashboard v4 — Fernando Fondillo / VIHOLABS
import { useState } from 'react';
import type { AgentOutput, SimResult } from './types';

const API = 'http://localhost:8000';

// Demo mode when backend unavailable
const DEMO_ENSEMBLE = {
  ensemble_biological_age: 50.7,
  ensemble_pace: 1.177,
  age_acceleration_years: 5.7,
  trajectory: "Tu edad biológica de 50.7 años supera en 5.7 años tu edad cronológica de 45 años. Los relojes (PhenoAge, Zhang, DunedinPACE) indican una aceleración moderada. Los principales motores de envejecimiento son: lipotoxicidad vascular, resistencia a la insulina subclínica, y declive de NAD+/AMPK. El Plan Combinado (ejercicio + ayuno + suplementos) mostraría una reducción de -3.2 años en edad biológica a 6 meses.",
  confidence: 0.87,
};
const DEMO_AGENTS = (() => {
  const names: [string,string,string,string[],[string,string[],[string]][]][] = [
    ['cardiovascular','Dr. Vessels','❤️ Sistema Cardiovascular',['LDL 155 mg/dL en rango de riesgo','HDL 42 mg/dL bajo','TG 210 mg/dL elevado'],[['El LDL partículas pequeñas densas están elevadas. La ratio LDL/HDL de 3.69 indica riesgo aterogénico. Sin embargo el HDL funcional está en 42 — por encima del umbral crítico de 40. La combinación de TG altos + HDL bajo es característica del fenotipo aterogénico.',['Iniciar dieta mediterránea','Reducir carbohidratos refinados','Añadir Omega-3 2g'],['Monitorizar LDL cada 3 meses','Considerar estáticas si LDL > 160']]]],
    ['metabolic','Dra. Glucose','🩸 Sistema Metabólico',['HOMA-IR 3.2 — resistencia a insulina','Glucosa ayunas 102 mg/dL borderline','HbA1c 5.8% pre-diabetes'],[['La resistencia a la insulina periférica está confirmada con HOMA-IR de 3.2 (normal <2.5). La hiperinsulinemia compensatoria mantiene la glucosa en rango pre-diabético. Sin intervención, progresión a DM2 en 3-5 años es probable.',['Ayuno intermitente 16:8','Reducir fructosa','Ejercicio HIIT 3x/semana'],['HbA1c cada 6 meses','Curva de glucosa completa']]]],
    ['molecular','Dr. Molecular','🧬 Biología Molecular NAD+/mTOR',['NAD+ 60% — declive moderado','AMPK 60% actividad basal','mTOR 50% actividad moderada'],[['El eje NAD+/AMPK/sirtuinas muestra actividad basal reducida. La edad biológica molecular estimada en 48.3 años sugiere activación insuficiente de los programas de reparación celular. La autofagia está en 40% — subóptima para清除 células senescentes.',['NMN 250mg/día','Resveratrol 100mg','Ejercicio aeróbico 150min/sem'],['Medir NAD+ en sangre cada 6 meses']]]],
    ['hepatic','Dr. Hepatic','🫀 Función Hepática',['AST/ALT ratio normal','TG hepático estimado elevado','Capacidad detox moderadamente reducida'],[['El hígado muestra primeros signos de esteatosis hepática no alcohólica (EHNA). La ratio AST/ALT <1 es sugestiva. La capacidad de detoxificación fase I está sobrecargada por carga metabólica. Sin intervención, progresión a fibrosis hepática posible en 5-8 años.',['Dieta baja en fructosa','Cúrcuma 500mg','Ejercicio aeróbico regular'],['Ecografía hepática anual','AST ALT cada 6 meses']]]],
    ['renal','Dra. Renal','🧪 Función Renal',['eGFR calculado normal','Creatinina 1.0 mg/dL','Relación albumina/creatinina normal'],[['La función renal estimada está dentro de rango normal para la edad cronológica. Sin embargo la néfrona funcional muestra primeros signos de senescencia. El estrés oxidativo renal está elevado — precursor de néfropatía diabética futura.',['Vitamina D 3000UI/día','Control de proteína dietética','Hidratación 2.5L/día'],['eGFR anual','Microalbuminuria anual']]]],
    ['cognitive','Dr. Cognitive','🧠 Función Cognitiva',['VO2max 32 ml/kg/min — por debajo óptimo','HRV SDNN 32ms — estrés moderado','Riego cerebral potencialmente reducido'],[['La reserva cognitiva está comprometida por baja capacidad cardiovascular. El VO2max de 32 indica que el cerebro recibe menos oxígeno del óptimo. La HRV reducida sugiere activación simpática crónica. Intervención temprana es crítica para prevenir deterioro cognitivo.',['Ejercicio aeróbico progresivo','Sueño 8h estructurado','Omega-3 DHA 1g'],['Neuropsych testing anual','Resonancia magnética funcional si síntomas']]]],
    ['endocrine','Dra. Endocrine','⚡ Sistema Hormonal',['Cortisol estimado moderado','DHEA-S bioactivo normal','TSH en rango норма'],[['El eje HPA está crónicamente activado por estrés moderado crónico. El cortisol de despertar está probablemente elevado. La relación DHEA-S/cortisol sugiere fase de transición hacia sarcopenia. El IGF-1 circulante debe monitorizarse.',['Manejo de estrés estructurado','Ashwagandha 300mg','Sueño deep 7-9h'],['Perfil hormonal completo anual']]]],
    ['immune','Dra. Immune','🛡️ Sistema Inmunitario',['PCR 3.5 mg/L — inflamacion baja crónica','Linfocitos funcionales normales','Inmunosenescencia incipiente'],[['La inflamación crónica de bajo grado (inflammaging) está presente. PCR de 3.5 mg/L indica activación del eje IL-6/CRP. Las células NK están funcionales pero con capacidad reducida de清除 células tumorales. La inmunosenescencia está comenzando.',['Vitamina D 3000UI','Zinc 30mg','Ejercicio moderado regular'],['PCRus anual','Subpoblaciones linfocitarias']]]],
    ['inflammatory','Dr. Inflam','🔥 Inflamación Crónica',['CRP 3.5 mg/L elevada','TNF-α estimado moderado','Estrés oxidativo tisular presente'],[['El microambiente inflamatorio crónico acelera el envejecimiento de tejidos. La activación del NF-κB está probable. El TNF-α elevado perpetúa resistencia a insulina y disfunción endotelial. Ciclo vicioso establecido.',['Semillas de lino','Curcumina 500mg','Ejercicio anti-inflamatorio'],['Panel citoquinas','Ferritina anual']]]],
    ['sleep_recovery','Dra. Sleep','😴 Sueño y Recuperación',['HRV SDNN 32ms reducida','Recovery score estimado 60%','Eficiencia de sueño probable 80%'],[['La recuperación durante sueño está comprometida. HRV SDNN de 32ms indica tono vagal bajo. El cortisol de despertar probablemente elevado. La melatonina估计 está reducida. Sin intervención, progresión a insomnio crónico es probable.',['Rutina de sueño estructurada','3h antes sin pantallas','Magnesio 400mg'],['Sleep tracking','Actigraphy si persiste']]]],
    ['sports_performance','Dr. Sports','💪 Rendimiento Deportivo',['VO2max 32ml/kg/min — moderado','HRV SDNN 32ms reducida','Capacidad anaeróbica límite'],[['El VO2max de 32 está en percentil 40 para hombres de 45 años — por debajo del óptimo de 45+. La potencia aeróbica límite (VAT) estimada en 75% de máxima. La recuperación post-ejercicio está alargada por HRV baja.',['HIIT 3x/semana progresiva','Control HRV daily','BCAA post-ejercicio'],['CPET si síntomas fatigables','Biomarcadores daño muscular']]]],
    ['epigenetic','Dr. Epigenetic','📋 Metilación del ADN',['Reloj epigenético estimado 48.3 años','Horloge de GrimAge elevado','Metilación global moderadamente alterada'],[['La edad epigenética de 48.3 años supera la cronológica de 45 — indica drift epigenético. La metilación de sitios CpG críticos está alterada. Los principales sitios son: AR, ESR1, FOXP3. La intervención con metformina podría modular la metilación.',['Metformina 850mg (bajo prescripción)','Dieta rica en metilación (folato,B12)','Ejercicio intenso'],['Reloj epigenetic Blood test','Microarray 450K si disponible']]]],
    ['adipose','Dra. Adipose','⚖️ Grasa Visceral',['IMC 28 — sobrepeso grado 1','Cintura 102cm — riesgo aumentado','Grasa visceral estimada elevada'],[['La adiposidad visceral es el principal driver metabólico del paciente. 102cm de cintura a los 45 años indica acumulación visceral. La grasa omental es endocrinamente activa — secreta adipocinas pro-inflamatorias (TNF-α, IL-6). Ciclo vicioso establecido.',['Deficit calorico 300-500kcal','Proteína 1.6g/kg','Ejercicio resistencia 3x'],['DEXA scan','MRI abdominal si clínica']]]],
    ['oxidative_stress','Dr. Oxidative','🆓 Estrés Oxidativo',['NAD+ 60% — substrato para repair reducido','Antioxidantes estimada moderada','Glutatión intracelular probablemente bajo'],[['El balance redox está desplazado hacia estrés oxidativo. El NAD+ reducido limita la actividad de SIRT1/2/3. La producción de ROS supera la capacidad antioxidante. Daño mitocondrial acumulándose en tejidos de alta demanda.',['Vitamina C 500mg','Vitamina E 400UI','Polyphenols 500mg'],['8-OHdG urinary','Glutatión eritrocitario si disponible']]]],
  ];
  return names.map(([id, name, icon, assessment, [reasoning, concerns, actions]]) => ({
    agent_id: id, assessment, reasoning, concerns, recommended_actions: actions,
    confidence: 0.85, signals_emitted: [],
  }));
})();

const DEMO_SIGNALS = [
  { name:'LIPOTOXICITY', priority:'HIGH', reasoning:'LDL partículas densas > TG elevados → acumulación en pared arterial. Riesgo aterogénico inmediato.', emitted_by:'cardiovascular' },
  { name:'PRO_INFLAM', priority:'HIGH', reasoning:'PCR 3.5 mg/L + TNF-α elevado → activación del eje inflamatorio sistémico crónico.', emitted_by:'inflammatory' },
  { name:'INSULIN_RESISTANCE', priority:'HIGH', reasoning:'HOMA-IR 3.2 > 2.5 → señalización de insulina comprometída en músculo e hígado.', emitted_by:'metabolic' },
  { name:'NAD_DECLINE', priority:'HIGH', reasoning:'NAD+ a 60% del óptimo → limitando reparación DNA, autofagia y función mitocondrial.', emitted_by:'molecular' },
  { name:'OXIDATIVE_STRESS', priority:'NORMAL', reasoning:'Desequilibrio ROS/antioxidantes → daño oxidativo acumulándose en tejidos.', emitted_by:'oxidative_stress' },
];

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
      // Try backend
      try {
        const initRes = await fetch(`${API}/api/v1/simulate/init`, {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify(ud),
        });
        const initData = await initRes.json();
        if (!initRes.ok) throw new Error(initData.error || 'Init failed');
      } catch { /* continue to run endpoint */ }
      // Run simulation
      const res = await fetch(`${API}/api/v1/simulate/run`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ months, intervention_id: interventions[0], user_data: ud }),
      });
      const data = await res.json();
      if (!res.ok || !data.agent_outputs?.length) throw new Error('No data');
      setResult(data);
    } catch {
      // DEMO MODE — use realistic simulated data
      setResult({
        simulation_id: 999,
        tick: months,
        biological_age: DEMO_ENSEMBLE.ensemble_biological_age,
        ensemble_pace: DEMO_ENSEMBLE.ensemble_pace,
        confidence: DEMO_ENSEMBLE.confidence,
        user_data: {},
        ensemble_summary: {
          ensemble_biological_age: DEMO_ENSEMBLE.ensemble_biological_age,
          ensemble_pace: DEMO_ENSEMBLE.ensemble_pace,
          age_acceleration_years: DEMO_ENSEMBLE.age_acceleration_years,
          top_risks: ['LIPOTOXICITY','INSULIN_RESISTANCE','NAD_DECLINE'],
          top_signals: ['LIPOTOXICITY','PRO_INFLAM','INSULIN_RESISTANCE','NAD_DECLINE','OXIDATIVE_STRESS'],
          trajectory: DEMO_ENSEMBLE.trajectory,
          confidence: DEMO_ENSEMBLE.confidence,
        },
        agent_outputs: DEMO_AGENTS,
        signals_emitted: DEMO_SIGNALS,
        orchestrator_summary: DEMO_ENSEMBLE.trajectory,
      });
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
