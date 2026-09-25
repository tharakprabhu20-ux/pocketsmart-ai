"""
Seed Data Script for PocketSmart AI.
Populates the SQLite database (pocketsmart.db) with realistic sample financial transactions
and baseline income to enable instant presentation-ready demonstration of all 50/30/20 analytics.
"""

import sys
import os
from datetime import datetime, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.db import init_db, set_user_income, add_transactions, clear_all_transactions, get_transactions, get_user_income
from backend.budget_engine import calculate_50_30_20_budget


def seed_database(income: float = 65000.0) -> None:
    """Populates pocketsmart.db with baseline user income and categorized transactions."""
    print("Initializing PocketSmart AI Database...")
    init_db()
    
    print("Clearing previous transactions...")
    clear_all_transactions()
    
    print(f"Setting baseline monthly net income to INR {income:,.2f}...")
    set_user_income(income)
    
    today = datetime.today()
    
    sample_records = [
        # --- NEEDS (Target: 50%) ---
        {
            "date": (today - timedelta(days=20)).strftime('%Y-%m-%d'),
            "merchant": "Apex Realty",
            "item_name": "Monthly Apartment Rent",
            "amount": 18000.0,
            "category": "Needs",
            "receipt_id": "REC-RENT-001"
        },
        {
            "date": (today - timedelta(days=15)).strftime('%Y-%m-%d'),
            "merchant": "Nature's Basket",
            "item_name": "Organic Monthly Groceries & Staples",
            "amount": 4250.0,
            "category": "Needs",
            "receipt_id": "REC-GROC-002"
        },
        {
            "date": (today - timedelta(days=10)).strftime('%Y-%m-%d'),
            "merchant": "State Electricity Board",
            "item_name": "Electricity & Power Utility",
            "amount": 2100.0,
            "category": "Needs",
            "receipt_id": "REC-UTIL-003"
        },
        {
            "date": (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            "merchant": "Apollo Pharmacy",
            "item_name": "Prescription Healthcare & Vitamins",
            "amount": 1450.0,
            "category": "Needs",
            "receipt_id": "REC-MED-004"
        },
        {
            "date": (today - timedelta(days=3)).strftime('%Y-%m-%d'),
            "merchant": "Metro Transit Authority",
            "item_name": "Monthly Commuter Metro Pass",
            "amount": 1200.0,
            "category": "Needs",
            "receipt_id": "REC-TRANS-005"
        },
        
        # --- WANTS (Target: 30%) ---
        {
            "date": (today - timedelta(days=18)).strftime('%Y-%m-%d'),
            "merchant": "The Bistro & Grill",
            "item_name": "Weekend Dinner with Friends",
            "amount": 2800.0,
            "category": "Wants",
            "receipt_id": "REC-DINE-006"
        },
        {
            "date": (today - timedelta(days=12)).strftime('%Y-%m-%d'),
            "merchant": "Netflix & Spotify",
            "item_name": "Digital Streaming Subscriptions",
            "amount": 1199.0,
            "category": "Wants",
            "receipt_id": "REC-SUB-007"
        },
        {
            "date": (today - timedelta(days=8)).strftime('%Y-%m-%d'),
            "merchant": "Zara Lifestyle",
            "item_name": "Casual Apparel & Sneakers",
            "amount": 4500.0,
            "category": "Wants",
            "receipt_id": "REC-SHOP-008"
        },
        {
            "date": (today - timedelta(days=2)).strftime('%Y-%m-%d'),
            "merchant": "Third Wave Coffee",
            "item_name": "Artisanal Coffee & Pastries",
            "amount": 650.0,
            "category": "Wants",
            "receipt_id": "REC-CAFE-009"
        },
        
        # --- SAVINGS (Target: 20%) ---
        {
            "date": (today - timedelta(days=22)).strftime('%Y-%m-%d'),
            "merchant": "Groww Mutual Funds",
            "item_name": "Nifty 50 Index Fund SIP",
            "amount": 7500.0,
            "category": "Savings",
            "receipt_id": "REC-INV-010"
        },
        {
            "date": (today - timedelta(days=5)).strftime('%Y-%m-%d'),
            "merchant": "HDFC Recurring Deposit",
            "item_name": "Emergency Fund Allocation",
            "amount": 3500.0,
            "category": "Savings",
            "receipt_id": "REC-SAV-011"
        }
    ]
    
    print(f"Injecting {len(sample_records)} realistic transaction records...")
    add_transactions(sample_records)
    
    # Audit metrics
    txs = get_transactions()
    current_inc = get_user_income()
    metrics = calculate_50_30_20_budget(current_inc, txs)
    
    print("\n" + "="*50)
    print("POCKETSMART AI SEED AUDIT")
    print("="*50)
    print(f"Monthly Net Income: INR {metrics['income']:,.2f}")
    print(f"Total Spent Logged: INR {metrics['total_spent']:,.2f} ({metrics['pct_income']['Total']}% of Income)")
    print(f"Remaining Cash Flow: INR {metrics['net_cash_flow']:,.2f}")
    print("\nCategory Performance:")
    print(f"  * Needs: Spent INR {metrics['actuals']['Needs']:,.2f} / Target INR {metrics['targets']['Needs']:,.2f} (Headroom: INR {metrics['variances']['Needs']:,.2f})")
    print(f"  * Wants: Spent INR {metrics['actuals']['Wants']:,.2f} / Target INR {metrics['targets']['Wants']:,.2f} (Headroom: INR {metrics['variances']['Wants']:,.2f})")
    print(f"  * Savings: Allocated INR {metrics['actuals']['Savings']:,.2f} / Target INR {metrics['targets']['Savings']:,.2f} (Headroom: INR {metrics['variances']['Savings']:,.2f})")
    print("="*50)
    print("Database seeding completed successfully!\n")


if __name__ == "__main__":
    seed_database()
