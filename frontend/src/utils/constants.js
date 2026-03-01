// Lab reference ranges and display config
export const LAB_CONFIG = {
  hemoglobin: { label: 'Hgb', unit: 'g/dL', low: 13.5, high: 17.5, critLow: 7, critHigh: 20 },
  hematocrit: { label: 'Hct', unit: '%', low: 38.3, high: 48.6, critLow: 25, critHigh: 60 },
  platelets: { label: 'Plt', unit: 'K/uL', low: 150, high: 400, critLow: 50, critHigh: 1000 },
  wbc: { label: 'WBC', unit: 'K/uL', low: 4.5, high: 11.0, critLow: 2, critHigh: 30 },
  bun: { label: 'BUN', unit: 'mg/dL', low: 7, high: 20, critLow: 0, critHigh: 100 },
  creatinine: { label: 'Cr', unit: 'mg/dL', low: 0.7, high: 1.3, critLow: 0, critHigh: 10 },
  lactate: { label: 'Lactate', unit: 'mmol/L', low: 0.5, high: 2.0, critLow: 0, critHigh: 10 },
  aptt: { label: 'aPTT', unit: 'sec', low: 25, high: 35, critLow: 0, critHigh: 150 },
  d_dimer: { label: 'D-dimer', unit: 'ug/mL', low: 0, high: 0.5, critLow: 0, critHigh: 20 },
  troponin: { label: 'Troponin', unit: 'ng/mL', low: 0, high: 0.04, critLow: 0, critHigh: 10 },
}

export const VITAL_CONFIG = {
  bp_systolic: { label: 'SBP', unit: 'mmHg', low: 90, high: 140, color: '#ef4444' },
  bp_diastolic: { label: 'DBP', unit: 'mmHg', low: 60, high: 90, color: '#f97316' },
  heart_rate: { label: 'HR', unit: 'bpm', low: 60, high: 100, color: '#22c55e' },
  resp_rate: { label: 'RR', unit: '/min', low: 12, high: 20, color: '#3b82f6' },
  spo2: { label: 'SpO2', unit: '%', low: 95, high: 100, color: '#a855f7' },
  temp: { label: 'Temp', unit: '°C', low: 36.5, high: 37.5, color: '#f59e0b' },
}

export function getLabColor(value, config) {
  if (!config) return '#94a3b8'
  if (value <= config.critLow || value >= config.critHigh) return '#ef4444'
  if (value < config.low || value > config.high) return '#f59e0b'
  return '#22c55e'
}

export function getTrendArrow(current, previous) {
  if (!previous) return ''
  const diff = current - previous
  const pctChange = Math.abs(diff / previous) * 100
  if (pctChange < 3) return ''
  if (diff > 0) return pctChange > 20 ? '↑↑' : '↑'
  return pctChange > 20 ? '↓↓' : '↓'
}
