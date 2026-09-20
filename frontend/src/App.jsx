import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  Compass,
  AlertCircle,
  Lightbulb,
  Sparkles,
  ArrowUpRight,
  Info
} from 'lucide-react';

import Navbar from './components/Navbar';
import TripForm from './components/TripForm';
import RouteSummary from './components/RouteSummary';
import RouteTimeline from './components/RouteTimeline';
import ItineraryView from './components/ItineraryView';
import BudgetSection from './components/BudgetSection';
import PlacesCards from './components/PlacesCards';
import AlternativeRoutes from './components/AlternativeRoutes';
import AgentLoader from './components/AgentLoader';
import AgentTelemetryModal from './components/AgentTelemetryModal';
import TravelTipsModal from './components/TravelTipsModal';

import { checkBackendHealth, fetchSamplePlans, planTrip } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [samplePlans, setSamplePlans] = useState([]);
  const [formValues, setFormValues] = useState(null);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTelemetry, setShowTelemetry] = useState(false);
  const [showTips, setShowTips] = useState(false);

  // Load initial backend health and sample plans
  useEffect(() => {
    async function init() {
      const h = await checkBackendHealth();
      setHealth(h);

      const samples = await fetchSamplePlans();
      setSamplePlans(samples);
    }
    init();
  }, []);

  const handlePlanSubmit = async (params) => {
    setIsLoading(true);
    setError(null);
    try {
      const plan = await planTrip(params);
      setCurrentPlan(plan);
      setFormValues(params);

      // Trigger celebratory confetti
      try {
        confetti({
          particleCount: 60,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (_) {}
    } catch (err) {
      setError(err.message || 'An unexpected error occurred while planning your trip.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadSample = (sample) => {
    setFormValues(sample);
    handlePlanSubmit(sample);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      alert('Trip URL copied to clipboard!');
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <Navbar
        health={health}
        samplePlans={samplePlans}
        onLoadSample={handleLoadSample}
        onOpenTelemetry={() => setShowTelemetry(true)}
      />

      {/* Main Grid: Form on Left (~35%), Plan Visualization on Right (~65%) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
        gap: '24px',
        alignItems: 'start'
      }}>
        
        {/* Left Column: Form & Key Tips */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <TripForm
            initialValues={formValues}
            onSubmit={handlePlanSubmit}
            isLoading={isLoading}
          />

          {/* Quick Guide Pill Card */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <Lightbulb size={18} color="#ec4899" />
              <h4 style={{ fontSize: '0.95rem', margin: 0, color: 'var(--text-main)' }}>
                How Atlas AI Plans Your Journey
              </h4>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0 0 10px 0', lineHeight: 1.5 }}>
              Atlas is a genuine LangChain agent with tool-calling capabilities:
            </p>
            <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <li><strong>Tavily Search:</strong> Scours live web information for authentic local food, hidden spots, and regional advisories.</li>
              <li><strong>Route Logic:</strong> Accurately estimates road/flight distances, transit durations, and scenic rest stops.</li>
              <li><strong>Budget Allocation:</strong> Calculates itemized breakdowns based on your traveler count and preferred travel style.</li>
            </ul>
          </div>
        </div>

        {/* Right Column: Loading State / Results */}
        <div>
          {isLoading && <AgentLoader />}

          {error && (
            <div className="glass-panel" style={{
              padding: '24px',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              background: 'rgba(239, 68, 68, 0.08)',
              marginBottom: '24px'
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <AlertCircle size={22} color="#f87171" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <h4 style={{ fontSize: '1.05rem', margin: '0 0 6px 0', color: '#fca5a5' }}>
                    Agent Planning Notice
                  </h4>
                  <p style={{ fontSize: '0.86rem', color: '#fecaca', margin: '0 0 12px 0' }}>
                    {error}
                  </p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                    Tip: Ensure your FastAPI backend is running on <code>http://localhost:8000</code> and keys in <code>.env</code> are formatted correctly.
                  </p>
                </div>
              </div>
            </div>
          )}

          {!isLoading && currentPlan && (
            <div>
              {/* Route Summary */}
              <RouteSummary
                plan={currentPlan}
                onPrint={handlePrint}
                onShare={handleShare}
              />

              {/* Route Trajectory & Timeline */}
              <RouteTimeline
                routeDetails={currentPlan.route_details}
                origin={currentPlan.origin}
                destination={currentPlan.destination}
                travelMode={currentPlan.travel_mode}
              />

              {/* Day-by-Day Itinerary */}
              <ItineraryView itinerary={currentPlan.itinerary} />

              {/* Budget Breakdown */}
              <BudgetSection
                budgetBreakdown={currentPlan.budget_breakdown}
                currency={currentPlan.currency}
                travelers={currentPlan.travelers}
                days={currentPlan.duration_days}
              />

              {/* Places to Visit & Food Gems */}
              <PlacesCards
                places={currentPlan.places_to_visit}
                foodAndActivities={currentPlan.food_and_activities}
              />

              {/* Alternative Routes */}
              <AlternativeRoutes routes={currentPlan.alternative_routes} />

              {/* Footer Travel Tips Button */}
              {currentPlan.travel_tips && currentPlan.travel_tips.length > 0 && (
                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setShowTips(true)}
                    style={{ padding: '12px 24px', fontSize: '0.9rem' }}
                  >
                    <Sparkles size={16} color="#ec4899" />
                    <span>View Complete Safety & Packing Tips</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

      </div>

      {/* Modals */}
      <AgentTelemetryModal
        isOpen={showTelemetry}
        onClose={() => setShowTelemetry(false)}
        plan={currentPlan}
      />

      <TravelTipsModal
        isOpen={showTips}
        onClose={() => setShowTips(false)}
        tips={currentPlan?.travel_tips}
        destination={currentPlan?.destination}
      />

    </div>
  );
}
