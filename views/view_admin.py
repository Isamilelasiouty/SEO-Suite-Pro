"""
Admin Analytics View for SEO Suite Pro:
- Aggregated platform usage metrics
- STRICT PRIVACY: Zero access to private user analyses, URLs, or client data
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from core.auth import is_admin
from core.database import get_admin_metrics
from views.components import (
    render_footer,
    render_header,
    render_kpi_row,
    render_section_header,
    style_plotly_figure,
)

def render_admin_view():
    render_header(subtitle="Administrative Platform Intelligence & Usage Metrics")
    
    if not is_admin():
        st.error("Access Restricted: This view is reserved exclusively for system administrators.")
        render_footer()
        return
        
    metrics = get_admin_metrics()
    
    st.markdown("""
    <div style="background:rgba(212,175,55,0.06);border:1px solid #D4AF37;border-radius:8px;padding:12px 18px;margin-bottom:20px;font-size:12px;color:#F5F5F5;">
        <strong style="color:#D4AF37;">Privacy Enforced:</strong> The Admin panel reports platform throughput, computational events, and capacity metrics only. No user audit payloads or target URLs are accessible.
    </div>
    """, unsafe_allow_html=True)
    
    render_kpi_row([
        ("Total Registered Users", metrics["total_users"], "Active tenant accounts"),
        ("Total Analyses Executed", metrics["total_analyses"], "Lifetime platform runs"),
        ("Events (Past 7 Days)", metrics["recent_events_7d"], "Platform interactions"),
        ("Security State", "Active & Enforced", "SSRF & bcrypt protected"),
    ])
    
    render_section_header("Usage & Throughput Breakdown")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Analyses Executed by Module")
        type_data = [{"Module": k.upper(), "Runs": v} for k, v in metrics["type_breakdown"].items()]
        if type_data:
            df_types = pd.DataFrame(type_data)
            fig_types = px.bar(df_types, x="Module", y="Runs", color_discrete_sequence=["#D4AF37"])
            st.plotly_chart(style_plotly_figure(fig_types, "Runs per Module"), use_container_width=True)
        else:
            st.info("No analysis events recorded yet.")
            
    with col2:
        st.markdown("#### Daily Event Velocity (Last 14 Days)")
        if metrics["daily_activity"]:
            df_daily = pd.DataFrame(metrics["daily_activity"])
            fig_daily = px.line(df_daily, x="date", y="count", markers=True, color_discrete_sequence=["#D4AF37"])
            st.plotly_chart(style_plotly_figure(fig_daily, "Daily Event Trends"), use_container_width=True)
        else:
            st.info("No daily activity data available.")
            
    render_footer()
