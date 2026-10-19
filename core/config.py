"""
Configuration and constants for SEO Suite Pro.
Strict adherence to the executive gold, black, and white design system.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.jpeg"
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "seo_suite.db"
R_SCRIPTS_DIR = BASE_DIR / "r_scripts"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Branding Metadata
BRAND_NAME = "SEO Suite Pro"
BRAND_OWNER = "Ismail El Asiouty"
BRAND_ROLE = "Technical SEO Architect & Full-Stack Engineer"
PORTFOLIO_URL = "https://isamilelasiouty.github.io/Isamilelasiouty-portfolio-/index.html"
LINKEDIN_URL = "https://www.linkedin.com/in/ismailelasiouty/"
PHONE_NUMBER = "01014672352"
WHATSAPP_URL = "https://wa.me/201014672352"
TEL_URL = "tel:+201014672352"
FOOTER_TEXT = "Built by Ismail El Asiouty"

# Color Palette (Gold, Black, White only)
COLOR_BG_PRIMARY = "#0B0B0B"
COLOR_BG_SURFACE = "#141414"
COLOR_BG_ELEVATED = "#1C1C1C"
COLOR_GOLD = "#D4AF37"
COLOR_GOLD_HOVER = "#B8962E"
COLOR_GOLD_MUTED = "rgba(212, 175, 55, 0.15)"
COLOR_GOLD_BORDER = "rgba(212, 175, 55, 0.35)"
COLOR_TEXT_WHITE = "#FFFFFF"
COLOR_TEXT_SOFT = "#F5F5F5"
COLOR_TEXT_MUTED = "#9E9E9E"

# Crawling and Analysis Defaults
DEFAULT_MAX_CRAWL_PAGES = 50
MAX_ALLOWED_CRAWL_PAGES = 300
CRAWL_TIMEOUT_SECONDS = 12
CRAWL_MAX_WORKERS = 8
MAX_FILE_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

# Stopwords for English Content Analysis
ENGLISH_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}
