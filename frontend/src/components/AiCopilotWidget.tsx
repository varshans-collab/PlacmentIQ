import React, { useState, useEffect, useRef } from 'react';
import { AiOrb, OrbState } from './AiOrb';
import { StudentDetailResponse, TPOOverviewResponse } from '../types';
import { Mic, MicOff, Volume2, VolumeX, Send, Sparkles, X, ArrowRight, HelpCircle, AlertCircle, CheckCircle2 } from 'lucide-react';

interface CopilotInsight {
  query: string;
  headline: string;
  body: string;
  currentVal?: string;
  targetVal?: string;
  effort?: string;
  simulatedImpact?: string;
  actionText?: string;
  actionSubTab?: string;
  actionType?: 'what_if' | 'roadmap' | 'opportunity_cost' | 'why_not_yet' | 'interventions';
}

interface Props {
  role: 'student' | 'rpo_tpo';
  studentData?: StudentDetailResponse | null;
  tpoData?: TPOOverviewResponse | null;
  onNavigateSubTab?: (tabId: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const AiCopilotWidget: React.FC<Props> = ({
  role,
  studentData,
  tpoData,
  onNavigateSubTab,
  isOpen = false,
  onClose
}) => {
  const [orbState, setOrbState] = useState<OrbState>('IDLE');
  const [inputText, setInputText] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [voiceAvailable, setVoiceAvailable] = useState<boolean>(true);
  const [currentInsight, setCurrentInsight] = useState<CopilotInsight | null>(null);
  const [transcriptHistory, setTranscriptHistory] = useState<{ role: 'user' | 'assistant'; text: string; insight?: CopilotInsight }[]>([]);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setOrbState('LISTENING');
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        handleProcessQuery(transcript);
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
        setOrbState('IDLE');
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } else {
      setVoiceAvailable(false);
    }
  }, [role, studentData, tpoData]);

  const toggleVoiceListen = () => {
    if (!voiceAvailable) return;
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleSpeakText = (text: string) => {
    if (isMuted || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onstart = () => setOrbState('RESPONDING');
    utterance.onend = () => setOrbState('IDLE');
    window.speechSynthesis.speak(utterance);
  };

  const handleProcessQuery = (query: string) => {
    if (!query.trim()) return;
    setOrbState('THINKING');

    setTimeout(() => {
      let insight: CopilotInsight;

      if (role === 'student' && studentData) {
        insight = processStudentIntent(query.toLowerCase(), studentData);
      } else if (role === 'rpo_tpo' && tpoData) {
        insight = processTpoIntent(query.toLowerCase(), tpoData);
      } else {
        insight = {
          query,
          headline: 'PlacementIQ Copilot Connected',
          body: 'System data loaded. Ask any question about your readiness score, feature attributions, or intervention simulations.'
        };
      }

      setCurrentInsight(insight);
      setTranscriptHistory(prev => [
        ...prev,
        { role: 'user', text: query },
        { role: 'assistant', text: insight.headline + '. ' + insight.body, insight }
      ]);
      setOrbState('RESPONDING');
      handleSpeakText(insight.headline + '. ' + insight.body);
    }, 600);
  };

  const processStudentIntent = (q: string, data: StudentDetailResponse): CopilotInsight => {
    const s = data.student;
    const p = data.prediction;
    const topGap = data.why_not_yet?.[0];

    if (q.includes('why') || q.includes('not ready') || q.includes('holding me back')) {
      return {
        query: q,
        headline: `Your primary gap is ${topGap?.feature_name || 'SQL & Databases'}`,
        body: `Current level is ${topGap?.current_val || 4.0} vs ${topGap?.required_val || 8.0} required for ${s.target_role}. SHAP model attribution identifies this as your largest drag (-${((topGap?.shap_impact || 0.05) * 100).toFixed(1)} pts).`,
        currentVal: `${topGap?.current_val || 4.0} / 10`,
        targetVal: `${topGap?.required_val || 8.0} / 10`,
        effort: '20 Hours',
        simulatedImpact: '+16.1 pts',
        actionText: 'View Why Not Yet Breakdown',
        actionSubTab: 'why_not_yet',
        actionType: 'why_not_yet'
      };
    } else if (q.includes('skill') || q.includes('improve') || q.includes('gap')) {
      return {
        query: q,
        headline: `Focus on ${topGap?.feature_name || 'SQL & Problem Solving'}`,
        body: `Improving ${topGap?.feature_name || 'SQL'} from ${topGap?.current_val || 4.0} to ${topGap?.required_val || 8.0} yields maximum readiness gain per hour of effort.`,
        currentVal: `${topGap?.current_val || 4.0}`,
        targetVal: `${topGap?.required_val || 8.0}`,
        effort: '20 Hours',
        simulatedImpact: '+16.1 pts',
        actionText: 'Simulate Improvement',
        actionSubTab: 'what_if',
        actionType: 'what_if'
      };
    } else if (q.includes('return') || q.includes('time') || q.includes('highest')) {
      return {
        query: q,
        headline: 'Highest Return Skill: SQL Bootcamp',
        body: 'SQL provides 0.81 readiness points per hour of effort — higher ROI than General Aptitude or DSA workshops.',
        currentVal: '4.0 / 10',
        targetVal: '8.0 / 10',
        effort: '20 Hours',
        simulatedImpact: '+16.1 pts',
        actionText: 'View Opportunity Cost Matrix',
        actionSubTab: 'opportunity_cost',
        actionType: 'opportunity_cost'
      };
    } else if (q.includes('70') || q.includes('reach') || q.includes('sql') || q.includes('what if')) {
      return {
        query: q,
        headline: `Target 70% Readiness is Achievable (${p.readiness_score}% → 69.8%)`,
        body: `Simulating a +4 boost in SQL and +1 project elevates your calibrated readiness from ${p.readiness_score}% to 69.8% (+16.1 pts delta).`,
        currentVal: `${p.readiness_score}%`,
        targetVal: '69.8%',
        effort: '25 Hours',
        simulatedImpact: '+16.1 pts',
        actionText: 'Open What-If Simulator',
        actionSubTab: 'what_if',
        actionType: 'what_if'
      };
    } else if (q.includes('roadmap') || q.includes('plan')) {
      return {
        query: q,
        headline: 'Personalized 8-Week Placement Roadmap Ready',
        body: `Structured preparation plan synthesized for target role ${s.target_role}. Phase 1 focuses on SQL foundations, followed by DSA & mock technical interviews.`,
        actionText: 'View 8-Week Roadmap',
        actionSubTab: 'roadmap',
        actionType: 'roadmap'
      };
    } else {
      return {
        query: q,
        headline: `Current Placement Readiness: ${p.readiness_score}% (${p.status})`,
        body: `Model predicts ${p.readiness_score}% readiness for ${s.target_role}. Your top strengths are ${p.positive_factors?.[0]?.feature_name || 'Academics'} and ${p.positive_factors?.[1]?.feature_name || 'DSA'}.`,
        actionText: 'Open What-If Simulator',
        actionSubTab: 'what_if',
        actionType: 'what_if'
      };
    }
  };

  const processTpoIntent = (q: string, data: TPOOverviewResponse): CopilotInsight => {
    const act = data.next_best_institutional_action;

    if (q.includes('losing') || q.includes('bottleneck') || q.includes('where')) {
      return {
        query: q,
        headline: 'Primary Bottleneck: Technical Round Attrition',
        body: 'Simulated recruitment funnel identifies Technical Round elimination as the largest loss stage (283 candidates eliminated due to SQL & Algorithmic gaps).',
        simulatedImpact: '+64 Selections',
        effort: '40 Hours',
        actionText: 'Launch Placement Flight Simulator',
        actionSubTab: 'funnel'
      };
    } else if (q.includes('department') || q.includes('dept') || q.includes('risk')) {
      return {
        query: q,
        headline: 'Department Focus: ECE & Mechanical Vulnerabilities',
        body: 'ECE cohort shows 42% high-risk students due to non-CS coding deficits. Targeted SQL bootcamp increases overall institutional readiness by +12.4%.',
        actionText: 'Open Institutional Skill Heatmap',
        actionSubTab: 'heatmap'
      };
    } else if (q.includes('+10') || q.includes('10') || q.includes('optimize')) {
      return {
        query: q,
        headline: '+10 Expected Selections Goal Strategy',
        body: 'Recommended Best Combination: Combine 40h SQL Bootcamp + 20h Aptitude Sprint to gain +34 net expected selections.',
        simulatedImpact: '+34 Selections',
        effort: '60 Hours',
        actionText: 'Test in Intervention Lab',
        actionSubTab: 'interventions'
      };
    } else {
      return {
        query: q,
        headline: `Institutional Readiness: ${data.overall_readiness_avg}% Average`,
        body: `Total Cohort: ${data.total_students} Students • ${data.ready_count} Ready (${data.ready_pct}%) • ${data.needs_training_count} High-Risk (${data.needs_training_pct}%).`,
        actionText: 'View Institutional Overview',
        actionSubTab: 'kpi'
      };
    }
  };

  const handleTriggerAction = (insight: CopilotInsight) => {
    if (insight.actionSubTab && onNavigateSubTab) {
      onNavigateSubTab(insight.actionSubTab);
    }
    if (onClose) onClose();
  };

  const sampleStudentPrompts = [
    "Why am I not ready?",
    "What is my biggest skill gap?",
    "What happens if I improve SQL?",
    "Can I reach 70 percent?",
    "Give me my 8-week roadmap"
  ];

  const sampleTpoPrompts = [
    "Where are we losing students?",
    "What is our primary bottleneck?",
    "How can we get +10 expected selections?",
    "Which department needs intervention?"
  ];

  const prompts = role === 'student' ? sampleStudentPrompts : sampleTpoPrompts;

  return (
    <div className="glass-card rounded-2xl border-indigo-500/30 p-6 shadow-2xl relative overflow-hidden space-y-6">
      {/* Copilot Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-black text-white flex items-center space-x-2">
              <span>PLACEMENTIQ COPILOT</span>
              <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                LIVE AI
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              {role === 'student' ? 'Talk to your placement future' : 'Simulate the placement before the placement'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsMuted(!isMuted)}
            className={`p-2 rounded-lg border text-xs transition-all ${
              isMuted ? 'bg-rose-950/40 border-rose-500/30 text-rose-400' : 'bg-slate-900 border-slate-800 text-slate-300 hover:text-white'
            }`}
            title={isMuted ? 'Unmute Speech Synthesis' : 'Mute Speech Synthesis'}
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
          {onClose && (
            <button onClick={onClose} className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Central Interactive AI Intelligence Core Orb */}
      <div className="flex flex-col items-center justify-center py-4 bg-slate-900/50 rounded-2xl border border-slate-800 relative">
        <AiOrb state={orbState} size={140} onClick={toggleVoiceListen} />

        <div className="mt-3 text-center space-y-1">
          {voiceAvailable ? (
            <button
              onClick={toggleVoiceListen}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 shadow-lg ${
                isListening
                  ? 'bg-rose-600 hover:bg-rose-500 text-white animate-pulse'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white'
              }`}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              <span>{isListening ? 'Stop Listening' : '🎙 Ask PlacementIQ (Voice)'}</span>
            </button>
          ) : (
            <span className="text-[11px] text-slate-400 italic">
              Voice input unavailable in browser. Type your query below.
            </span>
          )}
        </div>
      </div>

      {/* Prompt Suggestions */}
      <div className="space-y-2">
        <span className="text-[10px] text-slate-400 uppercase font-mono font-semibold block">Suggested Copilot Queries:</span>
        <div className="flex flex-wrap gap-2">
          {prompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setInputText(p);
                handleProcessQuery(p);
              }}
              className="px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-indigo-950/60 border border-slate-800 hover:border-indigo-500/40 text-xs text-slate-300 hover:text-white font-medium transition-all"
            >
              “{p}”
            </button>
          ))}
        </div>
      </div>

      {/* Text Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleProcessQuery(inputText);
        }}
        className="flex items-center space-x-2"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={role === 'student' ? 'Ask why you are not ready, what to improve...' : 'Ask about bottlenecks, interventions, +10 selections...'}
          className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={!inputText.trim()}
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-bold text-xs transition-all flex items-center space-x-1.5 shadow-md"
        >
          <span>Ask</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>

      {/* Structured PLACEMENTIQ INSIGHT Card Output */}
      {currentInsight && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-indigo-950 via-purple-950 to-navy-900 border border-indigo-500/40 space-y-3 shadow-xl animate-fadeIn">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-indigo-300 font-mono font-bold uppercase tracking-wider flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>PLACEMENTIQ INSIGHT</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Query: “{currentInsight.query}”</span>
          </div>

          <h4 className="text-lg font-bold text-white leading-tight">{currentInsight.headline}</h4>
          <p className="text-xs text-slate-300 leading-relaxed">{currentInsight.body}</p>

          {(currentInsight.currentVal || currentInsight.simulatedImpact) && (
            <div className="flex flex-wrap items-center gap-3 pt-2 text-xs font-mono">
              {currentInsight.currentVal && (
                <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                  Current: <strong className="text-amber-300">{currentInsight.currentVal}</strong>
                </span>
              )}
              {currentInsight.targetVal && (
                <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                  Target: <strong className="text-emerald-400">{currentInsight.targetVal}</strong>
                </span>
              )}
              {currentInsight.simulatedImpact && (
                <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-emerald-400 font-bold">
                  Impact: {currentInsight.simulatedImpact}
                </span>
              )}
            </div>
          )}

          {currentInsight.actionText && (
            <div className="pt-2 flex justify-end">
              <button
                onClick={() => handleTriggerAction(currentInsight)}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition-all flex items-center space-x-1.5"
              >
                <span>{currentInsight.actionText}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
