# Atlas AI Travel Agent — Agent Topology & Tool Calling Specifications

This document describes how the **Atlas AI Agent** works, how tools are registered and invoked, and how the system transitions between LLM function calling and deterministic fallback routines.

---

## 🏛️ Agent Design Philosophy

The core design principle governing Atlas:
> **The supervisor owns reasoning, routing, and synthesis; specialized tools own execution, math, and data retrieval.**

No tool invents facts outside its domain:
- **Route Tool**: Computes distances via Haversine geometry and road winding factors; never guesses lodging prices.
- **Budget Tool**: Computes strict mathematical allocations based on travelers and duration; never alters geographic route coordinates.
- **Tavily Search Tool**: Queries verified real-time web results for local food, attractions, and seasonal warnings.
- **Itinerary Tool**: Synthesizes balanced morning, afternoon, and evening daily schedules with duration bounds.

```
                  User Request (Origin, Destination, Mode, Budget, Dates)
                                       │
                                       ▼
                       FastAPI REST / Gradio Context Layer
                                       │
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │          Atlas AI Supervisor Agent        │
                 │      (Groq LLaMA-3.3-70B Function Calling) │
                 └─────────────────────┬─────────────────────┘
                                       │
           ┌───────────────┬───────────┴───────────┬───────────────┐
           ▼               ▼                       ▼               ▼
     [Route Tool]   [Tavily Search]         [Budget Engine] [Itinerary Gen]
      - Haversine    - Live Attractions      - Per-Person    - Morning slot
      - Rest Stops   - Hidden Dining Gems    - Daily Split   - Afternoon slot
      - Durations    - Regional Advisories   - Tiers (Eco/Lux)- Evening slot
           │               │                       │               │
           └───────────────┴───────────┬───────────┴───────────────┘
                                       │
                                       ▼
                             Tool Result Aggregator
                                       │
                                       ▼
                       Final Structured Plan Synthesis
                         (Pydantic Schema Validation)
```

---

## 🛠️ Tool Registry & Specifications

Every tool is implemented with explicit type hints, Pydantic docstrings, and strict schema validation:

| Tool Name | Purpose | Execution Mode | Schema / Signature |
| :--- | :--- | :--- | :--- |
| `calculate_route_details` | Evaluates road/air/rail distance, transit time by mode, and intermediate rest waypoints. | Deterministic Geodesic Math & Highway DB | `(origin: str, destination: str, travel_mode: str) -> str (JSON)` |
| `search_travel_info` | Real-time web search for attractions, authentic local cuisine, and travel tips. | Tavily API / Verified Destination DB | `(query: str, max_results: int = 4) -> str` |
| `estimate_trip_budget` | Itemized financial breakdown into 5 categories: Lodging, Transport, Food, Experiences, and Contingency. | Deterministic Financial Engine | `(total_budget: float, travelers: int, duration_days: int, travel_mode: str, destination: str) -> str (JSON)` |
| `generate_day_wise_itinerary` | Synthesizes full day-by-day morning, afternoon, and evening slots with duration and cost estimates. | Algorithmic Scheduler & Destination DB | `(destination: str, days: int, interests: List[str], travel_mode: str) -> str (JSON)` |

---

## 🔁 Dual Execution Modes

### 1. Online Mode (Groq LLaMA-3.3-70B Function Calling)
When `GROQ_API_KEY` is provided in `.env` or system environment:
1. The agent binds `TRAVEL_AGENT_TOOLS` using `llm.bind_tools(TRAVEL_AGENT_TOOLS)`.
2. The model inspects the prompt, identifies missing data or requirements, and calls the appropriate tools in parallel or sequence.
3. Outputs from tool calls are fed back into the agent context (`ToolMessage`).
4. The final synthesized plan matches the strict `TripPlanResponse` schema.

### 2. Deterministic Fallback Mode
When `GROQ_API_KEY` is not present, or during API outages/rate limits (HTTP 429/503):
- The agent immediately routes through the local deterministic calculation engine.
- Haversine geometry calculates accurate distances and travel times.
- Verified regional attraction and food databases seed the plan.
- **Zero hallucinations, zero downtime, and zero invented distances.**

---

## 📊 Telemetry & Auditability
Every generated plan includes `agent_reasoning_notes` detailing:
- The execution chain of tools invoked.
- Whether web queries were executed live via Tavily or seeded from the local verified database.
- Timestamp and parameter validation traces accessible directly in the React frontend via the **"Agent Telemetry"** modal.
