import React from 'react';

interface Props {
  score: number;
  status: string;
  size?: number;
  strokeWidth?: number;
}

export const ScoreRing: React.FC<Props> = ({ score, status, size = 140, strokeWidth = 10 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getColor = () => {
    if (score < 60) return {
      stroke: '#f59e0b',
      glow: 'rgba(245, 158, 11, 0.25)',
      text: 'text-amber-400',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30 glow-border-amber'
    };
    if (score < 80) return {
      stroke: '#6366f1',
      glow: 'rgba(99, 102, 241, 0.25)',
      text: 'text-indigo-400',
      badge: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 glow-border-indigo'
    };
    return {
      stroke: '#10b981',
      glow: 'rgba(16, 185, 129, 0.25)',
      text: 'text-emerald-400',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 glow-border-emerald'
    };
  };

  const colors = getColor();

  return (
    <div className="flex flex-col items-center justify-center relative group">
      {/* Ambient Radial Glow Backdrop */}
      <div
        className="absolute rounded-full filter blur-xl transition-all duration-500 pointer-events-none"
        style={{
          width: size * 1.2,
          height: size * 1.2,
          backgroundColor: colors.glow
        }}
      />

      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        {/* Outer Orbital Particle Ring */}
        <svg
          width={size * 1.15}
          height={size * 1.15}
          className="absolute transform animate-spin-slow pointer-events-none opacity-40"
        >
          <circle
            cx={(size * 1.15) / 2}
            cy={(size * 1.15) / 2}
            r={(size * 1.15) / 2 - 2}
            stroke="url(#ring-grad)"
            strokeWidth="1"
            strokeDasharray="4 8"
            fill="transparent"
          />
          <defs>
            <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={colors.stroke} stopOpacity="0.8" />
              <stop offset="100%" stopColor="#a855f7" stopOpacity="0.2" />
            </linearGradient>
          </defs>
        </svg>

        {/* Main Gauge SVG */}
        <svg width={size} height={size} className="transform -rotate-90 drop-shadow-md">
          {/* Background Track Ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.07)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Active Progress Arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out filter drop-shadow-lg"
            style={{
              filter: `drop-shadow(0px 0px 6px ${colors.stroke})`
            }}
          />
        </svg>

        {/* Center Content */}
        <div className="absolute flex flex-col items-center justify-center z-10">
          <span className={`text-3xl sm:text-4xl font-black font-mono tracking-tight ${colors.text} drop-shadow-sm`}>
            {score.toFixed(1)}%
          </span>
          <span className="text-[9px] sm:text-[10px] text-slate-400 font-bold tracking-widest uppercase mt-0.5">
            READINESS SCORE
          </span>
        </div>
      </div>

      <span className={`mt-4 px-3.5 py-1 text-xs font-bold rounded-full border transition-all shadow-lg ${colors.badge}`}>
        {status}
      </span>
    </div>
  );
};
