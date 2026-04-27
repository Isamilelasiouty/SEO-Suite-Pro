"""
╔══════════════════════════════════════════════════════════════╗
║              🚀 SEO Suite Pro — Python Edition              ║
║  🗺️  Sitemap Analyzer  |  🔍 Schema Checker                 ║
║  🔑 Keyword Extractor  |  🏠 Master Dashboard               ║
╚══════════════════════════════════════════════════════════════╝
"""

import re
import json
import time
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

# ═══════════════════════════════════════════════════════════════
#  ⚙️ CONFIGURATION
# ═══════════════════════════════════════════════════════════════
DEFAULT_CFG = dict(OLD_MONTHS=12, WARN_MONTHS=6, MAX_PAGES=150,
                   MIN_WORD_LEN=4, MIN_WORD_FREQ=3, TOP_KEYWORDS=30)

STOP_WORDS = {
    "من","إلى","على","في","عن","مع","هذا","هذه","التي","الذي","كان","كانت",
    "هو","هي","هم","أن","إن","لا","ما","لم","قد","كل","بعد","قبل","حتى",
    "أو","و","أي","ثم","لكن","بل","غير","عند","منذ","خلال","حول","نحو",
    "ذلك","تلك","هؤلاء","الذين","كيف","لماذا","متى","أين",
    "the","and","for","with","this","that","from","have","has","are","was",
    "were","been","will","would","could","should","their","there","then",
    "than","into","your","our","its","not","but","can","all","out","more",
    "also","when","what","which","who","how","they","them","some","about",
    "after","before","just","like","make","know","take","over","such","even",
    "most","back","only","well","very","still","here","come","good","new",
    "because","between","through","under","while","where","these","those",
}

SCHEMA_FIX_MAP = {
    "JSON خاطئ": "افتح الـ Schema في jsonlint.com وصلح الـ JSON",
    "@context": 'أضف "https://schema.org" في @context',
    "@type": "أضف نوع الـ Schema في @type",
    "headline": "أضف headline بعنوان المقال (أقل من 110 حرف)",
    "author": "أضف author باسم الكاتب",
    "datePublished": "أضف datePublished بتاريخ ISO مثل: 2024-01-15",
    "image": "أضف image برابط صورة واضحة",
    "offers": "أضف offers بالسعر والعملة",
    "mainEntity": "أضف mainEntity بقائمة الأسئلة والأجوبة",
    "reviewRating": "أضف reviewRating بتقييم من 1 لـ 5",
    "thumbnailUrl": "أضف thumbnailUrl لصورة الـ thumbnail",
    "uploadDate": "أضف uploadDate بتاريخ رفع الفيديو",
    "startDate": "أضف startDate بتاريخ بداية الفعالية",
    "Duplicate": "احذف الـ Schema المتكررة وسيّب واحدة بس",
    "ملهاش أي Schema": "أضف Schema مناسبة — راجع schema.org",
}

# ═══════════════════════════════════════════════════════════════
#  🛠️ SEO ENGINE — Core logic
# ═══════════════════════════════════════════════════════════════

def fetch_html(url: str, timeout: int = 15) -> str | None:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEOSuitePro/2.0; +https://github.com)"}
        r = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def months_ago(date_str: str | None) -> float | None:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m"):
        try:
            dt = datetime.strptime(date_str[:len(fmt.replace('%z','').replace('%','XX'))], fmt)
            return (datetime.now() - dt.replace(tzinfo=None)).days / 30.44
        except ValueError:
            continue
    try:
        from datetime import timezone
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        return (now - dt).days / 30.44
    except Exception:
        return None


def extract_tag_values(xml: str, tag: str) -> list[str]:
    vals = re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.IGNORECASE | re.DOTALL)
    return [v.strip().replace("<![CDATA[", "").replace("]]>", "").strip() for v in vals]


# ─── SITEMAP ────────────────────────────────────────────────────

def find_sitemap_urls(site_url: str) -> list[str]:
    candidates = [
        site_url + "/sitemap.xml",
        site_url + "/sitemap_index.xml",
        site_url + "/sitemap-index.xml",
        site_url + "/wp-sitemap.xml",
        site_url + "/post-sitemap.xml",
        site_url + "/news-sitemap.xml",
    ]
    try:
        robots = fetch_html(site_url + "/robots.txt")
        if robots:
            for u in re.findall(r"Sitemap:\s*(https?://\S+)", robots, re.IGNORECASE):
                u = u.strip()
                if u not in candidates:
                    candidates.insert(0, u)
    except Exception:
        pass

    found = []
    for url in candidates:
        content = fetch_html(url)
        if not content:
            continue
        if "<sitemap>" in content:
            locs = [l.strip().replace("<![CDATA[", "").replace("]]>", "")
                    for l in extract_tag_values(content, "loc") if l.strip().endswith(".xml")]
            found.extend(locs)
            break
        if "<url>" in content:
            found.append(url)
            break
    return list(dict.fromkeys(found))


def parse_sitemap(sitemap_url: str) -> list[dict]:
    content = fetch_html(sitemap_url)
    if not content:
        return []
    locs       = extract_tag_values(content, "loc")
    lastmods   = extract_tag_values(content, "lastmod")
    changefreqs = extract_tag_values(content, "changefreq")
    priorities  = extract_tag_values(content, "priority")

    pages = []
    for i, url in enumerate(locs):
        if url.endswith(".xml"):
            continue
        lm = lastmods[i] if i < len(lastmods) else None
        pages.append({
            "url":        url,
            "lastmod":    lm,
            "changefreq": changefreqs[i] if i < len(changefreqs) else None,
            "priority":   priorities[i]  if i < len(priorities)  else None,
            "months_ago": months_ago(lm),
        })
    return pages


def categorize_sitemap(pages: list[dict], cfg: dict) -> dict:
    old_m, warn_m = cfg["OLD_MONTHS"], cfg["WARN_MONTHS"]
    sorted_pages = sorted(pages, key=lambda p: p["lastmod"] or "")
    return {
        "all":     sorted_pages,
        "old":     [p for p in sorted_pages if p["months_ago"] and p["months_ago"] >= old_m],
        "warn":    [p for p in sorted_pages if p["months_ago"] and warn_m <= p["months_ago"] < old_m],
        "fresh":   [p for p in sorted_pages if p["months_ago"] and p["months_ago"] < warn_m],
        "no_date": [p for p in sorted_pages if not p["months_ago"]],
    }


# ─── SCHEMA ─────────────────────────────────────────────────────

def extract_schema_type(obj: dict) -> str:
    if not obj:
        return "Unknown"
    t = obj.get("@type", "Unknown")
    return t[0] if isinstance(t, list) else str(t)


def validate_schema_block(obj: dict, type_name: str) -> list[str]:
    issues = []
    if not obj:
        return issues
    if not obj.get("@context"):
        issues.append("مفيش @context")
    if not obj.get("@type"):
        issues.append("مفيش @type")

    checks = {
        ("Article", "BlogPosting", "NewsArticle"): [
            ("headline", "مفيش headline"),
            ("author", "مفيش author"),
            ("datePublished", "مفيش datePublished"),
            ("image", "مفيش image"),
        ],
        ("Product",): [("name","مفيش name"),("offers","مفيش offers"),("image","مفيش image")],
        ("FAQPage",): [("mainEntity","مفيش mainEntity")],
        ("BreadcrumbList",): [("itemListElement","مفيش itemListElement")],
        ("LocalBusiness", "Organization"): [("name","مفيش name"),("address","مفيش address")],
        ("Review",): [("reviewRating","مفيش reviewRating"),("author","مفيش author")],
        ("HowTo",): [("name","مفيش name"),("step","مفيش steps")],
        ("Recipe",): [("name","مفيش name"),("recipeIngredient","مفيش recipeIngredient"),
                       ("recipeInstructions","مفيش recipeInstructions")],
        ("VideoObject",): [("name","مفيش name"),("description","مفيش description"),
                            ("thumbnailUrl","مفيش thumbnailUrl"),("uploadDate","مفيش uploadDate")],
        ("Event",): [("name","مفيش name"),("startDate","مفيش startDate"),("location","مفيش location")],
    }
    for types, fields in checks.items():
        if type_name in types:
            for field, msg in fields:
                if not obj.get(field):
                    issues.append(msg)
    if type_name in ("Article","BlogPosting","NewsArticle"):
        if obj.get("headline") and len(str(obj["headline"])) > 110:
            issues.append("headline أطول من 110 حرف")
    if type_name == "LocalBusiness" and not obj.get("telephone"):
        issues.append("مفيش telephone")
    return issues


def parse_schema(html: str) -> dict:
    r = dict(has_schema=False, schema_types=[], schema_blocks=[],
             has_json_ld=False, has_microdata=False, has_rdfa=False,
             has_duplicate=False, issues=[])

    # JSON-LD
    for idx, inner in enumerate(re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
        html, re.IGNORECASE
    )):
        try:
            parsed = json.loads(inner.strip())
        except json.JSONDecodeError as e:
            r["issues"].append(f"JSON-LD #{idx+1}: JSON خاطئ — {str(e)[:80]}")
            r["schema_blocks"].append({"type":"JSON خاطئ","format":"JSON-LD","issues":["JSON syntax error"]})
            r["has_schema"] = r["has_json_ld"] = True
            continue
        for item in (parsed if isinstance(parsed, list) else [parsed]):
            tn = extract_schema_type(item)
            bi = validate_schema_block(item, tn)
            r["schema_blocks"].append({"type":tn,"format":"JSON-LD","issues":bi})
            if tn not in r["schema_types"]:
                r["schema_types"].append(tn)
            r["issues"].extend(f"[{tn}] {i}" for i in bi)
        r["has_json_ld"] = r["has_schema"] = True

    # Microdata
    if re.search(r"itemtype\s*=\s*[\"']https?://schema\.org", html, re.IGNORECASE):
        r["has_microdata"] = r["has_schema"] = True
        for m in re.finditer(r"itemtype\s*=\s*[\"']https?://schema\.org/([^\"'\s]+)[\"']", html, re.IGNORECASE):
            tn = m.group(1)
            if tn not in r["schema_types"]:
                r["schema_types"].append(tn)
            r["schema_blocks"].append({"type":tn,"format":"Microdata","issues":[]})

    # RDFa
    if re.search(r"typeof\s*=\s*[\"'][^\"']*schema\.org", html, re.IGNORECASE):
        r["has_rdfa"] = r["has_schema"] = True
        if "RDFa" not in r["schema_types"]:
            r["schema_types"].append("RDFa")
        r["schema_blocks"].append({"type":"RDFa","format":"RDFa","issues":[]})

    # Duplicates
    tc = Counter(b["type"] for b in r["schema_blocks"])
    for tn, cnt in tc.items():
        if cnt > 1:
            r["has_duplicate"] = True
            r["issues"].append(f'🔁 Duplicate: "{tn}" موجود {cnt} مرات')

    if not r["has_schema"]:
        r["issues"].append("الصفحة ملهاش أي Schema markup")
    return r


# ─── KEYWORDS ───────────────────────────────────────────────────

def analyze_word_freq(text: str, cfg: dict) -> dict:
    words = re.sub(r"[^\u0600-\u06FFa-zA-Z\s]", " ", text.lower()).split()
    words = [w for w in words if len(w) >= cfg["MIN_WORD_LEN"] and w not in STOP_WORDS]
    freq = Counter(words)
    return {w: c for w, c in freq.items() if c >= cfg["MIN_WORD_FREQ"]}


def extract_headings(html: str, tag: str) -> list[str]:
    out = []
    for m in re.finditer(rf"<{tag}[^>]*>([\s\S]*?)</{tag}>", html, re.IGNORECASE):
        text = re.sub(r"<[^>]+>", " ", m.group(1))
        text = re.sub(r"\s+", " ", text).strip()
        if 2 < len(text) < 250:
            out.append(text)
    return out


def parse_keywords(html: str, cfg: dict) -> dict:
    r = dict(title="", meta_description="", meta_keywords="", focus_keyword="",
             h1=[], h2=[], h3=[], word_freq={}, top_words="")

    m = re.search(r"<title[^>]*>([\s\S]*?)</title>", html, re.IGNORECASE)
    r["title"] = re.sub(r"<[^>]+>", "", m.group(1)).strip()[:300] if m else ""

    m = (re.search(r"<meta[^>]*name=[\"']description[\"'][^>]*content=[\"']([^\"']*)", html, re.IGNORECASE) or
         re.search(r"<meta[^>]*content=[\"']([^\"']*)[^>]*name=[\"']description[\"']", html, re.IGNORECASE))
    r["meta_description"] = m.group(1)[:300] if m else ""

    m = (re.search(r"<meta[^>]*name=[\"']keywords[\"'][^>]*content=[\"']([^\"']*)", html, re.IGNORECASE) or
         re.search(r"<meta[^>]*content=[\"']([^\"']*)[^>]*name=[\"']keywords[\"']", html, re.IGNORECASE))
    r["meta_keywords"] = m.group(1)[:300] if m else ""

    m = (re.search(r"focuskw[\"'\s]*:[\"'\s]*([^\"'\",\n]+)", html, re.IGNORECASE) or
         re.search(r"_yoast_wpseo_focuskw[\"'\s:>]+([^<\"'&\n]+)", html, re.IGNORECASE) or
         re.search(r"rank_math_focus_keyword[\"'\s:>]+([^<\"'&\n]+)", html, re.IGNORECASE))
    r["focus_keyword"] = m.group(1).strip()[:100] if m else ""

    r["h1"] = extract_headings(html, "h1")
    r["h2"] = extract_headings(html, "h2")
    r["h3"] = extract_headings(html, "h3")

    body = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body, flags=re.IGNORECASE)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    r["word_freq"] = analyze_word_freq(body, cfg)
    r["top_words"] = ", ".join(f"{w}({c})" for w, c in
                                sorted(r["word_freq"].items(), key=lambda x: -x[1])[:12])
    return r


def detect_content_type(url: str) -> str:
    u = url.lower()
    if re.search(r"/(blog|article|post|مقال|مدونة)", u): return "📝 مقال"
    if re.search(r"/(news|أخبار)", u):                  return "📰 أخبار"
    if re.search(r"/(product|shop|متجر|منتج)", u):      return "🛒 منتج"
    if re.search(r"/(category|cat|تصنيف|قسم)", u):      return "🗂️ تصنيف"
    if re.search(r"/(video|فيديو)", u):                  return "🎬 فيديو"
    if len(urlparse(u).path.strip("/").split("/")) <= 1:return "🏠 رئيسية"
    return "📄 عامة"


def suggest_schema_type(url: str) -> str:
    u = url.lower()
    if re.search(r"/(blog|article|post|مقال)", u): return "Article / BlogPosting"
    if re.search(r"/(news|أخبار)", u):             return "NewsArticle"
    if re.search(r"/(product|shop|منتج)", u):      return "Product"
    if "/faq" in u:     return "FAQPage"
    if "/recipe" in u:  return "Recipe"
    if "/event" in u:   return "Event"
    if "/about" in u:   return "Organization"
    if "/contact" in u: return "LocalBusiness"
    if re.search(r"/(how-to|tutorial)", u): return "HowTo"
    if "/video" in u: return "VideoObject"
    return "WebPage"


def get_suggested_fix(issue: str) -> str:
    for key, fix in SCHEMA_FIX_MAP.items():
        if key in issue:
            return fix
    return "راجع https://schema.org للتفاصيل"


# ─── FULL PAGE ANALYSIS ─────────────────────────────────────────

def analyze_page(url: str, cfg: dict) -> dict:
    r = dict(
        url=url, content_type=detect_content_type(url), error=None,
        has_schema=False, schema_types=[], schema_blocks=[],
        has_json_ld=False, has_microdata=False, has_rdfa=False,
        has_duplicate=False, issues=[],
        title="", meta_description="", meta_keywords="",
        focus_keyword="", h1=[], h2=[], h3=[],
        word_freq={}, top_words="",
    )
    try:
        html = fetch_html(url)
        if not html:
            r["error"] = "فشل التحميل"
            return r
        r.update(parse_schema(html))
        r.update(parse_keywords(html, cfg))
    except Exception as e:
        r["error"] = str(e)[:120]
    return r


# ═══════════════════════════════════════════════════════════════
#  🎨 STREAMLIT UI
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="🚀 SEO Suite Pro — Ismail El Asiouty",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Tajawal', 'Segoe UI', sans-serif;
}
.main { background: #f0f2f6; }

/* Cards */
.kpi-grid { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:16px; }
.kpi-card {
    flex:1; min-width:130px; background:white;
    border-radius:14px; padding:16px 12px; text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,.08);
    border-top: 4px solid;
    transition: transform .2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow:0 6px 20px rgba(0,0,0,.13); }
.kpi-label { font-size:12px; color:#666; margin-bottom:6px; font-weight:600; letter-spacing:.3px; }
.kpi-value { font-size:34px; font-weight:900; line-height:1.1; }
.kpi-sub   { font-size:11px; color:#999; margin-top:4px; }

/* Section headers */
.section-header {
    display:flex; align-items:center; gap:10px;
    background:linear-gradient(135deg, #1a1100 0%, #3d2b00 50%, #1a1100 100%);
    color:#FFD700; padding:12px 20px; border-radius:12px;
    margin:20px 0 14px; font-size:16px; font-weight:700; letter-spacing:.5px;
    border: 1px solid #FFD700;
}

/* Brand card */
.brand-card {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a00 50%, #0a0a0a 100%);
    border: 2px solid #FFD700;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    color: white;
    text-align: center;
    box-shadow: 0 0 30px rgba(255,215,0,0.15);
}
.brand-name {
    font-size: 28px;
    font-weight: 900;
    color: #FFD700;
    margin-bottom: 6px;
    text-shadow: 0 0 20px rgba(255,215,0,0.4);
}
.brand-title {
    font-size: 14px;
    color: #ccb84a;
    margin-bottom: 16px;
    line-height: 1.6;
}
.brand-links {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 12px;
}
.brand-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,215,0,0.12);
    border: 1px solid #FFD700;
    color: #FFD700 !important;
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    transition: all .2s;
}
.brand-link:hover {
    background: #FFD700;
    color: #000 !important;
}

/* Status badges */
.badge {
    display:inline-block; padding:3px 10px; border-radius:20px;
    font-size:12px; font-weight:700;
}
.badge-red    { background:#fce8e6; color:#c62828; }
.badge-yellow { background:#fef9c3; color:#e37400; }
.badge-green  { background:#e6f4ea; color:#137333; }
.badge-gray   { background:#f5f5f5; color:#757575; }
.badge-purple { background:#f3e5f5; color:#7b1fa2; }
.badge-blue   { background:#e8f0fe; color:#1a73e8; }

/* Progress bar */
.stProgress > div > div > div > div { border-radius: 8px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap:4px; background:#e8ecf0; padding:6px; border-radius:12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius:9px; padding:8px 18px; font-weight:600; font-size:14px;
}
.stTabs [aria-selected="true"] {
    background:white !important; box-shadow:0 2px 8px rgba(0,0,0,.12);
}

/* Tables */
.stDataFrame { border-radius:10px; overflow:hidden; }
[data-testid="stDataFrameResizable"] { border-radius:10px; }

/* Sidebar */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #1a1100 100%); }
section[data-testid="stSidebar"] .block-container { padding-top:1rem; }
section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #FFD700 !important; }
section[data-testid="stSidebar"] .stSlider label { color:#b0b0b0 !important; }
section[data-testid="stSidebar"] hr { border-color:#3d2b00 !important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ────────────────────────────────────────────────────

def kpi_card(label: str, value, color: str, sub: str = "", emoji: str = "") -> str:
    return f"""
    <div class="kpi-card" style="border-color:{color}">
        <div class="kpi-label">{emoji} {label}</div>
        <div class="kpi-value" style="color:{color}">{value}</div>
        {'<div class="kpi-sub">'+sub+'</div>' if sub else ''}
    </div>"""


def kpi_row(cards: list) -> None:
    st.markdown('<div class="kpi-grid">' +
                "".join(kpi_card(*c) for c in cards) +
                "</div>", unsafe_allow_html=True)


def section_header(icon: str, title: str) -> None:
    st.markdown(f'<div class="section-header"><span>{icon}</span><span>{title}</span></div>',
                unsafe_allow_html=True)


def make_donut(labels, values, colors, title="") -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker_colors=colors,
        hole=0.55,
        textinfo="label+percent",
        textfont_size=12,
        hovertemplate="%{label}: %{value} (<b>%{percent}</b>)<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font_size=14, x=0.5),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
        margin=dict(t=40, b=20, l=10, r=10),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def make_hbar(df: pd.DataFrame, x: str, y: str, color: str, title: str) -> go.Figure:
    df_s = df.sort_values(x).tail(20)
    fig = px.bar(df_s, x=x, y=y, orientation="h",
                 color_discrete_sequence=[color],
                 title=title, text=x)
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=max(280, len(df_s) * 28 + 80),
        margin=dict(t=40, b=20, l=10, r=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_showgrid=True, yaxis_showgrid=False,
        yaxis_title="", xaxis_title="",
    )
    return fig


def style_status_df(df: pd.DataFrame, status_col: str) -> pd.DataFrame.style:
    def row_color(row):
        v = str(row.get(status_col, ""))
        if "🔴" in v or "❌" in v:  return ["background-color:#fce8e6"] * len(row)
        if "🟡" in v or "⚠️" in v:  return ["background-color:#fef9c3"] * len(row)
        if "🟢" in v or "✅" in v:  return ["background-color:#e6f4ea"] * len(row)
        if "🔁" in v:               return ["background-color:#f3e5f5"] * len(row)
        return [""] * len(row)
    return df.style.apply(row_color, axis=1)


def download_buttons(df: pd.DataFrame, filename: str, label: str = "📥 تحميل النتائج") -> None:
    """Render CSV download + Google Sheets instructions."""
    if df is None or df.empty:
        return
    import base64
    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    b64 = base64.b64encode(csv_bytes).decode()
    st.markdown(
        f'''<div style="background:linear-gradient(135deg,#0a0a0a,#1a1100);border:1px solid #FFD700;border-radius:12px;padding:16px 20px;margin:14px 0;">
<div style="color:#FFD700;font-size:13px;font-weight:700;margin-bottom:12px;">📥 تحميل / Export — {label}</div>
<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
<a href="data:text/csv;charset=utf-8-sig;base64,{b64}" download="{filename}.csv" style="display:inline-flex;align-items:center;gap:8px;background:#1a1100;border:1.5px solid #FFD700;color:#FFD700;padding:9px 20px;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none;">⬇️ تحميل CSV</a>
<a href="https://docs.google.com/spreadsheets/d/new" target="_blank" style="display:inline-flex;align-items:center;gap:8px;background:#0f9d58;border:1.5px solid #0f9d58;color:white;padding:9px 20px;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none;">📊 فتح Google Sheets جديد</a>
<span style="color:#888;font-size:12px;">← حمّل الـ CSV ثم في Sheets: <strong style="color:#ccb84a">File ← Import ← Upload</strong></span>
</div></div>''',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════════
#  🗂️ SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 5px">
        <div style="font-size:22px; font-weight:900; color:#FFD700; text-shadow:0 0 10px rgba(255,215,0,0.4)">
            🚀 SEO Suite Pro
        </div>
        <div style="font-size:11px; color:#ccb84a; margin-top:4px">
            by <strong style="color:#FFD700">Ismail El Asiouty</strong>
        </div>
    </div>""",
        unsafe_allow_html=True
    )
    st.markdown("---")

    site_url_input = st.text_input(
        "🌐 رابط الموقع",
        placeholder="https://example.com",
        help="اكتب رابط الموقع بدون / في النهاية"
    )
    st.markdown("---")
    st.markdown("**⚙️ إعدادات التحليل**")
    max_pages   = st.slider("📄 أقصى صفحات",    10, 300, DEFAULT_CFG["MAX_PAGES"], 10)
    old_months  = st.slider("🔴 أقدم من (شهر)", 3,  24,  DEFAULT_CFG["OLD_MONTHS"])
    warn_months = st.slider("🟡 مراجعة (شهر)",  1,  12,  DEFAULT_CFG["WARN_MONTHS"])

    cfg = dict(DEFAULT_CFG, MAX_PAGES=max_pages, OLD_MONTHS=old_months, WARN_MONTHS=warn_months)
    st.markdown("---")

    run_all      = st.button("🔥 شغّل الـ 3 أدوات", type="primary", use_container_width=True)
    col_s, col_sc, col_k = st.columns(3)
    run_sitemap  = col_s.button("🗺️",  help="Sitemap فقط",  use_container_width=True)
    run_schema   = col_sc.button("🔍", help="Schema فقط",   use_container_width=True)
    run_keywords = col_k.button("🔑",  help="Keywords فقط", use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ مسح النتائج", use_container_width=True):
        for k in ["sitemap_data", "page_results", "global_word_freq", "analyzed_url"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#ccb84a; text-align:center; line-height:1.8">
    🚀 SEO Suite Pro v2.0<br>
    <span style="color:#FFD700; font-weight:700">Ismail El Asiouty</span><br>
    SEO Specialist | Python & AI Tools<br>
    <a href="https://www.linkedin.com/in/ismailelasiouty/" target="_blank"
       style="color:#FFD700; text-decoration:none">🔗 LinkedIn</a> &nbsp;|&nbsp;
    <a href="https://wa.me/201014672352" target="_blank"
       style="color:#FFD700; text-decoration:none">💬 WhatsApp</a>
    </div>""",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
#  🔄 RUN ANALYSIS
# ═══════════════════════════════════════════════════════════════

def normalize_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url
    return url


def run_analysis(site_url: str, cfg: dict,
                 do_sitemap=True, do_schema=True, do_keywords=True):
    """Core analysis runner with progress UI"""
    url = normalize_url(site_url)
    errors = []

    with st.status("🔍 جاري التحليل...", expanded=True) as status:
        # ── Step 1: Sitemap ──────────────────────────────────────
        st.write("🗺️ بدور على الـ Sitemap...")
        sitemap_urls = find_sitemap_urls(url)
        if not sitemap_urls:
            st.error("❌ مش لاقي Sitemap — تأكد من /sitemap.xml أو robots.txt")
            status.update(label="❌ فشل التحليل", state="error")
            return

        all_pages = []
        for sm_url in sitemap_urls:
            all_pages.extend(parse_sitemap(sm_url))

        # deduplicate
        seen = set()
        unique_pages = []
        for p in all_pages:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique_pages.append(p)

        if not unique_pages:
            st.error("⚠️ الـ Sitemap فاضي!")
            status.update(label="❌ فشل التحليل", state="error")
            return

        if do_sitemap:
            sitemap_data = categorize_sitemap(unique_pages, cfg)
            st.session_state["sitemap_data"] = sitemap_data

        # ── Step 2: Page analysis ────────────────────────────────
        if do_schema or do_keywords:
            pages_to_fetch = list(dict.fromkeys(p["url"] for p in unique_pages))[:cfg["MAX_PAGES"]]
            n = len(pages_to_fetch)
            st.write(f"⚙️ بحلل {n} صفحة (Schema + Keywords)...")
            progress_bar = st.progress(0, text="جاري التحليل...")
            page_results = []
            global_word_freq: dict[str, int] = {}

            for i, page_url in enumerate(pages_to_fetch):
                progress_bar.progress((i + 1) / n,
                    text=f"صفحة {i+1}/{n} — {page_url[-60:]}")
                r = analyze_page(page_url, cfg)
                page_results.append(r)
                for w, c in r["word_freq"].items():
                    global_word_freq[w] = global_word_freq.get(w, 0) + c

            st.session_state["page_results"] = page_results
            st.session_state["global_word_freq"] = global_word_freq

        st.session_state["analyzed_url"] = url
        status.update(label="✅ اتحلل بنجاح!", state="complete", expanded=False)


# Trigger analysis
if site_url_input:
    if run_all:
        run_analysis(site_url_input, cfg, True, True, True)
    elif run_sitemap:
        run_analysis(site_url_input, cfg, True, False, False)
    elif run_schema:
        run_analysis(site_url_input, cfg, True, True, False)
    elif run_keywords:
        run_analysis(site_url_input, cfg, True, False, True)


# ═══════════════════════════════════════════════════════════════
#  📊 TABS
# ═══════════════════════════════════════════════════════════════

tab_dash, tab_sitemap, tab_schema, tab_kw, tab_contact = st.tabs([
    "🏠 Master Dashboard",
    "🗺️ Sitemap Analyzer",
    "🔍 Schema Checker",
    "🔑 Keyword Extractor",
    "👤 التواصل",
])

# ── Fetch session data ───────────────────────────────────────────
sitemap_data     = st.session_state.get("sitemap_data")
page_results     = st.session_state.get("page_results", [])
global_word_freq = st.session_state.get("global_word_freq", {})
analyzed_url     = st.session_state.get("analyzed_url", "")


# ═══════════════════════════════════════════════════════════════
#  🏠 TAB 1: MASTER DASHBOARD
# ═══════════════════════════════════════════════════════════════
with tab_dash:
    if not sitemap_data and not page_results:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px">
            <div style="font-size:72px; margin-bottom:16px">🚀</div>
            <h2 style="color:#FFD700; font-size:30px; font-weight:900;
                       text-shadow:0 0 20px rgba(255,215,0,0.3)">SEO Suite Pro</h2>
            <div style="color:#888; font-size:13px; margin-bottom:6px">
                by <strong style="color:#FFD700">Ismail El Asiouty</strong> — SEO Specialist | Python & AI Tools
            </div>
            <p style="color:#666; font-size:15px; max-width:520px; margin:16px auto 28px">
                أدخل رابط الموقع في الـ Sidebar واضغط <strong>شغّل الـ 3 أدوات</strong>
                للحصول على تقرير SEO كامل
            </p>
            <div style="display:flex; justify-content:center; gap:24px; flex-wrap:wrap;
                        color:#ccb84a; font-size:13px; margin-bottom:32px">
                <span>🗺️ Sitemap Analyzer</span>
                <span>🔍 Schema Checker</span>
                <span>🔑 Keyword Extractor</span>
                <span>📥 Export CSV</span>
            </div>
            <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                <a href="https://www.linkedin.com/in/ismailelasiouty/" target="_blank"
                   style="display:inline-flex;align-items:center;gap:8px;
                          background:rgba(255,215,0,0.1);border:1px solid #FFD700;
                          color:#FFD700;padding:9px 20px;border-radius:25px;
                          font-size:12px;font-weight:700;text-decoration:none;">
                    🔗 LinkedIn
                </a>
                <a href="https://wa.me/201014672352" target="_blank"
                   style="display:inline-flex;align-items:center;gap:8px;
                          background:rgba(37,211,102,0.1);border:1px solid #25D366;
                          color:#25D366;padding:9px 20px;border-radius:25px;
                          font-size:12px;font-weight:700;text-decoration:none;">
                    💬 WhatsApp
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Hero header
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460,#16213e);
                    border-radius:16px; padding:24px 32px; margin-bottom:20px; color:white">
            <div style="font-size:13px; opacity:.7; margin-bottom:4px">🚀 SEO Suite Pro — Master Dashboard</div>
            <h1 style="margin:0; font-size:24px; font-weight:900">{analyzed_url or "تحليل SEO"}</h1>
            <div style="font-size:12px; opacity:.6; margin-top:6px">
                📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp;
                🗺️ {len(sitemap_data['all']) if sitemap_data else 0} صفحة في الـ Sitemap &nbsp;|&nbsp;
                ✅ {len(page_results)} صفحة حُللت
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Sitemap Section ──
        if sitemap_data:
            section_header("🗺️", "SITEMAP — حالة المحتوى")
            sm = sitemap_data
            total = len(sm["all"])
            pct_old   = round(len(sm["old"])/total*100)  if total else 0
            pct_fresh = round(len(sm["fresh"])/total*100) if total else 0
            kpi_row([
                ("الإجمالي",       total,              "#1565c0", f"sitemap files", "📦"),
                ("تحديث عاجل",    len(sm["old"]),     "#c62828", f"أقدم من {cfg['OLD_MONTHS']} شهر", "🔴"),
                ("تحتاج مراجعة",  len(sm["warn"]),    "#e37400", f"{cfg['WARN_MONTHS']}–{cfg['OLD_MONTHS']} شهر", "🟡"),
                ("حديثة",         len(sm["fresh"]),   "#137333", f"{pct_fresh}% من الكل", "🟢"),
                ("بدون تاريخ",    len(sm["no_date"]), "#757575", "no lastmod", "⚪"),
            ])

        # ── Schema Section ──
        if page_results:
            section_header("🔍", "SCHEMA — تغطية الـ Schema Markup")
            with_schema = [r for r in page_results if r["has_schema"]]
            no_schema   = [r for r in page_results if not r["has_schema"] and not r["error"]]
            with_issues = [r for r in page_results if r["issues"]]
            with_dupes  = [r for r in page_results if r["has_duplicate"]]
            n_pages = len(page_results)
            coverage = round(len(with_schema)/n_pages*100) if n_pages else 0
            kpi_row([
                ("فيها Schema",   len(with_schema), "#137333", f"{coverage}% تغطية", "✅"),
                ("ملهاش Schema",  len(no_schema),   "#c62828", "تحتاج إضافة", "❌"),
                ("فيها مشاكل",    len(with_issues),  "#e37400", "issues", "⚠️"),
                ("Duplicate",     len(with_dupes),   "#7b1fa2", "نفس الصفحة", "🔁"),
                ("نسبة التغطية",  f"{coverage}%",   "#1a73e8", "schema coverage", "📊"),
            ])

            # ── Keywords Section ──
            section_header("🔑", "KEYWORDS — تحليل المحتوى والكلمات المفتاحية")
            no_title   = [r for r in page_results if not r["title"]]
            no_h1      = [r for r in page_results if not r["h1"]]
            with_focus = [r for r in page_results if r["focus_keyword"]]
            kpi_row([
                ("كلمات فريدة",   len(global_word_freq), "#1b5e20", "unique keywords", "🔑"),
                ("Focus KW",      len(with_focus),        "#1a73e8", "Yoast/RankMath", "🎯"),
                ("بدون Title",    len(no_title),          "#c62828", "SEO issue", "❌"),
                ("بدون H1",       len(no_h1),             "#ad1457", "structure issue", "❌"),
                ("صفحات حُللت",   len(page_results),      "#4a4a4a", "analyzed", "📄"),
            ])

        # ── Charts Row ──
        if sitemap_data and page_results:
            st.markdown("---")
            col_a, col_b, col_c = st.columns([1.2, 1.2, 1.6])

            with col_a:
                sm = sitemap_data
                fig_sm = make_donut(
                    ["🔴 تحديث عاجل", "🟡 مراجعة", "🟢 حديثة", "⚪ بدون تاريخ"],
                    [len(sm["old"]), len(sm["warn"]), len(sm["fresh"]), len(sm["no_date"])],
                    ["#ef5350", "#ffa726", "#66bb6a", "#bdbdbd"],
                    "🗺️ توزيع الـ Sitemap"
                )
                st.plotly_chart(fig_sm, use_container_width=True)

            with col_b:
                schema_types_count = Counter()
                for r in page_results:
                    for t in r["schema_types"]:
                        schema_types_count[t] += 1
                if schema_types_count:
                    top_types = schema_types_count.most_common(8)
                    fig_schema = px.bar(
                        x=[t[1] for t in top_types],
                        y=[t[0] for t in top_types],
                        orientation="h",
                        color_discrete_sequence=["#e91e63"],
                        title="🔍 أنواع Schema",
                        text=[t[1] for t in top_types],
                    )
                    fig_schema.update_layout(
                        height=280, margin=dict(t=40,b=20,l=10,r=40),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis_title="", xaxis_title="", xaxis_showgrid=True,
                    )
                    fig_schema.update_traces(textposition="outside")
                    st.plotly_chart(fig_schema, use_container_width=True)

            with col_c:
                if global_word_freq:
                    top_kw = sorted(global_word_freq.items(), key=lambda x: -x[1])[:15]
                    df_kw  = pd.DataFrame(top_kw, columns=["كلمة", "تكرار"])
                    fig_kw = make_hbar(df_kw, "تكرار", "كلمة", "#1565c0", "🔑 أكثر الكلمات المفتاحية")
                    st.plotly_chart(fig_kw, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  🗺️ TAB 2: SITEMAP ANALYZER
# ═══════════════════════════════════════════════════════════════
with tab_sitemap:
    if not sitemap_data:
        st.info("🗺️ شغّل الـ Sitemap Analyzer من الـ Sidebar أولاً")
    else:
        sm = sitemap_data
        total = len(sm["all"])

        # KPIs
        section_header("🗺️", f"Sitemap Analyzer — {analyzed_url}")
        kpi_row([
            ("إجمالي الصفحات", total,              "#1565c0", "total pages", "📦"),
            ("تحديث عاجل",    len(sm["old"]),     "#c62828", f"+{cfg['OLD_MONTHS']} شهر", "🔴"),
            ("تحتاج مراجعة",  len(sm["warn"]),    "#e37400", f"{cfg['WARN_MONTHS']}-{cfg['OLD_MONTHS']} شهر","🟡"),
            ("حديثة",         len(sm["fresh"]),   "#137333", f"-{cfg['WARN_MONTHS']} شهر", "🟢"),
            ("بدون تاريخ",    len(sm["no_date"]), "#757575", "no lastmod", "⚪"),
        ])

        # Charts
        col1, col2 = st.columns([1, 2])
        with col1:
            fig = make_donut(
                ["🔴 تحديث عاجل","🟡 مراجعة","🟢 حديثة","⚪ بدون تاريخ"],
                [len(sm["old"]),len(sm["warn"]),len(sm["fresh"]),len(sm["no_date"])],
                ["#ef5350","#ffa726","#66bb6a","#bdbdbd"],
                "توزيع حالة المحتوى"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Age distribution
            mo_vals = [p["months_ago"] for p in sm["all"] if p["months_ago"]]
            if mo_vals:
                bins = [0, 3, 6, 12, 24, 999]
                labels_b = ["< 3 شهور","3-6 شهور","6-12 شهر","12-24 شهر","+24 شهر"]
                counts = [0]*5
                for v in mo_vals:
                    for i in range(len(bins)-1):
                        if bins[i] <= v < bins[i+1]:
                            counts[i] += 1; break
                colors_b = ["#66bb6a","#aed581","#ffa726","#ef5350","#b71c1c"]
                fig_age = px.bar(x=labels_b, y=counts, color=labels_b,
                                 color_discrete_sequence=colors_b,
                                 title="📅 توزيع عمر المحتوى",
                                 text=counts)
                fig_age.update_traces(textposition="outside")
                fig_age.update_layout(
                    height=280, showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=40,b=20,l=10,r=10),
                    yaxis_title="عدد الصفحات", xaxis_title=""
                )
                st.plotly_chart(fig_age, use_container_width=True)

        # Full table
        st.markdown("---")
        sub1, sub2, sub3 = st.tabs(["📋 كل الصفحات", "🔴 تحديث عاجل", "🟡 تحتاج مراجعة"])

        def sitemap_df(pages_list):
            rows = []
            for i, p in enumerate(pages_list, 1):
                mo = p["months_ago"]
                if not mo:      status = "⚪ بدون تاريخ"
                elif mo >= cfg["OLD_MONTHS"]:  status = "🔴 تحديث عاجل"
                elif mo >= cfg["WARN_MONTHS"]: status = "🟡 مراجعة"
                else:           status = "🟢 حديث"
                rows.append({
                    "#": i, "🔗 الرابط": p["url"],
                    "📅 آخر تحديث": p["lastmod"] or "—",
                    "⏳ شهور": f"{mo:.0f}" if mo else "—",
                    "🚦 الحالة": status,
                    "🔄 تكرار": p["changefreq"] or "—",
                    "⭐ أولوية": p["priority"] or "—",
                })
            return pd.DataFrame(rows)

        with sub1:
            df_all = sitemap_df(sm["all"])
            st.dataframe(style_status_df(df_all, "🚦 الحالة"),
                         use_container_width=True, height=500,
                         column_config={"🔗 الرابط": st.column_config.LinkColumn()})
            download_buttons(df_all, "sitemap_full_report", "كل صفحات الـ Sitemap")

        with sub2:
            if sm["old"]:
                df_old = sitemap_df(sm["old"])
                st.dataframe(style_status_df(df_old, "🚦 الحالة"),
                             use_container_width=True, height=400,
                             column_config={"🔗 الرابط": st.column_config.LinkColumn()})
                download_buttons(df_old, "sitemap_urgent_update", "صفحات تحتاج تحديث عاجل")
            else:
                st.success("🎉 كل المحتوى حديث! مفيش صفحات تحتاج تحديث عاجل.")

        with sub3:
            if sm["warn"]:
                df_warn = sitemap_df(sm["warn"])
                st.dataframe(style_status_df(df_warn, "🚦 الحالة"),
                             use_container_width=True, height=400,
                             column_config={"🔗 الرابط": st.column_config.LinkColumn()})
            else:
                st.success("🎉 مفيش صفحات في نطاق المراجعة!")


# ═══════════════════════════════════════════════════════════════
#  🔍 TAB 3: SCHEMA CHECKER
# ═══════════════════════════════════════════════════════════════
with tab_schema:
    if not page_results:
        st.info("🔍 شغّل الـ Schema Checker من الـ Sidebar أولاً")
    else:
        with_schema  = [r for r in page_results if r["has_schema"]]
        no_schema    = [r for r in page_results if not r["has_schema"] and not r["error"]]
        with_issues  = [r for r in page_results if r["issues"]]
        with_dupes   = [r for r in page_results if r["has_duplicate"]]
        with_errors  = [r for r in page_results if r["error"]]
        n = len(page_results)
        coverage = round(len(with_schema)/n*100) if n else 0

        section_header("🔍", f"Schema Checker — {analyzed_url}")
        kpi_row([
            ("فيها Schema",   len(with_schema), "#137333", f"{coverage}% تغطية", "✅"),
            ("ملهاش Schema",  len(no_schema),   "#c62828", "need markup", "❌"),
            ("فيها مشاكل",    len(with_issues), "#e37400", "issues found", "⚠️"),
            ("Duplicate",     len(with_dupes),  "#7b1fa2", "same page", "🔁"),
            ("نسبة التغطية",  f"{coverage}%",  "#1a73e8", "coverage rate", "📊"),
        ])

        # Charts
        col_a, col_b = st.columns(2)

        with col_a:
            schema_types_cnt = Counter()
            for r in page_results:
                for t in r["schema_types"]:
                    schema_types_cnt[t] += 1
            if schema_types_cnt:
                top_types = schema_types_cnt.most_common(10)
                df_st = pd.DataFrame(top_types, columns=["نوع Schema","عدد الصفحات"])
                fig_st = make_hbar(df_st, "عدد الصفحات", "نوع Schema", "#e91e63",
                                   "📋 أنواع Schema المستخدمة")
                st.plotly_chart(fig_st, use_container_width=True)

        with col_b:
            pie_labels = ["✅ فيها Schema","❌ ملهاش","⚠️ مشاكل","🔁 Duplicate"]
            pie_vals = [len(with_schema)-len(with_issues), len(no_schema), len(with_issues), len(with_dupes)]
            pie_vals = [max(0,v) for v in pie_vals]
            fig_cov = make_donut(pie_labels, pie_vals,
                                 ["#66bb6a","#ef5350","#ffa726","#ba68c8"],
                                 "📊 Schema Coverage")
            st.plotly_chart(fig_cov, use_container_width=True)

        # Sub-tabs
        st.markdown("---")
        s1, s2, s3, s4 = st.tabs([
            f"⚠️ المشاكل ({len(with_issues)})",
            f"❌ ملهاش Schema ({len(no_schema)})",
            f"🔁 Duplicates ({len(with_dupes)})",
            "📋 كل الصفحات",
        ])

        with s1:
            if with_issues:
                rows = []
                for i, r in enumerate(with_issues, 1):
                    for j, issue in enumerate(r["issues"]):
                        rows.append({
                            "#":       i if j == 0 else "",
                            "🔗 الرابط": r["url"] if j == 0 else "",
                            "⚠️ المشكلة": issue,
                            "🔧 الحل المقترح": get_suggested_fix(issue),
                            "🔴 خطورة": "عالية" if "JSON" in issue or "ملهاش أي" in issue else "متوسطة",
                        })
                df_issues = pd.DataFrame(rows)
                st.dataframe(style_status_df(df_issues, "⚠️ المشكلة"),
                             use_container_width=True, height=450,
                             column_config={"🔗 الرابط": st.column_config.LinkColumn()})
                download_buttons(df_issues, "schema_issues_report", "مشاكل الـ Schema")
            else:
                st.success("🎉 مفيش مشاكل! كل الـ Schema سليم 100%")

        with s2:
            if no_schema:
                rows = [{"#":i+1,"🔗 الرابط":r["url"],"💡 Schema المقترحة":suggest_schema_type(r["url"])}
                        for i, r in enumerate(no_schema)]
                df_ns = pd.DataFrame(rows)
                st.dataframe(df_ns, use_container_width=True, height=400,
                             column_config={"🔗 الرابط": st.column_config.LinkColumn()})
            else:
                st.success("🎉 كل الصفحات عندها Schema!")

        with s3:
            if with_dupes:
                rows = []
                for i, r in enumerate(with_dupes, 1):
                    tc = Counter(b["type"] for b in r["schema_blocks"])
                    for j, (tn, cnt) in enumerate([(t,c) for t,c in tc.items() if c > 1]):
                        rows.append({
                            "#": i if j==0 else "",
                            "🔗 الرابط": r["url"] if j==0 else "",
                            "🔁 النوع المكرر": tn,
                            "عدد المرات": f"{cnt} مرات",
                        })
                df_dup = pd.DataFrame(rows)
                st.dataframe(df_dup, use_container_width=True, height=380,
                             column_config={"🔗 الرابط": st.column_config.LinkColumn()})
            else:
                st.success("🎉 مفيش Duplicates!")

        with s4:
            rows = []
            for i, r in enumerate(page_results, 1):
                schema_status = "✅ سليم" if r["has_schema"] and not r["issues"] else \
                                "⚠️ مشاكل" if r["has_schema"] else \
                                "❌ ملهاش" if not r["error"] else "⛔ خطأ"
                rows.append({
                    "#": i,
                    "🔗 الرابط": r["url"],
                    "🚦 الحالة": schema_status,
                    "📋 الأنواع": " | ".join(r["schema_types"]) or "—",
                    "🔁 Dup": "نعم" if r["has_duplicate"] else "—",
                    "⚠️ مشاكل": len(r["issues"]),
                    "📝 JSON-LD": "✅" if r["has_json_ld"] else "—",
                    "🏷️ Micro": "✅" if r["has_microdata"] else "—",
                })
            df_all = pd.DataFrame(rows)
            st.dataframe(style_status_df(df_all, "🚦 الحالة"),
                         use_container_width=True, height=500,
                         column_config={"🔗 الرابط": st.column_config.LinkColumn()})
            download_buttons(df_all, "schema_full_report", "تقرير Schema الكامل")


# ═══════════════════════════════════════════════════════════════
#  🔑 TAB 4: KEYWORD EXTRACTOR
# ═══════════════════════════════════════════════════════════════
with tab_kw:
    if not page_results:
        st.info("🔑 شغّل الـ Keyword Extractor من الـ Sidebar أولاً")
    else:
        no_title   = [r for r in page_results if not r["title"]]
        no_desc    = [r for r in page_results if not r["meta_description"]]
        no_h1      = [r for r in page_results if not r["h1"]]
        with_focus = [r for r in page_results if r["focus_keyword"]]

        section_header("🔑", f"Keyword Extractor — {analyzed_url}")
        kpi_row([
            ("كلمات فريدة",   len(global_word_freq), "#1b5e20", "unique keywords", "🔑"),
            ("Focus KW",      len(with_focus),        "#1a73e8", "Yoast/RankMath", "🎯"),
            ("بدون Title",    len(no_title),          "#c62828", "SEO issue", "❌"),
            ("بدون Description", len(no_desc),        "#c62828", "SEO issue", "❌"),
            ("بدون H1",       len(no_h1),             "#ad1457", "structure issue", "❌"),
        ])

        # Charts
        col_a, col_b = st.columns([1.8, 1.2])

        with col_a:
            if global_word_freq:
                top_kw = sorted(global_word_freq.items(), key=lambda x: -x[1])[:20]
                df_kw = pd.DataFrame(top_kw, columns=["كلمة", "تكرار"])
                fig_kw = make_hbar(df_kw, "تكرار", "كلمة", "#1565c0",
                                   f"🏆 أكثر {min(20,len(top_kw))} كلمة مفتاحية")
                st.plotly_chart(fig_kw, use_container_width=True)

        with col_b:
            ct_cnt = Counter(r["content_type"] for r in page_results)
            if ct_cnt:
                fig_ct = make_donut(
                    list(ct_cnt.keys()), list(ct_cnt.values()),
                    ["#1565c0","#e91e63","#f57c00","#2e7d32","#7b1fa2","#00838f"],
                    "📂 توزيع نوع المحتوى"
                )
                st.plotly_chart(fig_ct, use_container_width=True)

        # Sub-tabs
        st.markdown("---")
        k1, k2, k3, k4 = st.tabs([
            "🔑 Top Keywords",
            "📄 كل الصفحات",
            "📌 Headings",
            "🏷️ Meta Data",
        ])

        with k1:
            if global_word_freq:
                kw_page_cnt: dict[str,int] = {}
                kw_top_page: dict[str,str] = {}
                for r in page_results:
                    for w, c in r["word_freq"].items():
                        kw_page_cnt[w] = kw_page_cnt.get(w, 0) + 1
                        if w not in kw_top_page or c > r["word_freq"].get(w, 0):
                            kw_top_page[w] = r["url"]

                top = sorted(global_word_freq.items(), key=lambda x: -x[1])[:cfg["TOP_KEYWORDS"]]
                rows = []
                for i, (w, freq) in enumerate(top, 1):
                    strength = "🔥 قوي جداً" if freq >= 50 else "💪 قوي" if freq >= 20 else "ℹ️ عادي"
                    rows.append({
                        "#": i, "🔑 الكلمة": w,
                        "إجمالي التكرار": freq,
                        "عدد الصفحات": kw_page_cnt.get(w, 0),
                        "💪 القوة": strength,
                        "🔗 أهم صفحة": kw_top_page.get(w, ""),
                    })
                df_top = pd.DataFrame(rows)

                def color_strength(row):
                    if "🔥" in str(row.get("💪 القوة","")):
                        return ["background-color:#e6f4ea"]*len(row)
                    if "💪" in str(row.get("💪 القوة","")):
                        return ["background-color:#f8f9fa"]*len(row)
                    return [""]*len(row)

                st.dataframe(
                    df_top.style.apply(color_strength, axis=1),
                    use_container_width=True, height=500,
                    column_config={"🔗 أهم صفحة": st.column_config.LinkColumn()}
                )
                download_buttons(df_top, "top_keywords_report", "أهم الكلمات المفتاحية")

        with k2:
            rows = []
            for i, r in enumerate(page_results, 1):
                rows.append({
                    "#": i,
                    "🔗 الرابط": r["url"],
                    "📝 Title": r["title"] or "❌ بدون Title",
                    "🎯 Focus KW": r["focus_keyword"] or "—",
                    "H1": r["h1"][0] if r["h1"] else "❌ بدون H1",
                    "📂 النوع": r["content_type"],
                    "🔑 أكثر كلمات": r["top_words"][:100] or "—",
                })
            df_pages = pd.DataFrame(rows)
            st.dataframe(
                style_status_df(df_pages, "📝 Title"),
                use_container_width=True, height=500,
                column_config={"🔗 الرابط": st.column_config.LinkColumn()}
            )

        with k3:
            rows = []
            for i, r in enumerate(page_results, 1):
                rows.append({
                    "#": i,
                    "🔗 الرابط": r["url"],
                    "H1": " | ".join(r["h1"]) or "❌ بدون H1",
                    "H2 (أهم 3)": " | ".join(r["h2"][:3]) or "—",
                    "H3 (أهم 3)": " | ".join(r["h3"][:3]) or "—",
                    "عدد H2": len(r["h2"]),
                    "عدد H3": len(r["h3"]),
                })
            df_h = pd.DataFrame(rows)
            st.dataframe(
                style_status_df(df_h, "H1"),
                use_container_width=True, height=450,
                column_config={"🔗 الرابط": st.column_config.LinkColumn()}
            )

            # Top H2s
            st.markdown("---")
            st.markdown("#### 🏆 أكثر H2 تكراراً — الموضوعات المهمة")
            h2_freq: dict[str,int] = {}
            for r in page_results:
                for h in r["h2"]:
                    k = h.lower().strip()
                    h2_freq[k] = h2_freq.get(k, 0) + 1
            if h2_freq:
                top_h2 = sorted(h2_freq.items(), key=lambda x: -x[1])[:20]
                df_h2 = pd.DataFrame([{"H2 Heading": h, "التكرار": c,
                                        "الأهمية": "🔥 مهم جداً" if c>=5 else "⚠️ مهم" if c>=3 else "ℹ️ عادي"}
                                       for h, c in top_h2])
                st.dataframe(style_status_df(df_h2, "الأهمية"),
                             use_container_width=True, height=350)

        with k4:
            rows = []
            for i, r in enumerate(page_results, 1):
                title_len = len(r["title"])
                desc_len  = len(r["meta_description"])
                title_status = ("✅" if 30 <= title_len <= 60 else
                                "⚠️ طويل" if title_len > 60 else
                                "❌ بدون Title" if not r["title"] else "⚠️ قصير")
                desc_status  = ("✅" if 120 <= desc_len <= 160 else
                                "⚠️ طويل" if desc_len > 160 else
                                "❌ بدون Description" if not r["meta_description"] else "⚠️ قصير")
                rows.append({
                    "#": i,
                    "🔗 الرابط": r["url"],
                    "📝 Title": r["title"] or "❌",
                    "📏 Title طول": title_len,
                    "✅ Title": title_status,
                    "📋 Description": r["meta_description"][:80] or "❌",
                    "📏 Desc طول": desc_len,
                    "✅ Desc": desc_status,
                    "🎯 Focus KW": r["focus_keyword"] or "—",
                    "🏷️ Meta KW": r["meta_keywords"][:60] or "—",
                })
            df_meta = pd.DataFrame(rows)
            st.dataframe(
                style_status_df(df_meta, "✅ Title"),
                use_container_width=True, height=500,
                column_config={"🔗 الرابط": st.column_config.LinkColumn()}
            )

            # Meta health summary
            st.markdown("---")
            col_m1, col_m2, col_m3 = st.columns(3)
            title_ok  = sum(1 for r in page_results if 30 <= len(r["title"]) <= 60)
            desc_ok   = sum(1 for r in page_results if 120 <= len(r["meta_description"]) <= 160)
            focus_ok  = sum(1 for r in page_results if r["focus_keyword"])
            n = len(page_results)
            col_m1.metric("✅ Title بالطول الصح",  f"{title_ok}/{n}",
                          f"{round(title_ok/n*100) if n else 0}%")
            col_m2.metric("✅ Description بالطول الصح", f"{desc_ok}/{n}",
                          f"{round(desc_ok/n*100) if n else 0}%")
            col_m3.metric("🎯 فيها Focus Keyword", f"{focus_ok}/{n}",
                          f"{round(focus_ok/n*100) if n else 0}%")
            download_buttons(df_meta, "meta_data_report", "تقرير الـ Meta Data")


# ═══════════════════════════════════════════════════════════════
#  👤 TAB 5: CONTACT / ABOUT
# ═══════════════════════════════════════════════════════════════
with tab_contact:
    _contact_html = (
        "<div style='background:linear-gradient(135deg,#0a0a0a 0%,#1a1100 50%,#0a0a0a 100%);"
        "border:2px solid #FFD700;border-radius:20px;padding:40px;margin:20px auto;"
        "max-width:750px;box-shadow:0 0 40px rgba(255,215,0,0.15);text-align:center;'>"
        "<div style='font-size:60px;margin-bottom:16px'>&#128640;</div>"
        "<div style='font-size:32px;font-weight:900;color:#FFD700;"
        "text-shadow:0 0 20px rgba(255,215,0,0.5);margin-bottom:8px;'>Ismail El Asiouty</div>"
        "<div style='font-size:14px;color:#ccb84a;line-height:1.9;margin-bottom:28px;"
        "max-width:560px;margin-left:auto;margin-right:auto;'>"
        "SEO Specialist | User Experience Analysis<br>"
        "Building SEO Tools with Python &amp; AI | Content Optimization</div>"
        "<div style='display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;'>"
        "<a href='https://www.linkedin.com/in/ismailelasiouty/' target='_blank' "
        "style='display:inline-flex;align-items:center;gap:10px;"
        "background:rgba(255,215,0,0.1);border:1.5px solid #FFD700;"
        "color:#FFD700;padding:12px 24px;border-radius:30px;"
        "font-size:14px;font-weight:700;text-decoration:none;'>&#128279; LinkedIn Profile</a>"
        "<a href='https://wa.me/201014672352' target='_blank' "
        "style='display:inline-flex;align-items:center;gap:10px;"
        "background:rgba(37,211,102,0.1);border:1.5px solid #25D366;"
        "color:#25D366;padding:12px 24px;border-radius:30px;"
        "font-size:14px;font-weight:700;text-decoration:none;'>&#128172; WhatsApp: 01014672352</a>"
        "</div>"
        "<hr style='border-color:#3d2b00;margin:24px 0;'>"
        "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;"
        "text-align:center;margin-bottom:24px;'>"
        "<div style='background:rgba(255,215,0,0.06);border:1px solid #3d2b00;"
        "border-radius:12px;padding:16px;'>"
        "<div style='font-size:28px'>&#128269;</div>"
        "<div style='color:#FFD700;font-weight:700;font-size:13px;margin:6px 0 4px'>SEO Analysis</div>"
        "<div style='color:#888;font-size:12px'>Schema &#8226; Sitemap &#8226; Keywords</div></div>"
        "<div style='background:rgba(255,215,0,0.06);border:1px solid #3d2b00;"
        "border-radius:12px;padding:16px;'>"
        "<div style='font-size:28px'>&#128013;</div>"
        "<div style='color:#FFD700;font-weight:700;font-size:13px;margin:6px 0 4px'>Python &amp; AI Tools</div>"
        "<div style='color:#888;font-size:12px'>Automation &#8226; Streamlit &#8226; APIs</div></div>"
        "<div style='background:rgba(255,215,0,0.06);border:1px solid #3d2b00;"
        "border-radius:12px;padding:16px;'>"
        "<div style='font-size:28px'>&#9997;&#65039;</div>"
        "<div style='color:#FFD700;font-weight:700;font-size:13px;margin:6px 0 4px'>Content Optimization</div>"
        "<div style='color:#888;font-size:12px'>UX &#8226; Copy &#8226; Strategy</div></div>"
        "</div>"
        "<div style='color:#888;font-size:12px;margin-top:16px;'>"
        "&#128640; SEO Suite Pro v2.0 &#8212; Built with Python &amp; Streamlit</div>"
        "</div>"
    )
    st.html(_contact_html)
