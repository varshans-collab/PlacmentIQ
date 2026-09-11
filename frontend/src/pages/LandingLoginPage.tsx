import React, { useState } from 'react';
import { Target, Sparkles, Users, ArrowRight, ShieldCheck, Lock, UserCheck, KeyRound, ArrowLeft, GraduationCap, Building2, Mic } from 'lucide-react';
import { loginApi } from '../api/client';
import { AiOrb } from '../components/AiOrb';

interface Props {
  onLoginSuccess: (role: 'student' | 'rpo_tpo', user: { email: string; id: string; name: string }) => void;
}

type ViewState = 'role_selection' | 'student_login' | 'tpo_login';

export const LandingLoginPage: React.FC<Props> = ({ onLoginSuccess }) => {
  const [viewState, setViewState] = useState<ViewState>('role_selection');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const openStudentLogin = () => {
    setViewState('student_login');
    setEmail('student@placementiq.demo');
    setPassword('student123');
    setError(null);
  };

  const openTpoLogin = () => {
    setViewState('tpo_login');
    setEmail('tpo@placementiq.demo');
    setPassword('tpo123');
    setError(null);
  };

  const backToRoleSelection = () => {
    setViewState('role_selection');
    setError(null);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const targetRole = viewState === 'student_login' ? 'student' : 'rpo_tpo';

    try {
      // Call backend auth API
      const res = await loginApi(email, password, targetRole);
      if (res.authenticated) {
        onLoginSuccess(res.role, res.user);
      } else {
        setError('Incorrect login details. Please try again.');
      }
    } catch (err: any) {
      // Fallback for hackathon demo if backend offline or error
      if (targetRole === 'student') {
        if ((email.trim().toLowerCase() === 'student@placementiq.demo' || email.trim().toLowerCase().startsWith('st_')) && password === 'student123') {
          const studentId = email.toLowerCase().startsWith('st_') ? email.toUpperCase() : 'ST_DEMO_001';
          onLoginSuccess('student', {
            email: email,
            id: studentId,
            name: studentId === 'ST_DEMO_001' ? 'Ananya Sharma' : studentId
          });
        } else {
          setError('Incorrect login details. Please try again.');
        }
      } else {
        if ((email.trim().toLowerCase() === 'tpo@placementiq.demo' || email.trim().toLowerCase() === 'rpo@placementiq.demo') && password === 'tpo123') {
          onLoginSuccess('rpo_tpo', {
            email: email,
            id: 'TPO_ADMIN_001',
            name: 'Institutional Placement Officer'
          });
        } else {
          setError('Incorrect login details. Please try again.');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoStudentLogin = () => {
    onLoginSuccess('student', {
      email: 'student@placementiq.demo',
      id: 'ST_DEMO_001',
      name: 'Ananya Sharma'
    });
  };

  const handleDemoTpoLogin = () => {
    onLoginSuccess('rpo_tpo', {
      email: 'tpo@placementiq.demo',
      id: 'TPO_ADMIN_001',
      name: 'Institutional Placement Officer'
    });
  };

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white relative overflow-hidden bg-command-grid">
      {/* 3D Ambient Backdrop Lights */}
      <div className="ambient-glow-indigo -top-20 left-1/4 -translate-x-1/2" />
      <div className="ambient-glow-purple -bottom-20 right-1/4 translate-x-1/2" />

      {/* Top Header Branding */}
      <header className="py-6 px-4 sm:px-8 border-b border-slate-800/80 bg-navy-900/60 backdrop-blur-md z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={backToRoleSelection}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-indigo-200">
                  PLACEMENT<span className="text-indigo-400">IQ</span>
                </span>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                  v2.0 AI
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="hidden sm:inline-block px-3 py-1 text-xs font-mono font-bold bg-indigo-500/10 text-indigo-300 rounded-full border border-indigo-500/30">
              ROLE-BASED AUTHENTICATION
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-6xl w-full mx-auto px-4 py-12 flex-1 flex flex-col justify-center z-10">
        {/* Brand Tagline & Subtitle */}
        <div className="text-center space-y-3 mb-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-bold uppercase tracking-wider shadow-inner">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>PLACEMENTIQ — AI PLACEMENT COPILOT</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            Understand readiness. Discover what is holding you back. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400">
              Simulate what could happen next.
            </span>
          </h1>

          <p className="text-base sm:text-lg font-bold text-slate-300 pt-1">Who are you today?</p>
        </div>

        {/* 1. ROLE SELECTION LANDING SCREEN */}
        {viewState === 'role_selection' && (
          <div className="space-y-6 animate-fadeIn">
            {/* Center AI Orb Intelligence Core */}
            <div className="flex flex-col items-center justify-center my-2">
              <AiOrb state="IDLE" size={130} onClick={handleDemoStudentLogin} />
              <button
                onClick={handleDemoStudentLogin}
                className="mt-3 px-4 py-2 rounded-xl bg-slate-900/90 hover:bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 hover:text-white text-xs font-bold transition-all flex items-center space-x-2 shadow-lg"
              >
                <Mic className="w-4 h-4 text-indigo-400 animate-pulse" />
                <span>🎙 TALK TO PLACEMENTIQ</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {/* STUDENT ROLE CARD */}
              <div className="glass-card rounded-2xl p-8 border border-slate-800 hover:border-indigo-500/50 transition-all duration-300 flex flex-col justify-between hover:shadow-2xl hover:shadow-indigo-500/10 group">
                <div className="space-y-4">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                    <GraduationCap className="w-7 h-7" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                      <span>STUDENT</span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        Personal AI Coach
                      </span>
                    </h2>
                    <p className="text-slate-300 text-sm mt-2 font-medium leading-relaxed">
                      “Know where you stand. Know what to improve.”
                    </p>
                  </div>
                </div>

                <div className="pt-8 space-y-3">
                  <button
                    onClick={openStudentLogin}
                    className="w-full py-3.5 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
                  >
                    <span>Enter Student Portal</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleDemoStudentLogin}
                    className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-semibold transition-all flex items-center justify-center space-x-1.5"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Quick Demo Student</span>
                  </button>
                </div>
              </div>

              {/* RPO / TPO ROLE CARD */}
              <div className="glass-card rounded-2xl p-8 border border-slate-800 hover:border-purple-500/50 transition-all duration-300 flex flex-col justify-between hover:shadow-2xl hover:shadow-purple-500/10 group">
                <div className="space-y-4">
                  <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                    <Building2 className="w-7 h-7" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                      <span>RPO / TPO</span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        Institutional Command Center
                      </span>
                    </h2>
                    <p className="text-slate-300 text-sm mt-2 font-medium leading-relaxed">
                      “Understand institutional readiness. Optimize placement interventions.”
                    </p>
                  </div>
                </div>

                <div className="pt-8 space-y-3">
                  <button
                    onClick={openTpoLogin}
                    className="w-full py-3.5 px-6 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-sm shadow-lg shadow-purple-600/30 transition-all flex items-center justify-center space-x-2"
                  >
                    <span>Enter RPO / TPO</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleDemoTpoLogin}
                    className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-semibold transition-all flex items-center justify-center space-x-1.5"
                  >
                    <Users className="w-3.5 h-3.5 text-purple-400" />
                    <span>Quick Demo TPO</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Secondary Action: Launch Placement Simulator */}
            <div className="text-center pt-4">
              <button
                onClick={handleDemoTpoLogin}
                className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white text-xs font-bold transition-all shadow-md"
              >
                <span>Launch Placement Simulator</span>
                <ArrowRight className="w-3.5 h-3.5 text-purple-400" />
              </button>
            </div>
          </div>
        )}

        {/* 2. STUDENT LOGIN SCREEN */}
        {viewState === 'student_login' && (
          <div className="max-w-md w-full mx-auto glass-card rounded-2xl p-8 border-indigo-500/30 shadow-2xl space-y-6 animate-fadeIn">
            <button
              onClick={backToRoleSelection}
              className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Role Selection</span>
            </button>

            <div className="space-y-1">
              <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-300 text-xs font-semibold border border-indigo-500/20 mb-1">
                <GraduationCap className="w-3.5 h-3.5" />
                <span>Student Portal Access</span>
              </div>
              <h2 className="text-2xl font-bold text-white">Student Login</h2>
              <p className="text-xs text-slate-400">Enter your credentials to access your readiness twin & SHAP XAI.</p>
            </div>

            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Student ID / Email</label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  placeholder="student@placementiq.demo or ST_DEMO_001"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-500/30 text-rose-300 text-xs font-semibold">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
              >
                <span>{isLoading ? 'Authenticating...' : 'Login as Student'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            <div className="pt-4 border-t border-slate-800/80 space-y-2">
              <button
                type="button"
                onClick={handleDemoStudentLogin}
                className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-indigo-500/30 text-indigo-300 text-xs font-bold transition-all flex items-center justify-center space-x-2"
              >
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span>Use Demo Student</span>
              </button>
              <p className="text-[11px] text-slate-500 text-center font-mono">
                Demo Credentials: student@placementiq.demo / student123
              </p>
            </div>
          </div>
        )}

        {/* 3. RPO / TPO LOGIN SCREEN */}
        {viewState === 'tpo_login' && (
          <div className="max-w-md w-full mx-auto glass-card rounded-2xl p-8 border-purple-500/30 shadow-2xl space-y-6 animate-fadeIn">
            <button
              onClick={backToRoleSelection}
              className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Role Selection</span>
            </button>

            <div className="space-y-1">
              <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded bg-purple-500/10 text-purple-300 text-xs font-semibold border border-purple-500/20 mb-1">
                <Building2 className="w-3.5 h-3.5" />
                <span>RPO / TPO Command Center</span>
              </div>
              <h2 className="text-2xl font-bold text-white">RPO / TPO Login</h2>
              <p className="text-xs text-slate-400">Access institutional cohort analytics, flight simulator & interventions.</p>
            </div>

            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Institution ID / Email</label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-purple-500 transition-colors"
                  placeholder="tpo@placementiq.demo"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-purple-500 transition-colors"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-500/30 text-rose-300 text-xs font-semibold">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all flex items-center justify-center space-x-2"
              >
                <span>{isLoading ? 'Authenticating...' : 'Login as RPO / TPO'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            <div className="pt-4 border-t border-slate-800/80 space-y-2">
              <button
                type="button"
                onClick={handleDemoTpoLogin}
                className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-purple-500/30 text-purple-300 text-xs font-bold transition-all flex items-center justify-center space-x-2"
              >
                <Users className="w-4 h-4 text-purple-400" />
                <span>Use Demo RPO / TPO</span>
              </button>
              <p className="text-[11px] text-slate-500 text-center font-mono">
                Demo Credentials: tpo@placementiq.demo / tpo123
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Institutional Footer */}
      <footer className="py-4 border-t border-slate-800/60 bg-navy-900/40 text-center text-xs text-slate-500">
        <p className="font-semibold text-slate-400">PLACEMENTIQ • AI Placement Intelligence & Intervention Simulator</p>
        <p className="text-[11px] text-slate-600 font-mono mt-0.5">Role-Based Access Control • Session Isolated • Scikit-Learn RF Pipeline</p>
      </footer>
    </div>
  );
};

export default LandingLoginPage;
