"""
Google Search Console Intelligence View for SEO Suite Pro:
- Dedicated prominent GSC upload zone (.zip, .csv, .json)
- Automatic ZIP extractor for standard Search Console export archives
- Google and GSC SVG badges
- Bilingual English & Arabic support
- Dual Python & R Statistical Engine
- 10-Class issue detector, Cannibalization resolver, and multi-format exports
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from core.auth import get_current_user
from core.database import save_analysis
from core.i18n import get_current_lang, t
from services.gsc_processor import (
    parse_gsc_csv,
    parse_gsc_json,
    parse_gsc_zip,
    process_search_console_data,
)
from services.r_statistical_runner import run_statistical_analysis
from utils.export_csv import generate_csv_bytes
from utils.export_excel import generate_excel_bytes
from utils.export_pdf import generate_pdf_report
from views.components import (
    get_google_logo_svg,
    get_gsc_logo_svg,
    render_footer,
    render_header,
    render_kpi_row,
    render_section_header,
    style_plotly_figure,
)

def get_enterprise_sample_gsc_data() -> pd.DataFrame:
    """Generates a realistic enterprise Google Search Console dataset for testing."""
    sample = [
        {"query": "best enterprise seo tools", "page": "https://example.com/tools/enterprise", "clicks": 240, "impressions": 3800, "ctr": 0.063, "position": 3.1, "device": "DESKTOP"},
        {"query": "best enterprise seo tools", "page": "https://example.com/blog/top-seo-tools", "clicks": 18, "impressions": 3100, "ctr": 0.005, "position": 9.4, "device": "MOBILE"},
        {"query": "technical seo audit platform", "page": "https://example.com/audit-software", "clicks": 180, "impressions": 4200, "ctr": 0.042, "position": 4.2, "device": "DESKTOP"},
        {"query": "technical seo audit platform", "page": "https://example.com/services/technical-audit", "clicks": 12, "impressions": 3900, "ctr": 0.003, "position": 14.1, "device": "MOBILE"},
        {"query": "how to fix keyword cannibalization", "page": "https://example.com/guide/cannibalization", "clicks": 310, "impressions": 5800, "ctr": 0.053, "position": 2.8, "device": "DESKTOP"},
        {"query": "keyword cannibalization solutions", "page": "https://example.com/guide/cannibalization", "clicks": 95, "impressions": 2100, "ctr": 0.045, "position": 4.1, "device": "MOBILE"},
        {"query": "schema markup validator tool", "page": "https://example.com/tools/schema", "clicks": 420, "impressions": 6100, "ctr": 0.068, "position": 2.1, "device": "DESKTOP"},
        {"query": "free schema generator json ld", "page": "https://example.com/tools/schema-generator", "clicks": 15, "impressions": 4800, "ctr": 0.003, "position": 8.7, "device": "MOBILE"},
        {"query": "what is robot txt disallow", "page": "https://example.com/knowledge/robots-txt", "clicks": 0, "impressions": 1200, "ctr": 0.0, "position": 18.2, "device": "DESKTOP"},
        {"query": "seo suite pro login", "page": "https://example.com/login", "clicks": 850, "impressions": 1100, "ctr": 0.772, "position": 1.0, "device": "DESKTOP"},
        {"query": "seo suite pro pricing", "page": "https://example.com/pricing", "clicks": 320, "impressions": 900, "ctr": 0.355, "position": 1.1, "device": "MOBILE"},
        {"query": "crawl budget optimization guide", "page": "https://example.com/guide/crawl-budget", "clicks": 65, "impressions": 3400, "ctr": 0.019, "position": 11.2, "device": "DESKTOP"},
        {"query": "internal linking strategy ecommerce", "page": "https://example.com/ecommerce/internal-links", "clicks": 42, "impressions": 2900, "ctr": 0.014, "position": 12.8, "device": "MOBILE"},
        {"query": "xml sitemap index vs sitemap", "page": "https://example.com/blog/sitemaps", "clicks": 0, "impressions": 950, "ctr": 0.0, "position": 19.5, "device": "DESKTOP"},
    ] * 3
    return pd.DataFrame(sample)

def render_gsc_view():
    lang = get_current_lang()
    is_ar = (lang == "ar")
    
    render_header(subtitle=t("gsc_header"))
    user = get_current_user()
    
    # ── Dedicated GSC Upload Area ────────────────────────────────────
    google_svg = get_google_logo_svg(28)
    gsc_svg = get_gsc_logo_svg(28)
    
    st.markdown(f"""
    <div class="gsc-upload-zone">
        <div style="display:flex;justify-content:center;align-items:center;gap:12px;margin-bottom:8px;">
            {google_svg}
            {gsc_svg}
            <span style="font-family:'Poppins','Cairo',sans-serif;font-size:20px;font-weight:800;color:var(--gold);">
                {t('gsc_upload_box_title')}
            </span>
        </div>
        <div style="font-size:13px;color:var(--text-muted);max-width:680px;margin:0 auto 16px;line-height:1.6;">
            {t('gsc_upload_box_desc')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_upload, col_meta = st.columns([2.5, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            t("gsc_upload_label"),
            type=["zip", "csv", "json"],
            help="Supports ZIP exported from Google Search Console, or individual CSV/JSON files"
        )
    with col_meta:
        brand_name = st.text_input(t("gsc_brand_label"), value="SEO Suite Pro")
        use_sample = st.button(t("gsc_sample_btn"), use_container_width=True)
        
    df_raw = None
    file_info = ""
    
    if uploaded_file is not None:
        content_bytes = uploaded_file.read()
        fname = uploaded_file.name.lower()
        fsize_kb = round(len(content_bytes) / 1024, 1)
        
        try:
            if fname.endswith(".zip"):
                df_raw, extracted_list = parse_gsc_zip(content_bytes)
                file_info = f"Archive: {uploaded_file.name} ({fsize_kb} KB) | Extracted: {', '.join(extracted_list)}"
            elif fname.endswith(".json"):
                df_raw = parse_gsc_json(content_bytes)
                file_info = f"JSON API File: {uploaded_file.name} ({fsize_kb} KB)"
            else:
                df_raw = parse_gsc_csv(content_bytes)
                file_info = f"CSV Export: {uploaded_file.name} ({fsize_kb} KB)"
                
            st.success(f"{file_info} — Loaded {len(df_raw)} records.")
            
            # Show preview expander
            with st.expander("Preview Uploaded Search Console Data", expanded=False):
                st.dataframe(df_raw.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to process uploaded file: {str(e)}")
            
    elif use_sample:
        df_raw = get_enterprise_sample_gsc_data()
        st.info("Loaded enterprise benchmark dataset representing multi-device search performance.")

    run_btn = st.button(t("gsc_run_btn"), type="primary", use_container_width=True)
    
    if (run_btn or df_raw is not None) and df_raw is not None and not df_raw.empty:
        with st.spinner("Processing NLP intent clustering, cannibalization detection, and R statistical tests..."):
            gsc_results = process_search_console_data(df_raw, brand_name)
            stats_results = run_statistical_analysis(df_raw)
            
            st.session_state["active_gsc_analysis"] = {
                "results": gsc_results,
                "stats": stats_results,
                "df": df_raw,
                "brand_name": brand_name
            }
            
    active_analysis = st.session_state.get("active_gsc_analysis")
    if not active_analysis:
        render_footer()
        return
        
    gsc_results = active_analysis["results"]
    stats_results = active_analysis["stats"]
    summary = gsc_results["summary"]
    df_processed = gsc_results["dataframe"]
    cannibalization = gsc_results["cannibalization_cases"]
    issues = gsc_results["issues"]
    
    # ── High Level KPIs ─────────────────────────────────────────────
    render_kpi_row([
        (t("kpi_clicks"), f"{summary['total_clicks']:,}", "Organic clicks"),
        (t("kpi_impressions"), f"{summary['total_impressions']:,}", "SERP exposures"),
        (t("kpi_ctr"), f"{summary['overall_ctr_pct']}%", "Average click-through"),
        (t("kpi_position"), f"{summary['avg_position']}", "Domain-wide mean rank"),
    ])
    
    render_kpi_row([
        (t("kpi_queries"), f"{summary['unique_queries']:,}", "Distinct search terms"),
        (t("kpi_pages"), f"{summary['unique_pages']:,}", "Indexed landing pages"),
        (t("kpi_cannibalization"), f"{summary['cannibalization_count']}", "Queries with competing URLs"),
        (t("kpi_issues"), f"{summary['total_issues_count']}", "Actionable technical items"),
    ])
    
    # ── Statistical Engine Status Banner ────────────────────────────
    st.markdown(f"""
    <div style="background:var(--bg-surface);border:1px solid var(--gold-border);border-radius:10px;padding:12px 20px;margin:18px 0;display:flex;justify-content:space-between;align-items:center;box-shadow:var(--shadow-card);">
        <div>
            <span style="font-weight:700;color:var(--gold);">Statistical Engine:</span>
            <span style="color:var(--text-soft);margin-left:8px;">{stats_results.get('engine', 'Python Engine')}</span>
            <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">{stats_results.get('notice', '')}</div>
        </div>
        <div>
            <span class="badge-label {'badge-optimal' if stats_results.get('r_available') else 'badge-neutral'}">
                {'R Active' if stats_results.get('r_available') else 'Python Fallback Mode'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Actions & Exports ───────────────────────────────────────────
    col_save, col_exports = st.columns([1, 2])
    with col_save:
        if user and st.button(t("save_to_history"), key="btn_save_gsc", use_container_width=True):
            save_analysis(user["id"], "gsc", f"GSC: {brand_name}", summary, {
                "summary": summary,
                "issues": issues,
                "cannibalization": cannibalization[:25]
            })
            st.success(t("saved_success"))
            
    with col_exports:
        df_issues_export = pd.DataFrame(issues)
        df_cann_export = pd.DataFrame(cannibalization)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(t("export_csv"), data=generate_csv_bytes(df_issues_export), file_name="gsc_issues.csv", mime="text/csv", use_container_width=True)
        with c2:
            st.download_button(t("export_excel"), data=generate_excel_bytes({
                "SEO Issues": df_issues_export,
                "Cannibalization": df_cann_export,
                "All Queries": df_processed
            }), file_name="gsc_intelligence_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c3:
            kpis_pdf = [
                ("Total Clicks", f"{summary['total_clicks']:,}"),
                ("Total Impressions", f"{summary['total_impressions']:,}"),
                ("Overall CTR", f"{summary['overall_ctr_pct']}%"),
                ("Average Position", str(summary["avg_position"])),
                ("Cannibalization", str(summary["cannibalization_count"])),
                ("Total Issues", str(summary["total_issues_count"]))
            ]
            pdf_bytes = generate_pdf_report("Search Console Intelligence Report", brand_name, kpis_pdf, issues)
            st.download_button(t("export_pdf"), data=pdf_bytes, file_name="gsc_executive_report.pdf", mime="application/pdf", use_container_width=True)
            
    # ── Tabs Breakdown ──────────────────────────────────────────────
    tab_issues, tab_cannibalization, tab_clusters, tab_stats, tab_raw = st.tabs([
        t("tab_issues"),
        t("tab_cannibalization"),
        t("tab_clusters"),
        t("tab_stats"),
        t("tab_raw")
    ])
    
    with tab_issues:
        render_section_header(t("tab_issues"))
        
        # Category Filter
        cats = ["All Categories"] + sorted(list(set(i["category"] for i in issues)))
        selected_cat = st.selectbox(t("filter_category"), cats)
        
        filtered_issues = issues if selected_cat == "All Categories" else [i for i in issues if i["category"] == selected_cat]
        st.markdown(f"**{'عرض' if is_ar else 'Showing'} {len(filtered_issues)} {'مشكلة' if is_ar else 'issues'}**")
        
        for idx, item in enumerate(filtered_issues, 1):
            sev_class = "badge-critical" if item["severity"] in ("Critical", "High") else "badge-warning" if item["severity"] in ("Warning", "Medium") else "badge-optimal"
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:14px;padding:18px 22px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div>
                        <span class="badge-label {sev_class}">{item['severity']}</span>
                        <span style="font-weight:700;color:var(--text-primary);margin-left:10px;">{item['category']}</span>
                    </div>
                    <div style="font-size:12px;color:var(--gold);font-weight:600;">{item['item']}</div>
                </div>
                <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px;"><strong>Target URL:</strong> {item['url']}</div>
                <div style="font-size:12px;color:var(--text-soft);margin-bottom:4px;"><strong>Data Evidence:</strong> {item['evidence']}</div>
                <div style="font-size:12px;color:var(--text-soft);margin-bottom:4px;"><strong>Root Cause:</strong> {item['problem']} ({item['why_it_happens']})</div>
                <div style="font-size:12px;color:var(--gold);background:var(--gold-tint);padding:10px 14px;border-radius:8px;border-left:3px solid var(--gold);margin-top:10px;">
                    <strong>Prescribed Technical Fix:</strong> {item['fix']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_cannibalization:
        render_section_header(t("tab_cannibalization"))
        st.markdown("""
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:16px;">
            The algorithmic solver determines the Primary URL using weighted scoring: Clicks (40%) + Impressions (30%) + Position (20%) + CTR (10%).
            Inspect competing pages and apply prescribed technical actions (301 redirect, canonicalize, merge, or differentiate intent).
        </div>
        """, unsafe_allow_html=True)
        
        if not cannibalization:
            st.success("No keyword cannibalization detected in this dataset.")
        else:
            for c in cannibalization:
                st.markdown(f"""
                <div class="glass-card" style="margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div style="font-size:16px;font-weight:700;color:var(--gold);">Query: "{c['query']}"</div>
                        <span class="badge-label badge-critical">{c['cause']}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px;">
                        <div style="background:var(--bg-elevated);padding:12px;border-radius:8px;border:1px solid var(--gold-border);">
                            <div class="card-label" style="color:var(--gold);">Primary Designated Page</div>
                            <div style="font-size:12px;font-weight:600;color:var(--text-primary);word-break:break-all;">{c['primary_url']}</div>
                            <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">{c['primary_metrics']}</div>
                        </div>
                        <div style="background:var(--bg-elevated);padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                            <div class="card-label">Secondary Competing URLs ({len(c['secondary_urls'])})</div>
                            <div style="font-size:12px;color:var(--text-muted);word-break:break-all;">{c['secondary_urls'][0]}</div>
                            <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">{c['secondary_metrics'][0]}</div>
                        </div>
                    </div>
                    <div style="font-size:12px;background:var(--gold-tint);padding:10px 14px;border-radius:8px;border-left:3px solid var(--gold);color:var(--text-soft);">
                        <strong style="color:var(--gold);">Action Protocol:</strong> {c['recommended_action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with tab_clusters:
        render_section_header(t("tab_clusters"))
        col_cl1, col_cl2 = st.columns([1, 1.2])
        
        with col_cl1:
            cluster_counts = df_processed["cluster_label"].value_counts().reset_index()
            cluster_counts.columns = ["Semantic Intent Cluster", "Query Count"]
            fig_clust = px.pie(cluster_counts, names="Semantic Intent Cluster", values="Query Count", hole=0.5, color_discrete_sequence=["#D4AF37", "#B8962E", "#E5E7EB", "#9CA3AF", "#4B5563"])
            st.plotly_chart(style_plotly_figure(fig_clust, "Query Intent Distribution", height=320), use_container_width=True)
            
        with col_cl2:
            st.markdown("#### Intent Cluster Breakdown")
            st.dataframe(cluster_counts, use_container_width=True)
            
    with tab_stats:
        render_section_header(t("tab_stats"))
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### Anomaly & Outlier Fences (Tukey IQR)")
            clk_ano = stats_results.get("anomalies", {}).get("clicks", {})
            imp_ano = stats_results.get("anomalies", {}).get("impressions", {})
            st.write(f"**Click Outliers Detected:** {clk_ano.get('outlier_count', 0)}")
            st.write(f"**Click Upper Anomaly Threshold:** {clk_ano.get('upper_threshold', 0):,}")
            st.write(f"**Impression Outliers Detected:** {imp_ano.get('outlier_count', 0)}")
            st.write(f"**Impression Upper Threshold:** {imp_ano.get('upper_threshold', 0):,}")
            
        with col_s2:
            st.markdown("#### Distribution Statistics")
            ctr_dist = stats_results.get("distributions", {}).get("ctr", {})
            pos_dist = stats_results.get("distributions", {}).get("position", {})
            st.write(f"**CTR Mean / Median:** {ctr_dist.get('mean', 0)} / {ctr_dist.get('median', 0)}")
            st.write(f"**CTR Skewness:** {ctr_dist.get('skewness', 0)} ({'Right-skewed' if ctr_dist.get('skewness', 0) > 0 else 'Left-skewed'})")
            st.write(f"**Position Mean / Median:** {pos_dist.get('mean', 0)} / {pos_dist.get('median', 0)}")
            
        st.markdown("---")
        st.markdown("#### Device Hypothesis Testing")
        sig = stats_results.get("significance_testing", {})
        if sig.get("performed"):
            st.write(f"**Test Executed:** {sig.get('test_name')}")
            st.write(f"**p-Value:** {sig.get('p_value')} ({'Statistically Significant' if sig.get('statistically_significant') else 'Not Significant'})")
            st.info(sig.get("interpretation"))
        else:
            st.info(sig.get("reason", "Device hypothesis test skipped."))
            
        # Scatter Plot CTR vs Position
        fig_scatter = px.scatter(df_processed, x="position", y="ctr", size="impressions", hover_data=["query", "page"], title="CTR vs SERP Position (Bubble Size = Impressions)", color_discrete_sequence=["#D4AF37"])
        st.plotly_chart(style_plotly_figure(fig_scatter, "CTR vs Position Distribution Curve", height=380), use_container_width=True)
        
    with tab_raw:
        render_section_header(t("tab_raw"))
        st.dataframe(df_processed, use_container_width=True, height=500)
        
    render_footer()
