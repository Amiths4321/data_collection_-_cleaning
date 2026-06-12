# collectors/web_collector.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_url(url: str) -> dict:
    """Scrape main text content from a webpage."""
    issues = []

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0"
        })
        resp.raise_for_status()
    except Exception as e:
        return {
            "source": url, "type": "web",
            "raw_text": "", "issues": [f"Failed to fetch: {str(e)}"]
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise tags
    for tag in soup(["script", "style", "nav", "footer",
                     "header", "aside", "form", "iframe"]):
        tag.decompose()

    # Extract main content
    main = soup.find("main") or soup.find("article") or soup.find("body")
    text = main.get_text(separator="\n") if main else soup.get_text(separator="\n")

    # Clean whitespace
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    text  = "\n".join(lines)

    if len(text) < 200:
        issues.append("Very little text extracted — page may require JavaScript")

    return {
        "source":   urlparse(url).netloc,
        "type":     "web",
        "url":      url,
        "raw_text": text,
        "issues":   issues
    }