"""
auth_manager.py - Lead: Teammate A & Tech Lead
AI-GLAZE Authentication & Project Portfolio Database Manager
Uses SQLite (users.db) with secure SHA-256 password hashing & salt.
Supports role-based user management (Architect / Homeowner) and project persistence.
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Creates a database connection with dict-like row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a password with a cryptographic salt using SHA-256."""
    if not salt:
        salt = os.urandom(16).hex()
    salted = (password + salt).encode("utf-8")
    pwd_hash = hashlib.sha256(salted).hexdigest()
    return pwd_hash, salt


def init_db(db_path: str = DB_PATH):
    """Initializes tables for users and saved design portfolios, and seeds demo accounts."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL,
        city TEXT DEFAULT 'Bangalore',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Projects Portfolio Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        project_name TEXT NOT NULL,
        style TEXT NOT NULL,
        target_surface TEXT,
        surface_material TEXT,
        budget_inr REAL,
        estimated_cost_inr REAL,
        floor_sqft REAL,
        wall_sqft REAL,
        preview_image_path TEXT,
        detected_items_count INTEGER DEFAULT 0,
        metadata_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()

    # Seed Quick Demo Accounts if table is empty or accounts do not exist
    demo_accounts = [
        {
            "full_name": "Ar. Sanjana Hoskote",
            "username": "sanjana_arch",
            "email": "sanjana@aiglaze.in",
            "password": "demo123",
            "role": "Professional Architect / Interior Designer",
            "city": "Bangalore"
        },
        {
            "full_name": "Rahul Sharma",
            "username": "rahul_home",
            "email": "rahul@gmail.com",
            "password": "demo123",
            "role": "Homeowner / DIY Renovator",
            "city": "Mumbai"
        }
    ]

    for acc in demo_accounts:
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (acc["username"], acc["email"]))
        if not cursor.fetchone():
            pwd_hash, salt = hash_password(acc["password"])
            cursor.execute("""
                INSERT INTO users (full_name, username, email, password_hash, salt, role, city)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (acc["full_name"], acc["username"], acc["email"], pwd_hash, salt, acc["role"], acc["city"]))

    conn.commit()
    conn.close()


def register_user(
    full_name: str,
    username: str,
    email: str,
    password: str,
    role: str = "Homeowner / DIY Renovator",
    city: str = "Bangalore",
    db_path: str = DB_PATH
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Registers a new user account with validated credentials."""
    full_name = full_name.strip()
    username = username.strip().lower()
    email = email.strip().lower()

    if not full_name or not username or not email or not password:
        return False, "All registration fields are required.", None

    if len(password) < 4:
        return False, "Password must be at least 4 characters long.", None

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, f"Username '{username}' is already registered.", None

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, f"Email '{email}' is already registered.", None

        pwd_hash, salt = hash_password(password)
        cursor.execute("""
            INSERT INTO users (full_name, username, email, password_hash, salt, role, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (full_name, username, email, pwd_hash, salt, role, city))

        user_id = cursor.lastrowid
        conn.commit()

        user_dict = {
            "id": user_id,
            "full_name": full_name,
            "username": username,
            "email": email,
            "role": role,
            "city": city
        }
        return True, "Account created successfully!", user_dict

    except sqlite3.IntegrityError as e:
        return False, f"Account creation failed: {e}", None
    finally:
        conn.close()


def authenticate_user(
    username_or_email: str,
    password: str,
    db_path: str = DB_PATH
) -> Optional[Dict[str, Any]]:
    """Authenticates user credentials against the SQLite database."""
    identifier = username_or_email.strip().lower()
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?
    """, (identifier, identifier))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    stored_hash = row["password_hash"]
    salt = row["salt"]
    check_hash, _ = hash_password(password, salt=salt)

    if check_hash == stored_hash:
        user_info = {
            "id": row["id"],
            "full_name": row["full_name"],
            "username": row["username"],
            "email": row["email"],
            "role": row["role"],
            "city": row["city"],
            "created_at": row["created_at"]
        }
        conn.close()
        return user_info

    conn.close()
    return None


def save_user_project(user_id: int, project_data: Dict[str, Any], db_path: str = DB_PATH) -> int:
    """Saves a room design configuration into the user's persistent portfolio."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    metadata_str = json.dumps(project_data.get("metadata", {}))

    cursor.execute("""
        INSERT INTO projects (
            user_id, project_name, style, target_surface, surface_material,
            budget_inr, estimated_cost_inr, floor_sqft, wall_sqft,
            preview_image_path, detected_items_count, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        project_data.get("project_name", "Untitled Living Room"),
        project_data.get("style", "Scandinavian Minimalist"),
        project_data.get("target_surface", "floor"),
        project_data.get("surface_material", "Italian Carrara Marble"),
        float(project_data.get("budget_inr", 150000.0)),
        float(project_data.get("estimated_cost_inr", 132000.0)),
        float(project_data.get("floor_sqft", 138.0)),
        float(project_data.get("wall_sqft", 401.5)),
        project_data.get("preview_image_path", "redesign_output.png"),
        int(project_data.get("detected_items_count", 0)),
        metadata_str
    ))

    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id


def get_user_projects(user_id: int, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all saved projects for a specific user, sorted from newest to oldest."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()

    projects = []
    for r in rows:
        p_dict = dict(r)
        if p_dict.get("metadata_json"):
            try:
                p_dict["metadata"] = json.loads(p_dict["metadata_json"])
            except Exception:
                p_dict["metadata"] = {}
        projects.append(p_dict)

    conn.close()
    return projects


def delete_user_project(project_id: int, user_id: int, db_path: str = DB_PATH) -> bool:
    """Deletes a portfolio project owned by the user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# Ensure database is automatically ready upon module import
init_db()

if __name__ == "__main__":
    print(f"✅ auth_manager database initialized at: {DB_PATH}")
    test_user = authenticate_user("sanjana_arch", "demo123")
    if test_user:
        print(f"✅ Demo auth test passed for: {test_user['full_name']} ({test_user['role']})")
