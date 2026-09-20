import React, { useState } from 'react';
import { MapPin, Calendar, Users, DollarSign, Car, Bike, Bus, Train, Plane, Heart, FileText, Sparkles, ArrowRight } from 'lucide-react';

const TRAVEL_MODES = [
  { id: 'car', label: 'Car / Road Trip', icon: Car },
  { id: 'train', label: 'Scenic Train', icon: Train },
  { id: 'flight', label: 'Flight', icon: Plane },
  { id: 'bus', label: 'Intercity Bus', icon: Bus },
  { id: 'bike', label: 'Bicycle Touring', icon: Bike },
];

const INTEREST_OPTIONS = [
  { id: 'nature', label: '🌲 Nature & Parks' }, { id: 'food', label: '🍜 Local Food & Dining' },
  { id: 'historical places', label: '🏛️ Historical Sites' }, { id: 'beaches', label: '🏖️ Beaches & Coastal' },
  { id: 'adventure', label: '🧗 Adventure & Hiking' }, { id: 'shopping', label: '🛍️ Shopping & Bazaars' },
  { id: 'photography', label: '📸 Photography Spots' }, { id: 'nightlife', label: '🍸 Nightlife & Cafes' },
  { id: 'culture', label: '🎭 Arts & Culture' }, { id: 'wellness', label: '🧘 Wellness & Spa' }
];

export default function TripForm({ initialValues, onSubmit, isLoading }) {
  const [origin, setOrigin] = useState(initialValues?.origin || '');
  const [destination, setDestination] = useState(initialValues?.destination || '');
  const [departureDate, setDepartureDate] = useState(initialValues?.departure_date || '');
  const [returnDate, setReturnDate] = useState(initialValues?.return_date || '');
  const [travelers, setTravelers] = useState(initialValues?.travelers || 2);
  const [budget, setBudget] = useState(initialValues?.budget || 1500);
  const [currency, setCurrency] = useState(initialValues?.currency || 'USD');
  const [travelMode, setTravelMode] = useState(initialValues?.travel_mode || 'car');
  const [interests, setInterests] = useState(initialValues?.interests || ['nature', 'food']);
  const [customNotes, setCustomNotes] = useState(initialValues?.custom_notes || '');

  React.useEffect(() => {
    if (initialValues) {
      if (initialValues.origin) setOrigin(initialValues.origin);
      if (initialValues.destination) setDestination(initialValues.destination);
      if (initialValues.departure_date) setDepartureDate(initialValues.departure_date);
      if (initialValues.return_date) setReturnDate(initialValues.return_date);
      if (initialValues.travelers) setTravelers(initialValues.travelers);
      if (initialValues.budget) setBudget(initialValues.budget);
      if (initialValues.currency) setCurrency(initialValues.currency);
      if (initialValues.travel_mode) setTravelMode(initialValues.travel_mode);
      if (initialValues.interests) setInterests(initialValues.interests);
      if (initialValues.custom_notes) setCustomNotes(initialValues.custom_notes);
    }
  }, [initialValues]);

  const toggleInterest = (id) => {
    if (interests.includes(id)) setInterests(interests.filter((item) => item !== id));
    else setInterests([...interests, id]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ origin, destination, departure_date: departureDate, return_date: returnDate, travelers: Number(travelers), budget: Number(budget), currency, travel_mode: travelMode, interests, custom_notes: customNotes });
  };

  const labelStyle = { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px', color: '#1e1b2e' };

  return (
    <div className="glass-panel" style={{ padding: '28px', background: '#ffffff' }}>
      <div style={{ marginBottom: '22px' }}>
        <h2 style={{ fontSize: '1.45rem', display: 'flex', alignItems: 'center', gap: '10px', color: '#1e1b2e' }}>
          <Sparkles size={22} color="#ec4899" />
          <span>Plan Your Route with AI Agent</span>
        </h2>
        <p style={{ fontSize: '0.88rem', color: '#6b7280' }}>Atlas uses LangChain tools to research attractions, compute routes, and balance your budget.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px', marginBottom: '20px' }}>
          <div>
            <label style={labelStyle}><MapPin size={16} color="#ec4899" /> Starting Location</label>
            <input type="text" required value={origin} onChange={(e) => setOrigin(e.target.value)} placeholder="e.g. San Francisco, CA" />
          </div>
          <div>
            <label style={labelStyle}><MapPin size={16} color="#be185d" /> Destination</label>
            <input type="text" required value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="e.g. Los Angeles, CA" />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '18px', marginBottom: '20px' }}>
          <div>
            <label style={labelStyle}><Calendar size={16} color="#ec4899" /> Departure Date</label>
            <input type="date" required value={departureDate} onChange={(e) => setDepartureDate(e.target.value)} />
          </div>
          <div>
            <label style={labelStyle}><Calendar size={16} color="#be185d" /> Return Date</label>
            <input type="date" value={returnDate} onChange={(e) => setReturnDate(e.target.value)} />
          </div>
          <div>
            <label style={labelStyle}><Users size={16} color="#ec4899" /> Travelers</label>
            <input type="number" min="1" max="25" value={travelers} onChange={(e) => setTravelers(e.target.value)} />
          </div>
          <div>
            <label style={labelStyle}><DollarSign size={16} color="#be185d" /> Total Budget</label>
            <div style={{ display: 'flex', gap: '6px' }}>
              <select value={currency} onChange={(e) => setCurrency(e.target.value)} style={{ width: '85px', padding: '12px 8px' }}>
                <option value="USD">USD ($)</option><option value="EUR">EUR (€)</option><option value="GBP">GBP (£)</option><option value="INR">INR (₹)</option><option value="CAD">CAD ($)</option>
              </select>
              <input type="number" min="50" step="50" value={budget} onChange={(e) => setBudget(e.target.value)} />
            </div>
          </div>
        </div>

        {/* Travel Mode */}
        <div style={{ marginBottom: '22px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px', color: '#1e1b2e' }}>Choose Travel Mode</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
            {TRAVEL_MODES.map((mode) => {
              const IconComp = mode.icon;
              const isSelected = travelMode === mode.id;
              return (
                <button key={mode.id} type="button" onClick={() => setTravelMode(mode.id)} style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', padding: '12px 10px', borderRadius: '12px',
                  border: isSelected ? '2px solid #ec4899' : '1px solid rgba(236,72,153,0.15)',
                  background: isSelected ? '#fdf2f8' : '#ffffff',
                  color: isSelected ? '#be185d' : '#6b7280', cursor: 'pointer', transition: 'all 0.2s ease',
                  boxShadow: isSelected ? '0 0 15px rgba(236,72,153,0.15)' : 'none'
                }}>
                  <IconComp size={22} color={isSelected ? '#ec4899' : '#9ca3af'} />
                  <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>{mode.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Interests */}
        <div style={{ marginBottom: '22px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px', color: '#1e1b2e' }}>
            <Heart size={16} color="#ec4899" /> Interests & Preferences
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {INTEREST_OPTIONS.map((item) => {
              const active = interests.includes(item.id);
              return (
                <button key={item.id} type="button" onClick={() => toggleInterest(item.id)} style={{
                  padding: '7px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: 500, cursor: 'pointer', transition: 'all 0.2s ease',
                  background: active ? '#fce7f3' : '#f9fafb',
                  border: active ? '1px solid #f9a8d4' : '1px solid #e5e7eb',
                  color: active ? '#be185d' : '#6b7280'
                }}>
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={labelStyle}><FileText size={16} color="#9ca3af" /> Custom Notes (Optional)</label>
          <input type="text" value={customNotes} onChange={(e) => setCustomNotes(e.target.value)} placeholder="e.g. Prefer dog-friendly hotels, vegetarian food, scenic passes" />
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading} style={{ width: '100%', padding: '15px' }}>
          {isLoading ? <span>Agent Planning Route...</span> : <><span>Generate AI Route Plan</span><ArrowRight size={18} /></>}
        </button>
      </form>
    </div>
  );
}
