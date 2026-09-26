"""
Database Layer for PocketSmart AI.
Provides thread-safe, idempotent SQLite persistence for:
1. User authentication and multi-user accounts
2. Baseline income and transaction ledgers
3. Specialized Planner recommendations & session history (Home, Party, Jewelry)
4. Enhanced Modules:
   - Monthly Household Budget Plans (Income, Fixed & Variable Costs, 50/30/20 Surpluses)
   - Trips & Vacation Expense Trackers (Trips ledger + itemized expense entries)
"""

import sqlite3
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pocketsmart.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection configured with sqlite3.Row factory."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Initializes tables idempotently."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Users table for authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. User profile table (singleton id=1 for backwards compatibility with budget engine)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                monthly_income REAL NOT NULL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Transactions ledger table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                date TEXT NOT NULL,
                merchant TEXT NOT NULL,
                item_name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL CHECK (category IN ('Needs', 'Wants', 'Savings')),
                receipt_id TEXT
            )
        """)
        
        # 4. Recommendation History table (for Home, Party, Jewelry, Monthly Budget, Trip Tracker)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                module_type TEXT NOT NULL, -- 'home', 'party', 'jewelry', 'monthly_budget', 'trip'
                title TEXT NOT NULL,
                budget REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'INR',
                user_inputs_json TEXT NOT NULL,
                plan_result_json TEXT NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Trips master table (for Trip Expense Tracker)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                trip_name TEXT NOT NULL,
                destination TEXT NOT NULL,
                budget REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'INR',
                start_date TEXT,
                end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 6. Trip expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trip_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                category TEXT NOT NULL, -- 'Flights/Transit', 'Hotels/Stay', 'Food & Dining', 'Activities', 'Shopping', 'Misc'
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
            )
        """)
        
        # Initialize default user profile row if missing (default to 0.0)
        cursor.execute("SELECT id FROM user_profile WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO user_profile (id, monthly_income) VALUES (1, 0.0)")
            
        conn.commit()


# =========================================================================
# User Management Functions
# =========================================================================

def create_user(email: str, full_name: str, hashed_password: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Creates a new registered user in SQLite."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (email, full_name, hashed_password)
                VALUES (?, ?, ?)
            """, (email.strip().lower(), full_name.strip(), hashed_password))
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "email": email.strip().lower(), "full_name": full_name.strip()}
        except sqlite3.IntegrityError:
            return None


def get_user_by_email(email: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves user by lowercase email."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, hashed_password, created_at FROM users WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves user by user ID."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


# =========================================================================
# Recommendation & Planner History Functions
# =========================================================================

def save_recommendation(
    module_type: str,
    title: str,
    budget: float,
    currency: str,
    user_inputs_json: str,
    plan_result_json: str,
    user_id: int = 1,
    image_path: Optional[str] = None,
    db_path: str = DB_PATH
) -> int:
    """Saves an AI-generated budget recommendation or manual calculation plan to history."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations (user_id, module_type, title, budget, currency, user_inputs_json, plan_result_json, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, module_type, title, float(budget), currency, user_inputs_json, plan_result_json, image_path))
        conn.commit()
        return cursor.lastrowid


def get_recommendations_by_user(user_id: Optional[int] = None, module_type: Optional[str] = None, limit: int = 50, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Fetches recommendation history logs, ordered newest first."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT id, user_id, module_type, title, budget, currency, user_inputs_json, plan_result_json, image_path, created_at FROM recommendations"
        params = []
        conditions = []
        if user_id is not None:
            conditions.append("user_id = ?")
            params.append(user_id)
        if module_type is not None:
            conditions.append("module_type = ?")
            params.append(module_type)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_recommendation_by_id(rec_id: int, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves single recommendation entry by primary key."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, module_type, title, budget, currency, user_inputs_json, plan_result_json, image_path, created_at
            FROM recommendations
            WHERE id = ?
        """, (rec_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


# =========================================================================
# Trip Expense Tracker Functions
# =========================================================================

def create_trip(
    user_id: int,
    trip_name: str,
    destination: str,
    budget: float,
    currency: str = "INR",
    start_date: str = "",
    end_date: str = "",
    db_path: str = DB_PATH
) -> int:
    """Creates a new trip record in SQLite."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trips (user_id, trip_name, destination, budget, currency, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, trip_name.strip(), destination.strip(), float(budget), currency, start_date, end_date))
        conn.commit()
        return cursor.lastrowid


def get_trips_by_user(user_id: Optional[int] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Fetches all trips with calculated total expenses and remaining balance."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("SELECT * FROM trips WHERE user_id = ? ORDER BY id DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM trips ORDER BY id DESC")
        trip_rows = cursor.fetchall()
        
        trips_list = []
        for t in trip_rows:
            trip_dict = dict(t)
            # Calculate total expenses for this trip
            cursor.execute("SELECT SUM(amount) as total_spent FROM trip_expenses WHERE trip_id = ?", (trip_dict["id"],))
            spent_row = cursor.fetchone()
            total_spent = float(spent_row["total_spent"]) if spent_row and spent_row["total_spent"] is not None else 0.0
            trip_dict["total_spent"] = total_spent
            trip_dict["remaining_budget"] = trip_dict["budget"] - total_spent
            trip_dict["utilization_pct"] = round((total_spent / trip_dict["budget"] * 100.0), 1) if trip_dict["budget"] > 0 else 0.0
            trips_list.append(trip_dict)
            
        return trips_list


def get_trip_by_id(trip_id: int, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Fetches single trip details along with its itemized expenses."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
        trip_row = cursor.fetchone()
        if not trip_row:
            return None
            
        trip_dict = dict(trip_row)
        cursor.execute("SELECT * FROM trip_expenses WHERE trip_id = ? ORDER BY expense_date DESC, id DESC", (trip_id,))
        expenses = [dict(r) for r in cursor.fetchall()]
        
        total_spent = sum(e["amount"] for e in expenses)
        trip_dict["expenses"] = expenses
        trip_dict["total_spent"] = total_spent
        trip_dict["remaining_budget"] = trip_dict["budget"] - total_spent
        trip_dict["utilization_pct"] = round((total_spent / trip_dict["budget"] * 100.0), 1) if trip_dict["budget"] > 0 else 0.0
        
        # Category breakdown aggregation
        cat_totals = {}
        for e in expenses:
            cat = e["category"]
            cat_totals[cat] = cat_totals.get(cat, 0.0) + float(e["amount"])
        trip_dict["category_totals"] = cat_totals
        
        return trip_dict


def add_trip_expense(
    trip_id: int,
    category: str,
    description: str,
    amount: float,
    expense_date: str = "",
    db_path: str = DB_PATH
) -> int:
    """Adds a single expense entry to a trip."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        date_val = expense_date if expense_date else datetime.today().strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO trip_expenses (trip_id, category, description, amount, expense_date)
            VALUES (?, ?, ?, ?, ?)
        """, (trip_id, category.strip(), description.strip(), float(amount), date_val))
        conn.commit()
        return cursor.lastrowid


# =========================================================================
# Legacy / Budget Engine Functions
# =========================================================================

def set_user_income(income: float, db_path: str = DB_PATH) -> None:
    """Updates or sets monthly baseline income for the user."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_profile (id, monthly_income, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                monthly_income = excluded.monthly_income,
                updated_at = CURRENT_TIMESTAMP
        """, (float(income),))
        conn.commit()


def get_user_income(db_path: str = DB_PATH) -> float:
    """Retrieves current baseline monthly income."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT monthly_income FROM user_profile WHERE id = 1")
        row = cursor.fetchone()
        if row and row["monthly_income"] is not None:
            return float(row["monthly_income"])
        return 0.0


def add_transactions(records: List[Dict[str, Any]], db_path: str = DB_PATH) -> int:
    """
    Inserts a batch of transaction records into the ledger table.
    Expects dict keys: date, merchant, item_name, amount, category, receipt_id (optional).
    """
    if not records:
        return 0
        
    init_db(db_path)
    inserted_count = 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for rec in records:
            category = str(rec.get("category", "Needs")).strip().capitalize()
            if category not in ("Needs", "Wants", "Savings"):
                category = "Needs"
                
            cursor.execute("""
                INSERT INTO transactions (date, merchant, item_name, amount, category, receipt_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(rec.get("date", datetime.today().strftime('%Y-%m-%d'))),
                str(rec.get("merchant", "Unknown Merchant")),
                str(rec.get("item_name", "Unspecified Expense")),
                float(rec.get("amount", 0.0)),
                category,
                rec.get("receipt_id", None)
            ))
            inserted_count += 1
        conn.commit()
    return inserted_count


def get_transactions(month: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetches all transactions or transactions for a specific YYYY-MM prefix.
    Returns list of dicts.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if month:
            cursor.execute("""
                SELECT id, date, merchant, item_name, amount, category, receipt_id
                FROM transactions
                WHERE date LIKE ?
                ORDER BY date DESC, id DESC
            """, (f"{month}%",))
        else:
            cursor.execute("""
                SELECT id, date, merchant, item_name, amount, category, receipt_id
                FROM transactions
                ORDER BY date DESC, id DESC
            """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def clear_all_transactions(db_path: str = DB_PATH, reset_income: bool = True) -> None:
    """Resets user transaction ledger and sets income back to 0.0."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        if reset_income:
            cursor.execute("UPDATE user_profile SET monthly_income = 0.0 WHERE id = 1")
        conn.commit()
