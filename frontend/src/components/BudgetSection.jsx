import React from 'react';
import { Wallet, PiggyBank, Hotel, Car, Utensils, Ticket, ShieldAlert, Lightbulb, CheckCircle2 } from 'lucide-react';

const CATEGORY_COLORS = {
  'Accommodation & Lodging': '#8b5cf6',
  'Transportation & Fuel/Transit': '#ec4899',
  'Food & Local Dining': '#10b981',
  'Sightseeing & Experiences': '#f59e0b',
  'Contingency & Souvenirs': '#06b6d4'
};

const CATEGORY_ICONS = {
  'Hotel': Hotel, 'Car': Car, 'Utensils': Utensils, 'Ticket': Ticket, 'ShieldAlert': ShieldAlert
};

export default function BudgetSection({ budgetBreakdown, currency, travelers, days }) {
  if (!budgetBreakdown) return null;

  const categories = budgetBreakdown.categories || [];
  const tips = budgetBreakdown.saving_tips || [];

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', background: '#ffffff' }}>
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: '#1e1b2e' }}>
            <Wallet size={20} color="#ec4899" />
            <span>Budget Estimation & Category Breakdown</span>
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#6b7280', margin: '4px 0 0 0' }}>
            Allocated across {travelers} traveler{travelers > 1 ? 's' : ''} for {days} days
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-violet" style={{ fontSize: '0.82rem', padding: '6px 12px' }}>
            Tier: {budgetBreakdown.budget_tier}
          </span>
          <span className="badge badge-emerald" style={{ fontSize: '0.82rem', padding: '6px 12px' }}>
            {currency} {budgetBreakdown.per_person_budget?.toLocaleString()} / person
          </span>
        </div>
      </div>

      {/* Multi-segment Progress Bar */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden',
          background: '#f3f4f6', border: '1px solid rgba(236,72,153,0.1)',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)'
        }}>
          {categories.map((cat, idx) => {
            const color = CATEGORY_COLORS[cat.category] || '#ec4899';
            return (
              <div key={idx} title={`${cat.category}: ${cat.percentage}% (${currency} ${cat.allocated_amount})`}
                style={{ width: `${cat.percentage}%`, background: color, transition: 'width 0.4s ease' }} />
            );
          })}
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '14px', marginTop: '10px', fontSize: '0.78rem' }}>
          {categories.map((cat, idx) => {
            const color = CATEGORY_COLORS[cat.category] || '#ec4899';
            return (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '3px', background: color }} />
                <span style={{ color: '#6b7280' }}>{cat.category}</span>
                <span style={{ fontWeight: 700, color: '#1e1b2e' }}>{cat.percentage}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Itemized Category Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginBottom: '22px' }}>
        {categories.map((cat, idx) => {
          const color = CATEGORY_COLORS[cat.category] || '#ec4899';
          const IconComp = CATEGORY_ICONS[cat.icon] || PiggyBank;

          return (
            <div key={idx} style={{
              background: '#fdf2f8', border: '1px solid rgba(236,72,153,0.1)',
              borderTop: `3px solid ${color}`, borderRadius: '12px', padding: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <IconComp size={16} color={color} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#1e1b2e' }}>
                    {cat.category.split('&')[0]}
                  </span>
                </div>
                <span style={{ fontSize: '1rem', fontWeight: 700, color: color }}>
                  {currency} {cat.allocated_amount?.toLocaleString()}
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#6b7280', margin: 0, lineHeight: 1.45 }}>
                {cat.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Money Saving Tips */}
      {tips.length > 0 && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.15)',
          borderRadius: '12px', padding: '16px 20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
            <Lightbulb size={18} color="#f59e0b" />
            <h4 style={{ fontSize: '0.95rem', margin: 0, color: '#b45309' }}>Agent Budget Optimization Tips</h4>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '8px' }}>
            {tips.map((tip, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.82rem', color: '#4b5563' }}>
                <CheckCircle2 size={14} color="#10b981" style={{ flexShrink: 0, marginTop: '3px' }} />
                <span>{tip}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
