import React from 'react';
import { Compass, Utensils, Clock, Tag, Sparkles, DollarSign, Camera, Star } from 'lucide-react';

export default function PlacesCards({ places, foodAndActivities }) {
  const hasPlaces = places && places.length > 0;
  const hasFood = foodAndActivities && foodAndActivities.length > 0;

  if (!hasPlaces && !hasFood) return null;

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', background: '#ffffff' }}>
      
      {/* Places to Visit Section */}
      {hasPlaces && (
        <div style={{ marginBottom: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: '#1e1b2e' }}>
              <Compass size={20} color="#ec4899" />
              <span>Recommended Attractions & Places to Visit</span>
            </h3>
            <span className="badge badge-cyan" style={{ fontSize: '0.75rem' }}>
              <Sparkles size={12} /> Tavily Web-Search Verified
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {places.map((place, idx) => (
              <div key={idx} className="glass-panel-interactive" style={{
                background: '#fdf2f8', border: '1px solid rgba(236,72,153,0.1)',
                borderRadius: '14px', padding: '18px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span className="badge badge-cyan" style={{ fontSize: '0.72rem' }}>{place.category}</span>
                    {place.is_web_search_verified && (
                      <span title="Verified via Tavily live web search" style={{ fontSize: '0.75rem', color: '#be185d', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Sparkles size={12} /> Live Info
                      </span>
                    )}
                  </div>

                  <h4 style={{ fontSize: '1.1rem', margin: '0 0 6px 0', color: '#1e1b2e' }}>{place.name}</h4>
                  <p style={{ fontSize: '0.84rem', color: '#4b5563', margin: '0 0 12px 0', lineHeight: 1.5 }}>{place.description}</p>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.78rem', color: '#9ca3af', marginBottom: '10px' }}>
                    {place.best_time_to_visit && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={12} /> {place.best_time_to_visit}
                      </div>
                    )}
                    {place.estimated_entry_cost && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <DollarSign size={12} /> {place.estimated_entry_cost}
                      </div>
                    )}
                  </div>

                  {place.tags && place.tags.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {place.tags.map((t, tIdx) => (
                        <span key={tIdx} style={{
                          fontSize: '0.7rem', background: 'rgba(236,72,153,0.06)',
                          padding: '2px 8px', borderRadius: '12px', color: '#be185d'
                        }}>
                          #{t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Food & Dining Recommendations */}
      {hasFood && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: '#1e1b2e' }}>
              <Utensils size={20} color="#f59e0b" />
              <span>Local Culinary Highlights & Food Gems</span>
            </h3>
            <span className="badge badge-amber" style={{ fontSize: '0.75rem' }}>Regional Cuisine Guide</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {foodAndActivities.map((food, idx) => (
              <div key={idx} className="glass-panel-interactive" style={{
                background: '#fffbeb', border: '1px solid rgba(245,158,11,0.12)',
                borderRadius: '14px', padding: '18px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span className="badge badge-amber" style={{ fontSize: '0.72rem' }}>{food.type}</span>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#b45309' }}>{food.price_level || '$$'}</span>
                </div>

                <h4 style={{ fontSize: '1.05rem', margin: '0 0 6px 0', color: '#1e1b2e' }}>{food.name}</h4>
                <p style={{ fontSize: '0.84rem', color: '#4b5563', margin: '0 0 10px 0', lineHeight: 1.5 }}>{food.description}</p>

                {food.highlight_dish_or_experience && (
                  <div style={{
                    background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.15)',
                    borderRadius: '8px', padding: '8px 12px', fontSize: '0.78rem', color: '#92400e'
                  }}>
                    🍴 <strong>Must Try:</strong> {food.highlight_dish_or_experience}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
