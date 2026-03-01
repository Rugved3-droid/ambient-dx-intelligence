import Sparkline from './Sparkline'
import { LAB_CONFIG, VITAL_CONFIG, getLabColor, getTrendArrow } from '../utils/constants'

function VitalCard({ label, value, unit, data, color, low, high }) {
  const isAbnormal = value < low || value > high
  const isCritical = value < low * 0.8 || value > high * 1.3

  return (
    <div className={`bg-clinical-surface rounded-lg p-3 border ${
      isCritical ? 'border-clinical-critical/50' : isAbnormal ? 'border-clinical-warning/30' : 'border-clinical-border'
    }`}>
      <div className="text-[10px] text-clinical-text-muted uppercase tracking-wider mb-1">{label}</div>
      <div className="flex items-end justify-between">
        <div>
          <span className={`text-2xl font-bold ${
            isCritical ? 'text-clinical-critical' : isAbnormal ? 'text-clinical-warning' : 'text-clinical-normal'
          }`}>
            {value}
          </span>
          <span className="text-xs text-clinical-text-muted ml-1">{unit}</span>
        </div>
        <Sparkline data={data} color={color} width={80} height={24} />
      </div>
    </div>
  )
}

function LabValue({ name, config, timestamps }) {
  // Find current and previous values
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
    <div className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-white/5">
      <span className="text-xs text-clinical-text-muted w-16">{config.label}</span>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold" style={{ color }}>
          {current.value}
        </span>
        {arrow && (
          <span className={`text-sm font-bold ${
            arrow.includes('↓') && (name === 'hemoglobin' || name === 'platelets')
              ? 'text-clinical-critical'
              : arrow.includes('↑') && (name === 'bun' || name === 'lactate' || name === 'wbc')
              ? 'text-clinical-critical'
              : 'text-clinical-text-muted'
          }`}>
            {arrow}
          </span>
        )}
        <span className="text-[10px] text-clinical-text-muted">{config.unit}</span>
      </div>
      <span className="source-badge">
        {current.flag || 'Normal'}
      </span>
    </div>
  )
}

export default function Dashboard({ patient, diagnostic }) {
  if (!patient) return null

  const vitals = patient.vitals?.trend || []
  const labs = patient.labs?.timestamps || []
  const meds = patient.current_medications || []
  const problems = patient.problem_list || []

  // Extract vital sign arrays for sparklines
  const bpSystolic = vitals.map(v => v.bp_systolic)
  const bpDiastolic = vitals.map(v => v.bp_diastolic)
  const heartRate = vitals.map(v => v.heart_rate)
  const respRate = vitals.map(v => v.resp_rate)
  const spo2 = vitals.map(v => v.spo2)
  const temp = vitals.map(v => v.temp)

  const lastVitals = vitals[vitals.length - 1] || {}

  // Key labs to display
  const keyLabs = ['hemoglobin', 'platelets', 'wbc', 'bun', 'creatinine', 'lactate', 'aptt', 'd_dimer']

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Vitals Grid */}
      <div>
        <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
          Vitals — Trending Over 8 Hours
        </h3>
        <div className="grid grid-cols-3 gap-2">
          <VitalCard
            label="Blood Pressure"
            value={`${lastVitals.bp_systolic}/${lastVitals.bp_diastolic}`}
            unit="mmHg"
            data={bpSystolic}
            color="#ef4444"
            low={90}
            high={140}
          />
          <VitalCard
            label="Heart Rate"
            value={lastVitals.heart_rate}
            unit="bpm"
            data={heartRate}
            color="#22c55e"
            low={60}
            high={100}
          />
          <VitalCard
            label="SpO2"
            value={lastVitals.spo2}
            unit="%"
            data={spo2}
            color="#a855f7"
            low={95}
            high={100}
          />
          <VitalCard
            label="Resp Rate"
            value={lastVitals.resp_rate}
            unit="/min"
            data={respRate}
            color="#3b82f6"
            low={12}
            high={20}
          />
          <VitalCard
            label="Temperature"
            value={lastVitals.temp}
            unit="°C"
            data={temp}
            color="#f59e0b"
            low={36.5}
            high={37.5}
          />
          <VitalCard
            label="MAP"
            value={Math.round(lastVitals.bp_diastolic + (lastVitals.bp_systolic - lastVitals.bp_diastolic) / 3)}
            unit="mmHg"
            data={bpSystolic.map((s, i) => Math.round(bpDiastolic[i] + (s - bpDiastolic[i]) / 3))}
            color="#f97316"
            low={65}
            high={100}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Key Labs */}
        <div>
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
            Key Lab Values
          </h3>
          <div className="bg-clinical-surface rounded-lg border border-clinical-border divide-y divide-clinical-border">
            {keyLabs.map(name => {
              const config = LAB_CONFIG[name]
              if (!config) return null
              // Build timestamps with results format
              const formatted = labs.map(tp => ({
                label: tp.label,
                results: tp.results,
              }))
              return <LabValue key={name} name={name} config={config} timestamps={formatted} />
            })}
          </div>
        </div>

        {/* Medications + Problems */}
        <div className="space-y-4">
          <div>
            <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
              Active Medications
            </h3>
            <div className="bg-clinical-surface rounded-lg border border-clinical-border p-2 space-y-1">
              {meds.filter(m => m.status === 'Active' || m.status.startsWith('Active')).map((med, i) => (
                <div key={i} className="flex items-center justify-between text-xs py-1 px-1 rounded hover:bg-white/5">
                  <div>
                    <span className={`font-medium ${
                      med.name === 'Heparin' ? 'text-clinical-critical' : 'text-clinical-text/90'
                    }`}>
                      {med.name}
                    </span>
                    <span className="text-clinical-text-muted ml-1">{med.dose}</span>
                  </div>
                  <span className="source-badge">{med.route} {med.frequency}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
              Problem List
            </h3>
            <div className="bg-clinical-surface rounded-lg border border-clinical-border p-2 space-y-1">
              {problems.map((prob, i) => (
                <div key={i} className={`text-xs py-1 px-1 rounded ${
                  prob.critical_flag ? 'bg-clinical-critical/10 border border-clinical-critical/20' : 'hover:bg-white/5'
                }`}>
                  <span className={prob.critical_flag ? 'text-clinical-critical font-bold' : 'text-clinical-text/80'}>
                    {prob.problem.split('—')[0].trim()}
                  </span>
                  <span className="text-clinical-text-muted ml-1 text-[10px]">
                    [{prob.status.split('—')[0].trim()}]
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
