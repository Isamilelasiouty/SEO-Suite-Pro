"""
On-Page Technical SEO Audit View for SEO Suite Pro:
- Concurrent multi-page crawling or single-page deep audit
- DOM inspection (Titles, Meta Descriptions, Headings, Schema, Readability, Links, Images)
- Robots.txt and server security headers evaluation
- Export to CSV, Excel (.xlsx), and executive PDF
- One-click persistence to user's private history
- Fully bilingual (English & Arabic) with dynamic Light & Dark mode support
- Strict defensive error handling preventing unhandled exceptions
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from core.auth import get_current_user
from core.database import save_analysis
from core.i18n import get_current_lang, t
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

def render_onpage_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("onpage_header"))
    user = get_current_user()
    
    col_input, col_opts = st.columns([3, 1])
    with col_input:
        target_input = st.text_input(
            t("onpage_target_label"),
            placeholder="https://example.com",
            help="Include http:// or https://"
        )
    with col_opts:
        scope_options = [t("onpage_scope_single"), t("onpage_scope_sitemap")]
        crawl_mode = st.selectbox(t("onpage_scope_label"), scope_options)
        
    max_pages = 25
    if crawl_mode == t("onpage_scope_sitemap"):
        max_pages = st.slider(t("onpage_max_pages"), min_value=5, max_value=150, value=25, step=5)
        
    start_btn = st.button(t("onpage_run_btn"), type="primary", use_container_width=True)
    
    if start_btn and target_input:
        is_valid, norm_url, err_msg = validate_and_normalize_url(target_input)
        if not is_valid:
            st.error(f"Invalid URL: {err_msg}")
            return
            
        with st.spinner("Analyzing site structure and initiating audit..."):
            urls_to_crawl = [norm_url]
            sitemap_found = []
            
            if crawl_mode == t("onpage_scope_sitemap"):
                sitemaps = discover_sitemap_urls(norm_url)
                if sitemaps:
                    sitemap_found = sitemaps
                    parsed_pages = parse_xml_sitemap(sitemaps[0])
                    if parsed_pages:
                        urls_to_crawl = [p["url"] for p in parsed_pages[:max_pages]]
                        
            # Execute Crawl
            prog_text = "جاري الزحف وفحص شجرة الـ DOM..." if is_ar else "Fetching and parsing DOM structures..."
            prog_bar = st.progress(0, text=prog_text)
            
            def update_progress(curr, total, page_url):
                lbl = f"فحص الصفحة {curr}/{total}: {page_url[:60]}" if is_ar else f"Auditing page {curr}/{total}: {page_url[:60]}"
                prog_bar.progress(curr / total, text=lbl)
                
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
            msg = f"تم الفحص بنجاح لـ {len(page_audits)} صفحة." if is_ar else f"Audit completed successfully for {len(page_audits)} pages."
            st.success(msg)
            
    # Display Results if Present
    audit_data = st.session_state.get("active_onpage_audit")
    if not audit_data:
        info_txt = "أدخل رابط الموقع بالأعلى ثم اضغط 'تنفيذ الفحص الفني' لبدء التحليل الشامل." if is_ar else "Enter a target URL above and click 'Execute Technical Audit' to generate a full DOM report."
        st.info(info_txt)
        render_footer()
        return
        
    pages = audit_data["pages"]
    target_url = audit_data["target_url"]
    valid_pages = [p for p in pages if "error" not in p or not p.get("error")]
    
    # Check if all crawled pages failed
    if not valid_pages:
        err_detail = pages[0].get("error", "No readable content returned.") if pages else "No pages could be crawled."
        status_code = pages[0].get("status_code", 0) if pages else 0
        err_msg_text = (
            f"تعذر استخراج محتوى HTML للرابط المستهدف {target_url} (كود الاستجابة HTTP {status_code}): {err_detail}"
            if is_ar else
            f"Audit could not extract readable HTML content for {target_url} (HTTP Status {status_code}): {err_detail}"
        )
        st.warning(err_msg_text)
        
        if pages:
            df_err = pd.DataFrame([{
                "URL": p.get("url"),
                "HTTP Status": p.get("status_code"),
                "Latency (ms)": p.get("elapsed_ms"),
                "Details": p.get("error") or f"HTTP {p.get('status_code')}"
            } for p in pages])
            st.dataframe(df_err, use_container_width=True)
            
        render_footer()
        return
    
    # Overview KPIs
    avg_score = round(sum(p.get("score", 0) for p in valid_pages) / max(1, len(valid_pages)))
    total_scanned = len(pages)
    missing_title = sum(1 for p in valid_pages if p.get("title", {}).get("status") == "Missing")
    missing_desc = sum(1 for p in valid_pages if p.get("meta_description", {}).get("status") == "Missing")
    missing_h1 = sum(1 for p in valid_pages if p.get("headings", {}).get("h1_status") == "Missing")
    
    render_kpi_row([
        (t("kpi_health_score"), f"{avg_score} / 100", "Composite weighted score"),
        (t("kpi_pages_scanned"), total_scanned, "DOM responses analyzed"),
        (t("kpi_missing_titles"), missing_title, "Critical SERP factor"),
        (t("kpi_missing_h1"), missing_h1, "Structure deficiency"),
    ])
    
    # Save to user history
    col_save, col_exp = st.columns([1, 2])
    with col_save:
        if user and st.button(t("save_to_history"), key="btn_save_onpage", use_container_width=True):
            summary = {
                "avg_health_score": avg_score,
                "pages_scanned": total_scanned,
                "missing_title": missing_title,
                "missing_desc": missing_desc,
                "missing_h1": missing_h1
            }
            save_analysis(user["id"], "onpage", target_url, summary, audit_data)
            st.success(t("saved_success"))
            
    # Export Options
    with col_exp:
        rows_summary = []
        for i, p in enumerate(valid_pages, 1):
            title_info = p.get("title", {})
            meta_info = p.get("meta_description", {})
            head_info = p.get("headings", {})
            content_info = p.get("content", {})
            dir_info = p.get("directives", {})
            schema_info = p.get("schema", {})
            img_info = p.get("images", {})
            
            rows_summary.append({
                "#": i,
                "URL": p.get("url", ""),
                "Health Score": p.get("score", 0),
                "Title": title_info.get("text", ""),
                "Title Length": title_info.get("length", 0),
                "Title Status": title_info.get("status", "Missing"),
                "Meta Description": meta_info.get("text", ""),
                "H1 Count": head_info.get("h1_count", 0),
                "Word Count": content_info.get("word_count", 0),
                "Readability (Flesch)": content_info.get("flesch_reading_ease", 0.0),
                "Canonical Status": dir_info.get("canonical_status", "Not Specified"),
                "Has Schema": "Yes" if schema_info.get("has_schema") else "No",
                "Images Missing Alt": img_info.get("missing_alt_count", 0)
            })
        df_export = pd.DataFrame(rows_summary)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            csv_bytes = generate_csv_bytes(df_export)
            st.download_button(t("export_csv"), data=csv_bytes, file_name="onpage_audit.csv", mime="text/csv", use_container_width=True)
        with c2:
            excel_bytes = generate_excel_bytes({"On-Page Summary": df_export})
            st.download_button(t("export_excel"), data=excel_bytes, file_name="onpage_audit.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
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
                        "url": p.get("url", ""),
                        "problem": d,
                        "fix": "Review on-page optimization rules."
                    })
            pdf_bytes = generate_pdf_report("On-Page Technical Audit", target_url, kpis_pdf, issues_pdf)
            st.download_button(t("export_pdf"), data=pdf_bytes, file_name="onpage_audit.pdf", mime="application/pdf", use_container_width=True)
            
    # Tabs for Detailed Breakdown
    tab_pages, tab_content, tab_schema, tab_technical, tab_links = st.tabs([
        "Page Summary Table" if not is_ar else "جدول ملخص الصفحات",
        "Content & Readability" if not is_ar else "المحتوى وسهولة القراءة",
        "Schema Validation" if not is_ar else "فحص السكيما المنظمة",
        "Robots & Server Security" if not is_ar else "ملف Robots وترويسات السيرفر",
        "Links & Media Audit" if not is_ar else "الروابط وملفات الوسائط"
    ])
    
    with tab_pages:
        st.dataframe(df_export, use_container_width=True, height=450)
        
    with tab_content:
        render_section_header("Content Quality & Readability Metrics" if not is_ar else "جودة المحتوى ومقاييس سهولة القراءة")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            readability_df = pd.DataFrame([{
                "URL": p["url"][:60],
                "Word Count": p.get("content", {}).get("word_count", 0),
                "Flesch Reading Ease": p.get("content", {}).get("flesch_reading_ease", 0.0),
                "Grade Level": p.get("content", {}).get("flesch_grade_level", "N/A"),
                "Assessment": p.get("content", {}).get("readability_label", "Standard")
            } for p in valid_pages])
            st.dataframe(readability_df, use_container_width=True)
            
        with col_r2:
            if len(readability_df) >= 2 and "Flesch Reading Ease" in readability_df.columns:
                try:
                    fig = px.histogram(readability_df, x="Flesch Reading Ease", nbins=10, title="Readability Distribution (60-70 is standard)", color_discrete_sequence=["#D4AF37"])
                    st.plotly_chart(style_plotly_figure(fig, "Readability Score Distribution"), use_container_width=True)
                except Exception:
                    st.info(f"Average Flesch Reading Ease: {readability_df['Flesch Reading Ease'].mean():.1f}")
            elif len(readability_df) == 1:
                single_score = readability_df.iloc[0].get("Flesch Reading Ease", 0.0)
                single_label = readability_df.iloc[0].get("Assessment", "")
                st.markdown(
                    f'<div class="metric-card"><div class="card-label">Flesch Reading Ease</div><div class="card-value">{single_score}</div><div class="card-subtitle">{single_label} (Target: 60-70)</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("No readability metrics available for the audited pages.")
            
    with tab_schema:
        render_section_header("Structured Data & Schema.org Audit" if not is_ar else "البيانات المنظمة وفحص Schema.org")
        schema_rows = []
        for p in valid_pages:
            schema_info = p.get("schema", {})
            schema_rows.append({
                "URL": p["url"][:60],
                "Has Schema": "Valid" if schema_info.get("has_schema") and not schema_info.get("issues") else "Issues" if schema_info.get("issues") else "None",
                "Declared Types": ", ".join(schema_info.get("types", [])) or "None",
                "Duplicates": ", ".join(schema_info.get("duplicates", [])) or "None",
                "Issues Detected": len(schema_info.get("issues", []))
            })
        if schema_rows:
            st.dataframe(pd.DataFrame(schema_rows), use_container_width=True)
        else:
            st.info("No structured schema data detected.")
        
    with tab_technical:
        render_section_header("Robots.txt Directives & Server Headers" if not is_ar else "تعليمات Robots.txt وترويسات الأمان")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### Robots.txt Analysis" if not is_ar else "#### فحص ملف Robots.txt")
            rb = audit_data.get("robots", {})
            st.write(f"**Status:** {'Accessible (HTTP 200)' if rb.get('exists') else 'Not Found'}")
            st.write(f"**Disallow Directives:** {len(rb.get('disallowed', []))}")
            st.write(f"**Declared Sitemaps:** {len(rb.get('sitemaps', []))}")
            if rb.get("issues"):
                for issue in rb["issues"]:
                    st.warning(issue)
            else:
                st.success("No blocking issues detected in robots.txt.")
        with col_t2:
            st.markdown("#### Server Response Headers" if not is_ar else "#### ترويسات استجابة السيرفر")
            headers_data = audit_data.get("server_headers", [])
            if headers_data:
                st.dataframe(pd.DataFrame(headers_data), use_container_width=True)
            else:
                st.info("No server header data captured.")
            
    with tab_links:
        render_section_header("Internal/External Links & Media Alt Text" if not is_ar else "الروابط الداخلية والخارجية ونصوص الصور")
        media_rows = []
        for p in valid_pages:
            img_info = p.get("images", {})
            link_info = p.get("links", {})
            media_rows.append({
                "URL": p["url"][:60],
                "Total Images": img_info.get("total", 0),
                "Missing Alt Text": img_info.get("missing_alt_count", 0),
                "Internal Links": link_info.get("internal_count", 0),
                "External Links": link_info.get("external_count", 0),
                "Nofollow Links": link_info.get("nofollow_count", 0)
            })
        if media_rows:
            st.dataframe(pd.DataFrame(media_rows), use_container_width=True)
        else:
            st.info("No media or link data captured.")
        
    render_footer()
