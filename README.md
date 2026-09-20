# 🌍 Atlas AI: Travel Route Planning Agent

An intelligent, full-stack multi-modal AI Agent for **Travel Route Planning** built with **FastAPI**, **LangChain**, **Groq LLaMA-3.3-70b**, **Tavily Web Search**, a **React Dashboard UI** (~70%), and a **Gradio Conversational Interface** (~30%).

---

## 🏛️ Architecture Overview

```
                      +------------------------------------------+
                      |               USER / CLIENT              |
                      +--------------------+---------------------+
                                           |
                    +----------------------+---------------------+
                    |                                            |
                    v                                            v
         +---------------------+                      +---------------------+
         |   React Dashboard   |                      |  Gradio Chat Agent  |
         |      (~70% UI)      |                      |      (~30% UI)      |
         |  Port: 5173 (Vite)  |                      |     Port: 7860      |
         +----------+----------+                      +----------+----------+
                    |                                            |
                    | REST API (POST /api/plan, /api/chat)       | Direct / REST
                    v                                            v
         +------------------------------------------------------------------+
         |                       FastAPI Backend Service                     |
         |                     (backend/main.py, Port: 8000)                |
         +---------------------------------+--------------------------------+
                                           |
                                           v
         +------------------------------------------------------------------+
         |                    LangChain AI Travel Agent                      |
         |                   (Native Tool-Calling Loop)                     |
         |             LLM: Groq LLaMA-3.3-70b-versatile                     |
         +----+-------------------+-------------------+----------------+----+
              |                   |                   |                |
              v                   v                   v                v
      +---------------+   +---------------+   +---------------+  +---------------+
      | Tavily Search |   | Route Tool    |   | Budget Tool   |  | Itinerary Gen |
      |  (Live Web)   |   | (Dist & Time) |   | (Itemized)    |  |  (Day-Wise)   |
      +---------------+   +---------------+   +---------------+  +---------------+
```

---

## ✨ Features

- **Genuine LangChain AI Agent**: Utilizes modern tool-calling architecture where Groq decides when and which tools to call based on the user's travel parameters.
- **Real-Time Web Search via Tavily**: Scours live web information for up-to-date attractions, local dining gems, and seasonal travel advisories.
- **Multi-Modal Route Logic**: Calculates route metrics, road distance, and travel time across 5 modes: **Car**, **Scenic Train**, **Flight**, **Intercity Bus**, and **Bicycle Touring**.
- **Transparent Estimations**: Explicitly indicates algorithmic distance/time calculations vs web-search verified data.
- **Itemized Budget Visualizer**: Breakdowns across Lodging, Transport, Food, Experiences, and Contingency, scaling with traveler count and chosen budget tier.
- **Curated Day-Wise Itinerary**: Detailed Morning, Afternoon, and Evening slots with transit tips and stay recommendations.
- **Modern Glassmorphism UI (React ~70%)**: Dark luxury aesthetic, interactive timeline, responsive grid, and celebratory micro-interactions.
- **Conversational Agent UI (Gradio ~30%)**: Dedicated chat interface with memory for follow-up questions, route adjustments, and contingency planning.
- **Graceful Fallbacks**: Fully operational even before API keys are input, with direct tool synthesis and 1-click sample trip loaders.

---

## 📁 Project Directory Structure

```
AI-AGENT-FOR-TRAVEL-ROUTE-PLANNING/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI server, endpoints, CORS & sample plans
│   ├── agent.py             # LangChain tool-calling agent & Groq loop
│   ├── tools.py             # 4 tools: Tavily search, Route, Budget, Itinerary
│   ├── prompts.py           # System prompts for planner & conversational agent
│   ├── schemas.py           # Pydantic input/output schemas
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (Timeline, Itinerary, Budget, etc.)
│   │   ├── services/api.js  # REST client for FastAPI
│   │   ├── App.jsx          # Primary dashboard state & orchestration
│   │   ├── index.css        # Tailored modern travel design system
│   │   └── main.jsx         # React DOM entry
│   ├── index.html           # HTML template with Google Fonts
│   ├── package.json         # React + Vite dependencies
│   └── vite.config.js       # Vite build & server configuration
├── gradio/
│   └── app.py               # Gradio AI Travel Agent chat interface
├── .env.example             # Environment variables template
└── README.md                # Full documentation & setup guide
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** & **npm**

### 2. Environment Variables Setup
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

Edit `.env` and paste your API keys:
```env
# Groq API Key (Free from https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Tavily API Key (Free from https://tavily.com)
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# Optional: Default Model for Groq (default: llama-3.3-70b-versatile)
GROQ_MODEL=llama-3.3-70b-versatile

# Backend Port (default: 8000)
BACKEND_PORT=8000
```

> **Note:** If you run without keys or before adding them, the application automatically operates in simulated fallback mode so you can preview the full UI and route planner immediately.

---

### 3. Backend Setup & Run

Install Python dependencies:
```powershell
pip install -r backend/requirements.txt
```

Start the FastAPI backend server:
```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- **FastAPI API URL:** `http://localhost:8000`
- **Swagger Documentation:** `http://localhost:8000/docs`
- **Health Endpoint:** `http://localhost:8000/api/health`

---

### 4. Frontend Setup & Run (React Dashboard ~70%)

Navigate to the `frontend/` directory and install dependencies:
```powershell
cd frontend
npm install
```

Start the Vite development server:
```powershell
npm run dev
```
- **React Dashboard:** `http://localhost:5173`

---

### 5. Gradio Interface Run (Conversational Agent ~30%)

In a new terminal window from the project root:
```powershell
python gradio/app.py
```
- **Gradio Chat UI:** `http://localhost:7860`

---

## 🛠️ LangChain Agent Tools Explained

1. `search_travel_info(query: str)`:
   - Uses Tavily Web Search to gather live regional travel guidance, hidden attractions, local food specialties, and weather notes.
2. `calculate_route_details(origin: str, destination: str, travel_mode: str)`:
   - Computes estimated road or corridor distances using geographical algorithms, transit duration profiles by travel mode, and suggests scenic intermediate rest stops.
3. `estimate_trip_budget(total_budget: float, travelers: int, duration_days: int, travel_mode: str, destination: str)`:
   - Calculates itemized allocations across Accommodation, Transportation, Food & Dining, Sightseeing, and Emergency Buffer.
4. `generate_day_wise_itinerary(destination: str, days: int, interests: list, travel_mode: str)`:
   - Structures daily morning, afternoon, and evening blocks tailored to traveler interests.

---

## 🧪 Sample Queries to Try

### In the React Dashboard:
1. **Pacific Coast Road Trip**:
   - Origin: `San Francisco, CA`
   - Destination: `Los Angeles, CA`
   - Travel Mode: `Car / Road Trip`
   - Travelers: `2` | Budget: `$2,200`
   - Interests: `Nature, Beaches, Food, Photography`

2. **Tokyo to Kyoto Cultural Rail Journey**:
   - Origin: `Tokyo`
   - Destination: `Kyoto`
   - Travel Mode: `Scenic Train`
   - Travelers: `2` | Budget: `$3,500`
   - Interests: `Historical Places, Culture, Food`

### In the Gradio Chat Agent:
- *"Suggest scenic detour viewpoints along Big Sur."*
- *"Can you recommend top-rated authentic vegetarian food spots for our destination?"*
- *"What indoor activities do you recommend if it rains on Day 3?"*
- *"Compare taking the train vs driving in terms of travel time and scenery."*

---

## 🔒 Security & Best Practices
- Never commit your `.env` file to version control.
- Input validation is strictly enforced using Pydantic schemas.
- Full CORS configuration enables seamless communication between React on `localhost:5173` and FastAPI on `localhost:8000`.
