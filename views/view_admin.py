"""
Admin Analytics View for SEO Suite Pro:
- Aggregated platform usage metrics
- STRICT PRIVACY: Zero access to private user analyses, URLs, or client data
- Bilingual support (English & Arabic) and Light/Dark mode compatible
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from core.auth import is_admin
from core.database import get_admin_metrics
from core.i18n import get_current_lang, t
from views.components import (
    render_footer,
    render_header,
    render_kpi_row,
    render_section_header,
    style_plotly_figure,
)

def render_admin_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("admin_header"))
    
    if not is_admin():
        st.error("Access Restricted: This view is reserved exclusively for system administrators." if not is_ar else "غير مصرح: هذا القسم مخصص لمدير المنصة فقط.")
        render_footer()
        return
        
    metrics = get_admin_metrics()
    
    st.markdown(f"""
    <div style="background:var(--bg-elevated);border:1px solid var(--gold-border);border-radius:10px;padding:14px 20px;margin-bottom:20px;font-size:12px;color:var(--text-soft);box-shadow:var(--shadow-card);">
        <strong style="color:var(--gold);">{'Privacy Enforced' if not is_ar else 'حماية الخصوصية الصارمة'}:</strong> {t('admin_privacy')}
    </div>
    """, unsafe_allow_html=True)
    
    render_kpi_row([
        (t("admin_kpi_users"), metrics["total_users"], "Active tenant accounts"),
        (t("admin_kpi_analyses"), metrics["total_analyses"], "Lifetime platform runs"),
        (t("admin_kpi_events"), metrics["recent_events_7d"], "Platform interactions"),
        (t("admin_kpi_security"), "Active & Enforced", "SSRF & bcrypt protected"),
    ])
    
    render_section_header("Usage & Throughput Breakdown" if not is_ar else "توزيع الاستخدام ومعدلات المعالجة")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Analyses Executed by Module" if not is_ar else "#### العمليات المنفذة حسب نوع الفحص")
        type_data = [{"Module": k.upper(), "Runs": v} for k, v in metrics["type_breakdown"].items()]
        if type_data:
            df_types = pd.DataFrame(type_data)
            fig_types = px.bar(df_types, x="Module", y="Runs", color_discrete_sequence=["#D4AF37"])
            st.plotly_chart(style_plotly_figure(fig_types, "Runs per Module"), use_container_width=True)
        else:
            st.info("No analysis events recorded yet." if not is_ar else "لا توجد عمليات مسجلة بعد.")
            
    with col2:
        st.markdown("#### Daily Event Velocity (Last 14 Days)" if not is_ar else "#### النشاط اليومي للعمليات (آخر 14 يوماً)")
        if metrics["daily_activity"]:
            df_daily = pd.DataFrame(metrics["daily_activity"])
            fig_daily = px.line(df_daily, x="date", y="count", markers=True, color_discrete_sequence=["#D4AF37"])
            st.plotly_chart(style_plotly_figure(fig_daily, "Daily Event Trends"), use_container_width=True)
        else:
            st.info("No daily activity data available." if not is_ar else "لا توجد بيانات نشاط يومي متوفرة.")
            
    render_footer()
