"""
Off-Page SEO & Backlink Intelligence Engine for SEO Suite Pro:
- Anchor text categorization (Exact Match, Partial, Branded, Generic, Naked URL)
- Algorithmic Over-Optimization Penalty Risk scoring
- Link diversity metrics and authority distribution modeling
- Brand mention footprint analysis
"""

import re
from urllib.parse import urlparse

GENERIC_ANCHOR_PATTERNS = {
    "click here", "here", "website", "link", "source", "read more", "learn more",
    "visit website", "check this out", "page", "this article", "view more", "more info",
    "details", "online", "homepage", "author", "post", "blog"
}

def classify_anchor_text(anchor: str, brand_name: str, target_keyword: str) -> str:
    """
    Classifies anchor text into industry standard distribution categories.
    """
    a = (anchor or "").strip().lower()
    b = (brand_name or "").strip().lower()
    k = (target_keyword or "").strip().lower()
    
    if not a or a == "[empty_anchor]":
        return "Generic"
    
    # Check if naked URL
    if a.startswith("http") or "www." in a or ".com" in a or ".org" in a or ".net" in a or "/" in a:
        return "Naked URL"
        
    # Check generic
    if a in GENERIC_ANCHOR_PATTERNS:
        return "Generic"
        
    # Check branded
    if b and (b in a or a in b):
        return "Branded"
        
    # Check exact match keyword
    if k and a == k:
        return "Exact Match"
        
    # Check partial match
    if k and any(word in a for word in k.split() if len(word) > 3):
        return "Partial Match"
        
    return "Generic"

def analyze_backlink_profile(backlinks_data: list[dict], brand_name: str = "", target_keyword: str = "") -> dict:
    """
    Analyzes a backlink dataset or simulated profile:
    Expected dict structure for each link:
    {'source_url', 'target_url', 'anchor_text', 'is_nofollow', 'authority_score'}
    """
    total_links = len(backlinks_data)
    if total_links == 0:
        return {
            "total_backlinks": 0,
            "referring_domains": 0,
            "distribution": {},
            "penalty_risk_score": 0,
            "penalty_risk_label": "No Data",
            "dofollow_ratio_pct": 0,
            "deep_link_ratio_pct": 0,
            "recommendations": ["No backlink records provided to evaluate."]
        }
        
    domains = set()
    anchor_categories = {"Exact Match": 0, "Partial Match": 0, "Branded": 0, "Generic": 0, "Naked URL": 0}
    dofollow_count = 0
    deep_link_count = 0
    
    for item in backlinks_data:
        src = item.get("source_url", "")
        if src:
            domains.add(urlparse(src).netloc.lower())
            
        target = item.get("target_url", "")
        parsed_target = urlparse(target)
        if parsed_target.path and parsed_target.path not in ("/", ""):
            deep_link_count += 1
            
        if not item.get("is_nofollow", False):
            dofollow_count += 1
            
        cat = classify_anchor_text(item.get("anchor_text", ""), brand_name, target_keyword)
        anchor_categories[cat] += 1
        
    # Percentages
    pct_dist = {k: round((v / total_links) * 100, 1) for k, v in anchor_categories.items()}
    exact_pct = pct_dist.get("Exact Match", 0)
    partial_pct = pct_dist.get("Partial Match", 0)
    branded_pct = pct_dist.get("Branded", 0)
    generic_pct = pct_dist.get("Generic", 0)
    naked_pct = pct_dist.get("Naked URL", 0)
    
    # Over-Optimization Risk Model
    # Healthy natural profiles have: Branded + Naked + Generic > 70%, Exact Match < 15%
    risk_score = 0
    recs = []
    
    if exact_pct > 25:
        risk_score += 60
        recs.append(f"High penalty danger: Exact match anchor text is {exact_pct}%. Keep below 10-15% to prevent algorithmic Penguin flags.")
    elif exact_pct > 15:
        risk_score += 30
        recs.append(f"Elevated exact match anchors ({exact_pct}%). Balance with branded and generic variations.")
        
    if branded_pct < 20 and brand_name:
        risk_score += 20
        recs.append(f"Low branded anchor presence ({branded_pct}%). Natural authority profiles typically feature 35-50% branded anchors.")
        
    dofollow_ratio = round((dofollow_count / total_links) * 100, 1)
    if dofollow_ratio > 95:
        risk_score += 15
        recs.append("Dofollow ratio exceeds 95%. A natural link profile includes a blend of nofollow/sponsored links.")
        
    risk_score = min(100, risk_score)
    if risk_score >= 50:
        risk_label = "High Risk"
    elif risk_score >= 25:
        risk_label = "Moderate Risk"
    else:
        risk_label = "Healthy & Natural"
        
    deep_link_ratio = round((deep_link_count / total_links) * 100, 1)

    return {
        "total_backlinks": total_links,
        "referring_domains": len(domains),
        "distribution_counts": anchor_categories,
        "distribution_pct": pct_dist,
        "penalty_risk_score": risk_score,
        "penalty_risk_label": risk_label,
        "dofollow_ratio_pct": dofollow_ratio,
        "deep_link_ratio_pct": deep_link_ratio,
        "recommendations": recs if recs else ["Backlink profile demonstrates healthy anchor diversity and natural distribution."]
    }
