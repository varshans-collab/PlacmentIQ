import React from 'react';
import { Target, Users, Plane, Sparkles, UserCheck, LogOut, ShieldCheck, GraduationCap, Building2 } from 'lucide-react';
import { AuthUser } from '../types';

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedPersona: string;
  setSelectedPersona: (persona: string) => void;
  authRole: 'student' | 'rpo_tpo' | null;
  authUser: AuthUser | null;
  onLogout: () => void;
}

export const Header: React.FC<Props> = ({
  activeTab,
  setActiveTab,
  selectedPersona,
  setSelectedPersona,
  authRole,
  authUser,
  onLogout
}) => {
  // Role-aware navigation links
  const studentNav = [
    { id: 'overview', label: 'Overview', icon: Target },
    { id: 'student', label: 'Student Portal', icon: Sparkles }
  ];

  const tpoNav = [
    { id: 'overview', label: 'Overview', icon: Target },
    { id: 'tpo', label: 'RPO / TPO Command Center', icon: Users },
    { id: 'simulator', label: 'Placement Flight Sim', icon: Plane }
  ];

  const mainNav = authRole === 'student' ? studentNav : tpoNav;

  return (
    <header className="border-b border-slate-800 bg-navy-900/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Tagline */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab(authRole === 'student' ? 'student' : 'tpo')}>
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
              <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
                Intervention Simulator & Career Intelligence
              </p>
            </div>
          </div>

          {/* Role Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {mainNav.map((nav) => {
              const Icon = nav.icon;
              const isActive = activeTab === nav.id;
              return (
                <button
                  key={nav.id}
                  onClick={() => setActiveTab(nav.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span>{nav.label}</span>
                </button>
              );
            })}
          </nav>

          {/* User Profile Info & Logout */}
          <div className="flex items-center space-x-3">
            {/* Persona Quick Switcher (ONLY in Student Mode) */}
            {authRole === 'student' && (
              <div className="hidden md:flex items-center space-x-2 bg-slate-900 border border-slate-700/60 rounded-lg px-2.5 py-1.5" title="Switch fictional student demo persona">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span className="text-xs text-slate-400 font-medium">Demo Student:</span>
                <select
                  value={selectedPersona}
                  onChange={(e) => setSelectedPersona(e.target.value)}
                  className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer max-w-[220px] truncate"
                >
                  <option value="ST_DEMO_001" className="bg-navy-900 text-amber-300">
                    Ananya Sharma (ECE • Needs Training)
                  </option>
                  <option value="ST_DEMO_002" className="bg-navy-900 text-indigo-300">
                    Rahul Verma (CSE • Near Ready)
                  </option>
                  <option value="ST_DEMO_003" className="bg-navy-900 text-emerald-300">
                    Priya Patel (CSE • Top Performer)
                  </option>
                  <option value="ST_DEMO_004" className="bg-navy-900 text-emerald-400">
                    Sneha Rao (ECE • Hidden Gem)
                  </option>
                  <option value="ST_DEMO_005" className="bg-navy-900 text-amber-300">
                    Arjun Mehta (ISE • High CGPA / Low Practical)
                  </option>
                  <option value="ST_DEMO_006" className="bg-navy-900 text-indigo-300">
                    Meera Nair (ECE • Strong Tech / Weak Comm)
                  </option>
                  <option value="ST_DEMO_007" className="bg-navy-900 text-amber-300">
                    Karan Shah (CSE • Strong Aptitude / Weak Tech)
                  </option>
                  <option value="ST_DEMO_008" className="bg-navy-900 text-emerald-300">
                    Divya Reddy (ISE • Strong Projects / No Intern)
                  </option>
                  <option value="ST_DEMO_009" className="bg-navy-900 text-indigo-300">
                    Rohan Kumar (MECH • Low Acad / Strong Practical)
                  </option>
                  <option value="ST_DEMO_010" className="bg-navy-900 text-amber-300">
                    Nisha Patel (CSE • Strong Comm / Weak Coding)
                  </option>
                  <option value="ST_DEMO_011" className="bg-navy-900 text-amber-300">
                    Vivek Rao (ECE • Strong Intern / Weak Acad)
                  </option>
                  <option value="ST_DEMO_012" className="bg-navy-900 text-emerald-300">
                    Pooja Singh (ISE • Balanced Mid-Ready)
                  </option>
                  <option value="ST_DEMO_013" className="bg-navy-900 text-rose-400 font-bold">
                    Aditya Kumar (MECH • Critical Intervention)
                  </option>
                </select>
              </div>
            )}

            {/* Authenticated User Badge */}
            {authUser && (
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                {authRole === 'student' ? (
                  <GraduationCap className="w-4 h-4 text-indigo-400" />
                ) : (
                  <Building2 className="w-4 h-4 text-purple-400" />
                )}
                <div className="hidden sm:block text-left">
                  <span className="font-semibold text-slate-200 block truncate max-w-[120px]">
                    {authUser.name}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono block">
                    {authRole === 'student' ? 'STUDENT' : 'RPO/TPO OFFICER'}
                  </span>
                </div>
              </div>
            )}

            {/* Visible Logout Button */}
            <button
              onClick={onLogout}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/50 text-rose-300 text-xs font-semibold transition-all shadow-sm"
              title="Logout of session"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="flex lg:hidden overflow-x-auto space-x-1 py-2 border-t border-slate-800/60">
          {mainNav.map((nav) => {
            const Icon = nav.icon;
            const isActive = activeTab === nav.id;
            return (
              <button
                key={nav.id}
                onClick={() => setActiveTab(nav.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap ${
                  isActive ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40' : 'text-slate-400'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{nav.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};

export default Header;
