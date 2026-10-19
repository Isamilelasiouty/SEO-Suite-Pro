"""
On-Page Technical SEO Audit View for SEO Suite Pro:
- Concurrent multi-page crawling or single-page deep audit
- DOM inspection (Titles, Meta Descriptions, Headings, Schema, Readability, Links, Images)
- Robots.txt and server security headers evaluation
- Export to CSV, Excel (.xlsx), and executive PDF
- One-click persistence to user's private history
"""

import pandas as pd
import streamlit as st
from core.auth import get_current_user
from core.database import save_analysis
from core.security import validate_and_normalize_url
from services.crawler import crawl_urls_concurrently, discover_sitemap_urls, fetch_url, parse_xml_sitemap
from services.onpage_analyzer import analyze_onpage
from services.technical_checker import audit_robots_txt, audit_server_headers
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
import plotly.express as px

def render_onpage_view():
    render_header(subtitle="On-Page Technical Audit & DOM Intelligence")
    user = get_current_user()
    
    col_input, col_opts = st.columns([3, 1])
    with col_input:
        target_input = st.text_input("Target Website URL", placeholder="https://example.com", help="Include http:// or https://")
    with col_opts:
        crawl_mode = st.selectbox("Audit Scope", ["Single Page", "Sitemap Crawl (Multi-Page)"])
        
    max_pages = 25
    if crawl_mode == "Sitemap Crawl (Multi-Page)":
        max_pages = st.slider("Maximum Pages to Crawl", min_value=5, max_value=150, value=25, step=5)
        
    start_btn = st.button("Execute Technical Audit", type="primary", use_container_width=True)
    
    if start_btn and target_input:
        is_valid, norm_url, err_msg = validate_and_normalize_url(target_input)
        if not is_valid:
            st.error(f"Invalid URL: {err_msg}")
            return
            
        with st.spinner("Analyzing site structure and initiating audit..."):
            urls_to_crawl = [norm_url]
            sitemap_found = []
            
            if crawl_mode == "Sitemap Crawl (Multi-Page)":
                sitemaps = discover_sitemap_urls(norm_url)
                if sitemaps:
                    sitemap_found = sitemaps
                    parsed_pages = parse_xml_sitemap(sitemaps[0])
                    if parsed_pages:
                        urls_to_crawl = [p["url"] for p in parsed_pages[:max_pages]]
                        
            # Execute Crawl
            prog_bar = st.progress(0, text="Fetching and parsing DOM structures...")
            
            def update_progress(curr, total, page_url):
                prog_bar.progress(curr / total, text=f"Auditing page {curr}/{total}: {page_url[:60]}")
                
            crawl_data = crawl_urls_concurrently(urls_to_crawl, progress_callback=update_progress)
            prog_bar.empty()
            
            # Analyze each crawled page
            page_audits = []
            for item in crawl_data:
                if item["status_code"] == 200 and item["content"]:
                    audit = analyze_onpage(item["url"], item["content"], item["headers"])
                    audit["status_code"] = item["status_code"]
                    audit["elapsed_ms"] = item["elapsed_ms"]
                    page_audits.append(audit)
                else:
                    page_audits.append({
                        "url": item["url"],
                        "score": 0,
                        "error": item.get("error") or f"HTTP Status {item['status_code']}",
                        "status_code": item["status_code"],
                        "elapsed_ms": item["elapsed_ms"]
                    })
                    
            # Technical checks (Robots & Server headers)
            robots_res = audit_robots_txt(norm_url)
            server_res = audit_server_headers(norm_url)
            
            st.session_state["active_onpage_audit"] = {
                "target_url": norm_url,
                "pages": page_audits,
                "robots": robots_res,
                "server_headers": server_res,
                "sitemaps": sitemap_found
            }
            st.success(f"Audit completed successfully for {len(page_audits)} pages.")
            
    # Display Results if Present
    audit_data = st.session_state.get("active_onpage_audit")
    if not audit_data:
        st.info("Enter a target URL above and click 'Execute Technical Audit' to generate a full DOM report.")
        render_footer()
        return
        
    pages = audit_data["pages"]
    target_url = audit_data["target_url"]
    valid_pages = [p for p in pages if "error" not in p or not p.get("error")]
    
    # Overview KPIs
    avg_score = round(sum(p.get("score", 0) for p in valid_pages) / max(1, len(valid_pages)))
    total_scanned = len(pages)
    missing_title = sum(1 for p in valid_pages if p["title"]["status"] == "Missing")
    missing_desc = sum(1 for p in valid_pages if p["meta_description"]["status"] == "Missing")
    missing_h1 = sum(1 for p in valid_pages if p["headings"]["h1_status"] == "Missing")
    
    render_kpi_row([
        ("On-Page Health Score", f"{avg_score} / 100", "Composite weighted score"),
        ("Pages Scanned", total_scanned, "DOM responses analyzed"),
        ("Missing Titles", missing_title, "Critical SERP factor"),
        ("Missing H1 Headings", missing_h1, "Structure deficiency"),
    ])
    
    # Save to user history
    col_save, col_exp = st.columns([1, 2])
    with col_save:
        if user and st.button("Save Audit to My History", key="btn_save_onpage", use_container_width=True):
            summary = {
                "avg_health_score": avg_score,
                "pages_scanned": total_scanned,
                "missing_title": missing_title,
                "missing_desc": missing_desc,
                "missing_h1": missing_h1
            }
            save_analysis(user["id"], "onpage", target_url, summary, audit_data)
            st.success("Audit saved to your private history.")
            
    # Export Options
    with col_exp:
        # Build Export DataFrames
        rows_summary = []
        for i, p in enumerate(valid_pages, 1):
            rows_summary.append({
                "#": i,
                "URL": p["url"],
                "Health Score": p.get("score", 0),
                "Title": p["title"]["text"],
                "Title Length": p["title"]["length"],
                "Title Status": p["title"]["status"],
                "Meta Description": p["meta_description"]["text"],
                "H1 Count": p["headings"]["h1_count"],
                "Word Count": p["content"]["word_count"],
                "Readability (Flesch)": p["content"]["flesch_reading_ease"],
                "Canonical Status": p["directives"]["canonical_status"],
                "Has Schema": "Yes" if p["schema"]["has_schema"] else "No",
                "Images Missing Alt": p["images"]["missing_alt_count"]
            })
        df_export = pd.DataFrame(rows_summary)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            csv_bytes = generate_csv_bytes(df_export)
            st.download_button("Export CSV", data=csv_bytes, file_name="onpage_audit.csv", mime="text/csv", use_container_width=True)
        with c2:
            excel_bytes = generate_excel_bytes({"On-Page Summary": df_export})
            st.download_button("Export Excel", data=excel_bytes, file_name="onpage_audit.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c3:
            kpis_pdf = [
                ("Health Score", f"{avg_score}/100"),
                ("Pages Scanned", str(total_scanned)),
                ("Missing Titles", str(missing_title)),
                ("Missing Meta Desc", str(missing_desc)),
                ("Missing H1", str(missing_h1)),
            ]
            issues_pdf = []
            for p in valid_pages:
                for d in p.get("deductions", []):
                    issues_pdf.append({
                        "category": "On-Page Factor",
                        "severity": "High" if "H1" in d or "title" in d else "Medium",
                        "item": d,
                        "url": p["url"],
                        "problem": d,
                        "fix": "Review on-page optimization rules."
                    })
            pdf_bytes = generate_pdf_report("On-Page Technical Audit", target_url, kpis_pdf, issues_pdf)
            st.download_button("Export PDF", data=pdf_bytes, file_name="onpage_audit.pdf", mime="application/pdf", use_container_width=True)
            
    # Tabs for Detailed Breakdown
    tab_pages, tab_content, tab_schema, tab_technical, tab_links = st.tabs([
        "Page Summary Table",
        "Content & Readability",
        "Schema Validation",
        "Robots & Server Security",
        "Links & Media Audit"
    ])
    
    with tab_pages:
        st.dataframe(df_export, use_container_width=True, height=450)
        
    with tab_content:
        render_section_header("Content Quality & Readability Metrics")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            readability_df = pd.DataFrame([{
                "URL": p["url"][:60],
                "Word Count": p["content"]["word_count"],
                "Flesch Reading Ease": p["content"]["flesch_reading_ease"],
                "Grade Level": p["content"]["flesch_grade_level"],
                "Assessment": p["content"]["readability_label"]
            } for p in valid_pages])
            st.dataframe(readability_df, use_container_width=True)
        with col_r2:
            fig = px.histogram(readability_df, x="Flesch Reading Ease", nbins=10, title="Readability Distribution (60-70 is standard)", color_discrete_sequence=["#D4AF37"])
            st.plotly_chart(style_plotly_figure(fig, "Readability Score Distribution"), use_container_width=True)
            
    with tab_schema:
        render_section_header("Structured Data & Schema.org Audit")
        schema_rows = []
        for p in valid_pages:
            schema_rows.append({
                "URL": p["url"][:60],
                "Has Schema": "Valid" if p["schema"]["has_schema"] and not p["schema"]["issues"] else "Issues" if p["schema"]["issues"] else "None",
                "Declared Types": ", ".join(p["schema"]["types"]) or "None",
                "Duplicates": ", ".join(p["schema"]["duplicates"]) or "None",
                "Issues Detected": len(p["schema"]["issues"])
            })
        st.dataframe(pd.DataFrame(schema_rows), use_container_width=True)
        
    with tab_technical:
        render_section_header("Robots.txt Directives & Server Headers")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### Robots.txt Analysis")
            rb = audit_data["robots"]
            st.write(f"**Status:** {'Accessible (HTTP 200)' if rb.get('exists') else 'Not Found'}")
            st.write(f"**Disallow Directives:** {len(rb.get('disallowed', []))}")
            st.write(f"**Declared Sitemaps:** {len(rb.get('sitemaps', []))}")
            if rb.get("issues"):
                for issue in rb["issues"]:
                    st.warning(issue)
            else:
                st.success("No blocking issues detected in robots.txt.")
        with col_t2:
            st.markdown("#### Server Response Headers")
            st.dataframe(pd.DataFrame(audit_data["server_headers"]), use_container_width=True)
            
    with tab_links:
        render_section_header("Internal/External Links & Media Alt Text")
        media_rows = []
        for p in valid_pages:
            media_rows.append({
                "URL": p["url"][:60],
                "Total Images": p["images"]["total"],
                "Missing Alt Text": p["images"]["missing_alt_count"],
                "Internal Links": p["links"]["internal_count"],
                "External Links": p["links"]["external_count"],
                "Nofollow Links": p["links"]["nofollow_count"]
            })
        st.dataframe(pd.DataFrame(media_rows), use_container_width=True)
        
    render_footer()
