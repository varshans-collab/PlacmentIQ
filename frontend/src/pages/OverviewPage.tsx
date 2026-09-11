import React from 'react';
import { Target, Sparkles, Users, Plane, ArrowRight } from 'lucide-react';
import { DataProvenanceBadge } from '../components/DataProvenanceBadge';

interface Props {
  setActiveTab: (tab: string) => void;
  setSelectedPersona: (persona: string) => void;
}

export const OverviewPage: React.FC<Props> = ({ setActiveTab, setSelectedPersona }) => {
  return (
    <div className="space-y-10 animate-fadeIn max-w-5xl mx-auto py-4">
      {/* Hero Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-indigo-950 via-navy-900 to-purple-950 p-8 sm:p-12 border border-indigo-500/20 shadow-2xl overflow-hidden text-center space-y-6">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
        
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-bold uppercase tracking-wider mx-auto">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span>AI Placement Intelligence & Intervention Simulator</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-tight">
          PLACEMENT<span className="text-indigo-400">IQ</span>
        </h1>

        <p className="text-xl sm:text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-200 to-pink-300 max-w-3xl mx-auto">
          Predict readiness. Explain the gaps. Simulate interventions. Improve placement outcomes.
        </p>

        <p className="text-slate-300 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
          Select a role workspace below to enter either individual student employability profiling & What-If simulation, or institutional officer cohort analytics & placement drive simulation.
        </p>

        {/* Primary Role Action Buttons */}
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4 max-w-xl mx-auto">
          <button
            onClick={() => {
              setSelectedPersona('ST_DEMO_001');
              setActiveTab('student');
            }}
            className="w-full sm:w-auto flex-1 flex items-center justify-center space-x-2.5 px-6 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-bold text-sm shadow-xl shadow-indigo-600/30 transition-all hover:scale-105"
          >
            <Sparkles className="w-5 h-5" />
            <span>Student Portal</span>
          </button>
          
          <button
            onClick={() => setActiveTab('tpo')}
            className="w-full sm:w-auto flex-1 flex items-center justify-center space-x-2.5 px-6 py-4 rounded-2xl bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white font-bold text-sm shadow-xl shadow-purple-600/30 transition-all hover:scale-105"
          >
            <Users className="w-5 h-5" />
            <span>RPO / TPO Command Center</span>
          </button>
        </div>

        {/* Secondary Action */}
        <div className="pt-2">
          <button
            onClick={() => setActiveTab('simulator')}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-700/80 text-xs font-semibold transition-all hover:scale-105"
          >
            <Plane className="w-4 h-4 text-purple-400" />
            <span>Launch Placement Flight Simulator →</span>
          </button>
        </div>
      </div>

      {/* Two Workspace Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Student Workspace Card */}
        <div
          onClick={() => {
            setSelectedPersona('ST_DEMO_001');
            setActiveTab('student');
          }}
          className="glass-card glass-card-hover p-8 rounded-3xl cursor-pointer space-y-4 border-l-4 border-l-indigo-500 flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Sparkles className="w-6 h-6" />
              </div>
              <DataProvenanceBadge type="SYNTHETIC" />
            </div>
            <h3 className="text-xl font-bold text-white">Student Workspace</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Personal employability digital twin, real SHAP XAI attributions, role-specific Why Not Yet? gaps, personalized roadmap, and interactive What-If skill simulator.
            </p>
          </div>
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-indigo-400 font-bold">
            <span>Enter Student Workspace</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>

        {/* RPO / TPO Workspace Card */}
        <div
          onClick={() => setActiveTab('tpo')}
          className="glass-card glass-card-hover p-8 rounded-3xl cursor-pointer space-y-4 border-l-4 border-l-purple-500 flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <Users className="w-6 h-6" />
              </div>
              <DataProvenanceBadge type="DERIVED" />
            </div>
            <h3 className="text-xl font-bold text-white">RPO / TPO Command Center</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Institutional batch analytics, department risk comparison, skill heatmap, officer student search, placement drive funnels, and +10 selection optimizer.
            </p>
          </div>
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-purple-400 font-bold">
            <span>Enter RPO / TPO Command Center</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
};
