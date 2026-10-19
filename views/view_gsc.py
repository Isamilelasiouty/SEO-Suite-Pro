"""
Search Console Intelligence View for SEO Suite Pro:
- Dual Python & R Statistical Engine
- Ingestion of GSC JSON API payloads or CSV exports
- Scikit-Learn TF-IDF semantic query clustering
- 10-Class issue detector with root-cause explanations and technical fixes
- Algorithmic Keyword Cannibalization resolver with primary page attribution
- Time-series anomaly detection and hypothesis testing with R or Python fallback
- Export to CSV, Excel, and PDF
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from core.auth import get_current_user
from core.database import save_analysis
from services.gsc_processor import parse_gsc_csv, parse_gsc_json, process_search_console_data
from services.r_statistical_runner import run_statistical_analysis
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
    render_header(subtitle="Google Search Console Analytics & Dual Statistical Engine")
    user = get_current_user()
    
    col_input, col_meta = st.columns([2, 1])
    with col_input:
        brand_name = st.text_input("Brand Name (for Branded vs Non-Branded Analysis)", value="SEO Suite Pro")
        input_type = st.radio("Search Console Ingestion Method", ["Upload Search Console JSON / CSV", "Load Enterprise Benchmark Dataset"], horizontal=True)
        
    df_raw = None
    
    if input_type == "Upload Search Console JSON / CSV":
        uploaded_file = st.file_uploader("Upload Search Console Export (.json or .csv)", type=["json", "csv"])
        if uploaded_file:
            content_bytes = uploaded_file.read()
            if uploaded_file.name.endswith(".json"):
                df_raw = parse_gsc_json(content_bytes)
            else:
                df_raw = parse_gsc_csv(content_bytes)
            st.success(f"Parsed {len(df_raw)} records from {uploaded_file.name}.")
    else:
        df_raw = get_enterprise_sample_gsc_data()
        st.info("Loaded enterprise benchmark dataset representing real-world multi-device search performance.")

    run_btn = st.button("Run Full Search Console Analysis", type="primary", use_container_width=True)
    
    if (run_btn or df_raw is not None) and df_raw is not None and not df_raw.empty:
        # Process GSC Data
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
        ("Total Organic Clicks", f"{summary['total_clicks']:,}", "Selected analysis window"),
        ("Total Impressions", f"{summary['total_impressions']:,}", "SERP exposures"),
        ("Average CTR", f"{summary['overall_ctr_pct']}%", "Overall click-through rate"),
        ("Average Position", f"{summary['avg_position']}", "Domain-wide mean rank"),
    ])
    
    render_kpi_row([
        ("Unique Queries", f"{summary['unique_queries']:,}", "Distinct search terms"),
        ("Unique Landing Pages", f"{summary['unique_pages']:,}", "Indexed ranking URLs"),
        ("Cannibalization Cases", f"{summary['cannibalization_count']}", "Queries with competing URLs"),
        ("Flagged SEO Issues", f"{summary['total_issues_count']}", "Actionable technical items"),
    ])
    
    # ── Statistical Engine Status Banner ────────────────────────────
    st.markdown(f"""
    <div style="background:#141414;border:1px solid rgba(212,175,55,0.3);border-radius:8px;padding:12px 18px;margin:16px 0;display:flex;justify-content:space-between;align-items:center;">
        <div>
            <span style="font-weight:700;color:#D4AF37;">Statistical Engine:</span>
            <span style="color:#F5F5F5;margin-left:8px;">{stats_results.get('engine', 'Python Engine')}</span>
            <div style="font-size:11px;color:#A0A0A0;margin-top:2px;">{stats_results.get('notice', '')}</div>
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
        if user and st.button("Save GSC Analysis to My History", key="btn_save_gsc", use_container_width=True):
            save_analysis(user["id"], "gsc", f"GSC: {brand_name}", summary, {
                "summary": summary,
                "issues": issues,
                "cannibalization": cannibalization[:25]
            })
            st.success("Search Console analysis saved to your private history.")
            
    with col_exports:
        df_issues_export = pd.DataFrame(issues)
        df_cann_export = pd.DataFrame(cannibalization)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("Export CSV (Issues)", data=generate_csv_bytes(df_issues_export), file_name="gsc_issues.csv", mime="text/csv", use_container_width=True)
        with c2:
            st.download_button("Export Excel (Multi-Sheet)", data=generate_excel_bytes({
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
            st.download_button("Export Executive PDF", data=pdf_bytes, file_name="gsc_executive_report.pdf", mime="application/pdf", use_container_width=True)
            
    # ── Tabs Breakdown ──────────────────────────────────────────────
    tab_issues, tab_cannibalization, tab_clusters, tab_stats, tab_raw = st.tabs([
        "Issue Classification (10 Categories)",
        "Keyword Cannibalization Solver",
        "Semantic Intent Clusters (TF-IDF)",
        "Statistical & Anomaly Analysis (R/Python)",
        "Raw Data Explorer"
    ])
    
    with tab_issues:
        render_section_header("Identified SEO Issues & Root-Cause Fixes")
        
        # Category Filter
        cats = ["All Categories"] + sorted(list(set(i["category"] for i in issues)))
        selected_cat = st.selectbox("Filter by Category", cats)
        
        filtered_issues = issues if selected_cat == "All Categories" else [i for i in issues if i["category"] == selected_cat]
        st.markdown(f"**Showing {len(filtered_issues)} issues**")
        
        for idx, item in enumerate(filtered_issues, 1):
            sev_class = "badge-critical" if item["severity"] in ("Critical", "High") else "badge-warning" if item["severity"] in ("Warning", "Medium") else "badge-optimal"
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:12px;padding:16px 20px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div>
                        <span class="badge-label {sev_class}">{item['severity']}</span>
                        <span style="font-weight:700;color:#FFFFFF;margin-left:10px;">{item['category']}</span>
                    </div>
                    <div style="font-size:12px;color:#D4AF37;">Target: {item['item']}</div>
                </div>
                <div style="font-size:12px;color:#A0A0A0;margin-bottom:6px;"><strong>URL:</strong> {item['url']}</div>
                <div style="font-size:12px;color:#F5F5F5;margin-bottom:4px;"><strong>Data Evidence:</strong> {item['evidence']}</div>
                <div style="font-size:12px;color:#F5F5F5;margin-bottom:4px;"><strong>Root Cause:</strong> {item['problem']} ({item['why_it_happens']})</div>
                <div style="font-size:12px;color:#D4AF37;background:rgba(212,175,55,0.08);padding:8px 12px;border-radius:6px;border-left:2px solid #D4AF37;margin-top:8px;">
                    <strong>Prescribed Fix:</strong> {item['fix']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_cannibalization:
        render_section_header("Keyword Cannibalization & Intent Overlap Resolver")
        st.markdown("""
        <div style="font-size:12px;color:#A0A0A0;margin-bottom:16px;">
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
                        <div style="font-size:16px;font-weight:700;color:#D4AF37;">Query: "{c['query']}"</div>
                        <span class="badge-label badge-critical">{c['cause']}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px;">
                        <div style="background:#141414;padding:12px;border-radius:8px;border:1px solid rgba(212,175,55,0.3);">
                            <div class="card-label" style="color:#D4AF37;">Primary Designated Page</div>
                            <div style="font-size:12px;font-weight:600;color:#FFFFFF;word-break:break-all;">{c['primary_url']}</div>
                            <div style="font-size:11px;color:#A0A0A0;margin-top:4px;">{c['primary_metrics']}</div>
                        </div>
                        <div style="background:#141414;padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);">
                            <div class="card-label">Secondary Competing URLs ({len(c['secondary_urls'])})</div>
                            <div style="font-size:12px;color:#A0A0A0;word-break:break-all;">{c['secondary_urls'][0]}</div>
                            <div style="font-size:11px;color:#777777;margin-top:4px;">{c['secondary_metrics'][0]}</div>
                        </div>
                    </div>
                    <div style="font-size:12px;background:rgba(212,175,55,0.08);padding:10px 14px;border-radius:6px;border-left:3px solid #D4AF37;color:#F5F5F5;">
                        <strong style="color:#D4AF37;">Action Protocol:</strong> {c['recommended_action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with tab_clusters:
        render_section_header("Semantic Query Clustering via Scikit-Learn TF-IDF")
        col_cl1, col_cl2 = st.columns([1, 1.2])
        
        with col_cl1:
            cluster_counts = df_processed["cluster_label"].value_counts().reset_index()
            cluster_counts.columns = ["Semantic Intent Cluster", "Query Count"]
            fig_clust = px.pie(cluster_counts, names="Semantic Intent Cluster", values="Query Count", hole=0.5, color_discrete_sequence=["#D4AF37", "#B8962E", "#FFFFFF", "#888888", "#555555"])
            st.plotly_chart(style_plotly_figure(fig_clust, "Query Intent Distribution", height=320), use_container_width=True)
            
        with col_cl2:
            st.markdown("#### Intent Cluster Breakdown")
            st.dataframe(cluster_counts, use_container_width=True)
            
    with tab_stats:
        render_section_header("Statistical Analysis, Outliers & Hypothesis Testing")
        
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
        render_section_header("Raw Query & Landing Page Table")
        st.dataframe(df_processed, use_container_width=True, height=500)
        
    render_footer()
