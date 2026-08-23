import type { ExerciseConfig } from '../types'

interface Props {
  name: string
  config: ExerciseConfig
  onClose: () => void
  onStart: () => void
}

export default function ExerciseDetailModal({ name, config, onClose, onStart }: Props) {
  const rules = config.alignment?.coaching_rules
    ? Object.values(config.alignment.coaching_rules)
    : [
        'Position yourself in clear view of the webcam.',
        'Align your posture with the semi-transparent Ghost Skeleton.',
        'Hold starting posture until calibration reaches 100%.',
      ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="glass-strong rounded-2xl w-full max-w-lg p-6 sm:p-8 space-y-6 relative overflow-hidden animate-fade-up border border-white/12 shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
      >
        {/* Background cyan glow */}
        <div
          className="absolute -top-20 -right-20 w-56 h-56 rounded-full opacity-20 pointer-events-none"
          style={{ background: 'radial-gradient(circle, #00d4ff 0%, transparent 70%)' }}
        />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-colors"
        >
          ✕
        </button>

        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-[10px] px-2.5 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase tracking-widest">
              {config.category || 'WORKOUT'}
            </span>
            <span className="font-mono text-[10px] px-2.5 py-0.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase tracking-widest">
              {config.type || 'REP_BASED'}
            </span>
          </div>
          <h2 className="font-black text-2xl sm:text-3xl text-white/95 tracking-tight">
            {name}
          </h2>
          <div className="text-xs font-mono text-white/40 mt-1">
            Primary Joint Target: <span className="text-cyan-400 capitalize">{config.primary_joint}</span>
          </div>
        </div>

        {/* Meta badges */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/4 rounded-xl p-3 border border-white/8 text-center">
            <div className="font-mono font-bold text-sm text-cyan-400">{config.target_reps} REPS</div>
            <div className="font-mono text-[9px] text-white/35 uppercase tracking-wider mt-0.5">Target Goal</div>
          </div>
          <div className="bg-white/4 rounded-xl p-3 border border-white/8 text-center">
            <div className="font-mono font-bold text-sm text-purple-400">{config.cooldown}s</div>
            <div className="font-mono text-[9px] text-white/35 uppercase tracking-wider mt-0.5">Rep Cooldown</div>
          </div>
          <div className="bg-white/4 rounded-xl p-3 border border-white/8 text-center">
            <div className="font-mono font-bold text-sm text-emerald-400">~10 kcal</div>
            <div className="font-mono text-[9px] text-white/35 uppercase tracking-wider mt-0.5">Est. Burn/min</div>
          </div>
        </div>

        {/* Posture Instructions */}
        <div className="bg-white/3 rounded-xl p-4 border border-white/6 space-y-3">
          <div className="font-mono text-xs font-bold text-white/80 uppercase tracking-wider flex items-center gap-1.5">
            <span className="text-cyan-400">◈</span> Posture Calibration Rules
          </div>
          <ul className="space-y-2 text-xs text-white/60">
            {rules.map((rule, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="font-mono text-cyan-400/80 font-bold">{idx + 1}.</span>
                <span>{rule}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Action Button */}
        <button
          onClick={onStart}
          className="select-btn w-full py-4 rounded-xl font-black text-sm tracking-wider uppercase text-black bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-300 hover:to-purple-400 transition-all shadow-[0_0_30px_rgba(0,212,255,0.3)] flex items-center justify-center gap-2"
        >
          <span>▶</span> START WORKOUT & CALIBRATION
        </button>
      </div>
    </div>
  )
}
