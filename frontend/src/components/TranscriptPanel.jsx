import { useEffect, useRef } from 'react'

const SPEAKER_COLORS = {
  'Nurse (RN Torres)': '#22c55e',
  'Resident (Dr. Zhao)': '#3b82f6',
  'Senior (Dr. Patel)': '#a855f7',
}

function getSpeakerColor(speaker) {
  return SPEAKER_COLORS[speaker] || '#94a3b8'
}

export default function TranscriptPanel({ transcript, intents, phase }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [transcript])

  const actionItems = intents?.action_items || []

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Transcript feed */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
        {transcript.length === 0 && (
          <div className="text-center text-clinical-text-muted text-sm py-8">
            <div className="text-2xl mb-2">🎙️</div>
            <p>Waiting for clinical conversation...</p>
            <p className="text-xs mt-1">Start the demo or enable live mic</p>
          </div>
        )}
        {transcript.map((entry, i) => {
          const color = getSpeakerColor(entry.speaker)
          // Check if this line contains a clinical intent keyword
          const text = entry.text || ''
          const hasIntent = /\b(GI bleed|PE|pulmonary embolism|heparin|platelet|hemoglobin|hypotension|tachycardia|Wells|HIT|bleed)\b/i.test(text)

          return (
            <div key={i} className="animate-fade-in">
              <div className="flex items-baseline gap-2 mb-0.5">
                <span className="text-[10px] font-bold tracking-wider uppercase" style={{ color }}>
                  {entry.speaker}
                </span>
                {entry.phase > 0 && (
                  <span className="text-[9px] text-clinical-text-muted">
                    Phase {entry.phase}
                  </span>
                )}
              </div>
              <p className={`text-sm leading-relaxed ${
                hasIntent
                  ? 'text-clinical-warning bg-clinical-warning/5 px-2 py-1 rounded border-l-2 border-clinical-warning/40'
                  : 'text-clinical-text/90'
              }`}>
                {text}
              </p>
            </div>
          )
        })}
      </div>

      {/* Action Items */}
      {actionItems.length > 0 && (
        <div className="flex-shrink-0 border-t border-clinical-border p-3">
          <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase mb-2">
            Action Items
          </h3>
          <div className="space-y-1">
            {actionItems.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className={`w-1.5 h-1.5 rounded-full ${
                  item.priority === 'stat' ? 'bg-clinical-critical' :
                  item.priority === 'urgent' ? 'bg-clinical-warning' :
                  'bg-clinical-info'
                }`}></span>
                <span className="text-clinical-text/80">{item.action}</span>
                <span className="text-[9px] text-clinical-text-muted uppercase">
                  [{item.status}]
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Intent summary */}
      {intents?.intents?.length > 0 && (
        <div className="flex-shrink-0 border-t border-clinical-border p-3 bg-clinical-info/5">
          <h3 className="text-[10px] font-bold text-clinical-info tracking-wider uppercase mb-1">
            Clinical Intent Detected
          </h3>
          {intents.intents.map((intent, i) => (
            <div key={i} className="text-xs text-clinical-text/80">
              <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase mr-2 ${
                intent.urgency === 'critical' ? 'bg-clinical-critical/20 text-clinical-critical' :
                intent.urgency === 'high' ? 'bg-clinical-warning/20 text-clinical-warning' :
                'bg-clinical-info/20 text-clinical-info'
              }`}>
                {intent.urgency}
              </span>
              {intent.summary}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
