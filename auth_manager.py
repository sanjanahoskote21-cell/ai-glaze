"""
auth_manager.py - User Authentication, Roles & Saved Project Management
Handles:
  - SQLite database persistence (users.db)
  - SHA-256 salted password hashing
  - Role-based access: Homeowner vs. Professional Architect
  - Project history and portfolio saving
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite tables for users and saved projects."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Homeowner',
            city TEXT DEFAULT 'Bangalore',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Saved Projects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            room_type TEXT DEFAULT 'Living Room',
            style TEXT NOT NULL,
            budget REAL NOT NULL,
            grand_total REAL,
            floor_sqft REAL,
            wall_sqft REAL,
            boq_json TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    create_demo_accounts(cursor, conn)
    conn.close()

def hash_password(password: str) -> str:
    """Hashes password using SHA-256 with static salt."""
    salt = "aiglaze_secure_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

def create_demo_accounts(cursor, conn):
    """Pre-populates quick demo accounts for examiners/guides."""
    demo_users = [
        ("architect_demo", "architect@aiglaze.com", "demo123", "Ar. Sanjana Hoskote", "Professional Architect", "Bangalore"),
        ("homeowner_demo", "homeowner@aiglaze.com", "demo123", "Rahul Sharma", "Homeowner", "Bangalore")
    ]
    for username, email, pwd, name, role, city in demo_users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            pwd_hash = hash_password(pwd)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, role, city)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, pwd_hash, name, role, city))
    conn.commit()

def register_user(username, email, password, full_name, role="Homeowner", city="Bangalore"):
    """Registers a new user. Returns (success: bool, message: str, user_dict)"""
    if not username or not email or not password or not full_name:
        return False, "All fields are required.", None
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role, city)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username.strip().lower(), email.strip().lower(), pwd_hash, full_name.strip(), role, city.strip()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, "Registration successful! You can now log in.", {
            "id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": role,
            "city": city
        }
    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e).lower():
            return False, "Username is already taken. Please choose another.", None
        return False, "An account with this email already exists.", None
    except Exception as e:
        conn.close()
        return False, f"Database error: {str(e)}", None

def authenticate_user(username_or_email, password):
    """Authenticates a user. Returns (success: bool, message: str, user_dict)"""
    if not username_or_email or not password:
        return False, "Please provide both username/email and password.", None
        
    conn = get_connection()
    cursor = conn.cursor()
    identifier = username_or_email.strip().lower()
    pwd_hash = hash_password(password)
    
    cursor.execute('''
        SELECT id, username, email, full_name, role, city FROM users 
        WHERE (username = ? OR email = ?) AND password_hash = ?
    ''', (identifier, identifier, pwd_hash))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_dict = dict(row)
        return True, "Login successful!", user_dict
    else:
        return False, "Invalid username/email or password.", None

def save_user_project(user_id, project_name, style, budget, grand_total, floor_sqft, wall_sqft, boq_data, image_path=""):
    """Saves a generated redesign into the user portfolio."""
    conn = get_connection()
    cursor = conn.cursor()
    boq_str = json.dumps(boq_data) if boq_data else "{}"
    
    cursor.execute('''
        INSERT INTO projects (user_id, project_name, style, budget, grand_total, floor_sqft, wall_sqft, boq_json, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, project_name, style, budget, grand_total, floor_sqft, wall_sqft, boq_str, image_path))
    
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id

def get_user_projects(user_id):
    """Fetches all saved projects for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize tables immediately on import
init_db()
