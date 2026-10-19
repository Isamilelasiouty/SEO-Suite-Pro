"""
Unit tests for On-Page technical SEO analysis, readability scoring, and schema validation.
"""

from services.onpage_analyzer import analyze_onpage, calculate_readability, count_syllables

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Technical SEO Architecture Checklist for 2026</title>
    <meta name="description" content="A comprehensive guide to modern enterprise search architecture, covering crawl budget, schema markup, and canonicalization.">
    <link rel="canonical" href="https://example.com/guide">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Enterprise Technical SEO Architecture",
        "author": "Ismail El Asiouty",
        "datePublished": "2026-01-15"
    }
    </script>
</head>
<body>
    <h1>Enterprise Technical SEO Architecture</h1>
    <h2>Crawl Budget Preservation</h2>
    <p>Search engines allocate limited crawl budgets to large websites. Optimizing server latency and XML sitemaps preserves crawl resources.</p>
    <h2>Canonical Directives and Intent</h2>
    <p>Canonical tags instruct crawlers regarding duplicate variations of similar documents.</p>
    <img src="/assets/chart.png" alt="Architecture diagram" />
    <img src="/assets/icon.png" />
    <a href="https://example.com/services">Internal Services</a>
    <a href="https://google.com" rel="nofollow">External Resource</a>
</body>
</html>
"""

def test_syllable_count():
    assert count_syllables("cat") == 1
    assert count_syllables("architecture") >= 3

def test_readability():
    text = "This is a simple sentence. It is very easy to read and understand."
    res = calculate_readability(text)
    assert res["flesch_reading_ease"] >= 60

def test_onpage_analysis():
    audit = analyze_onpage("https://example.com/guide", SAMPLE_HTML)
    assert audit["title"]["status"] == "Optimal"
    assert audit["headings"]["h1_count"] == 1
    assert audit["headings"]["h1_status"] == "Optimal"
    assert audit["schema"]["has_schema"] is True
    assert "Article" in audit["schema"]["types"]
    assert audit["directives"]["canonical_status"] == "Self-Referencing"
    assert audit["images"]["total"] == 2
    assert audit["images"]["missing_alt_count"] == 1
    assert audit["links"]["internal_count"] == 1
    assert audit["links"]["external_count"] == 1
    assert audit["links"]["nofollow_count"] == 1
