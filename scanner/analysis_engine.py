# scanner/analysis_engine.py
# Safe analysis module: classifies content, headers, and metadata.

def analyze_response(result):
    """
    Safe, non-offensive analysis of HTTP response content.
    This does NOT exploit, fuzz, attack, or probe anything.
    It only analyzes the data you already fetched.
    """

    status = result.get("status")
    headers = result.get("headers", {}) or {}
    body = result.get("body_sample", "") or ""

    analysis = {
        "status_category": categorize_status(status),
        "server_info": extract_server(headers),
        "tech_signals": detect_tech(body, headers),
        "keyword_flags": keyword_scan(body),
        "content_length": len(body),
    }

    return analysis


def categorize_status(status):
    if status is None:
        return "no-response"
    if 100 <= status < 200:
        return "informational"
    if 200 <= status < 300:
        return "success"
    if 300 <= status < 400:
        return "redirect"
    if 400 <= status < 500:
        return "client-error"
    if 500 <= status < 600:
        return "server-error"
    return "unknown"


def extract_server(headers):
    server = headers.get("Server")
    powered = headers.get("X-Powered-By")

    return {
        "server_header": server,
        "powered_by": powered,
    }


def detect_tech(body, headers):
    """
    Safe pattern-based tech hints.
    This is NOT fingerprinting for exploitation.
    It simply looks for common framework keywords.
    """

    tech = []

    text = (body or "").lower()

    patterns = {
        "react": "react",
        "nextjs": "next",
        "wordpress": "wp-content",
        "drupal": "drupal",
        "laravel": "laravel",
        "rails": "rails",
        "cloudflare": "cloudflare",
    }

    for name, keyword in patterns.items():
        if keyword in text:
            tech.append(name)

    # header-based hints
    server = headers.get("Server", "").lower()
    if "nginx" in server:
        tech.append("nginx")
    if "apache" in server:
        tech.append("apache")

    return tech


def keyword_scan(body):
    """
    Safe keyword scanning — looks for interesting words,
    but does NOT test or exploit anything.
    """

    keywords = [
        "error",
        "exception",
        "debug",
        "warning",
        "deprecated",
        "stack trace",
    ]

    found = []
    text = (body or "").lower()

    for k in keywords:
        if k in text:
            found.append(k)

    return found
