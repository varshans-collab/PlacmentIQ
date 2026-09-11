import React from 'react';

export type OrbState = 'IDLE' | 'LISTENING' | 'THINKING' | 'RESPONDING' | 'SIMULATING';

interface Props {
  state?: OrbState;
  size?: number;
  onClick?: () => void;
  interactive?: boolean;
}

export const AiOrb: React.FC<Props> = ({
  state = 'IDLE',
  size = 120,
  onClick,
  interactive = true
}) => {
  const getStateConfig = () => {
    switch (state) {
      case 'LISTENING':
        return {
          glowColor: 'rgba(56, 189, 248, 0.4)',
          coreGradient: 'from-sky-400 via-indigo-500 to-cyan-400',
          ringColor: 'stroke-sky-400',
          pulseSpeed: 'animate-ping',
          statusText: 'LISTENING...',
          textColor: 'text-sky-400'
        };
      case 'THINKING':
        return {
          glowColor: 'rgba(168, 85, 247, 0.4)',
          coreGradient: 'from-purple-500 via-pink-500 to-indigo-600',
          ringColor: 'stroke-purple-400',
          pulseSpeed: 'animate-spin-slow',
          statusText: 'ANALYZING...',
          textColor: 'text-purple-400'
        };
      case 'RESPONDING':
        return {
          glowColor: 'rgba(16, 185, 129, 0.4)',
          coreGradient: 'from-emerald-400 via-teal-500 to-cyan-500',
          ringColor: 'stroke-emerald-400',
          pulseSpeed: 'animate-pulse',
          statusText: 'SPEAKING...',
          textColor: 'text-emerald-400'
        };
      case 'SIMULATING':
        return {
          glowColor: 'rgba(245, 158, 11, 0.4)',
          coreGradient: 'from-amber-400 via-orange-500 to-rose-500',
          ringColor: 'stroke-amber-400',
          pulseSpeed: 'animate-reverse-spin',
          statusText: 'SIMULATING...',
          textColor: 'text-amber-400'
        };
      case 'IDLE':
      default:
        return {
          glowColor: 'rgba(99, 102, 241, 0.25)',
          coreGradient: 'from-indigo-500 via-purple-600 to-pink-500',
          ringColor: 'stroke-indigo-400',
          pulseSpeed: 'animate-spin-slow',
          statusText: 'COPILOT READY',
          textColor: 'text-indigo-300'
        };
    }
  };

  const config = getStateConfig();

  return (
    <div
      onClick={onClick}
      className={`relative flex flex-col items-center justify-center select-none ${
        interactive ? 'cursor-pointer group' : ''
      }`}
      style={{ width: size, height: size }}
    >
      {/* Background Ambient Radial Glow */}
      <div
        className="absolute rounded-full filter blur-2xl transition-all duration-700 pointer-events-none"
        style={{
          width: size * 1.3,
          height: size * 1.3,
          backgroundColor: config.glowColor
        }}
      />

      {/* Outer Rotating Orbital Ring 1 */}
      <svg
        width={size}
        height={size}
        className="absolute transform animate-spin-slow pointer-events-none opacity-60"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size / 2 - 4}
          className={`${config.ringColor} transition-colors duration-500`}
          strokeWidth="1.5"
          strokeDasharray="6 12"
          fill="transparent"
        />
      </svg>

      {/* Counter-Rotating Orbital Ring 2 */}
      <svg
        width={size * 0.85}
        height={size * 0.85}
        className="absolute transform animate-reverse-spin pointer-events-none opacity-40"
      >
        <circle
          cx={(size * 0.85) / 2}
          cy={(size * 0.85) / 2}
          r={(size * 0.85) / 2 - 2}
          stroke="url(#orb-grad-2)"
          strokeWidth="1"
          strokeDasharray="4 8"
          fill="transparent"
        />
        <defs>
          <linearGradient id="orb-grad-2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#818cf8" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#c084fc" stopOpacity="0.2" />
          </linearGradient>
        </defs>
      </svg>

      {/* Central 3D Glowing Core Sphere */}
      <div
        className={`rounded-full bg-gradient-to-tr ${config.coreGradient} shadow-2xl transition-all duration-500 flex items-center justify-center group-hover:scale-105`}
        style={{
          width: size * 0.55,
          height: size * 0.55,
          boxShadow: `0 0 35px ${config.glowColor}, inset 0 2px 4px rgba(255, 255, 255, 0.4)`
        }}
      >
        {/* Inner Core Pulse Dot */}
        <div
          className={`w-3 h-3 rounded-full bg-white opacity-90 shadow-md ${
            state !== 'IDLE' ? 'animate-ping' : 'animate-pulse'
          }`}
        />
      </div>

      {/* State Label */}
      <span className={`mt-2 text-[9px] font-mono font-bold tracking-widest uppercase ${config.textColor} transition-colors duration-300`}>
        {config.statusText}
      </span>
    </div>
  );
};
