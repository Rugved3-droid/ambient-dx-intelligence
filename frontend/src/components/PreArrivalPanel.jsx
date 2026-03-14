const STRENGTH_CONFIG = {
  Strong:   { color: '#ef4444', width: '85%', bg: 'bg-clinical-critical/15' },
  Moderate: { color: '#f59e0b', width: '55%', bg: 'bg-clinical-warning/15' },
  Weak:     { color: '#3b82f6', width: '30%', bg: 'bg-clinical-info/15' },
}

function StrengthBar({ strength }) {
  const cfg = STRENGTH_CONFIG[strength] || STRENGTH_CONFIG.Weak
  return (
    <div className="w-20 h-1.5 rounded-full bg-white/5 overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: cfg.width, background: cfg.color }}
      />
    </div>
  )
}

function formatScore(score) {
  if (!score) return null
  // Pull the short label: "Wells 4.5" or "4Ts 6" or "qSOFA 2"
  const name = score.name
    .replace('Score for PE', '')
    .replace('Score for HIT', '')
    .replace('Score', '')
    .trim()
  return `${name} ${score.value}`
}

function DifferentialRow({ diff, isHighlighted }) {
  const strength = diff.evidence_strength || 'Weak'
  const dotColor =
    strength === 'Strong' ? 'bg-clinical-critical' :
    strength === 'Moderate' ? 'bg-clinical-warning' :
    'bg-clinical-info'
  const score = formatScore(diff.clinical_score)

  return (
    <div
      className={`flex items-center gap-3 px-3 py-2 rounded transition-all ${
        isHighlighted
          ? 'bg-clinical-warning/8 ring-1 ring-clinical-warning/25'
          : 'hover:bg-white/[0.02]'
      }`}
    >
      {/* Severity dot */}
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor}`} />

      {/* Rank */}
      <span className="text-[10px] font-bold text-clinical-text-muted w-4 text-right flex-shrink-0">
        {diff.rank}
      </span>

      {/* Diagnosis name */}
      <span className={`text-xs font-semibold flex-1 truncate ${
        isHighlighted ? 'text-clinical-text' : 'text-clinical-text/85'
      }`}>
        {diff.name}
      </span>

      {/* Score chip */}
      {score ? (
        <span className="text-[10px] font-bold text-clinical-text-muted bg-white/5 px-1.5 py-0.5 rounded whitespace-nowrap flex-shrink-0">
          {score}
        </span>
      ) : (
        <span className="w-16 flex-shrink-0" />
      )}

      {/* Evidence bar */}
      <StrengthBar strength={strength} />

      {/* Findings count */}
      <span className="text-[9px] text-clinical-text-muted w-3 text-right flex-shrink-0">
        {diff.supporting_count}
      </span>
    </div>
  )
}

export default function PreArrivalPanel({ preArrival, diagnostic, patient, highlightedDifferentials }) {
  if (!preArrival && !patient) return null

  const differentials = preArrival?.differentials || []
  const safetyFlags = (preArrival?.safety_flags || []).filter(f => f.severity === 'critical')
  const highlightSet = new Set((highlightedDifferentials || []).map(d => d.toLowerCase()))

  return (
    <div className="p-4 border-b border-clinical-border">
      {/* Header row */}
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase">
          Differential Considerations
        </h2>
        {preArrival && (
          <span className="text-[9px] text-clinical-text-muted">
            {differentials.length} from EMR
          </span>
        )}
      </div>

      {!preArrival && (
        <div className="text-center py-6 text-clinical-text-muted text-xs">
          Click "Load Patient" to generate pre-arrival intelligence
        </div>
      )}

      {preArrival && (
        <>
          {/* Column labels */}
          <div className="flex items-center gap-3 px-3 mb-0.5">
            <span className="w-2 flex-shrink-0" />
            <span className="w-4 flex-shrink-0" />
            <span className="text-[8px] text-clinical-text-muted/50 uppercase tracking-wider flex-1">Diagnosis</span>
            <span className="text-[8px] text-clinical-text-muted/50 uppercase tracking-wider w-16 flex-shrink-0 text-center">Score</span>
            <span className="text-[8px] text-clinical-text-muted/50 uppercase tracking-wider w-20 flex-shrink-0">Evidence</span>
            <span className="w-3 flex-shrink-0" />
          </div>

          {/* Leaderboard rows */}
          <div className="divide-y divide-clinical-border/30">
            {differentials.map((diff) => {
              const isHighlighted = highlightSet.has(diff.name?.toLowerCase()) ||
                highlightedDifferentials?.some(h =>
                  diff.name?.toLowerCase().includes(h.toLowerCase()) ||
                  h.toLowerCase().includes(diff.name?.toLowerCase()?.split(' ')[0])
                )
              return (
                <DifferentialRow
                  key={diff.rank}
                  diff={diff}
                  isHighlighted={isHighlighted}
                />
              )
            })}
          </div>

          {/* Safety flag line */}
          {safetyFlags.length > 0 && (
            <div className="flex items-center gap-3 px-3 py-2 mt-1 rounded bg-clinical-critical/8 border border-clinical-critical/20">
              <span className="w-2 h-2 rounded-full bg-clinical-critical animate-pulse flex-shrink-0" />
              <span className="text-[10px] font-black text-clinical-critical uppercase tracking-wider flex-shrink-0">
                SAFETY
              </span>
              <span className="text-[11px] text-clinical-text/90 font-medium truncate">
                {safetyFlags[0].flag}
              </span>
            </div>
          )}
        </>
      )}
    </div>
  )
}
