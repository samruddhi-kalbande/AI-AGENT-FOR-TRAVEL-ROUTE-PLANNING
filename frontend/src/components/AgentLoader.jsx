import React, { useState, useEffect } from 'react';
import { Compass, Search, Calculator, Calendar, BrainCircuit, Check } from 'lucide-react';

const STEPS = [
  { id: 1, title: 'Route Calculation Tool', desc: 'Evaluating distance, road physics & intermediate stops...', icon: Compass },
  { id: 2, title: 'Tavily Search Tool', desc: 'Querying real-time attractions, local dining & conditions...', icon: Search },
  { id: 3, title: 'Budget Estimation Tool', desc: 'Itemizing lodging, transport, dining & buffer splits...', icon: Calculator },
  { id: 4, title: 'Itinerary Generation Tool', desc: 'Synthesizing morning, afternoon & evening daily schedule...', icon: Calendar },
  { id: 5, title: 'Groq LLaMA-3.3 Agent', desc: 'Harmonizing recommendations into final structured plan...', icon: BrainCircuit }
];

export default function AgentLoader() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel" style={{
      padding: '48px 32px',
      margin: '40px auto',
      maxWidth: '650px',
      textAlign: 'center',
      boxShadow: 'var(--shadow-card), var(--shadow-glow)'
    }}>
      {/* Animated Center Orb */}
      <div style={{
        width: '76px',
        height: '76px',
        margin: '0 auto 24px auto',
        borderRadius: '50%',
        background: 'var(--gradient-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 0 35px rgba(236, 72, 153, 0.45)'
      }} className="animate-pulse-subtle">
        <Compass size={40} color="#ffffff" className="animate-spin-slow" />
      </div>

      <h3 style={{ fontSize: '1.5rem', marginBottom: '8px', color: '#1e1b2e' }}>
        Atlas AI Agent at Work
      </h3>
      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '32px' }}>
        Executing LangChain tool-calling workflow with Groq reasoning and Tavily live search...
      </p>

      {/* Stepper Display */}
      <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {STEPS.map((step, idx) => {
          const IconComp = step.icon;
          const isDone = idx < activeStep;
          const isCurrent = idx === activeStep;

          return (
            <div
              key={step.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                padding: '12px 16px',
                borderRadius: '12px',
                background: isCurrent ? 'rgba(236, 72, 153, 0.08)' : isDone ? 'rgba(16, 185, 129, 0.06)' : '#fff1f5',
                border: isCurrent ? '1px solid var(--pink-bright)' : isDone ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(236, 72, 153, 0.12)',
                transition: 'all 0.3s ease'
              }}
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: isDone ? '#10b981' : isCurrent ? 'var(--pink-bright)' : 'rgba(236, 72, 153, 0.15)',
                color: isDone || isCurrent ? '#ffffff' : '#be185d'
              }}>
                {isDone ? <Check size={16} strokeWidth={3} /> : <IconComp size={16} />}
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.88rem', fontWeight: 600, color: isCurrent ? '#be185d' : isDone ? '#059669' : 'var(--text-main)' }}>
                  {step.title}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  {step.desc}
                </div>
              </div>

              {isCurrent && (
                <div className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                  Processing
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
