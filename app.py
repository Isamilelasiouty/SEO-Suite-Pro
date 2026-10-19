"""
═══════════════════════════════════════════════════════════════
SEO Suite Pro — Enterprise Technical SEO & Organic Intelligence
Architect: Ismail El Asiouty
Design System: Gold (#D4AF37), Black (#0B0B0B), White (#FFFFFF)
Dynamic Light / Dark Theme & Full Arabic / English Bilingual Support
═══════════════════════════════════════════════════════════════
"""

from pathlib import Path
import streamlit as st

# Core database, auth, and internationalization
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
from core.i18n import get_current_lang, set_lang, t

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

# ─── Initialize Session State Defaults ───────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

# ─── Streamlit Page Configuration ────────────────────────────────
favicon_target = str(LOGO_PATH) if LOGO_PATH.exists() else None

st.set_page_config(
    page_title=f"{BRAND_NAME} — {BRAND_OWNER}",
    page_icon=favicon_target,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Base CSS Injection ──────────────────────────────────────────
css_path = ASSETS_DIR / "custom.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Dynamic Theme & RTL Overrides ───────────────────────────────
active_theme = st.session_state.get("theme", "dark")
active_lang = st.session_state.get("lang", "en")

if active_theme == "light":
    st.markdown("""
    <style>
    :root, .stApp, section[data-testid="stSidebar"] {
        --bg-primary: #F8F9FA !important;
        --bg-surface: #FFFFFF !important;
        --bg-elevated: #F1F3F5 !important;
        --bg-gradient: radial-gradient(circle at 50% 0%, rgba(212, 175, 55, 0.08) 0%, rgba(248, 249, 250, 0.99) 75%), #F8F9FA !important;
        --gold: #B8860B !important;
        --gold-hover: #996515 !important;
        --gold-glow: rgba(184, 134, 11, 0.25) !important;
        --gold-tint: rgba(212, 175, 55, 0.08) !important;
        --gold-border: rgba(184, 134, 11, 0.3) !important;
        --text-primary: #111827 !important;
        --text-soft: #1F2937 !important;
        --text-muted: #4B5563 !important;
        --shadow-card: 0 4px 16px rgba(0, 0, 0, 0.06) !important;
        --sidebar-bg: linear-gradient(180deg, #FFFFFF 0%, #F3F4F6 100%) !important;
        --input-bg: #FFFFFF !important;
        --input-border: rgba(184, 134, 11, 0.3) !important;
    }
    .stApp {
        background: var(--bg-gradient) !important;
        color: #1F2937 !important;
    }
    .metric-card, .glass-card, .gsc-upload-zone {
        background: #FFFFFF !important;
        border: 1px solid rgba(184, 134, 11, 0.25) !important;
        color: #1F2937 !important;
    }
    .metric-card:hover, .glass-card:hover {
        box-shadow: 0 8px 24px rgba(184, 134, 11, 0.15) !important;
        border-color: #B8860B !important;
    }
    .card-label {
        color: #6B7280 !important;
    }
    .card-value {
        color: #B8860B !important;
    }
    .card-subtitle {
        color: #6B7280 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
    }
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid rgba(184, 134, 11, 0.2) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1F2937 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #F3F4F6 !important;
        border: 1px solid rgba(184, 134, 11, 0.2) !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #B8860B !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    :root, .stApp, section[data-testid="stSidebar"] {
        --bg-primary: #0B0B0B !important;
        --bg-surface: #141414 !important;
        --bg-elevated: #1C1C1C !important;
        --bg-gradient: radial-gradient(circle at 50% 0%, rgba(212, 175, 55, 0.12) 0%, rgba(11, 11, 11, 0.98) 75%), #0B0B0B !important;
        --gold: #D4AF37 !important;
        --gold-hover: #B8962E !important;
        --gold-glow: rgba(212, 175, 55, 0.35) !important;
        --gold-tint: rgba(212, 175, 55, 0.08) !important;
        --gold-border: rgba(212, 175, 55, 0.25) !important;
        --text-primary: #FFFFFF !important;
        --text-soft: #F5F5F5 !important;
        --text-muted: #A0A0A0 !important;
        --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.6) !important;
        --sidebar-bg: linear-gradient(180deg, #0B0B0B 0%, #141414 100%) !important;
        --input-bg: #141414 !important;
        --input-border: rgba(212, 175, 55, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

if active_lang == "ar":
    st.markdown("""
    <style>
    .stApp, .block-container, section[data-testid="stSidebar"], .stMarkdown, .stButton, .stTextInput, .stSelectbox {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Inter', sans-serif !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        font-family: 'Cairo', sans-serif !important;
    }
    .section-banner {
        border-left: 1px solid var(--gold-border) !important;
        border-right: 3px solid var(--gold) !important;
    }
    [data-testid="stSidebarNav"] {
        text-align: right !important;
    }
    div[data-testid="stRadio"] > div {
        align-items: flex-end !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_theme_lang_controls():
    """Renders dynamic theme and language selectors in the sidebar."""
    c_theme, c_lang = st.columns(2)
    with c_theme:
        theme_keys = ["dark", "light"]
        theme_labels = {"dark": t("theme_dark"), "light": t("theme_light")}
        curr_theme = st.session_state.get("theme", "dark")
        idx_t = theme_keys.index(curr_theme) if curr_theme in theme_keys else 0
        new_theme = st.selectbox(
            "Theme",
            theme_keys,
            index=idx_t,
            format_func=lambda x: theme_labels.get(x, x),
            key="theme_selector",
            label_visibility="collapsed"
        )
        if new_theme != curr_theme:
            st.session_state["theme"] = new_theme
            st.rerun()
            
    with c_lang:
        lang_keys = ["en", "ar"]
        lang_labels = {"en": "English", "ar": "العربية"}
        curr_lang = st.session_state.get("lang", "en")
        idx_l = lang_keys.index(curr_lang) if curr_lang in lang_keys else 0
        new_lang = st.selectbox(
            "Language",
            lang_keys,
            index=idx_l,
            format_func=lambda x: lang_labels.get(x, x),
            key="lang_selector",
            label_visibility="collapsed"
        )
        if new_lang != curr_lang:
            st.session_state["lang"] = new_lang
            st.rerun()

# ─── Unauthenticated Gateway ─────────────────────────────────────
if not is_authenticated():
    with st.sidebar:
        logo_uri = get_logo_base64()
        if logo_uri:
            st.markdown(f'<div style="text-align:center;padding:16px 0;"><img src="{logo_uri}" style="width:56px;height:56px;border-radius:10px;border:1px solid #D4AF37;object-fit:cover;" /></div>', unsafe_allow_html=True)
            
        st.markdown(f"""
        <div style="text-align:center;padding:0 10px 14px;">
            <div style="font-family:'Poppins','Cairo',sans-serif;font-size:18px;font-weight:800;color:var(--gold);">{BRAND_NAME}</div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">{BRAND_OWNER}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme & Language Switches on Login Sidebar
        render_theme_lang_controls()
        
        st.markdown("---")
        welcome_intro = (
            "مرحباً بك في منصة SEO Suite Pro. سجل الدخول للوصول إلى خزينتك الخاصة لفحص السيو، وتحليل جوجل سيرش كونسول، وخطط التحسين بالذكاء الاصطناعي."
            if active_lang == "ar"
            else "Welcome to SEO Suite Pro. Sign in to access your private technical audit vault, Search Console analysis, and AI optimization roadmaps."
        )
        st.markdown(f"""
        <div style="font-size:12px;color:var(--text-muted);line-height:1.7;">
            {welcome_intro}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:var(--text-muted);text-align:center;">
            {t('built_by')} {BRAND_OWNER}<br/>
            <a href="{PORTFOLIO_URL}" target="_blank" style="color:var(--gold);text-decoration:none;">{t('portfolio')}</a> &bull; 
            <a href="{LINKEDIN_URL}" target="_blank" style="color:var(--gold);text-decoration:none;">LinkedIn</a>
        </div>
        """, unsafe_allow_html=True)
        
    render_auth_view()
    st.stop()

# ─── Authenticated User Workspace ────────────────────────────────
else:
    user = get_current_user()

    # Sidebar Navigation
    with st.sidebar:
        logo_uri = get_logo_base64()
        if logo_uri:
            st.markdown(f'<div style="text-align:center;padding:12px 0 8px;"><img src="{logo_uri}" style="width:54px;height:54px;border-radius:10px;border:1px solid #D4AF37;object-fit:cover;" /></div>', unsafe_allow_html=True)
            
        st.markdown(f"""
        <div style="text-align:center;padding-bottom:10px;">
            <div style="font-family:'Poppins','Cairo',sans-serif;font-size:18px;font-weight:800;color:var(--gold);">{BRAND_NAME}</div>
            <div style="font-size:11px;color:var(--text-muted);">{BRAND_ROLE}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme & Language Switches
        render_theme_lang_controls()
        
        # User Profile Box
        role_badge = t("role_admin") if user and user.get("role") == "admin" else t("role_user")
        username_display = user["username"] if user else "Analyst"
        st.markdown(f"""
        <div style="background:var(--bg-surface);border:1px solid var(--gold-border);border-radius:8px;padding:10px 14px;margin:12px 0 16px;">
            <div style="font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;">{t('active_account')}</div>
            <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-top:2px;">{username_display} <span style="font-size:10px;color:var(--gold);">{role_badge}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation Options
        NAV_ITEMS = [
            ("dashboard", "nav_dashboard"),
            ("onpage", "nav_onpage"),
            ("gsc", "nav_gsc"),
            ("offpage", "nav_offpage"),
            ("gemini", "nav_gemini"),
            ("history", "nav_history"),
            ("contact", "nav_contact"),
        ]
        if is_admin():
            NAV_ITEMS.insert(6, ("admin", "nav_admin"))
            
        nav_keys = [k for k, _ in NAV_ITEMS]
        nav_dict = dict(NAV_ITEMS)
        
        # Check if a jump target was set in session state
        nav_target = st.session_state.pop("nav_target", None)
        default_index = 0
        if nav_target:
            clean_target = str(nav_target).lower().strip()
            for idx, (k, trans_key) in enumerate(NAV_ITEMS):
                if k == clean_target or t(trans_key).lower() == clean_target or clean_target in trans_key:
                    default_index = idx
                    break
                    
        selected_key = st.radio(
            "Navigation",
            nav_keys,
            index=default_index,
            format_func=lambda k: t(nav_dict[k]),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button(t("nav_signout"), use_container_width=True):
            logout_user()
            
        st.markdown(f"""
        <div style="padding-top:16px;text-align:center;font-size:11px;color:var(--text-muted);line-height:1.7;">
            {t('built_by')} <strong style="color:var(--gold);">{BRAND_OWNER}</strong><br/>
            <a href="{PORTFOLIO_URL}" target="_blank" style="color:var(--gold);text-decoration:none;">{t('portfolio')}</a> &bull; 
            <a href="{LINKEDIN_URL}" target="_blank" style="color:var(--gold);text-decoration:none;">LinkedIn</a> &bull; 
            <a href="{WHATSAPP_URL}" target="_blank" style="color:var(--gold);text-decoration:none;">WhatsApp</a>
        </div>
        """, unsafe_allow_html=True)

    # ─── Page Router ─────────────────────────────────────────────────
    if selected_key == "dashboard":
        render_dashboard_view()
    elif selected_key == "onpage":
        render_onpage_view()
    elif selected_key == "gsc":
        render_gsc_view()
    elif selected_key == "offpage":
        render_offpage_view()
    elif selected_key == "gemini":
        render_gemini_view()
    elif selected_key == "history":
        render_history_view()
    elif selected_key == "admin":
        render_admin_view()
    elif selected_key == "contact":
        render_contact_view()
