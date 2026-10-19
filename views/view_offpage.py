"""
Off-Page SEO & Backlink Risk View for SEO Suite Pro:
- Anchor text distribution analysis
- Over-Optimization Penguin penalty risk index
- Backlink profile upload or simulated audit
- Export to CSV, Excel, and PDF
- Fully bilingual (English & Arabic) and Light/Dark mode compatible
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from core.auth import get_current_user
from core.database import save_analysis
from core.i18n import get_current_lang, t
from services.offpage_analyzer import analyze_backlink_profile
from utils.export_csv import generate_csv_bytes
from utils.export_excel import generate_excel_bytes
from utils.export_pdf import generate_pdf_report
from views.components import (
    render_footer,
    render_header,
    render_kpi_row,
    render_section_header,
    style_plotly_figure,
)

def render_offpage_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("offpage_header"))
    user = get_current_user()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        target_domain = st.text_input(t("offpage_domain"), value="example.com")
        brand_name = st.text_input(t("offpage_brand"), value="Example Brand", help="Used to identify branded vs exact-match anchors")
        target_kw = st.text_input(t("offpage_keyword"), value="seo services", help="Used to detect exact-match anchor density")
    with col2:
        source_options = [t("offpage_upload_csv"), t("offpage_sample_profile")]
        input_mode = st.radio(t("offpage_data_source"), source_options)
        
    backlink_records = []
    
    if input_mode == t("offpage_upload_csv"):
        uploaded_file = st.file_uploader(t("offpage_csv_label"), type=["csv"])
        if uploaded_file:
            try:
                df_upload = pd.read_csv(uploaded_file)
                # Normalize column names
                rename_map = {}
                for c in df_upload.columns:
                    clow = c.lower().strip()
                    if "source" in clow: rename_map[c] = "source_url"
                    elif "target" in clow or "dest" in clow: rename_map[c] = "target_url"
                    elif "anchor" in clow: rename_map[c] = "anchor_text"
                    elif "nofollow" in clow: rename_map[c] = "is_nofollow"
                df_upload = df_upload.rename(columns=rename_map)
                backlink_records = df_upload.to_dict(orient="records")
                msg = f"تم تحميل {len(backlink_records)} رابط خلفي بنجاح." if is_ar else f"Loaded {len(backlink_records)} backlink records from CSV."
                st.success(msg)
            except Exception as e:
                st.error(f"Failed to read CSV: {str(e)}")
    else:
        # Diagnostic sample profile
        backlink_records = [
            {"source_url": "https://techblog.org/review", "target_url": f"https://{target_domain}/", "anchor_text": brand_name, "is_nofollow": False},
            {"source_url": "https://industry-news.com/post", "target_url": f"https://{target_domain}/services", "anchor_text": target_kw, "is_nofollow": False},
            {"source_url": "https://forum.net/thread", "target_url": f"https://{target_domain}/", "anchor_text": "click here", "is_nofollow": True},
            {"source_url": "https://directory.com/listing", "target_url": f"https://{target_domain}/", "anchor_text": f"https://{target_domain}", "is_nofollow": False},
            {"source_url": "https://digitalmag.com/tools", "target_url": f"https://{target_domain}/about", "anchor_text": f"best {target_kw} agency", "is_nofollow": False},
            {"source_url": "https://partner.com/links", "target_url": f"https://{target_domain}/", "anchor_text": brand_name.lower(), "is_nofollow": False},
            {"source_url": "https://affiliate.org/deals", "target_url": f"https://{target_domain}/services", "anchor_text": target_kw, "is_nofollow": False},
            {"source_url": "https://webindex.info/page", "target_url": f"https://{target_domain}/contact", "anchor_text": "website", "is_nofollow": True},
            {"source_url": "https://newsfeed.com/article", "target_url": f"https://{target_domain}/", "anchor_text": f"visit {brand_name}", "is_nofollow": False},
            {"source_url": "https://reviewhub.co/best", "target_url": f"https://{target_domain}/services", "anchor_text": target_kw, "is_nofollow": False},
        ] * 5

    run_btn = st.button(t("offpage_evaluate_btn"), type="primary", use_container_width=True)
    
    if run_btn or backlink_records:
        result = analyze_backlink_profile(backlink_records, brand_name, target_kw)
        
        # Overview KPIs
        render_kpi_row([
            (t("kpi_backlinks"), result["total_backlinks"], "Evaluated referring links"),
            (t("kpi_referring_domains"), result["referring_domains"], "Unique linking hostnames"),
            (t("kpi_risk_score"), f"{result['penalty_risk_score']} / 100", f"Assessment: {result['penalty_risk_label']}"),
            (t("kpi_dofollow"), f"{result['dofollow_ratio_pct']}%", "Healthy range: 60-85%"),
        ])
        
        # Save to history & Export
        col_s, col_e = st.columns([1, 2])
        with col_s:
            if user and st.button(t("save_to_history"), key="btn_save_offpage", use_container_width=True):
                save_analysis(user["id"], "offpage", target_domain, result, {"records": backlink_records[:50]})
                st.success(t("saved_success"))
                
        with col_e:
            df_dist = pd.DataFrame([
                {"Anchor Category": k, "Link Count": result["distribution_counts"][k], "Percentage": f"{result['distribution_pct'][k]}%"}
                for k in result["distribution_counts"]
            ])
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button(t("export_csv"), data=generate_csv_bytes(df_dist), file_name="offpage_anchors.csv", mime="text/csv", use_container_width=True)
            with c2:
                st.download_button(t("export_excel"), data=generate_excel_bytes({"Anchor Distribution": df_dist}), file_name="offpage_anchors.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with c3:
                kpis_pdf = [
                    ("Total Backlinks", str(result["total_backlinks"])),
                    ("Referring Domains", str(result["referring_domains"])),
                    ("Risk Score", f"{result['penalty_risk_score']}/100"),
                    ("Risk Status", result["penalty_risk_label"]),
                    ("Dofollow Ratio", f"{result['dofollow_ratio_pct']}%"),
                ]
                issues_pdf = [{
                    "category": "Off-Page Penalty Risk",
                    "severity": "High" if result["penalty_risk_score"] > 40 else "Medium",
                    "item": f"Risk Score: {result['penalty_risk_score']}/100",
                    "url": target_domain,
                    "problem": rec,
                    "fix": "Rebalance anchor text profile."
                } for rec in result["recommendations"]]
                st.download_button(t("export_pdf"), data=generate_pdf_report("Off-Page Anchor Risk Audit", target_domain, kpis_pdf, issues_pdf), file_name="offpage_audit.pdf", mime="application/pdf", use_container_width=True)
                
        # Visual Charts
        render_section_header("Anchor Text Breakdown & Distribution Curve" if not is_ar else "توزيع الروابط النصية ومنحنى المخاطر")
        col_c1, col_c2 = st.columns([1, 1.2])
        
        with col_c1:
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(result["distribution_pct"].keys()),
                values=list(result["distribution_pct"].values()),
                hole=0.55,
                marker=dict(colors=["#EF5350", "#FFA726", "#D4AF37", "#9E9E9E", "#B8962E"]),
                textinfo="label+percent"
            )])
            st.plotly_chart(style_plotly_figure(fig_pie, "Anchor Category Distribution", height=320), use_container_width=True)
            
        with col_c2:
            st.markdown("#### Algorithmic Risk Assessment & Recommendations" if not is_ar else "#### التقييم الفني للمخاطر وتوصيات المعالجة")
            for rec in result["recommendations"]:
                if "High" in rec or "penalty" in rec.lower() or "خطر" in rec:
                    st.error(rec)
                elif "Elevated" in rec or "Low" in rec or "متوسط" in rec:
                    st.warning(rec)
                else:
                    st.success(rec)
                    
            st.dataframe(df_dist, use_container_width=True)
            
    render_footer()
