# parse.py
from datetime import datetime
from typing import List, Dict, Any
import json
import os

from bs4 import BeautifulSoup

from config import TARGET_LINK_PREFIX, SELECTORS, DRIFT_CONFIG
from scoring import compute_total_score
from filters import should_exclude_item


def _load_drift_history() -> List[Dict[str, Any]]:
    path = DRIFT_CONFIG["history_file"]
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_drift_history(history: List[Dict[str, Any]]) -> None:
    path = DRIFT_CONFIG["history_file"]
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _record_drift_snapshot(item_count: int, selector_used: str) -> None:
    history = _load_drift_history()
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "item_count": item_count,
        "selector": selector_used,
    }
    history.append(snapshot)
    max_hist = DRIFT_CONFIG.get("max_history", 50)
    if len(history) > max_hist:
        history = history[-max_hist:]
    _save_drift_history(history)


def _analyze_drift(item_count: int) -> None:
    history = _load_drift_history()
    if not history:
        return

    prev_counts = [h["item_count"] for h in history[-10:]]  # last N runs
    avg = sum(prev_counts) / max(len(prev_counts), 1)

    if avg == 0:
        return

    ratio = item_count / avg
    if ratio < 0.3:
        print(
            f"[!] DOM drift warning: current items={item_count}, "
            f"recent average≈{avg:.1f} (ratio={ratio:.2f})"
        )


def extract_context(tag, max_chars: int = 200) -> str:
    parent_selector = SELECTORS.get("context_parent")
    parent = None

    if parent_selector:
        parent = tag.select_one(parent_selector)
    if not parent:
        parent = tag.parent

    if not parent:
        return ""

    text = parent.get_text(separator=" ", strip=True)
    return text[:max_chars]


def _get_title(tag) -> str:
    title_selector = SELECTORS.get("title")
    if title_selector:
        t = tag.select_one(title_selector)
        if t:
            text = t.get_text(separator=" ", strip=True)
            if text:
                return text
    # fallback: tag text
    text = tag.get_text(separator=" ", strip=True)
    return text or "Untitled Item"


def _get_link(tag) -> str:
    attr = SELECTORS.get("link_attr", "href")
    href = tag.get(attr, "")
    return href or ""


def parse_results(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    item_selector = SELECTORS.get("item", "a[href]")

    items = soup.select(item_selector)
    item_count = len(items)

    _record_drift_snapshot(item_count, item_selector)
    _analyze_drift(item_count)

    if item_count < DRIFT_CONFIG.get("min_items_warning", 3):
        print(
            f"[!] Warning: selector '{item_selector}' matched only {item_count} items. "
            "Possible DOM change or incorrect selector."
        )

    results: List[Dict] = []

    for tag in items:
        href = _get_link(tag)
        if not href:
            continue
        if not href.startswith(TARGET_LINK_PREFIX):
            continue

        title = _get_title(tag)

        if should_exclude_item(title):
            continue

        scoring = compute_total_score(title)
        context = extract_context(tag)

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

    results.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)
    return results
