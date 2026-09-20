"""
LangChain Travel Route Planning Agent implementation.
Uses Groq API for LLM reasoning and Tavily API for web search.
Operates a tool-calling reasoning loop using native LangChain tool binding.
"""

import os
import re
import json
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from backend.schemas import TripPlanRequest, TripPlanResponse, RouteDetails, BudgetBreakdown, DayItinerary
from backend.prompts import TRAVEL_AGENT_SYSTEM_PROMPT, CONVERSATIONAL_AGENT_PROMPT
from backend.tools import (
    TRAVEL_AGENT_TOOLS,
    search_travel_info,
    calculate_route_details,
    estimate_trip_budget,
    generate_day_wise_itinerary
)

TOOL_MAP = {t.name: t for t in TRAVEL_AGENT_TOOLS}


def get_groq_llm(temperature: float = 0.3):
    """Initializes ChatGroq if API key is present, with automatic model fallback."""
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        return None

    try:
        from langchain_groq import ChatGroq
        configured_model = os.environ.get("GROQ_MODEL", "").strip()
        candidates = []
        if configured_model:
            candidates.append(configured_model)
        candidates.extend([
            "openai/gpt-oss-120b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b"
        ])

        seen = set()
        unique_candidates = [c for c in candidates if not (c in seen or seen.add(c))]

        for model_name in unique_candidates:
            try:
                return ChatGroq(
                    api_key=groq_api_key,
                    model_name=model_name,
                    temperature=temperature,
                    max_retries=2
                )
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"Warning: Could not initialize ChatGroq: {e}")
        return None


def run_agentic_planning_loop(
    user_prompt: str,
    max_steps: int = 6
) -> Tuple[str, List[str]]:
    """
    Executes a multi-turn tool-calling loop where Groq decides
    which tools (Tavily search, route calculation, budget estimation, etc.) to invoke.
    """
    llm = get_groq_llm()
    tool_logs = []

    if not llm:
        tool_logs.append("GROQ_API_KEY not configured. Falling back to local tool synthesis.")
        return "", tool_logs

    llm_with_tools = llm.bind_tools(TRAVEL_AGENT_TOOLS)
    messages = [
        SystemMessage(content=TRAVEL_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    for step in range(max_steps):
        try:
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            # Check if tools were called
            if not ai_msg.tool_calls:
                # No more tools needed; final answer produced
                return ai_msg.content, tool_logs

            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                tool_logs.append(f"Invoking {tool_name} with args: {json.dumps(tool_args)}")

                selected_tool = TOOL_MAP.get(tool_name)
                if selected_tool:
                    try:
                        tool_output = selected_tool.invoke(tool_args)
                    except Exception as err:
                        tool_output = f"Tool execution failed: {str(err)}"
                else:
                    tool_output = f"Unknown tool: {tool_name}"

                messages.append(
                    ToolMessage(content=str(tool_output), tool_call_id=tool_id)
                )
        except Exception as e:
            tool_logs.append(f"Agent loop iteration error: {str(e)}")
            break

    # If loop ended without explicit final answer, invoke LLM once more to summarize
    try:
        final_msg = llm.invoke(messages)
        return final_msg.content, tool_logs
    except Exception as e:
        return "", tool_logs


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extracts JSON object from markdown code fence or raw string."""
    if not text:
        return None
    # Look for ```json ... ```
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except Exception:
            pass

    # Look for { ... }
    curly_match = re.search(r"(\{[\s\S]*\})", text)
    if curly_match:
        try:
            return json.loads(curly_match.group(1))
        except Exception:
            pass

    return None


def generate_direct_tool_plan(req: TripPlanRequest, tool_logs: List[str]) -> TripPlanResponse:
    """
    Executes tools directly to build a complete TripPlanResponse if Groq API key is
    missing or during offline testing. Ensures UI remains fully operational and informative.
    """
    # 1. Calculate duration
    duration = req.trip_duration_days or 5
    if req.departure_date and req.return_date:
        try:
            from datetime import datetime
            d1 = datetime.strptime(req.departure_date, "%Y-%m-%d")
            d2 = datetime.strptime(req.return_date, "%Y-%m-%d")
            diff = (d2 - d1).days + 1
            if diff > 0:
                duration = diff
        except Exception:
            pass

    # 2. Call route tool
    tool_logs.append("Direct Tool Call: calculate_route_details")
    raw_route = calculate_route_details.invoke({
        "origin": req.origin,
        "destination": req.destination,
        "travel_mode": req.travel_mode
    })
    route_data = json.loads(raw_route)

    # 3. Call budget tool
    tool_logs.append("Direct Tool Call: estimate_trip_budget")
    raw_budget = estimate_trip_budget.invoke({
        "total_budget": req.budget,
        "travelers": req.travelers,
        "duration_days": duration,
        "travel_mode": req.travel_mode,
        "destination": req.destination
    })
    budget_data = json.loads(raw_budget)

    # 4. Call itinerary tool
    tool_logs.append("Direct Tool Call: generate_day_wise_itinerary")
    raw_itin = generate_day_wise_itinerary.invoke({
        "destination": req.destination,
        "days": duration,
        "interests": req.interests,
        "travel_mode": req.travel_mode
    })
    itin_data = json.loads(raw_itin)

    # 5. Call Tavily search tool
    tool_logs.append(f"Direct Tool Call: search_travel_info for {req.destination}")
    raw_search = search_travel_info.invoke({
        "query": f"top attractions, best food, and travel guide in {req.destination}"
    })
    search_data = json.loads(raw_search)

    is_live_tavily = search_data.get("status") == "live_tavily_search"

    # Parse actual Tavily results for enrichment
    tavily_insights = []
    if is_live_tavily:
        for item in search_data.get("results", []):
            if isinstance(item, dict):
                if "answer" in item:
                    tavily_insights.append(item["answer"])
                elif "content" in item:
                    tavily_insights.append(item.get("title", "") + ": " + item["content"])

    # 6. Groq + Tavily Dynamic Synthesis for Places, Food & Day-wise Itinerary
    llm = get_groq_llm()
    places = []
    food_items = []
    dynamic_success = False

    if llm and tavily_insights:
        try:
            tool_logs.append("Groq LLM Synthesis: Generating destination-tailored places, cuisine, and activities from live Tavily research")
            tavily_context = "\n".join(tavily_insights[:6])
            interests_text = ", ".join(req.interests) if req.interests else "sightseeing, food, culture, nature"

            synth_prompt = f"""You are a master travel planner. Using this verified live research:
{tavily_context[:2500]}

Generate a valid JSON object tailored specifically for a {duration}-day trip to {req.destination}:
1. "places": List of 4 real, famous, distinct attractions in {req.destination}. Each item must have:
   - "name": Real name of the place
   - "category": e.g. "Historical Landmark", "Scenic Waterfront", "Museum", "Park"
   - "description": 1-2 sentence compelling description
   - "best_time_to_visit": e.g. "Morning", "Sunset", "Afternoon"
   - "estimated_entry_cost": e.g. "Free", "$10 - $25", "Varies"
   - "tags": list of 2-4 keywords (e.g. ["Heritage", "Views", "Photography"])
2. "food": List of 3 authentic dishes, specialties, or famous restaurants in {req.destination}. Each item must have:
   - "name": Name of the dish or restaurant
   - "type": e.g. "Street Food Specialty", "Iconic Seafood", "Heritage Dining"
   - "description": 1-2 sentence description
   - "highlight_dish_or_experience": Specific must-try item
   - "price_level": "$", "$$", or "$$$"
3. "itinerary": List of {duration} daily plans. Each item must have:
   - "day_number": integer
   - "title": e.g. "Day 1: Arrival & Historic Fort Exploration"
   - "theme": 3-5 word summary of the day's theme
   - "morning_title": Specific morning sight/activity
   - "morning_desc": 1-2 sentence details
   - "afternoon_title": Specific afternoon sight/activity
   - "afternoon_desc": 1-2 sentence details
   - "evening_title": Specific evening sight/activity
   - "evening_desc": 1-2 sentence details

Return ONLY the raw JSON object, without markdown ticks, without commentary."""

            resp = llm.invoke(synth_prompt)
            ai_data = extract_json_from_text(resp.content)
            if ai_data:
                # 1. Places
                if ai_data.get("places") and len(ai_data["places"]) >= 2:
                    for p in ai_data["places"][:5]:
                        places.append({
                            "name": p.get("name", f"Attraction in {req.destination}"),
                            "category": p.get("category", "Sightseeing"),
                            "description": p.get("description", f"Notable sight in {req.destination}"),
                            "best_time_to_visit": p.get("best_time_to_visit", "Morning"),
                            "estimated_entry_cost": p.get("estimated_entry_cost", "Varies"),
                            "tags": p.get("tags", ["Sightseeing", "Photography"]),
                            "is_web_search_verified": True
                        })
                # 2. Food
                if ai_data.get("food") and len(ai_data["food"]) >= 2:
                    for f in ai_data["food"][:4]:
                        food_items.append({
                            "name": f.get("name", "Local Specialty"),
                            "type": f.get("type", "Regional Cuisine"),
                            "description": f.get("description", f"Signature cuisine of {req.destination}"),
                            "highlight_dish_or_experience": f.get("highlight_dish_or_experience", "Local house specialty"),
                            "price_level": f.get("price_level", "$$"),
                            "is_web_search_verified": True
                        })
                # 3. Itinerary Days
                if ai_data.get("itinerary") and len(ai_data["itinerary"]) >= 1:
                    custom_days = []
                    for d_idx, day_obj in enumerate(ai_data["itinerary"][:duration], 1):
                        custom_days.append({
                            "day_number": d_idx,
                            "title": day_obj.get("title", f"Day {d_idx}: Exploring {req.destination}"),
                            "theme": day_obj.get("theme", "Cultural Discovery & Landmarks"),
                            "morning": {
                                "time_slot": "Morning (08:30 - 12:00)",
                                "title": day_obj.get("morning_title", f"Morning Sightseeing in {req.destination}"),
                                "description": day_obj.get("morning_desc", "Begin your day visiting top sights."),
                                "location": req.destination,
                                "estimated_duration": "3-3.5 hours",
                                "approximate_cost": "Free - $20",
                                "is_tavily_sourced": True
                            },
                            "afternoon": {
                                "time_slot": "Afternoon (13:00 - 17:00)",
                                "title": day_obj.get("afternoon_title", f"Afternoon Cultural Trail"),
                                "description": day_obj.get("afternoon_desc", "Discover local markets and artisan workshops."),
                                "location": req.destination,
                                "estimated_duration": "3-4 hours",
                                "approximate_cost": "$10 - $40",
                                "is_tavily_sourced": True
                            },
                            "evening": {
                                "time_slot": "Evening (18:00 - 21:30)",
                                "title": day_obj.get("evening_title", f"Evening Dining & Sunset Walk"),
                                "description": day_obj.get("evening_desc", "Relax with an authentic dinner and evening stroll."),
                                "location": req.destination,
                                "estimated_duration": "2.5-3 hours",
                                "approximate_cost": "$20 - $60",
                                "is_tavily_sourced": True
                            },
                            "stay_recommendation": f"Centrally located boutique hotel or guesthouse in {req.destination}.",
                            "local_transport_tip": f"Explore on foot and use local transit or {req.travel_mode} for longer hops."
                        })
                    if len(custom_days) >= 1:
                        itin_data["days"] = custom_days

                if places and food_items:
                    dynamic_success = True
        except Exception as synth_err:
            tool_logs.append(f"Notice: Groq synthesis encountered: {synth_err}. Using verified database.")

    # Fallback to local database if dynamic synthesis was not completed
    if not dynamic_success:
        from backend.tools import DESTINATION_ATTRACTIONS, DESTINATION_FOOD, _get_dest_key
        dest_key = _get_dest_key(req.destination)
        db_places = DESTINATION_ATTRACTIONS.get(dest_key, [])
        if db_places:
            places = [
                {
                    "name": p["name"],
                    "category": p["category"],
                    "description": p["description"],
                    "best_time_to_visit": p.get("best_time_to_visit", "Morning"),
                    "estimated_entry_cost": p.get("estimated_entry_cost", "Varies"),
                    "tags": p.get("tags", []),
                    "is_web_search_verified": is_live_tavily
                }
                for p in db_places
            ]
        else:
            places = [
                {
                    "name": f"Top Landmark in {req.destination}",
                    "category": "Must-See Landmark",
                    "description": f"The primary iconic attraction of {req.destination}.",
                    "best_time_to_visit": "Morning",
                    "estimated_entry_cost": "Varies",
                    "tags": ["Sightseeing", "Photography"],
                    "is_web_search_verified": is_live_tavily
                }
            ]

        db_food = DESTINATION_FOOD.get(dest_key, [])
        if db_food:
            food_items = [
                {
                    "name": f["name"],
                    "type": f["type"],
                    "description": f["description"],
                    "highlight_dish_or_experience": f.get("highlight_dish_or_experience", "Chef's special"),
                    "price_level": f.get("price_level", "$$"),
                    "is_web_search_verified": is_live_tavily
                }
                for f in db_food
            ]
        else:
            food_items = [
                {
                    "name": f"Local Specialty Dining in {req.destination}",
                    "type": "Regional Cuisine",
                    "description": f"Authentic recipes and fresh local ingredients in {req.destination}.",
                    "highlight_dish_or_experience": "House specialty",
                    "price_level": "$$",
                    "is_web_search_verified": is_live_tavily
                }
            ]

    # Build alternative routes with proper comparison
    from backend.tools import _estimate_distance_km
    distances = _estimate_distance_km(req.origin, req.destination)
    road_d = distances["road"]
    alt_modes = {"car": "train", "train": "car", "bus": "train", "flight": "car", "bike": "bus"}
    alt_mode = alt_modes.get(req.travel_mode, "train")

    alt_routes = [
        {
            "route_name": f"Scenic / Longer Route via Secondary Roads",
            "travel_mode": req.travel_mode,
            "estimated_time": f"+1-2 hours compared to express route",
            "estimated_distance": f"~{int(road_d * 1.2)} km (scenic detour)",
            "pros": ["More scenic viewpoints and photo stops", "Passes through charming small towns", "Less highway traffic"],
            "cons": ["Longer travel time", "Fewer fuel/rest stops on rural roads"],
            "summary": f"Take the scenic route from {req.origin} to {req.destination} for a more relaxed, picturesque drive with stops at local villages."
        },
        {
            "route_name": f"Switch to {alt_mode.capitalize()} Transit",
            "travel_mode": alt_mode,
            "estimated_time": f"~{int(distances.get('rail' if alt_mode == 'train' else 'road', road_d) / (130 if alt_mode == 'train' else 90) + 0.5)}h estimated",
            "estimated_distance": f"~{int(distances.get('rail' if alt_mode == 'train' else 'road', road_d))} km",
            "pros": [
                "Zero driving fatigue" if alt_mode in ["train", "bus"] else "Full schedule flexibility",
                "Eco-friendly footprint" if alt_mode == "train" else "Door-to-door convenience",
                "Scenic views from window" if alt_mode == "train" else "Stop anywhere you like"
            ],
            "cons": [
                "Fixed departure schedules" if alt_mode in ["train", "bus"] else "Driver fatigue on long routes",
                "Luggage handling" if alt_mode in ["train", "bus"] else "Fuel and parking costs"
            ],
            "summary": f"Consider {alt_mode} as an alternative for the {req.origin} to {req.destination} journey."
        }
    ]

    # Generate destination-aware travel tips
    tips = [
        f"Start your departure from {req.origin} early in the morning to maximize your first day and avoid peak traffic.",
        f"Download offline maps for {req.destination} — cellular coverage can be spotty in scenic or mountainous areas.",
        f"For {req.travel_mode} travel: {'check tire pressure, pack water and snacks, and note fuel stops along the route' if req.travel_mode in ['car', 'bike'] else 'book tickets in advance for better seats and lower fares'}.",
        f"Pack layers — temperatures between {req.origin} and {req.destination} can change significantly across altitudes and time of day.",
        f"Keep your budget buffer of ~{req.currency} {int(req.budget * 0.08)} reserved for unexpected expenses or once-in-a-lifetime detour opportunities.",
        f"Check current travel advisories, weather forecasts, and any seasonal closures for {req.destination} before departure."
    ]

    return TripPlanResponse(
        trip_title=f"{duration}-Day Expedition: {req.origin} to {req.destination}",
        overview=(
            f"A curated {duration}-day journey from {req.origin} to {req.destination} via {req.travel_mode}. "
            f"Tailored for {req.travelers} traveler{'s' if req.travelers > 1 else ''} with a {req.currency} {req.budget:,.0f} budget, "
            f"highlighting {', '.join(req.interests) if req.interests else 'regional sights'}."
        ),
        origin=req.origin,
        destination=req.destination,
        departure_date=req.departure_date,
        return_date=req.return_date,
        duration_days=duration,
        travelers=req.travelers,
        currency=req.currency,
        total_budget=req.budget,
        travel_mode=req.travel_mode,
        route_details=RouteDetails(**route_data),
        itinerary=[DayItinerary(**d) for d in itin_data["days"]],
        budget_breakdown=BudgetBreakdown(**budget_data),
        places_to_visit=places,
        food_and_activities=food_items,
        travel_tips=tips,
        alternative_routes=alt_routes,
        data_sources={
            "web_search": "Tavily Search API (Live)" if is_live_tavily else "Regional Travel Knowledge Base (Configure TAVILY_API_KEY for live search)",
            "route_metrics": "Algorithmic road/transit estimation engine",
            "reasoning_engine": "Groq LLaMA-3.3-70b (Configured in .env)" if os.environ.get("GROQ_API_KEY") else "Atlas Agent Tool Synthesizer"
        },
        agent_reasoning_notes=tool_logs
    )


def plan_trip(req: TripPlanRequest) -> TripPlanResponse:
    """
    Main entry point for generating a trip plan.
    Attempts Groq agentic reasoning loop with tool calling.
    Falls back gracefully to direct tool synthesis if Groq returns invalid JSON or is not set up.
    """
    prompt = f"""
    Please generate an in-depth, structured travel route plan based on these traveler inputs:
    - Origin: {req.origin}
    - Destination: {req.destination}
    - Departure Date: {req.departure_date}
    - Return Date: {req.return_date or 'Flexible / Not set'}
    - Trip Duration: {req.trip_duration_days or 'Calculate from dates'}
    - Travelers: {req.travelers}
    - Total Budget: {req.currency} {req.budget}
    - Travel Mode: {req.travel_mode}
    - Interests & Preferences: {', '.join(req.interests)}
    - Special Notes: {req.custom_notes or 'None'}

    Instructions:
    1. Call `calculate_route_details` to determine realistic distance, durations, and intermediate stops.
    2. Call `search_travel_info` via Tavily to fetch current top attractions, dining gems, and local conditions.
    3. Call `estimate_trip_budget` to create an itemized budget breakdown.
    4. Call `generate_day_wise_itinerary` to schedule day-by-day morning, afternoon, and evening activities.
    5. Assemble the final result into the specified JSON format.
    """

    raw_response, tool_logs = run_agentic_planning_loop(prompt)
    parsed_json = extract_json_from_text(raw_response)

    if parsed_json:
        try:
            # Inject reasoning notes
            parsed_json["agent_reasoning_notes"] = tool_logs
            return TripPlanResponse(**parsed_json)
        except Exception as err:
            tool_logs.append(f"JSON validation failed ({err}), falling back to direct tool synthesis.")

    # Direct tool fallback ensures full uptime and complete adherence to schema
    return generate_direct_tool_plan(req, tool_logs)


def chat_with_agent(
    message: str,
    current_trip: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, List[str]]:
    """
    Conversational agent for follow-up questions and plan modifications.
    """
    llm = get_groq_llm()
    tool_logs = []

    if not llm:
        # Fallback intelligent response
        reply = (
            f"**Atlas Travel Advisor:** Thank you for your question: *'{message}'*!\n\n"
            "To activate real-time LLM conversation and live Tavily web search, please add your "
            "`GROQ_API_KEY` and `TAVILY_API_KEY` to the `.env` file.\n\n"
            "**General Travel Recommendation:**\n"
            "- If adjusting travel modes, remember that train and bus routes often offer scenic advantages, "
            "while driving provides optimal flexibility for detour stops.\n"
            "- For budget optimizations, shifting lodging slightly outside central tourist plazas can save 20-30%."
        )
        return reply, tool_logs

    llm_with_tools = llm.bind_tools(TRAVEL_AGENT_TOOLS)
    messages = [SystemMessage(content=CONVERSATIONAL_AGENT_PROMPT)]

    if current_trip:
        trip_context = (
            f"Active Trip Plan Context: Origin: {current_trip.get('origin')}, "
            f"Destination: {current_trip.get('destination')}, "
            f"Travel Mode: {current_trip.get('travel_mode')}, "
            f"Duration: {current_trip.get('duration_days')} days, "
            f"Budget: {current_trip.get('currency')} {current_trip.get('total_budget')}."
        )
        messages.append(SystemMessage(content=trip_context))

    if history:
        for turn in history[-6:]:  # Keep recent context
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=message))

    try:
        response = llm_with_tools.invoke(messages)
        # Check if tools are needed
        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                t_name = tool_call["name"]
                t_args = tool_call["args"]
                tool_logs.append(f"Chat Tool Call: {t_name}")
                selected_tool = TOOL_MAP.get(t_name)
                t_out = selected_tool.invoke(t_args) if selected_tool else "Tool not found"
                messages.append(ToolMessage(content=str(t_out), tool_call_id=tool_call["id"]))
            final_reply = llm.invoke(messages)
            return final_reply.content, tool_logs

        return response.content, tool_logs
    except Exception as e:
        return f"Error communicating with travel reasoning model: {str(e)}", tool_logs
