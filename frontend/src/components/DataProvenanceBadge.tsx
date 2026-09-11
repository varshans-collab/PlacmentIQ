import React from 'react';
import { DataProvenanceType } from '../types';
import { Database, Cpu, Calculator, Sparkles } from 'lucide-react';

interface Props {
  type: DataProvenanceType;
  size?: 'sm' | 'md';
}

export const DataProvenanceBadge: React.FC<Props> = ({ type, size = 'sm' }) => {
  const styles = {
    OBSERVED: {
      bg: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/30',
      icon: Database,
      label: 'OBSERVED',
      tooltip: 'Real public benchmark source (AMEO 2015)'
    },
    SYNTHETIC: {
      bg: 'bg-indigo-950/80 text-indigo-300 border-indigo-500/30',
      icon: Cpu,
      label: 'SYNTHETIC',
      tooltip: 'Computer-generated institutional prototype data'
    },
    DERIVED: {
      bg: 'bg-amber-950/80 text-amber-300 border-amber-500/30',
      icon: Calculator,
      label: 'DERIVED',
      tooltip: 'Calculated indicator / gap analysis'
    },
    SIMULATED: {
      bg: 'bg-purple-950/80 text-purple-300 border-purple-500/30',
      icon: Sparkles,
      label: 'SIMULATED',
      tooltip: 'Counterfactual scenario / model projection'
    }
  }[type];

  const Icon = styles.icon;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono font-semibold tracking-wider uppercase rounded-full border ${styles.bg} ${sizeClasses}`}
      title={styles.tooltip}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>[{styles.label}]</span>
    </span>
  );
};
