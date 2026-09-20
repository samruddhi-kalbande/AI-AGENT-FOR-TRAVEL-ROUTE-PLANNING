import React from 'react';
import { GitFork, Check, X, Clock, Navigation } from 'lucide-react';

export default function AlternativeRoutes({ routes }) {
  if (!routes || routes.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', background: '#ffffff' }}>
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: '#1e1b2e' }}>
          <GitFork size={20} color="#ec4899" />
          <span>Alternative Route & Transit Options</span>
        </h3>
        <p style={{ fontSize: '0.85rem', color: '#6b7280', margin: '4px 0 0 0' }}>
          Evaluate scenic detours vs express corridors based on your transit preferences
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        {routes.map((alt, idx) => (
          <div key={idx} style={{
            background: '#fdf2f8', border: '1px solid rgba(236,72,153,0.1)',
            borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span className="badge badge-cyan" style={{ textTransform: 'capitalize' }}>{alt.travel_mode} Option</span>
                <span style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Clock size={13} /> {alt.estimated_time}
                </span>
              </div>

              <h4 style={{ fontSize: '1.1rem', margin: '0 0 8px 0', color: '#1e1b2e' }}>{alt.route_name}</h4>
              <p style={{ fontSize: '0.86rem', color: '#4b5563', marginBottom: '16px', lineHeight: 1.5 }}>{alt.summary}</p>

              {/* Pros */}
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#059669', textTransform: 'uppercase', marginBottom: '6px' }}>Advantages</div>
                {alt.pros.map((pro, pIdx) => (
                  <div key={pIdx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#374151', marginBottom: '4px' }}>
                    <Check size={14} color="#10b981" /> <span>{pro}</span>
                  </div>
                ))}
              </div>

              {/* Cons */}
              <div>
                <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#dc2626', textTransform: 'uppercase', marginBottom: '6px' }}>Trade-Offs</div>
                {alt.cons.map((con, cIdx) => (
                  <div key={cIdx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#6b7280', marginBottom: '4px' }}>
                    <X size={14} color="#ef4444" /> <span>{con}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(236,72,153,0.1)', fontSize: '0.75rem', color: '#9ca3af' }}>
              Distance: {alt.estimated_distance}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
