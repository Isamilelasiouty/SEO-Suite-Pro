"""
Shared UI Components for SEO Suite Pro:
- Header with official logo and portfolio link
- Metric cards, section banners, and status badges (strictly no emojis)
- Universal footer: 'Built by Ismail El Asiouty'
- Gold and black custom Plotly theme applicator
"""

import base64
import streamlit as st
import plotly.graph_objects as go
from core.config import (
    BRAND_NAME,
    BRAND_OWNER,
    BRAND_ROLE,
    COLOR_BG_PRIMARY,
    COLOR_BG_SURFACE,
    COLOR_GOLD,
    COLOR_GOLD_HOVER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_SOFT,
    COLOR_TEXT_WHITE,
    FOOTER_TEXT,
    LOGO_PATH,
    PORTFOLIO_URL,
)

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
    logo_html = f'<img src="{logo_uri}" style="width:48px;height:48px;border-radius:8px;border:1px solid #D4AF37;object-fit:cover;" />' if logo_uri else ''
    
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;background:#141414;border:1px solid rgba(212,175,55,0.25);border-radius:10px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:16px;">
            {logo_html}
            <div>
                <div style="font-family:'Poppins',sans-serif;font-size:20px;font-weight:800;color:#D4AF37;letter-spacing:-0.01em;">
                    {BRAND_NAME}
                </div>
                <div style="font-size:12px;color:#A0A0A0;">
                    {subtitle or f"{BRAND_ROLE} &bull; {BRAND_OWNER}"}
                </div>
            </div>
        </div>
        <div>
            <a href="{PORTFOLIO_URL}" target="_blank" style="display:inline-block;padding:7px 16px;border:1px solid #D4AF37;border-radius:6px;color:#D4AF37;text-decoration:none;font-size:12px;font-weight:600;transition:all 0.2s ease;">
                Portfolio Website
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Universal footer required on all pages."""
    st.markdown(f"""
    <div class="app-footer">
        <div>{FOOTER_TEXT}</div>
        <div style="margin-top:6px;font-size:11px;color:#777777;">
            Portfolio: <a href="{PORTFOLIO_URL}" target="_blank">{PORTFOLIO_URL}</a> &nbsp;|&nbsp; Enterprise SEO Architecture
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: str = ""):
    """Renders a section header banner."""
    sub_html = f'<div style="font-size:11px;color:#A0A0A0;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="section-banner">
        <div>
            <div class="section-banner-title">{title}</div>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str | int | float, sub: str = "", badge: str = ""):
    """Renders a gold-accented KPI card."""
    badge_html = f'<span class="badge-label badge-optimal" style="margin-left:8px;">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="card-label">{label} {badge_html}</div>
        <div class="card-value">{value}</div>
        <div class="card-subtitle">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_row(cards: list[tuple[str, str, str]]):
    """Renders a responsive row of KPI cards."""
    cols = st.columns(len(cards))
    for col, (label, val, sub) in zip(cols, cards):
        with col:
            render_metric_card(label, val, sub)

def style_plotly_figure(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    """Applies the strict gold, black, and white design system to Plotly charts."""
    fig.update_layout(
        title=dict(text=title, font=dict(family="Poppins", size=14, color=COLOR_TEXT_WHITE), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(t=48, b=24, l=16, r=16),
        font=dict(family="Inter", color=COLOR_TEXT_MUTED, size=11),
        legend=dict(
            font=dict(color=COLOR_TEXT_SOFT, size=11),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            linecolor="rgba(212,175,55,0.25)",
            tickfont=dict(color=COLOR_TEXT_MUTED)
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            linecolor="rgba(212,175,55,0.25)",
            tickfont=dict(color=COLOR_TEXT_MUTED)
        )
    )
    return fig
