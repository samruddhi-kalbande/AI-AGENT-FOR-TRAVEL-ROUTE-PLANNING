"""
FastAPI Server for Travel Route Planning AI Agent.
Provides REST API endpoints for React frontend and Gradio agent interface.
"""

import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from backend.schemas import (
    TripPlanRequest,
    TripPlanResponse,
    ChatQueryRequest,
    ChatQueryResponse
)
from backend.agent import plan_trip, chat_with_agent

app = FastAPI(
    title="Atlas - Travel Route Planning AI Agent",
    description="Intelligent AI Agent for multi-modal travel route planning, powered by LangChain, Groq, and Tavily.",
    version="1.0.0"
)

# CORS middleware configuration allowing React frontend (Vite port 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Atlas Travel Route Planning AI Agent API is running.",
        "documentation": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
def health_check():
    """Returns server status and API key detection status."""
    groq_set = bool(os.environ.get("GROQ_API_KEY") and os.environ.get("GROQ_API_KEY") != "your_groq_api_key_here")
    tavily_set = bool(os.environ.get("TAVILY_API_KEY") and os.environ.get("TAVILY_API_KEY") != "your_tavily_api_key_here")

    return {
        "status": "healthy",
        "api_keys_configured": {
            "groq": groq_set,
            "tavily": tavily_set
        },
        "mode": "Live Groq + Tavily Agent" if (groq_set and tavily_set) else "Simulated Agent / Fallback Tool Mode",
        "instruction": "Set GROQ_API_KEY and TAVILY_API_KEY in .env for live Groq LLM reasoning and real-time Tavily search."
    }


@app.post("/api/plan", response_model=TripPlanResponse)
def create_trip_plan(request: TripPlanRequest):
    """
    Executes the LangChain Travel Agent to create a complete, structured travel route plan.
    """
    try:
        response = plan_trip(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Travel Route Planning Agent encountered an error: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatQueryResponse)
def agent_chat(request: ChatQueryRequest):
    """
    Handles interactive conversational follow-ups and itinerary modifications.
    """
    try:
        reply, tool_logs = chat_with_agent(
            message=request.message,
            current_trip=request.current_trip_plan,
            history=request.conversation_history
        )
        return ChatQueryResponse(
            reply=reply,
            modified_trip_plan=None,
            tool_calls_made=tool_logs
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversational Agent error: {str(e)}"
        )


@app.get("/api/sample-plans")
def get_sample_plans() -> List[Dict[str, Any]]:
    """
    Provides curated sample trip parameters for quick 1-click loading in the UI.
    """
    return [
        {
            "id": "pacific_coast",
            "name": "Pacific Coast Highway Road Trip",
            "origin": "San Francisco, CA",
            "destination": "Los Angeles, CA",
            "departure_date": "2025-07-10",
            "return_date": "2025-07-15",
            "trip_duration_days": 6,
            "travelers": 2,
            "budget": 2200,
            "currency": "USD",
            "travel_mode": "car",
            "interests": ["nature", "beaches", "scenic drives", "food", "photography"],
            "custom_notes": "We love coastal cliff views, stops at Big Sur, and fresh seafood restaurants."
        },
        {
            "id": "tokyo_kyoto",
            "name": "Tokyo to Kyoto Cultural Express",
            "origin": "Tokyo",
            "destination": "Kyoto",
            "departure_date": "2025-09-05",
            "return_date": "2025-09-12",
            "trip_duration_days": 8,
            "travelers": 2,
            "budget": 3500,
            "currency": "USD",
            "travel_mode": "train",
            "interests": ["historical places", "culture", "food", "photography", "temples"],
            "custom_notes": "Keen to ride the Shinkansen Bullet Train, explore ancient shrines, and eat local ramen & matcha."
        },
        {
            "id": "alpine_adventure",
            "name": "Swiss Alpine Mountain Escape",
            "origin": "Zurich",
            "destination": "Zermatt",
            "departure_date": "2025-08-01",
            "return_date": "2025-08-06",
            "trip_duration_days": 6,
            "travelers": 2,
            "budget": 4000,
            "currency": "USD",
            "travel_mode": "train",
            "interests": ["adventure", "nature", "hiking", "photography"],
            "custom_notes": "Scenic cogwheel trains, views of Matterhorn, alpine fondue."
        }
    ]


# ─── Mount Gradio Conversational Agent ─────────────────────────────────────────
try:
    import gradio as gr
    from gradio_ui.app import demo as gradio_demo
    app = gr.mount_gradio_app(app, gradio_demo, path="/chat")
    print("✅ Gradio Conversational Agent mounted at /chat")
except Exception as e:
    print(f"Notice: Gradio mount skipped: {e}")


# ─── Mount Frontend Production Build (Single Web Service) ──────────────────────
from fastapi.staticfiles import StaticFiles
from pathlib import Path

dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend_spa")
    print("✅ React Frontend static SPA mounted at /")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", os.environ.get("BACKEND_PORT", 8000)))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
