export default function Sparkline({ data, width = 120, height = 32, color = '#3b82f6', showDots = true }) {
  if (!data || data.length < 2) return null

  const min = Math.min(...data) * 0.9
  const max = Math.max(...data) * 1.1
  const range = max - min || 1

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * width
    const y = height - ((val - min) / range) * height
    return { x, y, val }
  })

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')

  return (
    <svg width={width} height={height} className="sparkline-container">
      {/* Line */}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Dots */}
      {showDots && points.map((p, i) => (
        <circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={i === points.length - 1 ? 3 : 1.5}
          fill={i === points.length - 1 ? color : 'transparent'}
          stroke={color}
          strokeWidth="1"
        />
      ))}
      {/* Last value highlight */}
      {points.length > 0 && (
        <circle
          cx={points[points.length - 1].x}
          cy={points[points.length - 1].y}
          r="4"
          fill="transparent"
          stroke={color}
          strokeWidth="1"
          opacity="0.5"
        />
      )}
    </svg>
  )
}
