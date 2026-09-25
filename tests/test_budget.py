"""
Unit Test Suite for PocketSmart AI Budget Engine and Database.
Validates 50/30/20 arithmetic, category sum accuracy, and edge cases.
Compatible with pytest and standard library unittest.
"""

import os
import unittest
import tempfile
from backend.budget_engine import calculate_50_30_20_budget
from backend.db import (
    init_db,
    set_user_income,
    get_user_income,
    add_transactions,
    get_transactions,
    clear_all_transactions
)


class TestBudgetEngine(unittest.TestCase):
    
    def test_standard_50_30_20_calculation(self):
        income = 5000.0
        transactions = [
            {"item_name": "Rent", "amount": 2000.0, "category": "Needs"},
            {"item_name": "Groceries", "amount": 300.0, "category": "Needs"},
            {"item_name": "Dining", "amount": 500.0, "category": "Wants"},
            {"item_name": "Shopping", "amount": 200.0, "category": "Wants"},
            {"item_name": "Index Fund", "amount": 800.0, "category": "Savings"},
        ]
        
        metrics = calculate_50_30_20_budget(income, transactions)
        
        # Targets
        self.assertEqual(metrics["targets"]["Needs"], 2500.0)
        self.assertEqual(metrics["targets"]["Wants"], 1500.0)
        self.assertEqual(metrics["targets"]["Savings"], 1000.0)
        
        # Actuals
        self.assertEqual(metrics["actuals"]["Needs"], 2300.0)
        self.assertEqual(metrics["actuals"]["Wants"], 700.0)
        self.assertEqual(metrics["actuals"]["Savings"], 800.0)
        self.assertEqual(metrics["total_spent"], 3800.0)
        self.assertEqual(metrics["net_cash_flow"], 1200.0)
        
        # Variances (Target - Actual)
        self.assertEqual(metrics["variances"]["Needs"], 200.0)
        self.assertEqual(metrics["variances"]["Wants"], 800.0)
        self.assertEqual(metrics["variances"]["Savings"], 200.0)
        
        # Pct of income
        self.assertEqual(metrics["pct_income"]["Needs"], 46.0)
        self.assertEqual(metrics["pct_income"]["Wants"], 14.0)
        self.assertEqual(metrics["pct_income"]["Savings"], 16.0)
        self.assertEqual(metrics["pct_income"]["Total"], 76.0)

    def test_zero_income_edge_case(self):
        income = 0.0
        transactions = [
            {"item_name": "Coffee", "amount": 5.0, "category": "Wants"}
        ]
        metrics = calculate_50_30_20_budget(income, transactions)
        
        self.assertEqual(metrics["income"], 0.0)
        self.assertEqual(metrics["targets"]["Needs"], 0.0)
        self.assertEqual(metrics["targets"]["Wants"], 0.0)
        self.assertEqual(metrics["targets"]["Savings"], 0.0)
        self.assertEqual(metrics["actuals"]["Wants"], 5.0)
        self.assertEqual(metrics["net_cash_flow"], -5.0)
        self.assertEqual(metrics["pct_income"]["Wants"], 0.0)
        self.assertEqual(metrics["utilization"]["Wants"], 0.0)

    def test_zero_expenses_edge_case(self):
        income = 4000.0
        transactions = []
        metrics = calculate_50_30_20_budget(income, transactions)
        
        self.assertEqual(metrics["total_spent"], 0.0)
        self.assertEqual(metrics["net_cash_flow"], 4000.0)
        self.assertEqual(metrics["actuals"]["Needs"], 0.0)
        self.assertEqual(metrics["actuals"]["Wants"], 0.0)
        self.assertEqual(metrics["actuals"]["Savings"], 0.0)
        self.assertEqual(metrics["variances"]["Needs"], 2000.0)
        self.assertEqual(metrics["variances"]["Wants"], 1200.0)
        self.assertEqual(metrics["variances"]["Savings"], 800.0)

    def test_overage_budget_deficit(self):
        income = 2000.0
        transactions = [
            {"item_name": "Luxury Hotel", "amount": 1500.0, "category": "Wants"}
        ]
        metrics = calculate_50_30_20_budget(income, transactions)
        
        self.assertEqual(metrics["targets"]["Wants"], 600.0)
        self.assertEqual(metrics["actuals"]["Wants"], 1500.0)
        self.assertEqual(metrics["variances"]["Wants"], -900.0)
        self.assertEqual(metrics["utilization"]["Wants"], 250.0)


class TestDatabaseLayer(unittest.TestCase):
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_file.name
        self.temp_file.close()
        init_db(self.temp_db_path)

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except Exception:
                pass

    def test_user_income_crud(self):
        self.assertEqual(get_user_income(self.temp_db_path), 0.0)
        set_user_income(7500.0, self.temp_db_path)
        self.assertEqual(get_user_income(self.temp_db_path), 7500.0)
        set_user_income(8200.50, self.temp_db_path)
        self.assertEqual(get_user_income(self.temp_db_path), 8200.50)

    def test_transactions_crud(self):
        records = [
            {"date": "2026-09-01", "merchant": "Whole Foods", "item_name": "Organic Milk", "amount": 6.50, "category": "Needs"},
            {"date": "2026-09-02", "merchant": "Steam", "item_name": "Indie Game", "amount": 19.99, "category": "Wants"}
        ]
        add_transactions(records, self.temp_db_path)
        txs = get_transactions(db_path=self.temp_db_path)
        self.assertEqual(len(txs), 2)
        
        merchants = [t["merchant"] for t in txs]
        self.assertIn("Whole Foods", merchants)
        self.assertIn("Steam", merchants)
        
        clear_all_transactions(self.temp_db_path)
        self.assertEqual(len(get_transactions(db_path=self.temp_db_path)), 0)


if __name__ == "__main__":
    unittest.main()
