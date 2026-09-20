import React from 'react';
import { MapPin, Flag, Coffee, Camera, ArrowDown, Navigation, Sparkles, Info } from 'lucide-react';

export default function RouteTimeline({ routeDetails, origin, destination, travelMode }) {
  if (!routeDetails) return null;

  const stops = routeDetails.stops || [];
  const legs = routeDetails.legs || [];

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', background: '#ffffff' }}>
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: '#1e1b2e' }}>
            <Navigation size={20} color="#ec4899" />
            <span>Route Trajectory & Intermediate Stops</span>
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#6b7280', margin: '4px 0 0 0' }}>
            Visual progression from departure through scenic waypoints to destination
          </p>
        </div>
        <span className="badge badge-cyan" style={{ fontSize: '0.8rem' }}>
          Estimated Total: {routeDetails.total_estimated_distance}
        </span>
      </div>

      {/* Vertical Timeline container */}
      <div style={{ position: 'relative', paddingLeft: '28px', borderLeft: '2px dashed rgba(236, 72, 153, 0.3)', marginLeft: '12px' }}>
        
        {/* Origin Node */}
        <div style={{ position: 'relative', marginBottom: '32px' }}>
          <div style={{
            position: 'absolute', left: '-40px', top: '2px', width: '24px', height: '24px',
            borderRadius: '50%', background: 'var(--gradient-primary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 12px rgba(236, 72, 153, 0.5)'
          }}>
            <MapPin size={14} color="#ffffff" />
          </div>

          <div style={{ background: '#fdf2f8', padding: '14px 18px', borderRadius: '12px', border: '1px solid rgba(236, 72, 153, 0.15)' }}>
            <span className="badge badge-cyan" style={{ fontSize: '0.72rem', marginBottom: '4px' }}>ORIGIN / DEPARTURE</span>
            <h4 style={{ fontSize: '1.05rem', margin: '2px 0 4px 0', color: '#1e1b2e' }}>{origin}</h4>
            <p style={{ fontSize: '0.82rem', color: '#6b7280', margin: 0 }}>
              Commence journey. Check route conditions, fuel/battery level, and weather forecast before departure.
            </p>
          </div>
        </div>

        {/* Intermediate Legs & Stops */}
        {stops.map((stop, idx) => (
          <div key={idx} style={{ position: 'relative', marginBottom: '32px' }}>
            
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '6px',
              background: '#f9fafb', padding: '4px 10px', borderRadius: '6px',
              fontSize: '0.74rem', color: '#9ca3af', marginBottom: '10px'
            }}>
              <ArrowDown size={12} />
              <span>Transit segment (~{legs[idx]?.estimated_distance || 'Scenic stretch'} via {travelMode})</span>
            </div>

            <div style={{
              position: 'absolute', left: '-38px', top: '32px', width: '20px', height: '20px',
              borderRadius: '50%', background: '#f59e0b',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 10px rgba(245, 158, 11, 0.4)'
            }}>
              <Coffee size={12} color="#ffffff" />
            </div>

            <div style={{ background: '#fffbeb', padding: '14px 18px', borderRadius: '12px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '4px' }}>
                <span className="badge badge-amber" style={{ fontSize: '0.72rem' }}>WAYPOINT #{idx + 1}</span>
                <span style={{ fontSize: '0.76rem', color: '#b45309' }}>Recommended Stop: {stop.recommended_time_spent}</span>
              </div>
              <h4 style={{ fontSize: '1.05rem', margin: '2px 0 6px 0', color: '#1e1b2e' }}>{stop.name}</h4>
              <p style={{ fontSize: '0.84rem', color: '#6b7280', marginBottom: '8px' }}>{stop.description}</p>
              
              {stop.highlights && stop.highlights.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {stop.highlights.map((h, hIdx) => (
                    <span key={hIdx} style={{
                      fontSize: '0.72rem', background: 'rgba(245, 158, 11, 0.08)',
                      padding: '2px 8px', borderRadius: '6px', color: '#92400e'
                    }}>
                      • {h}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Destination Node */}
        <div style={{ position: 'relative' }}>
          <div style={{
            position: 'absolute', left: '-40px', top: '2px', width: '24px', height: '24px',
            borderRadius: '50%', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 12px rgba(16, 185, 129, 0.5)'
          }}>
            <Flag size={14} color="#ffffff" />
          </div>

          <div style={{ background: 'rgba(16, 185, 129, 0.06)', padding: '14px 18px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <span className="badge badge-emerald" style={{ fontSize: '0.72rem', marginBottom: '4px' }}>FINAL DESTINATION</span>
            <h4 style={{ fontSize: '1.05rem', margin: '2px 0 4px 0', color: '#059669' }}>{destination}</h4>
            <p style={{ fontSize: '0.82rem', color: '#6b7280', margin: 0 }}>
              Arrival and basecamp for multi-day exploration, dining, and curated activities.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
