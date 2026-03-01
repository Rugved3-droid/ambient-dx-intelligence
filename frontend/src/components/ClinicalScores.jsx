function ScoreCard({ score }) {
  return (
    <div className="bg-clinical-surface rounded-lg border border-clinical-border p-4 animate-slide-in">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-clinical-text">{score.score_name}</h3>
        <span className={`text-lg font-bold ${
          score.interpretation?.toLowerCase().includes('high')
            ? 'text-clinical-critical'
            : score.interpretation?.toLowerCase().includes('moderate')
            ? 'text-clinical-warning'
            : 'text-clinical-normal'
        }`}>
          {score.calculated_value}
        </span>
      </div>

      <p className="text-xs text-clinical-text/70 mb-3 bg-clinical-bg/50 rounded p-2">
        {score.interpretation}
      </p>

      {/* Components table */}
      {score.components?.length > 0 && (
        <div className="border border-clinical-border rounded overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-clinical-bg/50">
                <th className="text-left px-2 py-1.5 text-clinical-text-muted font-medium">Criterion</th>
                <th className="text-center px-2 py-1.5 text-clinical-text-muted font-medium">Value</th>
                <th className="text-center px-2 py-1.5 text-clinical-text-muted font-medium w-16">Points</th>
                <th className="text-right px-2 py-1.5 text-clinical-text-muted font-medium">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-clinical-border">
              {score.components.map((comp, i) => {
                const points = parseFloat(comp.points) || 0
                return (
                  <tr key={i} className="hover:bg-white/5">
                    <td className="px-2 py-1.5 text-clinical-text/80">{comp.criterion}</td>
                    <td className="px-2 py-1.5 text-center text-clinical-text/80">{comp.value}</td>
                    <td className="px-2 py-1.5 text-center">
                      <span className={`font-bold ${
                        points > 0 ? 'text-clinical-warning' : 'text-clinical-text-muted'
                      }`}>
                        {comp.points}
                      </span>
                    </td>
                    <td className="px-2 py-1.5 text-right">
                      <span className="source-badge">{comp.source}</span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function ClinicalScores({ diagnostic }) {
  const scores = diagnostic?.clinical_scores || []

  if (scores.length === 0) {
    return (
      <div className="text-center text-clinical-text-muted text-sm py-12">
        <div className="text-2xl mb-2">📊</div>
        <p>Clinical scores will appear here</p>
        <p className="text-xs mt-1">Scores are calculated during diagnostic reasoning</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 animate-fade-in">
      <h3 className="text-[10px] font-bold text-clinical-text-muted tracking-wider uppercase">
        Calculated Clinical Scores
      </h3>
      {scores.map((score, i) => (
        <ScoreCard key={i} score={score} />
      ))}
    </div>
  )
}
