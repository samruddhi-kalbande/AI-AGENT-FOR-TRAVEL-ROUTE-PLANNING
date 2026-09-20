import React from 'react';
import { MapPin, Clock, Navigation, Calendar, Users, Wallet, ShieldCheck, Printer, Share2, ExternalLink } from 'lucide-react';

export default function RouteSummary({ plan, onPrint, onShare }) {
  if (!plan) return null;

  return (
    <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', background: '#ffffff' }}>
      
      {/* Top Banner with Badges */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <span className="badge badge-emerald">
              <ShieldCheck size={13} /> {plan.duration_days} DAYS ITINERARY
            </span>
            <span className="badge badge-cyan" style={{ textTransform: 'capitalize' }}>
              Mode: {plan.travel_mode}
            </span>
            <span className="badge badge-amber">
              {plan.budget_breakdown?.budget_tier || 'Balanced Tier'}
            </span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: '#1e1b2e' }}>
            {plan.trip_title}
          </h2>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button type="button" className="btn-secondary" onClick={onPrint} title="Print or Save PDF">
            <Printer size={15} /> <span>Print</span>
          </button>
          <button type="button" className="btn-secondary" onClick={onShare} title="Share or Copy Link">
            <Share2 size={15} /> <span>Share</span>
          </button>
        </div>
      </div>

      {/* Overview Paragraph */}
      <p style={{ fontSize: '0.98rem', color: '#374151', marginBottom: '22px', lineHeight: 1.65 }}>
        {plan.overview}
      </p>

      {/* Metrics Row */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px',
        background: '#fdf2f8', padding: '18px', borderRadius: '14px',
        border: '1px solid rgba(236, 72, 153, 0.12)', marginBottom: '20px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#9ca3af', marginBottom: '4px' }}>
            <Navigation size={14} color="#ec4899" /> <span>ESTIMATED DISTANCE</span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#be185d' }}>
            {plan.route_details?.total_estimated_distance || 'Direct Route'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Algorithmic transit estimation</div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#9ca3af', marginBottom: '4px' }}>
            <Clock size={14} color="#10b981" /> <span>TRANSIT TIME</span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#059669' }}>
            {plan.route_details?.total_estimated_duration || 'Approx. 4-6h'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Excluding custom stops</div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#9ca3af', marginBottom: '4px' }}>
            <Calendar size={14} color="#f59e0b" /> <span>DATES & TIMELINE</span>
          </div>
          <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#1e1b2e' }}>
            {plan.departure_date}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
            {plan.return_date ? `To ${plan.return_date}` : `${plan.duration_days} days total`}
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#9ca3af', marginBottom: '4px' }}>
            <Wallet size={14} color="#8b5cf6" /> <span>BUDGET & TRAVELERS</span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#7c3aed' }}>
            {plan.currency} {plan.total_budget?.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
            For {plan.travelers} traveler{plan.travelers > 1 ? 's' : ''} ({plan.currency} {Math.round(plan.total_budget / (plan.travelers || 1)).toLocaleString()}/person)
          </div>
        </div>
      </div>

      {/* Transparency Note */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: 'rgba(236, 72, 153, 0.05)', border: '1px solid rgba(236, 72, 153, 0.15)',
        borderRadius: '10px', padding: '10px 14px', fontSize: '0.8rem', color: '#6b7280',
        flexWrap: 'wrap', gap: '8px'
      }}>
        <span>
          ℹ️ <strong>Data Transparency:</strong> {plan.route_details?.estimation_disclaimer || 'Distances are estimated via mathematical road models.'}
        </span>
        <span style={{ color: '#be185d', fontWeight: 600 }}>
          {plan.data_sources?.web_search?.includes('Live') ? '🟢 Live Tavily Verified' : '🔍 Tavily Search Integrated'}
        </span>
      </div>
    </div>
  );
}
