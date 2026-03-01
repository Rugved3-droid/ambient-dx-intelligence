export default function PatientBanner({ patient }) {
  if (!patient) return null
  const d = patient.demographics
  const allergies = patient.allergies || []

  return (
    <div className="flex-shrink-0 bg-[#0d1321] border-b border-clinical-border px-4 py-2">
      <div className="flex items-center justify-between">
        {/* Left: Patient info */}
        <div className="flex items-center gap-6">
          <div>
            <span className="text-base font-bold text-clinical-text">{d.name}</span>
            <span className="text-clinical-text-muted ml-3 text-sm">
              {d.age}yo {d.sex} | MRN: {d.mrn}
            </span>
          </div>
          <div className="text-sm text-clinical-text-muted">
            <span className="text-clinical-info">Room {d.room}{d.bed}</span>
            <span className="mx-2">|</span>
            <span>Admitted {d.admission_date}</span>
            <span className="mx-2">|</span>
            <span>{d.attending}</span>
          </div>
        </div>

        {/* Right: Code status + allergies */}
        <div className="flex items-center gap-3">
          <span className="px-2 py-0.5 text-xs font-bold bg-clinical-info/20 text-clinical-info border border-clinical-info/30 rounded">
            {d.code_status}
          </span>
          {allergies.map((a, i) => (
            <span
              key={i}
              className={`px-2 py-0.5 text-xs font-bold rounded ${
                a.severity?.includes('Life-threatening')
                  ? 'bg-clinical-critical/20 text-clinical-critical border border-clinical-critical/30 animate-pulse'
                  : 'bg-clinical-warning/20 text-clinical-warning border border-clinical-warning/30'
              }`}
              title={a.reaction}
            >
              ALLERGY: {a.allergen}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
