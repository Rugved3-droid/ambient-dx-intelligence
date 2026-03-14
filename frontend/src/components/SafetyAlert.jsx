import { useState } from 'react'

export default function SafetyAlert({ alerts, onDismiss }) {
  const [showDetails, setShowDetails] = useState(true)
  if (!alerts || alerts.length === 0) return null

  const alert = alerts[0]

  return (
    <div className="flex-shrink-0 safety-alert-slide-in">
      <div className="mx-2 mt-1 rounded-lg border-2 border-clinical-critical bg-clinical-critical/10 safety-alert-glow">
        <div className="px-4 py-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Header */}
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg animate-pulse">&#9888;&#65039;</span>
                <span className="text-sm font-black text-clinical-critical uppercase tracking-wider">
                  CRITICAL SAFETY ALERT
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-clinical-critical text-white rounded uppercase">
                  {alert.type}
                </span>
              </div>

              {/* Main message */}
              <p className="text-sm font-bold text-clinical-text mb-2">
                Heparin CONTRAINDICATED — Prior HIT (2023). Platelets dropping &gt;50%.
              </p>

              {/* Evidence Chain */}
              <div className="space-y-1.5 mb-3">
                <div className="text-[10px] font-bold text-clinical-critical uppercase tracking-wider">
                  Evidence Chain
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-clinical-critical/5 border border-clinical-critical/20 rounded p-2">
                    <div className="text-[9px] font-bold text-clinical-critical uppercase mb-0.5">Prior HIT</div>
                    <p className="text-[10px] text-clinical-text/80">
                      Positive PF4 antibody (OD 2.4), positive SRA
                    </p>
                    <span className="source-badge border-clinical-critical/30 mt-1 inline-block">
                      {alert.historical_source || 'Discharge Summary 2023 — Dr. Thompson'}
                    </span>
                  </div>
                  <div className="bg-clinical-critical/5 border border-clinical-critical/20 rounded p-2">
                    <div className="text-[9px] font-bold text-clinical-critical uppercase mb-0.5">Current Heparin</div>
                    <p className="text-[10px] text-clinical-text/80">
                      Heparin drip 18 units/kg/hr started 2026-03-10
                    </p>
                    <span className="source-badge border-clinical-critical/30 mt-1 inline-block">
                      {alert.current_source || 'Medication List — Heparin (Active)'}
                    </span>
                  </div>
                  <div className="bg-clinical-critical/5 border border-clinical-critical/20 rounded p-2">
                    <div className="text-[9px] font-bold text-clinical-critical uppercase mb-0.5">Platelet Decline</div>
                    <p className="text-[10px] text-clinical-text/80">
                      220 → 198 → 156 → 89 K/uL (&gt;50% decline over 4 days on heparin)
                    </p>
                    <span className="source-badge border-clinical-critical/30 mt-1 inline-block">
                      Lab Trend — Platelets
                    </span>
                  </div>
                </div>
              </div>

              {/* 4Ts Score */}
              {showDetails && (
                <div className="bg-clinical-surface/50 border border-clinical-border rounded p-2 mb-3">
                  <div className="text-[10px] font-bold text-clinical-warning uppercase tracking-wider mb-1">
                    4Ts Score: 6/8 — High Probability
                  </div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-[10px]">
                    <div><span className="text-clinical-warning font-bold">+2</span> <span className="text-clinical-text/70">Thrombocytopenia (&gt;50% fall, nadir 89)</span></div>
                    <div><span className="text-clinical-warning font-bold">+2</span> <span className="text-clinical-text/70">Timing (day 4-5, prior HIT exposure)</span></div>
                    <div><span className="text-clinical-warning font-bold">+1</span> <span className="text-clinical-text/70">Thrombosis suspected (tachycardia, D-dimer)</span></div>
                    <div><span className="text-clinical-warning font-bold">+1</span> <span className="text-clinical-text/70">Other causes possible but less likely</span></div>
                  </div>
                </div>
              )}

              {/* Recommended Actions */}
              <div className="flex flex-wrap gap-2 mb-2">
                {['STOP HEPARIN', 'Consider argatroban', 'STAT HIT antibody (PF4)', 'Hematology consult'].map((action, i) => (
                  <span key={i} className={`px-2 py-1 text-[10px] font-bold rounded ${
                    i === 0
                      ? 'bg-clinical-critical text-white'
                      : 'bg-clinical-warning/20 text-clinical-warning border border-clinical-warning/30'
                  }`}>
                    {action}
                  </span>
                ))}
              </div>

              <p className="text-[9px] text-clinical-text-muted">
                Argatroban was used successfully in 2023 HIT episode (per discharge summary)
              </p>
            </div>

            {/* Dismiss button */}
            <button
              onClick={onDismiss}
              className="text-clinical-text-muted hover:text-clinical-text text-lg ml-4 flex-shrink-0"
              title="Acknowledge alert"
            >
              &#10005;
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
