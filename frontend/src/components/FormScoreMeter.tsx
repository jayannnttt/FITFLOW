interface Props {
  score: number
  size?: number
}

export default function FormScoreMeter({ score, size = 120 }: Props) {
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const normalizedScore = Math.min(100, Math.max(0, score))
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference

  const color =
    score >= 80 ? '#10B981' : score >= 60 ? '#F59E0B' : '#EF4444'

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* Track circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth={strokeWidth}
        />
        {/* Value arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.4s ease, stroke 0.4s ease' }}
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="font-mono font-black text-2xl tracking-tighter" style={{ color }}>
          {Math.round(score)}%
        </span>
        <span className="font-mono text-[9px] text-white/40 tracking-widest uppercase">
          Form Score
        </span>
      </div>
    </div>
  )
}
