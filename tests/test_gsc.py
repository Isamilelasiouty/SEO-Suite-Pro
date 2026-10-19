"""
Unit tests for Search Console parsing, TF-IDF clustering, cannibalization detection, and issue classification.
"""

import pandas as pd
from services.gsc_processor import (
    cluster_queries_tfidf,
    detect_keyword_cannibalization,
    parse_gsc_csv,
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
