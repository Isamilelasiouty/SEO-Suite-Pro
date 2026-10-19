"""
═══════════════════════════════════════════════════════════════
SEO Suite Pro — Enterprise Technical SEO & Organic Intelligence
Architect: Ismail El Asiouty
Palette: Gold (#D4AF37), Black (#0B0B0B, #141414, #1C1C1C), White (#FFFFFF)
STRICT: Zero emojis, pure refined typography, responsive layout
═══════════════════════════════════════════════════════════════
"""

from pathlib import Path
import streamlit as st

# Core database and auth
from core.auth import get_current_user, is_admin, is_authenticated, logout_user
from core.config import (
    ASSETS_DIR,
    BRAND_NAME,
    BRAND_OWNER,
    BRAND_ROLE,
    LINKEDIN_URL,
    LOGO_PATH,
    PHONE_NUMBER,
    PORTFOLIO_URL,
    WHATSAPP_URL,
)
from core.database import init_db

# Views
from views.components import get_logo_base64
from views.view_admin import render_admin_view
from views.view_auth import render_auth_view
from views.view_contact import render_contact_view
from views.view_dashboard import render_dashboard_view
from views.view_gemini import render_gemini_view
from views.view_gsc import render_gsc_view
from views.view_history import render_history_view
from views.view_offpage import render_offpage_view
from views.view_onpage import render_onpage_view

# Initialize database schema
init_db()

# ─── Streamlit Page Configuration ────────────────────────────────
favicon_target = str(LOGO_PATH) if LOGO_PATH.exists() else None

st.set_page_config(
    page_title=f"{BRAND_NAME} — {BRAND_OWNER}",
    page_icon=favicon_target,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS Injection ────────────────────────────────────────
css_path = ASSETS_DIR / "custom.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Authentication Gateway ──────────────────────────────────────
if not is_authenticated():
    with st.sidebar:
        logo_uri = get_logo_base64()
        if logo_uri:
            st.markdown(f'<div style="text-align:center;padding:16px 0;"><img src="{logo_uri}" style="width:56px;height:56px;border-radius:10px;border:1px solid #D4AF37;object-fit:cover;" /></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center;padding:0 10px 16px;">
            <div style="font-family:'Poppins',sans-serif;font-size:18px;font-weight:800;color:#D4AF37;">{BRAND_NAME}</div>
            <div style="font-size:11px;color:#A0A0A0;margin-top:2px;">{BRAND_OWNER}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:12px;color:#A0A0A0;line-height:1.7;">
            Welcome to SEO Suite Pro. Sign in to access your private technical audit vault, 
            Search Console analysis, and AI optimization roadmaps.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:#777777;text-align:center;">
            Built by {BRAND_OWNER}<br/>
            <a href="{PORTFOLIO_URL}" target="_blank" style="color:#D4AF37;text-decoration:none;">Portfolio</a> &bull; 
            <a href="{LINKEDIN_URL}" target="_blank" style="color:#D4AF37;text-decoration:none;">LinkedIn</a>
        </div>
        """, unsafe_allow_html=True)
    render_auth_view()
    st.stop()
else:
    # ─── Authenticated User Workspace ────────────────────────────────
    user = get_current_user()

    # Sidebar Navigation
    with st.sidebar:
        logo_uri = get_logo_base64()
        if logo_uri:
            st.markdown(f'<div style="text-align:center;padding:12px 0 8px;"><img src="{logo_uri}" style="width:54px;height:54px;border-radius:10px;border:1px solid #D4AF37;object-fit:cover;" /></div>', unsafe_allow_html=True)
            
        st.markdown(f"""
        <div style="text-align:center;padding-bottom:12px;">
            <div style="font-family:'Poppins',sans-serif;font-size:18px;font-weight:800;color:#D4AF37;">{BRAND_NAME}</div>
            <div style="font-size:11px;color:#A0A0A0;">{BRAND_ROLE}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile Pill
        role_badge = "[ADMIN]" if user and user.get("role") == "admin" else "[USER]"
        username_display = user["username"] if user else "Analyst"
        st.markdown(f"""
        <div style="background:#141414;border:1px solid rgba(212,175,55,0.25);border-radius:8px;padding:10px 14px;margin-bottom:16px;">
            <div style="font-size:10px;color:#A0A0A0;text-transform:uppercase;letter-spacing:0.05em;">Active Account</div>
            <div style="font-size:13px;font-weight:700;color:#FFFFFF;margin-top:2px;">{username_display} <span style="font-size:10px;color:#D4AF37;">{role_badge}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation Options (Strictly text labels, zero emojis)
        nav_options = [
            "Executive Dashboard",
            "On-Page Audit",
            "Search Console",
            "Off-Page Analysis",
            "Gemini AI Assistant",
            "Private History",
            "Contact & Architecture"
        ]
        if is_admin():
            nav_options.insert(6, "Admin Analytics")
            
        # Check if a jump target was set in session state
        nav_target = st.session_state.pop("nav_target", None)
        default_index = 0
        if nav_target and nav_target in nav_options:
            default_index = nav_options.index(nav_target)
            
        selected_page = st.radio(
            "Navigation",
            nav_options,
            index=default_index,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            logout_user()
            
        st.markdown(f"""
        <div style="padding-top:20px;text-align:center;font-size:11px;color:#777777;line-height:1.7;">
            Built by <strong style="color:#D4AF37;">{BRAND_OWNER}</strong><br/>
            <a href="{PORTFOLIO_URL}" target="_blank" style="color:#D4AF37;text-decoration:none;">Portfolio</a> &bull; 
            <a href="{LINKEDIN_URL}" target="_blank" style="color:#D4AF37;text-decoration:none;">LinkedIn</a> &bull; 
            <a href="{WHATSAPP_URL}" target="_blank" style="color:#D4AF37;text-decoration:none;">WhatsApp</a>
        </div>
        """, unsafe_allow_html=True)

    # ─── Page Router ─────────────────────────────────────────────────
    if selected_page == "Executive Dashboard":
        render_dashboard_view()
    elif selected_page == "On-Page Audit":
        render_onpage_view()
    elif selected_page == "Search Console":
        render_gsc_view()
    elif selected_page == "Off-Page Analysis":
        render_offpage_view()
    elif selected_page == "Gemini AI Assistant":
        render_gemini_view()
    elif selected_page == "Private History":
        render_history_view()
    elif selected_page == "Admin Analytics":
        render_admin_view()
    elif selected_page == "Contact & Architecture":
        render_contact_view()
