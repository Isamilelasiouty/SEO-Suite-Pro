"""
Private Analysis History View for SEO Suite Pro:
- Strictly isolated to the authenticated user's records
- Reopen past audits, inspect summary metrics, download CSV/Excel/PDF, and safely delete records
"""

import pandas as pd
import streamlit as st
from core.auth import get_current_user
from core.database import delete_analysis, get_analysis_by_id, get_user_analyses
from utils.export_csv import generate_csv_bytes
from utils.export_excel import generate_excel_bytes
from utils.export_pdf import generate_pdf_report
from views.components import render_footer, render_header, render_section_header

def render_history_view():
    render_header(subtitle="Private User History & Saved Audits")
    user = get_current_user()
    
    if not user:
        st.error("Please sign in to view your private analysis history.")
        render_footer()
        return
        
    analyses = get_user_analyses(user["id"])
    
    if not analyses:
        st.info("You do not have any saved audits yet. Run an On-Page crawl or Search Console analysis and click 'Save to My History'.")
        render_footer()
        return
        
    render_section_header("Saved Analysis Vault", f"{len(analyses)} records strictly isolated to user {user['username']}")
    
    col_sel, col_del = st.columns([3, 1])
    with col_sel:
        options = {f"#{a['id']} - [{a['analysis_type'].upper()}] {a['target_name']} ({a['created_at']})": a["id"] for a in analyses}
        selected_label = st.selectbox("Select Saved Audit", list(options.keys()))
        selected_id = options[selected_label]
        
    with col_del:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("Delete This Record", type="secondary", use_container_width=True):
            if delete_analysis(selected_id, user["id"]):
                st.success("Record deleted successfully.")
                st.rerun()
            else:
                st.error("Failed to delete record.")
                
    # Load detailed record
    record = get_analysis_by_id(selected_id, user["id"])
    if record:
        st.markdown("---")
        summary = record["summary"]
        st.markdown(f"#### Audit Details: {record['target_name']} ({record['analysis_type'].upper()})")
        st.caption(f"Created: {record['created_at']}")
        
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
            render_section_header("Export Saved Data")
            c1, c2 = st.columns(2)
            with c1:
                # Flat dataframe from summary or payload
                flat_df = pd.DataFrame([summary])
                st.download_button("Download Summary CSV", data=generate_csv_bytes(flat_df), file_name=f"audit_{selected_id}_summary.csv", mime="text/csv", use_container_width=True)
            with c2:
                excel_bytes = generate_excel_bytes({"Summary": pd.DataFrame([summary])})
                st.download_button("Download Summary Excel", data=excel_bytes, file_name=f"audit_{selected_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                
    render_footer()
