import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { StudentPortal } from './pages/StudentPortal';
import { TpoCommandCenter } from './pages/TpoCommandCenter';
import { PlacementSimulator } from './pages/PlacementSimulator';
import { ModelDataGovernance } from './pages/ModelDataGovernance';
import { LandingLoginPage } from './pages/LandingLoginPage';
import { AuthUser } from './types';
import { getMeApi } from './api/client';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

export const App: React.FC = () => {
  const [authRole, setAuthRole] = useState<'student' | 'rpo_tpo' | null>(null);
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [activeTab, setActiveTab] = useState<string>('student');
  const [selectedPersona, setSelectedPersona] = useState<string>('ST_DEMO_001');
  const [authError, setAuthError] = useState<string | null>(null);

  // Restore and verify session from backend on page load/refresh
  useEffect(() => {
    const token = sessionStorage.getItem('placementiq_token');
    const stored = sessionStorage.getItem('placementiq_session');

    if (token) {
      getMeApi()
        .then((res) => {
          if (res && res.user) {
            const roleKey: 'student' | 'rpo_tpo' = res.user.role === 'student' ? 'student' : 'rpo_tpo';
            setAuthRole(roleKey);
            setAuthUser(res.user);
            if (res.user.student_id) {
              setSelectedPersona(res.user.student_id);
            }
            setActiveTab(roleKey === 'student' ? 'student' : 'tpo');
          }
        })
        .catch(() => {
          sessionStorage.removeItem('placementiq_session');
          sessionStorage.removeItem('placementiq_token');
          setAuthRole(null);
          setAuthUser(null);
        });
    } else if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.role && parsed.user) {
          setAuthRole(parsed.role);
          setAuthUser(parsed.user);
          if (parsed.user.student_id) {
            setSelectedPersona(parsed.user.student_id);
          }
          setActiveTab(parsed.role === 'student' ? 'student' : 'tpo');
        }
      } catch (e) {
        sessionStorage.removeItem('placementiq_session');
      }
    }
  }, []);

  const handleLoginSuccess = (role: 'student' | 'rpo_tpo', user: AuthUser) => {
    setAuthRole(role);
    setAuthUser(user);
    if (user.student_id) {
      setSelectedPersona(user.student_id);
    }
    sessionStorage.setItem('placementiq_session', JSON.stringify({ role, user }));
    setActiveTab(role === 'student' ? 'student' : 'tpo');
    setAuthError(null);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('placementiq_session');
    sessionStorage.removeItem('placementiq_token');
    setAuthRole(null);
    setAuthUser(null);
    setAuthError(null);
  };

  const handleTabChange = (targetTab: string) => {
    if (!authRole) {
      setAuthError('Your session has expired. Please sign in again.');
      return;
    }

    // Protect RPO/TPO routes from Student role
    if (authRole === 'student' && (targetTab === 'tpo' || targetTab === 'simulator' || targetTab === 'governance')) {
      setAuthError('You do not have permission to access this workspace.');
      return;
    }

    setAuthError(null);
    setActiveTab(targetTab);
  };

  // If unauthenticated, render LandingLoginPage
  if (!authRole || !authUser) {
    return <LandingLoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 font-sans flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Main Navigation Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        selectedPersona={selectedPersona}
        setSelectedPersona={setSelectedPersona}
        authRole={authRole}
        authUser={authUser}
        onLogout={handleLogout}
      />

      {/* Unauthorized / Route Protection Alert Banner */}
      {authError && (
        <div className="bg-rose-950/90 border-b border-rose-500/50 py-3 px-4 text-center">
          <div className="max-w-7xl mx-auto flex items-center justify-center space-x-2 text-rose-200 text-xs font-semibold">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>{authError}</span>
            <button
              onClick={() => setAuthError(null)}
              className="ml-4 underline hover:text-white text-[11px]"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <OverviewPage
            setActiveTab={handleTabChange}
            setSelectedPersona={setSelectedPersona}
          />
        )}

        {/* STUDENT WORKSPACE */}
        {activeTab === 'student' && (
          <StudentPortal
            selectedPersona={selectedPersona}
            setSelectedPersona={setSelectedPersona}
          />
        )}

        {/* RPO / TPO COMMAND CENTER */}
        {activeTab === 'tpo' && (
          authRole === 'rpo_tpo' ? (
            <TpoCommandCenter />
          ) : (
            <div className="glass-card rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4 border-rose-500/30">
              <ShieldAlert className="w-12 h-12 text-rose-400 mx-auto" />
              <h3 className="text-xl font-bold text-white">Access Denied</h3>
              <p className="text-sm text-slate-400">You do not have permission to access the RPO / TPO Command Center.</p>
              <button
                onClick={() => setActiveTab('student')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl"
              >
                Return to Student Portal
              </button>
            </div>
          )
        )}

        {/* PLACEMENT FLIGHT SIMULATOR */}
        {activeTab === 'simulator' && (
          authRole === 'rpo_tpo' ? (
            <PlacementSimulator />
          ) : (
            <div className="glass-card rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4 border-rose-500/30">
              <ShieldAlert className="w-12 h-12 text-rose-400 mx-auto" />
              <h3 className="text-xl font-bold text-white">Access Denied</h3>
              <p className="text-sm text-slate-400">You do not have permission to access the Institutional Flight Simulator.</p>
              <button
                onClick={() => setActiveTab('student')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl"
              >
                Return to Student Portal
              </button>
            </div>
          )
        )}

        {/* MODEL & DATA TRANSPARENCY */}
        {activeTab === 'governance' && (
          authRole === 'rpo_tpo' ? (
            <ModelDataGovernance />
          ) : (
            <div className="glass-card rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4 border-rose-500/30">
              <ShieldAlert className="w-12 h-12 text-rose-400 mx-auto" />
              <h3 className="text-xl font-bold text-white">Access Denied</h3>
              <p className="text-sm text-slate-400">You do not have permission to access Model & Data Governance.</p>
              <button
                onClick={() => setActiveTab('student')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl"
              >
                Return to Student Portal
              </button>
            </div>
          )
        )}
      </main>

      {/* Institutional Footer */}
      <footer className="border-t border-slate-800 bg-navy-900/60 py-6 text-center text-xs text-slate-500 space-y-1">
        <p className="font-semibold text-slate-400">PLACEMENTIQ — AI Placement Intelligence & Intervention Simulator</p>
        <p>“Predict readiness. Explain the gaps. Simulate interventions. Improve placement outcomes.”</p>
        <p className="text-[10px] text-slate-600 font-mono pt-1">
          Calibrated Random Forest Pipeline • Scikit-Learn • SHAP TreeExplainer • Layer A/B/C Provenance Enforced
        </p>
      </footer>
    </div>
  );
};

export default App;
