export default function DemoControls({ phase, status, onStartDemo, onRunPhase, onReset, onProcess, connected }) {
  const phaseLabels = {
    1: 'Rapid Response',
    2: 'GI Bleed Discussion',
    3: 'PE + HIT Catch',
  }

  const isProcessing = status?.stage && !['idle', 'complete', 'demo_complete'].includes(status.stage)

  return (
    <div className="flex-shrink-0 border-t border-clinical-border bg-[#0d1321] px-4 py-2">
      <div className="flex items-center justify-between">
        {/* Left: Demo controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={onStartDemo}
            disabled={!connected || isProcessing}
            className="px-4 py-1.5 text-xs font-bold uppercase tracking-wider bg-clinical-info hover:bg-clinical-info/80 disabled:bg-clinical-border disabled:text-clinical-text-muted text-white rounded transition-colors"
          >
            Start Demo
          </button>

          <div className="flex items-center gap-1">
            {[1, 2, 3].map(n => (
              <button
                key={n}
                onClick={() => onRunPhase(n)}
                disabled={!connected || isProcessing}
                className={`px-3 py-1.5 text-[10px] font-bold uppercase rounded transition-all ${
                  phase.phase === n && phase.status === 'started'
                    ? 'phase-active text-white'
                    : phase.phase > n || (phase.phase === n && phase.status === 'complete')
                    ? 'phase-complete text-white'
                    : 'phase-pending text-clinical-text-muted hover:bg-clinical-border-light disabled:opacity-50'
                }`}
                title={phaseLabels[n]}
              >
                P{n}
              </button>
            ))}
          </div>

          <button
            onClick={onProcess}
            disabled={!connected || isProcessing}
            className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider bg-clinical-surface hover:bg-clinical-border-light disabled:opacity-50 text-clinical-text-muted rounded border border-clinical-border transition-colors"
          >
            Process Now
          </button>

          <button
            onClick={onReset}
            disabled={!connected}
            className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-clinical-text-muted hover:text-clinical-critical hover:bg-clinical-critical/10 rounded transition-colors"
          >
            Reset
          </button>
        </div>

        {/* Center: Phase indicator */}
        <div className="flex items-center gap-2">
          {phase.phase > 0 && (
            <>
              <span className="text-[10px] text-clinical-text-muted uppercase">Phase {phase.phase}:</span>
              <span className="text-xs text-clinical-text font-medium">{phase.title}</span>
              <span className={`w-2 h-2 rounded-full ${
                phase.status === 'processing' ? 'bg-clinical-warning live-dot' :
                phase.status === 'complete' ? 'bg-clinical-normal' :
                phase.status === 'started' ? 'bg-clinical-info live-dot' :
                'bg-clinical-border'
              }`}></span>
            </>
          )}
          {status?.stage === 'demo_complete' && (
            <span className="text-xs text-clinical-normal font-medium">Demo Complete</span>
          )}
        </div>

        {/* Right: Mode indicator */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-clinical-text-muted uppercase">Mode:</span>
          <span className="px-2 py-0.5 text-[10px] font-bold bg-clinical-info/20 text-clinical-info border border-clinical-info/30 rounded">
            DEMO SCRIPT
          </span>
        </div>
      </div>
    </div>
  )
}
