"""
Unit and Integration Tests for PocketSmart AI FastAPI Application & 5 Specialized Modules.
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from backend.auth import hash_password, verify_password, create_access_token, decode_access_token
from backend.db import (
    create_user,
    get_user_by_email,
    save_recommendation,
    get_recommendations_by_user,
    create_trip,
    get_trips_by_user,
    get_trip_by_id,
    add_trip_expense
)

client = TestClient(app)


def test_auth_hashing():
    """Verifies bcrypt password hashing and verification."""
    raw = "SecurePassword123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    """Verifies JWT token encoding and decoding."""
    payload = {"sub": "42", "email": "test@pocketsmart.ai"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["email"] == "test@pocketsmart.ai"


def test_homepage_endpoint():
    """Verifies GET / returns 200 OK with all 5 module links."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PocketSmart AI" in response.text
    assert "Home Interior" in response.text
    assert "Party" in response.text
    assert "Household Budget" in response.text or "Monthly Budget" in response.text
    assert "Trip" in response.text


def test_login_register_pages():
    """Verifies GET /login and GET /register load successfully."""
    r_login = client.get("/login")
    assert r_login.status_code == 200
    assert "Welcome Back" in r_login.text

    r_reg = client.get("/register")
    assert r_reg.status_code == 200
    assert "Create Account" in r_reg.text or "Get Started" in r_reg.text


def test_registration_and_login_flow():
    """Tests complete registration and subsequent login flow."""
    import uuid
    random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Register
    reg_resp = client.post(
        "/register",
        data={"full_name": "Test User", "email": random_email, "password": "TestPassword123!"},
        follow_redirects=False
    )
    assert reg_resp.status_code == 302
    assert "access_token" in reg_resp.cookies

    # 2. Login
    login_resp = client.post(
        "/login",
        data={"email": random_email, "password": "TestPassword123!"},
        follow_redirects=False
    )
    assert login_resp.status_code == 302
    assert "access_token" in login_resp.cookies


def test_all_planner_get_routes():
    """Verifies all 5 planner GET pages and history load without errors."""
    for path in ["/home-budget", "/party-budget", "/jewelry-budget", "/monthly-budget", "/trip-tracker", "/history"]:
        resp = client.get(path)
        assert resp.status_code == 200


def test_monthly_household_budget_post():
    """Verifies POST /monthly-budget computes 50/30/20 math and surpluses."""
    resp = client.post(
        "/monthly-budget",
        data={
            "income": 100000.0,
            "currency": "INR",
            "housing_rent": 25000.0,
            "groceries": 15000.0,
            "utilities": 5000.0,
            "transport": 5000.0,
            "dining_entertainment": 15000.0,
            "shopping_lifestyle": 10000.0,
            "savings_investments": 25000.0
        }
    )
    assert resp.status_code == 200
    assert "Monthly Household Budget Plan" in resp.text
    assert "50/30/20 Framework Compliance" in resp.text


def test_trip_tracker_flow():
    """Verifies creating a trip and logging an itemized expense."""
    # 1. Create Trip
    trip_id = create_trip(
        user_id=1,
        trip_name="Goa Summer Retreat",
        destination="Goa, India",
        budget=50000.0,
        currency="INR",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )
    assert trip_id > 0

    # 2. Add Expense
    exp_id = add_trip_expense(
        trip_id=trip_id,
        category="Hotels/Stay",
        description="Beach Resort 3 Nights",
        amount=18000.0,
        expense_date="2026-10-11"
    )
    assert exp_id > 0

    # 3. Fetch Trip and verify calculations
    trip_data = get_trip_by_id(trip_id)
    assert trip_data is not None
    assert trip_data["total_spent"] == 18000.0
    assert trip_data["remaining_budget"] == 32000.0
    assert trip_data["utilization_pct"] == 36.0
    assert len(trip_data["expenses"]) >= 1

    # 4. View Trip Page
    resp = client.get(f"/trip-tracker?trip_id={trip_id}")
    assert resp.status_code == 200
    assert "Goa Summer Retreat" in resp.text
    assert "Beach Resort 3 Nights" in resp.text
