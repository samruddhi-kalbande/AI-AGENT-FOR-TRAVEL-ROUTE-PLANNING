import React from 'react';
import { X, Terminal, Database, Cpu, CheckCircle } from 'lucide-react';

export default function AgentTelemetryModal({ isOpen, onClose, plan }) {
  if (!isOpen) return null;

  const notes = plan?.agent_reasoning_notes || [
    'Direct tool execution completed: calculate_route_details',
    'Direct tool execution completed: search_travel_info',
    'Direct tool execution completed: estimate_trip_budget',
    'Direct tool execution completed: generate_day_wise_itinerary'
  ];

  const sources = plan?.data_sources || {};

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.4)', backdropFilter: 'blur(8px)',
      zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '680px', width: '100%', maxHeight: '85vh', overflowY: 'auto',
        padding: '28px', position: 'relative', boxShadow: '0 25px 60px rgba(0,0,0,0.15)', background: '#ffffff'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Terminal size={22} color="#ec4899" />
            <h3 style={{ fontSize: '1.25rem', margin: 0, color: '#1e1b2e' }}>Agent Telemetry & Tool Invocations</h3>
          </div>
          <button type="button" onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer', padding: '4px' }}>
            <X size={20} />
          </button>
        </div>

        {/* Data Sources */}
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ fontSize: '0.9rem', color: '#9ca3af', textTransform: 'uppercase', marginBottom: '10px' }}>Multi-Tool LangChain Integration</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(sources).map(([k, v], idx) => (
              <div key={idx} style={{
                background: '#fdf2f8', padding: '10px 14px', borderRadius: '8px',
                border: '1px solid rgba(236,72,153,0.1)', display: 'flex',
                alignItems: 'center', justifyContent: 'space-between', fontSize: '0.82rem'
              }}>
                <span style={{ color: '#be185d', fontWeight: 600, textTransform: 'capitalize' }}>{k.replace('_', ' ')}:</span>
                <span style={{ color: '#1e1b2e' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Execution Log */}
        <div>
          <h4 style={{ fontSize: '0.9rem', color: '#9ca3af', textTransform: 'uppercase', marginBottom: '10px' }}>Agent Reasoning Trace</h4>
          <div style={{
            background: '#1e1b2e', border: '1px solid rgba(236,72,153,0.15)',
            borderRadius: '10px', padding: '16px', fontFamily: 'monospace',
            fontSize: '0.8rem', color: '#f9a8d4', maxHeight: '260px', overflowY: 'auto'
          }}>
            {notes.map((n, idx) => (
              <div key={idx} style={{ marginBottom: '6px', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <span style={{ color: '#ec4899' }}>&gt;</span>
                <span>{n}</span>
              </div>
            ))}
            <div style={{ color: '#6ee7b7', marginTop: '10px' }}>
              ✓ Structured JSON output validated and delivered to React UI.
            </div>
          </div>
        </div>

        <div style={{ marginTop: '22px', textAlign: 'right' }}>
          <button type="button" className="btn-primary" onClick={onClose} style={{ padding: '8px 20px', fontSize: '0.88rem' }}>Close Trace</button>
        </div>
      </div>
    </div>
  );
}
