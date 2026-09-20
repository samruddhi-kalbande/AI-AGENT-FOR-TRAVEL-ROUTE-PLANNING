import React, { useState } from 'react';
import { CalendarDays, Sun, Sunset, Moon, Home, Bus, CheckCircle2, Sparkles, Layers } from 'lucide-react';

export default function ItineraryView({ itinerary }) {
  const [selectedDay, setSelectedDay] = useState(1);
  const [viewAll, setViewAll] = useState(false);

  if (!itinerary || itinerary.length === 0) return null;

  const currentDay = itinerary.find((d) => d.day_number === selectedDay) || itinerary[0];

  const renderSlotCard = (slot, icon, color, bgTint) => {
    if (!slot) return null;
    const IconComp = icon;

    return (
      <div style={{
        background: bgTint, border: '1px solid rgba(236, 72, 153, 0.08)',
        borderRadius: '14px', padding: '16px 20px', marginBottom: '12px', transition: 'all 0.2s ease'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '28px', height: '28px', borderRadius: '8px',
              background: `rgba(${color}, 0.12)`,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <IconComp size={16} color={`rgb(${color})`} />
            </div>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: `rgb(${color})`, textTransform: 'uppercase' }}>
              {slot.time_slot}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {slot.approximate_cost && (
              <span className="badge" style={{ background: 'rgba(236,72,153,0.06)', color: '#6b7280', fontSize: '0.72rem' }}>
                {slot.approximate_cost}
              </span>
            )}
            {slot.is_tavily_sourced && (
              <span className="badge badge-cyan" style={{ fontSize: '0.68rem' }}>
                <Sparkles size={11} /> Tavily Verified
              </span>
            )}
          </div>
        </div>

        <h4 style={{ fontSize: '1.02rem', margin: '0 0 6px 0', color: '#1e1b2e' }}>{slot.title}</h4>
        <p style={{ fontSize: '0.86rem', color: '#4b5563', margin: '0 0 8px 0', lineHeight: 1.55 }}>{slot.description}</p>

        {slot.location && (
          <div style={{ fontSize: '0.76rem', color: '#9ca3af' }}>
            📍 Location: {slot.location} {slot.estimated_duration ? `• Approx. ${slot.estimated_duration}` : ''}
          </div>
        )}
      </div>
    );
  };

  const renderDayContent = (day) => (
    <div key={day.day_number} style={{ marginBottom: '28px' }}>
      
      {/* Day Header Banner */}
      <div style={{
        background: 'linear-gradient(90deg, rgba(236, 72, 153, 0.08) 0%, #ffffff 100%)',
        borderLeft: '4px solid #ec4899', padding: '12px 18px',
        borderRadius: '0 12px 12px 0', marginBottom: '16px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px'
      }}>
        <div>
          <h3 style={{ fontSize: '1.18rem', margin: 0, color: '#1e1b2e' }}>{day.title}</h3>
          <span style={{ fontSize: '0.8rem', color: '#ec4899' }}>Theme: {day.theme}</span>
        </div>
        <span className="badge badge-cyan">Day {day.day_number}</span>
      </div>

      {/* Morning, Afternoon, Evening Slots */}
      {renderSlotCard(day.morning, Sun, '245, 158, 11', '#fffbeb')}
      {renderSlotCard(day.afternoon, Sunset, '236, 72, 153', '#fdf2f8')}
      {renderSlotCard(day.evening, Moon, '139, 92, 246', '#f5f3ff')}

      {/* Stay & Transport Tips */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', marginTop: '12px' }}>
        {day.stay_recommendation && (
          <div style={{
            background: 'rgba(139, 92, 246, 0.05)', border: '1px solid rgba(139, 92, 246, 0.15)',
            borderRadius: '10px', padding: '10px 14px', fontSize: '0.82rem',
            display: 'flex', alignItems: 'center', gap: '8px', color: '#4b5563'
          }}>
            <Home size={16} color="#8b5cf6" />
            <div><strong style={{ color: '#7c3aed' }}>Stay:</strong> {day.stay_recommendation}</div>
          </div>
        )}

        {day.local_transport_tip && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.15)',
            borderRadius: '10px', padding: '10px 14px', fontSize: '0.82rem',
            display: 'flex', alignItems: 'center', gap: '8px', color: '#4b5563'
          }}>
            <Bus size={16} color="#10b981" />
            <div><strong style={{ color: '#059669' }}>Transit Tip:</strong> {day.local_transport_tip}</div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', background: '#ffffff' }}>
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: '#1e1b2e' }}>
            <CalendarDays size={20} color="#ec4899" />
            <span>Day-Wise Curated Itinerary</span>
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#6b7280', margin: '4px 0 0 0' }}>
            Balanced morning, afternoon, and evening schedule with logistical guidance
          </p>
        </div>

        <button type="button" className="btn-secondary" onClick={() => setViewAll(!viewAll)} style={{ fontSize: '0.82rem', padding: '6px 14px' }}>
          <Layers size={14} />
          <span>{viewAll ? 'Show Tabs View' : 'Expand All Days'}</span>
        </button>
      </div>

      {/* Day Pills Bar */}
      {!viewAll && (
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '12px', marginBottom: '20px' }}>
          {itinerary.map((d) => {
            const isActive = selectedDay === d.day_number;
            return (
              <button key={d.day_number} type="button" onClick={() => setSelectedDay(d.day_number)} style={{
                padding: '8px 18px', borderRadius: '10px',
                border: isActive ? '1px solid #ec4899' : '1px solid rgba(236,72,153,0.15)',
                background: isActive ? 'var(--gradient-primary)' : '#ffffff',
                color: isActive ? '#ffffff' : '#1e1b2e', fontWeight: 700, fontSize: '0.85rem',
                cursor: 'pointer', whiteSpace: 'nowrap', transition: 'all 0.2s ease',
                boxShadow: isActive ? '0 2px 10px rgba(236, 72, 153, 0.3)' : 'none'
              }}>
                Day {d.day_number}
              </button>
            );
          })}
        </div>
      )}

      {viewAll ? itinerary.map((d) => renderDayContent(d)) : renderDayContent(currentDay)}
    </div>
  );
}
