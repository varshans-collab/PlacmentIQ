import React, { useEffect, useState } from 'react';
import {
  fetchTPOOverview,
  fetchSkillHeatmap,
  fetchVulnerableStudents,
  fetchStudentsList,
  fetchStudentDetail,
  validateCsvApi
} from '../api/client';
import { TPOOverviewResponse, StudentDetailResponse } from '../types';
import { DataProvenanceBadge } from '../components/DataProvenanceBadge';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';
import {
  Users, AlertTriangle, CheckCircle2, TrendingUp, Sparkles, Filter,
  Grid, Upload, ShieldAlert, BookOpen, Layers, Database, Search, ArrowLeft,
  Plane, Sliders, X, ArrowRight, Activity, HelpCircle, FileText, Check,
  RefreshCw, AlertCircle, DatabaseZap
} from 'lucide-react';
import { ModelDataGovernance } from './ModelDataGovernance';
import { PlacementSimulator } from './PlacementSimulator';
import { ScoreRing } from '../components/ScoreRing';
import { AiCopilotWidget } from '../components/AiCopilotWidget';
import axios from 'axios';

export const TpoCommandCenter: React.FC = () => {
  const [deptFilter, setDeptFilter] = useState<string>('ALL');
  const [overview, setOverview] = useState<TPOOverviewResponse | null>(null);
  const [overviewLoading, setOverviewLoading] = useState<boolean>(true);
  const [overviewError, setOverviewError] = useState<string | null>(null);

  // Skill Heatmap State
  const [heatmap, setHeatmap] = useState<any[]>([]);
  const [heatmapLoading, setHeatmapLoading] = useState<boolean>(true);
  const [heatmapError, setHeatmapError] = useState<string | null>(null);
  const [heatmapDept, setHeatmapDept] = useState<string>('ALL');
  const [heatmapSemester, setHeatmapSemester] = useState<number>(0);
  const [heatmapRole, setHeatmapRole] = useState<string>('ALL');

  // Vulnerable Risk List State
  const [vulnerable, setVulnerable] = useState<any[]>([]);
  const [vulnLoading, setVulnLoading] = useState<boolean>(true);
  const [vulnError, setVulnError] = useState<string | null>(null);
  const [vulnDept, setVulnDept] = useState<string>('ALL');
  const [vulnSemester, setVulnSemester] = useState<number>(0);
  const [vulnRole, setVulnRole] = useState<string>('ALL');
  const [maxReadiness, setMaxReadiness] = useState<number>(60);
  const [minBacklogs, setMinBacklogs] = useState<number>(0);
  const [skillDeficit, setSkillDeficit] = useState<string>('ALL');
  const [riskLevel, setRiskLevel] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<string>('readiness_asc');

  // Active Tab
  const [activeTab, setActiveTab] = useState<'kpi' | 'funnel' | 'interventions' | 'heatmap' | 'vulnerable' | 'search' | 'upload' | 'transparency'>('kpi');

  // Officer Student Search State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchDept, setSearchDept] = useState<string>('ALL');
  const [searchStatus, setSearchStatus] = useState<string>('ALL');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState<boolean>(false);
  const [selectedStudentForInspect, setSelectedStudentForInspect] = useState<string | null>(null);
  const [inspectData, setInspectData] = useState<StudentDetailResponse | null>(null);
  const [inspectLoading, setInspectLoading] = useState<boolean>(false);

  // 5-Step CSV Data Ingestion State
  const [csvStep, setCsvStep] = useState<1 | 2 | 3 | 4 | 5>(1);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<any | null>(null);
  const [validationLoading, setValidationLoading] = useState<boolean>(false);
  const [uploadLoading, setUploadLoading] = useState<boolean>(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  useEffect(() => {
    loadOverviewData();
  }, [deptFilter]);

  useEffect(() => {
    loadHeatmapData();
  }, [heatmapDept, heatmapSemester, heatmapRole]);

  useEffect(() => {
    loadVulnerable();
  }, [vulnDept, vulnSemester, vulnRole, maxReadiness, minBacklogs, skillDeficit, riskLevel, sortBy]);

  useEffect(() => {
    if (activeTab === 'search') {
      loadStudentSearch();
    }
  }, [activeTab, searchDept, searchStatus]);

  useEffect(() => {
    if (selectedStudentForInspect) {
      loadInspectStudent(selectedStudentForInspect);
    } else {
      setInspectData(null);
    }
  }, [selectedStudentForInspect]);

  const loadOverviewData = async () => {
    setOverviewLoading(true);
    setOverviewError(null);
    try {
      const ovData = await fetchTPOOverview(deptFilter);
      setOverview(ovData);
    } catch (err: any) {
      console.error(err);
      setOverviewError(err.message || 'Failed to aggregate institutional analytics');
    } finally {
      setOverviewLoading(false);
    }
  };

  const loadHeatmapData = async () => {
    setHeatmapLoading(true);
    setHeatmapError(null);
    try {
      const hmData = await fetchSkillHeatmap(heatmapDept, heatmapSemester, heatmapRole);
      setHeatmap(hmData.heatmap || []);
    } catch (err: any) {
      console.error(err);
      setHeatmapError(err.message || 'Failed to fetch skill heatmap');
    } finally {
      setHeatmapLoading(false);
    }
  };

  const loadVulnerable = async () => {
    setVulnLoading(true);
    setVulnError(null);
    try {
      const res = await fetchVulnerableStudents(
        vulnDept,
        maxReadiness,
        minBacklogs,
        skillDeficit,
        vulnSemester,
        vulnRole,
        riskLevel,
        sortBy
      );
      setVulnerable(res.vulnerable_students || []);
    } catch (err: any) {
      console.error(err);
      setVulnError(err.message || 'Failed to query vulnerable cohort');
    } finally {
      setVulnLoading(false);
    }
  };

  const loadStudentSearch = async () => {
    setSearchLoading(true);
    try {
      const res = await fetchStudentsList(searchDept === 'ALL' ? undefined : searchDept, searchStatus === 'ALL' ? undefined : searchStatus);
      setSearchResults(res.students || []);
    } catch (err) {
      console.error(err);
    } finally {
      setSearchLoading(false);
    }
  };

  const loadInspectStudent = async (sid: string) => {
    setInspectLoading(true);
    try {
      const res = await fetchStudentDetail(sid, true);
      setInspectData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectLoading(false);
    }
  };

  // Step 1 -> 2: Validate CSV
  const handleValidateCsv = async () => {
    if (!uploadFile) return;
    setValidationLoading(true);
    setUploadMsg(null);
    try {
      const res = await validateCsvApi(uploadFile);
      setValidationResult(res);
      setCsvStep(2);
    } catch (err: any) {
      setUploadMsg(`Validation Error: ${err.response?.data?.detail || err.message || 'Validation failed'}`);
    } finally {
      setValidationLoading(false);
    }
  };

  // Step 4 -> 5: Transaction-Safe Upload
  const handleExecuteUpload = async () => {
    if (!uploadFile) return;
    setUploadLoading(true);
    setUploadMsg(null);
    try {
      const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '';
      const formData = new FormData();
      formData.append('file', uploadFile);
      const res = await axios.post(`${BASE_URL}/api/students/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadMsg(`Database Transaction Success: ${res.data.message || 'Imported ' + res.data.imported_students_count + ' student records successfully'}`);
      setCsvStep(5);
      // Refresh backend analytics across dashboard
      loadOverviewData();
      loadHeatmapData();
      loadVulnerable();
    } catch (err: any) {
      setUploadMsg(`Transaction Failed (Rolled Back): ${err.response?.data?.detail || err.message || 'Database upload failed'}`);
    } finally {
      setUploadLoading(false);
    }
  };

  const resetCsvWizard = () => {
    setCsvStep(1);
    setUploadFile(null);
    setValidationResult(null);
    setUploadMsg(null);
  };

  const filteredStudents = searchResults.filter(s => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (s.name && s.name.toLowerCase().includes(q)) ||
      (s.student_id && s.student_id.toLowerCase().includes(q)) ||
      (s.target_role && s.target_role.toLowerCase().includes(q))
    );
  });

  const skillColumns = ["Python", "SQL", "DSA", "Cloud", "Aptitude", "Communication"];

  const getHeatmapBg = (score: number | null) => {
    if (score === null || score === undefined) return 'bg-slate-900 text-slate-500 border-slate-800';
    if (score < 3.0) return 'bg-rose-950/90 text-rose-300 border-rose-500/50 shadow-sm shadow-rose-950/50 font-bold';
    if (score < 5.0) return 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-sm shadow-amber-950/50 font-bold';
    if (score < 7.0) return 'bg-slate-800/80 text-yellow-200 border-yellow-500/30 font-bold';
    if (score < 8.5) return 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40 font-bold';
    return 'bg-emerald-900 text-emerald-100 border-emerald-400 font-black shadow-sm shadow-emerald-900';
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* TPO Header Banner */}
      <div className="glass-card p-6 rounded-2xl border-indigo-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">INSTITUTIONAL PLACEMENT COMMAND CENTER</h1>
            <DataProvenanceBadge type="SYNTHETIC" />
          </div>
          <p className="text-xs text-slate-300 mt-1 font-medium">
            “Turn student readiness data into placement decisions.” • 600-Student Demonstration Cohort
          </p>
        </div>

        {/* Department Filter */}
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5">
          <Filter className="w-4 h-4 text-indigo-400" />
          <span className="text-xs text-slate-400 font-medium">Department:</span>
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="bg-transparent text-xs font-bold text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="ALL" className="bg-navy-900">ALL DEPARTMENTS</option>
            <option value="CSE" className="bg-navy-900">CSE</option>
            <option value="ISE" className="bg-navy-900">ISE</option>
            <option value="ECE" className="bg-navy-900">ECE</option>
            <option value="Mechanical" className="bg-navy-900">Mechanical</option>
          </select>
        </div>
      </div>

      {/* INSTITUTIONAL PLACEMENT COMMAND COPILOT */}
      <AiCopilotWidget
        role="rpo_tpo"
        tpoData={overview}
        onNavigateSubTab={(tabId) => setActiveTab(tabId as any)}
      />

      {/* Top 4 KPI Cards */}
      {overviewLoading ? (
        <div className="flex items-center justify-center p-8 bg-slate-900/60 rounded-2xl border border-slate-800">
          <div className="flex items-center space-x-3 text-slate-400 text-xs">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <span>Loading Cohort KPIs & Overview Analytics...</span>
          </div>
        </div>
      ) : overviewError || !overview ? (
        <div className="p-6 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
          <h3 className="text-sm font-bold text-white">Cohort Overview Error</h3>
          <p className="text-xs text-slate-300">{overviewError || 'Failed to load cohort overview'}</p>
          <button
            onClick={loadOverviewData}
            className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition-all"
          >
            Retry Overview
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* KPI 1 */}
            <div className="glass-card p-5 rounded-2xl space-y-2 border-l-4 border-l-indigo-500">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Total Student Cohort</span>
                <Users className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-3xl font-black text-white font-mono">{overview.total_students}</div>
              <p className="text-[11px] text-slate-400">Institutional Batch Size</p>
            </div>

            {/* KPI 2 */}
            <div className="glass-card p-5 rounded-2xl space-y-2 border-l-4 border-l-emerald-500">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Placement Ready</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-3xl font-black text-emerald-400 font-mono">
                {overview.ready_count} <span className="text-sm font-normal text-slate-400">({overview.ready_pct}%)</span>
              </div>
              <p className="text-[11px] text-slate-400">Calibrated Score &ge; 80%</p>
            </div>

            {/* KPI 3 */}
            <div className="glass-card p-5 rounded-2xl space-y-2 border-l-4 border-l-indigo-400">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Near-Ready Cohort</span>
                <TrendingUp className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-3xl font-black text-indigo-300 font-mono">
                {overview.near_ready_count} <span className="text-sm font-normal text-slate-400">({overview.near_ready_pct}%)</span>
              </div>
              <p className="text-[11px] text-slate-400">Calibrated Score 60% - 79%</p>
            </div>

            {/* KPI 4 */}
            <div className="glass-card p-5 rounded-2xl space-y-2 border-l-4 border-l-amber-500">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>High-Risk / Vulnerable</span>
                <AlertTriangle className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-3xl font-black text-amber-400 font-mono">
                {overview.needs_training_count} <span className="text-sm font-normal text-slate-400">({overview.needs_training_pct}%)</span>
              </div>
              <p className="text-[11px] text-slate-400">Calibrated Score &lt; 60%</p>
            </div>
          </div>

          {/* Prominent PLACEMENT DECISION BRIEF Card */}
          {overview.next_best_institutional_action && (
            <div className="relative rounded-2xl bg-gradient-to-r from-indigo-950 via-purple-950 to-navy-900 p-6 border border-indigo-500/30 shadow-xl overflow-hidden">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
                <div className="space-y-2 max-w-2xl">
                  <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-[11px] font-bold uppercase tracking-wider border border-indigo-500/30">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>PLACEMENT DECISION BRIEF</span>
                  </div>
                  <h2 className="text-2xl font-black text-white">{overview.next_best_institutional_action.title}</h2>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Primary Bottleneck: <strong className="text-rose-300">Technical Round Attrition</strong> • Target cohort: <strong className="text-indigo-300">{overview.next_best_institutional_action.affected_students} vulnerable students</strong>.
                  </p>
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                    <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      Effort: <strong className="text-white">{overview.next_best_institutional_action.effort}</strong>
                    </span>
                    <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      Primary Deficit: <strong className="text-indigo-300">SQL & Algorithmic Problem Solving</strong>
                    </span>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row items-center gap-4 bg-slate-900/80 p-4 rounded-xl border border-indigo-500/30 shrink-0">
                  <div className="text-center px-2">
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">Estimated Impact</span>
                    <span className="text-xl font-black text-emerald-400 font-mono">{overview.next_best_institutional_action.estimated_impact}</span>
                  </div>
                  <div className="hidden sm:block h-10 w-px bg-slate-800"></div>
                  <div className="text-center px-2">
                    <span className="text-[10px] text-slate-400 uppercase font-mono block">Priority</span>
                    <span className="px-3 py-1 text-xs font-bold bg-rose-500/20 text-rose-300 rounded border border-rose-500/30">
                      {overview.next_best_institutional_action.priority}
                    </span>
                  </div>
                  <div className="pt-2 sm:pt-0 sm:pl-2">
                    <button
                      onClick={() => setActiveTab('interventions')}
                      className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-all flex items-center space-x-1.5"
                    >
                      <span>Test in Intervention Lab</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* TPO Sub-Navigation */}
      <div className="flex overflow-x-auto space-x-2 border-b border-slate-800 pb-2 custom-scrollbar">
        {[
          { id: 'kpi', label: 'Cohort Overview & Brief', icon: Layers },
          { id: 'funnel', label: 'Placement Flight Funnel', icon: Plane },
          { id: 'interventions', label: 'Intervention Lab', icon: Sparkles },
          { id: 'heatmap', label: 'Skill Heatmap', icon: Grid },
          { id: 'vulnerable', label: 'Vulnerable Risk List', icon: ShieldAlert },
          { id: 'search', label: 'Officer Student Search', icon: Search },
          { id: 'upload', label: 'Batch Data Ingestion', icon: Upload },
          { id: 'transparency', label: 'Model & Data Transparency', icon: Database }
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as any);
                setSelectedStudentForInspect(null);
              }}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Sub-Tab 1: Cohort Overview & Brief */}
      {activeTab === 'kpi' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Department Average Readiness Comparison</h3>
                <p className="text-xs text-slate-400">Mean Calibrated Readiness Score by Engineering Branch</p>
              </div>
              <DataProvenanceBadge type="DERIVED" />
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={overview?.department_breakdown || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.08)" />
                  <XAxis dataKey="department" stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} stroke="#64748b" />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                  <Bar dataKey="avg_readiness" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">High-Risk Summary</h3>
              <DataProvenanceBadge type="DERIVED" />
            </div>
            <p className="text-xs text-slate-400">Students with readiness &lt; 60% per department</p>
            <div className="space-y-3">
              {(overview?.department_breakdown || []).map((dept) => (
                <div key={dept.department} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-white block">{dept.department}</span>
                    <span className="text-[11px] text-slate-400">Total: {dept.total_students} students</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-mono font-bold text-amber-400 block">{dept.high_risk_count} Risk</span>
                    <span className="text-[10px] text-slate-500 font-mono">({dept.high_risk_pct}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 2: Placement Flight Funnel */}
      {activeTab === 'funnel' && (
        <PlacementSimulator />
      )}

      {/* Sub-Tab 3: Intervention Lab */}
      {activeTab === 'interventions' && (
        <PlacementSimulator />
      )}

      {/* Sub-Tab 4: Skill Heatmap Matrix */}
      {activeTab === 'heatmap' && (
        <div className="glass-card p-6 rounded-2xl space-y-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <Grid className="w-5 h-5 text-indigo-400" />
                <span>INSTITUTIONAL SKILL HEATMAP MATRIX</span>
              </h3>
              <p className="text-xs text-slate-400">
                Department &times; Skill competency matrix across student cohort
              </p>
            </div>
            <DataProvenanceBadge type="DERIVED" />
          </div>

          {/* Filters Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Filter Department</label>
              <select
                value={heatmapDept}
                onChange={(e) => setHeatmapDept(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="ALL">ALL DEPARTMENTS</option>
                <option value="CSE">CSE</option>
                <option value="ISE">ISE</option>
                <option value="ECE">ECE</option>
                <option value="Mechanical">Mechanical</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Filter Semester</label>
              <select
                value={heatmapSemester}
                onChange={(e) => setHeatmapSemester(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value={0}>ALL SEMESTERS</option>
                {[1, 2, 3, 4, 5, 6, 7, 8].map(s => (
                  <option key={s} value={s}>Semester {s}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Target Role Target</label>
              <select
                value={heatmapRole}
                onChange={(e) => setHeatmapRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="ALL">ALL TARGET ROLES</option>
                <option value="Software Engineer">Software Engineer</option>
                <option value="Data Analyst">Data Analyst</option>
                <option value="Cloud Engineer">Cloud Engineer</option>
                <option value="Core Engineer">Core Engineer</option>
              </select>
            </div>
          </div>

          {heatmapLoading ? (
            <div className="flex items-center justify-center py-16 text-xs text-slate-400 space-x-3">
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Computing Department &times; Skill Competency Matrix...</span>
            </div>
          ) : heatmapError ? (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs font-semibold">
              {heatmapError}
            </div>
          ) : (
            <div className="space-y-6">
              {/* True 2D Matrix Table */}
              <div className="overflow-x-auto rounded-xl border border-slate-800">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-900/90 text-slate-300 uppercase font-mono border-b border-slate-800">
                    <tr>
                      <th className="p-3.5 border-r border-slate-800 min-w-[140px]">Department</th>
                      <th className="p-3.5 border-r border-slate-800 text-center w-24">Cohort Size</th>
                      {skillColumns.map(sk => (
                        <th key={sk} className="p-3.5 text-center min-w-[130px] border-r border-slate-800 last:border-r-0">
                          {sk}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 bg-slate-950/40">
                    {heatmap.map((deptRow) => (
                      <tr key={deptRow.department} className="hover:bg-slate-900/40 transition-colors">
                        <td className="p-3.5 font-bold text-white border-r border-slate-800">
                          <span className="text-sm font-mono tracking-wider">{deptRow.department}</span>
                        </td>
                        <td className="p-3.5 font-mono text-center text-slate-400 border-r border-slate-800">
                          {deptRow.total}
                        </td>
                        {skillColumns.map(sk => {
                          const skillData = deptRow.skills ? deptRow.skills[sk] : deptRow[sk];
                          const score = skillData ? skillData.score : null;
                          const status = skillData ? skillData.status : 'N/A';
                          const count = skillData ? skillData.student_count : 0;
                          return (
                            <td key={sk} className="p-2 border-r border-slate-800 last:border-r-0 text-center">
                              <div
                                className={`p-2.5 rounded-lg border transition-all cursor-default text-center group relative ${getHeatmapBg(score)}`}
                                title={`${deptRow.department} ${sk}: ${score !== null ? score + '/10' : 'N/A'} (${status}) - ${count} students`}
                              >
                                <div className="text-sm font-black font-mono">
                                  {score !== null ? `${score.toFixed(1)}` : 'N/A'}
                                  <span className="text-[10px] font-normal text-slate-400"> / 10</span>
                                </div>
                                <div className="text-[10px] font-medium opacity-90 truncate mt-0.5">
                                  {status}
                                </div>
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Color Scale Legend */}
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2">
                <span className="text-[11px] font-mono uppercase text-slate-400 font-bold block">Competency Color Scale Legend</span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  <div className="flex items-center space-x-2 p-2 rounded-lg bg-rose-950/80 border border-rose-500/50 text-rose-300 text-[11px]">
                    <div className="w-3 h-3 rounded-full bg-rose-500 shrink-0"></div>
                    <div>
                      <span className="font-bold block">&lt; 3.0 / 10</span>
                      <span className="text-[10px] text-slate-400">Critical Deficit</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 p-2 rounded-lg bg-amber-950/80 border border-amber-500/50 text-amber-300 text-[11px]">
                    <div className="w-3 h-3 rounded-full bg-amber-500 shrink-0"></div>
                    <div>
                      <span className="font-bold block">3.0 - 4.9 / 10</span>
                      <span className="text-[10px] text-slate-400">Needs Improvement</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 p-2 rounded-lg bg-slate-800/80 border border-yellow-500/30 text-yellow-200 text-[11px]">
                    <div className="w-3 h-3 rounded-full bg-yellow-400 shrink-0"></div>
                    <div>
                      <span className="font-bold block">5.0 - 6.9 / 10</span>
                      <span className="text-[10px] text-slate-400">Developing</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 p-2 rounded-lg bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-[11px]">
                    <div className="w-3 h-3 rounded-full bg-emerald-500 shrink-0"></div>
                    <div>
                      <span className="font-bold block">7.0 - 8.4 / 10</span>
                      <span className="text-[10px] text-slate-400">Strong</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 p-2 rounded-lg bg-emerald-900 border border-emerald-400 text-emerald-100 text-[11px]">
                    <div className="w-3 h-3 rounded-full bg-emerald-300 shrink-0"></div>
                    <div>
                      <span className="font-bold block">8.5 - 10.0 / 10</span>
                      <span className="text-[10px] text-slate-400">Advanced</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 5: Vulnerable Risk List */}
      {activeTab === 'vulnerable' && (
        <div className="glass-card p-6 rounded-2xl space-y-6">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <ShieldAlert className="w-5 h-5 text-amber-400" />
                <span>VULNERABLE STUDENT RISK LIST</span>
              </h3>
              <p className="text-xs text-slate-400">
                Actionable student roster requiring targeted academic & skill interventions ({vulnerable.length} students matched)
              </p>
            </div>
            <DataProvenanceBadge type="SYNTHETIC" />
          </div>

          {/* Detailed Filtering & Sorting Control Panel */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Risk Level</label>
              <select
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="ALL">ALL RISK LEVELS</option>
                <option value="CRITICAL">CRITICAL (&lt; 40%)</option>
                <option value="HIGH">HIGH (40 - 59%)</option>
                <option value="MODERATE">MODERATE (60 - 79%)</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Department</label>
              <select
                value={vulnDept}
                onChange={(e) => setVulnDept(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="ALL">ALL DEPARTMENTS</option>
                <option value="CSE">CSE</option>
                <option value="ISE">ISE</option>
                <option value="ECE">ECE</option>
                <option value="Mechanical">Mechanical</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Max Readiness Cutoff</label>
              <div className="flex items-center space-x-2">
                <input
                  type="range"
                  min="30"
                  max="80"
                  value={maxReadiness}
                  onChange={(e) => setMaxReadiness(Number(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer"
                />
                <span className="text-xs font-mono font-bold text-indigo-400 w-10 text-right">{maxReadiness}%</span>
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Sort Cohort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="readiness_asc">Readiness Score (Low to High)</option>
                <option value="risk_desc">Risk Level (Critical First)</option>
                <option value="dept_asc">Department</option>
                <option value="name_asc">Student Name</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Min Active Backlogs</label>
              <select
                value={minBacklogs}
                onChange={(e) => setMinBacklogs(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value={0}>Any Backlogs (0+)</option>
                <option value={1}>At Least 1 Backlog</option>
                <option value={2}>2+ Backlogs</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Specific Skill Deficit</label>
              <select
                value={skillDeficit}
                onChange={(e) => setSkillDeficit(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="ALL">ALL DEFICITS</option>
                <option value="sql_score">SQL &lt; 6.0</option>
                <option value="dsa_score">DSA &lt; 6.0</option>
                <option value="communication_score">Comm &lt; 6.0</option>
                <option value="project_count">Projects &lt; 2</option>
                <option value="internships">0 Internships</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Semester</label>
              <select
                value={vulnSemester}
                onChange={(e) => setVulnSemester(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value={0}>ALL SEMESTERS</option>
                {[5, 6, 7, 8].map(s => (
                  <option key={s} value={s}>Semester {s}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Target Role</label>
              <select
                value={vulnRole}
                onChange={(e) => setVulnRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:border-indigo-500 outline-none"
              >
                <option value="ALL">ALL ROLES</option>
                <option value="Software Engineer">Software Engineer</option>
                <option value="Data Analyst">Data Analyst</option>
                <option value="Cloud Engineer">Cloud Engineer</option>
                <option value="Core Engineer">Core Engineer</option>
              </select>
            </div>
          </div>

          {vulnLoading ? (
            <div className="py-16 text-center text-xs text-slate-400 space-y-3">
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <span>Querying vulnerable student cohort...</span>
            </div>
          ) : vulnError ? (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs font-semibold">
              {vulnError}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-800">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono border-b border-slate-800">
                  <tr>
                    <th className="p-3">Student ID</th>
                    <th className="p-3">Student Name</th>
                    <th className="p-3">Dept &amp; Sem</th>
                    <th className="p-3">Readiness</th>
                    <th className="p-3">Risk Level</th>
                    <th className="p-3">Reason Badge</th>
                    <th className="p-3">Top Skill Deficit</th>
                    <th className="p-3">Target Role</th>
                    <th className="p-3">Recommended Action</th>
                    <th className="p-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                  {vulnerable.map((s, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-3 font-mono font-bold text-indigo-400">{s.student_id}</td>
                      <td className="p-3 font-semibold text-white">{s.name}</td>
                      <td className="p-3 text-slate-300">{s.department} (Sem {s.semester})</td>
                      <td className="p-3 font-mono font-bold text-amber-400">{s.readiness_score}%</td>
                      <td className="p-3">
                        <span className={`px-2.5 py-1 text-[10px] font-bold rounded-md border ${
                          s.risk === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse' :
                          s.risk === 'HIGH' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                          'bg-yellow-500/20 text-yellow-300 border-yellow-500/40'
                        }`}>
                          {s.risk}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${
                          s.reason_badge === 'SQL GAP' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' :
                          s.reason_badge === 'CODING GAP' ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' :
                          s.reason_badge === 'COMMUNICATION GAP' ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' :
                          s.reason_badge === 'PROJECT GAP' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                          'bg-rose-500/20 text-rose-300 border-rose-500/30'
                        }`}>
                          {s.reason_badge}
                        </span>
                      </td>
                      <td className="p-3 font-mono font-bold text-rose-300">{s.top_deficit}</td>
                      <td className="p-3 text-slate-400">{s.target_role}</td>
                      <td className="p-3 text-indigo-300 font-medium">{s.recommended_action}</td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => {
                            setActiveTab('search');
                            setSelectedStudentForInspect(s.student_id);
                          }}
                          className="px-3 py-1 text-[11px] font-bold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all shadow-md shadow-indigo-600/30"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 6: Officer Student Search */}
      {activeTab === 'search' && (
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Search className="w-5 h-5 text-indigo-400" />
                  <span>OFFICER STUDENT SEARCH &amp; DIRECTORY</span>
                </h3>
                <p className="text-xs text-slate-400">Inspect full student profiles inline with real synthetic Indian student names</p>
              </div>
              <DataProvenanceBadge type="SYNTHETIC" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by Name, Student ID, or Target Role..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <select
                  value={searchDept}
                  onChange={(e) => setSearchDept(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="ALL">ALL DEPARTMENTS</option>
                  <option value="CSE">CSE</option>
                  <option value="ISE">ISE</option>
                  <option value="ECE">ECE</option>
                  <option value="Mechanical">Mechanical</option>
                </select>
              </div>

              <div>
                <select
                  value={searchStatus}
                  onChange={(e) => setSearchStatus(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="ALL">ALL STATUSES</option>
                  <option value="Ready">Ready (&ge; 80%)</option>
                  <option value="Near-Ready">Near-Ready (60-79%)</option>
                  <option value="Needs Training">Needs Training (&lt; 60%)</option>
                </select>
              </div>
            </div>

            {searchLoading ? (
              <div className="py-8 text-center text-xs text-slate-400">Loading student directory...</div>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-800">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono border-b border-slate-800">
                    <tr>
                      <th className="p-3">Student ID</th>
                      <th className="p-3">Student Name</th>
                      <th className="p-3">Dept</th>
                      <th className="p-3">CGPA</th>
                      <th className="p-3">Target Role</th>
                      <th className="p-3">Readiness</th>
                      <th className="p-3">Status</th>
                      <th className="p-3 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                    {filteredStudents.slice(0, 30).map((s, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                        <td className="p-3 font-mono font-bold text-indigo-400">{s.student_id}</td>
                        <td className="p-3 font-semibold text-white">{s.name}</td>
                        <td className="p-3">{s.department}</td>
                        <td className="p-3 font-mono">{s.cgpa}</td>
                        <td className="p-3 font-medium text-slate-300">{s.target_role}</td>
                        <td className="p-3 font-mono font-bold">{s.readiness_score}%</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                            s.status === 'Ready' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                            s.status === 'Near-Ready' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' :
                            'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          }`}>
                            {s.status}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <button
                            onClick={() => setSelectedStudentForInspect(s.student_id)}
                            className="px-3 py-1 text-[11px] font-bold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all shadow-md shadow-indigo-600/30"
                          >
                            Inspect Profile
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Officer Student Diagnostic Drawer Modal */}
          {selectedStudentForInspect && (
            <div className="fixed inset-0 z-50 bg-navy-950/80 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="glass-card max-w-4xl w-full rounded-2xl p-6 border-indigo-500/30 shadow-2xl max-h-[90vh] overflow-y-auto space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => setSelectedStudentForInspect(null)}
                      className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 transition-colors"
                    >
                      <ArrowLeft className="w-4 h-4" />
                    </button>
                    <div>
                      <h3 className="text-xl font-bold text-white">Officer Student Diagnostic</h3>
                      <p className="text-xs text-slate-400">Student ID: {selectedStudentForInspect}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedStudentForInspect(null)}
                    className="p-2 text-slate-400 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {inspectLoading || !inspectData ? (
                  <div className="py-12 text-center text-xs text-slate-400">Loading student diagnostic twin...</div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 rounded-xl bg-slate-900 border border-slate-800 gap-4">
                      <div>
                        <h4 className="text-lg font-bold text-white">{inspectData.student.name}</h4>
                        <p className="text-xs text-slate-400">
                          {inspectData.student.department} &bull; Semester {inspectData.student.semester} &bull; CGPA {inspectData.student.cgpa} &bull; Target: {inspectData.student.target_role}
                        </p>
                      </div>
                      <ScoreRing score={inspectData.prediction.readiness_score} status={inspectData.prediction.status} size={90} strokeWidth={6} />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                        <h5 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Top Controllable Weaknesses</h5>
                        <ul className="space-y-1.5 text-xs text-slate-300">
                          {inspectData.why_not_yet?.slice(0, 4).map((g, i) => (
                            <li key={i} className="flex justify-between border-b border-slate-800/40 pb-1">
                              <span>{g.feature_name}</span>
                              <span className="font-mono text-rose-400 font-bold">{g.current_val} vs {g.required_val}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                        <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Next Best Institutional Action</h5>
                        {inspectData.opportunity_cost && inspectData.opportunity_cost.length > 0 ? (
                          <div>
                            <span className="text-xs font-bold text-white block">{inspectData.opportunity_cost[0].intervention}</span>
                            <span className="text-[11px] text-slate-300 mt-1 block">
                              +{inspectData.opportunity_cost[0].delta_readiness}% readiness in {inspectData.opportunity_cost[0].effort_hours}h effort
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400">Student is on track for target role.</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 7: 5-Step Batch Data Ingestion Wizard */}
      {activeTab === 'upload' && (
        <div className="glass-card p-6 rounded-2xl max-w-4xl mx-auto space-y-6 border-indigo-500/30">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <Upload className="w-5 h-5 text-indigo-400" />
                <span>BATCH DATA INGESTION WIZARD</span>
              </h3>
              <p className="text-xs text-slate-400">5-Step Institutional CSV Ingestion Pipeline with Transaction Safety</p>
            </div>
            <DataProvenanceBadge type="OBSERVED" />
          </div>

          {/* 5-Step Pipeline Tracker */}
          <div className="grid grid-cols-5 gap-2 bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-center text-xs font-semibold">
            {[
              { num: 1, label: 'Upload CSV' },
              { num: 2, label: 'Validate' },
              { num: 3, label: 'Preview' },
              { num: 4, label: 'Confirm' },
              { num: 5, label: 'Import' }
            ].map(step => (
              <div
                key={step.num}
                className={`py-2 px-1 rounded-lg border transition-all ${
                  csvStep === step.num
                    ? 'bg-indigo-600 text-white border-indigo-400 font-bold shadow-md shadow-indigo-600/30'
                    : csvStep > step.num
                    ? 'bg-emerald-950/60 text-emerald-300 border-emerald-500/30'
                    : 'bg-slate-950/40 text-slate-500 border-slate-800'
                }`}
              >
                <div className="text-[10px] uppercase tracking-wider font-mono">Step {step.num}</div>
                <div className="truncate">{step.label}</div>
              </div>
            ))}
          </div>

          {/* STEP 1: UPLOAD CSV FILE */}
          {csvStep === 1 && (
            <div className="space-y-6">
              <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-8 text-center space-y-4 bg-slate-900/40 transition-colors">
                <FileText className="w-10 h-10 text-indigo-400 mx-auto" />
                <div className="space-y-1">
                  <div className="text-sm text-white font-bold">Select Institutional CSV File</div>
                  <p className="text-xs text-slate-400 max-w-md mx-auto">
                    Required headers: <code className="text-indigo-300">cgpa, python_score, sql_score, dsa_score, department</code>
                  </p>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-5 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
                />
              </div>

              {uploadMsg && (
                <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-500/30 text-rose-300 text-xs font-semibold">
                  {uploadMsg}
                </div>
              )}

              <button
                onClick={handleValidateCsv}
                disabled={validationLoading || !uploadFile}
                className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {validationLoading ? (
                  <span>Executing CSV Validation &amp; Schema Dry-Run...</span>
                ) : (
                  <span>Validate CSV File (Dry-Run)</span>
                )}
              </button>
            </div>
          )}

          {/* STEP 2: VALIDATION RESULTS */}
          {csvStep === 2 && validationResult && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 font-mono uppercase block">Total Rows</span>
                  <span className="text-xl font-bold font-mono text-white">{validationResult.total_rows}</span>
                </div>
                <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
                  <span className="text-[10px] text-emerald-400 font-mono uppercase block">Valid Rows</span>
                  <span className="text-xl font-bold font-mono text-emerald-300">{validationResult.valid_rows}</span>
                </div>
                <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30">
                  <span className="text-[10px] text-rose-400 font-mono uppercase block">Invalid Rows</span>
                  <span className="text-xl font-bold font-mono text-rose-300">{validationResult.invalid_rows}</span>
                </div>
                <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-500/30">
                  <span className="text-[10px] text-amber-400 font-mono uppercase block">Duplicate IDs</span>
                  <span className="text-xl font-bold font-mono text-amber-300">{validationResult.duplicate_ids}</span>
                </div>
              </div>

              {validationResult.errors && validationResult.errors.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider">Validation Errors Identified</h4>
                  <div className="max-h-48 overflow-y-auto rounded-xl border border-rose-500/30 bg-rose-950/20">
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="bg-rose-950/60 font-mono text-rose-300">
                        <tr>
                          <th className="p-2">Row #</th>
                          <th className="p-2">Column</th>
                          <th className="p-2">Value</th>
                          <th className="p-2">Error Description</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-rose-950/40 font-mono">
                        {validationResult.errors.map((err: any, idx: number) => (
                          <tr key={idx}>
                            <td className="p-2 font-bold">{err.row}</td>
                            <td className="p-2 text-amber-300">{err.column}</td>
                            <td className="p-2 text-slate-400">{err.value}</td>
                            <td className="p-2 text-rose-300">{err.error}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={resetCsvWizard}
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-bold"
                >
                  Select Different File
                </button>
                <button
                  onClick={() => setCsvStep(3)}
                  disabled={validationResult.valid_rows === 0}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg disabled:opacity-50"
                >
                  Proceed to Data Preview ({validationResult.valid_rows} Valid Records)
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: DATA PREVIEW */}
          {csvStep === 3 && validationResult && (
            <div className="space-y-6">
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Parsed Data Sample Preview</h4>
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-900 font-mono text-slate-400 uppercase">
                      <tr>
                        <th className="p-3">Student ID</th>
                        <th className="p-3">Name</th>
                        <th className="p-3">Dept</th>
                        <th className="p-3">CGPA</th>
                        <th className="p-3">Python</th>
                        <th className="p-3">SQL</th>
                        <th className="p-3">DSA</th>
                        <th className="p-3">Target Role</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950">
                      {validationResult.preview?.map((p: any, idx: number) => (
                        <tr key={idx}>
                          <td className="p-3 font-mono font-bold text-indigo-400">{p.student_id}</td>
                          <td className="p-3 font-semibold text-white">{p.name}</td>
                          <td className="p-3">{p.department}</td>
                          <td className="p-3 font-mono">{p.cgpa}</td>
                          <td className="p-3 font-mono">{p.python_score}</td>
                          <td className="p-3 font-mono">{p.sql_score}</td>
                          <td className="p-3 font-mono">{p.dsa_score}</td>
                          <td className="p-3 text-slate-300">{p.target_role}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={() => setCsvStep(2)}
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-bold"
                >
                  Back to Validation
                </button>
                <button
                  onClick={() => setCsvStep(4)}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg"
                >
                  Proceed to Confirmation
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: CONFIRM & TRANSACTION SAFETY */}
          {csvStep === 4 && (
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-indigo-950/40 border border-indigo-500/40 space-y-4">
                <div className="flex items-center space-x-3">
                  <DatabaseZap className="w-6 h-6 text-indigo-400" />
                  <h4 className="text-base font-bold text-white">Atomic Transaction Safety Guarantee</h4>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  The SQLite database engine will execute this batch import inside an isolated SQL transaction (<code className="text-indigo-300">BEGIN TRANSACTION;</code>).
                  If any runtime error occurs during ML feature calculation or row insertion, the transaction will automatically perform a full rollback (<code className="text-indigo-300">ROLLBACK;</code>), ensuring zero database corruption.
                </p>
                <div className="text-xs font-mono text-emerald-300 font-bold bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                  Ready to import {validationResult?.valid_rows || 'batch'} records into PlacementIQ production state.
                </div>
              </div>

              {uploadMsg && (
                <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-500/30 text-rose-300 text-xs font-semibold">
                  {uploadMsg}
                </div>
              )}

              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={() => setCsvStep(3)}
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-bold"
                >
                  Back to Preview
                </button>
                <button
                  onClick={handleExecuteUpload}
                  disabled={uploadLoading}
                  className="px-8 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 transition-all flex items-center space-x-2 disabled:opacity-50"
                >
                  {uploadLoading ? (
                    <span>Executing SQL Transaction &amp; Running ML Predictions...</span>
                  ) : (
                    <span>Execute Transactional Import</span>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* STEP 5: IMPORT COMPLETE & REFRESH */}
          {csvStep === 5 && (
            <div className="text-center py-8 space-y-6">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center mx-auto">
                <Check className="w-8 h-8" />
              </div>
              <div className="space-y-2">
                <h4 className="text-xl font-bold text-white">Batch Import &amp; Ingestion Complete!</h4>
                <p className="text-xs text-slate-300 max-w-md mx-auto">
                  {uploadMsg || 'The batch data was ingested and instant ML predictions were calculated.'}
                </p>
              </div>
              <div className="pt-4 flex justify-center space-x-4">
                <button
                  onClick={resetCsvWizard}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg"
                >
                  Upload Another Batch CSV
                </button>
                <button
                  onClick={() => setActiveTab('heatmap')}
                  className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-bold border border-slate-800"
                >
                  View Updated Skill Heatmap
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 8: Model & Data Transparency */}
      {activeTab === 'transparency' && (
        <ModelDataGovernance />
      )}
    </div>
  );
};

export default TpoCommandCenter;
