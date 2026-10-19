"""
Crawler and Network Engine for SEO Suite Pro:
- Multi-threaded concurrent crawling with connection pooling
- Robust XML sitemap parser with namespace handling and index recursion
- SSRF prevention integration
- Structured error handling and graceful fallbacks
"""

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import (
    CRAWL_MAX_WORKERS,
    CRAWL_TIMEOUT_SECONDS,
)
from core.security import is_safe_host, validate_and_normalize_url

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def create_session() -> requests.Session:
    """Create a configured requests session with retries and pooling."""
    session = requests.Session()
    retries = Retry(
        total=2,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
    })
    return session

def fetch_url(url: str, session: requests.Session | None = None, timeout: int = CRAWL_TIMEOUT_SECONDS) -> dict:
    """
    Safely fetches a single URL with SSRF checks, timing, and error handling.
    """
    is_valid, norm_url, err_msg = validate_and_normalize_url(url)
    if not is_valid:
        return {
            "url": url,
            "final_url": url,
            "status_code": 0,
            "content": "",
            "headers": {},
            "elapsed_ms": 0,
            "size_bytes": 0,
            "error": err_msg or "Invalid or restricted URL."
        }
    
    close_session = False
    if session is None:
        session = create_session()
        close_session = True
        
    start_time = time.time()
    try:
        response = session.get(norm_url, timeout=timeout, allow_redirects=True)
        elapsed_ms = round((time.time() - start_time) * 1000)
        
        result = {
            "url": norm_url,
            "final_url": response.url,
            "status_code": response.status_code,
            "content": response.text if response.encoding else response.content.decode("utf-8", errors="replace"),
            "headers": dict(response.headers),
            "elapsed_ms": elapsed_ms,
            "size_bytes": len(response.content),
            "error": None
        }
        return result
    except requests.exceptions.Timeout:
        return {
            "url": norm_url,
            "final_url": norm_url,
            "status_code": 0,
            "content": "",
            "headers": {},
            "elapsed_ms": round((time.time() - start_time) * 1000),
            "size_bytes": 0,
            "error": "Request timed out."
        }
    except Exception as e:
        return {
            "url": norm_url,
            "final_url": norm_url,
            "status_code": 0,
            "content": "",
            "headers": {},
            "elapsed_ms": round((time.time() - start_time) * 1000),
            "size_bytes": 0,
            "error": str(e)
        }
    finally:
        if close_session:
            session.close()

def discover_sitemap_urls(base_url: str, session: requests.Session | None = None) -> list[str]:
    """
    Locates sitemaps by inspecting robots.txt and standard locations.
    """
    is_valid, norm_url, _ = validate_and_normalize_url(base_url)
    if not is_valid:
        return []
    
    candidates = [
        norm_url + "/sitemap.xml",
        norm_url + "/sitemap_index.xml",
        norm_url + "/sitemap-index.xml",
        norm_url + "/wp-sitemap.xml",
        norm_url + "/post-sitemap.xml"
    ]
    
    # 1. Check robots.txt for Sitemap directives
    robots_res = fetch_url(norm_url + "/robots.txt", session=session)
    if robots_res["status_code"] == 200 and robots_res["content"]:
        sitemap_lines = re.findall(r"^\s*sitemap:\s*(\S+)", robots_res["content"], re.IGNORECASE | re.MULTILINE)
        for s in sitemap_lines:
            s_clean = s.strip()
            if s_clean not in candidates:
                candidates.insert(0, s_clean)
                
    found = []
    for cand in candidates:
        res = fetch_url(cand, session=session, timeout=8)
        if res["status_code"] == 200 and ("<url" in res["content"].lower() or "<sitemap" in res["content"].lower()):
            found.append(cand)
            break
            
    return found

def parse_xml_sitemap(sitemap_url: str, max_depth: int = 2, session: requests.Session | None = None) -> list[dict]:
    """
    Parses an XML sitemap or sitemap index with full namespace and sub-sitemap recursion.
    Returns list of dicts: {'url', 'lastmod', 'changefreq', 'priority'}
    """
    if max_depth <= 0:
        return []
        
    res = fetch_url(sitemap_url, session=session)
    if res["status_code"] != 200 or not res["content"]:
        return []
        
    xml_content = res["content"].strip()
    # Strip XML namespace prefixes for robust element selection
    xml_cleaned = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', xml_content, count=1)
    
    pages = []
    try:
        root = ET.fromstring(xml_cleaned)
        
        # 1. Sitemap Index (<sitemapindex> -> <sitemap><loc>)
        if "sitemapindex" in root.tag.lower() or root.findall(".//sitemap"):
            sub_sitemaps = []
            for sm in root.findall(".//sitemap"):
                loc = sm.find("loc")
                if loc is not None and loc.text:
                    sub_sitemaps.append(loc.text.strip())
            
            # Recurse into sub-sitemaps (limit to 10 sub-sitemaps to prevent runaway crawls)
            for sub_sm in sub_sitemaps[:10]:
                pages.extend(parse_xml_sitemap(sub_sm, max_depth=max_depth - 1, session=session))
        
        # 2. URLset (<urlset> -> <url><loc>)
        for url_node in root.findall(".//url"):
            loc_node = url_node.find("loc")
            if loc_node is not None and loc_node.text:
                url_str = loc_node.text.strip()
                lastmod_node = url_node.find("lastmod")
                changefreq_node = url_node.find("changefreq")
                priority_node = url_node.find("priority")
                
                pages.append({
                    "url": url_str,
                    "lastmod": lastmod_node.text.strip() if lastmod_node is not None and lastmod_node.text else None,
                    "changefreq": changefreq_node.text.strip() if changefreq_node is not None and changefreq_node.text else None,
                    "priority": priority_node.text.strip() if priority_node is not None and priority_node.text else None
                })
    except ET.ParseError:
        # Fallback regex extraction if XML contains slight syntax defects
        locs = re.findall(r"<loc>(.*?)</loc>", xml_content, re.IGNORECASE)
        lastmods = re.findall(r"<lastmod>(.*?)</lastmod>", xml_content, re.IGNORECASE)
        for i, loc in enumerate(locs):
            clean_loc = loc.strip().replace("<![CDATA[", "").replace("]]>", "").strip()
            if clean_loc.endswith(".xml"):
                pages.extend(parse_xml_sitemap(clean_loc, max_depth=max_depth - 1, session=session))
            else:
                lm = lastmods[i].strip() if i < len(lastmods) else None
                pages.append({"url": clean_loc, "lastmod": lm, "changefreq": None, "priority": None})
                
    # Deduplicate by URL
    seen = set()
    unique_pages = []
    for p in pages:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique_pages.append(p)
            
    return unique_pages

def crawl_urls_concurrently(urls: list[str], max_workers: int = CRAWL_MAX_WORKERS, progress_callback=None) -> list[dict]:
    """
    Crawls multiple URLs in parallel using ThreadPoolExecutor with progress reporting.
    """
    results = []
    total = len(urls)
    session = create_session()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_url, u, session): u for u in urls}
        completed = 0
        for future in as_completed(future_to_url):
            data = future.result()
            results.append(data)
            completed += 1
            if progress_callback:
                progress_callback(completed, total, data["url"])
                
    session.close()
    return results
