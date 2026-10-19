"""
Authentication and Session Manager for SEO Suite Pro:
Handles Streamlit session state, login gating, and role-based permissions.
"""

import streamlit as st
from core.database import authenticate_user, register_user, get_user_by_id

SESSION_USER_KEY = "current_user"

def get_current_user() -> dict | None:
    """Retrieve currently authenticated user from session state."""
    return st.session_state.get(SESSION_USER_KEY)

def is_authenticated() -> bool:
    """Check if session is currently authenticated."""
    return get_current_user() is not None

def is_admin() -> bool:
    """Check if currently authenticated user has admin role."""
    user = get_current_user()
    return bool(user and user.get("role") == "admin")

def login_user(user: dict):
    """Store user in session state."""
    st.session_state[SESSION_USER_KEY] = user

def logout_user():
    """Clear user session state and sensitive caches."""
    st.session_state.pop(SESSION_USER_KEY, None)
    st.session_state.pop("gemini_api_key", None)
    st.session_state.pop("active_analysis_data", None)
    st.rerun()

def refresh_user():
    """Reload user data from database to capture profile or API key updates."""
    user = get_current_user()
    if user and user.get("id"):
        updated = get_user_by_id(user["id"])
        if updated:
            st.session_state[SESSION_USER_KEY] = updated
