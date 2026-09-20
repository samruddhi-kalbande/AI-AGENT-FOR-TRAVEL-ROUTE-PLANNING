import React, { useState } from 'react';
import { Compass, Sparkles, Server, MessageSquare, Terminal, ChevronDown } from 'lucide-react';

export default function Navbar({ health, samplePlans, onLoadSample, onOpenTelemetry }) {
  const [showSamples, setShowSamples] = useState(false);

  const isLive = health?.api_keys_configured?.groq && health?.api_keys_configured?.tavily;

  return (
    <nav className="glass-panel" style={{ padding: '14px 24px', marginBottom: '28px', background: '#ffffff' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>

        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '42px', height: '42px', borderRadius: '12px',
            background: 'var(--gradient-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 18px rgba(236, 72, 153, 0.35)'
          }}>
            <Compass size={24} color="#fff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.4rem', fontWeight: 800, margin: 0, color: '#1e1b2e' }}>
                ATLAS <span className="gradient-text">AI</span>
              </h1>
              <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>LANGCHAIN AGENT</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: '#9ca3af', margin: 0 }}>Multi-Modal Travel Route & Itinerary Planner</p>
          </div>
        </div>

        {/* Right Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>

          {/* Status Indicator */}
          <div className="badge" style={{
            background: isLive ? 'rgba(16, 185, 129, 0.08)' : 'rgba(245, 158, 11, 0.08)',
            border: isLive ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(245, 158, 11, 0.25)',
            color: isLive ? '#059669' : '#b45309', padding: '6px 12px'
          }}>
            <span style={{
              width: '8px', height: '8px', borderRadius: '50%',
              backgroundColor: isLive ? '#10b981' : '#f59e0b',
              boxShadow: isLive ? '0 0 8px #10b981' : '0 0 8px #f59e0b',
              display: 'inline-block'
            }} />
            <span style={{ fontSize: '0.78rem' }}>
              {isLive ? 'Groq + Tavily Live' : 'Fallback Mode'}
            </span>
          </div>

          {/* Sample Trips Dropdown */}
          {samplePlans && samplePlans.length > 0 && (
            <div style={{ position: 'relative' }}>
              <button type="button" className="btn-secondary" onClick={() => setShowSamples(!showSamples)} style={{ fontSize: '0.85rem', padding: '8px 14px' }}>
                <Sparkles size={15} color="#ec4899" />
                <span>Sample Trips</span>
                <ChevronDown size={14} />
              </button>
              {showSamples && (
                <div className="glass-panel" style={{
                  position: 'absolute', top: '110%', right: 0, width: '280px', zIndex: 100,
                  padding: '8px', boxShadow: '0 20px 40px rgba(0,0,0,0.12)', background: '#ffffff'
                }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9ca3af', padding: '6px 10px', textTransform: 'uppercase' }}>
                    Quick Load Plans
                  </div>
                  {samplePlans.map((sample) => (
                    <button key={sample.id} type="button"
                      onClick={() => { onLoadSample(sample); setShowSamples(false); }}
                      style={{
                        display: 'block', width: '100%', textAlign: 'left', padding: '10px 12px',
                        borderRadius: '8px', background: 'transparent', border: 'none',
                        color: '#1e1b2e', cursor: 'pointer', transition: 'background 0.2s', fontSize: '0.85rem'
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#fdf2f8'}
                      onMouseLeave={(e) => e.target.style.background = 'transparent'}
                    >
                      <div style={{ fontWeight: 600 }}>{sample.name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                        {sample.origin} ➔ {sample.destination} ({sample.travel_mode})
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <button type="button" className="btn-secondary" onClick={onOpenTelemetry} title="View Agent Reasoning & Tool Calls" style={{ fontSize: '0.85rem', padding: '8px 12px' }}>
            <Terminal size={15} color="#8b5cf6" />
            <span>Agent Trace</span>
          </button>

          <a href="http://localhost:7860" target="_blank" rel="noopener noreferrer" className="btn-secondary"
            style={{ fontSize: '0.85rem', padding: '8px 14px', textDecoration: 'none', background: 'rgba(139, 92, 246, 0.08)', borderColor: 'rgba(139, 92, 246, 0.2)', color: '#7c3aed' }}>
            <MessageSquare size={15} />
            <span>Gradio Agent Chat</span>
          </a>
        </div>
      </div>
    </nav>
  );
}
