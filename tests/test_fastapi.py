"""
Unit and Integration Tests for PocketSmart AI FastAPI Application & Authentication Layer.
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from backend.auth import hash_password, verify_password, create_access_token, decode_access_token
from backend.db import create_user, get_user_by_email, save_recommendation, get_recommendations_by_user

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
    """Verifies GET / returns 200 OK with home page elements."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PocketSmart AI" in response.text
    assert "Home Interior Planner" in response.text
    assert "Party &amp; Event Planner" in response.text or "Party & Event Planner" in response.text


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


def test_planner_get_routes():
    """Verifies planner GET pages load forms without errors."""
    for path in ["/home-budget", "/party-budget", "/jewelry-budget", "/history"]:
        resp = client.get(path)
        assert resp.status_code == 200
