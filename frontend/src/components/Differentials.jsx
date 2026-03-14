function LikelihoodBadge({ likelihood }) {
  const colors = {
    high: 'bg-clinical-critical/20 text-clinical-critical border-clinical-critical/30',
    moderate: 'bg-clinical-warning/20 text-clinical-warning border-clinical-warning/30',
    low: 'bg-clinical-info/20 text-clinical-info border-clinical-info/30',
  }
  return (
    <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded border ${colors[likelihood] || colors.low}`}>
      {likelihood}
    </span>
  )
}

function EvidenceItem({ item, type }) {
  const isFor = type === 'for'
  return (
    <div className="flex items-start gap-2 text-xs py-1">
      <span className={`mt-0.5 text-sm ${isFor ? 'text-clinical-normal' : 'text-clinical-critical'}`}>
        {isFor ? '+' : '-'}
      </span>
      <div className="flex-1">
        <span className="text-clinical-text/80">{item.finding}</span>
        {item.source && (
          <span className="source-badge ml-2">{item.source}</span>
        )}
        {item.strength && (
          <span className={`ml-1 text-[9px] ${
            item.strength === 'strong' ? 'text-clinical-text/60 font-bold' :
            item.strength === 'moderate' ? 'text-clinical-text/40' :
            'text-clinical-text/30'
          }`}>
            [{item.strength}]
          </span>
        )}
      </div>
    </div>
  )
}

function DifferentialCard({ dx, index }) {
  return (
    <div
      className="bg-clinical-surface rounded-lg border border-clinical-border p-4 animate-slide-in"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-clinical-text">{dx.diagnosis}</h3>
        <LikelihoodBadge likelihood={dx.likelihood} />
      </div>

      {/* Evidence For */}
      {dx.evidence_for?.length > 0 && (
        <div className="mb-2">
          <div className="text-[10px] font-bold text-clinical-normal tracking-wider uppercase mb-1">
            Evidence For
          </div>
          {dx.evidence_for.map((e, i) => (
            <EvidenceItem key={i} item={e} type="for" />
          ))}
        </div>
      )}

      {/* Evidence Against */}
      {dx.evidence_against?.length > 0 && (
        <div className="mb-2">
          <div className="text-[10px] font-bold text-clinical-critical tracking-wider uppercase mb-1">
            Evidence Against
          </div>
          {dx.evidence_against.map((e, i) => (
            <EvidenceItem key={i} item={e} type="against" />
          ))}
        </div>
      )}

      {/* Data Gaps */}
      {dx.data_gaps?.length > 0 && (
        <div className="mb-2">
          <div className="text-[10px] font-bold text-clinical-warning tracking-wider uppercase mb-1">
            Data Gaps
          </div>
          <div className="flex flex-wrap gap-1">
            {dx.data_gaps.map((gap, i) => (
              <span key={i} className="text-[10px] px-2 py-0.5 bg-clinical-warning/10 text-clinical-warning border border-clinical-warning/20 rounded">
                {gap}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Workup */}
      {dx.recommended_workup?.length > 0 && (
        <div>
          <div className="text-[10px] font-bold text-clinical-info tracking-wider uppercase mb-1">
            Recommended Workup
          </div>
          <div className="space-y-0.5">
            {dx.recommended_workup.map((w, i) => (
              <div key={i} className="text-xs text-clinical-text/70 flex items-center gap-1">
                <span className="text-clinical-info">→</span> {w}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Differentials({ diagnostic, safety }) {
  const differentials = diagnostic?.differential_diagnoses || []
  const alerts = diagnostic?.critical_alerts || []
  const safetyAlerts = safety?.safety_alerts || []
  const actions = diagnostic?.suggested_actions || []

  if (!diagnostic && !safety) {
    return (
      <div className="text-center text-clinical-text-muted text-sm py-12">
        <div className="text-2xl mb-2">🔬</div>
        <p>Diagnostic reasoning will appear here</p>
        <p className="text-xs mt-1">Ask a clinical question to begin analysis</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Patient Summary */}
      {diagnostic?.patient_summary && (
        <div className="bg-clinical-surface rounded-lg border border-clinical-border p-3">
          <div className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1">
            Assessment
          </div>
          <p className="text-sm text-clinical-text font-medium">
            {diagnostic.patient_summary.one_liner}
          </p>
          {diagnostic.patient_summary.active_situation && (
            <p className="text-xs text-clinical-text/70 mt-1">
              {diagnostic.patient_summary.active_situation}
            </p>
          )}
        </div>
      )}

      {/* Critical Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert, i) => (
            <div
              key={i}
              className={`rounded-lg p-3 border-l-4 ${
                alert.severity === 'critical'
                  ? 'bg-clinical-critical/10 border-clinical-critical'
                  : 'bg-clinical-warning/10 border-clinical-warning'
              }`}
            >
              <div className="text-xs font-bold text-clinical-critical uppercase mb-1">
                {alert.severity === 'critical' ? '⚠ CRITICAL' : '⚡ WARNING'}: {alert.finding?.substring(0, 80)}
              </div>
              <p className="text-xs text-clinical-text/80">{alert.evidence}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="source-badge">{alert.source}</span>
              </div>
              {alert.action_required && (
                <p className="text-xs text-clinical-warning font-medium mt-1">
                  Action: {alert.action_required}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Safety Alerts */}
      {safetyAlerts.length > 0 && (
        <div className="space-y-2">
          {safetyAlerts.map((alert, i) => (
            <div
              key={i}
              className="bg-clinical-critical/10 border-2 border-clinical-critical rounded-lg p-3 safety-alert-glow"
            >
              <div className="text-xs font-bold text-clinical-critical uppercase mb-1">
                🚨 MEDICATION SAFETY: {alert.type} — {alert.medication}
              </div>
              <p className="text-xs text-clinical-text/90">{alert.risk}</p>
              <div className="flex flex-wrap gap-2 mt-1">
                <span className="source-badge">{alert.historical_source}</span>
                <span className="source-badge">{alert.current_source}</span>
              </div>
              <p className="text-xs text-clinical-warning font-bold mt-2">
                {alert.recommended_action}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Differential Cards */}
      {differentials.length > 0 && (
        <div>
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
            Differential Diagnoses ({differentials.length})
          </h3>
          <div className="space-y-3">
            {differentials.map((dx, i) => (
              <DifferentialCard key={i} dx={dx} index={i} />
            ))}
          </div>
        </div>
      )}

      {/* Suggested Actions */}
      {actions.length > 0 && (
        <div className="bg-clinical-surface rounded-lg border border-clinical-border p-3">
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
            Suggested Actions
          </h3>
          <div className="space-y-1.5">
            {actions.map((action, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                  action.priority === 'immediate' ? 'bg-clinical-critical/20 text-clinical-critical' :
                  action.priority === 'urgent' ? 'bg-clinical-warning/20 text-clinical-warning' :
                  'bg-clinical-info/20 text-clinical-info'
                }`}>
                  {action.priority}
                </span>
                <div>
                  <span className="text-clinical-text/90 font-medium">{action.action}</span>
                  <span className="text-clinical-text-muted ml-1">— {action.rationale}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
