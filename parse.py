# parse.py
from datetime import datetime
from typing import List, Dict

from bs4 import BeautifulSoup

from config import TARGET_LINK_PREFIX
from scoring import compute_total_score
from filters import should_exclude_item


def extract_context(link_tag, max_chars: int = 200) -> str:
    """
    Grab some surrounding text as context.
    """
    parent = link_tag.parent
    if not parent:
        return ""

    text = parent.get_text(separator=" ", strip=True)
    return text[:max_chars]


def parse_results(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if not href.startswith(TARGET_LINK_PREFIX):
            continue

        title = link.get_text(separator=" ").strip() or "Untitled Item"

        if should_exclude_item(title):
            continue

        scoring = compute_total_score(title)
        context = extract_context(link)

        item = {
            "title": title,
            "link": href,
            "score": scoring["total_score"],
            "confidence": scoring["confidence"],
            "size_mb": scoring["size_mb"],
            "keyword_score": scoring["keyword_score"],
            "size_score": scoring["size_score"],
            "anomaly": scoring["anomaly"],
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        results.append(item)

    # Sort by score, then confidence
    results.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)
    return results
