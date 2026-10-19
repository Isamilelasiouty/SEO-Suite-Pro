"""
On-Page Technical SEO Analyzer for SEO Suite Pro:
- DOM parsing with BeautifulSoup and lxml
- Title, Meta Description, Headings (H1-H6) hierarchy verification
- Readability scoring (Flesch Reading Ease, Flesch-Kincaid Grade Level)
- Content metrics: word count, reading time, text-to-HTML ratio
- Canonical, Robots meta, and Open Graph validation
- Structured Data / Schema.org deep inspection
- Internal vs External link architecture and image optimization audit
"""

import json
import re
from collections import Counter
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from core.config import ENGLISH_STOPWORDS

def count_syllables(word: str) -> int:
    """Estimates syllable count for English words."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = len(re.findall(r'[aeiouy]{1,2}', word))
    return max(1, syllables)

def calculate_readability(text: str) -> dict:
    """
    Computes Flesch Reading Ease and Flesch-Kincaid Grade Level.
    Flesch Reading Ease:
      90-100: Very Easy
      60-70: Standard (Target for web copy)
      0-30: Very Difficult / Academic
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 3]
    words = [w.strip() for w in re.findall(r'\b[a-zA-Z]+\b', text.lower()) if len(w) > 0]
    
    total_sentences = max(1, len(sentences))
    total_words = max(1, len(words))
    total_syllables = sum(count_syllables(w) for w in words)
    
    asl = total_words / total_sentences  # Average Sentence Length
    asw = total_syllables / total_words  # Average Syllables per Word
    
    fre = 206.835 - (1.015 * asl) - (84.6 * asw)
    fre = max(0.0, min(100.0, round(fre, 1)))
    
    fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
    fkgl = max(1.0, round(fkgl, 1))
    
    if fre >= 80:
        fre_label = "Easy"
    elif fre >= 60:
        fre_label = "Standard (Optimal)"
    elif fre >= 40:
        fre_label = "Moderate"
    else:
        fre_label = "Difficult"
        
    return {
        "flesch_reading_ease": fre,
        "flesch_grade_level": fkgl,
        "readability_label": fre_label,
        "sentence_count": total_sentences,
        "word_count": total_words
    }

def analyze_onpage(url: str, html_content: str, response_headers: dict | None = None) -> dict:
    """
    Comprehensive On-Page analysis of an HTML document.
    """
    if not html_content:
        return {"url": url, "error": "Empty or unreadable HTML content."}
        
    soup = BeautifulSoup(html_content, "lxml")
    
    # ── 1. Title Analysis ───────────────────────────────────────────
    title_tag = soup.find("title")
    title_text = title_tag.get_text().strip() if title_tag else ""
    title_len = len(title_text)
    if not title_text:
        title_status = "Missing"
        title_advice = "Add a descriptive title tag between 50 and 60 characters."
    elif title_len < 30:
        title_status = "Short"
        title_advice = f"Title is {title_len} chars. Expand to 50-60 characters for maximum search visibility."
    elif title_len > 65:
        title_status = "Long"
        title_advice = f"Title is {title_len} chars. Shorten to under 60 characters to avoid SERP truncation."
    else:
        title_status = "Optimal"
        title_advice = "Title length is optimal for search engine display."
        
    # ── 2. Meta Description ─────────────────────────────────────────
    meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if not meta_desc_tag:
        meta_desc_tag = soup.find("meta", attrs={"property": re.compile(r"^og:description$", re.I)})
    meta_desc = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""
    desc_len = len(meta_desc)
    
    if not meta_desc:
        desc_status = "Missing"
        desc_advice = "Add an enticing meta description between 120 and 160 characters."
    elif desc_len < 70:
        desc_status = "Short"
        desc_advice = f"Meta description is {desc_len} chars. Expand to 120-160 characters."
    elif desc_len > 165:
        desc_status = "Long"
        desc_advice = f"Meta description is {desc_len} chars. Shorten to 160 characters to prevent truncation."
    else:
        desc_status = "Optimal"
        desc_advice = "Meta description length is in the ideal range."
        
    # ── 3. Headings Structure ───────────────────────────────────────
    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
    h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
    h3_tags = [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]
    
    if len(h1_tags) == 0:
        h1_status = "Missing"
        h1_advice = "Page lacks an H1 heading. Add a single prominent H1 representing the page topic."
    elif len(h1_tags) > 1:
        h1_status = "Multiple"
        h1_advice = f"Page contains {len(h1_tags)} H1 headings. Consolidate into a single primary H1."
    else:
        h1_status = "Optimal"
        h1_advice = "Page contains exactly one clear H1 heading."
        
    # ── 4. Content Quality & Readability ────────────────────────────
    # Extract body text without scripts, styles, navigations on an isolated soup
    body_soup = BeautifulSoup(html_content, "lxml")
    for tag in body_soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.extract()
    body_text = body_soup.get_text(separator=" ", strip=True)
    
    readability = calculate_readability(body_text)
    html_size = len(html_content)
    text_size = len(body_text)
    text_ratio = round((text_size / max(1, html_size)) * 100, 1)
    reading_time_min = max(1, round(readability["word_count"] / 200))
    
    # Top keywords extracted from visible text
    words_clean = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', body_text.lower()) if w not in ENGLISH_STOPWORDS]
    word_freq = Counter(words_clean).most_common(12)
    top_keywords_str = ", ".join(f"{w} ({c})" for w, c in word_freq)
    
    # ── 5. Technical Directives (Canonical & Robots) ────────────────
    canonical_tag = soup.find("link", attrs={"rel": re.compile(r"^canonical$", re.I)})
    canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else ""
    
    parsed_base = urlparse(url)
    clean_base = f"{parsed_base.scheme}://{parsed_base.netloc}{parsed_base.path}".rstrip("/")
    clean_canon = canonical_url.rstrip("/")
    
    if not canonical_url:
        canon_status = "Missing"
        canon_advice = "Specify a self-referencing canonical tag to prevent duplicate content ambiguity."
    elif clean_canon == clean_base or clean_canon == clean_base + "/":
        canon_status = "Self-Referencing"
        canon_advice = "Canonical tag correctly self-references this page."
    else:
        canon_status = "Mismatched"
        canon_advice = f"Canonical points to external or alternate target: {canonical_url}."
        
    robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    robots_content = robots_meta.get("content", "").lower() if robots_meta else "index, follow"
    is_noindex = "noindex" in robots_content
    is_nofollow = "nofollow" in robots_content
    
    # ── 6. Open Graph & Social Cards ────────────────────────────────
    og_title = (soup.find("meta", property="og:title") or {}).get("content", "")
    og_desc = (soup.find("meta", property="og:description") or {}).get("content", "")
    og_image = (soup.find("meta", property="og:image") or {}).get("content", "")
    og_type = (soup.find("meta", property="og:type") or {}).get("content", "")
    twitter_card = (soup.find("meta", attrs={"name": "twitter:card"}) or {}).get("content", "")
    has_open_graph = bool(og_title or og_image)
    
    # ── 7. Structured Data / Schema.org ─────────────────────────────
    schema_blocks = []
    schema_types = []
    schema_issues = []
    
    for script in soup.find_all("script", attrs={"type": re.compile(r"application/ld\+json", re.I)}):
        raw_json = script.string or ""
        try:
            parsed = json.loads(raw_json.strip())
            items = parsed if isinstance(parsed, list) else [parsed]
            for item in items:
                stype = item.get("@type", "Unknown")
                if isinstance(stype, list):
                    stype = stype[0]
                stype_str = str(stype)
                schema_types.append(stype_str)
                
                # Check standard required fields
                item_issues = []
                if not item.get("@context"):
                    item_issues.append("Missing @context definition.")
                if stype_str in ("Article", "BlogPosting", "NewsArticle"):
                    if not item.get("headline"): item_issues.append("Missing 'headline'.")
                    if not item.get("author"): item_issues.append("Missing 'author'.")
                    if not item.get("datePublished"): item_issues.append("Missing 'datePublished'.")
                elif stype_str == "Product":
                    if not item.get("name"): item_issues.append("Missing 'name'.")
                    if not item.get("offers"): item_issues.append("Missing 'offers'.")
                elif stype_str == "FAQPage":
                    if not item.get("mainEntity"): item_issues.append("Missing 'mainEntity' QA list.")
                    
                schema_blocks.append({
                    "type": stype_str,
                    "format": "JSON-LD",
                    "issues": item_issues
                })
                schema_issues.extend(f"[{stype_str}] {i}" for i in item_issues)
        except json.JSONDecodeError as err:
            schema_issues.append(f"JSON-LD syntax error: {str(err)[:80]}")
            schema_blocks.append({"type": "Invalid JSON", "format": "JSON-LD", "issues": ["Syntax error"]})
            
    # Check for duplicate schemas
    type_counts = Counter(schema_types)
    duplicate_schemas = [t for t, c in type_counts.items() if c > 1]
    if duplicate_schemas:
        schema_issues.append(f"Duplicate schemas detected: {', '.join(duplicate_schemas)}")
        
    has_schema = len(schema_types) > 0
    
    # ── 8. Image Optimization Audit ─────────────────────────────────
    images = soup.find_all("img")
    total_images = len(images)
    missing_alt_images = []
    lazy_images = 0
    
    for img in images:
        src = img.get("src") or img.get("data-src") or "unknown"
        alt = img.get("alt")
        if alt is None or not alt.strip():
            missing_alt_images.append(src[:80])
        if img.get("loading", "").lower() == "lazy":
            lazy_images += 1
            
    # ── 9. Links Architecture ───────────────────────────────────────
    base_netloc = parsed_base.netloc.lower()
    internal_links = []
    external_links = []
    nofollow_count = 0
    
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
            
        full_link = urljoin(url, href)
        parsed_link = urlparse(full_link)
        rel = a.get("rel", [])
        if isinstance(rel, list):
            rel_str = " ".join(rel).lower()
        else:
            rel_str = str(rel).lower()
            
        if "nofollow" in rel_str:
            nofollow_count += 1
            
        anchor_text = a.get_text(strip=True) or "[EMPTY_ANCHOR]"
        
        if parsed_link.netloc.lower() == base_netloc:
            internal_links.append({"href": full_link, "anchor": anchor_text})
        else:
            external_links.append({"href": full_link, "anchor": anchor_text})
            
    # Compile On-Page Health Score (0-100)
    score = 100
    deductions = []
    if title_status != "Optimal":
        score -= 10
        deductions.append("Sub-optimal title tag (-10)")
    if desc_status != "Optimal":
        score -= 10
        deductions.append("Sub-optimal meta description (-10)")
    if h1_status != "Optimal":
        score -= 15
        deductions.append("Missing or multiple H1 headings (-15)")
    if is_noindex:
        score -= 25
        deductions.append("Page has noindex directive (-25)")
    if canon_status == "Missing":
        score -= 10
        deductions.append("Missing canonical tag (-10)")
    if not has_schema:
        score -= 10
        deductions.append("No schema markup found (-10)")
    if len(missing_alt_images) > 0:
        score -= min(10, len(missing_alt_images) * 2)
        deductions.append(f"{len(missing_alt_images)} images missing alt text")
    score = max(0, score)

    return {
        "url": url,
        "score": score,
        "deductions": deductions,
        "title": {
            "text": title_text,
            "length": title_len,
            "status": title_status,
            "advice": title_advice
        },
        "meta_description": {
            "text": meta_desc,
            "length": desc_len,
            "status": desc_status,
            "advice": desc_advice
        },
        "headings": {
            "h1": h1_tags,
            "h1_count": len(h1_tags),
            "h1_status": h1_status,
            "h1_advice": h1_advice,
            "h2": h2_tags[:15],
            "h2_count": len(h2_tags),
            "h3": h3_tags[:15],
            "h3_count": len(h3_tags)
        },
        "content": {
            "word_count": readability["word_count"],
            "reading_time_min": reading_time_min,
            "flesch_reading_ease": readability["flesch_reading_ease"],
            "flesch_grade_level": readability["flesch_grade_level"],
            "readability_label": readability["readability_label"],
            "html_size_kb": round(html_size / 1024, 1),
            "text_ratio_pct": text_ratio,
            "top_keywords": top_keywords_str
        },
        "directives": {
            "canonical_url": canonical_url,
            "canonical_status": canon_status,
            "canonical_advice": canon_advice,
            "robots_content": robots_content,
            "is_noindex": is_noindex,
            "is_nofollow": is_nofollow
        },
        "social": {
            "has_open_graph": has_open_graph,
            "og_title": og_title,
            "og_description": og_desc,
            "og_image": og_image,
            "og_type": og_type,
            "twitter_card": twitter_card
        },
        "schema": {
            "has_schema": has_schema,
            "types": schema_types,
            "blocks": schema_blocks,
            "issues": schema_issues,
            "duplicates": duplicate_schemas
        },
        "images": {
            "total": total_images,
            "missing_alt_count": len(missing_alt_images),
            "missing_alt_sample": missing_alt_images[:5],
            "lazy_count": lazy_images
        },
        "links": {
            "internal_count": len(internal_links),
            "external_count": len(external_links),
            "nofollow_count": nofollow_count,
            "internal_sample": internal_links[:10],
            "external_sample": external_links[:10]
        }
    }
