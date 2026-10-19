"""
Unit tests for Search Console parsing, ZIP archives, TF-IDF clustering, cannibalization detection, and issue classification.
"""

import io
import zipfile
import pandas as pd
from core.i18n import set_lang, t
from services.gsc_processor import (
    cluster_queries_tfidf,
    detect_keyword_cannibalization,
    parse_gsc_csv,
    parse_gsc_zip,
    process_search_console_data,
)

def test_cannibalization_detection():
    data = [
        {"query": "seo audit tool", "page": "https://example.com/tool", "clicks": 100, "impressions": 1000, "ctr": 0.10, "position": 2.0},
        {"query": "seo audit tool", "page": "https://example.com/tool-duplicate", "clicks": 2, "impressions": 800, "ctr": 0.002, "position": 14.0},
        {"query": "unique query", "page": "https://example.com/page", "clicks": 50, "impressions": 500, "ctr": 0.10, "position": 1.0}
    ]
    df = pd.DataFrame(data)
    cannibal = detect_keyword_cannibalization(df)
    
    assert len(cannibal) == 1
    case = cannibal[0]
    assert case["query"] == "seo audit tool"
    assert case["primary_url"] == "https://example.com/tool"
    assert len(case["secondary_urls"]) == 1

def test_gsc_pipeline():
    data = [
        {"query": "best enterprise seo platform", "page": "https://example.com/platform", "clicks": 200, "impressions": 4000, "ctr": 0.05, "position": 3.0, "device": "DESKTOP"},
        {"query": "best enterprise seo platform", "page": "https://example.com/blog/platform", "clicks": 10, "impressions": 3000, "ctr": 0.003, "position": 11.0, "device": "MOBILE"},
        {"query": "technical seo guide", "page": "https://example.com/guide", "clicks": 50, "impressions": 2000, "ctr": 0.025, "position": 7.0, "device": "DESKTOP"},
        {"query": "zero click search terms", "page": "https://example.com/terms", "clicks": 0, "impressions": 500, "ctr": 0.0, "position": 15.0, "device": "MOBILE"},
    ] * 3
    df = pd.DataFrame(data)
    res = process_search_console_data(df, brand_name="example")
    
    assert res["summary"]["total_clicks"] > 0
    assert len(res["cannibalization_cases"]) >= 1
    assert len(res["issues"]) > 0

def test_parse_gsc_zip():
    """Verify in-memory ZIP archive unpacking with Queries.csv and Pages.csv."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        queries_csv = "Top queries,Clicks,Impressions,CTR,Position\nkeyword 1,120,2000,6.0%,2.1\nkeyword 2,40,1500,2.6%,8.4\n"
        pages_csv = "Top pages,Clicks,Impressions,CTR,Position\nhttps://example.com/p1,100,1800,5.5%,2.3\nhttps://example.com/p2,60,1700,3.5%,7.1\n"
        z.writestr("Queries.csv", queries_csv)
        z.writestr("Pages.csv", pages_csv)
        
    zip_bytes = zip_buffer.getvalue()
    df_result, extracted = parse_gsc_zip(zip_bytes)
    
    assert len(extracted) == 2
    assert len(df_result) >= 2
    assert "query" in df_result.columns
    assert "page" in df_result.columns
    assert df_result["clicks"].sum() > 0

def test_i18n_bilingual():
    """Verify English and Arabic translation dictionaries."""
    set_lang("en")
    assert "Google Search Console" in t("gsc_header")
    assert t("theme_dark") == "Dark Mode"
    
    set_lang("ar")
    assert "جوجل سيرش كونسول" in t("gsc_header")
    assert "الليلي" in t("theme_dark")
