"""
PocketSmart AI - Production-Grade FastAPI Application.
Implements:
1. Static files & Jinja2 template rendering
2. User authentication (Bcrypt hashing, JWT token creation, cookie session persistence)
3. Endpoints: /, /login, /register, /logout, /dashboard, /history, /recommendation-details/{id}
4. Core Lifestyle AI Modules:
   - /home-budget (Home Interior & Decor with IKEA, Amazon, Flipkart, Pepperfry links)
   - /party-budget (Party & Event with Swiggy, Zomato, OYO links)
   - /jewelry-budget (Jewelry & Outfit Vision with Tanishq, CaratLane, Bluestone links)
5. Enhanced Financial & Tracker Modules:
   - /monthly-budget (Monthly Household Fixed & Variable Allocations with 50/30/20 Surpluses)
   - /trip-tracker (Vacation & Trip Project Ledger with Itemized Expense Submissions)
"""

import os
import json
import uuid
from typing import Optional, List
from fastapi import FastAPI, Request, Form, UploadFile, File, Response, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Ensure project root paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

os.makedirs(UPLOADS_DIR, exist_ok=True)
load_dotenv()

from backend.db import (
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    save_recommendation,
    get_recommendations_by_user,
    get_recommendation_by_id,
    create_trip,
    get_trips_by_user,
    get_trip_by_id,
    add_trip_expense
)
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from backend.planner_service import (
    plan_home_interior,
    plan_party_event,
    plan_jewelry_recommendation
)

# Initialize Database tables
init_db()

# Initialize FastAPI App
app = FastAPI(
    title="PocketSmart AI API",
    description="Your Smart Budget & Recommendation Assistant",
    version="2.0.0"
)

# Mount Static Files and Jinja2 Templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# =========================================================================
# Authentication Helper Dependency
# =========================================================================

def get_current_user_optional(request: Request) -> Optional[dict]:
    """Extracts logged-in user from JWT cookie session if present."""
    token = request.cookies.get("access_token")
    if not token:
        # Also check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None
        
    payload = decode_access_token(token)
    if not payload:
        return None
        
    user_id = payload.get("sub")
    if user_id:
        try:
            return get_user_by_id(int(user_id))
        except (ValueError, TypeError):
            return None
    return None


# =========================================================================
# 1. CORE NAVIGATION & AUTHENTICATION ENDPOINTS
# =========================================================================

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Landing Home Page with hero banner, 5 planner cards, and testimonials."""
    user = get_current_user_optional(request)
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login view."""
    user = get_current_user_optional(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="login.html", context={"user": None, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Processes user login credentials and issues session JWT cookie."""
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"user": None, "error": "Invalid email or password. Please check your credentials."}
        )
        
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user["id"]), "email": user["email"]})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration view."""
    user = get_current_user_optional(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="register.html", context={"user": None, "error": None})


@app.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Registers a new user account with hashed password."""
    existing_user = get_user_by_email(email)
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"user": None, "error": "An account with this email already exists."}
        )
        
    hashed = hash_password(password)
    new_user = create_user(email=email, full_name=full_name, hashed_password=hashed)
    if not new_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"user": None, "error": "Registration failed. Please try again."}
        )
        
    # Auto-login newly registered user
    access_token = create_access_token(data={"sub": str(new_user["id"]), "email": new_user["email"]})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    return response


@app.get("/logout")
async def logout():
    """Clears the session cookie and redirects home."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@app.post("/token")
async def login_for_access_token(email: str = Form(...), password: str = Form(...)):
    """API token endpoint for programmatic access."""
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return JSONResponse(status_code=400, content={"error": "Invalid credentials"})
    token = create_access_token(data={"sub": str(user["id"]), "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


# =========================================================================
# 2. DASHBOARD & RECOMMENDATION HISTORY
# =========================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    """User Portal showing recent recommendation plans, active trips, and launch shortcuts."""
    user = get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
    recent_plans = get_recommendations_by_user(user_id=user["id"], limit=10)
    active_trips = get_trips_by_user(user_id=user["id"])
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user, "recent_plans": recent_plans, "active_trips": active_trips}
    )


@app.get("/history", response_class=HTMLResponse)
async def history_view(request: Request, module: Optional[str] = None):
    """Master log of all past AI recommendations and manual plans."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    recommendations = get_recommendations_by_user(user_id=user_id, module_type=module, limit=50)
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "user": user,
            "recommendations": recommendations,
            "current_module": module
        }
    )


@app.get("/recommendation-details/{rec_id}", response_class=HTMLResponse)
async def recommendation_details_view(request: Request, rec_id: int):
    """Detailed view for a single saved recommendation plan."""
    user = get_current_user_optional(request)
    plan = get_recommendation_by_id(rec_id)
    if not plan:
        return RedirectResponse(url="/history", status_code=status.HTTP_302_FOUND)
        
    try:
        details = json.loads(plan["plan_result_json"])
    except Exception:
        details = {}
        
    return templates.TemplateResponse(
        request=request,
        name="recommendation_details.html",
        context={
            "user": user,
            "plan": plan,
            "details": details
        }
    )


# =========================================================================
# 3. ENHANCED MODULE 1: MONTHLY HOUSEHOLD BUDGET PLANNER
# =========================================================================

@app.get("/monthly-budget", response_class=HTMLResponse)
async def monthly_budget_page(request: Request):
    """Monthly Household Budget view."""
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="monthly_budget.html",
        context={"user": user, "form_data": {}, "budget_result": None}
    )


@app.post("/monthly-budget", response_class=HTMLResponse)
async def monthly_budget_calculate(
    request: Request,
    income: float = Form(75000.0),
    currency: str = Form("INR"),
    housing_rent: float = Form(20000.0),
    groceries: float = Form(10000.0),
    utilities: float = Form(4000.0),
    transport: float = Form(3500.0),
    dining_entertainment: float = Form(8000.0),
    shopping_lifestyle: float = Form(6000.0),
    savings_investments: float = Form(15000.0)
):
    """Calculates deterministic 50/30/20 household budget breakdown and surpluses."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else 1
    
    # 1. Deterministic Category Aggregations
    needs_actual = housing_rent + groceries + utilities + transport
    wants_actual = dining_entertainment + shopping_lifestyle
    savings_actual = savings_investments
    total_expenses = needs_actual + wants_actual + savings_actual
    
    needs_target = income * 0.50
    wants_target = income * 0.30
    savings_target = income * 0.20
    
    needs_variance = needs_target - needs_actual
    wants_variance = wants_target - wants_actual
    savings_variance = savings_actual - savings_target
    net_cash_flow = income - total_expenses
    
    needs_pct = round((needs_actual / income * 100.0), 1) if income > 0 else 0.0
    wants_pct = round((wants_actual / income * 100.0), 1) if income > 0 else 0.0
    savings_pct = round((savings_actual / income * 100.0), 1) if income > 0 else 0.0
    
    # Generate diagnostic summary
    if net_cash_flow >= 0 and savings_pct >= 20.0:
        summary = f"Excellent financial health! Your household saves {savings_pct}% of take-home income ({currency} {savings_actual:,.2f}) with a net surplus buffer of {currency} {net_cash_flow:,.2f}."
    elif net_cash_flow >= 0:
        summary = f"Stable cash flow with a monthly surplus of {currency} {net_cash_flow:,.2f}. Consider trimming wants ({wants_pct}%) to hit the golden 20% savings target ({currency} {savings_target:,.2f})."
    else:
        summary = f"Deficit Warning: Monthly expenses exceed take-home pay by {currency} {abs(net_cash_flow):,.2f}. Needs represent {needs_pct}% and Wants represent {wants_pct}% of income."
        
    budget_result = {
        "plan_title": "Monthly Household Budget Plan",
        "income": income,
        "currency": currency,
        "needs_actual": needs_actual,
        "needs_target": needs_target,
        "needs_variance": needs_variance,
        "needs_pct": needs_pct,
        "wants_actual": wants_actual,
        "wants_target": wants_target,
        "wants_variance": wants_variance,
        "wants_pct": wants_pct,
        "savings_actual": savings_actual,
        "savings_target": savings_target,
        "savings_variance": savings_variance,
        "savings_pct": savings_pct,
        "total_expenses": total_expenses,
        "net_cash_flow": net_cash_flow,
        "summary": summary
    }
    
    # Save plan to SQLite history
    save_recommendation(
        module_type="monthly_budget",
        title=f"Household Budget ({currency} {income:,.0f}/mo)",
        budget=income,
        currency=currency,
        user_inputs_json=json.dumps({
            "income": income,
            "housing_rent": housing_rent,
            "groceries": groceries,
            "utilities": utilities,
            "transport": transport,
            "dining_entertainment": dining_entertainment,
            "shopping_lifestyle": shopping_lifestyle,
            "savings_investments": savings_investments
        }),
        plan_result_json=json.dumps(budget_result),
        user_id=user_id
    )
    
    form_data = {
        "income": income,
        "currency": currency,
        "housing_rent": housing_rent,
        "groceries": groceries,
        "utilities": utilities,
        "transport": transport,
        "dining_entertainment": dining_entertainment,
        "shopping_lifestyle": shopping_lifestyle,
        "savings_investments": savings_investments
    }
    
    return templates.TemplateResponse(
        request=request,
        name="monthly_budget.html",
        context={"user": user, "form_data": form_data, "budget_result": budget_result}
    )


# =========================================================================
# 4. ENHANCED MODULE 2: TRIP EXPENSE TRACKER
# =========================================================================

@app.get("/trip-tracker", response_class=HTMLResponse)
async def trip_tracker_page(request: Request, trip_id: Optional[int] = None):
    """Trip Expense Tracker hub with active ledger view."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else 1
    
    all_trips = get_trips_by_user(user_id=user_id)
    selected_trip = None
    
    if trip_id:
        selected_trip = get_trip_by_id(trip_id)
    elif all_trips:
        selected_trip = get_trip_by_id(all_trips[0]["id"])
        
    return templates.TemplateResponse(
        request=request,
        name="trip_tracker.html",
        context={
            "user": user,
            "all_trips": all_trips,
            "selected_trip": selected_trip
        }
    )


@app.post("/trip-tracker/new")
async def trip_tracker_create(
    request: Request,
    trip_name: str = Form(...),
    destination: str = Form(...),
    budget: float = Form(45000.0),
    currency: str = Form("INR"),
    start_date: str = Form(""),
    end_date: str = Form("")
):
    """Creates a new trip and redirects to its ledger."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else 1
    
    trip_id = create_trip(
        user_id=user_id,
        trip_name=trip_name,
        destination=destination,
        budget=budget,
        currency=currency,
        start_date=start_date,
        end_date=end_date
    )
    
    # Save a reference to recommendation history
    save_recommendation(
        module_type="trip",
        title=f"Trip: {trip_name} ({destination})",
        budget=budget,
        currency=currency,
        user_inputs_json=json.dumps({"trip_name": trip_name, "destination": destination}),
        plan_result_json=json.dumps({"trip_id": trip_id, "summary": f"Travel budget cap for {trip_name} set to {currency} {budget:,.2f}."}),
        user_id=user_id
    )
    
    return RedirectResponse(url=f"/trip-tracker?trip_id={trip_id}", status_code=status.HTTP_302_FOUND)


@app.post("/trip-tracker/expense")
async def trip_tracker_add_expense(
    request: Request,
    trip_id: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    expense_date: str = Form("")
):
    """Logs an itemized expense into an active trip."""
    add_trip_expense(
        trip_id=trip_id,
        category=category,
        description=description,
        amount=amount,
        expense_date=expense_date
    )
    return RedirectResponse(url=f"/trip-tracker?trip_id={trip_id}", status_code=status.HTTP_302_FOUND)


# =========================================================================
# 5. CORE AI PLANNER MODULES (HOME, PARTY, JEWELRY)
# =========================================================================

# --- A. HOME INTERIOR PLANNER ---
@app.get("/home-budget", response_class=HTMLResponse)
async def home_budget_page(request: Request):
    """Home Interior Planner form view."""
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={"user": user, "form_data": {}, "plan_result": None}
    )


@app.post("/home-budget", response_class=HTMLResponse)
async def home_budget_generate(
    request: Request,
    budget: float = Form(150000.0),
    currency: str = Form("INR"),
    rooms: List[str] = Form([]),
    style_preference: str = Form("Modern Minimalist"),
    lighting_count: int = Form(6),
    fan_count: int = Form(3),
    furniture: List[str] = Form([]),
    special_notes: str = Form("")
):
    """Processes home planner specifications and runs Gemini generation."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else 1
    
    plan_data = plan_home_interior(
        budget=budget,
        currency=currency,
        rooms=rooms,
        style_preference=style_preference,
        lighting_count=lighting_count,
        fan_count=fan_count,
        furniture_preferences=furniture,
        special_notes=special_notes
    )
    
    # Save plan to SQLite history
    save_recommendation(
        module_type="home",
        title=plan_data.get("plan_title", "Home Interior Plan"),
        budget=budget,
        currency=currency,
        user_inputs_json=json.dumps({
            "rooms": rooms,
            "style": style_preference,
            "lighting_count": lighting_count,
            "fan_count": fan_count,
            "furniture": furniture,
            "notes": special_notes
        }),
        plan_result_json=json.dumps(plan_data),
        user_id=user_id
    )
    
    form_data = {
        "budget": budget,
        "currency": currency,
        "rooms": rooms,
        "style_preference": style_preference,
        "lighting_count": lighting_count,
        "fan_count": fan_count,
        "furniture": furniture,
        "special_notes": special_notes
    }
    
    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={"user": user, "form_data": form_data, "plan_result": plan_data}
    )


# --- B. PARTY & EVENT PLANNER ---
@app.get("/party-budget", response_class=HTMLResponse)
async def party_budget_page(request: Request):
    """Party & Event Planner form view."""
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={"user": user, "form_data": {}, "plan_result": None}
    )


@app.post("/party-budget", response_class=HTMLResponse)
async def party_budget_generate(
    request: Request,
    budget: float = Form(50000.0),
    currency: str = Form("INR"),
    event_type: str = Form("Birthday Party"),
    guest_count: int = Form(25),
    venue_type: str = Form("Rooftop Lounge / Banquet"),
    catering_style: str = Form("Live Buffet & Mocktails"),
    entertainment: List[str] = Form([]),
    special_requirements: str = Form("")
):
    """Processes party specifications and generates per-head budget breakdown."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else 1
    
    plan_data = plan_party_event(
        budget=budget,
        currency=currency,
        event_type=event_type,
        guest_count=guest_count,
        venue_type=venue_type,
        catering_style=catering_style,
        entertainment_preferences=entertainment,
        special_requirements=special_requirements
    )
    
    # Save plan to SQLite history
    save_recommendation(
        module_type="party",
        title=plan_data.get("event_title", f"{event_type} Budget Plan"),
        budget=budget,
        currency=currency,
        user_inputs_json=json.dumps({
            "event_type": event_type,
            "guest_count": guest_count,
            "venue_type": venue_type,
            "catering_style": catering_style,
            "entertainment": entertainment,
            "requirements": special_requirements
        }),
        plan_result_json=json.dumps(plan_data),
        user_id=user_id
    )
    
    form_data = {
        "budget": budget,
        "currency": currency,
        "event_type": event_type,
        "guest_count": guest_count,
        "venue_type": venue_type,
        "catering_style": catering_style,
        "entertainment": entertainment,
        "special_requirements": special_requirements
    }
    
    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={"user": user, "form_data": form_data, "plan_result": plan_data}
    )


# --- C. JEWELRY & OUTFIT STYLIST (MULTIMODAL VISION) ---
@app.get("/jewelry-budget", response_class=HTMLResponse)
async def jewelry_budget_page(request: Request):
    """Jewelry Stylist form view."""
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={"user": user, "form_data": {}, "plan_result": None, "image_url": None}
    )


@app.post("/jewelry-budget", response_class=HTMLResponse)
async def jewelry_budget_generate(
    request: Request,
    budget: float = Form(45000.0),
    currency: str = Form("INR"),
    occasion: str = Form("Wedding / Reception"),
    metal_preference: str = Form("18k / 22k Yellow Gold"),
    jewelry_types: List[str] = Form([]),
    outfit_description: str = Form(""),
    outfit_image: Optional[UploadFile] = File(None)
):
    """Evaluates outfit photo or description with Gemini Multimodal Vision."""
    user = get_current_user_optional(request)
    user_id = user["id"] if user else 1
    
    image_bytes = None
    image_filename = None
    image_url = None
    
    if outfit_image and outfit_image.filename:
        image_bytes = await outfit_image.read()
        if len(image_bytes) > 0:
            ext = os.path.splitext(outfit_image.filename)[1] or ".jpg"
            image_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(UPLOADS_DIR, image_filename)
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            image_url = f"/static/uploads/{image_filename}"
            
    plan_data = plan_jewelry_recommendation(
        budget=budget,
        currency=currency,
        occasion=occasion,
        metal_preference=metal_preference,
        jewelry_types=jewelry_types,
        outfit_description=outfit_description,
        image_bytes=image_bytes
    )
    
    # Save plan to SQLite history
    save_recommendation(
        module_type="jewelry",
        title=plan_data.get("style_theme", "Jewelry Styling Plan"),
        budget=budget,
        currency=currency,
        user_inputs_json=json.dumps({
            "occasion": occasion,
            "metal": metal_preference,
            "jewelry_types": jewelry_types,
            "outfit_description": outfit_description
        }),
        plan_result_json=json.dumps(plan_data),
        user_id=user_id,
        image_path=image_filename
    )
    
    form_data = {
        "budget": budget,
        "currency": currency,
        "occasion": occasion,
        "metal_preference": metal_preference,
        "jewelry_types": jewelry_types,
        "outfit_description": outfit_description
    }
    
    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={
            "user": user,
            "form_data": form_data,
            "plan_result": plan_data,
            "image_url": image_url
        }
    )


# =========================================================================
# Application Runner
# =========================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
