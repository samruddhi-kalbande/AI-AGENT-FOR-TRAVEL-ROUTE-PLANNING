"""
Pydantic schemas for the Travel Route Planning AI Agent.
Validates input requests from React/Gradio and structures the agent response.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):
    """Input parameters provided by the user for planning a trip."""
    origin: str = Field(..., description="Starting location / departure city", json_schema_extra={"example": "San Francisco, CA"})
    destination: str = Field(..., description="Destination location", json_schema_extra={"example": "Yosemite National Park, CA"})
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)", json_schema_extra={"example": "2025-06-15"})
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)", json_schema_extra={"example": "2025-06-19"})
    trip_duration_days: Optional[int] = Field(None, description="Trip duration in days if return date is not specified", json_schema_extra={"example": 5})
    travelers: int = Field(1, ge=1, le=50, description="Number of travelers", json_schema_extra={"example": 2})
    budget: float = Field(..., ge=50, description="Total budget for the trip", json_schema_extra={"example": 1500})
    currency: str = Field("USD", description="Currency code (USD, EUR, GBP, INR, etc.)", json_schema_extra={"example": "USD"})
    travel_mode: str = Field(
        "car",
        description="Travel mode: car, bike, bus, train, flight",
        json_schema_extra={"example": "car"}
    )
    interests: List[str] = Field(
        default_factory=lambda: ["nature", "food", "historical places"],
        description="List of interests and preferences",
        json_schema_extra={"example": ["nature", "hiking", "photography", "food"]}
    )
    custom_notes: Optional[str] = Field(
        None,
        description="Special preferences, dietary needs, or accessibility requests",
        json_schema_extra={"example": "Prefer scenic mountain routes, dog-friendly stops, and vegetarian food."}
    )


class RouteStop(BaseModel):
    """Intermediate stop or viewpoint along the travel route."""
    name: str
    location_type: str = Field("intermediate_stop", description="origin, intermediate_stop, waypoint, destination")
    description: str
    recommended_time_spent: Optional[str] = "1-2 hours"
    highlights: List[str] = Field(default_factory=list)


class RouteLeg(BaseModel):
    """A segment of the journey between two points."""
    from_location: str
    to_location: str
    transport_mode: str
    estimated_distance: str
    estimated_duration: str
    scenic_rating: Optional[str] = "High"
    transit_tips: Optional[str] = None


class RouteDetails(BaseModel):
    """Complete route information including intermediate stops and estimates."""
    summary: str
    total_estimated_distance: str
    total_estimated_duration: str
    transport_mode: str
    is_estimated: bool = True
    estimation_disclaimer: str = (
        "Distance and travel times are algorithmic estimates based on standard routes. "
        "Real-time traffic, seasonal weather, and road closures may affect actual travel times."
    )
    stops: List[RouteStop] = Field(default_factory=list)
    legs: List[RouteLeg] = Field(default_factory=list)


class DayActivitySlot(BaseModel):
    """Morning, afternoon, or evening activity slot in a day itinerary."""
    time_slot: str = "Morning"  # Morning, Afternoon, Evening
    title: str
    description: str
    location: Optional[str] = None
    estimated_duration: Optional[str] = "2-3 hours"
    approximate_cost: Optional[str] = "Free - Moderate"
    is_tavily_sourced: bool = False


class DayItinerary(BaseModel):
    """Day-wise structured travel plan."""
    day_number: int
    title: str
    theme: str
    morning: DayActivitySlot
    afternoon: DayActivitySlot
    evening: DayActivitySlot
    stay_recommendation: Optional[str] = None
    local_transport_tip: Optional[str] = None


class BudgetCategory(BaseModel):
    """Itemized budget category."""
    category: str
    allocated_amount: float
    percentage: float
    icon: str
    description: str


class BudgetBreakdown(BaseModel):
    """Complete budget estimation and categorization."""
    total_budget: float
    currency: str = "USD"
    per_person_budget: float
    budget_tier: str = "Moderate"
    categories: List[BudgetCategory] = Field(default_factory=list)
    saving_tips: List[str] = Field(default_factory=list)
    estimation_disclaimer: str = (
        "Budget values are approximated estimates based on average regional hospitality, "
        "transit, and dining costs."
    )


class PlaceRecommendation(BaseModel):
    """Recommended attraction or point of interest."""
    name: str
    category: str
    description: str
    best_time_to_visit: Optional[str] = "Morning"
    estimated_entry_cost: Optional[str] = "Free"
    tags: List[str] = Field(default_factory=list)
    is_web_search_verified: bool = True


class FoodAndActivity(BaseModel):
    """Curated local dining and experience recommendation."""
    name: str
    type: str  # Food / Dining, Adventure, Culture, Shopping
    description: str
    highlight_dish_or_experience: Optional[str] = None
    price_level: Optional[str] = "$$"
    is_web_search_verified: bool = True


class AlternativeRoute(BaseModel):
    """Alternative transit or scenic route option."""
    route_name: str
    travel_mode: str
    estimated_time: str
    estimated_distance: str
    pros: List[str]
    cons: List[str]
    summary: str


class TripPlanResponse(BaseModel):
    """Complete structured response returned to React and Gradio."""
    trip_title: str
    overview: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    duration_days: int
    travelers: int
    currency: str
    total_budget: float
    travel_mode: str
    route_details: RouteDetails
    itinerary: List[DayItinerary]
    budget_breakdown: BudgetBreakdown
    places_to_visit: List[PlaceRecommendation]
    food_and_activities: List[FoodAndActivity]
    travel_tips: List[str]
    alternative_routes: List[AlternativeRoute]
    data_sources: Dict[str, str] = Field(
        default_factory=lambda: {
            "web_search": "Tavily Search API (live attractions, recent local conditions)",
            "route_metrics": "Algorithmic route estimation (road/transit formulas)",
            "reasoning_engine": "Groq LLaMA-3.3-70b AI Agent"
        }
    )
    agent_reasoning_notes: Optional[List[str]] = Field(default_factory=list)


class ChatQueryRequest(BaseModel):
    """Interactive follow-up question regarding a trip plan or custom travel query."""
    message: str
    current_trip_plan: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class ChatQueryResponse(BaseModel):
    """Response from conversational agent."""
    reply: str
    modified_trip_plan: Optional[TripPlanResponse] = None
    tool_calls_made: Optional[List[str]] = Field(default_factory=list)
