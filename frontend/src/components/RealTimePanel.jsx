import { useState } from 'react'
import Sparkline from './Sparkline'
import { LAB_CONFIG, getLabColor, getTrendArrow } from '../utils/constants'

function VitalCard({ label, value, unit, data, color, low, high, highlighted }) {
  const numVal = typeof value === 'string' ? parseFloat(value) : value
  const isAbnormal = numVal < low || numVal > high
  const isCritical = numVal < low * 0.8 || numVal > high * 1.3

  return (
    <div className={`bg-clinical-surface rounded-lg p-2.5 border transition-all ${
      highlighted ? 'border-clinical-warning/60 ring-1 ring-clinical-warning/30' :
      isCritical ? 'border-clinical-critical/50' : isAbnormal ? 'border-clinical-warning/30' : 'border-clinical-border'
    }`}>
      <div className="text-[9px] text-clinical-text-muted uppercase tracking-wider mb-0.5">{label}</div>
      <div className="flex items-end justify-between">
        <div>
          <span className={`text-xl font-bold ${
            isCritical ? 'text-clinical-critical' : isAbnormal ? 'text-clinical-warning' : 'text-clinical-normal'
          }`}>
            {value}
          </span>
          <span className="text-[10px] text-clinical-text-muted ml-1">{unit}</span>
        </div>
        <Sparkline data={data} color={color} width={60} height={20} />
      </div>
    </div>
  )
}

function LabRow({ name, config, timestamps, highlighted }) {
  const allValues = []
  for (const tp of timestamps) {
    if (tp.results[name]) {
      allValues.push({ label: tp.label, ...tp.results[name] })
    }
  }
  if (allValues.length === 0) return null

  const current = allValues[allValues.length - 1]
  const previous = allValues.length > 1 ? allValues[allValues.length - 2] : null
  const arrow = getTrendArrow(current.value, previous?.value)
  const color = getLabColor(current.value, config)

  return (
    <div className={`flex items-center justify-between py-1 px-2 rounded transition-all ${
      highlighted ? 'bg-clinical-warning/10 ring-1 ring-clinical-warning/20' : 'hover:bg-white/5'
    }`}>
      <span className="text-[11px] text-clinical-text-muted w-14">{config.label}</span>
      <div className="flex items-center gap-1.5">
        <span className="text-sm font-bold" style={{ color }}>
          {current.value}
        </span>
        {arrow && (
          <span className={`text-xs font-bold ${
            arrow.includes('\u2193') && (name === 'hemoglobin' || name === 'platelets')
              ? 'text-clinical-critical'
              : arrow.includes('\u2191') && (name === 'bun' || name === 'lactate' || name === 'wbc')
              ? 'text-clinical-critical'
              : 'text-clinical-text-muted'
          }`}>
            {arrow}
          </span>
        )}
        <span className="text-[9px] text-clinical-text-muted">{config.unit}</span>
      </div>
      <span className="source-badge">{current.flag || 'Normal'}</span>
    </div>
  )
}

function QueryResponseCard({ qr, index }) {
  const [showRaw, setShowRaw] = useState(false)

  return (
    <div
      className="bg-clinical-surface rounded-lg border border-clinical-info/30 p-3 animate-slide-in"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="px-1.5 py-0.5 text-[9px] font-bold bg-clinical-info/20 text-clinical-info border border-clinical-info/30 rounded">
          QUERY RESPONSE
        </span>
        {qr.confidence && (
          <span className={`text-[9px] px-1.5 py-0.5 rounded ${
            qr.confidence === 'high' ? 'bg-emerald-500/20 text-emerald-400' :
            qr.confidence === 'moderate' ? 'bg-amber-500/20 text-amber-400' :
            'bg-slate-500/20 text-slate-400'
          }`}>
            {qr.confidence}
          </span>
        )}
      </div>
      <p className="text-[10px] text-clinical-text-muted mb-1">Q: "{qr.question}"</p>
      <div className="text-xs text-clinical-text/90 leading-relaxed whitespace-pre-wrap">
        {qr.answer}
      </div>
      {qr.citations?.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {qr.citations.map((c, j) => (
            <span key={j} className="source-badge" title={c.relevant_text}>
              {c.source}
            </span>
          ))}
        </div>
      )}
      <button
        onClick={() => setShowRaw(!showRaw)}
        className="mt-1 text-[9px] text-clinical-info hover:text-clinical-info/80 font-medium"
      >
        {showRaw ? 'Hide Raw Data' : 'View Raw Data'}
      </button>
      {showRaw && qr.citations?.length > 0 && (
        <div className="mt-1 space-y-1 text-[10px] text-clinical-text/60 pl-2 border-l border-clinical-border">
          {qr.citations.map((c, j) => (
            <div key={j}>
              <span className="font-medium text-clinical-text/80">{c.source}</span>
              {c.relevant_text && <span className="ml-1">— {c.relevant_text}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function DismissedSafetyBanner({ safety }) {
  const [expanded, setExpanded] = useState(false)
  if (!safety?.safety_alerts?.length) return null
  const alert = safety.safety_alerts[0]

  return (
    <div className="bg-clinical-critical/10 border border-clinical-critical/40 rounded-lg p-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-black text-clinical-critical uppercase tracking-wider">
            SAFETY ALERT (ACKNOWLEDGED)
          </span>
          <span className="text-xs text-clinical-text/80 font-medium">
            {alert.medication} — {alert.type}
          </span>
        </div>
        <span className="text-[9px] text-clinical-text-muted">{expanded ? '\u25B2' : '\u25BC'}</span>
      </button>
      {expanded && (
        <div className="mt-2 space-y-1">
          <p className="text-xs text-clinical-text/90">{alert.risk}</p>
          <div className="flex flex-wrap gap-1">
            <span className="source-badge border-clinical-critical/30">{alert.historical_source}</span>
            <span className="source-badge border-clinical-critical/30">{alert.current_source}</span>
          </div>
          <p className="text-xs text-clinical-warning font-bold">{alert.recommended_action}</p>
        </div>
      )}
    </div>
  )
}

export default function RealTimePanel({ patient, diagnostic, queryResponses, safety, dismissedSafetyAlert, intents }) {
  if (!patient) return null

  const vitals = patient.vitals?.trend || []
  const labs = patient.labs?.timestamps || []
  const meds = patient.current_medications || []

  // Extract vital arrays for sparklines
  const bpSystolic = vitals.map(v => v.bp_systolic)
  const heartRate = vitals.map(v => v.heart_rate)
  const spo2 = vitals.map(v => v.spo2)
  const temp = vitals.map(v => v.temp)
  const lastVitals = vitals[vitals.length - 1] || {}

  const keyLabs = ['hemoglobin', 'platelets', 'wbc', 'bun', 'creatinine', 'lactate', 'aptt', 'd_dimer']

  // Determine what's highlighted based on conversation
  const discussedTopics = new Set()
  if (intents?.intents) {
    for (const intent of intents.intents) {
      for (const diff of (intent.differentials_mentioned || [])) {
        discussedTopics.add(diff.toLowerCase())
      }
    }
  }

  const hasConversation = queryResponses.length > 0 || diagnostic

  return (
    <div className="p-4">
      <h2 className="text-xs font-bold text-clinical-text tracking-wider uppercase mb-3">
        Real-Time Intelligence
      </h2>

      {/* Dismissed Safety Alert Banner */}
      {dismissedSafetyAlert && safety && (
        <div className="mb-3">
          <DismissedSafetyBanner safety={safety} />
        </div>
      )}

      {/* Vitals Grid */}
      <div className="mb-4">
        <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1.5">
          Vitals — 8-Hour Trend
        </h3>
        <div className="grid grid-cols-4 gap-1.5">
          <VitalCard
            label="Blood Pressure" value={`${lastVitals.bp_systolic}/${lastVitals.bp_diastolic}`}
            unit="mmHg" data={bpSystolic} color="#ef4444" low={90} high={140}
            highlighted={discussedTopics.has('hypotension')}
          />
          <VitalCard
            label="Heart Rate" value={lastVitals.heart_rate}
            unit="bpm" data={heartRate} color="#22c55e" low={60} high={100}
            highlighted={discussedTopics.has('tachycardia')}
          />
          <VitalCard
            label="SpO2" value={lastVitals.spo2}
            unit="%" data={spo2} color="#a855f7" low={95} high={100}
          />
          <VitalCard
            label="Temp" value={lastVitals.temp}
            unit="\u00B0C" data={temp} color="#f59e0b" low={36.5} high={37.5}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Key Labs */}
        <div>
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1.5">
            Key Labs
          </h3>
          <div className="bg-clinical-surface rounded-lg border border-clinical-border divide-y divide-clinical-border">
            {keyLabs.map(name => {
              const config = LAB_CONFIG[name]
              if (!config) return null
              const formatted = labs.map(tp => ({ label: tp.label, results: tp.results }))
              const highlighted = (name === 'hemoglobin' && discussedTopics.has('gi bleed')) ||
                (name === 'platelets' && (discussedTopics.has('hit') || discussedTopics.has('thrombocytopenia'))) ||
                (name === 'aptt' && discussedTopics.has('heparin'))
              return <LabRow key={name} name={name} config={config} timestamps={formatted} highlighted={highlighted} />
            })}
          </div>
        </div>

        {/* Medications */}
        <div>
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1.5">
            Current Medications
          </h3>
          <div className="bg-clinical-surface rounded-lg border border-clinical-border p-2 space-y-0.5">
            {meds.filter(m => m.status === 'Active' || m.status.startsWith('Active')).map((med, i) => (
              <div key={i} className={`flex items-center justify-between text-[11px] py-0.5 px-1 rounded ${
                med.name === 'Heparin' ? 'bg-clinical-critical/10 border border-clinical-critical/20' : 'hover:bg-white/5'
              }`}>
                <div>
                  <span className={`font-medium ${
                    med.name === 'Heparin' ? 'text-clinical-critical' : 'text-clinical-text/90'
                  }`}>
                    {med.name}
                  </span>
                  <span className="text-clinical-text-muted ml-1 text-[10px]">{med.dose}</span>
                </div>
                {med.name === 'Heparin' && (
                  <span className="text-[8px] font-bold text-clinical-critical px-1 py-0.5 bg-clinical-critical/20 rounded">
                    HIGH-ALERT
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Query Response Cards */}
      {queryResponses.length > 0 && (
        <div className="mb-4">
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1.5">
            Query Responses
          </h3>
          <div className="space-y-2">
            {queryResponses.map((qr, i) => (
              <QueryResponseCard key={i} qr={qr} index={i} />
            ))}
          </div>
        </div>
      )}

      {/* Action Items from diagnostic */}
      {diagnostic?.suggested_actions?.length > 0 && (
        <div>
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1.5">
            Suggested Actions
          </h3>
          <div className="bg-clinical-surface rounded-lg border border-clinical-border p-2 space-y-1">
            {diagnostic.suggested_actions.map((action, i) => (
              <div key={i} className="flex items-start gap-2 text-[11px]">
                <span className={`px-1 py-0.5 rounded text-[8px] font-bold uppercase flex-shrink-0 ${
                  action.priority === 'immediate' ? 'bg-clinical-critical/20 text-clinical-critical' :
                  action.priority === 'urgent' ? 'bg-clinical-warning/20 text-clinical-warning' :
                  'bg-clinical-info/20 text-clinical-info'
                }`}>
                  {action.priority}
                </span>
                <span className="text-clinical-text/80">{action.action}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!hasConversation && !patient && (
        <div className="text-center py-8 text-clinical-text-muted text-sm">
          <p>Real-time data will populate as the conversation progresses</p>
        </div>
      )}
    </div>
  )
}
