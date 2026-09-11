import React, { useEffect, useState } from 'react';
import { runFlightSimulator, compareInterventions } from '../api/client';
import { SimulatorResponse, InterventionResult } from '../types';
import { DataProvenanceBadge } from '../components/DataProvenanceBadge';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';
import {
  Plane, Sliders, AlertTriangle, Sparkles, CheckCircle2, TrendingUp,
  Layers, ArrowRight, Activity, ShieldAlert, Cpu
} from 'lucide-react';

export const PlacementSimulator: React.FC = () => {
  // Flight Simulator Configurations
  const [config, setConfig] = useState({
    target_role: 'Data Analyst',
    department: 'ALL',
    eligibility_cgpa: 7.0,
    eligibility_max_backlogs: 0,
    aptitude_threshold: 6.0,
    technical_threshold: 6.5,
    interview_threshold: 6.5
  });

  const [simData, setSimData] = useState<SimulatorResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Intervention Lab states
  const [selectedInterventions, setSelectedInterventions] = useState<string[]>([
    'SQL Bootcamp', 'Aptitude Training', 'Mock Interviews', 'DSA Intensive'
  ]);
  const [labResults, setLabResults] = useState<InterventionResult[]>([]);
  const [optimizer, setOptimizer] = useState<any>(null);
  const [labLoading, setLabLoading] = useState<boolean>(false);

  useEffect(() => {
    runSim();
  }, [config]);

  const runSim = async () => {
    setLoading(true);
    try {
      const res = await runFlightSimulator(config);
      setSimData(res);
      // Run intervention lab comparison
      loadLab(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadLab = async (currentSimRes?: SimulatorResponse) => {
    setLabLoading(true);
    try {
      const res = await compareInterventions(config, selectedInterventions);
      setLabResults(res.interventions || []);
      setOptimizer(res.plus_10_optimizer || null);
    } catch (err) {
      console.error(err);
    } finally {
      setLabLoading(false);
    }
  };

  const toggleIntervention = (key: string) => {
    setSelectedInterventions(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  if (loading || !simData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm font-medium text-slate-400">Executing Placement Flight Simulation Engine...</span>
        </div>
      </div>
    );
  }

  const catalogKeys = [
    'SQL Bootcamp', 'Aptitude Training', 'Mock Interviews', 'DSA Intensive', 'Cloud & DevOps Workshop', 'Project Program'
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Header */}
      <div className="relative rounded-2xl bg-gradient-to-r from-purple-950 via-indigo-950 to-navy-900 p-8 border border-purple-500/30 shadow-2xl overflow-hidden">
        <div className="max-w-3xl relative z-10 space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-bold uppercase tracking-wider">
            <Plane className="w-4 h-4" />
            <span>FLAGSHIP INSTITUTIONAL DIFFERENTIATOR</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            PLACEMENT FLIGHT SIMULATOR
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            Simulate recruitment drive funnel drop-offs for a 610-student cohort across academic eligibility, aptitude, technical, and interview rounds. Detect bottleneck elimination stages and optimize institutional interventions.
          </p>

          <div className="pt-2 flex items-center space-x-4 text-xs text-purple-300 font-mono">
            <span>Target Role: <strong className="text-white">{simData.target_role}</strong></span>
            <span>•</span>
            <span>Cohort Size: <strong className="text-white">{simData.total_cohort} Students</strong></span>
            <span>•</span>
            <span>Selection Rate: <strong className="text-emerald-400 font-bold">{simData.selection_rate}%</strong></span>
          </div>
        </div>
      </div>

      {/* Control Configuration Sliders */}
      <div className="glass-card p-6 rounded-2xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-purple-400" />
              <span>Drive Simulation Controls & Cutoff Thresholds</span>
            </h2>
            <p className="text-xs text-slate-400">Modify recruitment round criteria to test cohort survival rates</p>
          </div>
          <DataProvenanceBadge type="SIMULATED" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Role */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300">Target Role Benchmark</label>
            <select
              value={config.target_role}
              onChange={(e) => setConfig({ ...config, target_role: e.target.value })}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs font-semibold text-white focus:outline-none"
            >
              <option value="Data Analyst">Data Analyst</option>
              <option value="AI/ML Engineer">AI/ML Engineer</option>
              <option value="Full-Stack Developer">Full-Stack Developer</option>
              <option value="Cloud/DevOps Engineer">Cloud/DevOps Engineer</option>
            </select>
          </div>

          {/* Dept */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300">Department Filter</label>
            <select
              value={config.department}
              onChange={(e) => setConfig({ ...config, department: e.target.value })}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs font-semibold text-white focus:outline-none"
            >
              <option value="ALL">All Departments ({simData?.total_cohort || 610})</option>
              <option value="CSE">CSE</option>
              <option value="ISE">ISE</option>
              <option value="ECE">ECE</option>
              <option value="Mechanical">Mechanical</option>
            </select>
          </div>

          {/* CGPA */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Eligibility CGPA</span>
              <span className="text-purple-400 font-mono">{config.eligibility_cgpa}</span>
            </div>
            <input
              type="range"
              min="5.0"
              max="9.0"
              step="0.25"
              value={config.eligibility_cgpa}
              onChange={(e) => setConfig({ ...config, eligibility_cgpa: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>

          {/* Aptitude */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Aptitude Cutoff</span>
              <span className="text-purple-400 font-mono">{config.aptitude_threshold} / 10</span>
            </div>
            <input
              type="range"
              min="4.0"
              max="8.5"
              step="0.5"
              value={config.aptitude_threshold}
              onChange={(e) => setConfig({ ...config, aptitude_threshold: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>

          {/* Technical */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Technical Round Cutoff</span>
              <span className="text-purple-400 font-mono">{config.technical_threshold} / 10</span>
            </div>
            <input
              type="range"
              min="4.0"
              max="8.5"
              step="0.5"
              value={config.technical_threshold}
              onChange={(e) => setConfig({ ...config, technical_threshold: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>

          {/* Interview */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-300">Interview Cutoff</span>
              <span className="text-purple-400 font-mono">{config.interview_threshold} / 10</span>
            </div>
            <input
              type="range"
              min="4.0"
              max="8.5"
              step="0.5"
              value={config.interview_threshold}
              onChange={(e) => setConfig({ ...config, interview_threshold: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>
        </div>
      </div>

      {/* Placement Funnel & Bottleneck Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Funnel Chart */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">Simulated Recruitment Funnel</h3>
              <p className="text-xs text-slate-400">Student count remaining after each selection stage</p>
            </div>
            <DataProvenanceBadge type="SIMULATED" />
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={simData.stages} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.08)" />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="stage" type="category" stroke="#cbd5e1" width={110} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Bar dataKey="passed" fill="#8b5cf6" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Stage Losses Table */}
          <div className="overflow-x-auto pt-2">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900 text-slate-400 font-mono uppercase border-b border-slate-800">
                <tr>
                  <th className="p-2.5">Stage</th>
                  <th className="p-2.5">Qualifying Count</th>
                  <th className="p-2.5">Students Lost</th>
                  <th className="p-2.5">Loss %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {simData.stages.map((stg, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="p-2.5 font-bold text-white font-sans">{stg.stage}</td>
                    <td className="p-2.5 text-purple-300 font-bold">{stg.passed}</td>
                    <td className="p-2.5 text-rose-400">{stg.lost}</td>
                    <td className="p-2.5 text-amber-400">{stg.loss_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Primary Bottleneck & Pre-Mortem Column */}
        <div className="space-y-6">
          {/* Bottleneck Card */}
          <div className="glass-card p-6 rounded-2xl space-y-4 border-l-4 border-l-rose-500">
            <div className="flex items-center space-x-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
              <AlertTriangle className="w-4 h-4" />
              <span>PRIMARY SELECTION BOTTLENECK</span>
            </div>

            <div>
              <h3 className="text-xl font-black text-white">{simData.primary_bottleneck.stage}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className="px-2.5 py-0.5 text-xs font-mono font-bold bg-rose-500/20 text-rose-300 rounded border border-rose-500/30">
                  {simData.primary_bottleneck.loss_percentage}% Elimination Loss
                </span>
                <span className="text-xs text-slate-400 font-mono">({simData.primary_bottleneck.students_lost} Lost)</span>
              </div>
            </div>

            <p className="text-xs text-slate-300 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
              {simData.primary_bottleneck.recommendation}
            </p>
          </div>

          {/* Placement Pre-Mortem */}
          <div className="glass-card p-6 rounded-2xl space-y-3 border-l-4 border-l-amber-500">
            <h3 className="text-sm font-bold text-amber-300 uppercase tracking-wider flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4" />
              <span>PLACEMENT PRE-MORTEM</span>
            </h3>
            <p className="text-xs text-slate-400 font-semibold italic">“Assume this placement drive failed — why?”</p>
            <ul className="space-y-2 text-xs text-slate-300">
              {simData.pre_mortem.map((item, idx) => (
                <li key={idx} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Intervention Experiment Lab */}
      <div className="glass-card p-6 rounded-2xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span>Intervention Experiment Lab</span>
            </h2>
            <p className="text-xs text-slate-400">Select institutional interventions to run counterfactual cohort simulations</p>
          </div>
          <DataProvenanceBadge type="SIMULATED" />
        </div>

        {/* Catalog Selector Checklist */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {catalogKeys.map(key => {
            const isSelected = selectedInterventions.includes(key);
            return (
              <button
                key={key}
                onClick={() => toggleIntervention(key)}
                className={`p-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                  isSelected
                    ? 'bg-purple-600/30 text-purple-200 border-purple-500/50 shadow-md'
                    : 'bg-slate-900/50 text-slate-400 border-slate-800 hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold">{key}</span>
                  {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />}
                </div>
              </button>
            );
          })}
        </div>

        {/* Results Comparison Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900 text-slate-400 font-mono uppercase border-b border-slate-800">
              <tr>
                <th className="p-3">Intervention Scenario</th>
                <th className="p-3">Affected Students</th>
                <th className="p-3">Baseline Selections</th>
                <th className="p-3">Simulated Selections</th>
                <th className="p-3">Expected Delta</th>
                <th className="p-3">Effort</th>
                <th className="p-3">Priority</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {labResults.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="p-3">
                    <strong className="text-white block">{item.name}</strong>
                    <span className="text-[11px] text-slate-400">{item.description}</span>
                  </td>
                  <td className="p-3 font-mono">{item.affected_students}</td>
                  <td className="p-3 font-mono">{item.baseline_selections}</td>
                  <td className="p-3 font-mono text-purple-300 font-bold">{item.simulated_selections}</td>
                  <td className="p-3 font-mono font-bold text-emerald-400">+{item.delta_selections} Selections</td>
                  <td className="p-3 text-slate-400">{item.effort}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                      item.priority === 'HIGH' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {item.priority}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* "+10 Students" Optimizer Card */}
        {optimizer && (
          <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-indigo-500/30 space-y-4">
            <div className="flex items-center space-x-2 text-indigo-300 text-xs font-bold uppercase tracking-wider">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>“+10 STUDENTS” INTERVENTION OPTIMIZER</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-400 uppercase font-mono">Recommended Single Best Action</span>
                {optimizer.recommended_primary_intervention && (
                  <div>
                    <h4 className="text-sm font-bold text-white">{optimizer.recommended_primary_intervention.name}</h4>
                    <p className="text-xs text-emerald-400 font-mono font-bold mt-1">
                      +{optimizer.recommended_primary_intervention.delta_selections} selections ({optimizer.recommended_primary_intervention.affected_students} students)
                    </p>
                  </div>
                )}
              </div>

              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-400 uppercase font-mono">Recommended Combination Package</span>
                {optimizer.recommended_combination && (
                  <div>
                    <h4 className="text-sm font-bold text-white">{optimizer.recommended_combination.name}</h4>
                    <p className="text-xs text-emerald-400 font-mono font-bold mt-1">
                      +{optimizer.recommended_combination.delta_selections} selections ({optimizer.recommended_combination.effort})
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
