export default function DemoControls({
  status, demoPhase, onReset, onProcess, onLoadPatient, onStartDemo, onRunPhase,
  connected, micActive, micMode, onToggleMic, preArrivalLoaded
}) {
  const isProcessing = status?.stage && !['idle', 'complete', 'demo_complete'].includes(status.stage)

  const phases = [
    { num: 0, label: 'Pre-Arrival', short: 'P0' },
    { num: 1, label: 'Initial', short: 'P1' },
    { num: 2, label: 'GI Bleed', short: 'P2' },
    { num: 3, label: 'PE + Queries', short: 'P3' },
    { num: 4, label: 'HIT Catch', short: 'P4' },
  ]

  return (
    <div className="flex-shrink-0 border-t border-clinical-border bg-[#0d1321] px-4 py-2">
      <div className="flex items-center justify-between">
        {/* Left: Demo Controls */}
        <div className="flex items-center gap-2">
          {/* Load Patient / Start Demo */}
          {!preArrivalLoaded ? (
            <button
              onClick={onLoadPatient}
              disabled={!connected || isProcessing}
              className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider bg-gradient-to-r from-indigo-600 to-blue-500 text-white rounded border-0 transition-opacity disabled:opacity-50 hover:opacity-90"
            >
              Load Patient
            </button>
          ) : (
            <button
              onClick={() => onStartDemo(8)}
              disabled={!connected || isProcessing || demoPhase >= 1}
              className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider bg-gradient-to-r from-emerald-600 to-green-500 text-white rounded border-0 transition-opacity disabled:opacity-50 hover:opacity-90"
            >
              Start Rapid Response
            </button>
          )}

          {/* Phase indicators */}
          <div className="flex items-center gap-1 ml-2">
            {phases.map(p => (
              <button
                key={p.num}
                onClick={() => onRunPhase(p.num)}
                disabled={!connected || isProcessing}
                className={`px-2 py-1 text-[9px] font-bold rounded transition-all ${
                  p.num < demoPhase
                    ? 'bg-clinical-normal/20 text-clinical-normal border border-clinical-normal/30'
                    : p.num === demoPhase
                    ? 'bg-clinical-info/20 text-clinical-info border border-clinical-info/40 live-dot'
                    : 'bg-clinical-surface text-clinical-text-muted border border-clinical-border hover:border-clinical-border-light'
                }`}
                title={p.label}
              >
                {p.short}
              </button>
            ))}
          </div>

          <div className="w-px h-5 bg-clinical-border mx-1"></div>

          {/* Live Mic Toggle */}
          <button
            onClick={onToggleMic}
            className={`mic-toggle-btn ${micActive ? 'mic-active' : ''}`}
            title={micActive ? `Mic ON (${micMode || 'connecting'})` : 'Enable Live Mic'}
          >
            <span className={`mic-icon ${micActive ? 'mic-icon-active' : ''}`}>&#127908;</span>
            <span>{micActive ? 'MIC ON' : 'LIVE MIC'}</span>
          </button>

          <button
            onClick={onProcess}
            disabled={!connected || isProcessing}
            className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider bg-clinical-surface hover:bg-clinical-border-light disabled:opacity-50 text-clinical-text-muted rounded border border-clinical-border transition-colors"
          >
            Analyze
          </button>

          <button
            onClick={onReset}
            disabled={!connected}
            className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-clinical-text-muted hover:text-clinical-critical hover:bg-clinical-critical/10 rounded transition-colors"
          >
            Reset
          </button>
        </div>

        {/* Center: Processing indicator */}
        <div className="flex items-center gap-2">
          {isProcessing && (
            <div className="flex items-center gap-2">
              <span className="processing-spinner"></span>
              <span className="text-[10px] text-clinical-info font-medium">
                {status.stage?.replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Right: Mode indicator */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-clinical-text-muted uppercase">Mode:</span>
          {micActive ? (
            <span className="px-2 py-0.5 text-[10px] font-bold bg-clinical-critical/20 text-clinical-critical border border-clinical-critical/30 rounded mic-mode-badge">
              LIVE {micMode === 'deepgram' ? 'DEEPGRAM' : 'WEB SPEECH'}
            </span>
          ) : demoPhase >= 0 ? (
            <span className="px-2 py-0.5 text-[10px] font-bold bg-clinical-info/20 text-clinical-info border border-clinical-info/30 rounded">
              DEMO
            </span>
          ) : (
            <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded">
              INTERACTIVE
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
