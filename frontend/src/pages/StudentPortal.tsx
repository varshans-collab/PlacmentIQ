import React, { useEffect, useState } from 'react';
import {
  fetchStudentDetail,
  fetchOpportunityCost,
  fetchMinimumImprovement,
  fetchRoadmap,
  runWhatIfSimulation
} from '../api/client';
import {
  StudentDetailResponse,
  WhatIfResponse,
  OpportunityCostItem,
  MinimumImprovementResult
} from '../types';
import { ScoreRing } from '../components/ScoreRing';
import { DataProvenanceBadge } from '../components/DataProvenanceBadge';
import { AiCopilotWidget } from '../components/AiCopilotWidget';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts';
import {
  Sparkles, HelpCircle, Activity, TrendingUp, Sliders, CheckCircle2,
  Clock, Layers, BookOpen, ArrowRight, Target, ShieldCheck, AlertCircle, AlertTriangle
} from 'lucide-react';

interface Props {
  selectedPersona: string;
  setSelectedPersona: (id: string) => void;
}

export const StudentPortal: React.FC<Props> = ({ selectedPersona, setSelectedPersona }) => {
  const [data, setData] = useState<StudentDetailResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSubTab, setActiveSubTab] = useState<string>('digital_twin');

  // Lazy Opportunity Cost State
  const [oppCost, setOppCost] = useState<OpportunityCostItem[] | null>(null);
  const [oppCostLoading, setOppCostLoading] = useState<boolean>(false);
  const [oppCostError, setOppCostError] = useState<string | null>(null);

  // Lazy Minimum Improvement State
  const [minImp, setMinImp] = useState<MinimumImprovementResult | null>(null);
  const [minImpLoading, setMinImpLoading] = useState<boolean>(false);
  const [minImpError, setMinImpError] = useState<string | null>(null);

  // Lazy Roadmap State
  const [roadmap, setRoadmap] = useState<any | null>(null);
  const [roadmapLoading, setRoadmapLoading] = useState<boolean>(false);
  const [roadmapError, setRoadmapError] = useState<string | null>(null);

  // What-If Slider States
  const [whatIfSliders, setWhatIfSliders] = useState<Record<string, number>>({});
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null);
  const [whatIfLoading, setWhatIfLoading] = useState<boolean>(false);

  useEffect(() => {
    loadStudentData(selectedPersona);
  }, [selectedPersona]);

  useEffect(() => {
    if (activeSubTab === 'opportunity_cost' && !oppCost && !oppCostLoading) {
      loadOpportunityCostData(selectedPersona);
    } else if (activeSubTab === 'minimum_imp' && !minImp && !minImpLoading) {
      loadMinimumImprovementData(selectedPersona);
    } else if (activeSubTab === 'roadmap' && !roadmap && !roadmapLoading) {
      loadRoadmapData(selectedPersona, data?.student.target_role);
    }
  }, [activeSubTab, selectedPersona]);

  const loadStudentData = async (id: string) => {
    setLoading(true);
    setError(null);
    setOppCost(null);
    setOppCostError(null);
    setMinImp(null);
    setMinImpError(null);
    setRoadmap(null);
    setRoadmapError(null);
    try {
      const res = await fetchStudentDetail(id);
      setData(res);
      // Initialize sliders with student current values
      setWhatIfSliders({
        sql_score: res.student.sql_score,
        python_score: res.student.python_score,
        dsa_score: res.student.dsa_score,
        quantitative_aptitude: res.student.quantitative_aptitude,
        communication_score: res.student.communication_score,
        project_count: res.student.project_count,
        internships: res.student.internships
      });
      setWhatIfResult(null);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to load student details');
    } finally {
      setLoading(false);
    }
  };

  const loadOpportunityCostData = async (id: string) => {
    setOppCostLoading(true);
    setOppCostError(null);
    try {
      const res = await fetchOpportunityCost(id);
      setOppCost(res.matrix || []);
    } catch (err: any) {
      console.error(err);
      setOppCostError(err.message || 'Failed to calculate opportunity cost matrix');
    } finally {
      setOppCostLoading(false);
    }
  };

  const loadMinimumImprovementData = async (id: string) => {
    setMinImpLoading(true);
    setMinImpError(null);
    try {
      const res = await fetchMinimumImprovement(id);
      setMinImp(res.result || null);
    } catch (err: any) {
      console.error(err);
      setMinImpError(err.message || 'Failed to calculate minimum improvement');
    } finally {
      setMinImpLoading(false);
    }
  };

  const loadRoadmapData = async (id: string, role?: string) => {
    setRoadmapLoading(true);
    setRoadmapError(null);
    try {
      const res = await fetchRoadmap(id, role);
      setRoadmap(res);
    } catch (err: any) {
      console.error(err);
      setRoadmapError(err.message || 'Failed to generate personalized roadmap');
    } finally {
      setRoadmapLoading(false);
    }
  };

  const handleSliderChange = (feature: string, val: number) => {
    setWhatIfSliders(prev => ({ ...prev, [feature]: val }));
  };

  const handleRunWhatIf = async () => {
    if (!data) return;
    setWhatIfLoading(true);
    try {
      const res = await runWhatIfSimulation(selectedPersona, whatIfSliders, data.student.target_role);
      setWhatIfResult(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setWhatIfLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <div className="text-center space-y-1">
          <p className="text-sm font-bold text-white">Loading Student Twin Diagnostic...</p>
          <p className="text-xs text-slate-400">Executing Random Forest model inference & SHAP XAI calculations</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 rounded-2xl glass-card border-rose-500/30 text-center max-w-md mx-auto space-y-4">
        <HelpCircle className="w-12 h-12 text-rose-400 mx-auto" />
        <div>
          <h3 className="text-lg font-bold text-white">Student Data Error</h3>
          <p className="text-xs text-slate-300 mt-1">{error || 'Unable to load student profile'}</p>
        </div>
        <button
          onClick={() => loadStudentData(selectedPersona)}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md"
        >
          Retry Loading Student Data
        </button>
      </div>
    );
  }

  const { student, prediction, why_not_yet, trajectory } = data;
  const currentScore = whatIfResult ? whatIfResult.projected_score : prediction.readiness_score;
  const currentStatus = whatIfResult ? whatIfResult.projected_status : prediction.status;

  // Radar Chart Data Preparation
  const radarData = [
    { skill: 'Python', Student: student.python_score, Benchmark: 8.0, Top10: 9.0 },
    { skill: 'SQL', Student: student.sql_score, Benchmark: 8.0, Top10: 9.0 },
    { skill: 'DSA', Student: student.dsa_score, Benchmark: 8.0, Top10: 9.0 },
    { skill: 'Aptitude', Student: student.quantitative_aptitude, Benchmark: 7.5, Top10: 8.5 },
    { skill: 'Comm', Student: student.communication_score, Benchmark: 7.5, Top10: 8.5 },
    { skill: 'Projects', Student: student.project_count * 2, Benchmark: 8.0, Top10: 10.0 }
  ];

  const subTabs = [
    { id: 'digital_twin', label: 'Readiness Overview & Digital Twin', icon: Layers },
    { id: 'why_not_yet', label: 'Why Not Yet?', icon: HelpCircle },
    { id: 'shap_xai', label: 'Skill Gaps (SHAP XAI)', icon: Activity },
    { id: 'roadmap', label: 'Visual 8-Week Roadmap', icon: BookOpen },
    { id: 'what_if', label: 'What-If Simulator', icon: Sliders },
    { id: 'opportunity_cost', label: 'Opportunity Cost (Where to Spend Time)', icon: Clock },
    { id: 'trajectory', label: 'Progress Trajectory', icon: Activity },
    { id: 'minimum_imp', label: 'Career Fit & Minimum Target', icon: TrendingUp }
  ];

  const DEMO_PERSONAS = [
    { id: 'ST_DEMO_001', name: 'Ananya Sharma', dept: 'ECE', profile: 'Needs Training' },
    { id: 'ST_DEMO_002', name: 'Rahul Verma', dept: 'CSE', profile: 'Near Ready' },
    { id: 'ST_DEMO_003', name: 'Priya Patel', dept: 'CSE', profile: 'Top Performer' },
    { id: 'ST_DEMO_004', name: 'Sneha Rao', dept: 'ECE', profile: 'Hidden Gem' },
    { id: 'ST_DEMO_005', name: 'Arjun Mehta', dept: 'ISE', profile: 'High CGPA / Low Practical' },
    { id: 'ST_DEMO_006', name: 'Meera Nair', dept: 'ECE', profile: 'Strong Tech / Weak Comm' },
    { id: 'ST_DEMO_007', name: 'Karan Shah', dept: 'CSE', profile: 'Strong Aptitude / Weak Tech' },
    { id: 'ST_DEMO_008', name: 'Divya Reddy', dept: 'ISE', profile: 'Strong Projects / No Intern' },
    { id: 'ST_DEMO_009', name: 'Rohan Kumar', dept: 'MECH', profile: 'Low Acad / Strong Practical' },
    { id: 'ST_DEMO_010', name: 'Nisha Patel', dept: 'CSE', profile: 'Strong Comm / Weak Coding' },
    { id: 'ST_DEMO_011', name: 'Vivek Rao', dept: 'ECE', profile: 'Strong Intern / Weak Acad' },
    { id: 'ST_DEMO_012', name: 'Pooja Singh', dept: 'ISE', profile: 'Balanced Mid-Ready' },
    { id: 'ST_DEMO_013', name: 'Aditya Kumar', dept: 'MECH', profile: 'Critical Intervention' }
  ];

  // Calculate monthly trajectory delta if available
  const trajectoryDelta = (trajectory && trajectory.length >= 2)
    ? (trajectory[trajectory.length - 1].readiness_score - trajectory[0].readiness_score)
    : null;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* DEMO STUDENTS QUICK SELECTOR BAR */}
      <div className="glass-card rounded-2xl p-4 border border-indigo-500/20 bg-navy-900/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">DEMO STUDENT SELECTOR</span>
          <span className="text-[10px] text-indigo-300 px-2 py-0.5 rounded bg-indigo-500/20 font-mono">DEMO DATA • 13 Persona Twins</span>
        </div>

        <div className="flex items-center space-x-2 w-full md:w-auto">
          <label className="text-xs text-slate-400 hidden sm:inline">Select Persona:</label>
          <select
            value={selectedPersona}
            onChange={(e) => setSelectedPersona(e.target.value)}
            className="w-full md:w-auto bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-indigo-200 font-semibold focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            {DEMO_PERSONAS.map(p => (
              <option key={p.id} value={p.id} className="bg-navy-900 text-slate-200">
                {p.name} ({p.dept} • {p.profile})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Top Banner Header */}
      <div className="glass-card rounded-2xl p-6 border-indigo-500/20">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          {/* Left Student Meta */}
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-2xl font-black text-white shadow-xl shadow-indigo-600/30">
              {student.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold text-white">{student.name}</h1>
                <DataProvenanceBadge type="SYNTHETIC" />
              </div>
              <p className="text-xs text-slate-300 mt-1">
                {student.department} • Semester {student.semester} • CGPA {student.cgpa} • Target Career:{' '}
                <span className="text-indigo-300 font-bold">{student.target_role}</span>
              </p>
              <div className="flex items-center space-x-4 mt-2 text-[11px] text-slate-400">
                <span>Prediction Confidence: <strong className="text-indigo-300 font-mono">{prediction.prediction_confidence}</strong></span>
                <span>•</span>
                <span>Evidence Confidence: <strong className="text-slate-200">{prediction.evidence_confidence}%</strong></span>
                <span>•</span>
                <span>Profile Completeness: <strong className="text-slate-200">{prediction.profile_completeness}%</strong></span>
              </div>
            </div>
          </div>

          {/* Center Score Ring & Trajectory Badge */}
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <ScoreRing score={currentScore} status={currentStatus} size={120} strokeWidth={8} />
              {trajectoryDelta !== null && (
                <div className="mt-1 text-[11px] font-mono font-bold text-emerald-400">
                  +{trajectoryDelta.toFixed(1)}% this term
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* PLACEMENTIQ AI COPILOT WIDGET */}
      <AiCopilotWidget
        role="student"
        studentData={data}
        onNavigateSubTab={(tabId) => setActiveSubTab(tabId)}
      />

      {/* Prominent HERO NEXT BEST ACTION Card */}
      <div className="relative rounded-2xl bg-gradient-to-r from-indigo-950 via-purple-950 to-navy-900 p-6 border border-indigo-500/30 shadow-xl overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-[11px] font-bold uppercase tracking-wider border border-indigo-500/30">
              <Sparkles className="w-3.5 h-3.5" />
              <span>NEXT BEST ACTION</span>
            </div>
            <h2 className="text-2xl font-black text-white">Improve SQL & Query Optimization Proficiency</h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              Highest-return intervention identified by model counterfactual engine. Elevating SQL from <strong className="text-amber-300 font-mono">4.0</strong> to <strong className="text-emerald-400 font-mono">8.0</strong> provides maximum readiness gain per hour.
            </p>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
              <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Current Level: <strong className="text-amber-300 font-mono">4.0 / 10</strong>
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Target Level: <strong className="text-emerald-400 font-mono">8.0 / 10</strong>
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Estimated Effort: <strong className="text-white font-mono">20 Hours</strong>
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-4 bg-slate-900/80 p-4 rounded-xl border border-indigo-500/30 shrink-0">
            <div className="text-center px-2">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Simulated Impact</span>
              <span className="text-xl font-black text-emerald-400 font-mono">+16.1%</span>
            </div>
            <div className="hidden sm:block h-10 w-px bg-slate-800"></div>
            <div className="text-center px-2">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Priority</span>
              <span className="px-3 py-1 text-xs font-bold bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                HIGH
              </span>
            </div>
            <div className="flex flex-col gap-2 pt-2 sm:pt-0">
              <button
                onClick={() => setActiveSubTab('roadmap')}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-all flex items-center space-x-1.5 justify-center"
              >
                <span>View 8-Week Roadmap</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setActiveSubTab('what_if')}
                className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-300 font-bold text-[11px] transition-all flex items-center space-x-1.5 justify-center border border-indigo-500/30"
              >
                <span>Simulate Improvement</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex overflow-x-auto space-x-2 border-b border-slate-800 pb-2 custom-scrollbar">
        {subTabs.map(t => {
          const Icon = t.icon;
          const isActive = activeSubTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveSubTab(t.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* Sub-Tab 1: Readiness Overview & Digital Twin */}
      {activeSubTab === 'digital_twin' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Employability Digital Twin</h3>
                <p className="text-xs text-slate-400">Student Competencies vs Target Role Benchmark vs Top 10%</p>
              </div>
              <DataProvenanceBadge type="DERIVED" />
            </div>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255, 255, 255, 0.1)" />
                  <PolarAngleAxis dataKey="skill" stroke="#94a3b8" tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 10]} stroke="#64748b" />
                  <Radar name="Student Profile" dataKey="Student" stroke="#6366f1" fill="#6366f1" fillOpacity={0.4} />
                  <Radar name="Role Benchmark" dataKey="Benchmark" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} />
                  <Radar name="Top 10% Peer" dataKey="Top10" stroke="#10b981" fill="#10b981" fillOpacity={0.1} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-6 text-xs">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
                <span className="text-slate-300">You ({student.name})</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                <span className="text-slate-300">Target Role Benchmark</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                <span className="text-slate-300">Top 10% Peer Benchmark</span>
              </div>
            </div>
          </div>

          {/* Core Diagnostic Blockers */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">Top 3 Placement Blockers</h3>
              <DataProvenanceBadge type="DERIVED" />
            </div>
            <p className="text-xs text-slate-400">Primary skill deficits impacting model readiness score</p>
            <div className="space-y-3">
              {why_not_yet?.slice(0, 3).map((gap, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{gap.feature_name}</span>
                    <span className="text-[11px] font-mono font-bold text-rose-400">
                      {gap.current_val} vs {gap.required_val} Req
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-snug">{gap.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 2: Why Not Yet? */}
      {activeSubTab === 'why_not_yet' && (
        <div className="glass-card p-6 rounded-2xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-black text-white">WHY AM I NOT READY YET?</h3>
              <p className="text-xs text-slate-400">Direct comparison between your profile and target role requirements ({student.target_role})</p>
            </div>
            <DataProvenanceBadge type="DERIVED" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {why_not_yet.map((item, idx) => (
              <div key={idx} className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3 hover:border-indigo-500/40 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span className="text-sm font-bold text-white">{item.feature_name}</span>
                  </div>
                  <span className="px-2.5 py-1 text-[11px] font-mono font-bold bg-rose-500/20 text-rose-300 rounded border border-rose-500/30">
                    Gap: -{item.gap.toFixed(1)}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Current Level</span>
                    <strong className="text-amber-300 font-mono text-sm">{item.current_val}</strong>
                  </div>
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Target Requirement</span>
                    <strong className="text-emerald-400 font-mono text-sm">{item.required_val}</strong>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">{item.explanation}</p>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 font-mono">SHAP Impact: {(item.shap_impact * 100).toFixed(2)} pts</span>
                  <button
                    onClick={() => setActiveSubTab('what_if')}
                    className="px-3 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-bold transition-all flex items-center space-x-1"
                  >
                    <span>SIMULATE IMPROVEMENT</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub-Tab 3: Skill Gaps (SHAP XAI) */}
      {activeSubTab === 'shap_xai' && (() => {
        const UNCONTROLLABLE_FEATURES = ['cgpa', 'tenth_percentage', 'twelfth_percentage'];
        const posShapSum = prediction.positive_factors?.reduce((acc, f) => acc + f.shap_value, 0) || 0;
        const negShapSum = prediction.negative_factors?.reduce((acc, f) => acc + f.shap_value, 0) || 0;
        const totalShapSum = posShapSum + negShapSum;
        const rawRfScore = (prediction.base_value / 100.0) + totalShapSum;

        return (
          <div className="glass-card p-6 rounded-2xl space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-black text-white">WHY DID THE MODEL GIVE ME THIS SCORE?</h3>
                <p className="text-xs text-slate-400 mt-1">
                  SHAP explains the underlying Random Forest output. The final readiness score is the calibrated probability. Attributions are expressed in model contribution points (pts).
                </p>
              </div>
              <DataProvenanceBadge type="DERIVED" />
            </div>

            {/* Model Provenance & Attributable Math Summary Banner */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="space-y-0.5">
                <span className="text-[10px] text-slate-400 block font-semibold">BASE EXPECTATION E[f(x)]</span>
                <span className="text-sm font-mono font-bold text-slate-200">{prediction.base_value.toFixed(1)}%</span>
                <span className="text-[10px] text-slate-500 block">Mean tree output across cohort</span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[10px] text-slate-400 block font-semibold">NET SHAP ATTRIBUTION</span>
                <span className={`text-sm font-mono font-bold ${totalShapSum >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {totalShapSum >= 0 ? '+' : ''}{(totalShapSum * 100).toFixed(2)} pts
                </span>
                <span className="text-[10px] text-slate-500 block">Sum of feature attributions</span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[10px] text-slate-400 block font-semibold">RAW RF MODEL OUTPUT f(x)</span>
                <span className="text-sm font-mono font-bold text-amber-300">{(rawRfScore * 100).toFixed(1)}%</span>
                <span className="text-[10px] text-slate-500 block">Base Value + Total SHAP</span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[10px] text-slate-400 block font-semibold">CALIBRATED READINESS</span>
                <span className="text-sm font-mono font-bold text-indigo-300">{prediction.readiness_score.toFixed(1)}%</span>
                <span className="text-[10px] text-slate-500 block">Platt Calibrated Probability</span>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Positive Factors */}
              <div className="space-y-4">
                <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Top Positive Factors (+ Readiness Boost)</span>
                </h4>
                <div className="space-y-3">
                  {prediction.positive_factors?.map((f, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-center justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-white block">{f.feature_name}</span>
                          <span className="px-1.5 py-0.5 text-[9px] font-semibold bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">↑ Positive</span>
                        </div>
                        <span className="text-[11px] text-slate-400">Recorded Value: <strong className="text-slate-200">{f.val}</strong></span>
                      </div>
                      <span className="text-xs font-mono font-bold text-emerald-400">+{(f.shap_value * 100).toFixed(2)} pts</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Negative Factors */}
              <div className="space-y-4">
                <h4 className="text-sm font-bold text-rose-400 uppercase tracking-wider flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>Top Negative Factors (- Readiness Drag)</span>
                </h4>
                <div className="space-y-3">
                  {prediction.negative_factors?.map((f, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30 flex items-center justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-white block">{f.feature_name}</span>
                          <span className="px-1.5 py-0.5 text-[9px] font-semibold bg-rose-500/20 text-rose-300 rounded border border-rose-500/30">↓ Negative</span>
                        </div>
                        <span className="text-[11px] text-slate-400">Recorded Value: <strong className="text-slate-200">{f.val}</strong></span>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-mono font-bold text-rose-400 block">{(f.shap_value * 100).toFixed(2)} pts</span>
                        {!UNCONTROLLABLE_FEATURES.includes(f.feature) ? (
                          <button
                            onClick={() => setActiveSubTab('what_if')}
                            className="text-[10px] text-indigo-300 hover:underline mt-1 block font-semibold"
                          >
                            Simulate Improvement →
                          </button>
                        ) : (
                          <span className="text-[10px] text-slate-500 mt-1 block italic">(Fixed Academic Metric)</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Sub-Tab 4: Visual 8-Week Roadmap */}
      {activeSubTab === 'roadmap' && (
        <div className="glass-card p-6 rounded-2xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-black text-white flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-indigo-400" />
                <span>VISUAL 8-WEEK INTERVENTION ROADMAP</span>
              </h3>
              <p className="text-xs text-slate-400">
                Target Role: <strong className="text-indigo-300">{student.target_role}</strong> • Dynamically loaded preparation plan
              </p>
            </div>
            <DataProvenanceBadge type="DERIVED" />
          </div>

          {roadmapLoading ? (
            <div className="flex flex-col items-center justify-center py-12 space-y-3">
              <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs font-semibold text-slate-400">Synthesizing personalized preparation roadmap...</span>
            </div>
          ) : roadmapError ? (
            <div className="p-6 rounded-xl bg-rose-950/40 border border-rose-500/30 text-center space-y-3">
              <HelpCircle className="w-8 h-8 text-rose-400 mx-auto" />
              <p className="text-sm font-bold text-white">Roadmap Generation Error</p>
              <p className="text-xs text-slate-300">{roadmapError}</p>
              <button
                onClick={() => loadRoadmapData(selectedPersona, student.target_role)}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all"
              >
                Retry Roadmap Generation
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Visual 4-Phase Timeline */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { weeks: 'Weeks 1–2', title: 'SQL & Database Foundations', effort: '10h', priority: 'HIGH', status: 'In Progress' },
                  { weeks: 'Weeks 3–4', title: 'SQL Analytics & Complex Joins', effort: '10h', priority: 'HIGH', status: 'Upcoming' },
                  { weeks: 'Weeks 5–6', title: 'Aptitude & DSA Problem Solving', effort: '15h', priority: 'MEDIUM', status: 'Upcoming' },
                  { weeks: 'Weeks 7–8', title: 'Mock Interviews & Portfolio', effort: '15h', priority: 'MEDIUM', status: 'Upcoming' }
                ].map((phase, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="text-indigo-400 font-bold">{phase.weeks}</span>
                      <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">{phase.priority}</span>
                    </div>
                    <h4 className="text-xs font-bold text-white">{phase.title}</h4>
                    <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                      <span>Effort: {phase.effort}</span>
                      <span className="text-emerald-400 font-semibold">{phase.status}</span>
                    </div>
                  </div>
                ))}
              </div>

              {roadmap?.milestones?.map((m: any, idx: number) => (
                <div key={idx} className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-indigo-300">{m.phase}</span>
                    <span className="px-2.5 py-1 text-[11px] font-mono bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                      Phase {idx + 1}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-semibold">{m.focus}</p>
                  <ul className="space-y-2 pt-2 border-t border-slate-800/80">
                    {m.items?.map((item: string, iIdx: number) => (
                      <li key={iIdx} className="flex items-start space-x-2 text-xs text-slate-300">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 5: What-If Simulator */}
      {activeSubTab === 'what_if' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Sliders className="w-5 h-5 text-indigo-400" />
                  <span>Interactive What-If Skill Simulator</span>
                </h3>
                <p className="text-xs text-slate-400">Modifies feature values and invokes exact loaded Python ML model</p>
              </div>
              <DataProvenanceBadge type="SIMULATED" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {[
                { key: 'sql_score', name: 'SQL Proficiency', min: 1, max: 10, step: 0.5 },
                { key: 'python_score', name: 'Python Proficiency', min: 1, max: 10, step: 0.5 },
                { key: 'dsa_score', name: 'DSA Score', min: 1, max: 10, step: 0.5 },
                { key: 'quantitative_aptitude', name: 'Quantitative Aptitude', min: 1, max: 10, step: 0.5 },
                { key: 'communication_score', name: 'Communication Score', min: 1, max: 10, step: 0.5 },
                { key: 'project_count', name: 'Project Count', min: 1, max: 6, step: 1 },
                { key: 'internships', name: 'Internship Count', min: 0, max: 3, step: 1 }
              ].map(slider => (
                <div key={slider.key} className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">{slider.name}</span>
                    <span className="text-indigo-400 font-mono">{whatIfSliders[slider.key] ?? 5}</span>
                  </div>
                  <input
                    type="range"
                    min={slider.min}
                    max={slider.max}
                    step={slider.step}
                    value={whatIfSliders[slider.key] ?? 5}
                    onChange={(e) => handleSliderChange(slider.key, parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  />
                </div>
              ))}
            </div>

            <button
              onClick={handleRunWhatIf}
              disabled={whatIfLoading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
            >
              {whatIfLoading ? (
                <span>Running Python Model Simulation...</span>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Counterfactual Model Simulation</span>
                </>
              )}
            </button>
          </div>

          {/* Results Box */}
          <div className="glass-card p-6 rounded-2xl space-y-6 border-indigo-500/30">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-mono font-bold text-slate-400 uppercase">Scenario Result</span>
              <span className="px-2 py-0.5 text-[10px] font-mono bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                Model-simulated scenario
              </span>
            </div>

            {whatIfResult ? (
              <div className="space-y-6">
                <div className="text-center space-y-2">
                  <span className="text-xs text-slate-400 block font-mono">Projected Readiness</span>
                  <div className="text-4xl font-black text-indigo-300 font-mono">{whatIfResult.projected_score}%</div>
                  <span className={`inline-block px-3 py-1 text-xs font-bold rounded-full ${
                    whatIfResult.projected_status === 'Ready' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                    whatIfResult.projected_status === 'Near-Ready' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' :
                    'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}>
                    {whatIfResult.projected_status}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Score Delta</span>
                  <span className={`text-sm font-bold ${whatIfResult.score_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {whatIfResult.score_delta >= 0 ? `+${whatIfResult.score_delta}%` : `${whatIfResult.score_delta}%`}
                  </span>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <span className="text-[11px] text-slate-400 font-semibold block">Updated Target Role Fit</span>
                  <div className="space-y-1">
                    {Object.entries(whatIfResult.updated_career_fit || {}).slice(0, 3).map(([role, fit]) => (
                      <div key={role} className="flex justify-between text-xs">
                        <span className="text-slate-300">{role}</span>
                        <span className="font-mono text-indigo-300 font-bold">{fit}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-400 space-y-2">
                <Sliders className="w-8 h-8 text-indigo-400 mx-auto opacity-50" />
                <p>Adjust sliders on left and click "Run Counterfactual Model Simulation" to test scenarios.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sub-Tab 6: Opportunity Cost */}
      {activeSubTab === 'opportunity_cost' && (
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-black text-white">WHERE SHOULD I SPEND MY TIME?</h3>
              <p className="text-xs text-slate-400">Efficiency Index = Readiness Delta / Estimated Hours</p>
            </div>
            <DataProvenanceBadge type="SIMULATED" />
          </div>

          {oppCostLoading ? (
            <div className="flex flex-col items-center justify-center py-12 space-y-3">
              <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs font-semibold text-slate-400">Evaluating 8 Counterfactual Interventions & Efficiency Matrix...</span>
            </div>
          ) : oppCostError ? (
            <div className="p-6 rounded-xl bg-rose-950/40 border border-rose-500/30 text-center space-y-3">
              <HelpCircle className="w-8 h-8 text-rose-400 mx-auto" />
              <p className="text-sm font-bold text-white">Opportunity Cost Engine Error</p>
              <p className="text-xs text-slate-300">{oppCostError}</p>
              <button
                onClick={() => loadOpportunityCostData(selectedPersona)}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all"
              >
                Retry Calculation
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono border-b border-slate-800">
                  <tr>
                    <th className="p-3">Rank</th>
                    <th className="p-3">Skill / Intervention</th>
                    <th className="p-3">Current $\rightarrow$ Simulated</th>
                    <th className="p-3">Readiness Delta</th>
                    <th className="p-3">Effort (Hours)</th>
                    <th className="p-3">Efficiency Index</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {(oppCost || []).map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="p-3 font-mono font-bold text-indigo-400">#{idx + 1}</td>
                      <td className="p-3">
                        <strong className="text-white block">{item.intervention}</strong>
                        <span className="text-[11px] text-slate-400">{item.feature_name}</span>
                      </td>
                      <td className="p-3 font-mono">{item.current_value} $\rightarrow$ {item.simulated_value}</td>
                      <td className="p-3 font-mono text-emerald-400 font-bold">+{item.delta_readiness}%</td>
                      <td className="p-3 font-mono">{item.effort_hours}h</td>
                      <td className="p-3">
                        <span className="px-2.5 py-1 text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 rounded-full border border-indigo-500/30">
                          {item.efficiency_index} pts/hr
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 7: Progress Trajectory */}
      {activeSubTab === 'trajectory' && (
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">READINESS PROGRESS TRAJECTORY</h3>
              <p className="text-xs text-slate-400">Monthly snapshot history computed from database snapshots</p>
            </div>
            <DataProvenanceBadge type="DERIVED" />
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trajectory || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.08)" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis domain={[0, 100]} stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Line type="monotone" dataKey="readiness_score" stroke="#6366f1" strokeWidth={3} dot={{ fill: '#6366f1', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Sub-Tab 8: Minimum Improvement */}
      {activeSubTab === 'minimum_imp' && (
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white">MINIMUM IMPROVEMENT PATH TO 75.0% TARGET</h3>
              <p className="text-xs text-slate-400">Combinatorial greedy search for minimum skill changes required</p>
            </div>
            <DataProvenanceBadge type="SIMULATED" />
          </div>

          {minImpLoading ? (
            <div className="py-12 text-center text-xs text-slate-400">Calculating Minimum Path...</div>
          ) : minImpError ? (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs font-semibold">
              {minImpError}
            </div>
          ) : minImp ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                <span>Current Score: <strong className="text-amber-300 font-mono">{minImp.current_score}%</strong></span>
                <span>Target Score: <strong className="text-emerald-400 font-mono">{minImp.target_score}%</strong></span>
                <span>Projected Score: <strong className="text-indigo-300 font-mono">{minImp.projected_score}%</strong></span>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Required Minimum Changes</h4>
                {minImp.changes?.map((c, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-white font-bold">{c.intervention}</span>
                    <span className="font-mono text-emerald-400 font-bold">+{c.delta_readiness}% readiness</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default StudentPortal;
