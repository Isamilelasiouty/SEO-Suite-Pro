"""
Database Layer for SEO Suite Pro:
- SQLite persistent storage with migration readiness for PostgreSQL / Supabase
- Multi-user isolation enforcing strict per-user data ownership
- Bcrypt password hashing and verification
- Admin aggregated analytics pipeline with zero access to private user data
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import bcrypt
from core.config import DATABASE_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database tables with indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            encrypted_api_key TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        """)
        
        # User analyses history (Strict isolation by user_id)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            target_name TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            data_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)
        
        # Anonymized system event metrics for Admin view
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_created ON system_metrics(created_at);")
        
        # Seed initial admin if no users exist
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw("admin12345".encode("utf-8"), salt).decode("utf-8")
            cursor.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?);
            """, ("admin", "admin@seosuitepro.local", hashed, "admin"))
            
        conn.commit()

def hash_password(password: str) -> str:
    """Hash password securely using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def register_user(username: str, email: str, password: str, role: str = "user") -> tuple[bool, str]:
    """Register a new user with validation."""
    username = username.strip().lower()
    email = email.strip().lower()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email:
        return False, "Invalid email address format."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
        
    hashed = hash_password(password)
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?);
            """, (username, email, hashed, role))
            conn.commit()
            record_metric_event("user_registered")
            return True, "User registered successfully."
    except sqlite3.IntegrityError as e:
        if "users.username" in str(e):
            return False, "Username already exists. Choose another."
        if "users.email" in str(e):
            return False, "Email already registered. Please sign in."
        return False, "User creation failed: duplicate record."
    except Exception as e:
        return False, f"Database error: {str(e)}"

def authenticate_user(username_or_email: str, password: str) -> dict | None:
    """Authenticate user credentials and update last login timestamp."""
    ident = username_or_email.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, username, email, password_hash, role, encrypted_api_key, created_at, last_login
        FROM users
        WHERE username = ? OR email = ?;
        """, (ident, ident))
        row = cursor.fetchone()
        if not row:
            return None
        
        if check_password(password, row["password_hash"]):
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?;", (row["id"],))
            conn.commit()
            record_metric_event("user_login", user_id=row["id"])
            return dict(row)
        return None

def get_user_by_id(user_id: int) -> dict | None:
    """Retrieve user dictionary by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, username, email, password_hash, role, encrypted_api_key, created_at, last_login
        FROM users
        WHERE id = ?;
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_user_api_key(user_id: int, encrypted_key: str):
    """Store encrypted API key in user profile."""
    with get_connection() as conn:
        conn.execute("UPDATE users SET encrypted_api_key = ? WHERE id = ?;", (encrypted_key, user_id))
        conn.commit()

def save_analysis(user_id: int, analysis_type: str, target_name: str, summary_dict: dict, data_dict: dict) -> int:
    """Save an analysis record strictly isolated to the authenticated user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO analyses (user_id, analysis_type, target_name, summary_json, data_json)
        VALUES (?, ?, ?, ?, ?);
        """, (
            user_id,
            analysis_type,
            target_name,
            json.dumps(summary_dict, default=str),
            json.dumps(data_dict, default=str)
        ))
        conn.commit()
        record_metric_event(f"analysis_{analysis_type}", user_id=user_id)
        return cursor.lastrowid

def get_user_analyses(user_id: int, analysis_type: str | None = None) -> list[dict]:
    """Retrieve history records strictly belonging to the given user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if analysis_type:
            cursor.execute("""
            SELECT id, user_id, analysis_type, target_name, summary_json, created_at
            FROM analyses
            WHERE user_id = ? AND analysis_type = ?
            ORDER BY created_at DESC;
            """, (user_id, analysis_type))
        else:
            cursor.execute("""
            SELECT id, user_id, analysis_type, target_name, summary_json, created_at
            FROM analyses
            WHERE user_id = ?
            ORDER BY created_at DESC;
            """, (user_id,))
        
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["summary"] = json.loads(d["summary_json"])
            except Exception:
                d["summary"] = {}
            results.append(d)
        return results

def get_analysis_by_id(analysis_id: int, user_id: int) -> dict | None:
    """Retrieve full analysis payload with user ownership verification."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, user_id, analysis_type, target_name, summary_json, data_json, created_at
        FROM analyses
        WHERE id = ? AND user_id = ?;
        """, (analysis_id, user_id))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["summary"] = json.loads(res["summary_json"])
        res["data"] = json.loads(res["data_json"])
        return res

def delete_analysis(analysis_id: int, user_id: int) -> bool:
    """Safely delete an analysis record owned by user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?;", (analysis_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def record_metric_event(event_type: str, user_id: int | None = None):
    """Log an anonymous system event for administrative platform metrics."""
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO system_metrics (event_type, user_id) VALUES (?, ?);", (event_type, user_id))
            conn.commit()
    except Exception:
        pass

def get_admin_metrics() -> dict:
    """
    Generate aggregated platform metrics for the Admin view.
    STRICT PRIVACY: Returns zero private user data, zero private audit URLs.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # User counts
        cursor.execute("SELECT COUNT(*) FROM users;")
        total_users = cursor.fetchone()[0]
        
        # Total analyses
        cursor.execute("SELECT COUNT(*) FROM analyses;")
        total_analyses = cursor.fetchone()[0]
        
        # Analyses by type
        cursor.execute("""
        SELECT analysis_type, COUNT(*) as cnt
        FROM analyses
        GROUP BY analysis_type;
        """)
        type_breakdown = {r["analysis_type"]: r["cnt"] for r in cursor.fetchall()}
        
        # Recent platform events count (last 7 days)
        cursor.execute("""
        SELECT COUNT(*)
        FROM system_metrics
        WHERE created_at >= date('now', '-7 days');
        """)
        recent_events = cursor.fetchone()[0]
        
        # Activity by day
        cursor.execute("""
        SELECT date(created_at) as day, COUNT(*) as cnt
        FROM system_metrics
        GROUP BY day
        ORDER BY day DESC
        LIMIT 14;
        """)
        daily_activity = [{"date": r["day"], "count": r["cnt"]} for r in cursor.fetchall()]
        
        return {
            "total_users": total_users,
            "total_analyses": total_analyses,
            "type_breakdown": type_breakdown,
            "recent_events_7d": recent_events,
            "daily_activity": daily_activity,
        }
