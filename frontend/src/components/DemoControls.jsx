export default function DemoControls({ status, onReset, onProcess, connected, micActive, micMode, onToggleMic }) {
  const isProcessing = status?.stage && !['idle', 'complete', 'demo_complete'].includes(status.stage)

  return (
    <div className="flex-shrink-0 border-t border-clinical-border bg-[#0d1321] px-4 py-2">
      <div className="flex items-center justify-between">
        {/* Left: Controls */}
        <div className="flex items-center gap-3">
          {/* Live Mic Toggle — primary action */}
          <button
            onClick={onToggleMic}
            className={`mic-toggle-btn ${micActive ? 'mic-active' : ''}`}
            title={micActive ? `Mic ON (${micMode || 'connecting'})` : 'Enable Live Mic'}
          >
            <span className={`mic-icon ${micActive ? 'mic-icon-active' : ''}`}>🎙</span>
            <span>{micActive ? 'MIC ON' : 'LIVE MIC'}</span>
          </button>

          <button
            onClick={onProcess}
            disabled={!connected || isProcessing}
            className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider bg-clinical-surface hover:bg-clinical-border-light disabled:opacity-50 text-clinical-text-muted rounded border border-clinical-border transition-colors"
          >
            Analyze Now
          </button>

          <button
            onClick={onReset}
            disabled={!connected}
            className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-clinical-text-muted hover:text-clinical-critical hover:bg-clinical-critical/10 rounded transition-colors"
          >
            Clear
          </button>
        </div>

        {/* Center: Processing indicator */}
        <div className="flex items-center gap-2">
          {isProcessing && (
            <div className="processing-stage-indicator">
              <span className="processing-spinner"></span>
              <span className="text-xs text-clinical-info font-medium">
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
