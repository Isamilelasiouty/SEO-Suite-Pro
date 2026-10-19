"""
Technical Server and Robots.txt Checker for SEO Suite Pro:
- Robots.txt directive analysis and blocking vulnerability detection
- Security header audit (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
- Server caching and compression efficiency
- Response time and status code profiling
"""

import re
from core.security import validate_and_normalize_url
from services.crawler import fetch_url

def audit_robots_txt(base_url: str) -> dict:
    """
    Parses and checks robots.txt for indexation hazards and configuration issues.
    """
    is_valid, norm_url, err = validate_and_normalize_url(base_url)
    if not is_valid:
        return {"exists": False, "error": err}
        
    robots_url = norm_url + "/robots.txt"
    res = fetch_url(robots_url, timeout=10)
    
    if res["status_code"] != 200 or not res["content"]:
        return {
            "url": robots_url,
            "exists": False,
            "status_code": res["status_code"],
            "raw": "",
            "disallowed": [],
            "allowed": [],
            "sitemaps": [],
            "user_agents": [],
            "crawl_delay": None,
            "issues": [f"Robots.txt is not accessible (HTTP {res['status_code']}). Search engines may crawl without directives."]
        }
        
    raw_text = res["content"]
    user_agents = []
    disallowed = []
    allowed = []
    sitemaps = []
    crawl_delay = None
    issues = []
    
    current_agent = "*"
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
            
        key, _, val = line.partition(":")
        k = key.strip().lower()
        v = val.strip()
        
        if k == "user-agent":
            current_agent = v
            if v not in user_agents:
                user_agents.append(v)
        elif k == "disallow":
            if v:
                disallowed.append({"agent": current_agent, "path": v})
        elif k == "allow":
            if v:
                allowed.append({"agent": current_agent, "path": v})
        elif k == "sitemap":
            if v and v not in sitemaps:
                sitemaps.append(v)
        elif k == "crawl-delay":
            crawl_delay = v
            
    # Audit rules
    if not sitemaps:
        issues.append("No Sitemap directive declared in robots.txt.")
        
    if any(d["agent"] == "*" and d["path"] == "/" for d in disallowed):
        issues.append("CRITICAL: 'Disallow: /' for all robots detected! The entire domain is blocked from search crawlers.")
        
    if crawl_delay:
        try:
            if float(crawl_delay) > 10:
                issues.append(f"Crawl-Delay is set to {crawl_delay}s, which severely restricts bot crawling velocity.")
        except ValueError:
            pass

    return {
        "url": robots_url,
        "exists": True,
        "status_code": 200,
        "raw": raw_text,
        "disallowed": disallowed,
        "allowed": allowed,
        "sitemaps": sitemaps,
        "user_agents": user_agents,
        "crawl_delay": crawl_delay,
        "issues": issues
    }

def audit_server_headers(target_url: str) -> list[dict]:
    """
    Evaluates server response headers against modern web security and performance standards.
    """
    res = fetch_url(target_url, timeout=10)
    if res["status_code"] == 0:
        return []
        
    h = {k.lower(): v for k, v in res["headers"].items()}
    checks = []
    
    # 1. HTTPS Protocol
    is_https = target_url.startswith("https://")
    checks.append({
        "check": "HTTPS Protocol",
        "status": "Optimal" if is_https else "Critical",
        "value": "Enabled" if is_https else "Disabled (Insecure HTTP)",
        "recommendation": "Maintain enforced HTTPS with full TLS redirection." if is_https else "Migrate entire site to HTTPS immediately."
    })
    
    # 2. Strict-Transport-Security (HSTS)
    hsts = h.get("strict-transport-security")
    checks.append({
        "check": "Strict-Transport-Security (HSTS)",
        "status": "Optimal" if hsts else "Warning",
        "value": hsts or "Not Present",
        "recommendation": "Header is active." if hsts else "Enable HSTS to prevent SSL stripping attacks."
    })
    
    # 3. X-Frame-Options
    xfo = h.get("x-frame-options")
    checks.append({
        "check": "X-Frame-Options",
        "status": "Optimal" if xfo else "Warning",
        "value": xfo or "Not Present",
        "recommendation": "Prevents clickjacking." if xfo else "Set X-Frame-Options: SAMEORIGIN to protect against clickjacking."
    })
    
    # 4. Content-Security-Policy (CSP)
    csp = h.get("content-security-policy")
    checks.append({
        "check": "Content-Security-Policy",
        "status": "Optimal" if csp else "Warning",
        "value": "Configured" if csp else "Not Present",
        "recommendation": "CSP is active." if csp else "Implement a modern Content Security Policy."
    })
    
    # 5. X-Content-Type-Options
    xcto = h.get("x-content-type-options")
    checks.append({
        "check": "X-Content-Type-Options",
        "status": "Optimal" if xcto == "nosniff" else "Warning",
        "value": xcto or "Not Present",
        "recommendation": "Active." if xcto == "nosniff" else "Set 'nosniff' to prevent MIME-type confusion attacks."
    })
    
    # 6. Cache-Control
    cc = h.get("cache-control")
    checks.append({
        "check": "Cache-Control",
        "status": "Optimal" if cc else "Warning",
        "value": cc or "Not Present",
        "recommendation": "Leverage browser caching for static assets." if not cc else "Caching policy detected."
    })
    
    # 7. Server Banner Information Disclosure
    server = h.get("server")
    has_version = bool(server and re.search(r"\d+\.\d+", server))
    checks.append({
        "check": "Server Banner Disclosure",
        "status": "Warning" if has_version else "Optimal",
        "value": server or "Hidden / Masked",
        "recommendation": "Hide exact server version strings to limit reconnaissance." if has_version else "Server signature is appropriately minimized."
    })
    
    # 8. TTFB Response Time
    elapsed = res["elapsed_ms"]
    speed_status = "Optimal" if elapsed < 800 else "Warning" if elapsed < 2000 else "Critical"
    checks.append({
        "check": "Time to First Byte (TTFB)",
        "status": speed_status,
        "value": f"{elapsed} ms",
        "recommendation": "Fast initial response." if elapsed < 800 else "Optimize server processing, caching, and CDN routing."
    })
    
    return checks
