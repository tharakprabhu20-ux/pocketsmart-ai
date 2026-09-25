"""
Deterministic Budget Engine for PocketSmart AI.
Strictly implements the 50/30/20 financial rule with pure Python arithmetic.
Guarantees zero LLM arithmetic hallucinations.
"""

from typing import List, Dict, Any


def calculate_50_30_20_budget(income: float, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes absolute category sums, target vs. actual variance ($ and %),
    total spent, and net cash flow according to the 50/30/20 framework:
      - Target Needs = Income * 0.50
      - Target Wants = Income * 0.30
      - Target Savings = Income * 0.20
    """
    safe_income = max(0.0, float(income))
    
    # Target calculations
    target_needs = round(safe_income * 0.50, 2)
    target_wants = round(safe_income * 0.30, 2)
    target_savings = round(safe_income * 0.20, 2)
    
    # Aggregate actuals
    actual_needs = 0.0
    actual_wants = 0.0
    actual_savings = 0.0
    
    for tx in transactions:
        cat = str(tx.get("category", "")).strip().capitalize()
        amount = max(0.0, float(tx.get("amount", 0.0)))
        if cat == "Needs":
            actual_needs += amount
        elif cat == "Wants":
            actual_wants += amount
        elif cat == "Savings":
            actual_savings += amount
            
    actual_needs = round(actual_needs, 2)
    actual_wants = round(actual_wants, 2)
    actual_savings = round(actual_savings, 2)
    
    total_spent = round(actual_needs + actual_wants + actual_savings, 2)
    net_cash_flow = round(safe_income - total_spent, 2)
    
    # Dollar variance (Target - Actual): Positive means under budget (surplus), negative means over budget (deficit)
    variance_needs_dollar = round(target_needs - actual_needs, 2)
    variance_wants_dollar = round(target_wants - actual_wants, 2)
    variance_savings_dollar = round(target_savings - actual_savings, 2)
    
    # Percent of Income spent in each category
    pct_income_needs = round((actual_needs / safe_income * 100), 1) if safe_income > 0 else 0.0
    pct_income_wants = round((actual_wants / safe_income * 100), 1) if safe_income > 0 else 0.0
    pct_income_savings = round((actual_savings / safe_income * 100), 1) if safe_income > 0 else 0.0
    pct_income_total = round((total_spent / safe_income * 100), 1) if safe_income > 0 else 0.0
    
    # Category utilization (% of category target spent)
    utilization_needs = round((actual_needs / target_needs * 100), 1) if target_needs > 0 else 0.0
    utilization_wants = round((actual_wants / target_wants * 100), 1) if target_wants > 0 else 0.0
    utilization_savings = round((actual_savings / target_savings * 100), 1) if target_savings > 0 else 0.0

    return {
        "income": safe_income,
        "total_spent": total_spent,
        "net_cash_flow": net_cash_flow,
        "targets": {
            "Needs": target_needs,
            "Wants": target_wants,
            "Savings": target_savings,
        },
        "actuals": {
            "Needs": actual_needs,
            "Wants": actual_wants,
            "Savings": actual_savings,
        },
        "variances": {
            "Needs": variance_needs_dollar,
            "Wants": variance_wants_dollar,
            "Savings": variance_savings_dollar,
        },
        "pct_income": {
            "Needs": pct_income_needs,
            "Wants": pct_income_wants,
            "Savings": pct_income_savings,
            "Total": pct_income_total,
        },
        "utilization": {
            "Needs": utilization_needs,
            "Wants": utilization_wants,
            "Savings": utilization_savings,
        }
    }


# Backwards compatibility alias
calculate_budget_metrics = calculate_50_30_20_budget
