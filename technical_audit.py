"""
╔══════════════════════════════════════════════════════╗
║   🔧 Technical Audit Pro                            ║
║   robots.txt • 404s • Page Size • JS • Server       ║
╚══════════════════════════════════════════════════════╝
"""

import re
import time
import requests
import pandas as pd
import streamlit as st
from urllib.parse import urlparse, urljoin
from collections import defaultdict
from datetime import datetime
import base64

# ─── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="🔧 Technical Audit — Ismail El Asiouty",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', 'Segoe UI', sans-serif; }
.main { background: #f0f2f6; }

.section-header {
    display:flex; align-items:center; gap:10px;
    background:linear-gradient(135deg,#1a1100 0%,#3d2b00 50%,#1a1100 100%);
    color:#FFD700; padding:12px 20px; border-radius:12px;
    margin:20px 0 14px; font-size:16px; font-weight:700;
    border:1px solid #FFD700;
}
.metric-card {
    background:white; border-radius:12px; padding:16px;
    border-left:4px solid #FFD700;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    text-align:center;
}
.metric-val { font-size:28px; font-weight:900; color:#1a1100; }
.metric-lbl { font-size:12px; color:#666; margin-top:4px; }
.status-ok  { color:#0f9d58; font-weight:700; }
.status-err { color:#e53935; font-weight:700; }
.status-warn{ color:#f57c00; font-weight:700; }

section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0a0a0a 0%,#1a1100 100%);
}
section[data-testid="stSidebar"] * { color:#e0e0e0 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color:#FFD700 !important; }
section[data-testid="stSidebar"] hr  { border-color:#3d2b00 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)",
    "Accept": "text/html,application/xhtml+xml,*/*",
}
TIMEOUT = 10

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    return url.rstrip("/")

def safe_get(url: str, stream=False):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                         allow_redirects=True, stream=stream)
        return r
    except Exception as e:
        return None

def fmt_bytes(size: int) -> str:
    if size < 1024:        return f"{size} B"
    if size < 1024**2:     return f"{size/1024:.1f} KB"
    return f"{size/1024**2:.2f} MB"

def download_csv(df: pd.DataFrame, filename: str, label: str):
    if df is None or df.empty:
        return
    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    b64 = base64.b64encode(csv_bytes).decode()
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0a0a0a,#1a1100);'
        f'border:1px solid #FFD700;border-radius:10px;padding:14px 18px;margin:12px 0;">'
        f'<span style="color:#FFD700;font-weight:700;font-size:13px;">📥 {label}</span>&nbsp;&nbsp;'
        f'<a href="data:text/csv;charset=utf-8-sig;base64,{b64}" download="{filename}.csv" '
        f'style="background:#1a1100;border:1.5px solid #FFD700;color:#FFD700;'
        f'padding:7px 18px;border-radius:7px;font-size:12px;font-weight:700;text-decoration:none;">'
        f'⬇️ تحميل CSV</a>&nbsp;&nbsp;'
        f'<a href="https://docs.google.com/spreadsheets/d/new" target="_blank" '
        f'style="background:#0f9d58;color:white;padding:7px 18px;border-radius:7px;'
        f'font-size:12px;font-weight:700;text-decoration:none;">'
        f'📊 Google Sheets</a>'
        f'<span style="color:#888;font-size:11px;margin-right:10px;"> ← File → Import → Upload</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════
#  AUDIT FUNCTIONS
# ══════════════════════════════════════════════════════════════

def audit_robots(base_url: str) -> dict:
    """Fetch and parse robots.txt"""
    result = {
        "url": f"{base_url}/robots.txt",
        "exists": False,
        "status_code": None,
        "raw": "",
        "disallowed": [],
        "allowed": [],
        "sitemaps": [],
        "user_agents": [],
        "issues": [],
        "crawl_delay": None,
    }
    r = safe_get(f"{base_url}/robots.txt")
    if not r:
        result["issues"].append("❌ مش قادر يوصل لـ robots.txt")
        return result

    result["status_code"] = r.status_code
    if r.status_code != 200:
        result["issues"].append(f"❌ robots.txt رجع كود {r.status_code}")
        return result

    result["exists"] = True
    result["raw"] = r.text

    current_agent = "*"
    for line in r.text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()

        if key == "user-agent":
            current_agent = val
            if val not in result["user_agents"]:
                result["user_agents"].append(val)
        elif key == "disallow":
            if val:
                result["disallowed"].append({"agent": current_agent, "path": val})
        elif key == "allow":
            if val:
                result["allowed"].append({"agent": current_agent, "path": val})
        elif key == "sitemap":
            result["sitemaps"].append(val)
        elif key == "crawl-delay":
            result["crawl_delay"] = val

    # Issues detection
    if not result["sitemaps"]:
        result["issues"].append("⚠️ مفيش Sitemap مذكور في robots.txt")
    if any(d["path"] == "/" and d["agent"] == "*" for d in result["disallowed"]):
        result["issues"].append("🔴 خطر! Disallow: / للـ * — كل الموقع محجوب عن الـ bots!")
    if result["crawl_delay"] and int(result["crawl_delay"]) > 10:
        result["issues"].append(f"⚠️ Crawl-Delay = {result['crawl_delay']} ثانية — ده عالي جداً")

    return result


def audit_sitemap_status(base_url: str, max_pages: int, progress_bar) -> list:
    """Fetch sitemap URLs and check their HTTP status"""
    # Try common sitemap locations
    sitemap_urls_to_try = [
        f"{base_url}/sitemap.xml",
        f"{base_url}/sitemap_index.xml",
        f"{base_url}/sitemap-index.xml",
        f"{base_url}/sitemap/sitemap.xml",
    ]

    all_urls = []
    for sitemap_url in sitemap_urls_to_try:
        r = safe_get(sitemap_url)
        if r and r.status_code == 200 and "<url" in r.text:
            found = re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", r.text)
            # Handle sitemap index
            if "<sitemap>" in r.text and not found:
                sub_sitemaps = re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", r.text)
                for sub in sub_sitemaps[:5]:
                    sub_r = safe_get(sub)
                    if sub_r and sub_r.status_code == 200:
                        sub_urls = re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", sub_r.text)
                        all_urls.extend(sub_urls)
            else:
                all_urls.extend(found)
            break

    all_urls = list(dict.fromkeys(all_urls))[:max_pages]
    results = []

    for i, url in enumerate(all_urls):
        progress_bar.progress((i + 1) / max(len(all_urls), 1),
                              text=f"🔍 فاحص {i+1}/{len(all_urls)}: {url[:60]}...")
        start = time.time()
        r = safe_get(url)
        elapsed = round((time.time() - start) * 1000)  # ms

        if r is None:
            status = 0
            size = 0
            js_count = 0
            html_size = 0
            redirected = False
            final_url = url
        else:
            status = r.status_code
            size = len(r.content)
            html_size = len(r.text)
            js_count = len(re.findall(r'<script', r.text, re.I))
            redirected = r.url != url
            final_url = r.url

        status_icon = (
            "✅" if status == 200 else
            "🔁" if 300 <= status < 400 else
            "🔴" if status == 404 else
            "⛔" if status >= 500 else
            "❌" if status == 0 else "⚠️"
        )

        size_flag = "🔴 كبيرة جداً" if html_size > 200_000 else \
                    "🟡 كبيرة" if html_size > 100_000 else "✅ طبيعي"
        js_flag   = "🔴 كتير جداً" if js_count > 30 else \
                    "🟡 كتير" if js_count > 15 else "✅ طبيعي"
        speed_flag = "🔴 بطيء" if elapsed > 3000 else \
                     "🟡 متوسط" if elapsed > 1500 else "✅ سريع"

        results.append({
            "🔗 الرابط": url,
            "🚦 Status": f"{status_icon} {status}",
            "⏱️ وقت الاستجابة": f"{elapsed} ms — {speed_flag}",
            "📦 حجم الصفحة": f"{fmt_bytes(html_size)} — {size_flag}",
            "📜 عدد JS scripts": f"{js_count} — {js_flag}",
            "🔁 Redirect": "نعم ➜ " + final_url[:60] if redirected else "—",
        })
        time.sleep(0.05)

    return results


def audit_page_resources(base_url: str, sample_urls: list, progress_bar) -> list:
    """Deep audit: JS/CSS file sizes from sampled pages"""
    results = []
    for i, url in enumerate(sample_urls[:20]):
        progress_bar.progress((i + 1) / max(len(sample_urls[:20]), 1),
                              text=f"📦 تحليل ريسورسز: {url[:60]}...")
        r = safe_get(url)
        if not r or r.status_code != 200:
            continue

        js_files  = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', r.text, re.I)
        css_files = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\']', r.text, re.I)

        for js in js_files[:10]:
            abs_js = js if js.startswith("http") else urljoin(url, js)
            jr = safe_get(abs_js)
            size = len(jr.content) if jr else 0
            flag = "🔴 كبير جداً" if size > 500_000 else \
                   "🟡 كبير" if size > 200_000 else "✅ طبيعي"
            results.append({
                "📄 الصفحة": url,
                "📁 النوع": "JavaScript",
                "🔗 الملف": abs_js[:80],
                "📦 الحجم": fmt_bytes(size),
                "🚦 التقييم": flag,
            })

        for css in css_files[:5]:
            abs_css = css if css.startswith("http") else urljoin(url, css)
            cr = safe_get(abs_css)
            size = len(cr.content) if cr else 0
            flag = "🔴 كبير جداً" if size > 200_000 else \
                   "🟡 كبير" if size > 100_000 else "✅ طبيعي"
            results.append({
                "📄 الصفحة": url,
                "📁 النوع": "CSS",
                "🔗 الملف": abs_css[:80],
                "📦 الحجم": fmt_bytes(size),
                "🚦 التقييم": flag,
            })

    return results


def audit_server_headers(base_url: str) -> list:
    """Check server headers for common issues"""
    r = safe_get(base_url)
    if not r:
        return []

    checks = []
    h = r.headers

    checks.append({"🔍 الفحص": "HTTPS", "🚦 الحالة":
        "✅ نعم" if base_url.startswith("https") else "🔴 لأ — مفيش HTTPS!"})
    checks.append({"🔍 الفحص": "X-Frame-Options", "🚦 الحالة":
        "✅ موجود" if "x-frame-options" in {k.lower() for k in h} else "⚠️ مش موجود"})
    checks.append({"🔍 الفحص": "Content-Security-Policy", "🚦 الحالة":
        "✅ موجود" if "content-security-policy" in {k.lower() for k in h} else "⚠️ مش موجود"})
    checks.append({"🔍 الفحص": "X-Content-Type-Options", "🚦 الحالة":
        "✅ موجود" if "x-content-type-options" in {k.lower() for k in h} else "⚠️ مش موجود"})
    checks.append({"🔍 الفحص": "Cache-Control", "🚦 الحالة":
        f"✅ {h.get('cache-control', h.get('Cache-Control', ''))}" if any(
            k.lower() == 'cache-control' for k in h) else "⚠️ مش موجود"})
    checks.append({"🔍 الفحص": "Server", "🚦 الحالة":
        h.get("Server", h.get("server", "غير معروف"))})
    checks.append({"🔍 الفحص": "Response Time", "🚦 الحالة":
        f"{round(r.elapsed.total_seconds()*1000)} ms"})
    checks.append({"🔍 الفحص": "HTTP Status", "🚦 الحالة":
        f"{'✅' if r.status_code == 200 else '⚠️'} {r.status_code}"})

    return checks


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 5px">
        <div style="font-size:22px;font-weight:900;color:#FFD700;
                    text-shadow:0 0 10px rgba(255,215,0,0.4)">
            🔧 Technical Audit
        </div>
        <div style="font-size:11px;color:#ccb84a;margin-top:4px">
            by <strong style="color:#FFD700">Ismail El Asiouty</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    raw_url = st.text_input("🌐 رابط الموقع", placeholder="https://example.com")

    st.markdown("### ⚙️ الإعدادات")
    max_pages = st.number_input("📄 أقصى صفحات للفحص",
                                 min_value=10, max_value=5000,
                                 value=100, step=50)
    check_robots   = st.checkbox("🤖 فحص robots.txt",    value=True)
    check_status   = st.checkbox("🔴 فحص الـ Status Codes (404/5xx)", value=True)
    check_resources= st.checkbox("📦 فحص حجم JS/CSS",   value=True)
    check_server   = st.checkbox("🖥️ فحص Server Headers", value=True)

    st.markdown("---")
    run_btn = st.button("🚀 ابدأ الـ Audit", use_container_width=True,
                         type="primary")
    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#ccb84a;text-align:center;line-height:1.8">
    🔧 Technical Audit Pro<br>
    <span style="color:#FFD700;font-weight:700">Ismail El Asiouty</span><br>
    <a href="https://www.linkedin.com/in/ismailelasiouty/" target="_blank"
       style="color:#FFD700;text-decoration:none">🔗 LinkedIn</a> &nbsp;|&nbsp;
    <a href="https://wa.me/201014672352" target="_blank"
       style="color:#FFD700;text-decoration:none">💬 WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:linear-gradient(135deg,#0a0a0a,#1a1100);
            border:2px solid #FFD700;border-radius:16px;
            padding:24px 32px;margin-bottom:24px;">
  <div style="font-size:26px;font-weight:900;color:#FFD700;">
    🔧 Technical Audit Pro
  </div>
  <div style="color:#ccb84a;font-size:13px;margin-top:6px;">
    robots.txt • Status Codes 404/5xx • حجم الصفحات • JS/CSS • Server Headers
  </div>
</div>
""", unsafe_allow_html=True)

if not run_btn or not raw_url:
    st.markdown("""
    <div style="text-align:center;padding:50px 20px;color:#888;">
        <div style="font-size:56px;margin-bottom:12px">🔧</div>
        <div style="font-size:18px;font-weight:700;color:#FFD700;margin-bottom:8px">
            Technical Audit Pro
        </div>
        <div style="font-size:14px;color:#666;max-width:500px;margin:0 auto;">
            أدخل رابط الموقع في الـ Sidebar واختار الفحوصات اللي عايزها
            ثم اضغط <strong style="color:#FFD700">ابدأ الـ Audit</strong>
        </div>
        <div style="display:flex;justify-content:center;gap:20px;flex-wrap:wrap;
                    margin-top:24px;font-size:13px;color:#ccb84a;">
            <span>🤖 robots.txt</span>
            <span>🔴 404 & 5xx</span>
            <span>📦 Page Size</span>
            <span>📜 JS/CSS</span>
            <span>🖥️ Server</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Run ──────────────────────────────────────────────────────
base_url = normalize_url(raw_url)
domain   = urlparse(base_url).netloc

st.markdown(f"""
<div style="background:#1a1100;border:1px solid #FFD700;border-radius:10px;
            padding:12px 20px;margin-bottom:16px;color:#FFD700;font-size:13px;">
    🔍 جاري فحص: <strong>{base_url}</strong>
</div>
""", unsafe_allow_html=True)

tab_robots, tab_status, tab_resources, tab_server = st.tabs([
    "🤖 robots.txt",
    "🔴 Status Codes",
    "📦 JS / CSS / حجم",
    "🖥️ Server Headers",
])

# ══════════════════════════════════════════════════════════════
#  TAB 1: ROBOTS.TXT
# ══════════════════════════════════════════════════════════════
with tab_robots:
    if not check_robots:
        st.info("الفحص ده مش مفعّل — فعّله من الـ Sidebar")
    else:
        st.markdown('<div class="section-header">🤖 تحليل robots.txt</div>',
                    unsafe_allow_html=True)
        with st.spinner("جاري قراءة robots.txt ..."):
            rb = audit_robots(base_url)

        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"""<div class="metric-card">
            <div class="metric-val">{'✅' if rb['exists'] else '❌'}</div>
            <div class="metric-lbl">robots.txt موجود</div></div>""",
            unsafe_allow_html=True)
        col2.markdown(f"""<div class="metric-card">
            <div class="metric-val">{len(rb['disallowed'])}</div>
            <div class="metric-lbl">Disallow rules</div></div>""",
            unsafe_allow_html=True)
        col3.markdown(f"""<div class="metric-card">
            <div class="metric-val">{len(rb['sitemaps'])}</div>
            <div class="metric-lbl">Sitemaps مذكورة</div></div>""",
            unsafe_allow_html=True)
        col4.markdown(f"""<div class="metric-card">
            <div class="metric-val">{len(rb['user_agents'])}</div>
            <div class="metric-lbl">User-agents</div></div>""",
            unsafe_allow_html=True)

        # Issues
        if rb["issues"]:
            st.markdown("#### ⚠️ مشاكل مكتشفة")
            for issue in rb["issues"]:
                st.error(issue)
        else:
            st.success("✅ مفيش مشاكل واضحة في robots.txt")

        # Sitemaps found
        if rb["sitemaps"]:
            st.markdown("#### 🗺️ Sitemaps المذكورة")
            for s in rb["sitemaps"]:
                st.markdown(f"- 🔗 [{s}]({s})")

        # Disallow table
        if rb["disallowed"]:
            st.markdown("#### 🚫 Disallow Rules")
            df_dis = pd.DataFrame(rb["disallowed"])
            df_dis.columns = ["👤 User-Agent", "🚫 المسار المحجوب"]
            st.dataframe(df_dis, use_container_width=True)
            download_csv(df_dis, f"{domain}_robots_disallow", "تحميل Disallow Rules")

        # Raw content
        with st.expander("📄 محتوى robots.txt الكامل"):
            st.code(rb["raw"] or "مفيش محتوى", language="text")


# ══════════════════════════════════════════════════════════════
#  TAB 2: STATUS CODES
# ══════════════════════════════════════════════════════════════
with tab_status:
    if not check_status:
        st.info("الفحص ده مش مفعّل — فعّله من الـ Sidebar")
    else:
        st.markdown('<div class="section-header">🔴 فحص Status Codes — 404 / 5xx / Redirects</div>',
                    unsafe_allow_html=True)

        prog = st.progress(0, text="جاري تحليل الـ Sitemap ...")
        with st.spinner("بيفحص الصفحات ..."):
            status_results = audit_sitemap_status(base_url, max_pages, prog)
        prog.empty()

        if not status_results:
            st.warning("⚠️ مش قادر يجيب URLs من الـ Sitemap — تأكد إن الـ Sitemap موجود وشغّال")
        else:
            df_status = pd.DataFrame(status_results)

            # Summary metrics
            total    = len(df_status)
            ok_200   = df_status["🚦 Status"].str.contains("200").sum()
            err_404  = df_status["🚦 Status"].str.contains("404").sum()
            redirect = df_status["🚦 Status"].str.contains("🔁").sum()
            server_err = df_status["🚦 Status"].str.contains("5").sum()
            slow     = df_status["⏱️ وقت الاستجابة"].str.contains("بطيء").sum()
            big_pages= df_status["📦 حجم الصفحة"].str.contains("كبير").sum()
            too_js   = df_status["📜 عدد JS scripts"].str.contains("كتير").sum()

            c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
            for col, val, lbl, clr in [
                (c1, total,      "إجمالي الصفحات", "#1a1100"),
                (c2, ok_200,     "✅ سليمة 200",    "#0f9d58"),
                (c3, err_404,    "🔴 صفحات 404",    "#e53935"),
                (c4, redirect,   "🔁 Redirects",    "#6200ea"),
                (c5, server_err, "⛔ أخطاء Server", "#e53935"),
                (c6, slow,       "🐢 صفحات بطيئة",  "#f57c00"),
                (c7, big_pages,  "📦 صفحات كبيرة",  "#1565c0"),
            ]:
                col.markdown(f"""<div class="metric-card" style="border-color:{clr}">
                    <div class="metric-val" style="color:{clr}">{val}</div>
                    <div class="metric-lbl">{lbl}</div></div>""",
                    unsafe_allow_html=True)

            st.markdown("---")

            # Filters
            filter_col, _ = st.columns([2, 3])
            with filter_col:
                filter_opt = st.selectbox("🔍 فلتر النتايج", [
                    "كل الصفحات",
                    "🔴 صفحات 404 فقط",
                    "⛔ أخطاء Server (5xx)",
                    "🔁 Redirects فقط",
                    "🐢 صفحات بطيئة",
                    "📦 صفحات حجمها كبير",
                    "📜 JS كتير",
                ])

            df_show = df_status.copy()
            if filter_opt == "🔴 صفحات 404 فقط":
                df_show = df_show[df_show["🚦 Status"].str.contains("404")]
            elif filter_opt == "⛔ أخطاء Server (5xx)":
                df_show = df_show[df_show["🚦 Status"].str.contains("5[0-9][0-9]", regex=True)]
            elif filter_opt == "🔁 Redirects فقط":
                df_show = df_show[df_show["🚦 Status"].str.contains("🔁")]
            elif filter_opt == "🐢 صفحات بطيئة":
                df_show = df_show[df_show["⏱️ وقت الاستجابة"].str.contains("بطيء")]
            elif filter_opt == "📦 صفحات حجمها كبير":
                df_show = df_show[df_show["📦 حجم الصفحة"].str.contains("كبير")]
            elif filter_opt == "📜 JS كتير":
                df_show = df_show[df_show["📜 عدد JS scripts"].str.contains("كتير")]

            st.markdown(f"**{len(df_show)} صفحة**")
            st.dataframe(df_show, use_container_width=True, height=500,
                         column_config={"🔗 الرابط": st.column_config.LinkColumn()})
            download_csv(df_status, f"{domain}_status_report", "تحميل تقرير Status Codes")


# ══════════════════════════════════════════════════════════════
#  TAB 3: JS / CSS / PAGE SIZE
# ══════════════════════════════════════════════════════════════
with tab_resources:
    if not check_resources:
        st.info("الفحص ده مش مفعّل — فعّله من الـ Sidebar")
    else:
        st.markdown('<div class="section-header">📦 تحليل حجم JS / CSS / الصفحات</div>',
                    unsafe_allow_html=True)

        if "status_results" not in dir() or not status_results:
            st.warning("⚠️ لازم تشغّل فحص الـ Status Codes الأول عشان يجيب قائمة الـ URLs")
        else:
            sample = [
                r["🔗 الرابط"] for r in status_results
                if "200" in r.get("🚦 Status", "")
            ][:20]

            st.info(f"🔍 هيفحص أول {len(sample)} صفحة سليمة (200) عشان يحلل ملفات JS/CSS")
            prog2 = st.progress(0, text="جاري تحليل الـ Resources ...")
            with st.spinner("بيحلل ملفات JS و CSS ..."):
                res_results = audit_page_resources(base_url, sample, prog2)
            prog2.empty()

            if not res_results:
                st.info("مفيش ملفات JS/CSS واضحة في الصفحات دي")
            else:
                df_res = pd.DataFrame(res_results)

                big_js  = df_res[(df_res["📁 النوع"] == "JavaScript") &
                                  (df_res["🚦 التقييم"].str.contains("🔴|🟡"))].shape[0]
                big_css = df_res[(df_res["📁 النوع"] == "CSS") &
                                  (df_res["🚦 التقييم"].str.contains("🔴|🟡"))].shape[0]

                col1, col2, col3 = st.columns(3)
                col1.metric("📜 إجمالي ملفات JS", df_res[df_res["📁 النوع"]=="JavaScript"].shape[0])
                col2.metric("🎨 إجمالي ملفات CSS", df_res[df_res["📁 النوع"]=="CSS"].shape[0])
                col3.metric("⚠️ ملفات كبيرة", big_js + big_css)

                st.markdown("---")
                type_filter = st.selectbox("فلتر", ["الكل", "JavaScript فقط", "CSS فقط",
                                                     "🔴 كبير جداً فقط"])
                df_show_r = df_res.copy()
                if type_filter == "JavaScript فقط":
                    df_show_r = df_show_r[df_show_r["📁 النوع"] == "JavaScript"]
                elif type_filter == "CSS فقط":
                    df_show_r = df_show_r[df_show_r["📁 النوع"] == "CSS"]
                elif type_filter == "🔴 كبير جداً فقط":
                    df_show_r = df_show_r[df_show_r["🚦 التقييم"].str.contains("🔴")]

                st.dataframe(df_show_r, use_container_width=True, height=450)
                download_csv(df_res, f"{domain}_resources_report", "تحميل تقرير JS/CSS")


# ══════════════════════════════════════════════════════════════
#  TAB 4: SERVER HEADERS
# ══════════════════════════════════════════════════════════════
with tab_server:
    if not check_server:
        st.info("الفحص ده مش مفعّل — فعّله من الـ Sidebar")
    else:
        st.markdown('<div class="section-header">🖥️ فحص Server Headers والأمان</div>',
                    unsafe_allow_html=True)

        with st.spinner("جاري فحص الـ Server Headers ..."):
            server_checks = audit_server_headers(base_url)

        if not server_checks:
            st.error("❌ مش قادر يوصل للموقع")
        else:
            df_srv = pd.DataFrame(server_checks)

            issues_srv = [r for r in server_checks if "⚠️" in r["🚦 الحالة"] or "🔴" in r["🚦 الحالة"]]
            ok_srv     = [r for r in server_checks if "✅" in r["🚦 الحالة"]]

            col1, col2 = st.columns(2)
            col1.markdown(f"""<div class="metric-card" style="border-color:#0f9d58">
                <div class="metric-val" style="color:#0f9d58">{len(ok_srv)}</div>
                <div class="metric-lbl">✅ فحوصات سليمة</div></div>""",
                unsafe_allow_html=True)
            col2.markdown(f"""<div class="metric-card" style="border-color:#e53935">
                <div class="metric-val" style="color:#e53935">{len(issues_srv)}</div>
                <div class="metric-lbl">⚠️ تحتاج مراجعة</div></div>""",
                unsafe_allow_html=True)

            st.markdown("---")

            if issues_srv:
                st.markdown("#### ⚠️ تحتاج مراجعة")
                for item in issues_srv:
                    st.warning(f"**{item['🔍 الفحص']}** — {item['🚦 الحالة']}")

            st.markdown("#### 📋 كل النتايج")
            st.dataframe(df_srv, use_container_width=True)
            download_csv(df_srv, f"{domain}_server_headers", "تحميل تقرير Server Headers")
