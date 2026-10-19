# SEO Suite Pro — Enterprise Organic Intelligence Platform

An enterprise-grade Technical SEO and Search Console analytics platform architected by **Ismail El Asiouty**. Built with Python, R, and Streamlit, featuring Scikit-Learn semantic intent clustering, algorithmic keyword cannibalization detection, time-series anomaly modeling, Google Gemini AI integration, multi-format exports (CSV, Excel, PDF), and a private user history vault.

**Author & Owner:** [Ismail El Asiouty](https://isamilelasiouty.github.io/Isamilelasiouty-portfolio-/index.html)  
**Live Application:** [SEO Suite Pro on Streamlit Cloud](https://seo-suite-pro-gsvmtun9dhvcl5ikrtg8vn.streamlit.app/)  
**LinkedIn:** [linkedin.com/in/ismailelasiouty](https://www.linkedin.com/in/ismailelasiouty/)  
**Contact:** 01014672352 | [WhatsApp Direct](https://wa.me/201014672352) | [tel:+201014672352](tel:+201014672352)  

---

## What's New in Version 2.2

- **Dynamic Light & Dark Mode:** Instant toggle between luxury obsidian black and crisp executive light mode with gold accents and custom Plotly figure theme alignment.
- **Full Bilingual Support (English & Arabic):** Complete UI localization with automatic Right-to-Left (RTL) formatting and Google `Cairo` font typography.
- **Dedicated GSC Upload Zone:** Prominent drag-and-drop file ingestion supporting `.zip` archives directly exported from Google Search Console (automatically unpacks `Queries.csv`, `Pages.csv`, `Devices.csv`), standalone `.csv` files, and `.json` API payloads.
- **Official Brand & Google Badges:** Embedded official Google 4-color SVG logo, Google Search Console badge, and Gemini sparkle icons.
- **Eye-Friendly Animations:** Subtle CSS fade-in, smooth card elevation, and gold glow transitions respecting `prefers-reduced-motion`.

---

## Key Modules & Capabilities

### 1. On-Page & Technical DOM Audit
- **Concurrent Multi-Page Crawling:** Fast multi-threaded crawling powered by `requests.Session` connection pooling and `ThreadPoolExecutor`.
- **DOM Hierarchy & Meta Tags:** Title and meta description pixel and character validation, H1-H6 structural hierarchy verification, and duplicate tag detection.
- **Readability & Content Depth:** Flesch Reading Ease score, Flesch-Kincaid Grade Level, word count, reading time estimation, and text-to-HTML ratio.
- **Structured Data (Schema.org):** JSON-LD extraction, syntax validation, required field checks (Article, Product, FAQPage, etc.), and duplicate schema detection.
- **Technical Directives:** Canonical tag self-reference validation, Robots meta directives, Open Graph, and Twitter Card audits.
- **Media & Link Architecture:** Missing alt text detection, lazy-loading presence, internal vs. external link classification, and nofollow distributions.
- **Server & Robots.txt:** Deep inspection of `robots.txt` disallows, sitemaps, crawl-delay, TTFB latency, and security headers (HTTPS, HSTS, X-Frame-Options, CSP, X-Content-Type-Options, Cache-Control).

### 2. Search Console Intelligence (Python + R Dual Engine)
- **Dedicated Upload Zone:** Drag-and-drop support for `.zip` (direct GSC exports), `.csv`, and `.json`.
- **Semantic Intent Clustering (Python / Scikit-Learn):** TF-IDF vectorization and KMeans / Cosine clustering to group queries and landing pages into distinct search intent clusters.
- **10-Class Automated Issue Detection:**
  1. *Low CTR with High Impressions* (Snippet re-optimization opportunities).
  2. *Striking Distance Opportunities* (Position 8–20 quick-win ranking targets).
  3. *Dropped & Declining Queries* (Traffic loss velocity alerts).
  4. *Zero-Click High-Impression Queries* (SERP feature cannibalization).
  5. *Keyword Cannibalization* (Multiple URLs ranking for identical search terms).
  6. *Duplicate Search Intent* (Scattered topical authority across redundant URLs).
  7. *Thin Content Signals* (High query footprint with negligible clicks and poor positions).
  8. *Branded vs. Non-Branded Imbalance* (Quantifying reliance on brand navigation).
  9. *Device Discrepancies* (Mobile vs. Desktop CTR performance gaps).
  10. *Geographic Gaps* (Regional ranking drops).
- **Keyword Cannibalization Resolver:** Evaluates competing pages via weighted composite scoring (Clicks 40%, Impressions 30%, Position 20%, CTR 10%), designates the Primary URL, identifies the technical root cause (Duplicate Content, Overlapping Intent, Internal Anchor Conflict, or Healthy SERP Coverage), and prescribes the exact remediation protocol (301 Redirect, Canonical Tag, Merge & Consolidate, or Intent Differentiation).
- **R Statistical Engine (`r_scripts/`):** Executes R statistical scripts for Tukey IQR anomaly fences, skewness/kurtosis distribution modeling, and Wilcoxon / Mann-Whitney hypothesis testing.
- **Graceful Python Fallback:** If R is not installed on the host system, the platform displays an informative status banner and seamlessly executes equivalent high-precision statistical analyses using `scipy.stats` and `numpy`.

### 3. Off-Page & Anchor Text Risk Model
- **Anchor Text Categorization:** Exact Match, Partial Match, Branded, Generic ("click here", "learn more"), and Naked URL distributions.
- **Algorithmic Penalty Risk Index:** Evaluates over-optimization penalty risk (e.g. flags exact-match densities exceeding healthy thresholds).
- **Authority & Diversity Indicators:** Dofollow vs. nofollow ratio, deep-link distribution, and referring domain breadth.

### 4. Google Gemini AI Strategic Assistant
- **Zero-Trust Key Management:** Users paste their free-tier Gemini API key from Google AI Studio. Keys are stored only in the active session or encrypted in the user's isolated profile using symmetric Fernet encryption. Keys are never logged and never stored in plain text.
- **Executive 30-Day Roadmaps:** Plain-language synthesis of On-Page DOM findings and Search Console metrics into prioritized technical sprints (Days 1–7: Critical Fixes, Days 8–15: Quick Wins, Days 16–30: Content Consolidation).
- **High-CTR Snippet Rewriter:** Generates 3 distinct high-converting Title and Meta Description variants for underperforming search queries.
- **Cannibalization Differentiation Briefs:** Generates tailored content restructuring briefs to resolve keyword conflicts.
- **Optional & Resilient:** All core crawling, auditing, and Search Console features remain 100% operational without an API key.

### 5. Multi-User Authentication & Private History
- **Security by Default:** User registration and sign-in with `bcrypt` password hashing (cost factor 12).
- **Strict Data Isolation:** Multi-tenant SQLite database architecture where past audits and Search Console uploads are strictly isolated by `user_id`.
- **History Vault:** Dedicated page to inspect past audits, review summary KPIs, download reports, and safely delete records.
- **Privacy-Preserving Admin Analytics:** Admin accounts access platform throughput and event metrics with zero visibility into user audit payloads or target URLs.

### 6. Multi-Format Report Exporters
- **CSV:** Clean UTF-8 with BOM exports compatible with Microsoft Excel and Google Sheets without encoding issues.
- **Excel (.xlsx):** Multi-sheet workbooks generated via `openpyxl` with custom gold headers, auto-adjusted column widths, and styled data rows.
- **Executive PDF:** Branded PDF reports generated via `reportlab` featuring the official logo, KPI summary grids, prioritized issue tables, and author metadata.

---

## Luxury Gold, Black & White Design System

The platform strictly adheres to an executive, distraction-free aesthetic:
- **Palette:** Gold (`#D4AF37`, hover `#B8962E`), Deep Black (`#0B0B0B`, surfaces `#141414`, `#1C1C1C`), and Soft White (`#FFFFFF`, `#F5F5F5`).
- **Dynamic Light & Dark Themes:** Light theme utilizes clean surfaces with refined gold accents.
- **Bilingual RTL Support:** Native Arabic typography utilizing Google Fonts `Cairo` with automatic right-to-left layout alignments.
- **Strict Anti-Emoji Policy:** Zero emojis, decorative icons, or icon fonts across the UI. Replaced by refined typography (Inter / Poppins / Cairo) and uppercase text badges (`[OPTIMAL]`, `[WARNING]`, `[CRITICAL]`).
- **Smooth Animations:** Subtle page fade-in and gentle card hover lifts respecting `prefers-reduced-motion`.

---

## Architecture & Directory Structure

```
seo-suite-pro/
├── app.py                      # Master application entry point, routing gateway & theme/lang controllers
├── requirements.txt            # Pinned production Python dependencies
├── packages.txt                # Linux system dependencies for Streamlit Cloud (R runtime)
├── .gitignore                  # Exclusion rules for databases, secrets, and caches
├── assets/
│   ├── logo.jpeg               # Official brand logo
│   └── custom.css              # Gold, black, white design system & theme/RTL stylesheet
├── core/
│   ├── config.py               # Constants, design tokens, and crawling limits
│   ├── i18n.py                 # Bilingual translation dictionary (English & Arabic)
│   ├── security.py             # SSRF prevention, URL sanitization, and Fernet encryption
│   ├── database.py             # SQLite persistence, bcrypt auth, and admin metrics
│   └── auth.py                 # Streamlit session management and role gates
├── services/
│   ├── crawler.py              # Concurrent HTTP crawling and XML sitemap recursion
│   ├── onpage_analyzer.py      # BeautifulSoup/lxml DOM parser and readability scorer
│   ├── offpage_analyzer.py     # Anchor text categorization and over-optimization model
│   ├── technical_checker.py    # Robots.txt validation and server security header audit
│   ├── gsc_processor.py        # GSC ingestion (ZIP, CSV, JSON), TF-IDF clustering & cannibalization solver
│   ├── r_statistical_runner.py # Rscript execution bridge with seamless Scipy fallback
│   └── gemini_service.py       # Google Gemini AI client
├── r_scripts/
│   └── gsc_statistical_analysis.R # R statistical script for anomaly and hypothesis tests
├── utils/
│   ├── export_csv.py           # UTF-8 BOM CSV generator
│   ├── export_excel.py         # OpenPyXL styled multi-sheet workbook generator
│   └── export_pdf.py           # ReportLab branded PDF generator
├── views/
│   ├── components.py           # Header, footer, Google/GSC/Gemini SVG badges, and theme Plotly styles
│   ├── view_auth.py            # User sign in and registration portal
│   ├── view_dashboard.py       # Executive overview and module launchpad
│   ├── view_onpage.py          # On-page DOM and technical crawler view
│   ├── view_gsc.py             # Search Console Python + R intelligence view with dedicated upload zone
│   ├── view_offpage.py         # Backlink profile and anchor risk view
│   ├── view_gemini.py          # Gemini AI action plan and snippet assistant
│   ├── view_history.py         # Private user audit vault view
│   ├── view_admin.py           # Administrative usage metrics view
│   └── view_contact.py         # Official Contact Me page
└── tests/
    ├── test_security.py        # SSRF and encryption unit tests
    ├── test_parsers.py         # On-page DOM and schema unit tests
    ├── test_gsc.py             # Cannibalization, ZIP extraction & i18n unit tests
    └── test_auth_db.py         # Authentication and data isolation tests
```

---

## Local Installation & Setup

### Prerequisites
- Python 3.10+ (Recommended: Python 3.11)
- Optional: R runtime (`Rscript`) with `jsonlite` package (if not installed, the platform automatically activates its native Python statistical engine).

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/isamilelasiouty/seo-suite-pro.git
   cd seo-suite-pro
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Using uv (fastest)
   uv venv .venv --python 3.11
   .venv\Scripts\activate       # Windows
   # source .venv/bin/activate  # macOS / Linux

   # Or using standard venv
   python -m venv .venv
   .venv\Scripts\activate       # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run automated test suite:**
   ```bash
   python -m pytest tests/
   ```

5. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## Streamlit Cloud Deployment

This repository is optimized for one-click deployment on [Streamlit Community Cloud](https://share.streamlit.io):

1. **Repository Settings:**
   - Main file path: `app.py`
   - Python version: `3.11`

2. **System Dependencies (R Runtime):**
   - The repository includes `packages.txt` containing `r-base` and `r-base-dev`. Streamlit Cloud installs R automatically during build time, enabling native R statistical analysis.

3. **Secrets (Optional):**
   - No secrets are mandatory to boot the app. Users can securely provide their own Gemini API key directly in the application UI.

---

## Contact & Consultation

For custom search architecture, enterprise audits, or technical consultations:

- **Architect:** Ismail El Asiouty
- **Portfolio:** [isamilelasiouty.github.io](https://isamilelasiouty.github.io/Isamilelasiouty-portfolio-/index.html)
- **LinkedIn:** [linkedin.com/in/ismailelasiouty](https://www.linkedin.com/in/ismailelasiouty/)
- **Phone:** 01014672352
- **WhatsApp:** [wa.me/201014672352](https://wa.me/201014672352)
- **Direct Call:** [tel:+201014672352](tel:+201014672352)

*Built by Ismail El Asiouty*
