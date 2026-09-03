import type { Screen } from '../types'

interface Props {
  currentScreen: Screen
  onNavigate: (screen: 'home' | 'history') => void
  wsConnected?: boolean
}

export default function TopNavBar({ currentScreen, onNavigate }: Props) {
  return (
    <header
      className="px-6 md:px-8 py-3.5 flex items-center justify-between flex-shrink-0 relative z-30"
      style={{
        background: 'var(--card)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      {/* Brand Lockup */}
      <button
        onClick={() => onNavigate('home')}
        className="flex flex-col text-left cursor-pointer transition-opacity hover:opacity-85"
      >
        <span className="font-bold text-[16px] text-white tracking-tight leading-tight">
          FITFLOW
        </span>
        <span
          className="text-[11px] uppercase tracking-wider leading-none"
          style={{ color: 'var(--muted-foreground)' }}
        >
          COACH
        </span>
      </button>

      {/* Navigation Links */}
      <nav className="flex items-center gap-6">
        <button
          onClick={() => onNavigate('home')}
          className={`text-[13px] font-medium transition-colors cursor-pointer py-1 ${
            currentScreen === 'home'
              ? 'active'
              : 'hover:text-white'
          }`}
          style={{
            color: currentScreen === 'home' ? 'var(--primary)' : 'var(--secondary-foreground)',
            borderBottom: currentScreen === 'home' ? '2px solid var(--primary)' : '2px solid transparent',
          }}
        >
          Home
        </button>
        <button
          onClick={() => onNavigate('history')}
          className={`text-[13px] font-medium transition-colors cursor-pointer py-1 ${
            currentScreen === 'history'
              ? 'active'
              : 'hover:text-white'
          }`}
          style={{
            color: currentScreen === 'history' ? 'var(--primary)' : 'var(--secondary-foreground)',
            borderBottom: currentScreen === 'history' ? '2px solid var(--primary)' : '2px solid transparent',
          }}
        >
          History
        </button>
      </nav>
    </header>
  )
}
