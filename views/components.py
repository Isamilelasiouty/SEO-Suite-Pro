"""
Shared UI Components for SEO Suite Pro:
- Official brand logo, Google logo, GSC logo, Gemini logo, Python and R badges
- Light / Dark theme awareness for Plotly figures and HTML cards
- Bilingual Arabic / English support
- Universal footer: 'Built by Ismail El Asiouty'
"""

import base64
import plotly.graph_objects as go
import streamlit as st
from core.config import (
    BRAND_NAME,
    BRAND_OWNER,
    BRAND_ROLE,
    COLOR_GOLD,
    FOOTER_TEXT,
    LOGO_PATH,
    PORTFOLIO_URL,
)
from core.i18n import get_current_lang, t

def get_google_logo_svg(size: int = 24) -> str:
    """Official Google 4-Color 'G' SVG."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
    </svg>"""

def get_gsc_logo_svg(size: int = 24) -> str:
    """Google Search Console / Search Analytics SVG."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="#4285F4"/>
        <path d="M7 10l2-2 2 2 3-3" stroke="#34A853" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""

def get_gemini_logo_svg(size: int = 24) -> str:
    """Google Gemini Sparkle Logo SVG."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L13.8 8.2L20 10L13.8 11.8L12 18L10.2 11.8L4 10L10.2 8.2L12 2Z" fill="url(#gemini-grad)"/>
        <path d="M18 15L19 18L22 19L19 20L18 23L17 20L14 19L17 18L18 15Z" fill="url(#gemini-grad)"/>
        <defs>
            <linearGradient id="gemini-grad" x1="4" y1="2" x2="22" y2="23" gradientUnits="userSpaceOnUse">
                <stop stop-color="#4285F4"/>
                <stop offset="0.5" stop-color="#9B72CB"/>
                <stop offset="1" stop-color="#D96570"/>
            </linearGradient>
        </defs>
    </svg>"""

def get_logo_base64() -> str:
    """Reads the logo file and returns a base64 encoded data URI."""
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as f:
                data = f.read()
                return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
        except Exception:
            return ""
    return ""

def render_header(subtitle: str = ""):
    """Renders the executive brand header with logo, title, and portfolio link."""
    logo_uri = get_logo_base64()
    logo_html = f'<img src="{logo_uri}" style="width:48px;height:48px;border-radius:10px;border:1px solid #D4AF37;object-fit:cover;box-shadow:0 2px 10px rgba(212,175,55,0.2);" />' if logo_uri else ''
    html = (
        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:16px 22px;background:var(--bg-surface);border:1px solid var(--gold-border);border-radius:12px;margin-bottom:24px;box-shadow:var(--shadow-card);">'
        f'<div style="display:flex;align-items:center;gap:16px;">{logo_html}<div>'
        f'<div style="font-family:\'Poppins\',\'Cairo\',sans-serif;font-size:20px;font-weight:800;color:var(--gold);letter-spacing:-0.01em;">{BRAND_NAME}</div>'
        f'<div style="font-size:12px;color:var(--text-muted);">{subtitle or f"{BRAND_ROLE} &bull; {BRAND_OWNER}"}</div>'
        f'</div></div>'
        f'<div style="display:flex;align-items:center;gap:12px;"><a href="{PORTFOLIO_URL}" target="_blank" style="display:inline-block;padding:7px 16px;border:1px solid var(--gold);border-radius:8px;color:var(--gold);text-decoration:none;font-size:12px;font-weight:600;transition:all 0.2s ease;">{t("portfolio")}</a></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_footer():
    """Universal footer required on all pages."""
    html = (
        f'<div class="app-footer">'
        f'<div>{t("built_by")} <strong>{BRAND_OWNER}</strong></div>'
        f'<div style="margin-top:6px;font-size:11px;color:var(--text-muted);">'
        f'{t("portfolio")}: <a href="{PORTFOLIO_URL}" target="_blank">{PORTFOLIO_URL}</a> &nbsp;|&nbsp; Enterprise Technical Architecture'
        f'</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: str = ""):
    """Renders a section header banner."""
    sub_html = f'<div style="font-size:11px;color:var(--text-muted);margin-top:2px;">{subtitle}</div>' if subtitle else ""
    html = f'<div class="section-banner"><div><div class="section-banner-title">{title}</div>{sub_html}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_metric_card(label: str, value: str | int | float, sub: str = "", badge: str = ""):
    """Renders a gold-accented KPI card."""
    badge_html = f'<span class="badge-label badge-optimal" style="margin-left:8px;">{badge}</span>' if badge else ""
    html = f'<div class="metric-card"><div class="card-label">{label} {badge_html}</div><div class="card-value">{value}</div><div class="card-subtitle">{sub}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_kpi_row(cards: list[tuple[str, str, str]]):
    """Renders a responsive row of KPI cards."""
    cols = st.columns(len(cards))
    for col, (label, val, sub) in zip(cols, cards):
        with col:
            render_metric_card(label, val, sub)

def style_plotly_figure(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    """Applies the strict gold, black, and white design system to Plotly charts respecting active theme."""
    theme = st.session_state.get("theme", "dark")
    is_dark = (theme == "dark")
    
    text_color = "#FFFFFF" if is_dark else "#111827"
    muted_color = "#A0A0A0" if is_dark else "#6B7280"
    grid_color = "rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)"
    line_color = "rgba(212,175,55,0.3)"
    
    fig.update_layout(
        title=dict(text=title, font=dict(family="Poppins, Cairo", size=14, color=text_color), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(t=48, b=24, l=16, r=16),
        font=dict(family="Inter, Cairo", color=muted_color, size=11),
        legend=dict(
            font=dict(color=text_color, size=11),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            gridcolor=grid_color,
            linecolor=line_color,
            tickfont=dict(color=muted_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            linecolor=line_color,
            tickfont=dict(color=muted_color)
        )
    )
    return fig
