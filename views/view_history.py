"""
Private Analysis History View for SEO Suite Pro:
- Strictly isolated to the authenticated user's records
- Reopen past audits, inspect summary metrics, download CSV/Excel/PDF, and safely delete records
- Bilingual support (English & Arabic) and Light/Dark mode compatible
"""

import pandas as pd
import streamlit as st
from core.auth import get_current_user
from core.database import delete_analysis, get_analysis_by_id, get_user_analyses
from core.i18n import get_current_lang, t
from utils.export_csv import generate_csv_bytes
from utils.export_excel import generate_excel_bytes
from views.components import render_footer, render_header, render_section_header

def render_history_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("history_header"))
    user = get_current_user()
    
    if not user:
        st.error("Please sign in to view your private analysis history." if not is_ar else "يرجى تسجيل الدخول لعرض سجلك الخاص.")
        render_footer()
        return
        
    analyses = get_user_analyses(user["id"])
    
    if not analyses:
        st.info(t("history_empty"))
        render_footer()
        return
        
    vault_title = t("history_vault")
    sub_title = f"{len(analyses)} records strictly isolated to user {user['username']}" if not is_ar else f"{len(analyses)} تحليلاً محفوظاً بشكل مشفر للمستخدم {user['username']}"
    render_section_header(vault_title, sub_title)
    
    col_sel, col_del = st.columns([3, 1])
    with col_sel:
        options = {f"#{a['id']} - [{a['analysis_type'].upper()}] {a['target_name']} ({a['created_at']})": a["id"] for a in analyses}
        selected_label = st.selectbox(t("history_select"), list(options.keys()))
        selected_id = options[selected_label]
        
    with col_del:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button(t("delete_record"), type="secondary", use_container_width=True):
            if delete_analysis(selected_id, user["id"]):
                st.success("تم حذف السجل بنجاح." if is_ar else "Record deleted successfully.")
                st.rerun()
            else:
                st.error("Failed to delete record." if not is_ar else "فشل حذف السجل.")
                
    # Load detailed record
    record = get_analysis_by_id(selected_id, user["id"])
    if record:
        st.markdown("---")
        summary = record["summary"]
        det_title = f"تفاصيل التحليل: {record['target_name']} ({record['analysis_type'].upper()})" if is_ar else f"Audit Details: {record['target_name']} ({record['analysis_type'].upper()})"
        st.markdown(f"#### {det_title}")
        st.caption(f"{'تاريخ الإنشاء' if is_ar else 'Created'}: {record['created_at']}")
        
        # Display summary cards
        cols = st.columns(min(4, max(1, len(summary))))
        for col, (k, v) in zip(cols, summary.items()):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="card-label">{k.replace('_', ' ').title()}</div>
                    <div class="card-value" style="font-size:24px;">{v}</div>
                </div>
                """, unsafe_allow_html=True)
                
        # Export options for this record
        data_payload = record.get("data", {})
        if data_payload:
            render_section_header(t("export_csv") + " / " + t("export_excel"))
            c1, c2 = st.columns(2)
            with c1:
                flat_df = pd.DataFrame([summary])
                st.download_button(t("export_csv"), data=generate_csv_bytes(flat_df), file_name=f"audit_{selected_id}_summary.csv", mime="text/csv", use_container_width=True)
            with c2:
                excel_bytes = generate_excel_bytes({"Summary": pd.DataFrame([summary])})
                st.download_button(t("export_excel"), data=excel_bytes, file_name=f"audit_{selected_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                
    render_footer()
