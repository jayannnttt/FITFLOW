import type { Screen } from '../types'

interface Props {
  currentScreen: Screen
  onNavigate: (screen: 'home' | 'history') => void
  wsConnected?: boolean
}

export default function TopNavBar({ currentScreen, onNavigate, wsConnected }: Props) {
  return (
    <header className="glass-strong border-b border-white/8 px-5 md:px-8 py-3.5 flex items-center justify-between flex-shrink-0 relative z-30">
      {/* Brand Logo */}
      <button
        onClick={() => onNavigate('home')}
        className="flex items-center gap-3 text-left group transition-transform active:scale-98"
      >
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-600 p-0.5 flex items-center justify-center glow-cyan">
          <div className="w-full h-full bg-black/90 rounded-[10px] flex items-center justify-center font-black text-cyan-400 text-sm tracking-tighter">
            ⚡
          </div>
        </div>
        <div>
          <div className="font-black text-sm tracking-tight text-white/95 flex items-center gap-1.5">
            AI FITNESS COACH
            <span className="font-mono text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase tracking-widest font-normal">
              v2.0
            </span>
          </div>
          <div className="font-mono text-[10px] text-white/35 tracking-wider uppercase">
            Computer Vision Pose Engine
          </div>
        </div>
      </button>

      {/* Navigation & Status */}
      <div className="flex items-center gap-4">
        {/* Connection status indicator if provided */}
        {wsConnected !== undefined && (
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-white/4 border border-white/8 text-xs font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                wsConnected ? 'bg-emerald-400 animate-pulse glow-cyan' : 'bg-rose-500'
              }`}
            />
            <span className="text-white/40 text-[11px]">
              {wsConnected ? 'WEBSOCKET ONLINE' : 'OFFLINE'}
            </span>
          </div>
        )}

        <nav className="flex items-center gap-1 bg-white/4 p-1 rounded-xl border border-white/8">
          <button
            onClick={() => onNavigate('home')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
              currentScreen === 'home'
                ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(0,212,255,0.15)]'
                : 'text-white/50 hover:text-white/80 hover:bg-white/5'
            }`}
          >
            Home
          </button>
          <button
            onClick={() => onNavigate('history')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
              currentScreen === 'history'
                ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(0,212,255,0.15)]'
                : 'text-white/50 hover:text-white/80 hover:bg-white/5'
            }`}
          >
            History
          </button>
        </nav>
      </div>
    </header>
  )
}
