import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas import TripPlanRequest
from backend.tools import (
    calculate_route_details,
    estimate_trip_budget,
    generate_day_wise_itinerary,
    search_travel_info,
    TRAVEL_AGENT_TOOLS
)
from backend.agent import plan_trip, chat_with_agent

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "api_keys_configured" in data

def test_sample_plans_endpoint():
    response = client.get("/api/sample-plans")
    assert response.status_code == 200
    plans = response.json()
    assert isinstance(plans, list)
    assert len(plans) >= 3
    assert "destination" in plans[0]

def test_calculate_route_details_car():
    raw = calculate_route_details.invoke({
        "origin": "San Francisco, CA",
        "destination": "Los Angeles, CA",
        "travel_mode": "car"
    })
    res = json.loads(raw)
    assert "total_estimated_distance" in res
    assert "total_estimated_duration" in res
    assert len(res["stops"]) >= 1

def test_calculate_route_details_flight():
    raw = calculate_route_details.invoke({
        "origin": "New York, NY",
        "destination": "London, UK",
        "travel_mode": "flight"
    })
    res = json.loads(raw)
    assert "total_estimated_distance" in res
    assert "h" in res["total_estimated_duration"]

def test_estimate_trip_budget():
    raw = estimate_trip_budget.invoke({
        "total_budget": 2000,
        "travelers": 2,
        "duration_days": 5,
        "travel_mode": "car",
        "destination": "Los Angeles, CA"
    })
    res = json.loads(raw)
    assert res["total_budget"] == 2000
    assert res["per_person_budget"] == 1000
    assert res["daily_per_person"] == 200
    assert len(res["categories"]) >= 4

def test_generate_day_wise_itinerary():
    raw = generate_day_wise_itinerary.invoke({
        "destination": "Kyoto, Japan",
        "days": 3,
        "interests": ["temples", "matcha", "bamboo forest"],
        "travel_mode": "train"
    })
    res = json.loads(raw)
    assert len(res["days"]) == 3
    for day in res["days"]:
        assert "morning" in day
        assert "afternoon" in day
        assert "evening" in day

def test_search_travel_info():
    raw = search_travel_info.invoke({
        "query": "top attractions and scenic spots in Tokyo"
    })
    assert len(raw) > 50

def test_full_plan_trip():
    req = TripPlanRequest(
        origin="Paris, France",
        destination="Nice, France",
        departure_date="2025-08-10",
        return_date="2025-08-15",
        travelers=2,
        budget=2500,
        travel_mode="train",
        interests=["coastal views", "french cuisine", "museums"]
    )
    plan = plan_trip(req)
    assert plan.origin == "Paris, France"
    assert plan.destination == "Nice, France"
    assert len(plan.itinerary) == 6
    assert plan.budget_breakdown.total_budget == 2500
    assert len(plan.places_to_visit) >= 1

def test_chat_with_agent():
    reply, logs = chat_with_agent(
        message="What are the best vegetarian restaurants in Nice?",
        current_trip={"origin": "Paris", "destination": "Nice", "travel_mode": "train", "travelers": 2, "total_budget": 2500, "currency": "USD"}
    )
    assert reply is not None
    assert len(reply) > 20
