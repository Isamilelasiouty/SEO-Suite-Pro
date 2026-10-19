"""
Master Executive Dashboard View for SEO Suite Pro:
- High-level platform KPIs
- Quick launchpad to On-Page, Off-Page, Search Console, and Gemini AI tools
- Recent private audit history summary
- Fully bilingual (English & Arabic) and Light/Dark mode compatible
"""

import textwrap
import streamlit as st
from core.auth import get_current_user
from core.database import get_user_analyses
from core.i18n import get_current_lang, t
from views.components import (
    render_footer,
    render_header,
    render_kpi_row,
    render_section_header,
)

def render_dashboard_view():
    user = get_current_user()
    username = user["username"] if user else "Analyst"
    
    welcome_sub = t("dash_welcome").format(name=username.title())
    render_header(subtitle=welcome_sub)
    
    # Hero Intro Card
    intro_html = textwrap.dedent(f"""
    <div class="glass-card">
        <div style="font-family:'Poppins','Cairo',sans-serif;font-size:22px;font-weight:800;color:var(--gold);margin-bottom:8px;">
            {t('dash_title')}
        </div>
        <div style="font-size:13px;color:var(--text-soft);line-height:1.6;max-width:820px;">
            {t('dash_desc')}
        </div>
    </div>
    """).strip()
    st.markdown(intro_html, unsafe_allow_html=True)
    
    # User Private Stats
    recent_analyses = get_user_analyses(user["id"]) if user else []
    total_saved = len(recent_analyses)
    gsc_count = sum(1 for a in recent_analyses if a["analysis_type"] == "gsc")
    onpage_count = sum(1 for a in recent_analyses if a["analysis_type"] == "onpage")
    
    render_kpi_row([
        (t("kpi_total_saved"), total_saved, "Private database records"),
        (t("kpi_gsc_reports"), gsc_count, "Processed datasets"),
        (t("kpi_onpage_crawls"), onpage_count, "DOM audits conducted"),
        (t("kpi_dual_engine"), "Python & R", t("dual_engine_sub")),
    ])
    
    render_section_header(t("modules_header"), t("modules_sub"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        c1_html = textwrap.dedent(f"""
        <div class="glass-card" style="height:220px;">
            <div class="card-label">{t('mod_onpage_badge')}</div>
            <div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">{t('mod_onpage_title')}</div>
            <div style="font-size:12px;color:var(--text-muted);line-height:1.6;">
                {t('mod_onpage_desc')}
            </div>
        </div>
        """).strip()
        st.markdown(c1_html, unsafe_allow_html=True)
        if st.button(t("launch_onpage"), key="btn_dash_onpage", use_container_width=True):
            st.session_state["nav_target"] = "onpage"
            st.rerun()
            
    with col2:
        c2_html = textwrap.dedent(f"""
        <div class="glass-card" style="height:220px;">
            <div class="card-label">{t('mod_gsc_badge')}</div>
            <div style="font-size:16px;font-weight:700;color:var(--gold);margin-bottom:8px;">{t('mod_gsc_title')}</div>
            <div style="font-size:12px;color:var(--text-muted);line-height:1.6;">
                {t('mod_gsc_desc')}
            </div>
        </div>
        """).strip()
        st.markdown(c2_html, unsafe_allow_html=True)
        if st.button(t("launch_gsc"), key="btn_dash_gsc", type="primary", use_container_width=True):
            st.session_state["nav_target"] = "gsc"
            st.rerun()
            
    with col3:
        c3_html = textwrap.dedent(f"""
        <div class="glass-card" style="height:220px;">
            <div class="card-label">{t('mod_offpage_badge')}</div>
            <div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">{t('mod_offpage_title')}</div>
            <div style="font-size:12px;color:var(--text-muted);line-height:1.6;">
                {t('mod_offpage_desc')}
            </div>
        </div>
        """).strip()
        st.markdown(c3_html, unsafe_allow_html=True)
        if st.button(t("launch_offpage"), key="btn_dash_offpage", use_container_width=True):
            st.session_state["nav_target"] = "offpage"
            st.rerun()
            
    # Recent Audits Table
    if recent_analyses:
        render_section_header(t("recent_audits_title"), t("recent_audits_sub"))
        records = []
        for a in recent_analyses[:5]:
            records.append({
                "ID": a["id"],
                "Project": a["target_name"],
                "Module": a["analysis_type"].upper(),
                "Timestamp": a["created_at"]
            })
        st.dataframe(records, use_container_width=True)
        
    render_footer()
