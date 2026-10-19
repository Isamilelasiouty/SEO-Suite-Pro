"""
Master Executive Dashboard View for SEO Suite Pro:
- High-level platform KPIs
- Quick launchpad to On-Page, Off-Page, Search Console, and Gemini AI tools
- Recent private audit history summary
"""

import streamlit as st
from core.auth import get_current_user
from core.database import get_user_analyses
from views.components import render_header, render_footer, render_section_header, render_kpi_row, render_metric_card

def render_dashboard_view():
    user = get_current_user()
    username = user["username"] if user else "Analyst"
    
    render_header(subtitle=f"Executive Intelligence Dashboard &bull; Welcome, {username.title()}")
    
    # Hero Intro Card
    st.markdown("""
    <div class="glass-card">
        <div style="font-family:'Poppins',sans-serif;font-size:22px;font-weight:800;color:#D4AF37;margin-bottom:8px;">
            Professional SEO Suite & Search Architecture
        </div>
        <div style="font-size:13px;color:#F5F5F5;line-height:1.6;max-width:780px;">
            An enterprise-grade SEO diagnostic environment designed for deep technical crawling, 
            Google Search Console statistical modeling (Python + R dual engines), keyword cannibalization attribution, 
            and Google Gemini AI strategic recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User Private Stats
    recent_analyses = get_user_analyses(user["id"]) if user else []
    total_saved = len(recent_analyses)
    gsc_count = sum(1 for a in recent_analyses if a["analysis_type"] == "gsc")
    onpage_count = sum(1 for a in recent_analyses if a["analysis_type"] == "onpage")
    
    render_kpi_row([
        ("Total Saved Audits", total_saved, "Private database records"),
        ("Search Console Reports", gsc_count, "Processed datasets"),
        ("On-Page Crawls", onpage_count, "DOM audits conducted"),
        ("System Architecture", "Python & R", "Dual statistical engines"),
    ])
    
    render_section_header("Analysis Modules", "Select an operational workflow to begin")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="height:210px;">
            <div class="card-label">On-Page & Technical</div>
            <div style="font-size:16px;font-weight:700;color:#FFFFFF;margin-bottom:8px;">DOM & Sitemap Audit</div>
            <div style="font-size:12px;color:#A0A0A0;line-height:1.5;">
                Deep crawling with BeautifulSoup and lxml: title and meta length checks, heading hierarchies, schema validation, canonical tags, readability scores, and image alt text.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch On-Page Audit", key="btn_dash_onpage", use_container_width=True):
            st.session_state["nav_target"] = "On-Page Audit"
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class="glass-card" style="height:210px;">
            <div class="card-label">Search Console Intelligence</div>
            <div style="font-size:16px;font-weight:700;color:#D4AF37;margin-bottom:8px;">Python + R Dual Engine</div>
            <div style="font-size:12px;color:#A0A0A0;line-height:1.5;">
                Ingest GSC JSON API responses or CSV exports. Features Scikit-Learn TF-IDF clustering, algorithmic keyword cannibalization detection, and R anomaly modeling.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Search Console", key="btn_dash_gsc", type="primary", use_container_width=True):
            st.session_state["nav_target"] = "Search Console"
            st.rerun()
            
    with col3:
        st.markdown("""
        <div class="glass-card" style="height:210px;">
            <div class="card-label">Off-Page & Authority</div>
            <div style="font-size:16px;font-weight:700;color:#FFFFFF;margin-bottom:8px;">Anchor Text & Risk Model</div>
            <div style="font-size:12px;color:#A0A0A0;line-height:1.5;">
                Analyze backlink distributions, exact-match ratios, anchor text diversity, and algorithmic over-optimization penalty risk indicators.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Off-Page Audit", key="btn_dash_offpage", use_container_width=True):
            st.session_state["nav_target"] = "Off-Page Analysis"
            st.rerun()
            
    # Recent Audits Table
    if recent_analyses:
        render_section_header("Recent Saved Analyses", "Access past private records")
        records = []
        for a in recent_analyses[:5]:
            records.append({
                "ID": a["id"],
                "Target Domain / Project": a["target_name"],
                "Module": a["analysis_type"].upper(),
                "Saved Timestamp": a["created_at"]
            })
        st.dataframe(records, use_container_width=True)
        
    render_footer()
