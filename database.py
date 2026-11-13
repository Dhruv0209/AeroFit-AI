"""
Database management for AI Fitness Planner
Handles SQLite persistence for users, workout plans, diet plans, activity logs, and chat history.
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitness_planner.db")


def get_db_connection():
    """Get a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hash password with sha256 and salt."""
    salt = "fit_planner_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER DEFAULT 28,
            gender TEXT DEFAULT 'Male',
            height_cm REAL DEFAULT 175.0,
            weight_kg REAL DEFAULT 75.0,
            target_weight_kg REAL DEFAULT 70.0,
            fitness_goal TEXT DEFAULT 'Weight Loss',
            activity_level TEXT DEFAULT 'Moderately Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Workout plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            goal TEXT,
            experience_level TEXT,
            split_type TEXT,
            equipment TEXT,
            duration_weeks INTEGER DEFAULT 4,
            plan_json TEXT NOT NULL,
            raw_markdown TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Diet plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            diet_type TEXT,
            target_calories INTEGER,
            target_protein INTEGER,
            target_carbs INTEGER,
            target_fats INTEGER,
            plan_json TEXT NOT NULL,
            raw_markdown TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Activity completion logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_type TEXT NOT NULL, -- 'workout' or 'diet'
            plan_id INTEGER NOT NULL,
            item_key TEXT NOT NULL,  -- e.g. 'day_1_ex_0' or 'day_1' or 'meal_breakfast'
            date_str TEXT NOT NULL,  -- 'YYYY-MM-DD'
            status TEXT NOT NULL,    -- 'completed', 'pending'
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, plan_type, plan_id, item_key, date_str),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Chat messages history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()

    # Create default demo user if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute("""
            INSERT INTO users (username, password_hash, name, age, gender, height_cm, weight_kg, target_weight_kg, fitness_goal, activity_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "demo_athlete",
            hash_password("fitness123"),
            "Alex Carter",
            28,
            "Male",
            178.0,
            78.0,
            72.0,
            "Weight Loss & Muscle Definition",
            "Moderately Active"
        ))
        conn.commit()

    conn.close()


# ---------------- USER FUNCTIONS ---------------- #

def register_user(username: str, password: str, name: str, **kwargs) -> Optional[int]:
    """Register a new user and return user id, or None if username exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, name, age, gender, height_cm, weight_kg, target_weight_kg, fitness_goal, activity_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username.strip().lower(),
            hash_password(password),
            name.strip(),
            kwargs.get("age", 28),
            kwargs.get("gender", "Male"),
            kwargs.get("height_cm", 175.0),
            kwargs.get("weight_kg", 75.0),
            kwargs.get("target_weight_kg", 70.0),
            kwargs.get("fitness_goal", "Weight Loss"),
            kwargs.get("activity_level", "Moderately Active"),
        ))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE username = ? AND password_hash = ?
    """, (username.strip().lower(), hash_password(password)))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user by id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_default_demo_user() -> Dict[str, Any]:
    """Retrieve demo user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def update_user_profile(user_id: int, **kwargs) -> bool:
    """Update profile attributes for a user."""
    allowed = ["name", "age", "gender", "height_cm", "weight_kg", "target_weight_kg", "fitness_goal", "activity_level"]
    fields = [f"{k} = ?" for k in kwargs if k in allowed]
    if not fields:
        return False
    values = [kwargs[k] for k in kwargs if k in allowed]
    values.append(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return True


# ---------------- WORKOUT PLANS ---------------- #

def save_workout_plan(user_id: int, title: str, plan_data: Dict[str, Any], raw_markdown: str = "",
                      goal: str = "", experience_level: str = "", split_type: str = "",
                      equipment: str = "", duration_weeks: int = 4) -> int:
    """Save a generated workout plan and set it as active."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Deactivate previous active plans for this user
    cursor.execute("UPDATE workout_plans SET is_active = 0 WHERE user_id = ?", (user_id,))

    cursor.execute("""
        INSERT INTO workout_plans (user_id, title, goal, experience_level, split_type, equipment, duration_weeks, plan_json, raw_markdown, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        user_id,
        title,
        goal,
        experience_level,
        split_type,
        equipment,
        duration_weeks,
        json.dumps(plan_data),
        raw_markdown
    ))
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id


def get_active_workout_plan(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch the currently active workout plan for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM workout_plans WHERE user_id = ? AND is_active = 1 ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    try:
        data["plan_data"] = json.loads(data["plan_json"])
    except Exception:
        data["plan_data"] = {}
    return data


def set_active_workout_plan(user_id: int, plan_id: int) -> bool:
    """Set a specific plan as the active workout plan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE workout_plans SET is_active = 0 WHERE user_id = ?", (user_id,))
    cursor.execute("UPDATE workout_plans SET is_active = 1 WHERE user_id = ? AND id = ?", (user_id, plan_id))
    conn.commit()
    conn.close()
    return True


def get_workout_history(user_id: int) -> List[Dict[str, Any]]:
    """Fetch list of all past workout plans for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, goal, experience_level, split_type, duration_weeks, is_active, created_at, plan_json
        FROM workout_plans WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["plan_data"] = json.loads(d["plan_json"])
        except Exception:
            d["plan_data"] = {}
        result.append(d)
    return result


def delete_workout_plan(user_id: int, plan_id: int) -> bool:
    """Delete a workout plan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workout_plans WHERE user_id = ? AND id = ?", (user_id, plan_id))
    cursor.execute("DELETE FROM activity_logs WHERE user_id = ? AND plan_type = 'workout' AND plan_id = ?", (user_id, plan_id))
    conn.commit()
    conn.close()
    return True


# ---------------- DIET PLANS ---------------- #

def save_diet_plan(user_id: int, title: str, plan_data: Dict[str, Any], raw_markdown: str = "",
                   diet_type: str = "", target_calories: int = 2000, target_protein: int = 150,
                   target_carbs: int = 200, target_fats: int = 65) -> int:
    """Save a generated diet plan and set it as active."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE diet_plans SET is_active = 0 WHERE user_id = ?", (user_id,))

    cursor.execute("""
        INSERT INTO diet_plans (user_id, title, diet_type, target_calories, target_protein, target_carbs, target_fats, plan_json, raw_markdown, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        user_id,
        title,
        diet_type,
        target_calories,
        target_protein,
        target_carbs,
        target_fats,
        json.dumps(plan_data),
        raw_markdown
    ))
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id


def get_active_diet_plan(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch active diet plan for user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM diet_plans WHERE user_id = ? AND is_active = 1 ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    try:
        data["plan_data"] = json.loads(data["plan_json"])
    except Exception:
        data["plan_data"] = {}
    return data


def set_active_diet_plan(user_id: int, plan_id: int) -> bool:
    """Set a specific plan as active diet plan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE diet_plans SET is_active = 0 WHERE user_id = ?", (user_id,))
    cursor.execute("UPDATE diet_plans SET is_active = 1 WHERE user_id = ? AND id = ?", (user_id, plan_id))
    conn.commit()
    conn.close()
    return True


def get_diet_history(user_id: int) -> List[Dict[str, Any]]:
    """Fetch list of all past diet plans for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, diet_type, target_calories, target_protein, target_carbs, target_fats, is_active, created_at, plan_json
        FROM diet_plans WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["plan_data"] = json.loads(d["plan_json"])
        except Exception:
            d["plan_data"] = {}
        result.append(d)
    return result


def delete_diet_plan(user_id: int, plan_id: int) -> bool:
    """Delete a diet plan."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diet_plans WHERE user_id = ? AND id = ?", (user_id, plan_id))
    cursor.execute("DELETE FROM activity_logs WHERE user_id = ? AND plan_type = 'diet' AND plan_id = ?", (user_id, plan_id))
    conn.commit()
    conn.close()
    return True


# ---------------- ACTIVITY LOGS & COMPLETION ---------------- #

def toggle_activity_status(user_id: int, plan_type: str, plan_id: int, item_key: str, date_str: Optional[str] = None) -> bool:
    """Toggle completion status of an exercise, workout, or meal."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status FROM activity_logs
        WHERE user_id = ? AND plan_type = ? AND plan_id = ? AND item_key = ? AND date_str = ?
    """, (user_id, plan_type, plan_id, item_key, date_str))
    row = cursor.fetchone()

    if row and row["status"] == "completed":
        cursor.execute("""
            DELETE FROM activity_logs
            WHERE user_id = ? AND plan_type = ? AND plan_id = ? AND item_key = ? AND date_str = ?
        """, (user_id, plan_type, plan_id, item_key, date_str))
        is_completed = False
    else:
        cursor.execute("""
            INSERT OR REPLACE INTO activity_logs (user_id, plan_type, plan_id, item_key, date_str, status, completed_at)
            VALUES (?, ?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP)
        """, (user_id, plan_type, plan_id, item_key, date_str))
        is_completed = True

    conn.commit()
    conn.close()
    return is_completed


def get_completed_items_set(user_id: int, plan_type: str, plan_id: int, date_str: Optional[str] = None) -> set:
    """Return a set of item keys marked as completed for a given plan and date."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT item_key FROM activity_logs
        WHERE user_id = ? AND plan_type = ? AND plan_id = ? AND date_str = ? AND status = 'completed'
    """, (user_id, plan_type, plan_id, date_str))
    rows = cursor.fetchall()
    conn.close()
    return {r["item_key"] for r in rows}


def get_user_activity_stats(user_id: int) -> Dict[str, Any]:
    """Calculate summary completion stats for user dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Completed exercises today
    cursor.execute("""
        SELECT COUNT(*) as count FROM activity_logs
        WHERE user_id = ? AND date_str = ? AND status = 'completed' AND plan_type = 'workout'
    """, (user_id, today_str))
    workouts_today = cursor.fetchone()["count"]

    # Total completed workouts all-time
    cursor.execute("""
        SELECT COUNT(*) as count FROM activity_logs
        WHERE user_id = ? AND status = 'completed' AND plan_type = 'workout'
    """, (user_id,))
    total_completed = cursor.fetchone()["count"]

    # Total plans created
    cursor.execute("SELECT COUNT(*) as count FROM workout_plans WHERE user_id = ?", (user_id,))
    total_workout_plans = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM diet_plans WHERE user_id = ?", (user_id,))
    total_diet_plans = cursor.fetchone()["count"]

    conn.close()

    return {
        "today_completed_exercises": workouts_today,
        "total_completed_exercises": total_completed,
        "total_workout_plans": total_workout_plans,
        "total_diet_plans": total_diet_plans,
    }


# ---------------- CHAT HISTORY ---------------- #

def save_chat_message(user_id: int, role: str, content: str):
    """Save a message to chat history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (user_id, role, content)
        VALUES (?, ?, ?)
    """, (user_id, role, content))
    conn.commit()
    conn.close()


def get_chat_history(user_id: int, limit: int = 50) -> List[Dict[str, str]]:
    """Retrieve recent chat history for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM chat_history
        WHERE user_id = ? ORDER BY id ASC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def clear_chat_history(user_id: int):
    """Clear chat history for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# Auto-initialize DB on module import
init_db()

