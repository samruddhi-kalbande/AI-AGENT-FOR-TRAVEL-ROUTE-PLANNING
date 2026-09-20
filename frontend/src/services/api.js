/**
 * API Service for communicating with the FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend offline or unreachable:', err.message);
    return {
      status: 'offline',
      api_keys_configured: { groq: false, tavily: false },
      mode: 'Offline / Unreachable'
    };
  }
}

export async function fetchSamplePlans() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/sample-plans`);
    if (!res.ok) throw new Error('Failed to fetch sample plans');
    return await res.json();
  } catch (err) {
    console.error('Error fetching sample plans:', err);
    return [];
  }
}

export async function planTrip(planRequest) {
  const res = await fetch(`${API_BASE_URL}/api/plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(planRequest)
  });

  if (!res.ok) {
    let errorDetail = 'Failed to generate travel route plan.';
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return await res.json();
}

export async function sendChatMessage(message, currentTrip = null, conversationHistory = []) {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      current_trip_plan: currentTrip,
      conversation_history: conversationHistory
    })
  });

  if (!res.ok) {
    let errorDetail = 'Agent chat failed.';
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return await res.json();
}
