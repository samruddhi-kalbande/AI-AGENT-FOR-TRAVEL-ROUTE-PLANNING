import React from 'react';
import { X, CheckCircle2, ShieldCheck, SunMedium, Compass } from 'lucide-react';

export default function TravelTipsModal({ isOpen, onClose, tips, destination }) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.35)', backdropFilter: 'blur(8px)',
      zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '560px', width: '100%', maxHeight: '80vh', overflowY: 'auto',
        padding: '28px', position: 'relative', background: '#ffffff', boxShadow: '0 25px 60px rgba(0,0,0,0.12)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Compass size={22} color="#ec4899" />
            <h3 style={{ fontSize: '1.25rem', margin: 0, color: '#1e1b2e' }}>Travel & Logistics Advice</h3>
          </div>
          <button type="button" onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <p style={{ fontSize: '0.88rem', color: '#6b7280', marginBottom: '18px' }}>
          Key recommendations synthesized by Atlas AI for safe and seamless travel to {destination || 'your destination'}:
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {tips && tips.map((tip, idx) => (
            <div key={idx} style={{
              display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '12px',
              background: '#fdf2f8', borderRadius: '10px', border: '1px solid rgba(236,72,153,0.1)'
            }}>
              <CheckCircle2 size={18} color="#ec4899" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span style={{ fontSize: '0.88rem', color: '#1e1b2e', lineHeight: 1.5 }}>{tip}</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '24px', textAlign: 'right' }}>
          <button type="button" className="btn-primary" onClick={onClose} style={{ padding: '8px 20px', fontSize: '0.88rem' }}>Got It</button>
        </div>
      </div>
    </div>
  );
}
