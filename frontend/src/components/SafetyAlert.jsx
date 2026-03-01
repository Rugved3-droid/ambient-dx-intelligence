export default function SafetyAlert({ alerts, onDismiss }) {
  if (!alerts || alerts.length === 0) return null

  const alert = alerts[0] // Show the most critical alert

  return (
    <div className="flex-shrink-0 animate-slide-in">
      <div className="mx-2 mt-1 rounded-lg border-2 border-clinical-critical bg-clinical-critical/10 safety-alert-glow">
        <div className="px-4 py-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">⚠️</span>
                <span className="text-sm font-black text-clinical-critical uppercase tracking-wider">
                  CRITICAL SAFETY ALERT
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-clinical-critical text-white rounded uppercase">
                  {alert.type}
                </span>
              </div>

              <p className="text-sm font-bold text-clinical-text mb-2">
                Heparin contraindicated — Prior HIT (2023). Platelets dropping &gt;50%.
                STOP HEPARIN. Consider argatroban.
              </p>

              <div className="flex flex-wrap gap-2 mb-2">
                <span className="source-badge border-clinical-critical/30">
                  {alert.historical_source || 'Discharge Summary — Dr. Park, 2023'}
                </span>
                <span className="source-badge border-clinical-critical/30">
                  Lab Trend — Platelets (245→89, -63.7%)
                </span>
                <span className="source-badge border-clinical-critical/30">
                  {alert.current_source || 'Medication List — Heparin (Active)'}
                </span>
              </div>

              <p className="text-xs text-clinical-warning font-medium">
                {alert.recommended_action}
              </p>
            </div>

            <button
              onClick={onDismiss}
              className="text-clinical-text-muted hover:text-clinical-text text-lg ml-4 flex-shrink-0"
              title="Acknowledge alert"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
