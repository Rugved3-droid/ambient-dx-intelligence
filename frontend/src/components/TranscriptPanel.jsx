import { useState, useEffect, useRef } from 'react'

const SPEAKER_COLORS = {
  'Nurse (RN Torres)': '#22c55e',
  'Resident (Dr. Zhao)': '#3b82f6',
  'Senior (Dr. Patel)': '#a855f7',
  'Code Leader (Dr. Patel)': '#ec4899',
  'Live Speaker': '#f59e0b',
  'Judge': '#ec4899',
  'Query': '#ec4899',
}

function getSpeakerColor(speaker) {
  return SPEAKER_COLORS[speaker] || '#94a3b8'
}

function detectIntentType(text, intentType) {
  // Direct query patterns
  if (intentType === 'direct_query') return 'query'
  const queryPatterns = /^(what['s]?\s|show\s+me|calculate|check|is\s+he\s+on|when\s+was|does\s+he|any\s+prior|what\s+does)/i
  if (queryPatterns.test(text)) return 'query'
  // Clinical discussion
  const clinicalPatterns = /\b(GI bleed|PE|pulmonary embolism|heparin|platelet|hemoglobin|hypotension|tachycardia|Wells|HIT|bleed|sepsis|hemorrhage|DVT|surgery|post.op)\b/i
  if (clinicalPatterns.test(text)) return 'clinical'
  return null
}

export default function TranscriptPanel({ transcript, intents, partialTranscript, onQuery, isProcessing }) {
  const scrollRef = useRef(null)
  const [queryText, setQueryText] = useState('')

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [transcript, partialTranscript])

  const actionItems = intents?.action_items || []

  const handleQuerySubmit = (e) => {
    e.preventDefault()
    if (!queryText.trim() || isProcessing) return
    onQuery(queryText.trim())
    setQueryText('')
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Transcript feed */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {transcript.length === 0 && !partialTranscript && (
          <div className="text-center text-clinical-text-muted text-sm py-8">
            <div className="text-2xl mb-2">&#129504;</div>
            <p className="text-clinical-text/70 font-medium">Ask me anything about this patient</p>
            <p className="text-xs mt-2 text-clinical-text-muted">
              Type a question below or enable Live Mic
            </p>
            <div className="mt-4 space-y-1.5">
              {['Does this patient have a PE risk?',
                'What about HIT?',
                'Summarize the lab trends',
                'Any medication safety concerns?'
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => onQuery(q)}
                  className="follow-up-btn block mx-auto"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {transcript.map((entry, i) => {
          const color = getSpeakerColor(entry.speaker)
          const text = entry.text || ''
          const intentType = detectIntentType(text, entry.intent_type)

          // AI Answer — special rendering
          if (entry.isAnswer) {
            return (
              <div key={i} className="animate-fade-in ai-answer-block">
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-[10px] font-bold tracking-wider uppercase text-emerald-400">
                    AI Assistant
                  </span>
                  {entry.confidence && (
                    <span className={`text-[9px] px-1.5 py-0.5 rounded ${
                      entry.confidence === 'high' ? 'bg-emerald-500/20 text-emerald-400' :
                      entry.confidence === 'moderate' ? 'bg-amber-500/20 text-amber-400' :
                      'bg-slate-500/20 text-slate-400'
                    }`}>
                      {entry.confidence} confidence
                    </span>
                  )}
                </div>
                <div className="ai-answer-text text-xs leading-relaxed text-clinical-text/90">
                  {text}
                </div>
                {entry.citations?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {entry.citations.map((c, j) => (
                      <span key={j} className="source-badge" title={c.relevant_text}>
                        {c.source}
                      </span>
                    ))}
                  </div>
                )}
                {entry.followUp?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {entry.followUp.map((q, j) => (
                      <button
                        key={j}
                        onClick={() => { if (onQuery) onQuery(q) }}
                        className="follow-up-btn"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          }

          // Regular transcript entry
          return (
            <div key={i} className="animate-fade-in">
              <div className="flex items-baseline gap-2 mb-0.5">
                <span className="text-[10px] font-bold tracking-wider uppercase" style={{ color }}>
                  {entry.speaker}
                </span>
                {intentType === 'query' && (
                  <span className="px-1.5 py-0.5 text-[8px] font-bold bg-clinical-info/20 text-clinical-info border border-clinical-info/30 rounded uppercase">
                    Query Detected
                  </span>
                )}
                {intentType === 'clinical' && (
                  <span className="px-1.5 py-0.5 text-[8px] font-bold bg-clinical-warning/20 text-clinical-warning border border-clinical-warning/30 rounded uppercase">
                    Clinical Intent
                  </span>
                )}
              </div>
              <p className={`text-xs leading-relaxed ${
                intentType === 'query'
                  ? 'text-clinical-info bg-clinical-info/5 px-2 py-1 rounded border-l-2 border-clinical-info/40'
                  : intentType === 'clinical'
                  ? 'text-clinical-warning bg-clinical-warning/5 px-2 py-1 rounded border-l-2 border-clinical-warning/40'
                  : 'text-clinical-text/90'
              }`}>
                {text}
              </p>
            </div>
          )
        })}

        {/* Partial transcript (live mic interim results) */}
        {partialTranscript && (
          <div className="animate-fade-in opacity-60">
            <div className="flex items-baseline gap-2 mb-0.5">
              <span className="text-[10px] font-bold tracking-wider uppercase text-amber-400">
                Live Speaker
              </span>
              <span className="mic-listening-dot"></span>
            </div>
            <p className="text-xs leading-relaxed text-clinical-text/50 italic">
              {partialTranscript}
            </p>
          </div>
        )}

        {/* Processing indicator inline */}
        {isProcessing && (
          <div className="animate-fade-in flex items-center gap-2 py-2">
            <span className="processing-spinner"></span>
            <span className="text-[10px] text-clinical-info">AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Action Items */}
      {actionItems.length > 0 && (
        <div className="flex-shrink-0 border-t border-clinical-border p-2">
          <h3 className="text-[9px] font-bold text-clinical-text-muted tracking-wider uppercase mb-1">
            Action Items
          </h3>
          <div className="space-y-0.5">
            {actionItems.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-[10px]">
                <span className={`w-1.5 h-1.5 rounded-full ${
                  item.priority === 'stat' ? 'bg-clinical-critical' :
                  item.priority === 'urgent' ? 'bg-clinical-warning' :
                  'bg-clinical-info'
                }`}></span>
                <span className="text-clinical-text/80">{item.action}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Query Input — always visible */}
      <form onSubmit={handleQuerySubmit} className="flex-shrink-0 border-t border-clinical-border p-2 bg-[#0d1321]">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Ask about this patient..."
            className="query-input"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={!queryText.trim() || isProcessing}
            className="query-submit-btn"
          >
            {isProcessing ? '...' : 'Ask'}
          </button>
        </div>
      </form>
    </div>
  )
}
