"""
Gemini Service Layer for PocketSmart AI.
Integrates Google Gemini multimodal APIs for receipt OCR, financial health audits, and what-if scenario reasoning.
Supports dynamic multi-currency localization (₹, $, €, £, د.إ, etc.).
Strict separation: Gemini provides qualitative reasoning and classification; all math is fed in directly from the deterministic budget engine.
"""

import os
import json
from typing import Dict, Any, List, Optional
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.generativeai as genai

load_dotenv()

# Active standard generation models for Google Gemini API
FLASH_MODEL = "gemini-3.6-flash"
PRO_MODEL = "gemini-3.6-flash"  # Flash delivers low-latency high-quality reasoning; falls back seamlessly

# Initialize Gemini API configuration
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


# --- Pydantic v2 Models for Structured Receipt Parsing ---

class ExpenseItem(BaseModel):
    item_name: str = Field(description="Name or description of the purchased item or service")
    amount: float = Field(description="Price or cost of the item as a positive float in the active receipt currency")
    category: str = Field(
        description="Must be strictly one of: 'Needs', 'Wants', or 'Savings'. 'Needs' for groceries, healthcare, utilities, rent, transit. 'Wants' for dining, entertainment, electronics, retail, hobby. 'Savings' for debt repayment, investments, or bank savings transfers."
    )


class ReceiptData(BaseModel):
    merchant: str = Field(description="Name of the store, vendor, or merchant")
    date: str = Field(description="Date of the receipt in YYYY-MM-DD format if found, otherwise today's date")
    total_amount: float = Field(description="Total receipt amount indicated on the receipt")
    items: List[ExpenseItem] = Field(description="List of individual line items extracted from the receipt")


# Alias for backwards compatibility
ReceiptExtraction = ReceiptData


def get_configured_model(model_name: str = FLASH_MODEL):
    """Returns a GenerativeModel instance with proper API configuration check."""
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key or current_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not configured in the environment or .env file.")
    genai.configure(api_key=current_key)
    return genai.GenerativeModel(model_name)


def parse_receipt_image(image_input, currency_symbol: str = "₹") -> Dict[str, Any]:
    """
    Calls Gemini vision model with structured JSON response schema enforcement via Pydantic.
    Accepts PIL Image or bytes and accounts for receipt amounts in the chosen currency.
    """
    try:
        model = get_configured_model(FLASH_MODEL)
        
        # Prepare PIL Image
        if isinstance(image_input, bytes):
            image = Image.open(BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            image = Image.open(image_input)
            
        prompt = f"""
        You are an elite financial OCR specialist.
        Analyze this receipt image thoroughly and extract all fields into the active currency ({currency_symbol}):
        1. Merchant / Store name
        2. Transaction Date (in YYYY-MM-DD format)
        3. Total receipt amount
        4. Every line item with its cost and 50/30/20 category classification:
           - "Needs": Groceries, medical, hygiene, utilities, essential transit, household staples.
           - "Wants": Restaurants, coffee, alcohol, apparel, electronics, entertainment, decor, subscriptions.
           - "Savings": Direct transfers, investment receipts, loan/debt principal repayments.
        
        Strictly format your response according to the requested JSON schema.
        """
        
        # Using structured output generation
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=ReceiptData,
                temperature=0.1
            )
        )
        
        parsed_json = json.loads(response.text)
        return parsed_json
        
    except Exception as e:
        # Fallback error handling
        return {
            "error": str(e),
            "merchant": "Unknown Merchant",
            "date": "",
            "total_amount": 0.0,
            "items": []
        }


def generate_budget_advice(income: float, budget: Dict[str, Any], currency_symbol: str = "₹") -> str:
    """
    Calls Gemini model passing pre-calculated deterministic math metrics and localized currency.
    Generates a 3-part behavioral spending audit:
      1. Financial Health Diagnosis
      2. 3 High-Impact Spending Cuts for overage categories
      3. 30-Day Action Item Sprint
    """
    try:
        model = get_configured_model(PRO_MODEL)
        cur = currency_symbol
        
        system_context = f"""
        You are an elite FinTech Solutions Architect & Behavioral Financial Coach.
        Here is the user's verified, deterministic 50/30/20 budget summary for the current month in currency: {cur}
        - Monthly Net Income: {cur}{income:,.2f}
        - Total Spent: {cur}{budget['total_spent']:,.2f} ({budget['pct_income']['Total']}% of Income)
        - Net Cash Flow / Remaining: {cur}{budget['net_cash_flow']:,.2f}

        Category Benchmarks vs Actuals:
        1. Needs (Target: 50% = {cur}{budget['targets']['Needs']:,.2f}):
           - Actual Spent: {cur}{budget['actuals']['Needs']:,.2f} ({budget['pct_income']['Needs']}% of Income)
           - Variance (Surplus/Deficit): {cur}{budget['variances']['Needs']:,.2f}
           - Target Utilization: {budget['utilization']['Needs']}%
           
        2. Wants (Target: 30% = {cur}{budget['targets']['Wants']:,.2f}):
           - Actual Spent: {cur}{budget['actuals']['Wants']:,.2f} ({budget['pct_income']['Wants']}% of Income)
           - Variance (Surplus/Deficit): {cur}{budget['variances']['Wants']:,.2f}
           - Target Utilization: {budget['utilization']['Wants']}%
           
        3. Savings (Target: 20% = {cur}{budget['targets']['Savings']:,.2f}):
           - Actual Allocated: {cur}{budget['actuals']['Savings']:,.2f} ({budget['pct_income']['Savings']}% of Income)
           - Variance (Surplus/Deficit): {cur}{budget['variances']['Savings']:,.2f}
           - Target Utilization: {budget['utilization']['Savings']}%

        TASK:
        Generate a professional, encouraging, highly actionable 3-part spending audit in clean Markdown, always referencing numbers with the currency symbol {cur}:
        
        ### 1. 🩺 Financial Health Diagnosis
        Provide a concise evaluation of whether their spending adheres to the 50/30/20 balance. Highlight whether they have a healthy surplus or dangerous category leakage.

        ### 2. ✂️ 3 High-Impact Spending Cuts
        Focus on whichever category is in deficit or closest to exceeding its ceiling (especially Wants or bloated Needs). Give 3 concrete, realistic behavioral adjustments with estimated monthly savings in {cur}.

        ### 3. 🎯 30-Day Action Item Sprint
        Define one specific, high-leverage financial sprint for the next 30 days to rebalance their cash flow and lock in their 20% savings rate.
        
        Rules:
        - Do not recalculate or alter the mathematical totals. Rely directly on the provided numbers.
        - Always use {cur} as the currency symbol.
        - Be direct, strategic, empathetic, and quantitative.
        """
        
        response = model.generate_content(
            system_context,
            generation_config=genai.GenerationConfig(
                temperature=0.4
            )
        )
        return response.text
        
    except Exception as e:
        return f"⚠️ Unable to generate AI advisory recommendations: {str(e)}"


# Backwards compatibility alias for audit function
def get_budget_recommendations(metrics: Dict[str, Any], currency_symbol: str = "₹") -> str:
    return generate_budget_advice(metrics.get("income", 0.0), metrics, currency_symbol)


def answer_what_if_scenario(
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    context: Optional[Dict[str, Any]] = None,
    currency_symbol: str = "₹"
) -> str:
    """
    Interactive scenario assistant evaluating 'What-If' queries (e.g., 'Can I afford a ₹15,000 flight this weekend?').
    Evaluates affordability against the user's remaining 'Wants' and 'Savings' ceilings in the active currency.
    """
    try:
        model = get_configured_model(PRO_MODEL)
        context_metrics = context or {}
        cur = currency_symbol
        
        history_formatted = ""
        if chat_history:
            for msg in chat_history[-6:]:  # Keep recent context
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_formatted += f"{role}: {msg.get('content', '')}\n"

        prompt = f"""
        You are the PocketSmart AI Scenario Modeling Assistant.
        The user is asking a "What-If" purchase or budgeting question in currency: {cur}.

        Current Verified Ledger & 50/30/20 Metrics ({cur}):
        - Monthly Income: {cur}{context_metrics.get('income', 0.0):,.2f}
        - Total Spent So Far: {cur}{context_metrics.get('total_spent', 0.0):,.2f}
        - Net Remaining Cash Flow: {cur}{context_metrics.get('net_cash_flow', 0.0):,.2f}
        - Needs: Target {cur}{context_metrics.get('targets', {}).get('Needs', 0.0):,.2f} | Spent {cur}{context_metrics.get('actuals', {}).get('Needs', 0.0):,.2f} | Remaining Headroom {cur}{context_metrics.get('variances', {}).get('Needs', 0.0):,.2f}
        - Wants: Target {cur}{context_metrics.get('targets', {}).get('Wants', 0.0):,.2f} | Spent {cur}{context_metrics.get('actuals', {}).get('Wants', 0.0):,.2f} | Remaining Headroom {cur}{context_metrics.get('variances', {}).get('Wants', 0.0):,.2f}
        - Savings: Target {cur}{context_metrics.get('targets', {}).get('Savings', 0.0):,.2f} | Allocated {cur}{context_metrics.get('actuals', {}).get('Savings', 0.0):,.2f} | Remaining Headroom {cur}{context_metrics.get('variances', {}).get('Savings', 0.0):,.2f}

        Recent Conversation History:
        {history_formatted}

        User Question:
        "{query}"

        Instructions:
        1. Classify the contemplated expense into Needs, Wants, or Savings.
        2. Evaluate affordability against the specific category's remaining budget ceiling and the total monthly cash flow using {cur}.
        3. Provide a clear **VERDICT** (e.g., ✅ Fully Affordable, ⚠️ Feasible with Trade-offs, or ❌ Deficit Risk).
        4. If it breaches the target ceiling, suggest exact category trade-offs in {cur}.
        5. Keep your tone empowering, concise, and mathematically consistent.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3
            )
        )
        return response.text
        
    except Exception as e:
        return f"⚠️ Unable to evaluate scenario: {str(e)}"


# Backwards compatibility alias
def ask_scenario_assistant(user_prompt: str, context_metrics: Dict[str, Any], chat_history: Optional[List[Dict[str, str]]] = None, currency_symbol: str = "₹") -> str:
    return answer_what_if_scenario(query=user_prompt, chat_history=chat_history, context=context_metrics, currency_symbol=currency_symbol)
