"""
Database Layer for PocketSmart AI.
Provides thread-safe, idempotent SQLite persistence for user financial profiles and transactions.
"""

import sqlite3
import os
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
        
        # User profile table (singleton id=1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                monthly_income REAL NOT NULL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions ledger table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                merchant TEXT NOT NULL,
                item_name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL CHECK (category IN ('Needs', 'Wants', 'Savings')),
                receipt_id TEXT
            )
        """)
        
        # Initialize default user profile row if missing (default to 0.0)
        cursor.execute("SELECT id FROM user_profile WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO user_profile (id, monthly_income) VALUES (1, 0.0)")
            
        conn.commit()


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
