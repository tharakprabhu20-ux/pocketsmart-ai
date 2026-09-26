"""
Specialized Generative AI Recommendation Service for Home, Party, and Jewelry Planners.
Integrates Google Gemini 1.5/2.5 Flash models to generate structured cost allocations,
multimodal outfit image matching, and intelligent retail brand search links.
"""

import os
import json
import urllib.parse
from typing import Dict, Any, List, Optional
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.generativeai as genai

load_dotenv()

FLASH_MODEL = "gemini-1.5-flash"
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def get_genai_model(model_name: str = FLASH_MODEL):
    """Configures and returns a GenerativeModel instance."""
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key or current_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not configured in .env")
    genai.configure(api_key=current_key)
    return genai.GenerativeModel(model_name)


def generate_search_links(item_name: str, category: str = "general") -> List[Dict[str, str]]:
    """
    Generates tailored e-commerce affiliate and direct search URLs
    for Amazon, Flipkart, IKEA, Myntra, Ajio, Tanishq, CaratLane, Swiggy, Zomato, etc.
    """
    encoded_query = urllib.parse.quote_plus(item_name)
    links = []
    
    if category in ("home", "furniture", "lighting", "appliances"):
        links = [
            {"platform": "Amazon", "icon": "📦", "url": f"https://www.amazon.in/s?k={encoded_query}"},
            {"platform": "Flipkart", "icon": "🛍️", "url": f"https://www.flipkart.com/search?q={encoded_query}"},
            {"platform": "IKEA", "icon": "🛋️", "url": f"https://www.ikea.com/in/en/search/?q={encoded_query}"},
            {"platform": "Pepperfry", "icon": "🪵", "url": f"https://www.pepperfry.com/site_product/search?q={encoded_query}"}
        ]
    elif category in ("party", "catering", "venue", "decorations", "cake"):
        links = [
            {"platform": "Amazon", "icon": "📦", "url": f"https://www.amazon.in/s?k={encoded_query}"},
            {"platform": "Swiggy", "icon": "🛵", "url": f"https://www.swiggy.com/search?query={encoded_query}"},
            {"platform": "Zomato", "icon": "🍽️", "url": f"https://www.zomato.com/india?q={encoded_query}"},
            {"platform": "OYO / Venues", "icon": "🏨", "url": f"https://www.oyorooms.com/search?query={encoded_query}"},
            {"platform": "Booking.com", "icon": "✈️", "url": f"https://www.booking.com/searchresults.html?ss={encoded_query}"}
        ]
    elif category in ("jewelry", "outfit", "accessories"):
        links = [
            {"platform": "Tanishq", "icon": "💎", "url": f"https://www.tanishq.co.in/search?q={encoded_query}"},
            {"platform": "CaratLane", "icon": "✨", "url": f"https://www.caratlane.com/search?q={encoded_query}"},
            {"platform": "Bluestone", "icon": "💍", "url": f"https://www.bluestone.com/search?q={encoded_query}"},
            {"platform": "Melorra", "icon": "🌸", "url": f"https://www.melorra.com/search?q={encoded_query}"},
            {"platform": "Myntra", "icon": "👗", "url": f"https://www.myntra.com/{encoded_query}"},
            {"platform": "Amazon", "icon": "📦", "url": f"https://www.amazon.in/s?k={encoded_query}"},
            {"platform": "Meesho", "icon": "🛒", "url": f"https://www.meesho.com/search?q={encoded_query}"}
        ]
    else:
        links = [
            {"platform": "Amazon", "icon": "📦", "url": f"https://www.amazon.in/s?k={encoded_query}"},
            {"platform": "Flipkart", "icon": "🛍️", "url": f"https://www.flipkart.com/search?q={encoded_query}"},
            {"platform": "Google Shopping", "icon": "🌐", "url": f"https://www.google.com/search?tbm=shop&q={encoded_query}"}
        ]
    return links


# =========================================================================
# 1. HOME INTERIOR PLANNER ENGINE
# =========================================================================

def plan_home_interior(
    budget: float,
    currency: str,
    rooms: List[str],
    style_preference: str,
    lighting_count: int,
    fan_count: int,
    furniture_preferences: List[str],
    special_notes: str = ""
) -> Dict[str, Any]:
    """Generates structured home interior allocation and item recommendations within total budget."""
    try:
        model = get_genai_model(FLASH_MODEL)
        
        prompt = f"""
        Act as a Master Interior Architect and Cost Estimator.
        Generate a comprehensive, realistic, within-budget home interior and decor plan:
        
        Client Project Specs:
        - Total Budget: {currency} {budget:,.2f}
        - Selected Rooms: {', '.join(rooms) if rooms else 'Whole House'}
        - Design Aesthetic: {style_preference}
        - Required Fixture Counts: {lighting_count} Lighting setups, {fan_count} Fans/Appliance setups
        - Furniture Focus: {', '.join(furniture_preferences) if furniture_preferences else 'Standard Living & Bedroom suite'}
        - Special Requests: {special_notes}
        
        Provide a detailed JSON response matching this schema:
        {{
            "plan_title": "string (e.g. Modern Minimalist 2BHK Interior Plan)",
            "summary": "string (2-3 sentences overview)",
            "total_estimated_cost": float (sum must not exceed total budget),
            "currency": "{currency}",
            "room_breakdown": [
                {{
                    "room_name": "Living Room / Kitchen / etc.",
                    "allocated_budget": float,
                    "color_palette": "string",
                    "key_features": ["feature 1", "feature 2"],
                    "items": [
                        {{
                            "item_name": "string (e.g., 3-Seater Velvet Sofa)",
                            "estimated_cost": float,
                            "priority": "High / Medium / Low",
                            "recommendation_tip": "string"
                        }}
                    ]
                }}
            ],
            "budget_saving_tips": [
                "tip 1",
                "tip 2",
                "tip 3"
            ]
        }}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        data = json.loads(response.text)
        
        # Inject e-commerce platform links into each item
        for room in data.get("room_breakdown", []):
            for item in room.get("items", []):
                item["shopping_links"] = generate_search_links(item["item_name"], category="home")
                
        return data
    except Exception as e:
        # Graceful fallback plan
        return _fallback_home_plan(budget, currency, rooms, style_preference)


def _fallback_home_plan(budget: float, currency: str, rooms: List[str], style: str) -> Dict[str, Any]:
    """Deterministic fallback if Gemini API is offline."""
    room_list = rooms if rooms else ["Living Room", "Master Bedroom", "Modular Kitchen"]
    per_room = budget / len(room_list) if room_list else budget
    breakdown = []
    
    for r in room_list:
        items = [
            {"item_name": f"{r} Essential Lighting & Accent Lamps", "estimated_cost": round(per_room * 0.2, 2), "priority": "High", "recommendation_tip": "Choose warm 3000K LED lights", "shopping_links": generate_search_links(f"{r} lights", "home")},
            {"item_name": f"{r} Core Furniture Package", "estimated_cost": round(per_room * 0.5, 2), "priority": "High", "recommendation_tip": "Modular space-saving furniture", "shopping_links": generate_search_links(f"{r} furniture", "home")},
            {"item_name": f"{r} Decor, Curtains & Soft Furnishings", "estimated_cost": round(per_room * 0.3, 2), "priority": "Medium", "recommendation_tip": "Neutral textured linens", "shopping_links": generate_search_links(f"{r} decor curtains", "home")}
        ]
        breakdown.append({
            "room_name": r,
            "allocated_budget": round(per_room, 2),
            "color_palette": "Slate Gray, Soft Oak, Brushed Brass",
            "key_features": ["Space optimization", "Ambiance lighting", "Cohesive aesthetic"],
            "items": items
        })
        
    return {
        "plan_title": f"{style} Interior Budget Blueprint",
        "summary": f"A balanced {style} layout optimized for your {currency} {budget:,.2f} budget across {len(room_list)} room(s).",
        "total_estimated_cost": budget,
        "currency": currency,
        "room_breakdown": breakdown,
        "budget_saving_tips": [
            "Opt for multi-functional storage ottomans and sofa beds.",
            "Utilize direct warm LED spot lighting rather than extensive false ceilings.",
            "Compare prices across IKEA, Amazon, and local carpenters before placing bulk orders."
        ]
    }


# =========================================================================
# 2. PARTY PLANNER ENGINE
# =========================================================================

def plan_party_event(
    budget: float,
    currency: str,
    event_type: str,
    guest_count: int,
    venue_type: str,
    catering_style: str,
    entertainment_preferences: List[str],
    special_requirements: str = ""
) -> Dict[str, Any]:
    """Generates structured party and event budget allocations with vendor search links."""
    try:
        model = get_genai_model(FLASH_MODEL)
        
        prompt = f"""
        Act as an Expert Event Producer and Party Planner.
        Design a complete, high-energy, optimized budget plan:
        
        Event Details:
        - Event Type: {event_type}
        - Total Budget: {currency} {budget:,.2f}
        - Number of Guests: {guest_count}
        - Venue Style: {venue_type}
        - Food/Catering: {catering_style}
        - Entertainment: {', '.join(entertainment_preferences) if entertainment_preferences else 'Music and Photography'}
        - Notes: {special_requirements}
        
        Provide a detailed JSON response matching this schema:
        {{
            "event_title": "string (e.g. Elegant Golden Jubilee Birthday Gala)",
            "summary": "string",
            "per_guest_cost": float,
            "total_estimated_cost": float (must be <= budget),
            "currency": "{currency}",
            "contingency_fund": float (recommended 5-10% of budget),
            "categories": [
                {{
                    "category_name": "Venue & Logistics / Food & Drinks / Decor & Theme / Entertainment",
                    "allocated_amount": float,
                    "percentage": float,
                    "line_items": [
                        {{
                            "item_name": "string (e.g., Buffet Catering from Top Local Kitchen)",
                            "estimated_cost": float,
                            "vendor_suggestion": "Swiggy Catering / Zomato / Local Venue"
                        }}
                    ]
                }}
            ],
            "timeline_schedule": [
                {{"time": "6:00 PM", "activity": "Welcome drinks & Guest Arrival"}},
                {{"time": "7:30 PM", "activity": "Main Program / Entertainment"}},
                {{"time": "9:00 PM", "activity": "Dinner & Socializing"}}
            ],
            "money_saving_hacks": [
                "hack 1",
                "hack 2",
                "hack 3"
            ]
        }}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        data = json.loads(response.text)
        
        # Inject platform search links for venue and catering
        for cat in data.get("categories", []):
            for item in cat.get("line_items", []):
                item["shopping_links"] = generate_search_links(item["item_name"], category="party")
                
        return data
    except Exception as e:
        return _fallback_party_plan(budget, currency, event_type, guest_count, venue_type, catering_style)


def _fallback_party_plan(budget: float, currency: str, event_type: str, guests: int, venue: str, catering: str) -> Dict[str, Any]:
    """Deterministic fallback for party budget planning."""
    g_count = max(1, guests)
    per_guest = budget / g_count
    
    venue_cost = round(budget * 0.30, 2)
    food_cost = round(budget * 0.40, 2)
    decor_cost = round(budget * 0.15, 2)
    ent_cost = round(budget * 0.10, 2)
    contingency = round(budget * 0.05, 2)
    
    return {
        "event_title": f"{event_type} Celebration Blueprint",
        "summary": f"Carefully engineered event plan for {guests} guests with a per-head budget of {currency} {per_guest:,.2f}.",
        "per_guest_cost": round(per_guest, 2),
        "total_estimated_cost": budget,
        "currency": currency,
        "contingency_fund": contingency,
        "categories": [
            {
                "category_name": "Food & Beverage",
                "allocated_amount": food_cost,
                "percentage": 40.0,
                "line_items": [
                    {"item_name": f"{catering} Live Food Counters & Starters", "estimated_cost": round(food_cost * 0.7, 2), "vendor_suggestion": "Swiggy Gourmet / Zomato Catering", "shopping_links": generate_search_links("Party catering buffet", "party")},
                    {"item_name": "Beverages, Mocktails & Desserts", "estimated_cost": round(food_cost * 0.3, 2), "vendor_suggestion": "Local Beverage Vendor", "shopping_links": generate_search_links("Party mocktails dessert", "party")}
                ]
            },
            {
                "category_name": "Venue & Setup",
                "allocated_amount": venue_cost,
                "percentage": 30.0,
                "line_items": [
                    {"item_name": f"{venue} Space Rental & Seating", "estimated_cost": venue_cost, "vendor_suggestion": "OYO Townhouse / Banquet Partner", "shopping_links": generate_search_links(f"{venue} party venue", "party")}
                ]
            },
            {
                "category_name": "Decorations & Theme",
                "allocated_amount": decor_cost,
                "percentage": 15.0,
                "line_items": [
                    {"item_name": "Custom Backdrop, Balloon Arch & Lighting", "estimated_cost": decor_cost, "vendor_suggestion": "Amazon Party Store", "shopping_links": generate_search_links("Party decor backdrop", "party")}
                ]
            },
            {
                "category_name": "Music & Photography",
                "allocated_amount": ent_cost,
                "percentage": 10.0,
                "line_items": [
                    {"item_name": "Sound System, Playlist Setup & Event Photos", "estimated_cost": ent_cost, "vendor_suggestion": "Local Creative Artist", "shopping_links": generate_search_links("Party DJ sound lighting", "party")}
                ]
            }
        ],
        "timeline_schedule": [
            {"time": "6:30 PM", "activity": "Welcome Refreshments & Photo Wall"},
            {"time": "7:45 PM", "activity": "Main Celebration & Interactive Games"},
            {"time": "9:00 PM", "activity": "Dinner Buffet Open"},
            {"time": "10:30 PM", "activity": "Cake Cutting & Farewell"}
        ],
        "money_saving_hacks": [
            "Order party supplies in bulk packages online rather than from single retail stores.",
            "Create a curated playlist on Spotify paired with a hired PA system to save on DJ charges.",
            "Opt for buffet-style service to minimize catering staffing overhead."
        ]
    }


# =========================================================================
# 3. JEWELRY & OUTFIT STYLIST ENGINE (MULTIMODAL VISION)
# =========================================================================

def plan_jewelry_recommendation(
    budget: float,
    currency: str,
    occasion: str,
    metal_preference: str,
    jewelry_types: List[str],
    outfit_description: str = "",
    image_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Uses Gemini Multimodal Vision to inspect outfit image (if uploaded) or analyzes styling text,
    and returns matching jewelry pieces with brand search links.
    """
    try:
        model = get_genai_model(FLASH_MODEL)
        
        prompt = f"""
        Act as an Elite Celebrity Stylist and Fine Jewelry Consultant.
        Recommend the perfect jewelry collection to complement the outfit and occasion:
        
        Client Details:
        - Total Budget: {currency} {budget:,.2f}
        - Occasion: {occasion}
        - Metal / Material: {metal_preference}
        - Target Jewelry Pieces: {', '.join(jewelry_types) if jewelry_types else 'Earrings, Necklace, Bracelet, Rings'}
        - Outfit Notes: {outfit_description if outfit_description else 'Modern ethnic / contemporary formal'}
        
        If an outfit image is attached, inspect the neckline, primary and secondary colors, embroidery, and fabric texture to recommend complementary jewelry shapes and gem colors.
        
        Provide a detailed JSON response matching this schema:
        {{
            "style_theme": "string (e.g., Royal Emerald & Rose Gold Fusion)",
            "outfit_analysis": "string (1-2 sentences on color harmony and neckline matching)",
            "total_estimated_cost": float (must be <= budget),
            "currency": "{currency}",
            "recommended_pieces": [
                {{
                    "piece_name": "string (e.g., Polki Drop Earrings in 18k Rose Gold)",
                    "category": "Earrings / Necklace / Ring / Bracelet / Maang Tikka",
                    "estimated_cost": float,
                    "metal_gem_details": "string (e.g., 18k Rose Gold with CZ Zircons)",
                    "style_rationale": "string (why this matches the outfit neckline and tone)",
                    "recommended_brands": ["Tanishq", "CaratLane", "Melorra"]
                }}
            ],
            "styling_pro_tips": [
                "tip 1",
                "tip 2"
            ]
        }}
        """
        
        content = [prompt]
        if image_bytes:
            img = Image.open(BytesIO(image_bytes))
            content.append(img)
            
        response = model.generate_content(
            content,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        data = json.loads(response.text)
        
        # Inject brand search links for Tanishq, CaratLane, Bluestone, etc.
        for piece in data.get("recommended_pieces", []):
            piece["shopping_links"] = generate_search_links(piece["piece_name"], category="jewelry")
            
        return data
    except Exception as e:
        return _fallback_jewelry_plan(budget, currency, occasion, metal_preference, jewelry_types, outfit_description)


def _fallback_jewelry_plan(budget: float, currency: str, occasion: str, metal: str, types: List[str], outfit: str) -> Dict[str, Any]:
    """Deterministic fallback for jewelry styling."""
    selected_types = types if types else ["Necklace", "Earrings", "Bracelet / Bangles", "Statement Ring"]
    per_piece = budget / len(selected_types) if selected_types else budget
    
    pieces = []
    for t in selected_types:
        name = f"Designer {metal} {t}"
        pieces.append({
            "piece_name": name,
            "category": t,
            "estimated_cost": round(per_piece, 2),
            "metal_gem_details": f"Hallmarked {metal} finish with brilliant accent stones",
            "style_rationale": f"Perfect visual balance for {occasion} attire.",
            "recommended_brands": ["Tanishq", "CaratLane", "Bluestone", "Melorra"],
            "shopping_links": generate_search_links(name, "jewelry")
        })
        
    return {
        "style_theme": f"Contemporary {metal} Radiance",
        "outfit_analysis": f"Complementary styling tuned for {occasion} with {metal} accents.",
        "total_estimated_cost": budget,
        "currency": currency,
        "recommended_pieces": pieces,
        "styling_pro_tips": [
            "Match your necklace length to the neckline (chokers for sweetheart necklines, layered pendants for V-necks).",
            "Balance statement earrings with a delicate bracelet to prevent visual clutter."
        ]
    }
