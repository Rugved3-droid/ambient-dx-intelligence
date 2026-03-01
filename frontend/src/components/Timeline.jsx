export default function Timeline({ patient, safetyAlertActive }) {
  const notes = patient?.clinical_notes || []

  // Sort chronologically
  const sorted = [...notes].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  )

  const formatDate = (ts) => {
    const d = new Date(ts)
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const noteTypeColor = (type) => {
    switch (type) {
      case 'Discharge Summary': return 'border-clinical-critical'
      case 'Surgical Note': return 'border-clinical-info'
      case 'Progress Note': return 'border-clinical-normal'
      case 'Nursing Note': return 'border-clinical-warning'
      default: return 'border-clinical-border'
    }
  }

  const noteTypeBg = (type) => {
    switch (type) {
      case 'Discharge Summary': return 'bg-clinical-critical/5'
      case 'Surgical Note': return 'bg-clinical-info/5'
      case 'Progress Note': return 'bg-clinical-normal/5'
      case 'Nursing Note': return 'bg-clinical-warning/5'
      default: return 'bg-clinical-surface'
    }
  }

  return (
    <div className="space-y-3 animate-fade-in">
      <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase">
        Clinical Notes Timeline
      </h3>

      {sorted.map((note, i) => {
        const isHITNote = note.title?.includes('Heparin-Induced') || note.content?.includes('HIT')
        const isHighlighted = isHITNote && safetyAlertActive

        return (
          <div
            key={i}
            className={`rounded-lg border-l-4 ${noteTypeColor(note.type)} ${noteTypeBg(note.type)} p-3 ${
              isHighlighted ? 'ring-2 ring-clinical-critical safety-alert-glow' : ''
            } animate-slide-in`}
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-bold uppercase tracking-wider ${
                  note.type === 'Discharge Summary' ? 'text-clinical-critical' :
                  note.type === 'Nursing Note' ? 'text-clinical-warning' :
                  note.type === 'Surgical Note' ? 'text-clinical-info' :
                  'text-clinical-normal'
                }`}>
                  {note.type}
                </span>
                {isHighlighted && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-clinical-critical/20 text-clinical-critical rounded animate-pulse">
                    SAFETY-RELEVANT
                  </span>
                )}
                {note.title?.includes('RAPID RESPONSE') && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-clinical-critical/20 text-clinical-critical rounded">
                    URGENT
                  </span>
                )}
              </div>
              <span className="text-[10px] text-clinical-text-muted">
                {formatDate(note.timestamp)}
              </span>
            </div>

            <div className="text-xs text-clinical-text/60 mb-1">{note.author}</div>
            <h4 className="text-xs font-bold text-clinical-text/90 mb-2">{note.title}</h4>

            <pre className="text-xs text-clinical-text/70 whitespace-pre-wrap font-mono leading-relaxed max-h-48 overflow-y-auto">
              {note.content}
            </pre>
          </div>
        )
      })}
    </div>
  )
}
