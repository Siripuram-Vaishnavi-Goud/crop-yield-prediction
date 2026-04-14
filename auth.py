"""utils/auth.py — Authentication helpers (SQLite-backed)"""

import sqlite3
import hashlib
import os
import streamlit as st

# Always store users.db in the project ROOT (parent of utils/)
# This works no matter where the script is run from on Windows
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))   # utils/
_ROOT_DIR  = os.path.dirname(_THIS_DIR)                    # project root
DB_PATH    = os.path.join(_ROOT_DIR, "users.db")


def init_db():
    """Create users table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            created  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, email: str, password: str):
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username.strip(), email.strip().lower(), _hash(password))
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        err = str(e).lower()
        if "username" in err:
            return False, "Username already taken. Choose a different username."
        if "email" in err:
            return False, "Email already registered. Try logging in instead."
        return False, str(e)
    except Exception as e:
        return False, f"Database error: {str(e)}"


def login_user(username: str, password: str):
    init_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT id, username FROM users WHERE username=? AND password=?",
            (username.strip(), _hash(password))
        ).fetchone()
        conn.close()
        if row:
            return True, row[1]
        # Check if username exists (to give better error)
        conn2 = sqlite3.connect(DB_PATH)
        user_exists = conn2.execute(
            "SELECT id FROM users WHERE username=?", (username.strip(),)
        ).fetchone()
        conn2.close()
        if user_exists:
            return False, "Wrong password. Please try again."
        return False, "Username not found. Please register first."
    except Exception as e:
        return False, f"Login error: {str(e)}"


def get_all_users():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, username, email, created FROM users"
    ).fetchall()
    conn.close()
    return rows


def delete_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def get_username() -> str:
    return st.session_state.get("username", "Guest")


def do_logout():
    for key in ["logged_in", "username"]:
        st.session_state.pop(key, None)


def get_db_path() -> str:
    """Return DB path for display in admin panel."""
    return DB_PATH